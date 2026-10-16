"""Shared Qt work controller: variable data is separate from structural editor."""
import copy
import json
import uuid
import unicodedata
from PySide6.QtCore import Qt,QTimer,QSignalBlocker
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,
    QTabWidget,QTableWidget,QTableWidgetItem,QHeaderView,QScrollArea,QDockWidget,QMessageBox,QInputDialog,QPlainTextEdit,QLabel,QCheckBox,QSizePolicy)
from .window import button,label,vbox
from ..emission_work import WorkConflict

PHASE={'DRAFT':'Borrador','EMITTING':'Intento interrumpido','ISSUED':'Emitido','ERROR':'Revisar archivo'}


class VariableText(QPlainTextEdit):
    """Multiline variable input retaining the existing WorkPanel text contract."""
    def __init__(self,text=''):
        super().__init__(text);self.setFixedHeight(64);self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed);self.setTabChangesFocus(True)
    @property
    def textEdited(self):return self.textChanged
    def text(self):return self.toPlainText()
    def setText(self,text):self.setPlainText(text)


class WorkPanel(QWidget):
    def __init__(self,window):
        super().__init__();self.window=window;self.loading=False;self.inputs={};self.profile_inputs={};self.error_labels={};self.field_widgets={}
        layout=vbox(self,12,8);self.panel_layout=layout;self._compact=False
        top=QHBoxLayout();self.top_actions=top;self.choice=QComboBox();self.choice.setMinimumWidth(170);top.addWidget(self.choice,1)
        top.addWidget(button('Abrir',self.open_selected));layout.addLayout(top)
        actions=QHBoxLayout();self.action_row=actions
        self.shortcut_buttons=[button('Nuevo',window.new_emission_work),button('Copiar',window.copy_emission_work),
                               button('Recargar',window.reload_emission_work)]
        for action in self.shortcut_buttons:actions.addWidget(action)
        layout.addLayout(actions)
        self.note=label('Seleccione o cree un trabajo. Guardar borrador no emite.','subtle');self.note.setWordWrap(True);layout.addWidget(self.note)
        self.identity=label('','subtle');self.identity.setWordWrap(True);layout.addWidget(self.identity)
        self.tabs=QTabWidget();layout.addWidget(self.tabs,1)
        common=QWidget();common.setObjectName('workForm');self.common_form=QFormLayout(common)
        self.common_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.common_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        self.common_form.setVerticalSpacing(10);self.common_form.setContentsMargins(10,12,10,12)
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(common);self.tabs.addTab(scroll,'Datos de lote')
        self.containers=QTableWidget(0,5);self.containers.setHorizontalHeaderLabels(['Nº','Lote','PN kg','PB kg','Conservación'])
        self.containers.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.container_keys=['lote','pn','pb','conservacion']
        self.containers.setAlternatingRowColors(True);self.containers.verticalHeader().hide()
        self.containers.itemChanged.connect(self.changed);self.tabs.addTab(self.containers,'Recipientes')
        self.containers.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        from PySide6.QtGui import QAction
        clear=QAction('Limpiar datos de este recipiente (heredar lote)',self.containers);clear.triggered.connect(self.clear_container_row);self.containers.addAction(clear)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.containers.setToolTip('Un valor vacío hereda el dato común. Pesos PN/PB: puede escribir 0,3558 o 0,3558 kg. También puede pegar datos desde Excel.')
        cfg=QWidget();cfg.setObjectName('workForm');form=QFormLayout(cfg)
        self.design_sheet_button=button('Diseñar hoja…',self.design_sheet,'primary');form.addRow(self.design_sheet_button)
        self.calibrate_button=button('Calibrar impresora…',self.calibrate_printer)
        form.addRow(self.calibrate_button)
        for key,title in [('count','Recipientes'),('copies','Copias por recipiente'),('selection','Números (1-3,5; vacío = todos)')]:
            e=QLineEdit();e.textEdited.connect(self.changed);self.inputs[key]=e;form.addRow(title,self.with_error(e,key))
        for key,title in [('width_mm','Ancho mm'),('height_mm','Alto mm'),('margin_mm','Margen de hoja mm'),('gap_mm','Separación mm'),
            ('offset_x_mm','Desplazamiento X mm'),('offset_y_mm','Desplazamiento Y mm'),('start_slot','Casilla inicial'),('safety_mm','Seguridad mm'),('printer_name','Impresora (referencia)')]:
            e=QLineEdit();e.textEdited.connect(self.changed);self.profile_inputs[key]=e;form.addRow(title,self.with_error(e,key))
        self.keep_ratio=QCheckBox('Conservar proporción del diseño');self.keep_ratio.setChecked(True);form.addRow(self.keep_ratio)
        form.addRow(button('Restaurar tamaño del diseño',self.restore_size))
        for key in ('width_mm','height_mm'):self.profile_inputs[key].textEdited.connect(lambda _,k=key:self.scale_size(k))
        self.orientation=QComboBox();self.orientation.addItem('Vertical','portrait');self.orientation.addItem('Horizontal','landscape');self.orientation.currentTextChanged.connect(self.changed);form.addRow('Orientación',self.orientation)
        self.cut=QComboBox();self.cut.addItem('Sin marcas','0');self.cut.addItem('Con marcas','1');self.cut.currentTextChanged.connect(self.changed);form.addRow('Marcas de corte',self.cut)
        self.profile_choice=QComboBox();self.profile_choice.addItem('Aplicar perfil guardado…',None)
        for p in window.api.profile_list():self.profile_choice.addItem(p['name'],p)
        from ..layout_profiles import LayoutProfiles
        profile_repo=LayoutProfiles(window.api._repository.root)
        for p in profile_repo.list(tolerate_corrupt=True):self.profile_choice.addItem(p['name'],p['profile'])
        self.profile_choice.activated.connect(self.apply_profile);form.addRow('Perfil reutilizable',self.profile_choice)
        if profile_repo.invalid_files:
            self.profile_corruption_warning=label(
                f'Hay {len(profile_repo.invalid_files)} perfil(es) visuales no legibles. No se han alterado. '
                'Consulte con Calidad/IT.', 'fieldError')
            self.profile_corruption_warning.setWordWrap(True)
            form.addRow(self.profile_corruption_warning)
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(cfg);self.tabs.addTab(scroll,'Formato y emisión')
        status=QWidget();status.setObjectName('workForm');f=QFormLayout(status);self.status_kind=QComboBox();
        for title,key in [('Sin etiqueta de estado','ninguna'),('Sin analizar','sin_analizar'),('Aprobado','aprobado'),('Rechazado','rechazado')]:self.status_kind.addItem(title,key)
        self.status_kind.currentTextChanged.connect(self.changed);f.addRow('Etiqueta de estado',self.status_kind)
        self.placement=QComboBox();self.placement.addItem('Integrada','integrada');self.placement.addItem('Independiente','independiente');self.placement.currentTextChanged.connect(self.changed);f.addRow('Ubicación',self.placement)
        self.status_inputs={}
        for key,title in [('fecha','Fecha'),('persona','Responsable'),('caducidad_reanalisis','Caducidad / reanálisis')]:
            e=QLineEdit();e.textEdited.connect(self.changed);self.status_inputs[key]=e;f.addRow(title,self.with_error(e,'status:'+key))
        self.tabs.addTab(status,'Estado')
        row=QHBoxLayout();self.save=button('Guardar borrador',window.flush_emission_work,'primary');row.addWidget(self.save)
        row.addWidget(button('Recuperar',window.recover_emission_work));layout.addLayout(row)
        row=QHBoxLayout();row.addWidget(button('PDF de prueba',window.proof_emission_work));row.addWidget(button('Emitir…',window.issue_emission_work));layout.addLayout(row)
        layout.addWidget(button('Actualizar vínculo documental…',window.refresh_work_binding))
    def set_compact(self,enabled):
        """Move the same work buttons into one line in short windows; no commands disappear."""
        enabled=bool(enabled)
        if self._compact==enabled:return
        self._compact=enabled
        destination=self.top_actions if enabled else self.action_row
        for action in self.shortcut_buttons:destination.addWidget(action)
        self.panel_layout.setContentsMargins(*(6,6,6,6) if enabled else (12,12,12,12))
        self.panel_layout.setSpacing(4 if enabled else 8)
        self.top_actions.setSpacing(4 if enabled else 6)
        self.choice.setMinimumWidth(125 if enabled else 170)
        for action in self.shortcut_buttons:action.setStyleSheet('padding:6px 9px;' if enabled else '')
        self.note.setVisible(not enabled)
        self.identity.setVisible(not enabled)

    def with_error(self,entry,key):
        holder=QWidget();layout=QVBoxLayout(holder);layout.setContentsMargins(0,0,0,0);layout.setSpacing(3);layout.addWidget(entry)
        holder.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
        error=label('');error.setObjectName('fieldError');error.setWordWrap(True);error.hide();layout.addWidget(error)
        self.error_labels[key]=error;self.field_widgets[key]=entry
        return holder
    def show_errors(self,errors):
        from PySide6.QtGui import QColor
        blocker=QSignalBlocker(self.containers)
        for key,error in list(self.error_labels.items()):
            try:error.hide();self.field_widgets[key].setProperty('invalid',False);self.field_widgets[key].style().unpolish(self.field_widgets[key]);self.field_widgets[key].style().polish(self.field_widgets[key])
            except RuntimeError:self.error_labels.pop(key,None);self.field_widgets.pop(key,None)
        for row in range(self.containers.rowCount()):
            for col in range(1,self.containers.columnCount()):
                item=self.containers.item(row,col)
                if item:item.setBackground(QColor('transparent'));item.setToolTip(item.text())
        for error in errors:
            key=error['target'];target=self.error_labels.get(key)
            if target:
                target.setText(error['message']);target.show();entry=self.field_widgets[key];entry.setProperty('invalid',True);entry.style().unpolish(entry);entry.style().polish(entry)
            if key.startswith('container:') and error.get('recipient'):
                field=key.split(':',1)[1]
                if field in self.container_keys:
                    item=self.containers.item(error['recipient']-1,self.container_keys.index(field)+1)
                    if item:item.setBackground(QColor('#FCE9E7'));item.setToolTip(error['message'])
    def tab_changed(self,index):
        if not self.loading and index==1 and self.window.emission_work:
            if self.window.flush_emission_work():self.display(self.window.emission_work)
    def refresh_choices(self):
        current=self.window.emission_work
        self.choice.blockSignals(True);self.choice.clear()
        for w in self.window.api.work.list():self.choice.addItem(w['name']+' · '+PHASE[w['phase']],w['uid'])
        if current:self.choice.setCurrentIndex(self.choice.findData(current['uid']))
        self.choice.blockSignals(False)
    def open_selected(self):
        uid=self.choice.currentData()
        if uid:self.window.load_emission_work(uid)
    def display(self,w):
        self.loading=True
        try:
            self.refresh_choices()
            while self.common_form.rowCount():self.common_form.removeRow(0)
            self.value_inputs={}
            if not w:self.identity.setText('Sin trabajo activo');self.tabs.setEnabled(False);return
            b=w['binding'];v=self.window.api.version(b['revision_id']);variant=self.window.api.variant(b['variant_id']) if b['variant_id'] else None
            self.identity.setText(f"{v['name']} · Revisión {v['version']} · "+('Variante '+variant['code'] if variant else 'Diseño heredado'));self.identity.setToolTip('Trabajo '+w['uid']+' · generación '+str(w['generation']))
            self.note.setText(PHASE[w['phase']]+' · Guardado localmente')
            # Include removed/unknown keys to prevent silent loss on document changes.
            fields=json.loads(v['fields_json'])
            if variant:fields=json.loads(variant['design_json'])['layout']['fields']
            labels={unicodedata.normalize('NFC',f['key']):f.get('label',f['key']) for f in fields if f['key'] not in ('numero','texto_fijo')}
            labels.update({k:labels.get(k,k+' (conservado)') for k in w['values']})
            for key,title in labels.items():
                if key in ('pn','pb'):
                    e=QLineEdit(w['values'].get(key,''))
                    e.setPlaceholderText('Ej.: 0,3558 kg')
                    e.setToolTip('Admite 0,3558 o 0,3558 kg. El valor se conserva como lo escribió; el maestro controla cómo aparece KG en la etiqueta.')
                    if 'kg' not in title.lower():title+=' (kg)'
                else:
                    e=VariableText(w['values'].get(key,''))
                e.textEdited.connect(self.changed);self.value_inputs[key]=e;self.common_form.addRow(title,self.with_error(e,'value:'+key))
            for k,e in self.inputs.items():e.setText(w[k])
            for k,e in self.profile_inputs.items():e.setText(str(w['profile'].get(k,'')))
            self.orientation.setCurrentIndex(max(0,self.orientation.findData(w['profile'].get('orientation','portrait'))));self.cut.setCurrentIndex(max(0,self.cut.findData(str(w['profile'].get('crop_marks',0)))))
            state=w['status'];self.status_kind.setCurrentIndex(max(0,self.status_kind.findData(state.get('kind','ninguna'))));self.placement.setCurrentIndex(max(0,self.placement.findData(state.get('placement','integrada'))))
            for k,e in self.status_inputs.items():e.setText(state.get(k,''))
            try:count=int(w['count'])
            except ValueError:count=0
            count=min(10000,max(0,count));self.containers.setRowCount(count)
            for row in range(count):
                n=QTableWidgetItem(str(row+1));n.setFlags(n.flags() & ~Qt.ItemFlag.ItemIsEditable);self.containers.setItem(row,0,n)
                for col,key in enumerate(('lote','pn','pb','conservacion'),1):self.containers.setItem(row,col,QTableWidgetItem(w['per_container'].get(str(row+1),{}).get(key,'')))
            editable=w['phase']=='DRAFT';self.tabs.setEnabled(editable);self.save.setEnabled(editable)
        finally:self.loading=False
    def capture(self):
        w=self.window.emission_work;per=copy.deepcopy(w['per_container'])
        for row in range(self.containers.rowCount()):
            data=per.get(str(row+1),{}).copy()
            for col,key in enumerate(('lote','pn','pb','conservacion'),1):
                item=self.containers.item(row,col);value=item.text() if item else ''
                if value:data[key]=value
                else:data.pop(key,None)
            if data:per[str(row+1)]=data
            else:per.pop(str(row+1),None)
        status={'kind':self.status_kind.currentData()}
        if status['kind']!='ninguna':status.update(placement=self.placement.currentData(),**{k:e.text() for k,e in self.status_inputs.items()})
        return {'values':{k:e.text() for k,e in self.value_inputs.items()},'per_container':per,
            'profile':{**w['profile'],**{k:e.text() for k,e in self.profile_inputs.items()},'orientation':self.orientation.currentData(),'crop_marks':self.cut.currentData()},
            'status':status,**{k:e.text() for k,e in self.inputs.items()}}
    def restore_size(self):
        if not self.window.emission_work:return
        b=self.window.emission_work['binding'];v=self.window.api.resolved_design(b['revision_id'],b['variant_id'])
        for k,source in [('width_mm','base_w_mm'),('height_mm','base_h_mm')]:self.profile_inputs[k].setText(f"{v[source]:.6f}".rstrip('0').rstrip('.'))
        self.changed()
    def scale_size(self,key):
        if self.loading or not self.keep_ratio.isChecked() or not self.window.emission_work:return
        try:
            b=self.window.emission_work['binding'];v=self.window.api.resolved_design(b['revision_id'],b['variant_id'])
            other='height_mm' if key=='width_mm' else 'width_mm';ratio=v['base_h_mm']/v['base_w_mm']
            value=float(self.profile_inputs[key].text().replace(',','.'))*(ratio if key=='width_mm' else 1/ratio)
            self.profile_inputs[other].setText(f'{value:.6f}'.rstrip('0').rstrip('.'));self.changed()
        except (ValueError,ZeroDivisionError):pass
    def clear_container_row(self):
        row=self.containers.currentRow()
        if row<0:return
        blocker=QSignalBlocker(self.containers)
        for col in range(1,self.containers.columnCount()):self.containers.item(row,col).setText('')
        del blocker;self.changed()
    def changed(self,*_):
        if not self.loading:self.window.work_changed(self)
    def calibrate_printer(self):
        w=self.window
        if not w.emission_work or not w.flush_emission_work():return
        from .printer_calibration_ui import CalibrationDialog
        try:
            draft=copy.deepcopy(w.emission_work)
            dialog=CalibrationDialog(w,w.api,draft['profile'])
            if dialog.exec()==QDialog.DialogCode.Accepted:
                w.emission_work=w.api.work.save(draft['uid'],draft['generation'],
                    {'profile':dialog.profile})
                w.refresh_work_panels()
        except (ValueError,OSError) as ex:
            QMessageBox.warning(w,'Calibración no aplicada',str(ex))

    def design_sheet(self):
        w=self.window
        if not w.emission_work or not w.flush_emission_work():return
        from .sheet_designer import SheetDesigner
        from .pdf_view import PdfPane
        from PySide6.QtWidgets import QDialogButtonBox
        from ..emission_work import parameters
        from PySide6.QtWidgets import QDialog
        import uuid
        work=copy.deepcopy(w.emission_work)
        def proof(profile,parent):
            w.api.work.assert_current(work)
            trial=copy.deepcopy(work);trial['profile']=profile
            p,indices,count,copies=parameters(trial);b=trial['binding']
            path=w.api.output_path('cache','sheet-proof-'+uuid.uuid4().hex+'.pdf')
            w.api.render(w.api.version(b['revision_id']),trial['values'],p,indices,count,copies,path,True,per_container=trial['per_container'],status=trial['status'],variant_id=b['variant_id'])
            dialog=QDialog(parent);dialog.setWindowTitle('PDF de prueba · sin emisión');dialog.resize(min(900,parent.width()),max(350,parent.height()-30));lay=vbox(dialog,10);pane=PdfPane(w.api);lay.addWidget(pane);pane.load(path,'PDF de prueba real');close=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);close.rejected.connect(dialog.reject);lay.addWidget(close);dialog.exec()
        try:
            b=work['binding'];version=w.api.resolved_design(b['revision_id'],b['variant_id'])
            thumbnail=w.api.thumbnail(version,width_px=450)
            dialog=SheetDesigner(w,work['profile'],proof,w.api._repository.root,f"Recipientes: {work['count']} · Copias por recipiente: {work['copies']}",thumbnail=thumbnail,nominal=(version['base_w_mm'],version['base_h_mm']))
            if dialog.exec()==QDialog.DialogCode.Accepted:
                w.emission_work=w.api.work.save(work['uid'],work['generation'],{'profile':dialog.profile});w.refresh_work_panels()
        except (ValueError,OSError) as ex:QMessageBox.warning(w,'Hoja no aplicada',str(ex))

    def apply_profile(self,*_):
        p=self.profile_choice.currentData()
        if not p:return
        if self.window.emission_work and self.window.flush_emission_work():
            w=self.window.emission_work
            self.window.emission_work=self.window.api.work.save(w['uid'],w['generation'],{'profile':dict(p)})
            self.window.refresh_work_panels();return
        for k,e in self.profile_inputs.items():e.setText(str(p.get(k,'')))
        self.orientation.setCurrentIndex(self.orientation.findData(p['orientation']));self.cut.setCurrentIndex(self.cut.findData(str(p['crop_marks'])));self.changed()


class EmissionWorkMixin:
    def __init__(self,session):
        self.emission_work=None;self.work_dirty_panel=None;self.work_panels=[];self._work_ready=False
        super().__init__(session)
        self.work_timer=QTimer(self);self.work_timer.setSingleShot(True);self.work_timer.timeout.connect(self.flush_emission_work)
        self.emission_page=self.build_emission_page();self.stack.addWidget(self.emission_page)
        self.work_dock=QDockWidget('Datos variables del trabajo',self);self.work_dock.setObjectName('emissionWork')
        self.editor_work_panel=WorkPanel(self);self.work_panels.append(self.editor_work_panel);self.work_dock.setWidget(self.editor_work_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.work_dock);self.work_dock.hide()
        # Add a compact explicit entry, without changing structural tool panels.
        self.editor.layout().itemAt(0).layout().addWidget(button('Datos del trabajo',self.show_editor_work))
        self.editor.layout().itemAt(self.editor.layout().count()-1).widget().setText('Fuente fija protegida · Diseño: guardado explícito · Datos del trabajo: autoguardado local')
        self.work_dock.setMinimumWidth(460)
        self._work_ready=True;self.refresh_work_panels()
        self.setWindowTitle('COVEX Label Manager · R3B2+B3 · Variantes y trabajos')
        if self.api.work.list():self.statusBar().showMessage('Hay trabajos locales recuperables. Ábralos en Emisión.')
    def build_emission_page(self):
        page=QWidget();layout=vbox(page,20,8)
        layout.addWidget(label('Trabajos de emisión','title'))
        self.emission_panel=WorkPanel(self);self.work_panels.append(self.emission_panel);layout.addWidget(self.emission_panel,1)
        return page
    def refresh_work_panels(self):
        for p in self.work_panels:p.display(self.emission_work)
    def show_editor_work(self):
        self.work_dock.show();self.work_dock.raise_()
    def navigate(self,key):
        if getattr(self,'_work_ready',False):
            if not self.flush_emission_work():return
            if key=='emission':
                self.stack.setCurrentWidget(self.emission_page)
                for name,b in self.nav.items():b.setChecked(name==key)
                self.work_dock.hide();return
            if key!='editor':self.work_dock.hide()
        super().navigate(key)
    def work_changed(self,panel):
        if self.emission_work is None:return
        if self.work_dirty_panel and self.work_dirty_panel is not panel and not self.flush_emission_work():return
        self.work_dirty_panel=panel;panel.note.setText('Cambios por guardar…');self.work_timer.start(400)
    def flush_emission_work(self):
        if not self.work_dirty_panel:return True
        self.work_timer.stop();panel=self.work_dirty_panel
        try:
            w=self.emission_work;changes=panel.capture()
            self.emission_work=self.api.work.save(w['uid'],w['generation'],changes)
            self.work_dirty_panel=None
            for other in self.work_panels:
                if other is not panel:other.display(self.emission_work)
            self.statusBar().showMessage('Borrador guardado localmente.',3000)
            panel.note.setText('Borrador guardado localmente · generación '+str(self.emission_work['generation']))
            panel.identity.setToolTip('Trabajo '+self.emission_work['uid']+' · generación '+str(self.emission_work['generation']))
            # Count changes resize the table on explicit reload/tab switch, keeping
            # typing focus stable during ordinary autosaves.
            return True
        except (ValueError,OSError,PermissionError) as ex:
            panel.note.setText('NO GUARDADO · '+str(ex));self.statusBar().showMessage('No guardado: '+str(ex));return False
    def work_action(self,action):
        try:return action()
        except (ValueError,OSError,PermissionError) as ex:QMessageBox.warning(self,'Trabajo conservado',str(ex));return None
    def selected_work_design(self):
        if self.stack.currentWidget()==self.editor and self.current_editor_id:return self.current_editor_id,self.current_variant_id
        if getattr(self,'emission_page',None) is self.stack.currentWidget() and self.emission_work:
            b=self.emission_work['binding'];return b['revision_id'],b['variant_id']
        if self.row:return self.row['version_id'],self.library_variant_id
        raise ValueError('Seleccione una revisión en Biblioteca.')
    def new_emission_work(self):
        if not self.flush_emission_work():return
        def create():
            vid,variant=self.selected_work_design()
            name,ok=QInputDialog.getText(self,'Nuevo trabajo','Denominación del trabajo o lote:')
            if ok and name.strip():
                self.emission_work=self.api.work.create(vid,variant,name);self.refresh_work_panels()
        self.work_action(create)
    def copy_emission_work(self):
        if not self.emission_work or not self.flush_emission_work():return
        def create():
            w=self.emission_work;b=w['binding'];self.emission_work=self.api.work.create(b['revision_id'],b['variant_id'],w['name']+' · copia',w);self.refresh_work_panels()
        self.work_action(create)
    def load_emission_work(self,uid):
        if not self.flush_emission_work():return False
        def load():self.emission_work=self.api.work.get(uid);self.refresh_work_panels();self.statusBar().showMessage('Trabajo abierto · Datos guardados localmente.',5000);return True
        return self.work_action(load)
    def reload_emission_work(self):
        if not self.emission_work:return
        if self.work_dirty_panel:
            if QMessageBox.question(self,'Recargar trabajo','Descartar expresamente los valores de pantalla y cargar la versión guardada?',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Yes:return
            self.work_timer.stop();self.work_dirty_panel=None
        self.load_emission_work(self.emission_work['uid'])
    def refresh_work_binding(self):
        if not self.emission_work or not self.flush_emission_work():return
        if QMessageBox.question(self,'Actualizar vínculo','Conservar datos variables y vincular este trabajo a la documentación actual? Revise los campos antes de emitir.',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Yes:return
        def refresh():
            w=self.emission_work;self.emission_work=self.api.work.refresh_binding(w['uid'],w['generation']);self.refresh_work_panels()
        self.work_action(refresh)
    def recover_emission_work(self):
        panel=self.work_dirty_panel or (self.editor_work_panel if self.work_dock.isVisible() else self.emission_panel)
        uid=self.emission_work['uid'] if self.emission_work else panel.choice.currentData()
        if not uid:return
        if self.work_dirty_panel and not self.flush_emission_work():return
        if QMessageBox.question(self,'Recuperar trabajo','Reconciliar un intento interrumpido o recuperar la copia anterior del archivo corrupto? Los archivos de diagnóstico se conservan.',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Yes:return
        def recover():
            from ..emission_work import WorkCorrupt
            try:
                w=self.api.work.get(uid)
                self.emission_work=self.api.work.recover_attempt(uid,w['generation']) if w['phase']=='EMITTING' else w
            except WorkCorrupt:self.emission_work=self.api.work.recover_previous(uid)
            self.refresh_work_panels()
        self.work_action(recover)
    def proof_emission_work(self):
        if not self.emission_work or not self.flush_emission_work():return
        def proof():
            w=self.emission_work;out=self.api.output_path('cache','work-proof-'+uuid.uuid4().hex+'.pdf')
            self.api.work.proof(w['uid'],w['generation'],out);self.statusBar().showMessage('PDF de prueba: '+str(out))
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(out)))
        self.work_action(proof)
    def issue_emission_work(self):
        if not self.emission_work or not self.flush_emission_work() or self.legacy_process:return
        def launch():
            from ..qt_legacy import launch_legacy
            w=self.emission_work;self.api.work.assert_current(w,True)
            if w['phase']!='DRAFT':raise PermissionError('Copie o recupere el trabajo antes de emitir.')
            b=w['binding'];self.api.selected_variant_id=b['variant_id']
            self.legacy_process=launch_legacy(self.api,'emitir',b['revision_id'],'production',work_uid=w['uid'],work_generation=w['generation'])
            self.set_mutations_enabled(False)
        self.work_action(launch)
    def set_mutations_enabled(self,enabled):
        super().set_mutations_enabled(enabled)
        if getattr(self,'_work_ready',False):self.emission_page.setEnabled(enabled);self.work_dock.setEnabled(enabled)
    def open_legacy(self,target='maestro',mode='production'):
        if not self.flush_emission_work():return
        if target=='emitir':
            if self.legacy_process:return
            self.new_emission_work()
            if self.emission_work:self.navigate('emission')
            return
        super().open_legacy(target,mode)
    def poll_legacy(self):
        was=self.legacy_process is not None
        super().poll_legacy()
        if was and self.legacy_process is None and self.emission_work:self.load_emission_work(self.emission_work['uid'])
    def closeEvent(self,event):
        if not self.flush_emission_work():
            QMessageBox.warning(self,'No guardado','El trabajo sigue en pantalla. Reintente guardar o recargue expresamente antes de cerrar.');event.ignore();return
        super().closeEvent(event)
        if event.isAccepted():
            for timer in (self.work_timer,self.legacy_timer,self.poll_timer):timer.stop()
