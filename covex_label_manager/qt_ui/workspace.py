"""Presentation of the retained Editor, with all existing controller objects."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QTabWidget, QBoxLayout, QPushButton, QScrollArea,
    QComboBox, QVBoxLayout, QLabel, QFormLayout, QHBoxLayout, QFrame, QSizePolicy)


def arrange_editor(window):
    w = window
    outer = w.editor.layout()
    toolbar = outer.itemAt(1).widget().layout()
    # Keep one action strip; field creation belongs beside the element list.
    outer.removeWidget(w.field_action_bar)
    w.field_action_bar.layout().setDirection(QBoxLayout.Direction.TopToBottom)
    w.editor_tools.layout().insertWidget(1, w.field_action_bar)
    w.variant_edit_button.setText('Crear variante editable…')
    variant_row = outer.itemAt(2).layout()
    outer.removeItem(variant_row)
    variant_row.setParent(None)
    variant_row.setDirection(QBoxLayout.Direction.LeftToRight)
    variant_row.itemAt(0).widget().hide()
    variant_menu=variant_row.itemAt(variant_row.count()-1).widget()
    variant_menu.setText('Gestionar variantes');variant_menu.setToolTip('Gestionar variantes de diseño')
    w.editor_variant_menu_button = variant_menu
    variant_menu.setAccessibleName('Gestionar variantes de diseño')
    # A named command gets its own row; never squeeze the selector beside an ellipsis.
    variant_row.removeWidget(variant_menu)
    w.editor_variant_selector.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    w.editor_variant_selector.setMinimumContentsLength(6)
    w.editor_variant_selector.setAccessibleName('Variante de diseño del Editor')
    w.editor_variant_selector.currentTextChanged.connect(w.editor_variant_selector.setToolTip)
    w.editor_variant_selector.setMinimumWidth(0)
    toolbar.removeWidget(w.editor_reset_button)
    w.editor_advanced.layout().addWidget(w.editor_reset_button)
    outer.removeWidget(w.save_button)
    w.undo_button.setText('Deshacer');w.redo_button.setText('Rehacer')
    w.undo_button.setAccessibleName('Deshacer cambio de diseño')
    w.redo_button.setAccessibleName('Rehacer cambio de diseño')
    w.undo_button.setToolTip('Deshacer (Ctrl+Z)')
    w.redo_button.setToolTip('Rehacer (Ctrl+Shift+Z)')
    w.canvas_focus = QPushButton('Ampliar lienzo')
    w.canvas_focus.setCheckable(True)
    w.canvas_focus.setAccessibleName('Ampliar lienzo y recuperar paneles del Editor')
    def focus(checked):
        w.tools_scroll.setVisible(not checked)
        w.editor_context.setVisible(not checked)
        w.canvas_focus.setText('Mostrar paneles' if checked else 'Ampliar lienzo')
        w.canvas.fit()
    w.canvas_focus.toggled.connect(focus)
    toolbar.insertWidget(0, w.canvas_focus)
    # Remove the decorative LIENZO label, not a command.
    for i in reversed(range(toolbar.count())):
        item = toolbar.itemAt(i)
        if item.widget() and hasattr(item.widget(), 'text') and item.widget().text() == 'LIENZO':
            item.widget().hide();toolbar.removeWidget(item.widget())
    w.field_snap.setText('Ajustar a 1 mm')
    w.field_grid.setText('Cuadrícula 10 mm')
    for note in w.editor_tools.findChildren(QLabel):
        if note.text().startswith('Solo se editan campos variables'):
            note.setToolTip(note.text());note.setText('Maestro fijo protegido.')
        elif note.text()=='Campos variables':note.setText('Campos')
    w.editor_tip.setText('El PDF fijo está protegido. Seleccione un campo para editar sus propiedades.')
    w.editor_title.setStyleSheet('font-size:20px;')
    w.editor_note.hide()
    w.new_field_button.setText('Añadir campo')
    w.delete_field_button = next(b for b in w.design_buttons if b.text() == 'Quitar campo')
    w.delete_field_button.setText('Eliminar campo')
    w.field_action_bar.layout().insertWidget(2, w.delete_field_button)
    # Essential properties leave the collapsed technical sections. Keep all
    # original widgets, signals, controllers and documentary checks.
    previous_properties = w.properties_scroll.takeWidget()
    properties = QFrame();properties.setObjectName('editorProperties')
    pl = QVBoxLayout(properties);pl.setContentsMargins(10, 8, 10, 8);pl.setSpacing(7)
    pl.addWidget(QLabel('PROPIEDADES'))
    w.field_title.setStyleSheet('font-size:15px;font-weight:700;')
    pl.addWidget(w.field_title)
    form = QFormLayout();form.setSpacing(5)
    form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    form.addRow('Nombre visible', w.name_input)
    w.key_label = QLabel('Identificador');form.addRow(w.key_label, w.key_input)
    for key, text in [('x','Posición X'),('y','Posición Y'),('w','Anchura'),('h','Altura')]:
        w.spins[key].setKeyboardTracking(False)
        form.addRow(text, w.spins[key])
    w.font_size.setKeyboardTracking(False)
    form.addRow('Tamaño de texto', w.font_size)
    form.addRow(w.bold);form.addRow(w.required);form.addRow(w.locked)
    form.addRow('Modo de texto', w.draw_mode);pl.addLayout(form)
    pl.addWidget(QLabel('VARIANTE DE DISEÑO'))
    pl.addLayout(variant_row);pl.addWidget(variant_menu)
    pl.addStretch()
    w.properties_scroll.setWidget(properties)
    previous_properties.deleteLater()
    # Plain technical headings stay discoverable; only the specialized bodies
    # fold. Essential field properties do not depend on this switch.
    w.editor_advanced_button.setChecked(True);w.editor_advanced.show()
    w.editor_advanced_button.setToolTip('Mostrar u ocultar las herramientas técnicas de documento y composición. Las propiedades del campo permanecen accesibles.')
    w.field_list.setMinimumHeight(100)
    w.field_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    w.field_list.setTextElideMode(Qt.TextElideMode.ElideRight)
    w.field_list.setStyleSheet('QListWidget::item { padding:7px 5px; }')
    w.editor_tools.layout().removeWidget(w.field_list)
    w.editor_tools.layout().insertWidget(2,w.field_list,1)
    for note in w.editor_tools.findChildren(QLabel):
        if note.text()=='Campos':note.hide()
    w.editor_tip.setToolTip(w.editor_tip.text());w.editor_tip.hide()
    w.editor_tools.setMinimumWidth(165);w.editor_tools.setMaximumWidth(210)
    w.editor_tools.layout().setContentsMargins(8,8,8,8);w.editor_tools.layout().setSpacing(6)
    w.tools_scroll.setMinimumWidth(175);w.tools_scroll.setMaximumWidth(220)
    w.properties_scroll.setMinimumWidth(260);w.properties_scroll.setMaximumWidth(320)
    for control in properties.findChildren(QWidget):
        if isinstance(control,(QComboBox,)):
            control.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
    # Durable save/status footer is outside BOTH scroll areas and work tabs.
    footer = QWidget();footer.setObjectName('editorFooter')
    fl = QHBoxLayout(footer);fl.setContentsMargins(2,2,2,2);fl.setSpacing(8)
    w.editor_document_note = QLabel();w.editor_document_note.setWordWrap(True)
    fl.addWidget(w.editor_document_note, 2);fl.addWidget(w.edit_status, 1);fl.addWidget(w.save_button)
    last = outer.takeAt(outer.count()-1)
    if last.widget():last.widget().deleteLater()
    outer.addWidget(footer)
    split = w.canvas.parentWidget()
    w.editor_context = QTabWidget()
    w.editor_context.setMinimumWidth(270)
    w.editor_context.addTab(w.properties_scroll, 'Propiedades')
    # Retain the dock's enable/disable contract, but contain it inside Editor.
    w.removeDockWidget(w.work_dock)
    w.work_dock.setParent(w.editor_context)
    w.work_dock.setMinimumWidth(0)
    w.work_dock.setTitleBarWidget(QWidget())
    w.work_dock.setFeatures(w.work_dock.DockWidgetFeature.NoDockWidgetFeatures)
    work_scroll = QScrollArea()
    work_scroll.setWidgetResizable(True);work_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    work_scroll.setWidget(w.work_dock)
    w.editor_context.addTab(work_scroll, 'Trabajo de lote')
    w.editor_context.currentChanged.connect(lambda index: w.work_dock.setVisible(index == 1))
    split.addWidget(w.editor_context)
    split.setChildrenCollapsible(False)
    split.setSizes([185, 900, 285])
    w.editor_split = split
    w.work_dock.hide()
    for layout in (outer, toolbar):
        layout.setSpacing(6)
        layout.setContentsMargins(8, 6, 8, 6)


def arrange_inspector(w):
    """Keep the existing primary commands below, rather than inside, the scroll."""
    body=w.inspector.layout()
    actions=[body.takeAt(body.count()-1) for _ in range(3)]
    footer=QWidget();footer.setObjectName('inspectorActions')
    footer_layout=QVBoxLayout(footer);footer_layout.setContentsMargins(8,6,8,6);footer_layout.setSpacing(4)
    for item in reversed(actions):
        if item.widget():footer_layout.addWidget(item.widget())
        else:
            item.layout().setParent(None);footer_layout.addLayout(item.layout())
    w.inspector.setMinimumHeight(0)
    old_scroll=w.inspector_panel
    container=QWidget();container.setMinimumWidth(340);container.setMaximumWidth(380)
    layout=QVBoxLayout(container);layout.setContentsMargins(0,0,0,0);layout.setSpacing(0)
    index=w.library_split.indexOf(old_scroll)
    w.library_split.replaceWidget(index,container)
    layout.addWidget(old_scroll,1);layout.addWidget(footer)
    w.inspector_scroll=old_scroll;w.inspector_panel=container
    w.table.itemSelectionChanged.connect(lambda:footer.setEnabled(w.row is not None))
