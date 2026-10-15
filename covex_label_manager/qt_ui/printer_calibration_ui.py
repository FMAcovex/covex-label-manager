"""Native Qt interactive calibration from measured nonproductive reference marks."""
import uuid
from copy import deepcopy
from PySide6.QtWidgets import (
    QDialog,QFormLayout,QLineEdit,QDialogButtonBox,QVBoxLayout,QHBoxLayout,QMessageBox
)
from .window import label,button,vbox
from .pdf_view import PdfPane
from ..printer_calibration import calibrated,numeric


class CalibrationDialog(QDialog):
    def __init__(self,parent,api,profile):
        super().__init__(parent)
        self.api=api;self.original=deepcopy(profile);self.profile=deepcopy(profile)
        self.setWindowTitle('Calibrar impresora · Prueba no productiva')
        self.resize(670,570)
        layout=vbox(self,14,9)
        note=label('1. Genere una hoja de prueba en papel nuevo. Imprima al 100 % (sin ajustar). '
                   '2. Mida desde el borde superior izquierdo la posición REAL de la esquina '
                   'superior izquierda de la casilla 1. '
                   '3. Introduzca la posición esperada y la medida en mm. '
                   'Se corregirá el desplazamiento X/Y, nunca el tamaño del documento.','subtle')
        note.setWordWrap(True);layout.addWidget(note)
        form=QFormLayout();layout.addLayout(form)
        self.printer=QLineEdit(profile.get('printer_name',''))
        self.printer.setPlaceholderText('Modelo / cola de impresora exacta')
        form.addRow('Impresora (obligatoria)',self.printer)
        from ..sheet_layout import slots
        from ..engine import plan_sheet
        try:
            plan=plan_sheet(profile,1);first=slots(profile,plan.cols,plan.rows)[0]
            self.reference=(first.x,first.y)
        except (ValueError,KeyError,TypeError):
            self.reference=(0.,0.)
        self.inputs={}
        for key,title,initial in [('reference_x','X esperada (mm)',self.reference[0]),
                                  ('reference_y','Y esperada (mm)',self.reference[1]),
                                  ('measured_x','X medida en papel (mm)',self.reference[0]),
                                  ('measured_y','Y medida en papel (mm)',self.reference[1])]:
            entry=QLineEdit(str(round(initial,3)));self.inputs[key]=entry;form.addRow(title,entry)
        self.status=label('PDF de calibración = muestra no productiva. La impresión física nunca se confirma automáticamente.','subtle')
        self.status.setWordWrap(True);layout.addWidget(self.status)
        actions=QHBoxLayout();actions.addWidget(button('Generar PDF de calibración',self.proof));actions.addStretch()
        layout.addLayout(actions)
        self.box=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        self.box.button(QDialogButtonBox.StandardButton.Ok).setText('Aplicar al trabajo (sin aprobar)')
        self.box.accepted.connect(self.accept_calibration);self.box.rejected.connect(self.reject)
        layout.addWidget(self.box)
    def proof(self):
        try:
            destination=self.api.output_path('cache','calibration-'+uuid.uuid4().hex+'.pdf')
            # A calibration PDF is not an issuance and cannot alter master assets.
            self.api.calibration(self.original,destination)
            dlg=QDialog(self);dlg.setWindowTitle('Hoja de calibración no productiva')
            dlg.resize(770,620);lay=vbox(dlg,10)
            pane=PdfPane(self.api);lay.addWidget(pane,1)
            pane.load(destination,'Calibración · no productiva','Imprimir al 100 %. La prueba no registra emisión.')
            close=QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
            close.rejected.connect(dlg.reject);lay.addWidget(close);dlg.exec()
        except (OSError,ValueError) as ex:
            self.status.setText('No se pudo generar la hoja de calibración: '+str(ex))
    def accept_calibration(self):
        try:
            entries={k:numeric(v.text()) for k,v in self.inputs.items()}
            self.profile=calibrated(self.original,self.printer.text(),
                entries['measured_x'],entries['measured_y'],
                entries['reference_x'],entries['reference_y'])
            from ..engine import plan_sheet
            plan_sheet(self.profile,1)
            # Explicitly no automatic calibration approval or new master revision.
            self.accept()
        except (ValueError,KeyError,TypeError) as ex:
            self.status.setText('Calibración no aplicada: '+str(ex))
