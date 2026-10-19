"""Native visual variable-field editor for independent R7A status labels.

Only DRAFT layouts can be saved; source Word/PDF, fixed text, and approval
evidence are never modified. Field boxes use absolute source PDF points.
"""
from __future__ import annotations

import copy
import re
from pathlib import Path

import fitz
from PIL import Image
from PySide6.QtCore import Qt, QRectF, QTimer, QPointF
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtWidgets import (
    QDialogButtonBox, QWidget, QHBoxLayout, QFormLayout, QLineEdit,
    QListWidget, QMessageBox, QCheckBox, QDoubleSpinBox, QGraphicsScene,
    QGraphicsView, QGraphicsItem, QInputDialog, QScrollArea, QSplitter,
)

from .window import label, button, vbox, pixmap, Preview
from .responsive import AdaptiveDialog, accessible_form
from .resize_item import ResizableRect
from ..status_design import validate_layout, StatusDesignError, MAX_FIELDS


class StatusFieldsCanvas(Preview):
    """Draw new variable fields directly over the existing label PDF crop."""

    def __init__(self, on_draw):
        super().__init__()
        self.on_draw = on_draw
        self.drawing = False
        self.start = None
        self.guide = None
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setMinimumSize(470, 350)

    def begin_draw(self):
        self.drawing = True
        self.start = None
        self.viewport().setCursor(Qt.CursorShape.CrossCursor)

    def end_draw(self):
        self.drawing = False
        self.start = None
        self.viewport().unsetCursor()
        if self.guide is not None:
            self.scene().removeItem(self.guide)
            self.guide = None

    def _point(self, event):
        p = self.mapToScene(event.position().toPoint())
        rect = self.scene().sceneRect()
        return QPointF(max(rect.left(), min(rect.right(), p.x())),
                       max(rect.top(), min(rect.bottom(), p.y())))

    def mousePressEvent(self, event):
        if self.drawing and event.button() == Qt.MouseButton.LeftButton:
            self.start = self._point(event)
            self.guide = self.scene().addRect(
                QRectF(self.start, self.start), QPen(QColor("#147D71"), 2),
                QBrush(QColor(20, 125, 113, 40)))
            self.guide.setZValue(200)
            self.guide.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drawing and self.start is not None:
            self.guide.setRect(QRectF(self.start, self._point(event)).normalized())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drawing and self.start is not None and event.button() == Qt.MouseButton.LeftButton:
            rect = QRectF(self.start, self._point(event)).normalized()
            self.end_draw()
            self.on_draw(rect)
            event.accept()
            return
        super().mouseReleaseEvent(event)


class StatusFieldShape(ResizableRect):
    """Draggable, eight-handle editable overlay; no PDF modification."""

    def __init__(self, index, field, crop, image_size, released):
        super().__init__(0, 0, 1, 1)
        self.index = index
        self._on_released = released
        self.setPen(QPen(QColor("#137C70"), 2, Qt.PenStyle.DashLine))
        self.setBrush(QBrush(QColor(20, 125, 113, 45)))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        sx = image_size[0] / (crop[2] - crop[0])
        sy = image_size[1] / (crop[3] - crop[1])
        rect = field["rect"]
        self.setRect(0, 0, (rect[2] - rect[0]) * sx, (rect[3] - rect[1]) * sy)
        self.setPos((rect[0] - crop[0]) * sx, (rect[1] - crop[1]) * sy)
        self.enable_handles(True)
        self.setZValue(10 + index)

    def released(self):
        # Used by both the parent rect drag and the eight ResizeHandle items.
        self._on_released(self.index)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.released()


class StatusFieldsDialog(AdaptiveDialog):
    """User edits fields visually and explicitly saves a normalized draft."""

    def __init__(self, api, revision, parent=None):
        super().__init__(parent)
        if revision["state"] != "DRAFT":
            raise PermissionError("Una revisión aprobada o pendiente no se edita.")
        self.api = api
        self.catalog = api.status_catalog
        self.revision = revision
        self.pdf = self.catalog.root / revision["pdf_path"]
        self.design = copy.deepcopy(__import__("json").loads(revision["layout_json"]))
        self.crop = list(self.design["crop"])
        with fitz.open(self.pdf) as document:
            validated = validate_layout(self.design, document)
            if validated != self.design:
                raise ValueError("Diseño de referencia no canónico.")
            page = document[self.design["page"]]
            clipped = page.get_pixmap(matrix=fitz.Matrix(2, 2),
                                      clip=fitz.Rect(self.crop), alpha=False)
            self.image = Image.frombytes(
                "RGB", (clipped.width, clipped.height), clipped.samples)
        self.image_size = self.image.size
        self.shapes = []
        self.busy = False
        self.property_index = -1
        self.undo_states = [];self.redo_states = []
        self.setWindowTitle("Editor visual · " + revision["kind"] +
                            " · revisión " + revision["revision"])
        self.resize(1150, 760)
        root = vbox(self, 12, 9)
        root.addWidget(label(
            "Editor de campos variables · etiqueta de estado",
            "panelTitle"))
        help_text = label(
            "Los elementos fijos del Word/PDF no se modifican. "
            "Seleccione un campo para configurar sus datos; "
            "arrastre sus bordes para cambiar el tamaño. "
            "Solo se guarda el borrador de esta etiqueta.", "subtle")
        help_text.setWordWrap(True)
        root.addWidget(help_text)
        body = QSplitter()
        body.setChildrenCollapsible(False)
        elements = QWidget();left = vbox(elements,8,6)
        left.addWidget(label('ELEMENTOS','section'))
        self.items = QListWidget()
        self.items.currentRowChanged.connect(self.select_field)
        self.items.setMinimumSize(130,80)
        self.items.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.items.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.items.setStyleSheet('QListWidget::item { padding:7px 5px; }')
        left.addWidget(button('Añadir campo',self.quick_add_field))
        self.new_field_button = button('Dibujar campo',self.new_field)
        left.addWidget(self.new_field_button)
        self.delete_field_button = button('Eliminar campo',self.remove_field)
        left.addWidget(self.delete_field_button)
        left.addWidget(self.items,1)
        elements.setMaximumWidth(205);body.addWidget(elements)
        self.view = StatusFieldsCanvas(self.add_field_from_drag)
        self.view.setMinimumSize(160,140)
        self.view.scene().selectionChanged.connect(self.scene_selected)
        body.addWidget(self.view)
        from .workspace import EditorProperties
        self.properties_scroll=QScrollArea();self.properties_scroll.setWidgetResizable(True)
        aside = EditorProperties(self.properties_scroll,minimum=245,maximum=310)
        panel = vbox(aside, 8, 6)
        panel.addWidget(label('PROPIEDADES','section'))
        self.draw_hint = label(
            "Pulse «Dibujar campo» y arrastre un rectángulo directamente sobre la etiqueta.",
            "subtle")
        self.draw_hint.setWordWrap(True)
        panel.addWidget(self.draw_hint)
        properties = QFormLayout()
        properties.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        properties.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.key = QLineEdit()
        self.name = QLineEdit()
        self.font_size = QDoubleSpinBox()
        self.font_size.setRange(5, 72)
        self.font_size.setDecimals(1)
        self.bold = QCheckBox("Negrita")
        self.required = QCheckBox("Obligatorio")
        properties.addRow("Identificador", self.key)
        properties.addRow("Nombre", self.name)
        self.spins = {}
        for key, caption in [('x','Posición X'),('y','Posición Y'),('w','Anchura'),('h','Altura')]:
            entry=QDoubleSpinBox();entry.setRange(0,10000);entry.setDecimals(3)
            entry.setSuffix(' mm');entry.setKeyboardTracking(False)
            self.spins[key]=entry;properties.addRow(caption,entry)
        properties.addRow("Tamaño original (pt)", self.font_size)
        properties.addRow("Estilo", self.bold)
        from .text_appearance import TextAppearance
        self.text_appearance=TextAppearance();properties.addRow(self.text_appearance)
        self.example=QLineEdit();self.example.setPlaceholderText('Ejemplo para PDF real')
        properties.addRow('Texto de ejemplo',self.example)
        properties.addRow("Validación", self.required)
        accessible_form(properties)
        panel.addLayout(properties)
        panel.addWidget(button("Aplicar propiedades", self.apply_properties))
        self.geometry_note = label("", "subtle")
        self.geometry_note.setWordWrap(True)
        panel.addWidget(self.geometry_note)
        panel.addWidget(self.draw_hint)
        panel.addStretch()
        self.properties_scroll.setWidget(aside);body.addWidget(self.properties_scroll)
        aside.ensurePolished();aside.fit_width()
        body.setSizes([170,600,270]);body.setStretchFactor(1,1)
        from .pdf_view import EditorPdfPane,canvas_pdf_stack
        index=body.indexOf(self.view);placeholder=QWidget();body.replaceWidget(index,placeholder)
        self.pdf_preview=EditorPdfPane(api);self.preview_stack=canvas_pdf_stack(self.view,self.pdf_preview)
        body.replaceWidget(index,self.preview_stack);placeholder.hide();placeholder.deleteLater()
        self.pdf_timer=QTimer(self);self.pdf_timer.setSingleShot(True);self.pdf_timer.timeout.connect(self.refresh_pdf)
        tools=QHBoxLayout()
        self.undo_button=button('Deshacer',self.undo_edit);self.redo_button=button('Rehacer',self.redo_edit)
        tools.addWidget(self.undo_button);tools.addWidget(self.redo_button)
        tools.addWidget(button('Ajustar a pantalla',self.fit))
        self.pdf_toggle=button('PDF real',lambda:None);self.pdf_toggle.setCheckable(True)
        def pdf_mode(checked):
            self.preview_stack.setCurrentIndex(int(checked))
            if checked:self.refresh_pdf()
        self.pdf_toggle.toggled.connect(pdf_mode);tools.addWidget(self.pdf_toggle)
        tools.addWidget(button('−',lambda:self.view.zoom(1/1.2)))
        tools.addWidget(button('+',lambda:self.view.zoom(1.2)))
        root.addLayout(tools)
        root.addWidget(label('Tipo de etiqueta: '+{'aprobado':'Aprobado','rechazado':'Rechazado','sin_analizar':'Sin analizar'}[revision['kind']]+' · Revisión '+revision['revision']+' · Borrador editable. El tipo no indica aprobación documental.','subtle'))
        root.addWidget(body, 1)
        footer = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel)
        footer.button(QDialogButtonBox.StandardButton.Save).setText(
            "Guardar diseño borrador")
        footer.accepted.connect(self.save)
        footer.rejected.connect(self.reject)
        root.addWidget(footer)
        # This editor already has a dedicated property scroll and a flexible
        # three-zone splitter. Do not wrap the whole canvas in another scroll:
        # that would size it to an off-screen body instead of the viewport.
        self._adaptive_ready = True
        self.footer_widgets = [footer]
        for entry in (self.key,self.name,self.font_size,*self.spins.values()):
            entry.editingFinished.connect(self.commit_properties)
        for check in (self.bold,self.required):
            check.toggled.connect(self.commit_properties)
        self.example.editingFinished.connect(self.commit_properties)
        self.text_appearance.edited.connect(self.commit_properties)
        self.draw()
        QTimer.singleShot(0, self, self.fit)

    def fit(self):
        self.view.fit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "view") and not self.view.sceneRect().isEmpty():
            QTimer.singleShot(0, self, self.fit)

    def draw(self, selected=None):
        if selected is None:
            selected = self.items.currentRow() if hasattr(self, "items") else -1
        self.busy = True
        self.property_index = -1
        self.view.end_draw()
        scene = self.view.scene()
        scene.clear()
        scene.addPixmap(pixmap(self.image))
        scene.setSceneRect(QRectF(0, 0, *self.image_size))
        self.shapes = []
        self.items.clear()
        for index, field in enumerate(self.design["fields"]):
            shape = StatusFieldShape(index, field, self.crop,
                                     self.image_size, self.moved)
            scene.addItem(shape)
            self.shapes.append(shape)
            self.items.addItem(field["label"] + "  ·  " + field["key"]+(' · obligatorio' if field['required'] else ''))
            self.items.item(index).setToolTip(self.items.item(index).text())
        self.busy = False
        if self.shapes:
            self.items.setCurrentRow(max(0, min(selected, len(self.shapes)-1)))
        else:
            self.select_field(-1)
        self.undo_button.setEnabled(bool(self.undo_states));self.redo_button.setEnabled(bool(self.redo_states))

    def scene_selected(self):
        from shiboken6 import isValid
        if not isValid(self.view) or not isValid(self.items):return
        if self.busy:
            return
        for shape in self.shapes:
            if not isValid(shape):continue  # native scene teardown, not a gesture
            if shape.isSelected() and self.items.currentRow() != shape.index:
                self.items.setCurrentRow(shape.index)
                return

    def select_field(self, index):
        if self.busy:
            return
        if self.property_index != index and not self.apply_properties():
            self.busy=True;self.items.setCurrentRow(self.property_index)
            for shape in self.shapes:shape.setSelected(shape.index==self.property_index)
            self.busy=False
            return
        self.busy = True
        self.property_index = index
        for shape in self.shapes:
            shape.setSelected(shape.index == index)
        valid = 0 <= index < len(self.design["fields"])
        for widget in (self.key, self.name, self.font_size,
                       self.bold, self.required,self.text_appearance,self.example, *self.spins.values()):
            widget.setEnabled(valid)
        if valid:
            field = self.design["fields"][index]
            self.key.setText(field["key"])
            self.name.setText(field["label"])
            self.font_size.setValue(field["font_size"])
            self.bold.setChecked(field["bold"])
            self.text_appearance.load(field);self.example.setText(field.get('example',''))
            self.required.setChecked(field["required"])
            self.load_geometry(index)
            self.show_geometry(index)
        else:
            self.key.clear()
            self.name.clear()
            self.geometry_note.setText("Dibuje un campo o seleccione uno existente.")
        self.busy = False
        self.delete_field_button.setEnabled(valid)

    def load_geometry(self,index):
        r=self.design['fields'][index]['rect'];mm=25.4/72
        for key,value in zip(('x','y','w','h'),(r[0]-self.crop[0],r[1]-self.crop[1],r[2]-r[0],r[3]-r[1])):
            self.spins[key].setValue(value*mm)
        self.geometry_reference={k:e.value() for k,e in self.spins.items()}

    def remember(self,before):
        if before==self.design:return
        self.undo_states.append(before);self.undo_states=self.undo_states[-100:];self.redo_states.clear()
        self.undo_button.setEnabled(True);self.redo_button.setEnabled(False)

    def undo_edit(self):
        if not self.apply_properties() or not self.undo_states:return
        self.redo_states.append(copy.deepcopy(self.design));self.design=self.undo_states.pop();self.draw()

    def redo_edit(self):
        if not self.apply_properties() or not self.redo_states:return
        self.undo_states.append(copy.deepcopy(self.design));self.design=self.redo_states.pop();self.draw()

    def show_geometry(self, index):
        r = self.design["fields"][index]["rect"]
        mm = 25.4 / 72
        self.geometry_note.setText(
            f"Posición: {r[0]*mm:.2f}, {r[1]*mm:.2f} mm\n"
            f"Medidas: {(r[2]-r[0])*mm:.2f} × {(r[3]-r[1])*mm:.2f} mm\n"
            "Coordenadas respecto a la página fuente.")

    def apply_properties(self):
        index = self.property_index
        if not 0 <= index < len(self.design["fields"]):
            return True
        for entry in (*self.spins.values(),self.font_size):entry.interpretText()
        key = self.key.text().strip()
        name = self.name.text().strip()
        if (not re.fullmatch(r"[a-z][a-z0-9_]{0,39}", key)
                or any(i != index and f["key"] == key
                       for i, f in enumerate(self.design["fields"]))):
            QMessageBox.warning(self, "Identificador incorrecto",
                                "Utilice letras minúsculas, números o _; clave única.")
            return False
        if not name or len(name) > 80:
            QMessageBox.warning(self, "Nombre incorrecto",
                                "Indique un nombre entre 1 y 80 caracteres.")
            return False
        before=copy.deepcopy(self.design);candidate=copy.deepcopy(self.design)
        field = candidate["fields"][index]
        field.update(key=key, label=name,
                     font_size=self.font_size.value(),
                     bold=self.bold.isChecked(),
                     required=self.required.isChecked())
        try:style=self.text_appearance.configuration()
        except ValueError as ex:
            QMessageBox.warning(self,'Tipografía no válida',str(ex));return False
        if style is None:field.pop('typography',None)
        else:field['typography']=style
        if self.example.text() or 'example' in field:field['example']=self.example.text()
        if any('typography' in f or 'example' in f for f in candidate['fields']):candidate['contract']=2
        if any(entry.value()!=self.geometry_reference[k] for k,entry in self.spins.items()):
            x,y,w,h=(self.spins[k].value()*72/25.4 for k in ('x','y','w','h'))
            field['rect']=[self.crop[0]+x,self.crop[1]+y,self.crop[0]+x+w,self.crop[1]+y+h]
        try:
            with fitz.open(self.pdf) as document:validate_layout(candidate,document)
        except (ValueError,OSError,RuntimeError) as ex:
            QMessageBox.warning(self,'Cambio no realizado',str(ex));return False
        self.design=candidate;self.remember(before)
        self.items.item(index).setText(name + "  ·  " + key)
        shape=self.shapes[index];sx=self.image_size[0]/(self.crop[2]-self.crop[0]);sy=self.image_size[1]/(self.crop[3]-self.crop[1])
        r=field['rect'];shape.setPos((r[0]-self.crop[0])*sx,(r[1]-self.crop[1])*sy)
        shape.setRect(0,0,(r[2]-r[0])*sx,(r[3]-r[1])*sy);shape.position_handles()
        self.load_geometry(index);self.show_geometry(index)
        if self.pdf_toggle.isChecked():self.pdf_timer.start(350)
        return True

    def refresh_pdf(self):
        from ..status_design import render_proof
        import uuid
        try:
            path=self.api.output_path('cache','r8c-status-'+uuid.uuid4().hex+'.pdf')
            values={f['key']:f.get('example','') for f in self.design['fields']}
            render_proof(self.pdf,self.design,values,path)
            with fitz.open(path) as pdf:details=pdf.metadata.get('subject','')
            self.pdf_preview.load(path,'PDF real · ejemplos de estado',details or 'PRUEBA / NO GMP · No modifica los textos fijos ni registra una emisión.')
        except (ValueError,OSError,RuntimeError) as ex:self.pdf_preview.clear('Prueba bloqueada: '+str(ex))

    def commit_properties(self,*_):
        if not self.busy:return self.apply_properties()

    def moved(self, index):
        if not 0 <= index < len(self.shapes):
            return
        shape = self.shapes[index]
        bounding = shape.mapRectToScene(shape.rect())
        sx = (self.crop[2]-self.crop[0]) / self.image_size[0]
        sy = (self.crop[3]-self.crop[1]) / self.image_size[1]
        rect = [self.crop[0]+bounding.left()*sx,
                self.crop[1]+bounding.top()*sy,
                self.crop[0]+bounding.right()*sx,
                self.crop[1]+bounding.bottom()*sy]
        before=copy.deepcopy(self.design)
        candidate=copy.deepcopy(self.design)
        candidate['fields'][index]['rect']=rect
        try:
            with fitz.open(self.pdf) as document:validate_layout(candidate,document)
        except (ValueError,OSError,RuntimeError) as ex:
            # A native item/handle release is still on the C++ stack. Restore
            # this item in place; never redraw/delete it inside that callback.
            r=before['fields'][index]['rect']
            shape.setPos((r[0]-self.crop[0])/sx,(r[1]-self.crop[1])/sy)
            shape.setRect(0,0,(r[2]-r[0])/sx,(r[3]-r[1])/sy)
            shape.position_handles()
            self.draw_hint.setText('Cambio no realizado: '+str(ex))
            return
        self.design=candidate
        self.remember(before)
        self.load_geometry(index)
        self.show_geometry(index)

    def new_field(self):
        if not self.apply_properties():return
        if self.view.drawing:
            self.view.end_draw()
            self.new_field_button.setText("Dibujar campo…")
            self.draw_hint.setText("Dibujo cancelado. El borrador no ha cambiado.")
            return
        if len(self.design["fields"]) >= MAX_FIELDS:
            QMessageBox.warning(self, "Número de campos", "Se ha alcanzado el máximo de campos.")
            return
        self.view.begin_draw()
        self.new_field_button.setText("Cancelar dibujo")
        self.draw_hint.setText(
            "Arrastre con el botón izquierdo sobre la etiqueta para crear el campo. "
            "Después puede moverlo o redimensionarlo con sus asas.")

    def quick_add_field(self):
        if not self.apply_properties():return
        # Find a free default box; never create overlapping fields silently.
        width=self.image_size[0]*.35;height=self.image_size[1]*.12
        for y in range(0,9):
            for x in range(0,6):
                region=QRectF(x*self.image_size[0]*.1,y*self.image_size[1]*.1,width,height)
                if not self.view.sceneRect().contains(region):continue
                if any(shape.mapRectToScene(shape.rect()).intersects(region) for shape in self.shapes):continue
                self.add_field_from_drag(region);return
        self.draw_hint.setText('No queda espacio para un campo propuesto. Utilice «Dibujar campo» en una zona libre.')

    def add_field_from_drag(self, region):
        if not self.apply_properties():return
        if len(self.design['fields'])>=MAX_FIELDS:
            QMessageBox.warning(self,'Número de campos','Se ha alcanzado el máximo de campos.');return
        sx = (self.crop[2] - self.crop[0]) / self.image_size[0]
        sy = (self.crop[3] - self.crop[1]) / self.image_size[1]
        rect = [self.crop[0] + region.left() * sx,
                self.crop[1] + region.top() * sy,
                self.crop[0] + region.right() * sx,
                self.crop[1] + region.bottom() * sy]
        self.new_field_button.setText("Dibujar campo…")
        if min(rect[2] - rect[0], rect[3] - rect[1]) < 5:
            self.draw_hint.setText(
                "Área demasiado pequeña. Vuelva a pulsar Dibujar campo y arrastre más.")
            return
        n = 1
        existing = {field["key"] for field in self.design["fields"]}
        while f"campo_{n}" in existing:
            n += 1
        before=copy.deepcopy(self.design)
        self.design["fields"].append({
            "key": f"campo_{n}", "label": f"Campo {n}",
            "rect": rect, "font_size": 10.0, "bold": False, "required": False,
        })
        try:
            with fitz.open(self.pdf) as document:validate_layout(self.design,document)
        except (ValueError,OSError,RuntimeError) as ex:
            self.design=before;self.draw_hint.setText(str(ex));return
        self.remember(before)
        self.draw(len(self.design["fields"])-1)
        self.draw_hint.setText(
            "Campo creado. Edite el nombre y las propiedades, pulse Aplicar propiedades "
            "y finalmente Guardar diseño borrador.")

    def remove_field(self):
        if not self.apply_properties():return
        i = self.items.currentRow()
        if not 0 <= i < len(self.design["fields"]):
            return
        name = self.design["fields"][i]["label"]
        result = QMessageBox.question(
            self, "Eliminar campo del borrador",
            "¿Eliminar el campo variable «" + name + "»?\n"
            "No se modificará el original Word/PDF.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if result == QMessageBox.StandardButton.Yes:
            before=copy.deepcopy(self.design)
            self.design["fields"].pop(i)
            self.remember(before)
            self.draw(i-1)

    def save(self):
        if self.view.drawing:
            QMessageBox.warning(
                self, "Campo sin terminar",
                "Termine de dibujar el campo o cancele el dibujo antes de guardar.")
            return
        if not self.apply_properties():
            return
        try:
            self.catalog.save_draft(self.revision["uid"], self.design,
                                    expected_layout_sha=self.revision["layout_sha"])
            self.revision = self.catalog.get(self.revision["uid"])
            self.accept()
        except (ValueError, PermissionError, OSError, RuntimeError) as error:
            QMessageBox.warning(self, "Diseño no guardado", str(error))

    def reject(self):
        import json
        for entry in (*self.spins.values(),self.font_size):entry.interpretText()
        original = json.loads(self.revision["layout_json"])
        index = self.items.currentRow()
        properties_changed = False
        if 0 <= index < len(self.design["fields"]):
            field = self.design["fields"][index]
            properties_changed = any((
                self.key.text() != field["key"], self.name.text() != field["label"],
                self.font_size.value() != field["font_size"],
                self.bold.isChecked() != field["bold"],
                self.required.isChecked() != field["required"]))
            properties_changed=properties_changed or any(e.value()!=self.geometry_reference[k] for k,e in self.spins.items())
        if self.design != original or properties_changed:
            choice = QMessageBox.question(self, "Diseño sin guardar",
                "Hay cambios sin guardar. ¿Desea guardar el borrador antes de cerrar?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
            if choice == QMessageBox.StandardButton.Cancel:
                return
            if choice == QMessageBox.StandardButton.Save:
                self.save()
                return
        self.view.end_draw()
        super().reject()
