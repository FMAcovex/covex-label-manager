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
from .responsive import AdaptiveDialog as QDialog


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
        """Three human-readable areas; all prior actions remain accessible.

        Reorganization only: no new persistence, direct SQLite access, or
        change to existing documentary/approval service contracts.
        """
        page = QWidget()
        page.setObjectName('nativeSettings')
        layout = vbox(page, 18, 9)
        layout.addWidget(label('Configuración y datos', 'title'))
        subtitle = label(
            'Tus preferencias, documentos de referencia y herramientas de revisión, '
            'ordenados por finalidad. Cada acción indica si modifica información.',
            'subtle',
        )
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        self.settings_tabs = QTabWidget()
        self.settings_tabs.setObjectName('settingsMainTabs')
        self.settings_tabs.tabBar().setObjectName('settingsPrimaryNav')
        self.settings_tabs.setAccessibleName('Secciones de configuración')
        layout.addWidget(self.settings_tabs, 1)

        # GENERAL: the operator only needs these two pages for everyday use.
        general_container = QWidget()
        general_layout = vbox(general_container, 8, 6)
        self.settings_general_tabs = QTabWidget()
        self.settings_general_tabs.setObjectName('settingsGeneralTabs')
        general_layout.addWidget(self.settings_general_tabs, 1)
        self.settings_tabs.addTab(general_container, 'General')

        overview = _scroll_tab(self.settings_general_tabs, 'Resumen')
        summary = _section(
            overview, 'Tu biblioteca local',
            'Cifras de la instalación abierta. Las variantes no cuentan como revisiones.',
        )
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
        summary.addWidget(button('Actualizar cifras', self.refresh_native_settings))
        quick = _section(
            overview, 'Accesos habituales',
            'Elige una tarea. Las acciones de conciliación y consulta nunca aprueban documentos.',
        )
        quick.addWidget(button(
            'Cambiar operador o crear copia de seguridad…',
            lambda: self.open_settings_section(0, 1),
        ))
        quick.addWidget(button(
            'Comparar el libro máster con la biblioteca…',
            lambda: self.open_settings_section(1, 0),
        ))
        quick.addWidget(button('Ir a Biblioteca', lambda: self.navigate('library')))
        state = _section(
            overview, 'Uso documental',
            'Emitir un PDF no confirma su impresión. La aceptación en Windows, '
            'Word real, impresoras y la validación GMP siguen siendo actividades independientes.',
        )
        state.addWidget(button(
            'Ver pruebas y diagnóstico (administración)…',
            lambda: self.open_settings_section(2, 1),
        ))
        overview.addStretch()

        general = _scroll_tab(self.settings_general_tabs, 'Preferencias y copias')
        pref = _section(
            general, 'Operador de las emisiones',
            'Se guarda como dato del operador para nuevas emisiones. '
            'No supone inicio de sesión ni firma electrónica.',
        )
        self.settings_operator = QLineEdit()
        self.settings_operator.setObjectName('settingsOperator')
        self.settings_operator.setPlaceholderText('Nombre o identificador del operador')
        pref.addWidget(self.settings_operator)
        pref.addWidget(button('Guardar operador', self.save_settings_operator, 'primary'))
        data = _section(
            general, 'Carpeta local de datos · Solo consulta',
            'Muestra dónde se guarda la biblioteca. Copiar la ruta no mueve ni cambia ningún archivo.',
        )
        self.settings_data_path = QLineEdit()
        self.settings_data_path.setReadOnly(True)
        self.settings_data_path.setObjectName('settingsDataPath')
        data.addWidget(self.settings_data_path)
        data.addWidget(button('Copiar ruta', self.copy_settings_path))
        backup = _section(
            general, 'Copia de seguridad · Crea un archivo ZIP',
            'Incluye base de datos, maestros, fuentes, trabajos y evidencias. '
            'Es una acción de escritura en la carpeta de copias, no una restauración.',
        )
        backup.addWidget(button(
            'Crear copia de seguridad verificada…', self.create_settings_backup, 'primary',
        ))
        restore = label(
            'Para restaurar: cierre las aplicaciones, compruebe el ZIP y siga '
            'el procedimiento documentado sobre una carpeta nueva. '
            'No se restaura ni sobrescribe información desde esta pantalla.',
            'subtle',
        )
        restore.setWordWrap(True)
        backup.addWidget(restore)
        general.addStretch()

        # DOCUMENTARY tasks remain separate from local user preferences.
        docs_container = QWidget()
        docs_layout = vbox(docs_container, 8, 6)
        self.settings_documents_tabs = QTabWidget()
        self.settings_documents_tabs.setObjectName('settingsDocumentTabs')
        docs_layout.addWidget(self.settings_documents_tabs, 1)
        self.settings_tabs.addTab(docs_container, 'Gestión documental')

        master = _scroll_tab(self.settings_documents_tabs, 'Libro máster')
        reconciliation = _section(
            master, 'Conciliar libro máster · Solo lectura',
            'Compara un listado Excel XLSX, CSV o TSV que selecciones '
            'con las etiquetas y revisiones de la biblioteca local.',
        )
        reconciliation.addWidget(label(
            'Podrás revisar: coincidencias, etiquetas o revisiones ausentes, '
            'diferencias de metadatos/estado, duplicados y registros '
            'que solo constan en la aplicación.', 'subtle',
        ))
        self.settings_reconcile_button = button(
            'Seleccionar libro y comparar…', self.reconcile_master, 'primary',
        )
        reconciliation.addWidget(self.settings_reconcile_button)
        precautions = _section(
            master, '¿Qué hace y qué NO hace?',
            'Solo prepara un informe. No conecta con SharePoint, no importa '
            'etiquetas, no corrige códigos y no aprueba ni retira revisiones.',
        )
        precautions.addWidget(label(
            'El listado puede ser parcial: «Solo en biblioteca» no implica '
            'que debas eliminar documentos. Los códigos con ceros iniciales '
            'deben estar guardados como texto en Excel.', 'subtle',
        ))
        precautions.addWidget(button(
            'Inventariar documentos de una carpeta…', self.review_catalog_folder,
        ))
        master.addStretch()

        cm = _scroll_tab(self.settings_documents_tabs, 'Catálogo CM')
        catalog = _section(
            cm, 'Materiales y clasificación CM',
            'Importa materiales desde DOCX. Es una incorporación de datos '
            'que requiere confirmación: nunca corrige ni elimina duplicados automáticamente.',
        )
        self.settings_cm_summary = label('', 'subtle')
        catalog.addWidget(self.settings_cm_summary)
        catalog.addWidget(button(
            'Importar clasificación CM (DOCX)…', self.import_settings_cm, 'primary',
        ))
        duplicates = _section(
            cm, 'Códigos repetidos · Pendientes de revisión manual',
            'Consulta informativa. Ningún código se fusiona automáticamente.',
        )
        self.settings_duplicates = _read_only_table(
            ['Código', 'Coincidencias', 'Denominaciones'],
        )
        duplicates.addWidget(self.settings_duplicates)
        cm.addStretch()

        status = _scroll_tab(self.settings_documents_tabs, 'Maestros de estado')
        status_card = _section(
            status, 'Plantillas Sin analizar / Aprobado / Rechazado',
            'Solo se registra una aprobación documental externa ya existente. '
            'Requiere cotejar el diseño con el Word autorizado y aportar evidencias.',
        )
        self.settings_status = _read_only_table(
            ['Estado', 'Versión', 'Situación', 'Referencia'],
        )
        status_card.addWidget(self.settings_status)
        self.settings_approve_status = button(
            'Registrar aprobación documental externa…',
            self.approve_settings_status,
            'primary',
        )
        self.settings_approve_status.setToolTip(
            'Esta acción SÍ modifica el estado documental de un maestro pendiente. '
            'Requiere referencia, responsable y confirmación expresa.',
        )
        status_card.addWidget(self.settings_approve_status)
        status.addStretch()

        # ADVANCED is discoverable, but no longer occupies the user summary.
        advanced_container = QWidget()
        advanced_layout = vbox(advanced_container, 8, 6)
        self.settings_admin_tabs = QTabWidget()
        self.settings_admin_tabs.setObjectName('settingsAdminTabs')
        advanced_layout.addWidget(self.settings_admin_tabs, 1)
        self.settings_tabs.addTab(advanced_container, 'Administración avanzada')

        audit = _scroll_tab(self.settings_admin_tabs, 'Auditoría local')
        audit_card = _section(
            audit, 'Consulta del historial técnico',
            'Solo lectura. La auditoría local registra actividad, '
            'pero no es inviolable ni sustituye la documentación GMP.',
        )
        self.settings_audit = _read_only_table(
            ['Fecha', 'Evento', 'Referencia', 'Detalle'],
        )
        audit_card.addWidget(self.settings_audit)
        audit_card.addWidget(button('Actualizar movimientos', self.refresh_native_settings))
        audit.addStretch()

        diagnostic = _scroll_tab(self.settings_admin_tabs, 'Diagnóstico y pruebas')
        info = _section(
            diagnostic, 'Verificaciones técnicas de aceptación',
            'Herramientas para IT y Calidad. Una ejecución satisfactoria '
            'no aprueba por sí sola el uso en producción.',
        )
        info.addWidget(button('Diagnóstico de preaceptación…', self.open_acceptance_readiness))
        info.addWidget(button('Sesiones de pruebas presenciales…', self.open_uat_session))
        report = _section(
            diagnostic, 'Exportar evidencia técnica',
            'Genera un archivo local que debe revisarse antes de compartir. '
            'No reemplaza la copia de seguridad documental.',
        )
        report.addWidget(button(
            'Exportar informe de diagnóstico…', self.export_diagnostic_report,
        ))
        compatibility = _section(
            diagnostic, 'Compatibilidad con versión clásica',
            'Acceso excepcional a las opciones históricas. '
            'Cierre esa ventana antes de continuar editando en Qt.',
        )
        compatibility.addWidget(button(
            'Abrir Configuración clásica…', lambda: self.open_legacy('admin'),
        ))
        diagnostic.addStretch()
        return page

    def open_settings_section(self, group, section=0):
        """Navigation-only shortcut; never mutates source or audit data."""
        self.settings_tabs.setCurrentIndex(group)
        tabs = (
            self.settings_general_tabs,
            self.settings_documents_tabs,
            self.settings_admin_tabs,
        )[group]
        tabs.setCurrentIndex(section)

    def export_diagnostic_report(self):
        from ..diagnostics import Diagnostics
        diagnostic = getattr(self, 'diagnostics', None)
        owned = diagnostic is None
        try:
            if owned:diagnostic = Diagnostics(self.api.location(), install_hooks=False)
            filename, _ = QFileDialog.getSaveFileName(self, 'Exportar informe de diagnóstico',
                'COVEX-diagnostico.zip', 'Informe ZIP (*.zip)')
            if not filename:return
            diagnostic.export(filename)
            self.statusBar().showMessage('Informe técnico exportado. No incluye documentos, trabajos ni registros GMP.')
        except (ValueError, OSError):
            QMessageBox.warning(self, 'Informe no exportado',
                'No se pudo guardar el informe. Elija una carpeta local escribible y vuelva a intentarlo.')
        finally:
            if owned and diagnostic is not None:diagnostic.close()

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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if getattr(self, 'settings_ready', False):
            self.nav['settings'].setToolTip('Configuración · Función nativa Qt')

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

    def open_acceptance_readiness(self):
        if self.legacy_process is not None or not self.flush_emission_work() or not self.resolve_work():return
        try:
            from .acceptance_dialog import ReadinessDialog
            ReadinessDialog(self,self.api).exec()
        except Exception as ex:
            QMessageBox.warning(self,'Diagnóstico no iniciado',str(ex))

    def open_uat_session(self):
        if self.legacy_process is not None or not self.flush_emission_work() or not self.resolve_work():return
        try:
            from .uat_session_dialog import UatSessionDialog
            UatSessionDialog(self,self.api).exec()
        except Exception as ex:QMessageBox.warning(self,'Sesiones R6B no disponibles',str(ex))
