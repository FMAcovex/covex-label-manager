"""R3D native administrative settings, reusing the 0.3.1 services verbatim.

No direct SQLite access, no implicit document approval, no in-place data migration.
The classic window remains available through the transition bridge.
"""
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QTabWidget,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QFormLayout, QCheckBox,
)
from .window import label, button, vbox, box


def _scroll_tab(tabs, name):
    page = QWidget()
    page_layout = vbox(page, 14, 12)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    scroll.setWidget(page)
    tabs.addTab(scroll, name)
    return page_layout


def _section(layout, title, subtitle=None):
    card = box()
    inner = vbox(card, 16, 10)
    inner.addWidget(label(title, 'panelTitle'))
    if subtitle:
        desc = label(subtitle, 'subtle')
        desc.setWordWrap(True)
        inner.addWidget(desc)
    layout.addWidget(card)
    return inner


def _read_only_table(headers):
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setAlternatingRowColors(True)
    table.verticalHeader().hide()
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.setMinimumHeight(155)
    return table


class SettingsMixin:
    """Replace the temporary Configuracion catalogue, keeping Tk compatibility."""

    def __init__(self, session):
        self.settings_ready = False
        super().__init__(session)
        self.settings_page = self.build_native_settings()
        self.stack.addWidget(self.settings_page)
        self.settings_ready = True
        self.nav['settings'].setToolTip('Configuración y datos · Interfaz nativa Qt')
        self.refresh_native_settings()

    def build_native_settings(self):
        page = QWidget()
        page.setObjectName('nativeSettings')
        layout = vbox(page, 20, 11)
        layout.addWidget(label('Configuración y datos', 'title'))
        subtitle = label(
            'Preferencias locales, respaldo documental, clasificación CM, '
            'maestros de estado y trazabilidad. Sin cambiar los datos originales.',
            'subtle',
        )
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        self.settings_tabs = QTabWidget()
        layout.addWidget(self.settings_tabs, 1)

        overview = _scroll_tab(self.settings_tabs, 'Resumen')
        summary = _section(overview, 'Estado de la biblioteca',
                           'Recuentos reales de la instalación abierta; las variantes no se cuentan como revisiones.')
        tiles = QGridLayout()
        tiles.setSpacing(10)
        self.settings_counts = {}
        items = [
            ('labels', 'Etiquetas'),
            ('approved', 'Revisiones vigentes'),
            ('pending', 'Revisiones pendientes'),
            ('issues', 'Emisiones registradas'),
            ('materials', 'Materiales CM'),
        ]
        for index, (key, title) in enumerate(items):
            card = box()
            body = vbox(card, 12, 6)
            body.addWidget(label(title, 'subtle'))
            value = label('—', 'panelTitle')
            value.setObjectName('settingsCount_' + key)
            body.addWidget(value)
            self.settings_counts[key] = value
            tiles.addWidget(card, index // 3, index % 3)
        summary.addLayout(tiles)
        summary.addWidget(button('Actualizar recuentos', self.refresh_native_settings))
        info = _section(overview, 'Estado operativo')
        info.addWidget(label(
            'Los PDF generados no acreditan impresión física. Esta versión continúa '
            'pendiente de aceptación Windows/Word/impresora y validación GMP.', 'subtle',
        ))
        info.addWidget(button('Ir a Biblioteca', lambda: self.navigate('library')))
        overview.addStretch()

        general = _scroll_tab(self.settings_tabs, 'Preferencias y datos')
        pref = _section(general, 'Operador',
                        'Identificador que constará en las nuevas emisiones. No equivale a autenticación o firma electrónica.')
        self.settings_operator = QLineEdit()
        self.settings_operator.setObjectName('settingsOperator')
        self.settings_operator.setPlaceholderText('Nombre o identificador del operador')
        pref.addWidget(self.settings_operator)
        pref.addWidget(button('Guardar operador', self.save_settings_operator, 'primary'))
        data = _section(general, 'Directorio de datos',
                        'La ruta es solo de consulta. Para trasladarla, cierre la aplicación y utilice el procedimiento de copia íntegra.')
        self.settings_data_path = QLineEdit()
        self.settings_data_path.setReadOnly(True)
        self.settings_data_path.setObjectName('settingsDataPath')
        data.addWidget(self.settings_data_path)
        data.addWidget(button('Copiar ruta', self.copy_settings_path))
        backup = _section(general, 'Copia de seguridad ZIP',
                          'Incluye SQLite v4, maestros, fuentes, evidencias, trabajos y manifiestos. Guárdela en un lugar protegido.')
        backup.addWidget(button('Crear copia de seguridad verificada', self.create_settings_backup, 'primary'))
        restore = label(
            'Restauración: con ambas aplicaciones cerradas, verifique el ZIP y '
            'restaure en una carpeta nueva mediante el procedimiento documentado. '
            'No existe una restauración automática ni se debe sobrescribir data en uso.',
            'subtle',
        )
        restore.setWordWrap(True)
        backup.addWidget(restore)
        general.addStretch()

        cm = _scroll_tab(self.settings_tabs, 'Catálogo CM')
        catalog = _section(cm, 'Clasificación de materiales',
                           'Importación acumulativa desde DOCX; no borra, sobrescribe ni corrige duplicados automáticamente.')
        self.settings_cm_summary = label('', 'subtle')
        catalog.addWidget(self.settings_cm_summary)
        catalog.addWidget(button('Importar clasificación CM (DOCX)…', self.import_settings_cm, 'primary'))
        duplicates = _section(cm, 'Duplicidades de código — revisión manual')
        self.settings_duplicates = _read_only_table(['Código', 'Coincidencias', 'Denominaciones'])
        duplicates.addWidget(self.settings_duplicates)
        cm.addStretch()

        status = _scroll_tab(self.settings_tabs, 'Maestros de estado')
        status_card = _section(
            status, 'Etiquetas de estado',
            'Registrar una aprobación requiere cotejo con el Word autorizado y '
            'evidencia documental externa. No se aprueban automáticamente.',
        )
        self.settings_status = _read_only_table(['Estado', 'Versión', 'Situación', 'Referencia'])
        status_card.addWidget(self.settings_status)
        self.settings_approve_status = button(
            'Registrar aprobación documental…', self.approve_settings_status, 'primary',
        )
        status_card.addWidget(self.settings_approve_status)
        status.addStretch()

        audit = _scroll_tab(self.settings_tabs, 'Auditoría local')
        audit_card = _section(audit, 'Últimos movimientos',
                              'Consulta del registro local existente; no equivale a una auditoría inviolable.')
        self.settings_audit = _read_only_table(['Fecha', 'Evento', 'Referencia', 'Detalle'])
        audit_card.addWidget(self.settings_audit)
        audit_card.addWidget(button('Actualizar movimientos', self.refresh_native_settings))
        audit.addStretch()

        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(button('Configuración clásica (compatibilidad)…', lambda: self.open_legacy('admin')))
        layout.addLayout(footer)
        return page

    def navigate(self, key):
        if key == 'settings' and getattr(self, 'settings_ready', False):
            if self.legacy_process is not None:
                QMessageBox.information(self, 'Configuración clásica abierta',
                                        'Cierre la ventana anterior antes de editar desde Qt.')
                return
            if not self.flush_emission_work() or not self.resolve_work():
                return
            self.refresh_native_settings()
            self.stack.setCurrentWidget(self.settings_page)
            for name, action in self.nav.items():
                action.setChecked(name == 'settings')
            return
        return super().navigate(key)

    def set_mutations_enabled(self, enabled):
        super().set_mutations_enabled(enabled)
        if getattr(self, 'settings_ready', False):
            self.settings_page.setEnabled(enabled)

    def poll_legacy(self):
        was_open = self.legacy_process is not None
        super().poll_legacy()
        if was_open and self.legacy_process is None and getattr(self, 'settings_ready', False):
            self.refresh_native_settings()

    def refresh_native_settings(self):
        if not getattr(self, 'settings_ready', False):
            return
        stats = self.api.stats()
        for key, widget in self.settings_counts.items():
            widget.setText(str(stats.get(key, 0)))
        self.settings_operator.setText(self.api.setting('operator'))
        path = self.api.location()
        self.settings_data_path.setText(path)
        self.settings_data_path.setToolTip(path)
        dups = list(self.api.material_duplicates())
        self.settings_cm_summary.setText(
            f'{stats["materials"]} materiales cargados · {len(dups)} códigos duplicados por revisar',
        )
        self.settings_duplicates.setRowCount(len(dups))
        for index, row in enumerate(dups):
            for col, value in enumerate((row['code'], str(row['total']), row['names'])):
                cell = QTableWidgetItem(str(value or ''))
                cell.setToolTip(str(value or ''))
                self.settings_duplicates.setItem(index, col, cell)

        self.settings_status.setRowCount(0)
        for asset in self.api.status_masters():
            row = self.settings_status.rowCount()
            self.settings_status.insertRow(row)
            values = (asset['name'], asset['version'], asset['state'], asset['approval_ref'] or '—')
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if col == 0:
                    item.setData(Qt.ItemDataRole.UserRole, asset['kind'])
                self.settings_status.setItem(row, col, item)
        self.settings_approve_status.setEnabled(
            any(asset['state'] == 'PENDING' for asset in self.api.status_masters())
        )

        entries = list(self.api.audit_entries())
        self.settings_audit.setRowCount(len(entries))
        for index, row in enumerate(entries):
            values = (row['at'][:19], row['event'], row['subject'], row['detail'])
            for col, value in enumerate(values):
                cell = QTableWidgetItem(str(value or ''))
                cell.setToolTip(str(value or ''))
                self.settings_audit.setItem(index, col, cell)

    def save_settings_operator(self):
        new = self.settings_operator.text().strip()
        if len(new) < 3:
            QMessageBox.warning(self, 'Operador obligatorio', 'Indique un nombre o identificador de al menos tres caracteres.')
            return False
        try:
            self.api.set_setting('operator', new)
            self.refresh_native_settings()
            self.statusBar().showMessage('Operador actualizado; no se ha modificado el historial.')
            return True
        except (ValueError, OSError) as ex:
            QMessageBox.warning(self, 'No guardado', str(ex))
            return False

    def copy_settings_path(self):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.api.location())

    def create_settings_backup(self):
        if self.legacy_process is not None or not self.flush_emission_work() or not self.resolve_work():
            return False
        answer = QMessageBox.question(
            self, 'Confirmar copia de seguridad',
            'Se creará una copia ZIP verificada con los archivos y el catálogo actuales.\n\n'
            '¿Continuar? No se sobrescribirán copias anteriores.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return False
        try:
            path = self.api.backup()
            self.refresh_native_settings()
            QMessageBox.information(
                self, 'Copia verificada',
                'Copia creada en:\n' + str(path) + '\n\nConserve el archivo en un lugar protegido.',
            )
            return True
        except (ValueError, OSError, RuntimeError) as ex:
            QMessageBox.warning(self, 'Copia no creada', str(ex))
            return False

    def import_settings_cm(self):
        if self.legacy_process is not None or not self.flush_emission_work():
            return False
        source, _ = QFileDialog.getOpenFileName(
            self, 'Seleccionar clasificación CM', '', 'Documento Word DOCX (*.docx)',
        )
        if not source:
            return False
        if Path(source).suffix.lower() != '.docx':
            QMessageBox.warning(self, 'Archivo incorrecto', 'Seleccione un archivo DOCX.')
            return False
        try:
            rows = self.api.read_cm(source)
            if not rows:
                raise ValueError('No hay materiales reconocibles en el documento.')
            answer = QMessageBox.question(
                self, 'Confirmar incorporación CM',
                f'Se han identificado {len(rows)} filas en el DOCX.\n\n'
                'Se incorporarán sin borrar ni corregir automáticamente registros anteriores.\n'
                '¿Continuar?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return False
            self.api.import_materials(rows)
            self.refresh_native_settings()
            return True
        except (ValueError, OSError) as ex:
            QMessageBox.warning(self, 'CM no importado', str(ex))
            return False

    def approve_settings_status(self):
        row = self.settings_status.currentRow()
        if row < 0:
            QMessageBox.information(self, 'Seleccione un maestro',
                                    'Seleccione primero una etiqueta de estado pendiente.')
            return False
        item = self.settings_status.item(row, 0)
        kind = item.data(Qt.ItemDataRole.UserRole) if item else None
        asset = self.api.status_master(kind) if kind else None
        if not asset or asset['state'] != 'PENDING':
            QMessageBox.warning(self, 'Aprobación no disponible',
                                'El maestro seleccionado ya no está pendiente.')
            self.refresh_native_settings()
            return False

        dialog = QDialog(self)
        dialog.setWindowTitle('Registro documental externo · ' + asset['name'])
        dialog.resize(560, 320)
        lay = vbox(dialog, 18, 12)
        note = label(
            'Esta acción registra una aprobación externa existente. '
            'Verifique previamente el documento Word autorizado.', 'subtle',
        )
        note.setWordWrap(True)
        lay.addWidget(note)
        form = QFormLayout()
        reviewer = QLineEdit()
        reviewer.setObjectName('statusApprovalReviewer')
        evidence = QLineEdit()
        evidence.setObjectName('statusApprovalReference')
        form.addRow('Responsable de la revisión', reviewer)
        form.addRow('Referencia documental vigente', evidence)
        lay.addLayout(form)
        ack = QCheckBox('He cotejado físicamente el diseño con su Word autorizado.')
        ack.setObjectName('statusApprovalAcknowledgement')
        lay.addWidget(ack)
        error = label('', 'fieldError')
        error.setWordWrap(True)
        lay.addWidget(error)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText('Registrar aprobación')
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText('Cancelar')
        def validate():
            valid = len(reviewer.text().strip()) >= 3 and len(evidence.text().strip()) >= 5 and ack.isChecked()
            buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(valid)
            return valid
        reviewer.textChanged.connect(validate)
        evidence.textChanged.connect(validate)
        ack.toggled.connect(validate)
        buttons.accepted.connect(lambda: dialog.accept() if validate() else error.setText('Complete los datos y el cotejo.'))
        buttons.rejected.connect(dialog.reject)
        lay.addWidget(buttons)
        validate()
        if dialog.exec() != QDialog.DialogCode.Accepted or not validate():
            return False
        try:
            current = self.api.status_master(kind)
            if current['state'] != 'PENDING':
                raise ValueError('El maestro cambió de estado. Recargue la información.')
            self.api.approve_status_master(kind, reviewer.text().strip(), evidence.text().strip())
            self.refresh_native_settings()
            return True
        except (ValueError, OSError) as ex:
            QMessageBox.warning(self, 'Aprobación no registrada', str(ex))
            return False
