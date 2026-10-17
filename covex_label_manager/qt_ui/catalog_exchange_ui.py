"""R5A inventory and export: deliberate, read-only Qt actions."""
import json
from pathlib import Path
from PySide6.QtWidgets import (QFileDialog,QMessageBox,QPlainTextEdit,QDialogButtonBox,
    QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QPushButton)

from .window import vbox,label
from .responsive import AdaptiveDialog as QDialog


class InventoryReportDialog(QDialog):
    """Human-readable inventory with the original, unchanged technical report."""
    def __init__(self,parent,report):
        super().__init__(parent)
        self.setWindowTitle('Inventario previo · Solo lectura');self.resize(910,650)
        layout=vbox(self)
        note=label('Las coincidencias por nombre/revisión son orientativas. '
                   'Este informe NO aprueba ni importa etiquetas.','subtle')
        note.setWordWrap(True);layout.addWidget(note)
        names={'EXACT_DUPLICATE':'Duplicado exacto','IDENTITY_CONFLICT':'Coincidencia de nombre/revisión',
               'REVIEW_REQUIRED':'Requiere revisión','BLOCKED_SYMLINK':'Enlace bloqueado'}
        self.summary=label(' · '.join(f"{name}: {report['counts'].get(key,0)}" for key,name in names.items()),'subtle')
        self.summary.setWordWrap(True);layout.addWidget(self.summary)
        self.table=QTableWidget(len(report['files']),4)
        self.table.setAccessibleName('Resultado del inventario de archivos')
        self.table.setHorizontalHeaderLabels(['Archivo','Nombre propuesto','Revisión','Resultado'])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for row,entry in enumerate(report['files']):
            values=(entry['path'],entry.get('name','—'),entry.get('version','—'),names.get(entry['status'],entry['status']))
            for col,value in enumerate(values):
                item=QTableWidgetItem(str(value));item.setToolTip(str(value));self.table.setItem(row,col,item)
        layout.addWidget(self.table,1)
        self.details=QPlainTextEdit(json.dumps(report,ensure_ascii=False,indent=2))
        self.details.setReadOnly(True);self.details.setAccessibleName('Informe técnico JSON íntegro')
        self.details.setMaximumHeight(180);self.details.hide()
        toggle=QPushButton('Mostrar detalle técnico JSON');toggle.setCheckable(True)
        toggle.toggled.connect(self.details.setVisible)
        toggle.toggled.connect(lambda visible:toggle.setText('Ocultar detalle técnico JSON' if visible else 'Mostrar detalle técnico JSON'))
        layout.addWidget(toggle);layout.addWidget(self.details)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject);layout.addWidget(buttons)


class CatalogExchangeMixin:
    def review_catalog_folder(self):
        if self.legacy_process or not self.flush_emission_work() or not self.resolve_work():return
        folder=QFileDialog.getExistingDirectory(self,'Inventario de etiquetas (sin importar)')
        if not folder:return
        try:
            report=self.api.catalog_inventory(folder)
            InventoryReportDialog(self,report).exec()
        except Exception as ex:QMessageBox.warning(self,'Inventario no disponible',str(ex))

    def export_entire_library(self):
        if self.legacy_process or not self.flush_emission_work() or not self.resolve_work():return
        target,_=QFileDialog.getSaveFileName(self,'Exportar catálogo completo (no es backup)',
                                            'COVEX_catalogo_etiquetas.zip','ZIP (*.zip)')
        if not target:return
        if QMessageBox.question(self,'Confirmar exportación documental',
                'Se incluirán originales y PDF maestros de TODAS las revisiones, '
                'incluidas pendientes y retiradas. El ZIP puede contener información '
                'confidencial. Guárdelo en una ubicación autorizada. ¿Continuar?',
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Yes:return
        try:
            result=self.api.catalog_export(target)
            QMessageBox.information(self,'Exportación verificada',
                f"Exportadas {result['revisions']} revisiones y {result['assets']} activos."
                '\nEste ZIP NO es una copia de seguridad para restaurar la aplicación.')
        except Exception as ex:QMessageBox.warning(self,'Exportación no realizada',str(ex))

    def reconcile_master(self):
        if self.legacy_process or not self.flush_emission_work() or not self.resolve_work():return
        path,_=QFileDialog.getOpenFileName(self,'Seleccionar libro máster local',
            '','Libro de etiquetas (*.xlsx *.csv *.tsv)')
        if not path:return
        try:
            from .master_reconcile_ui import MasterReconciliationDialog
            MasterReconciliationDialog(self,self.api,path).exec()
        except Exception as ex:QMessageBox.warning(self,'Conciliación no iniciada',str(ex))
