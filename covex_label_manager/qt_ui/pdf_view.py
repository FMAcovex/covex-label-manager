"""Real PDF pages, shared by emission and history; never a parallel compositor."""
from PySide6.QtWidgets import QWidget,QHBoxLayout,QComboBox
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from .window import Preview,button,label,vbox


class PdfPane(QWidget):
    def __init__(self,api,parent=None):
        super().__init__(parent);self.api=api;self.path=None;self.page_count=0;self.validator=None
        layout=vbox(self,0,8);top=QHBoxLayout();self.title=label('Vista previa A4','panelTitle');top.addWidget(self.title,1)
        self.pages=QComboBox();self.pages.setMinimumWidth(105);self.pages.currentIndexChanged.connect(self.page_changed);top.addWidget(self.pages)
        layout.addLayout(top);tools=QHBoxLayout()
        self.view=Preview();self.zoom=label('Vista 100 %','subtle');self.view.zoom_label=self.zoom
        tools.addWidget(button('Ajustar',self.view.fit));tools.addWidget(button('−',lambda:self.view.zoom(1/1.2)));tools.addWidget(button('+',lambda:self.view.zoom(1.2)));tools.addWidget(self.zoom);tools.addStretch()
        self.open_button=button('Abrir PDF',self.open_pdf);self.open_button.setEnabled(False);tools.addWidget(self.open_button);layout.addLayout(tools)
        layout.addWidget(self.view,1);self.note=label('Actualice la vista previa con los datos del trabajo.','subtle');layout.addWidget(self.note)
    def clear(self,message='Los datos han cambiado. Actualice la vista previa.'):
        self.path=None;self.page_count=0;self.validator=None;self.view.scene().clear();self.pages.blockSignals(True);self.pages.clear();self.pages.blockSignals(False);self.open_button.setEnabled(False);self.note.setText(message)
    def load(self,path,title='Vista previa A4',note=''):
        image,count=self.api.pdf_page(path,0,maxwidth=1600);self.path=path;self.page_count=count
        self.title.setText(title);self.pages.blockSignals(True);self.pages.clear()
        for n in range(count):self.pages.addItem(f'Página {n+1} de {count}',n)
        self.pages.blockSignals(False);self.view.set_image(image);self.note.setText(note);self.note.setWordWrap(True);self.open_button.setEnabled(True)
    def verified(self):
        try:
            if self.validator:self.validator()
            return True
        except Exception as ex:self.clear('PDF bloqueado: '+str(ex));return False
    def page_changed(self,index):
        if self.path is not None and index>=0 and self.verified():
            try:image,_=self.api.pdf_page(self.path,index,maxwidth=1600);self.view.set_image(image)
            except Exception as ex:self.clear('No se puede mostrar el PDF: '+str(ex))
    def open_pdf(self):
        if self.path is not None and self.verified():return QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.path)))
        return False
