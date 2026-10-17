"""R3A Qt: functional library, retained work and explicit legacy access."""
import copy
import json
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QKeySequence, QShortcut, QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QFormLayout,QLineEdit,
    QDialog,QDialogButtonBox,QMessageBox,QFileDialog,QInputDialog,QMenu,QCheckBox,QPushButton,QLabel)
from .window import StudioWindow,STATE,FILTERS,label,button,vbox
from .status_manager import StatusManagerMixin
from .responsive import AdaptiveDialog as QDialog
from ..contracts import METADATA_FIELDS
from ..qt_legacy import launch_legacy

class BaseFunctionalWindow(StudioWindow):
    def __init__(self,session):
        self.legacy_process=None;self.demo=getattr(session,'fictional',False)
        self.original_fields={};self.dirty=False;self._initializing=True;self._filter_expanded_preference=None
        super().__init__(session)
        self._initializing=False
        self.setWindowTitle('COVEX Label Manager · R3A Qt · Transición')
        for note in self.header.findChildren(QLabel):
            if 'PRUEBA VISUAL' in note.text():note.setText('DATOS FICTICIOS' if self.demo else 'R3A Qt · Local')
        self.statusBar().showMessage('Biblioteca Qt funcional · Ajuste avanzado completo e impresión disponibles en la versión anterior')
        remember,expanded=self.api.filter_preferences();self.remember_filters.blockSignals(True);self.remember_filters.setChecked(remember);self.remember_filters.blockSignals(False)
        self.advanced.setVisible(expanded);self.advanced_button.setChecked(expanded);self._filter_expanded_preference=expanded
        self.table_shortcut=QShortcut(QKeySequence('Return'),self.table);self.table_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.table_shortcut.activated.connect(self.open_editor)
        self.legacy_timer=QTimer(self);self.legacy_timer.timeout.connect(self.poll_legacy);self.legacy_timer.start(500)
        self.poll_timer=QTimer(self);self.poll_timer.timeout.connect(self.recheck_actions);self.poll_timer.start(1500)
        self.refresh();self.recheck_actions()

    def build_library(self):
        page=super().build_library()
        for note in self.inspector.findChildren(QLabel):
            if 'PDF ficticio' in note.text():note.setText('Documentos locales · Fuente controlada')
        for widget in self.inspector.findChildren(QPushButton):
            replacements={'Ficha completa y referencias':self.document_details,
                'Documentos y aprobación externa':lambda:self.open_document(),
                'Importaciones PDF / Word':lambda:self.open_document(True)}
            if widget.text() in replacements:
                old_text=widget.text()
                widget.clicked.disconnect();widget.clicked.connect(replacements[old_text])
                widget.setText({'Documentos y aprobación externa':'Abrir PDF maestro',
                    'Importaciones PDF / Word':'Abrir documento original'}.get(old_text,old_text))
        self.active_filter_text=label('','subtle');page.layout().insertWidget(3,self.active_filter_text)
        self.remember_filters=QCheckBox('Recordar apertura')
        self.remember_filters.setToolTip('Recordar si los filtros avanzados estaban abiertos o cerrados entre inicios.')
        self.remember_filters.toggled.connect(self.remember_filter_choice)
        self.advanced.layout().insertWidget(1,self.remember_filters)
        self.prepare_button=button('Preparar emisión',lambda:self.open_legacy('emitir'),'primary','print')
        self.test_button=button('PDF de prueba',lambda:self.open_legacy('emitir',mode='test'))
        layout=self.inspector.layout()
        old=layout.takeAt(layout.count()-1)
        if old and old.widget():old.widget().deleteLater()
        row=QHBoxLayout();row.addWidget(self.prepare_button);row.addWidget(self.test_button);layout.addLayout(row)
        self.native_approval_button=button('Registrar aprobación de revisión…',self.approve_revision)
        self.inspector.layout().insertWidget(self.inspector.layout().count()-1,self.native_approval_button)
        self.inspector.setMinimumHeight(550)
        return page
    def update_filter_summary(self):
        active=[f'{FILTERS[key]}: {c.currentText()}' for key,c in self.filters.items() if c.currentData()]
        self.active_filter_text.setText('Filtros activos · '+' · '.join(active) if active else '')
        self.active_filter_text.setVisible(bool(active));self.active_filter_text.setToolTip('\n'.join(active))
    def remember_filter_choice(self,*_):
        self._filter_expanded_preference=not self.advanced.isHidden();self.save_filter_preference()
    def save_filter_preference(self,*_):
        expanded=self._filter_expanded_preference if self._filter_expanded_preference is not None else not self.advanced.isHidden()
        self.api.remember_filters(self.remember_filters.isChecked(),expanded)
    def toggle_advanced(self):
        super().toggle_advanced()
        if hasattr(self,'remember_filters') and not getattr(self,'_resizing',False):self._filter_expanded_preference=not self.advanced.isHidden();self.save_filter_preference()
    def resizeEvent(self,event):
        self._resizing=True
        try:super().resizeEvent(event)
        finally:self._resizing=False
    def refresh_facets(self):
        self.loading=True
        for key,combo in self.filters.items():
            selected=combo.currentData();combo.clear();combo.addItem('Todos','')
            for value in self.api.library.facets()[key]:combo.addItem(STATE[value][0] if key=='state' else value,value)
            combo.setCurrentIndex(max(0,combo.findData(selected)));combo.setEnabled(combo.count()>1)
        self.loading=False
    def selected(self):
        try:
            super().selected()
            if self.row:
                version=self.api.version(self.row['version_id'])
                if version['state']=='APPROVED':self.doc_note.setText(f'Aprobación externa: {version["approval_ref"] or "Sin referencia"}\nResponsable: {version["approved_by"] or "Sin dato"}')
                else:self.doc_note.setText('Pendiente de aprobación: solo PDF de prueba.' if version['state']=='PENDING' else 'Retirada: solo consulta.')
        except (ValueError,OSError,RuntimeError) as ex:
            self.preview.scene().clear();self.doc_note.setText('Documento no disponible: '+str(ex))
            self.statusBar().showMessage('Revisar documento: '+str(ex))
        self.recheck_actions()
    def recheck_actions(self):
        if not hasattr(self,'prepare_button'):return
        busy=self.legacy_process is not None
        vid=self.row['version_id'] if self.row else None
        ok,reason=self.api.eligibility(vid) if vid else (False,'Seleccione una revisión.')
        test_ok,test_reason=self.api.eligibility(vid,False) if vid else (False,'Seleccione una revisión.')
        self.prepare_button.setEnabled(ok and not busy);self.prepare_button.setToolTip(reason or 'Abrir emisión en la versión anterior, con esta revisión.')
        self.test_button.setEnabled(test_ok and not busy);self.test_button.setToolTip(test_reason or 'Abrir preparación de prueba en la versión anterior. No registra emisión definitiva.')
        if hasattr(self,'native_approval_button'):
            pending=bool(vid and self.api.version(vid)['state']=='PENDING')
            self.native_approval_button.setEnabled(pending and not busy)
            self.native_approval_button.setToolTip('Registrar una aprobación documental externa existente.' if pending else 'Seleccione una revisión pendiente.')
        if hasattr(self,'save_button'):
            editable=self.current_editor_id is not None and self.api.version(self.current_editor_id)['state']=='PENDING'
            self.save_button.setEnabled(self.dirty and not busy and editable)
            self.save_button.setToolTip('Edición bloqueada mientras está abierta la versión anterior.' if busy else ('Revisión vigente o retirada: solo lectura.' if not editable else ('Guardar los cambios pendientes del borrador.' if self.dirty else 'Sin cambios pendientes de guardar.')))
    def open_legacy(self,target='maestro',mode='production'):
        if self.legacy_process is not None:
            QMessageBox.information(self,'Versión anterior abierta','Continúe en la ventana de la versión anterior y ciérrela antes de abrir otra tarea.');return
        if not self.resolve_work():return
        vid=self.current_editor_id if target=='editor' else (self.row['version_id'] if self.row else None)
        try:
            self.legacy_process=launch_legacy(self.api,target,vid,mode)
            self.set_mutations_enabled(False);self.recheck_actions()
            self.statusBar().showMessage('Versión anterior abierta · Usa los mismos datos · Edición Qt bloqueada hasta cerrarla')
        except (ValueError,OSError) as ex:QMessageBox.warning(self,'No abierto',str(ex))
    def set_mutations_enabled(self,enabled):
        self.library.setEnabled(enabled);self.editor.setEnabled(enabled)
        self.catalog.setEnabled(enabled)
    def poll_legacy(self):
        if self.legacy_process is None or self.legacy_process.poll() is None:return
        code=self.legacy_process.returncode;self.legacy_process=None
        self.set_mutations_enabled(True);self.refresh_facets();self.refresh()
        if self.current_editor_id is not None:
            self.editor_version=dict(self.api.version(self.current_editor_id))
            self.fields=json.loads(self.editor_version['fields_json']);self.layouts[self.current_editor_id]=self.fields
            self.original_fields[self.current_editor_id]=copy.deepcopy(self.fields);self.dirty=False;self.draw_editor()
        self.recheck_actions();self.statusBar().showMessage('Versión anterior cerrada; datos actualizados.' if code==0 else f'La versión anterior terminó con código {code}. Revisar antes de continuar.')
    def build_catalog(self):
        page=super().build_catalog()
        layout=page.layout();layout.insertWidget(2,button('Abrir esta sección en la versión anterior',self.open_catalog_legacy,'primary'))
        return page
    def navigate(self,key):
        super().navigate(key);self.catalog_key=key
        if key not in ('library','editor') and hasattr(self,'catalog_text'):
            self.catalog_text.setText('Esta sección continúa en la versión Tkinter operativa. El botón abre esa aplicación con los mismos datos; no simula una función Qt migrada.')
    def open_catalog_legacy(self):
        target={'emission':'emitir','history':'historial','settings':'admin','import':'maestro','document':'maestro'}.get(self.catalog_key,'maestro')
        self.open_legacy(target)
    def actions_menu(self):
        self.document_menu().exec(self.cursor().pos())

    def document_menu(self):
        menu=QMenu(self)
        menu.setToolTipsVisible(True)
        for title,action in [('Ficha completa',self.document_details),('Abrir PDF maestro',lambda:self.open_document()),
            ('Abrir documento original',lambda:self.open_document(True)),('Editar metadatos con fuente',self.edit_metadata),
            ('Crear nueva revisión documental',self.clone_revision),('Registrar aprobación externa',self.approve_revision),
            ('Revisiones y variantes…',lambda:self.show_access('document'))]:
            item=menu.addAction(title,action)
            pending=bool(self.row and self.api.version(self.row['version_id'])['state']=='PENDING')
            enabled=bool(self.row and not self.legacy_process and (pending or action!=self.approve_revision))
            item.setEnabled(enabled)
            item.setToolTip('Seleccione una revisión pendiente.' if action==self.approve_revision and not pending
                            else ('Cierre primero la compatibilidad Tkinter.' if self.legacy_process else 'Seleccione una revisión.'))
        menu.addSeparator()
        item=menu.addAction('Comparar revisiones…',self.compare_revisions)
        item.setEnabled(bool(self.row and len(self.api.versions(self.row['id']))>1 and not self.legacy_process))
        item.setToolTip('Se necesitan dos revisiones de la misma etiqueta.')
        return menu

    def exchange_menu(self):
        self.build_exchange_menu().exec(self.cursor().pos())

    def build_exchange_menu(self):
        menu=QMenu(self);menu.setToolTipsVisible(True)
        menu.addAction('Importar PDF / Word…',self.import_document)
        menu.addAction('Importar carpeta…',self.import_folder_native)
        menu.addSeparator()
        menu.addAction('Inventariar carpeta sin importar…',self.review_catalog_folder)
        menu.addAction('Conciliar libro máster…',self.reconcile_master)
        menu.addAction('Exportar catálogo completo…',self.export_entire_library)
        for item in menu.actions():
            if not item.isSeparator():
                item.setEnabled(not self.legacy_process)
                item.setToolTip('Cierre primero la compatibilidad Tkinter.' if self.legacy_process else item.text())
        return menu
    def open_document(self,original=False):
        if not self.row:return
        try:
            path=self.api.open_document(self.row['version_id'],original)
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(path))):raise OSError('No se pudo abrir el visor del sistema.')
        except (ValueError,OSError) as ex:QMessageBox.warning(self,'Documento no abierto',str(ex))
    def ask_form(self,title,fields):
        dialog=QDialog(self);dialog.setWindowTitle(title);dialog.resize(570,450);layout=vbox(dialog)
        layout.addWidget(label(title,'panelTitle'));form=QFormLayout();inputs={}
        for key,text,value in fields:
            entry=QLineEdit(str(value or ''));form.addRow(text,entry);inputs[key]=entry
        layout.addLayout(form)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject);layout.addWidget(buttons)
        return {key:entry.text().strip() for key,entry in inputs.items()} if dialog.exec()==QDialog.DialogCode.Accepted else None
    def mutate(self,action):
        if self.legacy_process:return
        try:
            result=action();self.refresh_facets();self.refresh();self.recheck_actions();return result
        except (ValueError,PermissionError,OSError) as ex:QMessageBox.warning(self,'Cambio no realizado',str(ex))
    def edit_metadata(self):
        if not self.row:return
        names={'product':'Producto','family':'Familia','type':'Tipo','country':'País','language':'Idioma'}
        values=self.ask_form('Metadatos documentados',[(k,names[k],self.row.get(k,'')) for k in METADATA_FIELDS]+[('source','Referencia fuente obligatoria','')])
        if values:self.mutate(lambda:self.api.library.update_metadata(self.row['id'],{k:values[k] for k in METADATA_FIELDS},values['source']))
    def clone_revision(self):
        if not self.row or not self.resolve_work():return
        values=self.ask_form('Nueva revisión pendiente',[('version','Código de revisión',''),('notes','Motivo obligatorio','')])
        if not values:return
        def create():
            if not values['version'] or not values['notes']:raise ValueError('Indique código y motivo de revisión.')
            vid=self.api.clone_version(self.row['version_id'],values['version'],values['notes']);self.reset_filters();self.select_version(vid);return vid
        self.mutate(create)
    def approve_revision(self):
        if not self.row or not self.resolve_work() or self.legacy_process:return
        version=self.api.version(self.row['version_id'])
        if version['state']!='PENDING':
            QMessageBox.information(self,'Estado documental',
                'Solo pueden registrarse aprobaciones de revisiones pendientes.');return
        from .revision_approval import RevisionApprovalDialog
        dialog=RevisionApprovalDialog(self,self.api,version)
        if dialog.exec()==QDialog.DialogCode.Accepted:
            self.refresh_facets();self.refresh();self.select_version(version['id'])
            self.recheck_actions()
            self.statusBar().showMessage('Aprobación documental externa registrada. Revise historial y estado.',7000)
    def import_document(self):
        path,_=QFileDialog.getOpenFileName(self,'Importar documento local','','PDF / Word (*.pdf *.docx)')
        if not path:return
        values=self.ask_form('Documento inicial pendiente',[('name','Denominación',''),('code','Código',''),('category','Categoría',''),
            ('origin','Origen (COVEX o CLIENTE)','COVEX'),('customer','Cliente',''),('ref_customer','Referencia cliente',''),('version','Revisión','00'),('annex','Anexo','')])
        if not values:return
        def do_import():
            if not values['name'] or not values['version']:raise ValueError('Denominación y revisión obligatorias.')
            if values['origin'] not in ('COVEX','CLIENTE'):raise ValueError('Origen: COVEX o CLIENTE.')
            vid=self.api.import_label(path,values);self.reset_filters();self.select_version(vid);return vid
        self.mutate(do_import)

    def build_editor(self):
        page=super().build_editor()
        self.editor_advanced_button.setText('Ajuste avanzado')
        self.save_button=button('Guardar campos del borrador',self.save_work,'primary')
        page.layout().insertWidget(page.layout().count()-1,self.save_button)
        self.key_label=label('IDENTIFICADOR','section');self.properties_scroll.widget().layout().insertWidget(3,self.key_label)
        self.key_input=QLineEdit();self.key_input.setPlaceholderText('Identificador del campo')
        self.key_input.textEdited.connect(self.change_key)
        self.properties_scroll.widget().layout().insertWidget(4,self.key_input)
        field_actions=QHBoxLayout();field_actions.addWidget(button('Agregar',self.add_field));field_actions.addWidget(button('Quitar',self.remove_field))
        self.editor_advanced.layout().insertLayout(3,field_actions)
        # Existing full tools stay real in the companion application, not a fake Qt catalog.
        for child in self.editor_advanced.findChildren(QPushButton):
            if child.text() in ('Reajuste y escalado','Recorte y anclaje Word','Seguridad y límites'):
                child.setText({'Reajuste y escalado':'Reajuste y escalado','Recorte y anclaje Word':'Recorte y anclaje','Seguridad y límites':'Seguridad y límites'}[child.text()]);child.setToolTip('Abrir ajuste avanzado completo en la versión anterior.');child.clicked.disconnect();target='centro' if child.text()=='Seguridad y límites' else 'editor';child.clicked.connect(lambda checked=False,t=target:self.open_legacy(t))
        for note in self.editor_advanced.findChildren(QLabel):
            if 'Accesos previstos' in note.text():note.setText('Herramientas en la versión anterior:')
            elif 'Herramientas no migradas' in note.text():note.setText('Abren una ventana de la versión anterior.')
        self.editor_reset_button.setText('Restablecer campos')
        page.layout().itemAt(page.layout().count()-1).widget().setText('Edición de campos · Las herramientas indicadas abren la versión anterior. Sin autoguardado.')
        return page
    def draw_editor(self):
        super().draw_editor()
        self.editor_note.setText('Revisión pendiente · Configuración de campos' if self.editor_version['state']=='PENDING' else 'Revisión vigente o retirada · Solo lectura')
    def toggle_editor_advanced(self):
        super().toggle_editor_advanced()
        self.field_list.setMaximumHeight(165 if self.editor_advanced.isVisible() else 16777215)
        self.editor_advanced.layout().setSpacing(6)
    def open_editor(self):
        if not self.row:return
        vid=self.row['version_id']
        try:self.api.open_document(vid)
        except (ValueError,OSError) as ex:QMessageBox.warning(self,'Documento no disponible',str(ex));return
        if self.current_editor_id!=vid:
            if not self.resolve_work():return
            self.layouts.pop(vid,None);self.original_fields.pop(vid,None)
        super().open_editor();self.original_fields.setdefault(vid,copy.deepcopy(self.fields));self.update_dirty()
    def select_field(self,index):
        super().select_field(index)
        if hasattr(self,'key_input') and 0<=index<len(self.fields):
            self.key_input.setText(self.fields[index]['key']);self.key_input.setEnabled(self.editor_version['state']=='PENDING');self.update_dirty()
    def change_key(self,value):
        index=self.field_list.currentRow()
        if not self.loading and index>=0:self.fields[index]['key']=value;self.update_dirty()
    def change_geometry(self,*args):super().change_geometry(*args);self.update_dirty()
    def moved(self,index):super().moved(index);self.update_dirty()
    def change_name(self,value):super().change_name(value);self.update_dirty()
    def change_flags(self,*args):super().change_flags(*args);self.update_dirty()
    def reset_layout(self):super().reset_layout();self.update_dirty()
    def update_dirty(self):
        if self._initializing or self.current_editor_id is None:return
        self.dirty=self.fields!=self.original_fields.get(self.current_editor_id,self.fields)
        self.recheck_actions()
        if hasattr(self,'edit_status'):self.edit_status.setText('Cambios sin guardar.' if self.dirty else ('Configuración guardada. Sin autoguardado.' if self.editor_version['state']=='PENDING' else 'Revisión vigente o retirada: solo lectura.'))
    def save_work(self):
        if self.current_editor_id is None or self.legacy_process:return False
        try:
            current=self.api.version(self.current_editor_id)
            if current['state']!='PENDING':raise PermissionError('Revisión no pendiente. No se puede guardar.')
            if json.loads(current['fields_json'])!=self.original_fields[self.current_editor_id]:raise ValueError('El borrador cambió fuera de Qt; vuelva a abrirlo antes de guardar.')
            keys=[f.get('key','').strip() for f in self.fields]
            if any(not k for k in keys) or len(set(keys))!=len(keys):raise ValueError('Identificadores obligatorios y únicos.')
            for f in self.fields:
                if f['x']<0 or f['y']<0 or f['w']<=0 or f['h']<=0 or f['x']+f['w']>1.00001 or f['y']+f['h']>1.00001:raise ValueError('Campo fuera de límites.')
            self.api.replace_pending_fields(self.current_editor_id,self.fields)
            self.editor_version=dict(self.api.version(self.current_editor_id));self.original_fields[self.current_editor_id]=copy.deepcopy(self.fields);self.update_dirty();self.refresh();return True
        except (ValueError,PermissionError,OSError) as ex:QMessageBox.warning(self,'No guardado',str(ex));return False
    def resolve_work(self):
        if not self.dirty:return True
        answer=QMessageBox.question(self,'Trabajo sin guardar','Guardar los cambios del borrador antes de cambiar de revisión o abrir la versión anterior?',
            QMessageBox.StandardButton.Save|QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)
        if answer==QMessageBox.StandardButton.Cancel:return False
        if answer==QMessageBox.StandardButton.Save:return self.save_work()
        self.fields=copy.deepcopy(self.original_fields[self.current_editor_id]);self.layouts[self.current_editor_id]=self.fields;self.dirty=False;self.draw_editor();return True
    def add_field(self):
        if self.current_editor_id is None or self.editor_version['state']!='PENDING':return
        key,ok=QInputDialog.getText(self,'Nuevo campo','Identificador único:')
        if not ok or not key.strip():return
        if key.strip() in [f['key'] for f in self.fields]:QMessageBox.warning(self,'Duplicado','El identificador ya existe.');return
        self.fields.append(dict(key=key.strip(),label=key.strip(),x=.1,y=.1,w=.4,h=.08,font_pt=12,bold=False,required=False,locked=False))
        self.draw_editor();self.update_dirty()
    def remove_field(self):
        index=self.field_list.currentRow()
        if self.current_editor_id is None or self.editor_version['state']!='PENDING' or index<0:return
        if QMessageBox.question(self,'Quitar campo','Quitar el campo seleccionado del borrador?')!=QMessageBox.StandardButton.Yes:return
        self.fields.pop(index);self.draw_editor();self.update_dirty()
    def closeEvent(self,event):
        if self.legacy_process:
            QMessageBox.information(self,'Trabajo activo','Cierre la versión anterior antes de cerrar Qt.');event.ignore();return
        if not self.resolve_work():event.ignore();return
        self.save_filter_preference();event.accept()


from .advanced_editor import AdvancedEditorMixin


from .variants import VariantsMixin

from .work import EmissionWorkMixin

from .emission_centre import EmissionCentreMixin
from .history import HistoryMixin
from .settings import SettingsMixin
from .compare import CompareMixin
from .folder_import import FolderImportMixin
from .catalog_exchange_ui import CatalogExchangeMixin
from .print_control import PrintWorkflowMixin

class FunctionalWindow(StatusManagerMixin, CatalogExchangeMixin, PrintWorkflowMixin, FolderImportMixin, CompareMixin, SettingsMixin, HistoryMixin, EmissionCentreMixin, EmissionWorkMixin, VariantsMixin, AdvancedEditorMixin, BaseFunctionalWindow):
    """Retained controllers, with an integrated responsive Qt workspace."""
    def __init__(self, session):
        from PySide6.QtWidgets import QApplication,QFormLayout
        from .responsive import install_translation,accessible_form
        install_translation(QApplication.instance())
        super().__init__(session)
        from .workspace import arrange_editor,arrange_inspector
        arrange_editor(self)
        arrange_inspector(self)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.library_context_menu)
        self.history_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_table.customContextMenuRequested.connect(self.history_context_menu)
        self.canvas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.canvas.customContextMenuRequested.connect(self.editor_context_menu)
        self.setWindowTitle('COVEX Label Manager · '+('Datos ficticios' if self.demo else 'Local'))
        self.search.setAccessibleName('Buscar en Biblioteca')
        self.history_search.setAccessibleName('Buscar en Historial')
        self.name_input.setAccessibleName('Nombre visible del campo')
        self.key_input.setAccessibleName('Identificador del campo')
        self.canvas.setAccessibleName('Lienzo de campos variables sobre el PDF fijo')
        self.font_size.setAccessibleName('Tamaño de texto en puntos')
        for key,control in self.spins.items():
            control.setAccessibleName({'x':'Posición X en mm','y':'Posición Y en mm',
                'w':'Ancho del campo en mm','h':'Alto del campo en mm'}[key])
        for form in self.findChildren(QFormLayout):accessible_form(form)
        self.adapt_header()

    def library_context_menu(self, point):
        index=self.table.indexAt(point)
        if index.isValid():self.table.selectRow(index.row())
        self.document_menu().exec(self.table.viewport().mapToGlobal(point))

    def history_context_menu(self, point):
        index=self.history_table.indexAt(point)
        if index.isValid():self.history_table.selectRow(index.row())
        menu=QMenu(self)
        view=menu.addAction('Verificar y ver PDF',self.preview_native_issue)
        view.setEnabled(self.history_id is not None)
        reprint=menu.addAction('Reimpresión controlada…',self.native_reprint)
        reprint.setEnabled(self.reprint_button.isEnabled())
        printing=menu.addAction('Imprimir PDF registrado…',self.print_historical_pdf)
        printing.setEnabled(self.print_history_button.isEnabled())
        menu.exec(self.history_table.viewport().mapToGlobal(point))

    def editor_context_menu(self, point):
        item=self.canvas.itemAt(point)
        while item is not None and not hasattr(item,'index'):item=item.parentItem()
        if item is not None:
            self.canvas.scene().clearSelection();item.setSelected(True)
        menu=QMenu(self);menu.setToolTipsVisible(True)
        for text,callback,enabled in [
            ('Nuevo campo…',self.add_field,self.editable()),
            ('Dibujar campo…',self.draw_new_field,self.editable()),
            ('Quitar campo…',self.remove_field,self.editable() and bool(self.selected_indices())),
            ('Deshacer diseño',self.undo_edit,self.undo_button.isEnabled()),
            ('Rehacer diseño',self.redo_edit,self.redo_button.isEnabled())]:
            action=menu.addAction(text,callback);action.setEnabled(bool(enabled))
            action.setToolTip(text if enabled else 'Requiere un diseño editable y una selección o cambio aplicable.')
        menu.exec(self.canvas.viewport().mapToGlobal(point))

    def show_access(self, key):
        if key=='document':
            if self.legacy_process or not self.flush_emission_work() or not self.resolve_work():return
            from .revision_browser import RevisionBrowserDialog
            if self.row:RevisionBrowserDialog(self).exec()
            return
        if key=='import':return self.import_document()
        return super().show_access(key)

    def navigate(self, key):
        result = super().navigate(key)
        if hasattr(self, 'work_dock') and hasattr(self,'editor_context'):
            self.work_dock.setVisible(self.stack.currentWidget() is self.editor and self.editor_context.currentIndex()==1)
        return result

    def show_editor_work(self):
        if not hasattr(self, 'editor_context'):
            return super().show_editor_work()
        self.editor_context.show()
        self.editor_context.setCurrentIndex(1)
        self.work_dock.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'editor_context'):
            self.editor_note.hide()
            self.editor_title.setStyleSheet('font-size:20px;')
            self.editor.layout().setContentsMargins(8, 6, 8, 6)
            self.editor.layout().setSpacing(6)
            self.editor_reset_button.setText('Restablecer diseño guardado')
            self.adapt_header()

    def adapt_header(self):
        compact=self.width()<1200
        self.header.setFixedHeight(46 if compact else 56)
        self.header.layout().setContentsMargins(12,5,12,5)
        self.header.layout().setSpacing(4)
        for control in self.nav.values():control.setStyleSheet('padding:7px 6px;')
        for note in self.header.findChildren(QLabel):
            if note.text()=='Diseño y emisión de etiquetas':note.setVisible(not compact)

    def toggle_editor_advanced(self):
        if hasattr(self,'canvas_focus') and self.canvas_focus.isChecked():self.canvas_focus.setChecked(False)
        return super().toggle_editor_advanced()


