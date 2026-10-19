"""Real PDF pages, shared by emission and history; never a parallel compositor."""
from PySide6.QtWidgets import QWidget,QHBoxLayout,QComboBox,QDialog,QDialogButtonBox,QVBoxLayout,QSizePolicy
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import Qt,QUrl
from .window import Preview,button,label,vbox
from .responsive import AdaptiveDialog as QDialog


class PdfPane(QWidget):
    def __init__(self,api,parent=None):
        super().__init__(parent);self.api=api;self.path=None;self.page_count=0;self.validator=None
        layout=vbox(self,0,8);top=QHBoxLayout();self.header_layout=top;self._full_title='Vista previa PDF'
        self.title=label(self._full_title,'panelTitle');self.title.setWordWrap(False)
        self.title.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred);top.addWidget(self.title,1)
        self.pages=QComboBox();self.pages.setMinimumWidth(105);self.pages.setAccessibleName('Página del PDF');self.pages.currentIndexChanged.connect(self.page_changed);top.addWidget(self.pages)
        layout.addLayout(top);self.tools=QWidget();tools=QHBoxLayout(self.tools);tools.setContentsMargins(0,0,0,0)
        self.view=Preview();self.zoom=label('Vista 100 %','subtle');self.view.zoom_label=self.zoom
        tools.addWidget(button('Ajustar',self.view.fit));tools.addWidget(button('−',lambda:self.view.zoom(1/1.2)));tools.addWidget(button('+',lambda:self.view.zoom(1.2)));tools.addWidget(self.zoom);tools.addStretch();self.expand_button=button('Ampliar PDF',self.expand_pdf)
        self.expand_button.setToolTip('Abrir el PDF completo para comprobar el diseño y las etiquetas')
        self.expand_button.setEnabled(False)
        self.expand_button.setStyleSheet('background:#E4F1ED;color:#116C62;border:1px solid #B8DCD3;font-weight:700;')
        top.addWidget(self.expand_button)
        self.open_button=button('Abrir PDF',self.open_pdf);self.open_button.setEnabled(False);tools.addWidget(self.open_button);layout.addWidget(self.tools)
        layout.addWidget(self.view,1);self.note=label('Actualice la vista previa con los datos del trabajo.','subtle');layout.addWidget(self.note)
    def clear(self,message='Los datos han cambiado. Actualice la vista previa.'):
        self.path=None;self.page_count=0;self.validator=None;self.view.scene().clear();self.pages.blockSignals(True);self.pages.clear();self.pages.blockSignals(False);self.open_button.setEnabled(False);self.expand_button.setEnabled(False);self.note.setText(message)
    def load(self,path,title='Vista previa PDF',note=''):
        image,count=self.api.pdf_page(path,0,maxwidth=1600);self.path=path;self.page_count=count
        self._full_title=title;self.title.setText(title);self.pages.blockSignals(True);self.pages.clear()
        for n in range(count):self.pages.addItem(f'Página {n+1} de {count}',n)
        self.pages.blockSignals(False);self.view.set_image(image);self.note.setText(note);self.note.setWordWrap(True);self.open_button.setEnabled(True);self.expand_button.setEnabled(True);self.elide_title()
    def compact(self,enabled):
        self.tools.show();self.note.show()
        if enabled and not getattr(self,'_compact_tools',False):
            self.layout().removeWidget(self.tools)
            self.header_layout.insertWidget(1,self.tools)
        elif not enabled and getattr(self,'_compact_tools',False):
            self.header_layout.removeWidget(self.tools)
            self.layout().insertWidget(1,self.tools)
        self._compact_tools=enabled
        self.tools.layout().setSpacing(4 if enabled else 8)
        for control in self.tools.findChildren(QWidget):
            if hasattr(control,'setAccessibleName') and hasattr(control,'text'):
                text=control.text()
                if text in ('+','−'):control.setAccessibleName('Acercar vista PDF' if text=='+' else 'Alejar vista PDF')
        self.title.setStyleSheet('font-size:14px;' if enabled else '')
        self.elide_title()
    def elide_title(self):
        """Elide only the heading, never the operator controls or the original PDF."""
        if not hasattr(self,'expand_button'):return
        available=max(48,self.width()-self.pages.sizeHint().width()-self.expand_button.sizeHint().width()-36)
        title=self.title.fontMetrics().elidedText(self._full_title,Qt.TextElideMode.ElideRight,available)
        if self.title.text()!=title:self.title.setText(title)
        self.title.setToolTip(self._full_title)
    def resizeEvent(self,event):
        super().resizeEvent(event)
        self.elide_title()
    def expand_pdf(self):
        if self.path is None or not self.verified():return
        dialog=QDialog(self);dialog.setWindowTitle(self.title.text());layout=vbox(dialog,12,8);pane=PdfPane(self.api);pane.validator=self.validator;pane.expand_button.hide()
        layout.addWidget(pane,1);pane.load(self.path,self.title.text(),self.note.text());pane.pages.setCurrentIndex(self.pages.currentIndex())
        close=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);close.button(QDialogButtonBox.StandardButton.Close).setText('Cerrar');close.rejected.connect(dialog.reject);layout.addWidget(close)
        dialog.showMaximized();dialog.exec()
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


class EditorPdfPane(PdfPane):
    """PDF tools wrap inside a narrow Editor pane without enlarging its window.

    The normal emission/history toolbar remains unchanged. All commands keep
    their handlers and accessible names; no font shrink or hidden action.
    """
    def __init__(self,api,parent=None):
        super().__init__(api,parent)
        from PySide6.QtWidgets import QGridLayout
        old=self.tools;controls=[]
        while old.layout().count():
            item=old.layout().takeAt(0)
            if item.widget():controls.append(item.widget())
        index=self.layout().indexOf(old);self.layout().removeWidget(old)
        self.tools=QWidget();self._editor_tool_grid=QGridLayout(self.tools)
        self._editor_tool_grid.setContentsMargins(0,0,0,0);self._editor_tool_grid.setSpacing(4)
        self._editor_tool_controls=controls;self._editor_narrow=None
        self.layout().insertWidget(index,self.tools);old.hide();old.deleteLater()
        self.expand_button.setAccessibleName('Ampliar PDF completo')
        self.expand_button.setToolTip('Ampliar PDF completo para inspeccionar la etiqueta')
        self.reflow_editor_tools()

    def reflow_editor_tools(self):
        narrow=self.width()<480
        if narrow==self._editor_narrow:return
        grid=self._editor_tool_grid
        for control in self._editor_tool_controls:grid.removeWidget(control)
        for i,control in enumerate(self._editor_tool_controls):
            if narrow:
                row,column=(0,i) if i<3 else (1,0 if i==3 else 2)
                grid.addWidget(control,row,column,1,2 if i==3 else 1)
            else:grid.addWidget(control,0,i)
        self.expand_button.setText('Ampliar' if narrow else 'Ampliar PDF')
        self._editor_narrow=narrow

    def resizeEvent(self,event):
        if hasattr(self,'_editor_tool_controls'):self.reflow_editor_tools()
        super().resizeEvent(event)


def canvas_pdf_stack(canvas,pdf):
    """An inactive PDF page must not set the geometry canvas minimum width."""
    from PySide6.QtWidgets import QStackedWidget,QLayout
    stack=QStackedWidget()
    stack.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Expanding)
    stack.layout().setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
    stack.setMinimumWidth(canvas.minimumWidth())
    stack.addWidget(canvas);stack.addWidget(pdf)
    return stack
