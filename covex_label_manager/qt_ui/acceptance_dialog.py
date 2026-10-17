"""Qt R6A read-only pre-acceptance inspection and template export."""
from PySide6.QtWidgets import QDialog,QFileDialog,QMessageBox,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QDialogButtonBox,QHBoxLayout
from .window import vbox,label,button
from .responsive import AdaptiveDialog as QDialog
class ReadinessDialog(QDialog):
    def __init__(self,parent,api):
        super().__init__(parent);self.api=api;self.report=None
        self.setWindowTitle('R6A - Diagnóstico de preaceptación');self.resize(1040,650)
        layout=vbox(self,14,9)
        layout.addWidget(label('Preaceptación técnica: NO es validación GMP','panelTitle'))
        note=label('Las pruebas físicas y Word real quedan SIN EJECUTAR. No se modifica SQLite ni se aprueban documentos.','subtle')
        note.setWordWrap(True);layout.addWidget(note)
        self.status=label('Ejecute el diagnóstico cuando desee.','subtle');layout.addWidget(self.status)
        self.table=QTableWidget(0,5);self.table.setHorizontalHeaderLabels(['Área','Referencia','Control','Estado','Detalle'])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True);layout.addWidget(self.table,1)
        bar=QHBoxLayout();bar.addWidget(button('Ejecutar diagnóstico',self.run,'primary'))
        self.export_button=button('Exportar evidencias ZIP…',self.export_zip)
        self.export_button.setEnabled(False);bar.addWidget(self.export_button);bar.addStretch();layout.addLayout(bar)
        close=QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close.rejected.connect(self.reject);layout.addWidget(close)
    def run(self):
        try:self.report=self.api.acceptance_preflight()
        except Exception as ex:
            self.report=None;self.export_button.setEnabled(False)
            QMessageBox.warning(self,'Diagnóstico no realizado',str(ex));return
        summary=self.report['summary']
        self.status.setText(f"{summary['pass']} conformes, {summary['fail']} incidencias, {summary['review']} a revisar. "
            f"{summary['manual_open']} pruebas manuales sin ejecutar. ESTADO GLOBAL: NO ACEPTADO.")
        rows=self.report['checks'];self.table.setRowCount(len(rows))
        for i,row in enumerate(rows):
            for j,k in enumerate(('group','subject','code','status','detail')):
                item=QTableWidgetItem(str(row[k]));item.setToolTip(str(row[k]));self.table.setItem(i,j,item)
        self.export_button.setEnabled(True)
    def export_zip(self):
        if not self.report:return
        filename,_=QFileDialog.getSaveFileName(self,'Guardar diagnóstico R6A','COVEX_R6A_preaceptacion.zip','ZIP (*.zip)')
        if not filename:return
        if QMessageBox.question(self,'Datos internos','El informe incluye referencias documentales internas. '
            'Guárdelo en un lugar autorizado. No acredita uso GMP. ¿Continuar?',
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Yes:return
        try:
            r=self.api.acceptance_export(self.report,filename)
            QMessageBox.information(self,'Paquete creado',
                f"{r['checks']} controles y {r['manual']} pruebas manuales PENDIENTES. "
                'No constituye aceptación GMP.')
        except Exception as ex:QMessageBox.warning(self,'Exportación fallida',str(ex))
