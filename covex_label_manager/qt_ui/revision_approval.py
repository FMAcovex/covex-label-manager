"""Explicit Qt documentary-approval registration (not electronic signing)."""
from PySide6.QtWidgets import (QDialog,QFormLayout,QLineEdit,QCheckBox,QDialogButtonBox,
    QMessageBox,QPushButton)
from .window import vbox,label

class RevisionApprovalDialog(QDialog):
    def __init__(self,parent,api,version):
        super().__init__(parent);self.api=api;self.version=dict(version)
        self.setWindowTitle('Registrar aprobación documental · revisión pendiente')
        self.resize(610,440)
        layout=vbox(self,18,12)
        layout.addWidget(label('Registrar aprobación externa','panelTitle'))
        info=label(f"Etiqueta: {version['name']} · Código: {version['code']} · "
            f"Revisión: {version['version']} · Estado: PENDIENTE",'subtle')
        info.setWordWrap(True);layout.addWidget(info)
        self.notice=label('Este registro no constituye firma electrónica ni sustituye la '
            'aprobación documental externa. Verifique previamente el Word/PDF maestro '
            'y la referencia aprobada.','subtle')
        self.notice.setWordWrap(True);layout.addWidget(self.notice)
        current=next((dict(v) for v in api.versions(version['label_id'])
                      if v['state']=='APPROVED' and v['id']!=version['id']),None)
        self.previous=current
        if current:
            warning=label(f"Atención: la revisión vigente {current['version']} pasará "
                          "automáticamente a RETIRADA cuando se registre la nueva aprobación.",'fieldError')
            warning.setWordWrap(True);layout.addWidget(warning)
        form=QFormLayout();self.reviewer=QLineEdit();self.reviewer.setPlaceholderText('Responsable de la aprobación documental')
        self.reference=QLineEdit();self.reference.setPlaceholderText('Referencia externa aprobada, al menos 5 caracteres')
        form.addRow('Responsable *',self.reviewer);form.addRow('Referencia de aprobación *',self.reference)
        layout.addLayout(form)
        self.confirm=QCheckBox('Confirmo que la aprobación documental externa existe, '
                               'corresponde a esta revisión y he revisado su diseño.')
        self.confirm.setWordWrap(True);layout.addWidget(self.confirm)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self.accept_button=QPushButton('Registrar aprobación');buttons.addButton(self.accept_button,QDialogButtonBox.ButtonRole.AcceptRole)
        self.accept_button.clicked.connect(self.commit);buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.reviewer.textChanged.connect(self.update_state);self.reference.textChanged.connect(self.update_state)
        self.confirm.toggled.connect(self.update_state);self.update_state()

    def update_state(self,*_):
        self.accept_button.setEnabled(len(self.reviewer.text().strip())>=3 and
                                      len(self.reference.text().strip())>=5 and self.confirm.isChecked())

    def commit(self):
        if not self.accept_button.isEnabled():return
        current=self.api.version(self.version['id'])
        if not current or current['state']!='PENDING':
            QMessageBox.warning(self,'Estado documental cambiado',
                'La revisión ya no está pendiente. Actualice la biblioteca.');return
        if current['pdf_sha256']!=self.version['pdf_sha256'] or current['source_sha256']!=self.version['source_sha256']:
            QMessageBox.warning(self,'Fuente documental cambiada',
                'La fuente cambió. Reabra la revisión y vuelva a comprobarla.');return
        message=(f"¿Registrar la aprobación documental externa de {current['name']} "
                 f"· revisión {current['version']}?\n\n"
                 f"Responsable: {self.reviewer.text().strip()}\n"
                 f"Referencia: {self.reference.text().strip()}\n\n"
                 + (f"La revisión vigente {self.previous['version']} quedará RETIRADA.\n\n"
                    if self.previous else '')
                 + 'Esta acción se registra en auditoría y no es una firma electrónica.')
        if QMessageBox.question(self,'Confirmar aprobación documental',message,
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Yes:return
        try:
            # The repository independently verifies state, hashes and renderability.
            self.api.approve(current['id'],self.reviewer.text().strip(),self.reference.text().strip())
        except (ValueError,PermissionError,OSError) as ex:
            QMessageBox.warning(self,'Aprobación no registrada',str(ex));return
        self.accept()
