"""Qt master reconciliation wizard: map columns, compare, filter, export. No writes."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog,QFileDialog,QMessageBox,QComboBox,QFormLayout,
    QHBoxLayout,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QWidget,
    QDialogButtonBox)
from .window import vbox,label,button
from ..master_reconciliation import source_sheets,read_master,FIELDS,norm


GUESSES={
 'name':('denominación','denominacion','nombre','etiqueta','nombre etiqueta','descripcion'),
 'version':('revisión','revision','versión','version','rev'),
 'code':('código','codigo','referencia','cod.'),
 'origin':('origen','propietario'),
 'customer':('cliente','customer'),
 'product':('producto','product'),
 'language':('idioma','language','lenguaje'),
 'state':('estado','situación','situacion','vigencia')
}

class MasterReconciliationDialog(QDialog):
    def __init__(self,parent,api,path):
        super().__init__(parent)
        self.api=api;self.path=path;self.report=None
        self.setWindowTitle('R5C · Conciliación con libro máster (solo lectura)')
        self.resize(1080,720)
        layout=vbox(self,14,10)
        heading=label('Comparar el listado máster con la biblioteca local','panelTitle')
        layout.addWidget(heading)
        notice=label('Seleccione la hoja y asocie expresamente las columnas. '
            'No se modifican revisiones, metadatos ni estados. '
            'Los códigos numéricos de Excel deben ser texto para conservar ceros.','subtle')
        notice.setWordWrap(True);layout.addWidget(notice)
        sheetrow=QHBoxLayout();sheetrow.addWidget(label('Hoja:'))
        self.sheets=QComboBox();self.sheets.addItems(source_sheets(path))
        self.sheets.currentIndexChanged.connect(self.refresh_columns)
        sheetrow.addWidget(self.sheets,1);layout.addLayout(sheetrow)
        form=QFormLayout();self.inputs={}
        names={'name':'Denominación *','version':'Revisión *','code':'Código',
               'origin':'Origen','customer':'Cliente','product':'Producto',
               'language':'Idioma','state':'Estado documental'}
        for key in FIELDS:
            combo=QComboBox();self.inputs[key]=combo;form.addRow(names[key],combo)
        layout.addLayout(form)
        controls=QHBoxLayout()
        self.compare=button('Comparar con catálogo',self.run_compare,'primary')
        controls.addWidget(self.compare)
        self.filter=QComboBox();self.filter.addItem('Todos los resultados','')
        self.filter.currentIndexChanged.connect(self.display_results)
        controls.addWidget(self.filter);controls.addStretch()
        self.export=button('Exportar informe ZIP…',self.export_result)
        self.export.setEnabled(False);controls.addWidget(self.export)
        layout.addLayout(controls)
        self.summary=label('Sin comparación; revisar correspondencia de columnas.','subtle')
        self.summary.setWordWrap(True);layout.addWidget(self.summary)
        self.table=QTableWidget(0,6)
        self.table.setHorizontalHeaderLabels(['Fila','Estado','Denominación','Código','Revisión','Diferencias'])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table,1)
        close=QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close.rejected.connect(self.reject);layout.addWidget(close)
        self.refresh_columns()

    def refresh_columns(self,*_):
        self.report=None;self.export.setEnabled(False)
        self.table.setRowCount(0);self.filter.blockSignals(True)
        self.filter.clear();self.filter.addItem('Todos los resultados','')
        self.filter.blockSignals(False)
        try:table=read_master(self.path,self.sheets.currentText())
        except Exception as ex:
            self.summary.setText(str(ex));return
        self.summary.setText(f"{len(table['rows'])} filas de origen. Compruebe correspondencias antes de comparar.")
        for key,combo in self.inputs.items():
            combo.blockSignals(True);combo.clear();combo.addItem('— No comparar —',None)
            for col in table['headers']:combo.addItem(col,col)
            matches=[col for col in table['headers'] if norm(col) in
                     tuple(norm(v) for v in GUESSES[key])]
            if len(matches)==1:combo.setCurrentIndex(combo.findData(matches[0]))
            combo.blockSignals(False)

    def run_compare(self):
        from ..master_reconciliation import reconcile
        mapping={k:combo.currentData() for k,combo in self.inputs.items()}
        try:self.report=reconcile(self.api,self.path,self.sheets.currentText(),mapping)
        except Exception as ex:
            self.report=None;self.export.setEnabled(False)
            QMessageBox.warning(self,'Conciliación no realizada',str(ex));return
        self.export.setEnabled(True)
        self.filter.blockSignals(True);self.filter.clear()
        self.filter.addItem('Todos los resultados','')
        for kind,count in self.report['summary']['counts'].items():
            if count:self.filter.addItem(f'{kind} ({count})',kind)
        if self.report['only_in_app']:
            self.filter.addItem(f"ONLY_IN_APP ({len(self.report['only_in_app'])})",'ONLY_IN_APP')
        self.filter.blockSignals(False)
        self.display_results()

    def display_results(self,*_):
        if not self.report:return
        choice=self.filter.currentData() or ''
        records=self.report['results']
        if choice=='ONLY_IN_APP':records=[{
            'source_row':'—','status':'ONLY_IN_APP',
            'master':{'name':r['name'],'code':r['code'],'version':r['revision']},
            'differences':['Verificar cobertura del libro; no borrar automáticamente']}
            for r in self.report['only_in_app']]
        elif choice:records=[r for r in records if r['status']==choice]
        shown=records[:1000];self.table.setRowCount(len(shown))
        for i,r in enumerate(shown):
            row=r['master'];values=[str(r['source_row']),r['status'],
                row['name'],row['code'],row['version'],' | '.join(r['differences'])]
            for j,value in enumerate(values):
                cell=QTableWidgetItem(str(value));cell.setToolTip(str(value))
                self.table.setItem(i,j,cell)
        s=self.report['summary'];value=s['coverage_percent']
        ratio=('No calculable' if value is None else f'{value:.2f}%')
        self.summary.setText(f"Coincidencias completas: {s['matched']}/{s['compared']} · "
            f"Cobertura documental orientativa: {ratio} · "
            f"Solo en app: {s['extra_app_revisions']} · "
            f"Mostrando {len(shown)} de {len(records)} filas. "
            "Para el informe completo use Exportar.")

    def export_result(self):
        if not self.report:return
        target,_=QFileDialog.getSaveFileName(self,'Guardar informe R5C',
                    'Conciliacion_COVEX_R5C.zip','ZIP (*.zip)')
        if not target:return
        try:
            from ..master_reconciliation import export_report
            result=export_report(self.api,self.path,self.report,target)
            QMessageBox.information(self,'Informe verificado',
                f"ZIP creado con {result['rows']} filas del libro y evidencia SHA-256. "
                'No equivale a una aprobación documental ni a un backup.')
        except Exception as ex:QMessageBox.warning(self,'Exportación no realizada',str(ex))
