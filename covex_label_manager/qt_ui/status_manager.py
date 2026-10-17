"""R7A independent status labels: Qt administration and standalone issue dialog."""
from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QDialogButtonBox, QFileDialog, QMessageBox, QDialog,
    QComboBox, QLineEdit, QLabel, QInputDialog, QFormLayout, QSpinBox,
    QDoubleSpinBox, QCheckBox, QSplitter,
)
from .window import label, button, vbox
from .pdf_view import PdfPane
from .responsive import AdaptiveDialog
from ..status_design import KINDS, make_layout

NAMES = {"sin_analizar": "Sin analizar", "aprobado": "Aprobado", "rechazado": "Rechazado"}
STATES = {"DRAFT": "Borrador", "PENDING": "Pendiente", "APPROVED": "Vigente",
          "RETIRED": "Retirada", "CANCELLED": "Anulada"}


class StatusManagerMixin:
    def __init__(self, session):
        self.status_manager_ready = False
        super().__init__(session)
        self.status_manager = self.build_status_manager()
        self.stack.addWidget(self.status_manager)
        self.status_manager_ready = True
        self.nav["status-manager"] = button(
            "Estados", lambda: self.navigate("status-manager"), "nav")
        self.nav["status-manager"].setCheckable(True)
        # Insert before header stretch: prominent independent library access.
        self.header.layout().insertWidget(self.header.layout().count() - 2,
                                          self.nav["status-manager"])
        self.refresh_status_manager()

    def build_status_manager(self):
        page = QWidget()
        layout = vbox(page, 16, 12)
        layout.addWidget(label("Etiquetas de estado", "title"))
        text = label(
            "Tres etiquetas independientes en Biblioteca: importación de un Word común o PDF,"
            " revisiones por diseño y emisión separada. Importar nunca autoriza la emisión.",
            "subtle",
        )
        text.setWordWrap(True)
        layout.addWidget(text)
        actions = QHBoxLayout()
        for caption, handler in (
            ("Importar Word/PDF", self.import_status_document),
            ("Revisiones", self.refresh_status_manager),
            ("Configurar recorte y campos", self.edit_status_draft),
            ("Presentar para revisión", self.submit_status_revision),
            ("Registrar aprobación externa", self.approve_status_revision),
            ("Retirar revisión", self.retire_status_revision),
        ):
            actions.addWidget(button(caption, handler))
        layout.addLayout(actions)
        self.status_table = QTableWidget(0, 5)
        self.status_table.setHorizontalHeaderLabels(["Etiqueta", "Revisión", "Situación", "Fecha", "Referencia"])
        self.status_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.status_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.status_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.status_table.horizontalHeader().setStretchLastSection(True)
        self.status_table.verticalHeader().hide()
        layout.addWidget(self.status_table, 2)
        bottom = QHBoxLayout()
        self.status_preview = PdfPane(self.api)
        bottom.addWidget(self.status_preview, 3)
        right = QWidget()
        right_layout = vbox(right, 12, 9)
        right_layout.addWidget(label("Emisión individual", "panelTitle"))
        right_layout.addWidget(label("Sin seleccionar etiqueta principal de producto.", "subtle"))
        right_layout.addWidget(button("Preparar / PDF de prueba", lambda: self.open_status_issue(True), "primary"))
        right_layout.addWidget(button("Emitir etiqueta individual", lambda: self.open_status_issue(False)))
        right_layout.addWidget(button("Ver original", self.view_status_original))
        right_layout.addStretch()
        bottom.addWidget(right, 2)
        layout.addLayout(bottom, 2)
        layout.addWidget(label("La emisión de «Aprobado» no representa liberación de material.", "subtle"))
        self.status_table.itemSelectionChanged.connect(self.update_status_selection)
        return page

    def navigate(self, key):
        if key == "status-manager" and getattr(self, "status_manager_ready", False):
            if self.legacy_process is not None or not self.flush_emission_work() or not self.resolve_work():
                return
            self.refresh_status_manager()
            self.stack.setCurrentWidget(self.status_manager)
            for name, action in self.nav.items():
                action.setChecked(name == key)
            return
        return super().navigate(key)

    def refresh_status_manager(self):
        if not getattr(self, "status_manager_ready", False):
            return
        previous = self.selected_status_uid()
        rows = self.api.status_catalog.list_revisions()
        self.status_table.setRowCount(len(rows))
        target = -1
        for index, row in enumerate(rows):
            values = [NAMES[row["kind"]], row["revision"], STATES[row["state"]],
                      row["created_at"][:16], row["approval_ref"] or "—"]
            for col, value in enumerate(values):
                cell = QTableWidgetItem(value)
                if col == 0:
                    cell.setData(Qt.ItemDataRole.UserRole, row["uid"])
                self.status_table.setItem(index, col, cell)
            if row["uid"] == previous:
                target = index
        if rows:
            self.status_table.selectRow(max(0, target))

    def selected_status_uid(self):
        if not hasattr(self, "status_table"):
            return None
        index = self.status_table.currentRow()
        if index < 0:
            return None
        item = self.status_table.item(index, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def selected_status(self):
        uid = self.selected_status_uid()
        if not uid:
            raise ValueError("Seleccione una etiqueta de estado.")
        return self.api.status_catalog.get(uid)

    def update_status_selection(self):
        try:
            rec = self.selected_status()
            if self.api.status_catalog.verify(rec["uid"]):
                self.status_preview.load(self.api.status_catalog.root / rec["pdf_path"])
        except (ValueError, OSError, RuntimeError) as err:
            self.status_preview.clear("Origen no disponible: " + str(err))

    def import_status_document(self):
        if self.legacy_process is not None:
            return
        filename, _ = QFileDialog.getOpenFileName(
            self, "Importar Word/PDF autorizado", "", "Word/PDF (*.docx *.pdf)"
        )
        if not filename:
            return
        # Conversion is temporary: not an activation or approval.
        import tempfile
        from ..importer import docx_to_pdf
        from ..status_design import validate_layout
        try:
            with tempfile.TemporaryDirectory() as temp:
                converted = docx_to_pdf(filename, temp)
                import fitz
                with fitz.open(converted) as doc:
                    entries = []
                    for kind in KINDS:
                        choice = QMessageBox.question(
                            self, "Diseño " + NAMES[kind],
                            "¿Está presente «" + NAMES[kind] + "» en el archivo?\n"
                            "Debe confirmar la página y el recorte; no se asignará vigencia.",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No
                        )
                        if choice != QMessageBox.StandardButton.Yes:
                            continue
                        page, ok = QInputDialog.getInt(
                            self, "Página de " + NAMES[kind], "Página (comienza en 1):",
                            1, 1, len(doc))
                        if not ok:
                            return
                        rect = doc[page - 1].rect
                        values = []
                        for prompt, default, maximum in (
                            ("Inicio horizontal X (puntos PDF)", rect.x0, rect.x1),
                            ("Inicio vertical Y (puntos PDF)", rect.y0, rect.y1),
                            ("Final horizontal X (puntos PDF)", rect.x1, rect.x1),
                            ("Final vertical Y (puntos PDF)", rect.y1, rect.y1),
                        ):
                            val, ok = QInputDialog.getDouble(
                                self, "Recorte: " + NAMES[kind], prompt,
                                float(default), 0, float(maximum), 2)
                            if not ok:
                                return
                            values.append(val)
                        revision, ok = QInputDialog.getText(
                            self, "Revisión documental", "Revisión autorizada de " + NAMES[kind] + ":")
                        if not ok:
                            return
                        proposed = make_layout(converted, kind, page-1, values)
                        entries.append({"kind": kind, "revision": revision.strip(), "layout": proposed})
                if entries:
                    response = QMessageBox.question(
                        self, "Confirmar importación",
                        f"Se crearán {len(entries)} borradores INDEPENDIENTES. "
                        "No se autoriza ninguna emisión.\n¿Guardar los diseños?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                        QMessageBox.StandardButton.Cancel
                    )
                    if response == QMessageBox.StandardButton.Yes:
                        self.api.status_catalog.import_many(filename, entries)
                        self.refresh_status_manager()
        except (ValueError, OSError, RuntimeError) as err:
            QMessageBox.warning(self, "Importación no realizada", str(err))

    def edit_status_draft(self):
        try:
            rec = self.selected_status()
            if rec["state"] != "DRAFT":
                raise PermissionError("Solo se modifica un borrador; cree una nueva revisión.")
            # Controlled JSON editor provides full field geometry, not arbitrary fixed-text editing.
            from PySide6.QtWidgets import QPlainTextEdit
            dialog = AdaptiveDialog(self)
            dialog.setWindowTitle("Diseño variable · " + NAMES[rec["kind"]])
            dialog.resize(700, 570)
            area = vbox(dialog, 12, 9)
            area.addWidget(label("Recorte, página y campos por etiqueta (PDF points)", "panelTitle"))
            editor = QPlainTextEdit()
            editor.setPlainText(json.dumps(json.loads(rec["layout_json"]), indent=2, ensure_ascii=False))
            area.addWidget(editor, 1)
            footer = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
            footer.accepted.connect(dialog.accept)
            footer.rejected.connect(dialog.reject)
            area.addWidget(footer)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.api.status_catalog.save_draft(rec["uid"], json.loads(editor.toPlainText()))
                self.refresh_status_manager()
        except (ValueError, PermissionError, OSError, RuntimeError) as err:
            QMessageBox.warning(self, "Diseño no guardado", str(err))

    def submit_status_revision(self):
        try:
            rec = self.selected_status()
            self.api.status_catalog.submit(rec["uid"])
            self.refresh_status_manager()
        except (ValueError, PermissionError, OSError) as err:
            QMessageBox.warning(self, "No presentada", str(err))

    def approve_status_revision(self):
        try:
            rec = self.selected_status()
            reviewer, ok = QInputDialog.getText(self, "Revisión documental", "Responsable:")
            if not ok:
                return
            ref, ok = QInputDialog.getText(self, "Evidencia externa", "Referencia documental de aprobación:")
            if not ok:
                return
            previous = self.api.status_catalog.current(rec["kind"])
            reason = None
            if previous:
                reason, ok = QInputDialog.getText(
                    self, "Sustituir revisión vigente", "Motivo documentado de la sustitución:")
                if not ok:
                    return
            check = QMessageBox.question(
                self, "Cotejo externo requerido",
                "¿Ha cotejado el documento con su versión autorizada y dispone de aprobación EXTERNA verificable?\n"
                "Este registro NO constituye una firma electrónica.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if check != QMessageBox.StandardButton.Yes:
                return
            self.api.status_catalog.approve(
                rec["uid"], reviewer, ref, confirmation=True, replacement_reason=reason)
            self.refresh_status_manager()
        except (ValueError, PermissionError, OSError) as err:
            QMessageBox.warning(self, "No aprobado", str(err))

    def retire_status_revision(self):
        try:
            rec = self.selected_status()
            reason, ok = QInputDialog.getText(self, "Retirada documental", "Motivo:")
            if ok:
                self.api.status_catalog.retire(rec["uid"], reason)
                self.refresh_status_manager()
        except (ValueError, PermissionError, OSError) as err:
            QMessageBox.warning(self, "No retirado", str(err))

    def view_status_original(self):
        try:
            rec = self.selected_status()
            self.api.status_catalog.verify(rec["uid"])
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl.fromLocalFile(
                str(self.api.status_catalog.root / rec["source_path"])))
        except (ValueError, PermissionError, OSError) as err:
            QMessageBox.warning(self, "Documento no disponible", str(err))

    def open_status_issue(self, proof):
        try:
            rec = self.selected_status()
            if not proof and rec["state"] != "APPROVED":
                raise PermissionError("Emisión bloqueada: revisión no aprobada externamente.")
            dialog = AdaptiveDialog(self)
            dialog.setWindowTitle(("PDF de prueba" if proof else "Emisión") + " · " + NAMES[rec["kind"]])
            dialog.resize(560, 530)
            box = vbox(dialog, 12, 8)
            form = QFormLayout()
            operator = QLineEdit(self.api.setting("operator"))
            form.addRow("Operador", operator)
            count = QSpinBox()
            count.setRange(1, 500)
            form.addRow("Número de etiquetas", count)
            paper = QComboBox()
            paper.addItems(["A4", "A3", "A5", "Carta"])
            form.addRow("Hoja", paper)
            width = QDoubleSpinBox()
            width.setRange(10, 500)
            width.setDecimals(2)
            width.setValue(json.loads(rec["layout_json"])["size_mm"][0])
            form.addRow("Anchura de etiqueta (mm)", width)
            controls = {}
            for field in json.loads(rec["layout_json"])["fields"]:
                widget = QLineEdit()
                widget.setPlaceholderText(field["label"])
                form.addRow(field["label"] + (" *" if field["required"] else ""), widget)
                controls[field["key"]] = widget
            box.addLayout(form)
            box.addWidget(label("El PDF de prueba no es apto para uso GMP.", "subtle"))
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            box.addWidget(buttons)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            values = {key: widget.text() for key, widget in controls.items()}
            options = {"count": count.value(), "paper": paper.currentText(),
                       "width_mm": width.value()}
            if proof:
                dest = self.api.status_catalog.preview(rec["uid"], values, **options)
            else:
                confirmation = QMessageBox.question(
                    self, "Confirmar emisión documental",
                    "¿Confirma la revisión de estado, su aprobación externa y los datos?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Cancel)
                if confirmation != QMessageBox.StandardButton.Yes:
                    return
                _, dest = self.api.status_catalog.emit(rec["uid"], values, operator.text(), **options)
            self.status_preview.load(dest)
            QMessageBox.information(self, "PDF generado", str(dest))
        except (ValueError, PermissionError, OSError, RuntimeError) as err:
            QMessageBox.warning(self, "No emitido", str(err))
