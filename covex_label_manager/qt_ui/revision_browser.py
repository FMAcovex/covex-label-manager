"""Read-only selection of existing revisions/variants; no lifecycle mutation."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox,QTableWidget,QTableWidgetItem,QHeaderView,
    QAbstractItemView,QDialogButtonBox,QHBoxLayout)
from .responsive import AdaptiveDialog
from .window import vbox,label,button,STATE


class RevisionBrowserDialog(AdaptiveDialog):
    def __init__(self,window):
        super().__init__(window);self.window=window
        self.setWindowTitle('Revisiones documentales y variantes de diseño')
        self.resize(760,530)
        layout=vbox(self)
        layout.addWidget(label('Seleccionar no modifica ni aprueba documentos.','subtle'))
        self.revisions=QComboBox();self.revisions.setAccessibleName('Revisión documental')
        for revision in window.api.versions(window.row['id']):
            self.revisions.addItem(f"{revision['version']} · {STATE[revision['state']][0]}",revision['id'])
        self.revisions.setCurrentIndex(max(0,self.revisions.findData(window.row['version_id'])))
        layout.addWidget(self.revisions)
        self.table=QTableWidget(0,3);self.table.setHorizontalHeaderLabels(['Diseño','Denominación','Estado'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table,1)
        actions=QHBoxLayout()
        actions.addWidget(button('Seleccionar en Biblioteca',lambda:self.select(False)))
        actions.addWidget(button('Abrir en Editor',lambda:self.select(True),'primary'))
        layout.addLayout(actions)
        close=QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        close.rejected.connect(self.reject);layout.addWidget(close)
        self.revisions.currentIndexChanged.connect(self.populate);self.populate()

    def populate(self,*_):
        from .variants import STATES
        variants=self.window.api.variants(self.revisions.currentData())
        self.table.setRowCount(len(variants)+1)
        for row,values in enumerate([('Diseño de revisión','Sin variante',None,None)]+
            [(v['code'],v['name'],v['state'],v['id']) for v in variants]):
            for col,text in enumerate((values[0],values[1],STATES.get(values[2],'Estado de la revisión'))):
                item=QTableWidgetItem(text);item.setData(Qt.ItemDataRole.UserRole,values[3]);self.table.setItem(row,col,item)
        self.table.selectRow(0)

    def select(self,editor):
        row=self.table.currentRow()
        if row<0:return
        w=self.window
        if not w.flush_emission_work() or not w.resolve_work():return
        w.select_version(self.revisions.currentData())
        w.library_variant_id=self.table.item(row,0).data(Qt.ItemDataRole.UserRole)
        w.selected()
        if editor:w.open_editor()
        else:w.navigate('library');w.set_inspector(True);w.inspector_tabs.setCurrentIndex(1)
        self.accept()
