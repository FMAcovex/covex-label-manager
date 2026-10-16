"""R5A inventory and export: deliberate, read-only Qt actions."""
import json
from pathlib import Path
from PySide6.QtWidgets import QFileDialog,QMessageBox,QDialog,QPlainTextEdit,QDialogButtonBox

from .window import vbox,label


class CatalogExchangeMixin:
    def review_catalog_folder(self):
        if self.legacy_process or not self.flush_emission_work() or not self.resolve_work():return
        folder=QFileDialog.getExistingDirectory(self,'Inventario de etiquetas (sin importar)')
        if not folder:return
        try:
            report=self.api.catalog_inventory(folder)
            dialog=QDialog(self);dialog.setWindowTitle('R5A · Inventario previo (solo lectura)')
            dialog.resize(910,650);layout=vbox(dialog)
            note=label('La detección de coincidencias por nombre/revisión es orientativa. '
                       'Este informe NO aprueba ni importa etiquetas.','subtle')
            note.setWordWrap(True);layout.addWidget(note)
            editor=QPlainTextEdit(json.dumps(report,ensure_ascii=False,indent=2))
            editor.setReadOnly(True);layout.addWidget(editor,1)
            buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
            buttons.rejected.connect(dialog.reject);layout.addWidget(buttons)
            dialog.exec()
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
