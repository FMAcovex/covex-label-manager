"""Qt-only presentation helpers; no document, database or emission decisions."""
from PySide6.QtCore import QSize, QPoint, QTranslator, QLibraryInfo
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QAbstractButton, QWidget,
    QVBoxLayout, QScrollArea, QSizePolicy, QLayout, QFormLayout, QLineEdit,
    QComboBox, QPlainTextEdit, QAbstractSpinBox, QApplication)


def install_translation(app):
    retain_screens(app)
    if not hasattr(app, '_covex_standard_buttons'):
        translator=QTranslator(app)
        translator.load('qtbase_es',QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath))
        app._covex_standard_buttons=translator
        if not translator.isEmpty():app.installTranslator(translator)


def retain_screens(app):
    """Keep PySide QScreen wrappers alive for the QApplication's lifetime.

    In PySide 6.8.3 a collected transient QWidget.screen() wrapper can delete
    the native QScreen while Qt still lists it. A subsequent QWidget then
    crashes in QScreen::virtualSiblings. Track hotplug without owning/deleting
    monitors or changing their geometry, DPI or resolution.
    """
    if not hasattr(app, '_covex_screens'):
        app._covex_screens = []
        def refresh(*_):
            app._covex_screens[:] = app.screens()
        app.screenAdded.connect(refresh)
        app.screenRemoved.connect(refresh)
    # QWidget destruction may invalidate an existing wrapper; reacquire the
    # current application-owned wrappers, rather than retaining a stale list.
    app._covex_screens[:] = app.screens()


def translate_buttons(root):
    captions = {
        QDialogButtonBox.StandardButton.Ok: 'Aceptar',
        QDialogButtonBox.StandardButton.Cancel: 'Cancelar',
        QDialogButtonBox.StandardButton.Close: 'Cerrar',
        QDialogButtonBox.StandardButton.Save: 'Guardar',
    }
    for box in root.findChildren(QDialogButtonBox):
        for standard, caption in captions.items():
            control = box.button(standard)
            # Preserve task-specific captions such as Registrar aprobación.
            if control and control.text().replace('&', '') in ('OK', 'Ok', 'Cancel', 'Close', 'Save'):
                control.setText(caption)


def _footer(item):
    widget = item.widget()
    if widget:
        return isinstance(widget, (QDialogButtonBox, QAbstractButton))
    layout = item.layout()
    if not layout:
        return False
    children = [layout.itemAt(i) for i in range(layout.count())]
    return any(x.widget() for x in children) and all(
        x.spacerItem() is not None or _footer(x) for x in children)


class AdaptiveDialog(QDialog):
    """Scrollable content and a persistent action footer, sized in logical pixels.

    Existing layouts/signals/validation remain owned by their original callers.
    The wrapping is deferred until show so dynamically built dialogs are complete.
    """
    def prepare_layout(self):
        retain_screens(QApplication.instance())
        if getattr(self, '_adaptive_ready', False) or self.layout() is None:
            return
        self._adaptive_ready = True
        root = self.layout()
        items = []
        while root.count():
            items.append(root.takeAt(0))
        footer = []
        while items and _footer(items[-1]):
            footer.insert(0, items.pop())
        body = QWidget(self)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        for item in items:
            if item.widget():
                layout.addWidget(item.widget())
            elif item.layout():
                item.layout().setParent(None)
                layout.addLayout(item.layout())
            else:
                layout.addItem(item)
        for form in body.findChildren(QFormLayout):
            form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
            form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
            accessible_form(form)
        self.content_scroll = QScrollArea(self)
        self.content_scroll.setObjectName('dialogContent')
        self.content_scroll.setWidgetResizable(True)
        self.content_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.content_scroll.setMinimumSize(0, 40)
        self.content_scroll.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        self.content_scroll.setWidget(body)
        root.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        root.addWidget(self.content_scroll, 1)
        self.footer_widgets = []
        for item in footer:
            if item.widget():
                root.addWidget(item.widget())
                self.footer_widgets.append(item.widget())
            elif item.layout():
                root.addLayout(item.layout())
                self.footer_widgets.extend(item.layout().itemAt(i).widget()
                    for i in range(item.layout().count()) if item.layout().itemAt(i).widget())
        translate_buttons(self)
        self.setMinimumSize(0, 0)

    def fit_available(self, size=None):
        self.prepare_layout()
        if size is None:
            # QWidget.screen() binds the wrapper to this transient dialog in
            # PySide 6.8.3. Query via QApplication, whose lifetime is stable.
            screen = QApplication.screenAt(self.mapToGlobal(QPoint(self.width()//2,self.height()//2))) or QApplication.primaryScreen()
            available = screen.availableGeometry().size() - QSize(24, 48)
        else:
            available = size
        wanted=self.width()
        if hasattr(self,'content_scroll'):
            margins=self.layout().contentsMargins()
            wanted=max(wanted,self.content_scroll.widget().minimumSizeHint().width()+margins.left()+margins.right()+16)
        self.resize(min(wanted, available.width()), min(self.height(), available.height()))

    def showEvent(self, event):
        self.fit_available()
        super().showEvent(event)

    def setVisible(self, visible):
        # Establish QObject/layout ownership before Qt enters native show/event
        # handling (including QDialog.exec), not while processing showEvent.
        if visible:
            self.prepare_layout()
        super().setVisible(visible)


def accessible_form(form):
    """Expose explicit field names as well as Qt's native form associations."""
    for row in range(form.rowCount()):
        label_item = form.itemAt(row, QFormLayout.ItemRole.LabelRole)
        field_item = form.itemAt(row, QFormLayout.ItemRole.FieldRole)
        if label_item and label_item.widget() and field_item and field_item.widget():
            caption = label_item.widget().text().replace('&', '').rstrip(': *')
            field_item.widget().setAccessibleName(caption)
            for control in field_item.widget().findChildren(QWidget):
                if isinstance(control,(QLineEdit,QComboBox,QPlainTextEdit,QAbstractSpinBox)) and not control.accessibleName():
                    control.setAccessibleName(caption)
