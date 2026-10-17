"""Visual per-label crop selection on a shared DOCX/PDF source.

All values are PDF page-space points, not pixels. This dialog never imports,
edits a corporate source, approves a revision or issues a production PDF.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QWidget, QVBoxLayout, QHBoxLayout,
    QDialogButtonBox, QComboBox, QLabel, QMessageBox,
)
from .responsive import AdaptiveDialog
from .window import label, button, vbox, pixmap
from ..status_design import StatusDesignError


class CropCanvas(QGraphicsView):
    """Drag a rectangle over the rasterized full PDF page."""

    def __init__(self, callback):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setRenderHints(self.renderHints())
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setMinimumSize(500, 320)
        self._active = False
        self._point = None
        self._crop_item = None
        self._callback = callback
        self._scale_x = 1.0
        self._scale_y = 1.0

    def display_page(self, pil_image, pdf_rect):
        self.scene().clear()
        item = self.scene().addPixmap(pixmap(pil_image))
        self.scene().setSceneRect(item.boundingRect())
        self._active = False
        self._point = None
        self._crop_item = self.scene().addRect(
            QRectF(), QPen(QColor("#D35400"), 2), QBrush(QColor(255, 205, 120, 65)))
        self._crop_item.setZValue(5)
        self._scale_x = pdf_rect.width / pil_image.width
        self._scale_y = pdf_rect.height / pil_image.height
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._callback(None)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.sceneRect().isEmpty():
            self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def _local(self, event):
        point = self.mapToScene(event.position().toPoint())
        box = self.sceneRect()
        return QPointF(max(box.left(), min(point.x(), box.right())),
                       max(box.top(), min(point.y(), box.bottom())))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._active = True
            self._point = self._local(event)
            self._crop_item.setRect(QRectF(self._point, self._point))
            self._callback(None)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._active:
            point = self._local(event)
            self._crop_item.setRect(QRectF(self._point, point).normalized())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._active and event.button() == Qt.MouseButton.LeftButton:
            self._active = False
            box = QRectF(self._point, self._local(event)).normalized()
            self._crop_item.setRect(box)
            if box.width() <= 1 or box.height() <= 1:
                self._callback(None)
            else:
                self._callback([
                    round(box.left() * self._scale_x, 4),
                    round(box.top() * self._scale_y, 4),
                    round(box.right() * self._scale_x, 4),
                    round(box.bottom() * self._scale_y, 4),
                ])
            event.accept()
            return
        super().mouseReleaseEvent(event)


class StatusCropDialog(AdaptiveDialog):
    def __init__(self, api, pdf_path, title, parent=None):
        super().__init__(parent)
        self.api = api
        self.pdf_path = pdf_path
        self.selected_crop = None
        self.pdf_page = 0
        self.setWindowTitle("Seleccionar diseño · " + title)
        self.resize(1000, 750)
        root = vbox(self, 14, 10)
        root.addWidget(label("Seleccione una sola etiqueta mediante el ratón", "panelTitle"))
        desc = label(
            "El documento puede contener las tres etiquetas. Dibuje el rectángulo "
            "de esta etiqueta exclusivamente, sin los títulos externos. "
            "Cada diseño se registrará como borrador independiente.",
            "subtle",
        )
        desc.setWordWrap(True)
        root.addWidget(desc)
        toolbar = QHBoxLayout()
        toolbar.addWidget(label("Página del Word/PDF", "subtle"))
        self.pages = QComboBox()
        toolbar.addWidget(self.pages)
        toolbar.addStretch()
        self.measurements = QLabel("Arrastre el ratón para elegir el área.")
        toolbar.addWidget(self.measurements)
        root.addLayout(toolbar)
        self.canvas = CropCanvas(self.crop_changed)
        root.addWidget(self.canvas, 1)
        footer = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        footer.button(QDialogButtonBox.StandardButton.Ok).setText("Confirmar recorte")
        footer.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        footer.accepted.connect(self.accept_if_valid)
        footer.rejected.connect(self.reject)
        root.addWidget(footer)
        self.footer = footer
        import fitz
        with fitz.open(self.pdf_path) as pdf:
            for index in range(len(pdf)):
                self.pages.addItem("Página " + str(index + 1), index)
        self.pages.currentIndexChanged.connect(self.display_page)
        self.display_page(0)

    def crop_changed(self, crop):
        self.selected_crop = crop
        valid = crop is not None and crop[2] - crop[0] > 10 and crop[3] - crop[1] > 8
        self.footer.button(QDialogButtonBox.StandardButton.Ok).setEnabled(valid)
        if valid:
            self.measurements.setText(
                f"Área: {(crop[2] - crop[0]) * 25.4 / 72:.1f} × "
                f"{(crop[3] - crop[1]) * 25.4 / 72:.1f} mm")
        else:
            self.measurements.setText("Seleccione el área completa de la etiqueta.")

    def display_page(self, index):
        if index < 0:
            return
        import fitz
        with fitz.open(self.pdf_path) as pdf:
            rect = pdf[index].rect
        image, _ = self.api.pdf_page(self.pdf_path, index, maxwidth=1400)
        self.pdf_page = index
        self.canvas.display_page(image, rect)

    def accept_if_valid(self):
        if not self.selected_crop:
            return
        try:
            from ..status_design import validate_layout
            import fitz
            with fitz.open(self.pdf_path) as pdf:
                validate_layout(
                    {"contract": 1, "kind": "sin_analizar", "page": self.pdf_page,
                     "crop": self.selected_crop, "fields": []}, pdf)
        except (StatusDesignError, OSError) as error:
            QMessageBox.warning(self, "Recorte incorrecto", str(error))
            return
        self.accept()

    def selection(self):
        if self.selected_crop is None:
            raise ValueError("No se confirmó un recorte.")
        return self.pdf_page, list(self.selected_crop)
