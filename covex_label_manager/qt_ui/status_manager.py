"""R7A independent status labels: Qt administration and standalone issue dialog."""
from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt,QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QDialogButtonBox, QFileDialog, QMessageBox, QDialog,
    QComboBox, QLineEdit, QLabel, QInputDialog, QFormLayout, QSpinBox,
    QDoubleSpinBox, QCheckBox, QSplitter,QScrollArea,
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
        self._active_status_uid = None
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
        if getattr(self, "history_ready", False):
            history_bar = self.history_page.layout().itemAt(0).layout()
            history_bar.insertWidget(
                max(0, history_bar.count()-1),
                button("Historial de estados", self.open_status_history))

    def build_emission_page(self):
        # No extra vertical row: the compact 1366x768 emission acceptance
        # depends on retaining minimum PDF preview height.
        from PySide6.QtWidgets import QMenu
        page = super().build_emission_page()
        header = page.layout().itemAt(0).layout()
        menu_button = button("Estados ▾", lambda: None)
        menu_button.setToolTip("Emitir Sin analizar, Aprobado o Rechazado por separado.")
        menu = QMenu(menu_button)
        for kind in KINDS:
            menu.addAction(NAMES[kind],
                           lambda checked=False, kind=kind:
                           self.open_library_status(kind))
        menu_button.setMenu(menu)
        self.status_emission_menu = menu
        self.status_emission_button = menu_button
        header.insertWidget(max(0, header.count()-1), menu_button)
        return page

    def build_library(self):
        # AC1: no second banner above the table. Registered status revisions
        # are rendered as ordinary rows in the same QTableWidget.
        return super().build_library()

    def make_filter(self, key):
        combo = super().make_filter(key)
        self._add_status_filter_options(key, combo)
        return combo

    @staticmethod
    def _add_status_filter_options(key, combo):
        extras = {
            "category": [("Etiquetas de estado", "Etiquetas de estado")],
            "type": [("Etiqueta de estado", "Etiqueta de estado")],
            "state": [("Borrador", "DRAFT")],
        }
        for title, code in extras.get(key, []):
            if combo.findData(code) < 0:
                combo.addItem(title, code)
        if combo.count() > 1:
            combo.setEnabled(True)

    def refresh_facets(self):
        super().refresh_facets()
        for key in ("category", "type", "state"):
            if key in self.filters:
                self._add_status_filter_options(key, self.filters[key])

    def _visible_status_revisions(self):
        filters = {key: control.currentData() for key, control in self.filters.items()}
        query = self.search.text().strip().casefold()
        if self.mode == "favorites":
            return []
        if filters.get("category") not in ("", None, "Etiquetas de estado"):
            return []
        if filters.get("type") not in ("", None, "Etiqueta de estado"):
            return []
        if filters.get("origin") not in ("", None, "COVEX"):
            return []
        if any(filters.get(key) for key in ("family", "customer", "country", "language", "acquisition")):
            return []
        results = []
        for revision in self.api.status_catalog.list_revisions():
            if filters.get("state") and filters["state"] != revision["state"]:
                continue
            if filters.get("version") and filters["version"] != revision["revision"]:
                continue
            kind = revision["kind"]
            searchable = " ".join((
                NAMES[kind], kind, "etiqueta de estado",
                revision["revision"], STATES[revision["state"]],
                revision["approval_ref"] or "",
            )).casefold()
            if query and query not in searchable:
                continue
            results.append(revision)
        return results

    def refresh(self, *_):
        # The base Library refresh owns product rows. Append status records,
        # never fake product-version IDs or mutate the validated product store.
        selected_status = getattr(self, "_active_status_uid", None)
        super().refresh(*_)
        if not getattr(self, "status_manager_ready", False):
            return
        revisions = self._visible_status_revisions()
        from PySide6.QtGui import QColor
        table = self.table
        previous = table.blockSignals(True)
        try:
            initial = table.rowCount()
            table.setRowCount(initial + len(revisions))
            for offset, rec in enumerate(revisions):
                kind = rec["kind"]
                state = rec["state"]
                values = [
                    "☆", "EST-" + kind.upper().replace("_", "-"),
                    NAMES[kind], "Etiqueta de estado", rec["revision"],
                    "COVEX", "", "", STATES[state],
                ]
                marker = "status:" + rec["uid"]
                for column, value in enumerate(values):
                    cell = QTableWidgetItem(value)
                    cell.setData(Qt.ItemDataRole.UserRole, marker)
                    cell.setToolTip(value)
                    table.setItem(initial + offset, column, cell)
                colors = {
                    "APPROVED": "#247454", "PENDING": "#90651D",
                    "DRAFT": "#4B6478", "RETIRED": "#986066",
                    "CANCELLED": "#986066",
                }
                table.item(initial + offset, 8).setForeground(QColor(colors.get(state, "#4B6478")))
            self.count.setText(f"{table.rowCount()} revisiones")
            few = 0 < table.rowCount() <= 5
            self.selection_help.setVisible(few)
            table.setMaximumHeight(max(170, 60 + 46 * table.rowCount()) if few else 16777215)
        finally:
            table.blockSignals(previous)
        if selected_status:
            self.select_version("status:" + selected_status)
        elif not self.rows and revisions:
            self.select_version("status:" + revisions[0]["uid"])

    def _library_status_uid(self):
        item = self.table.item(self.table.currentRow(), 0) if self.table.currentRow() >= 0 else None
        marker = item.data(Qt.ItemDataRole.UserRole) if item else None
        if isinstance(marker, str) and marker.startswith("status:"):
            return marker.split(":", 1)[1]
        return None

    def select_version(self, vid):
        if isinstance(vid, str) and vid.startswith("status:"):
            for index in range(self.table.rowCount()):
                item = self.table.item(index, 0)
                if item and item.data(Qt.ItemDataRole.UserRole) == vid:
                    self.table.selectRow(index)
                    self.selected()
                    return True
            return False
        return super().select_version(vid)

    def selected(self):
        uid = self._library_status_uid() if hasattr(self, "table") else None
        if uid is None:
            self._active_status_uid = None
            if hasattr(self,'inspector_editor_button'):self.inspector_editor_button.setText('Abrir en Editor')
            for name in ('favorite_button','prepare_button','test_button','native_approval_button'):
                control=getattr(self,name,None)
                if control is not None:control.setVisible(True)
            if hasattr(self, "favorite_button"):
                self.favorite_button.setEnabled(True)
            return super().selected()
        try:
            rec = self.api.status_catalog.verify(uid)
            self._active_status_uid = uid
            self.row = None  # Product-specific actions cannot target a status.
            self.inspector_panel.setEnabled(True)
            self.doc_title.setText(NAMES[rec["kind"]])
            self.badge.setText(STATES[rec["state"]])
            color = "#247454" if rec["state"] == "APPROVED" else "#90651D"
            self.badge.setStyleSheet("color:" + color + ";")
            from PIL import Image
            import fitz
            design = json.loads(rec["layout_json"])
            path = self.api.status_catalog.root / rec["pdf_path"]
            with fitz.open(path) as pdf:
                pix = pdf[design["page"]].get_pixmap(
                    matrix=fitz.Matrix(1.8, 1.8),
                    clip=fitz.Rect(design["crop"]), alpha=False)
                clipped = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            self.preview.set_image(clipped)
            details = [
                ("Tipo", "Etiqueta de estado"),
                ("Etiqueta", NAMES[rec["kind"]]),
                ("Revisión", rec["revision"]),
                ("Estado documental", STATES[rec["state"]]),
                ("Dimensiones", "{:.2f} × {:.2f} mm".format(*design["size_mm"])),
                ("Aprobación externa", rec["approval_ref"] or "No registrada"),
            ]
            self.meta.setText("\n\n".join(a + "   " + b for a, b in details))
            self.selection_summary.setText(
                NAMES[rec["kind"]] + " · Rev. " + rec["revision"])
            self.revision.blockSignals(True)
            try:
                self.revision.clear()
                for item in self.api.status_catalog.list_revisions(rec["kind"]):
                    self.revision.addItem(
                        "Revisión " + item["revision"] + " · " + STATES[item["state"]],
                        "status:" + item["uid"])
                self.revision.setCurrentIndex(
                    self.revision.findData("status:" + uid))
            finally:
                self.revision.blockSignals(False)
            self.doc_note.setText(
                ("Aprobación externa: " + rec["approval_ref"] if rec["approval_ref"]
                 else "Borrador/pendiente: emitir únicamente PDF de prueba."))
            self.favorite_button.setEnabled(False)
            # Status revision operations live in the state manager. Do not show
            # product-only inactive controls that appear broken on this selection.
            for name in ('favorite_button','prepare_button','test_button','native_approval_button'):
                control=getattr(self,name,None)
                if control is not None:control.setVisible(False)
            self.inspector_editor_button.setText('Consultar revisión de estado' if rec['state'] != 'DRAFT' else 'Editar borrador de estado')
            self.inspector_editor_button.setToolTip('Abrir el gestor de estados y sus revisiones.' if rec['state'] != 'DRAFT' else 'Editar campos variables de esta revisión en borrador.')
            self.inspector_editor_button.setEnabled(True)
            self.recheck_actions()
        except (ValueError, OSError, RuntimeError) as err:
            self._active_status_uid = uid
            self.row = None
            self.preview.scene().clear()
            self.doc_note.setText("Etiqueta de estado no disponible: " + str(err))
            self.recheck_actions()

    def revision_changed(self, index):
        marker = self.revision.itemData(index)
        if isinstance(marker, str) and marker.startswith("status:"):
            if not self.select_version(marker):
                QMessageBox.information(
                    self, "Revisión fuera de filtro",
                    "Quite los filtros para mostrar esta revisión de estado.")
            return
        return super().revision_changed(index)

    def open_editor(self):
        uid = self._library_status_uid() if hasattr(self, "table") else None
        if uid:
            rec = self.api.status_catalog.get(uid)
            if rec["state"] == "DRAFT":
                from .status_fields_dialog import StatusFieldsDialog
                if StatusFieldsDialog(self.api, rec, self).exec() == QDialog.DialogCode.Accepted:
                    self.refresh_status_manager()
                    self.select_version("status:" + uid)
            else:
                QMessageBox.information(
                    self, "Diseño protegido",
                    "Solo puede editar una revisión en Borrador.\n"
                    "En Estados → Nueva revisión podrá crear un borrador independiente.")
                self.open_library_status(rec['kind'], uid=uid)
            return
        return super().open_editor()

    def favorite(self):
        if getattr(self, "_active_status_uid", None):
            return  # No favorites are written into a fictitious product record.
        return super().favorite()

    def enlarge(self):
        if getattr(self, "_active_status_uid", None):
            self.open_library_status(self.api.status_catalog.get(self._active_status_uid)["kind"])
            return
        return super().enlarge()

    def document_details(self):
        if getattr(self, "_active_status_uid", None):
            rec = self.api.status_catalog.get(self._active_status_uid)
            self.open_library_status(rec["kind"], uid=rec["uid"])
            return
        return super().document_details()

    def show_access(self, key):
        """Status inspector links must open the selected status, not product-only pages."""
        uid = self._library_status_uid() if hasattr(self, "table") else None
        if uid and key in ("document", "import"):
            rec = self.api.status_catalog.get(uid)
            self.open_library_status(rec["kind"], uid=uid)
            return
        return super().show_access(key)

    def inspector_emission(self):
        """Route inspector emission access to the independent status issue flow."""
        uid = self._library_status_uid() if hasattr(self, "table") else None
        if uid:
            rec = self.api.status_catalog.get(uid)
            self.open_library_status(rec["kind"], uid=uid)
            return
        return super().inspector_emission()

    def document_menu(self):
        if getattr(self, "_active_status_uid", None):
            from PySide6.QtWidgets import QMenu
            menu = QMenu(self)
            menu.addAction("Abrir ficha de estado", self.document_details)
            menu.addAction("Editar campos del borrador", self.open_editor)
            menu.addAction("Gestionar revisiones", lambda: self.navigate("status-manager"))
            return menu
        return super().document_menu()

    def open_library_status(self, kind, uid=None):
        self.navigate("status-manager")
        if self.stack.currentWidget() is not getattr(self, "status_manager", None):
            return
        revisions = self.api.status_catalog.list_revisions(kind)
        selected = next((r for r in revisions if r["uid"] == uid), None) if uid else None
        active = next((r for r in revisions if r["state"] == "APPROVED"), None)
        chosen = selected or active or (revisions[0] if revisions else None)
        if chosen:
            for row in range(self.status_table.rowCount()):
                item = self.status_table.item(row, 0)
                if item and item.data(Qt.ItemDataRole.UserRole) == chosen["uid"]:
                    self.status_table.selectRow(row)
                    break
        else:
            self.status_preview.clear(
                "Aún no se ha importado esta etiqueta. Utilice «Importar Word/PDF».")

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
            ("Nueva revisión", self.clone_status_revision),
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
        right_layout.addWidget(button("Historial y reimpresiones", self.open_status_history))
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
        self.refresh()

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
            self.api.status_catalog.verify(rec["uid"])
            from ..status_design import render_proof
            import uuid
            original = self.api.status_catalog.root / rec["pdf_path"]
            layout = json.loads(rec["layout_json"])
            proof = self.api.output_path(
                "cache", "status-selection-" + uuid.uuid4().hex + ".pdf")
            render_proof(original, layout, {}, proof,
                         width_mm=min(130, layout["size_mm"][0]))
            self.status_preview.validator = (
                lambda uid=rec["uid"]: self.api.status_catalog.verify(uid))
            self.status_preview.load(
                proof, "Recorte de " + NAMES[rec["kind"]],
                "PRUEBA visual del recorte · Sin autorización de uso GMP.")
        except (ValueError, OSError, RuntimeError) as err:
            self.status_preview.clear("Diseño no disponible: " + str(err))

    def open_status_history(self):
        from .status_history_dialog import StatusHistoryDialog
        StatusHistoryDialog(self.api, self).exec()

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
                        from .status_crop_dialog import StatusCropDialog
                        crop_dialog = StatusCropDialog(
                            self.api, converted, NAMES[kind], self)
                        if crop_dialog.exec() != QDialog.DialogCode.Accepted:
                            return
                        page_index, values = crop_dialog.selection()
                        revision, ok = QInputDialog.getText(
                            self, "Revisión documental", "Revisión autorizada de " + NAMES[kind] + ":")
                        if not ok:
                            return
                        proposed = make_layout(converted, kind, page_index, values)
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

    def clone_status_revision(self):
        try:
            base = self.selected_status()
            revision, ok = QInputDialog.getText(
                self, "Nueva revisión", "Código de la nueva revisión de " +
                NAMES[base["kind"]] + ":")
            if not ok:
                return
            reason, ok = QInputDialog.getText(
                self, "Justificación documental",
                "Motivo de crear una nueva revisión:")
            if not ok:
                return
            uid = self.api.status_catalog.new_revision(
                base["uid"], revision.strip(), reason.strip())
            self.refresh_status_manager()
            for row in range(self.status_table.rowCount()):
                item = self.status_table.item(row, 0)
                if item and item.data(Qt.ItemDataRole.UserRole) == uid:
                    self.status_table.selectRow(row)
                    break
        except (ValueError, OSError, PermissionError) as err:
            QMessageBox.warning(self, "Revisión no creada", str(err))

    def edit_status_draft(self):
        try:
            rec = self.selected_status()
            if rec["state"] != "DRAFT":
                raise PermissionError("Solo se modifica un borrador; cree una nueva revisión.")
            from .status_fields_dialog import StatusFieldsDialog
            dialog = StatusFieldsDialog(self.api, rec, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
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
            dialog.resize(1000, 720)
            box = vbox(dialog, 12, 8)
            split=QSplitter();panel=QWidget();form=QFormLayout(panel)
            form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
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
            height=QDoubleSpinBox();height.setRange(8,500);height.setDecimals(2)
            source_size=json.loads(rec['layout_json'])['size_mm']
            height.setValue(source_size[1]);form.addRow('Altura de área (mm)',height)
            composition=QComboBox()
            for title,key in [('Histórico · proporcional',None),('Ajustar sin deformar','fit'),('Rellenar · recorte protegido','fill')]:composition.addItem(title,key)
            form.addRow('Composición física',composition)
            def adapt_size(*_):
                height.setEnabled(composition.currentData() is not None)
                if composition.currentData() is None:height.setValue(width.value()*source_size[1]/source_size[0])
            composition.currentIndexChanged.connect(adapt_size);width.valueChanged.connect(adapt_size);adapt_size()
            information=label('Histórico conserva las métricas anteriores. Ajustar puede dejar margen. Rellenar bloquea cualquier recorte crítico. La revisión documental seleccionada no cambia.','subtle');information.setWordWrap(True);form.addRow(information)
            controls = {}
            for field in json.loads(rec["layout_json"])["fields"]:
                widget = QLineEdit()
                widget.setPlaceholderText(field["label"])
                form.addRow(field["label"] + (" *" if field["required"] else ""), widget)
                controls[field["key"]] = widget
            scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(panel);scroll.setMaximumWidth(340);split.addWidget(scroll)
            pane=PdfPane(self.api);split.addWidget(pane);split.setStretchFactor(1,1);box.addWidget(split,1)
            timer=QTimer(dialog);timer.setSingleShot(True)
            def settings():
                options={'count':count.value(),'paper':paper.currentText(),'width_mm':width.value()}
                if composition.currentData():
                    options.update(height_mm=height.value(),composition=dict(contract=1,mode=composition.currentData(),align_x='center',align_y='middle'))
                return options
            def live_preview():
                try:
                    values={key:widget.text() for key,widget in controls.items()}
                    dest=self.api.status_catalog.preview(rec['uid'],values,**settings())
                    pane.load(dest,'PDF real · PRUEBA / NO GMP',f"{NAMES[rec['kind']]} · Revisión {rec['revision']} · "+('Sin deformación · el recorte crítico bloquea el PDF.' if composition.currentData() else 'Proporción histórica.'))
                    import fitz
                    with fitz.open(dest) as pdf:
                        details=pdf.metadata.get('subject','')
                    if details:pane.note.setText(pane.note.text()+'\n'+details)
                except (ValueError,OSError,RuntimeError) as err:pane.clear('Prueba bloqueada: '+str(err))
            timer.timeout.connect(live_preview)
            for control in (count,width,height):control.valueChanged.connect(lambda *_:timer.start(350))
            for control in (paper,composition):control.currentIndexChanged.connect(lambda *_:timer.start(350))
            for control in controls.values():control.textEdited.connect(lambda *_:timer.start(350))
            QTimer.singleShot(0,dialog,live_preview)
            box.addWidget(label("El PDF de prueba no es apto para uso GMP.", "subtle"))
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            box.addWidget(buttons)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            values = {key: widget.text() for key, widget in controls.items()}
            timer.stop();options=settings()
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
