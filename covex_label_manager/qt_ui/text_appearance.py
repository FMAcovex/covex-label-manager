"""Compact shared appearance controls; no replacement of documentary guards."""
from copy import deepcopy
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget,QFormLayout,QComboBox,QCheckBox,QLineEdit,QPushButton,QColorDialog,QHBoxLayout,QLabel
from ..typography import DEFAULT,FAMILIES,validate


class TextAppearance(QWidget):
    edited=Signal()
    def __init__(self,parent=None):
        super().__init__(parent);self.loading=False
        form=QFormLayout(self);form.setContentsMargins(0,0,0,0);form.setSpacing(5)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.family=QComboBox();self.family.addItem('Histórica · sin reinterpretar',None)
        self.family.setToolTip('Histórica conserva la ruta y métricas anteriores, que pueden depender del equipo. Las tres familias R8C usan recursos embebidos y verificados, sin fuentes del sistema.')
        for key,title in FAMILIES.items():self.family.addItem(title,key)
        self.family.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.family.setMinimumContentsLength(5);form.addRow('Fuente',self.family)
        self.italic=QCheckBox('Cursiva');form.addRow(self.italic)
        self.color=QLineEdit();self.color.setMaxLength(7);self.color.setPlaceholderText('#RRGGBB')
        self.swatch=QPushButton('Color…');row=QWidget();hl=QHBoxLayout(row);hl.setContentsMargins(0,0,0,0);hl.addWidget(self.color,1);hl.addWidget(self.swatch);form.addRow('Color',row)
        self.align=QComboBox();self.valign=QComboBox();self.wrap=QComboBox()
        for title,key in [('Izquierda','left'),('Centro','center'),('Derecha','right')]:self.align.addItem(title,key)
        for title,key in [('Arriba','top'),('Centro','middle'),('Abajo','bottom')]:self.valign.addItem(title,key)
        self.wrap.addItem('Ajustar por palabras','word');self.wrap.addItem('Una línea · bloquear exceso','none')
        form.addRow('Alineación',self.align);form.addRow('Vertical (cajas)',self.valign);form.addRow('Líneas',self.wrap)
        self.hint=QLabel('Sin reducción ni recorte de texto automático.');self.hint.setWordWrap(True);form.addRow(self.hint)
        self._controls=(self.italic,self.color,self.swatch,self.align,self.valign,self.wrap)
        self._baseline=False
        for combo in (self.family,self.align,self.valign,self.wrap):combo.activated.connect(self.changed)
        self.italic.toggled.connect(self.changed);self.color.editingFinished.connect(self.changed);self.swatch.clicked.connect(self.choose_color)
        self.load({})
        from .responsive import accessible_form
        accessible_form(form)

    def load(self,field):
        self.loading=True
        style=field.get('typography',DEFAULT)
        self.family.setCurrentIndex(max(0,self.family.findData(style['family'] if 'typography' in field else None)))
        self.italic.setChecked(style['italic']);self.color.setText(style['color'])
        for name in ('align','valign','wrap'):
            control=getattr(self,name);control.setCurrentIndex(control.findData(style[name]))
        self._baseline=field.get('draw') in ('baseline','continuation')
        self.loading=False;self.enable_controls()

    def enable_controls(self):
        active=self.family.currentData() is not None
        for widget in self._controls:widget.setEnabled(active)
        self.valign.setEnabled(active and not self._baseline)
        self.wrap.setEnabled(active and not self._baseline)
        self.wrap.setToolTip('La línea base no se divide; la continuación conserva su flujo documental. Use caja o párrafo para elegir ajuste de línea.' if self._baseline else 'Ajuste dentro de la caja sin reducir ni recortar texto.')
        self.valign.setToolTip('No aplicable a una línea base o continuación anclada.' if self._baseline else 'Alineación dentro del recuadro.')
        color=QColor(self.color.text())
        self.swatch.setStyleSheet('border-left:8px solid '+color.name()+';' if color.isValid() else '')

    def configuration(self):
        if self.family.currentData() is None:return None
        return validate(dict(DEFAULT,family=self.family.currentData(),italic=self.italic.isChecked(),
                             color=self.color.text(),align=self.align.currentData(),
                             valign='top' if self._baseline else self.valign.currentData(),wrap=self.wrap.currentData()))

    def changed(self,*_):
        if self.loading:return
        self.enable_controls();self.edited.emit()

    def choose_color(self):
        color=QColorDialog.getColor(QColor(self.color.text()),self,'Color del texto variable')
        if color.isValid():self.color.setText(color.name().upper());self.changed()
