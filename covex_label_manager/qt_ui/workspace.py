"""Presentation of the retained Editor, with all existing controller objects."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QTabWidget, QBoxLayout, QPushButton, QScrollArea,
    QComboBox, QVBoxLayout, QLabel)


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
    variant_menu.setText('⋯');variant_menu.setToolTip('Gestionar variantes de diseño')
    variant_menu.setAccessibleName('Gestionar variantes de diseño')
    w.properties_scroll.widget().layout().insertLayout(1, variant_row)
    w.editor_variant_selector.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    w.editor_variant_selector.setMinimumContentsLength(6)
    w.editor_variant_selector.setAccessibleName('Variante de diseño del Editor')
    w.editor_variant_selector.currentTextChanged.connect(w.editor_variant_selector.setToolTip)
    w.editor_variant_selector.setMinimumWidth(0)
    toolbar.removeWidget(w.editor_reset_button)
    w.editor_advanced.layout().addWidget(w.editor_reset_button)
    outer.removeWidget(w.save_button)
    toolbar.addWidget(w.save_button)
    w.undo_button.setText('↶');w.redo_button.setText('↷')
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
    w.editor_tools.setMinimumWidth(175);w.editor_tools.setMaximumWidth(245)
    w.tools_scroll.setMinimumWidth(185);w.tools_scroll.setMaximumWidth(255)
    w.properties_scroll.setMinimumWidth(245);w.properties_scroll.setMaximumWidth(340)
    split = w.canvas.parentWidget()
    w.editor_context = QTabWidget()
    w.editor_context.setMinimumWidth(255)
    w.editor_context.addTab(w.properties_scroll, 'Campo y variante')
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
    split.setSizes([190, 900, 285])
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
