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
    QGraphicsView, QGraphicsItem, QInputDialog,
)

from .window import label, button, vbox, pixmap
from .responsive import AdaptiveDialog
from .resize_item import ResizableRect
from ..status_design import validate_layout, StatusDesignError, MAX_FIELDS


class StatusFieldsCanvas(QGraphicsView):
    """Draw new variable fields directly over the existing label PDF crop."""

    def __init__(self, on_draw):
        super().__init__()
        self.on_draw = on_draw
        self.drawing = False
        self.start = None
        self.guide = None
        self.setScene(QGraphicsScene(self))
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
        self.layout = copy.deepcopy(__import__("json").loads(revision["layout_json"]))
        self.crop = list(self.layout["crop"])
        with fitz.open(self.pdf) as document:
            validated = validate_layout(self.layout, document)
            if validated != self.layout:
                raise ValueError("Diseño de referencia no canónico.")
            page = document[self.layout["page"]]
            clipped = page.get_pixmap(matrix=fitz.Matrix(2, 2),
                                      clip=fitz.Rect(self.crop), alpha=False)
            self.image = Image.frombytes(
                "RGB", (clipped.width, clipped.height), clipped.samples)
        self.image_size = self.image.size
        self.shapes = []
        self.busy = False
        self.setWindowTitle("Editor visual · " + revision["kind"] +
                            " · revisión " + revision["revision"])
        self.resize(1150, 760)
        root = vbox(self, 12, 9)
        root.addWidget(label(
            "Campos variables: dibujar, mover y redimensionar con el ratón",
            "panelTitle"))
        help_text = label(
            "Los elementos fijos del Word/PDF no se modifican. "
            "Seleccione un campo para configurar sus datos; "
            "arrastre sus bordes para cambiar el tamaño. "
            "Solo se guarda el borrador de esta etiqueta.", "subtle")
        help_text.setWordWrap(True)
        root.addWidget(help_text)
        body = QHBoxLayout()
        self.view = StatusFieldsCanvas(self.add_field_from_drag)
        self.view.scene().selectionChanged.connect(self.scene_selected)
        body.addWidget(self.view, 3)
        aside = QWidget()
        panel = vbox(aside, 9, 9)
        panel.addWidget(label("CAMPOS DE ESTA ETIQUETA", "section"))
        self.items = QListWidget()
        self.items.currentRowChanged.connect(self.select_field)
        panel.addWidget(self.items, 2)
        actions = QHBoxLayout()
        self.new_field_button = button("Dibujar campo…", self.new_field)
        actions.addWidget(self.new_field_button)
        actions.addWidget(button("Eliminar", self.remove_field))
        panel.addLayout(actions)
        self.draw_hint = label(
            "Pulse «Dibujar campo» y arrastre un rectángulo directamente sobre la etiqueta.",
            "subtle")
        self.draw_hint.setWordWrap(True)
        panel.addWidget(self.draw_hint)
        properties = QFormLayout()
        self.key = QLineEdit()
        self.name = QLineEdit()
        self.font_size = QDoubleSpinBox()
        self.font_size.setRange(5, 72)
        self.font_size.setDecimals(1)
        self.bold = QCheckBox("Negrita")
        self.required = QCheckBox("Obligatorio")
        properties.addRow("Identificador", self.key)
        properties.addRow("Nombre", self.name)
        properties.addRow("Tamaño original (pt)", self.font_size)
        properties.addRow("Estilo", self.bold)
        properties.addRow("Validación", self.required)
        panel.addLayout(properties)
        panel.addWidget(button("Aplicar propiedades", self.apply_properties))
        self.geometry = label("", "subtle")
        self.geometry.setWordWrap(True)
        panel.addWidget(self.geometry)
        panel.addStretch()
        body.addWidget(aside, 2)
        root.addLayout(body, 1)
        footer = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel)
        footer.button(QDialogButtonBox.StandardButton.Save).setText(
            "Guardar diseño borrador")
        footer.accepted.connect(self.save)
        footer.rejected.connect(self.reject)
        root.addWidget(footer)
        self.draw()
        QTimer.singleShot(0, self.fit)

    def fit(self):
        self.view.fitInView(self.view.sceneRect(),
                           Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "view") and not self.view.sceneRect().isEmpty():
            QTimer.singleShot(0, self.fit)

    def draw(self, selected=None):
        if selected is None:
            selected = self.items.currentRow() if hasattr(self, "items") else -1
        self.busy = True
        scene = self.view.scene()
        scene.clear()
        scene.addPixmap(pixmap(self.image))
        scene.setSceneRect(QRectF(0, 0, *self.image_size))
        self.shapes = []
        self.items.clear()
        for index, field in enumerate(self.layout["fields"]):
            shape = StatusFieldShape(index, field, self.crop,
                                     self.image_size, self.moved)
            scene.addItem(shape)
            self.shapes.append(shape)
            self.items.addItem(field["label"] + "  ·  " + field["key"])
        self.busy = False
        if self.shapes:
            self.items.setCurrentRow(max(0, min(selected, len(self.shapes)-1)))
        else:
            self.select_field(-1)

    def scene_selected(self):
        if self.busy:
            return
        for shape in self.shapes:
            if shape.isSelected() and self.items.currentRow() != shape.index:
                self.items.setCurrentRow(shape.index)
                return

    def select_field(self, index):
        if self.busy:
            return
        self.busy = True
        for shape in self.shapes:
            shape.setSelected(shape.index == index)
        valid = 0 <= index < len(self.layout["fields"])
        for widget in (self.key, self.name, self.font_size,
                       self.bold, self.required):
            widget.setEnabled(valid)
        if valid:
            field = self.layout["fields"][index]
            self.key.setText(field["key"])
            self.name.setText(field["label"])
            self.font_size.setValue(field["font_size"])
            self.bold.setChecked(field["bold"])
            self.required.setChecked(field["required"])
            self.show_geometry(index)
        else:
            self.key.clear()
            self.name.clear()
            self.geometry.setText("Dibuje un campo o seleccione uno existente.")
        self.busy = False

    def show_geometry(self, index):
        r = self.layout["fields"][index]["rect"]
        mm = 25.4 / 72
        self.geometry.setText(
            f"Posición: {r[0]*mm:.2f}, {r[1]*mm:.2f} mm\n"
            f"Medidas: {(r[2]-r[0])*mm:.2f} × {(r[3]-r[1])*mm:.2f} mm\n"
            "Coordenadas respecto a la página fuente.")

    def apply_properties(self):
        index = self.items.currentRow()
        if not 0 <= index < len(self.layout["fields"]):
            return True
        key = self.key.text().strip()
        name = self.name.text().strip()
        if (not re.fullmatch(r"[a-z][a-z0-9_]{0,39}", key)
                or any(i != index and f["key"] == key
                       for i, f in enumerate(self.layout["fields"]))):
            QMessageBox.warning(self, "Identificador incorrecto",
                                "Utilice letras minúsculas, números o _; clave única.")
            return False
        if not name or len(name) > 80:
            QMessageBox.warning(self, "Nombre incorrecto",
                                "Indique un nombre entre 1 y 80 caracteres.")
            return False
        field = self.layout["fields"][index]
        field.update(key=key, label=name,
                     font_size=self.font_size.value(),
                     bold=self.bold.isChecked(),
                     required=self.required.isChecked())
        self.items.item(index).setText(name + "  ·  " + key)
        return True

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
        self.layout["fields"][index]["rect"] = rect
        self.show_geometry(index)

    def new_field(self):
        if self.view.drawing:
            self.view.end_draw()
            self.new_field_button.setText("Dibujar campo…")
            self.draw_hint.setText("Dibujo cancelado. El borrador no ha cambiado.")
            return
        if len(self.layout["fields"]) >= MAX_FIELDS:
            QMessageBox.warning(self, "Número de campos", "Se ha alcanzado el máximo de campos.")
            return
        self.view.begin_draw()
        self.new_field_button.setText("Cancelar dibujo")
        self.draw_hint.setText(
            "Arrastre con el botón izquierdo sobre la etiqueta para crear el campo. "
            "Después puede moverlo o redimensionarlo con sus asas.")

    def add_field_from_drag(self, region):
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
        existing = {field["key"] for field in self.layout["fields"]}
        while f"campo_{n}" in existing:
            n += 1
        self.layout["fields"].append({
            "key": f"campo_{n}", "label": f"Campo {n}",
            "rect": rect, "font_size": 10.0, "bold": False, "required": False,
        })
        self.draw(len(self.layout["fields"])-1)
        self.draw_hint.setText(
            "Campo creado. Edite el nombre y las propiedades, pulse Aplicar propiedades "
            "y finalmente Guardar diseño borrador.")

    def remove_field(self):
        i = self.items.currentRow()
        if not 0 <= i < len(self.layout["fields"]):
            return
        name = self.layout["fields"][i]["label"]
        result = QMessageBox.question(
            self, "Eliminar campo del borrador",
            "¿Eliminar el campo variable «" + name + "»?\n"
            "No se modificará el original Word/PDF.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if result == QMessageBox.StandardButton.Yes:
            self.layout["fields"].pop(i)
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
            self.catalog.save_draft(self.revision["uid"], self.layout)
            self.accept()
        except (ValueError, PermissionError, OSError, RuntimeError) as error:
            QMessageBox.warning(self, "Diseño no guardado", str(error))
