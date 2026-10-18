"""Read-only inspection and controlled PDF reprint for STATUS_ONLY emissions.

This dialog is accessible from the regular native History page and from the
state catalogue. It never changes lot status or marks physical printing.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QAbstractItemView, QDialogButtonBox,
    QHBoxLayout, QMessageBox, QInputDialog,
)

from .window import label, button, vbox
from .responsive import AdaptiveDialog
from .pdf_view import PdfPane

NAMES = {
    "sin_analizar": "Sin analizar", "aprobado": "Aprobado",
    "rechazado": "Rechazado",
}


class StatusHistoryDialog(AdaptiveDialog):
    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.catalog = api.status_catalog
        self.api = api
        self.rows = []
        self.setWindowTitle("Historial · Emisiones independientes de estado")
        self.resize(1020, 750)
        root = vbox(self, 14, 10)
        root.addWidget(label("Emisiones independientes de etiquetas de estado", "panelTitle"))
        note = label(
            "Consulta y reimpresión del PDF exacto registrado, también después "
            "de retirar la revisión. El histórico no certifica impresión física.",
            "subtle")
        note.setWordWrap(True)
        root.addWidget(note)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Identificador", "Fecha", "Etiqueta", "Revisión", "Operador", "Origen"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().hide()
        self.table.itemSelectionChanged.connect(self.selected)
        root.addWidget(self.table, 2)
        self.pdf = PdfPane(api)
        root.addWidget(self.pdf, 3)
        controls = QHBoxLayout()
        controls.addWidget(button("Actualizar historial", self.refresh))
        controls.addStretch()
        controls.addWidget(button("Verificar y abrir PDF", self.selected))
        controls.addWidget(button("Reimpresión controlada…", self.reprint, "primary"))
        root.addLayout(controls)
        footer = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        footer.rejected.connect(self.reject)
        root.addWidget(footer)
        self.refresh()

    def refresh(self):
        before = self.selected_uid()
        self.rows = self.catalog.issues()
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(len(self.rows))
            target = -1
            for index, entry in enumerate(self.rows):
                values = [
                    entry["uid"][:12], entry["created_at"][:19],
                    NAMES.get(entry["kind"], entry["kind"]),
                    entry["revision"], entry["operator"],
                    entry["origin_issue_uid"][:12] if entry["origin_issue_uid"] else "Original",
                ]
                for column, value in enumerate(values):
                    item = QTableWidgetItem(str(value))
                    item.setToolTip(str(value))
                    if column == 0:
                        item.setData(Qt.ItemDataRole.UserRole, entry["uid"])
                    self.table.setItem(index, column, item)
                if entry["uid"] == before:
                    target = index
        finally:
            self.table.blockSignals(False)
        if self.rows:
            self.table.selectRow(max(0, target))
        else:
            self.pdf.clear("Todavía no existen emisiones autónomas de estado.")

    def selected_uid(self):
        index = self.table.currentRow()
        if index < 0:
            return None
        item = self.table.item(index, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def selected(self):
        uid = self.selected_uid()
        if not uid:
            self.pdf.clear("Seleccione una emisión registrada.")
            return False
        try:
            entry, path = self.catalog.inspect_issue(uid)
            self.pdf.validator = lambda: self.catalog.inspect_issue(uid)
            self.pdf.load(
                path,
                "Documento registrado · " + uid[:12],
                "Versión: " + entry["revision"] +
                " · Se conserva el PDF original. Impresión física no confirmada.")
            return True
        except (OSError, ValueError, RuntimeError) as error:
            self.pdf.clear("PDF histórico bloqueado: " + str(error))
            return False

    def reprint(self):
        uid = self.selected_uid()
        if not uid:
            return
        try:
            self.catalog.inspect_issue(uid)
            reason, ok = QInputDialog.getText(
                self, "Reimpresión controlada", "Motivo documentado:")
            if not ok:
                return
            confirm = QMessageBox.question(
                self, "Confirmar reimpresión",
                "Se copiará exactamente el PDF histórico sin aplicar revisiones "
                "nuevas. ¿Confirma la reimpresión por el motivo indicado?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel)
            if confirm != QMessageBox.StandardButton.Yes:
                return
            operator = self.api.setting("operator")
            new_uid, _ = self.catalog.reprint(uid, operator, reason)
            self.refresh()
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0).data(Qt.ItemDataRole.UserRole) == new_uid:
                    self.table.selectRow(row)
                    break
        except (ValueError, OSError, PermissionError, RuntimeError) as error:
            QMessageBox.warning(self, "No se pudo reimprimir", str(error))
