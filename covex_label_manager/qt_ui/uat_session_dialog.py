"""R6B native Qt field UAT wizard; no automated GMP acceptance."""
from datetime import date
from pathlib import Path
from PySide6.QtWidgets import (QDialog,QFileDialog,QMessageBox,QLineEdit,QComboBox,
    QPlainTextEdit,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,
    QFormLayout,QHBoxLayout,QDialogButtonBox,QWidget,QSplitter)
from PySide6.QtCore import Qt
from .window import vbox,label,button
from .responsive import AdaptiveDialog as QDialog

STATES=(('Sin ejecutar','NOT_EXECUTED'),('Conforme','PASS'),('No conforme','FAIL'),
        ('Bloqueada','BLOCKED'),('No aplicable','NOT_APPLICABLE'))

class UatSessionDialog(QDialog):
    def __init__(self,parent,api):
        super().__init__(parent);self.api=api;self.path=None;self.report=None;self.evidence_path=None
        self.setWindowTitle('R6B · Pruebas presenciales y evidencias');self.resize(1190,790)
        layout=vbox(self,14,9)
        layout.addWidget(label('Registro de aceptación presencial · NO ACEPTADO','panelTitle'))
        note=label('Cada resultado requiere comprobación real por un responsable. '
            'No imprime, no aprueba diseños ni altera datos GMP. '
            'Los registros y evidencias deben conservarse fuera de data.','subtle')
        note.setWordWrap(True);layout.addWidget(note)
        actions=QHBoxLayout()
        actions.addWidget(button('Nueva sesión desde R6A…',self.new_session))
        actions.addWidget(button('Abrir sesión JSON…',self.open_session))
        self.verify_button=button('Verificar evidencias',self.verify)
        self.verify_button.setEnabled(False);actions.addWidget(self.verify_button)
        actions.addStretch();layout.addLayout(actions)
        self.summary=label('Seleccione un paquete R6A o abra una sesión existente.','subtle')
        self.summary.setWordWrap(True);layout.addWidget(self.summary)
        split=QSplitter(Qt.Orientation.Horizontal)
        self.table=QTableWidget(0,3)
        self.table.setHorizontalHeaderLabels(['Prueba','Área','Resultado'])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.itemSelectionChanged.connect(self.select_case)
        split.addWidget(self.table)
        editor=QWidget();form=QFormLayout(editor)
        self.criterion=label('Seleccione una prueba.','subtle');self.criterion.setWordWrap(True)
        form.addRow('Criterio',self.criterion)
        self.outcome=QComboBox()
        for caption,state in STATES:self.outcome.addItem(caption,state)
        form.addRow('Resultado',self.outcome)
        self.tester=QLineEdit();form.addRow('Responsable',self.tester)
        self.when=QLineEdit();self.when.setPlaceholderText('AAAA-MM-DD')
        form.addRow('Fecha de realización',self.when)
        self.notes=QPlainTextEdit();self.notes.setPlaceholderText('Observaciones, incidencia o motivo')
        form.addRow('Observaciones',self.notes)
        evidence=QHBoxLayout()
        self.evidence=QLineEdit();self.evidence.setReadOnly(True)
        evidence.addWidget(self.evidence,1)
        evidence.addWidget(button('Seleccionar archivo…',self.choose_evidence))
        form.addRow('Nueva evidencia',evidence)
        self.existing=label('Evidencias: —','subtle');self.existing.setWordWrap(True)
        form.addRow('Registradas',self.existing)
        self.save_button=button('Guardar nueva generación',self.save_case,'primary')
        self.save_button.setEnabled(False)
        split.addWidget(editor);split.setSizes([480,650]);layout.addWidget(split,1)
        layout.addWidget(self.save_button)
        footer=QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        footer.rejected.connect(self.reject);layout.addWidget(footer)

    def _warn(self,action,error):
        QMessageBox.warning(self,action,str(error))

    def new_session(self):
        pack,_=QFileDialog.getOpenFileName(self,'Paquete R6A verificado','','ZIP (*.zip)')
        if not pack:return
        dialog=QDialog(self);dialog.setWindowTitle('Identificación del equipo y portable')
        body=vbox(dialog);form=QFormLayout()
        fields={}
        for key,title in [('machine','Equipo / identificador'),('windows','Windows / versión'),
                          ('tester','Operador responsable'),('commit','Commit Git (40 hex)'),
                          ('portable_sha256','SHA-256 portable (64 hex)')]:
            widget=QLineEdit();widget.setPlaceholderText(title)
            fields[key]=widget;form.addRow(title,widget)
        body.addLayout(form)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject)
        body.addWidget(buttons)
        if dialog.exec()!=QDialog.DialogCode.Accepted:return
        destination,_=QFileDialog.getSaveFileName(self,'Nueva sesión externa a data',
                'R6B_sesion_01.json','JSON (*.json)')
        if not destination:return
        try:
            self.api.uat_create(pack,destination,{k:w.text().strip() for k,w in fields.items()})
            self.load(destination)
        except Exception as ex:self._warn('No se ha creado la sesión',ex)

    def open_session(self):
        source,_=QFileDialog.getOpenFileName(self,'Abrir generación UAT','','JSON (*.json)')
        if not source:return
        try:self.load(source)
        except Exception as ex:self._warn('No se ha abierto la sesión',ex)

    def load(self,path,preferred=None):
        report=self.api.uat_read(path)
        self.path=str(path);self.report=report
        self.evidence_path=None;self.evidence.clear()
        self.table.blockSignals(True);self.table.setRowCount(len(report['cases']))
        for i,item in enumerate(report['cases']):
            for j,value in enumerate((item['id'],item['area'],item['status'])):
                cell=QTableWidgetItem(value);cell.setToolTip(value)
                self.table.setItem(i,j,cell)
        self.table.blockSignals(False)
        completed=sum(c['status']=='PASS' for c in report['cases'])
        open_count=sum(c['status']=='NOT_EXECUTED' for c in report['cases'])
        self.summary.setText(f"Generación {report['generation']} · {completed} conformes · "
            f"{open_count} sin ejecutar · {len(report['cases'])} pruebas · "
            'ESTADO GLOBAL: NO ACEPTADO. Archivo: '+str(path))
        self.verify_button.setEnabled(True)
        index=next((i for i,c in enumerate(report['cases']) if c['id']==preferred),0)
        self.table.selectRow(index);self.select_case()

    def select_case(self):
        if not self.report:return
        row=self.table.currentRow()
        if row<0 or row>=len(self.report['cases']):return
        item=self.report['cases'][row]
        self.criterion.setText(item['criterion'])
        self.outcome.setCurrentIndex(self.outcome.findData(item['status']))
        self.tester.setText(item['tester'])
        self.when.setText(item['date'])
        self.notes.setPlainText(item['notes'])
        self.existing.setText('Evidencias: '+(', '.join(x['name'] for x in item['evidence'])
                                   if item['evidence'] else 'ninguna'))
        self.evidence_path=None;self.evidence.clear();self.save_button.setEnabled(True)

    def choose_evidence(self):
        if not self.report:return
        path,_=QFileDialog.getOpenFileName(self,'Evidencia externa controlada')
        if path:self.evidence_path=path;self.evidence.setText(path)

    def save_case(self):
        if not self.report or self.table.currentRow()<0:return
        item=self.report['cases'][self.table.currentRow()]
        outcome=self.outcome.currentData()
        if outcome=='PASS' and not (self.evidence_path or item['evidence']):
            self._warn('Evidencia obligatoria','Un resultado conforme requiere evidencia documental.')
            return
        if QMessageBox.question(self,'Confirmar resultado manual',
            f"Registrar {item['id']} como {outcome}. Se creará otra generación JSON "
            'sin sobrescribir las anteriores. ¿Continuar?',
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Yes:return
        try:
            path=self.api.uat_update(self.path,self.report['generation'],item['id'],outcome,
                tester=self.tester.text(),when=self.when.text().strip(),
                notes=self.notes.toPlainText(),evidence=self.evidence_path)
            self.load(path,preferred=item['id'])
        except Exception as ex:self._warn('Resultado no registrado',ex)

    def verify(self):
        if not self.report:return
        errors=self.api.uat_verify(self.report)
        if errors:self._warn('Evidencias ausentes o alteradas','Casos: '+', '.join(errors))
        else:QMessageBox.information(self,'Evidencias verificadas',
            'Las huellas de los archivos referenciados coinciden. '
            'No demuestra que la prueba física haya sido realizada.')
