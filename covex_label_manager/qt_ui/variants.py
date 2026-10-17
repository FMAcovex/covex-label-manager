"""Controlled variant selector/lifecycle on the retained R3B1 library and editor."""
import copy
import json
from PySide6.QtWidgets import QComboBox,QHBoxLayout,QMenu,QMessageBox,QFileDialog,QDialog,QPlainTextEdit,QDialogButtonBox
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from .window import button,label,vbox
from .responsive import AdaptiveDialog as QDialog
from ..editor_layout import LayoutHistory,layout_from_version,source_identity
from ..variants import design_from_revision,update_design_layout
from ..canonical import digest

STATES={'DRAFT':'Borrador','PENDING':'Pendiente','APPROVED':'Aprobada','RETIRED':'Retirada'}


class VariantsMixin:
    def __init__(self,session):
        self.library_variant_id=None;self.current_variant_id=None;self.variant_generation=None;self._variants_refreshing=False
        super().__init__(session)
        self.setWindowTitle('COVEX Label Manager · R3B2 · Variantes controladas')
    def build_library(self):
        page=super().build_library();layout=self.inspector.layout()
        self.preview.setMinimumHeight(120);self.preview.setMaximumHeight(190)
        row=QHBoxLayout();self.variant_selector=QComboBox();self.variant_selector.setMinimumWidth(140)
        self.variant_selector.currentIndexChanged.connect(self.choose_library_variant);row.addWidget(self.variant_selector,1)
        self.variant_menu_button=button('Variantes ▾',self.variant_menu);row.addWidget(self.variant_menu_button)
        layout.insertLayout(3,row)
        self.variant_note=label('Diseño heredado de la revisión','subtle');self.variant_note.setWordWrap(True)
        self.variant_note.hide()
        return page
    def build_editor(self):
        page=super().build_editor();row=QHBoxLayout();row.addWidget(label('Variante:','section'))
        self.editor_variant_selector=QComboBox();row.addWidget(self.editor_variant_selector,1)
        self.editor_variant_selector.currentIndexChanged.connect(self.choose_editor_variant)
        row.addWidget(button('Gestionar variantes',self.variant_menu));page.layout().insertLayout(2,row)
        return page
    def fill_variants(self,combo,revision_id,selected):
        combo.blockSignals(True);combo.clear();combo.addItem('Diseño heredado de la revisión',None)
        for row in self.api.variants(revision_id):
            size=json.loads(row['design_json'])['nominal_size_mm']
            combo.addItem(f"{row['code']} · {row['name']} · {size['width']:.1f} × {size['height']:.1f} mm · {STATES[row['state']]}",row['id'])
        index=combo.findData(selected);combo.setCurrentIndex(max(0,index));combo.blockSignals(False)
        return combo.currentData()
    def selected(self):
        previous=self.row['version_id'] if getattr(self,'row',None) else None
        super().selected()
        if not hasattr(self,'variant_selector') or not self.row:return
        vid=self.row['version_id']
        if getattr(self,'_variant_revision',None)!=vid:self.library_variant_id=None
        self._variant_revision=vid
        self.library_variant_id=self.fill_variants(self.variant_selector,vid,self.library_variant_id)
        self.update_variant_note();self.recheck_actions()
    def choose_library_variant(self,*_):
        self.library_variant_id=self.variant_selector.currentData();self.update_variant_note();self.recheck_actions()
    def update_variant_note(self):
        if self.library_variant_id is None:self.variant_note.setText('Diseño heredado · La aprobación documental pertenece a la revisión.');return
        row=self.api.variant(self.library_variant_id)
        self.variant_selector.setToolTip(STATES[row['state']]+' · '+row['reason'])
        self.variant_note.setText(STATES[row['state']]+' · '+row['reason']+ ('\nAprobación externa: '+row['approval_ref'] if row['approval_ref'] else '\nSin aprobación de variante registrada.'))
    def editor_record(self,version_id=None):
        vid=version_id if version_id is not None else self.current_editor_id
        # Consultation of retired variants must work even when rendering is blocked.
        if self.current_variant_id is None:return self.api.version(vid)
        from ..editor_layout import version_with_layout
        row=self.api.variant(self.current_variant_id)
        if row['revision_id']!=vid:raise ValueError('Variante de otra revisión.')
        design=json.loads(row['design_json']);record=version_with_layout(self.api.version(vid),design['layout']);record['_variant_id']=row['id']
        record['base_w_mm']=design['nominal_size_mm']['width'];record['base_h_mm']=design['nominal_size_mm']['height']
        return record
    def editable(self):
        if self.current_variant_id is None:return super().editable()
        if self.design is None or self.legacy_process:return False
        row=self.api.variant(self.current_variant_id)
        revision=self.api.version(row['revision_id'])
        return row['state']=='DRAFT' and revision['state']!='RETIRED'
    def open_editor(self):
        if not self.row:return
        changed=(self.row['version_id'],self.library_variant_id)!=(self.current_editor_id,self.current_variant_id)
        if changed:
            if not self.resolve_work():return
            self.current_variant_id=self.library_variant_id;self.current_editor_id=None
            if self.current_variant_id is not None:self.variant_generation=self.api.variant(self.current_variant_id)['generation']
        super().open_editor()
        if self.current_editor_id:self.fill_variants(self.editor_variant_selector,self.current_editor_id,self.current_variant_id)
    def choose_editor_variant(self,*_):
        selected=self.editor_variant_selector.currentData()
        if selected==self.current_variant_id:return
        if not self.resolve_work():self.fill_variants(self.editor_variant_selector,self.current_editor_id,self.current_variant_id);return
        self.select_version(self.current_editor_id);self.library_variant_id=selected
        self.variant_selector.setCurrentIndex(self.variant_selector.findData(selected));self.open_editor()
    def sync_design(self):
        super().sync_design()
        if self.current_variant_id is not None:
            row=self.api.variant(self.current_variant_id)
            design=update_design_layout(json.loads(row['design_json']),self.design.state)
            self.editor_version['base_w_mm']=design['nominal_size_mm']['width']
            self.editor_version['base_h_mm']=design['nominal_size_mm']['height']

    def draw_editor(self,fit=False):
        super().draw_editor(fit)
        if self.current_variant_id is not None and self.design:
            row=self.api.variant(self.current_variant_id)
            self.editor_title.setText(self.editor_version['name']+' / '+self.editor_version['version']+' / '+row['code'])
            self.save_button.setText('Guardar variante')
            self.editor_note.setText('Revisión: '+{'APPROVED':'Vigente','PENDING':'Pendiente','RETIRED':'Retirada'}.get(self.editor_version['state'],self.editor_version['state'])+' · Variante: '+STATES[row['state']]+' · Original protegido')
    def save_work(self):
        if self.current_variant_id is None:return super().save_work()
        if not self.editable():return False
        try:
            row=self.api.variant(self.current_variant_id);design=update_design_layout(json.loads(row['design_json']),copy.deepcopy(self.design.state))
            self.api.save_variant(row['id'],self.variant_generation,design,self.api.setting('operator'))
            self.variant_generation=self.api.variant(row['id'])['generation'];self.expected_layout=copy.deepcopy(self.design.state);self.design.mark_clean()
            self.editor_version=self.editor_record();self.refresh();self.draw_editor();return True
        except (ValueError,PermissionError,OSError) as ex:QMessageBox.warning(self,'Variante no guardada',str(ex));return False
    def recheck_actions(self):
        super().recheck_actions()
        if not hasattr(self,'variant_selector') or not self.row:return
        vid=self.row['version_id'];busy=self.legacy_process is not None
        for widget,production in [(self.prepare_button,True),(self.test_button,False)]:
            ok,reason=self.api.eligibility(vid,production,self.library_variant_id);widget.setEnabled(ok and not busy);widget.setToolTip(reason)
        if self.current_variant_id is not None and hasattr(self,'save_button'):self.save_button.setEnabled(bool(self.design and self.design.dirty) and self.editable())
    def open_legacy(self,target='maestro',mode='production'):
        self.api.selected_variant_id=self.current_variant_id if target=='editor' else self.library_variant_id
        super().open_legacy(target,mode)
    def poll_legacy(self):
        was_open=self.legacy_process is not None
        super().poll_legacy()
        if was_open and self.legacy_process is None and self.current_variant_id is not None:
            self.variant_generation=self.api.variant(self.current_variant_id)['generation']
    def variant_menu(self):
        if self.stack.currentWidget()==self.editor and self.current_editor_id is not None:
            self.select_version(self.current_editor_id);self.library_variant_id=self.current_variant_id
            self.variant_selector.setCurrentIndex(self.variant_selector.findData(self.current_variant_id))
        if not self.row:return
        self.build_variant_menu().exec(self.cursor().pos())

    def build_variant_menu(self):
        """Presentation mirrors the lifecycle; repositories still revalidate it."""
        menu=QMenu(self);menu.setToolTipsVisible(True)
        revision=self.api.version(self.row['version_id']) if self.row else None
        variant=self.api.variant(self.library_variant_id) if self.library_variant_id is not None else None
        state=variant['state'] if variant else None
        base_state={'APPROVED':'Vigente','PENDING':'Pendiente','RETIRED':'Retirada'}
        header=menu.addAction('Revisión documental · '+(base_state[revision['state']] if revision else 'Sin selección'));header.setEnabled(False)
        context=menu.addAction('Original y aprobación documental: menú Documento');context.setEnabled(False)
        menu.addSeparator()
        header=menu.addAction('Variante de diseño · '+(STATES[state] if state else 'Diseño heredado, sin variante'));header.setEnabled(False)
        explanation=menu.addAction('La variante no sustituye la revisión documental');explanation.setEnabled(False)
        available=bool(revision and revision['state']!='RETIRED' and not self.legacy_process)
        commands=[
            ('Crear variante desde esta revisión',self.create_variant_ui,available,'Seleccione una revisión no retirada.'),
            ('Derivar variante seleccionada',lambda:self.create_variant_ui(True),available and variant is not None,'Seleccione una variante de una revisión no retirada.'),
            ('Tamaño nominal reutilizable',self.edit_nominal_size,available and state=='DRAFT','Solo se edita una variante en borrador.'),
            ('Enviar a revisión',lambda:self.variant_transition('PENDING'),available and state=='DRAFT','Solo desde borrador.'),
            ('Devolver a borrador',lambda:self.variant_transition('DRAFT'),available and state=='PENDING','Solo desde pendiente de revisión.'),
            ('Registrar aprobación externa',self.approve_variant_ui,available and state=='PENDING' and revision['state']=='APPROVED','Variante pendiente y revisión documental vigente obligatorias.'),
            ('Retirar / cancelar variante',lambda:self.variant_transition('RETIRED'),state in ('DRAFT','PENDING','APPROVED') and not self.legacy_process,'Seleccione una variante no retirada; se exige motivo.'),
            ('Comparar revisión y variante',self.compare_variant,variant is not None,'Seleccione una variante.'),
            ('Consultar evidencia',self.open_variant_evidence,bool(variant and variant['evidence_path']),'La variante no tiene evidencia de aprobación registrada.'),
        ]
        unavailable=[]
        for text,callback,enabled,reason in commands:
            if not enabled:
                unavailable.append((text,reason));continue
            action=menu.addAction(text,callback)
            action.setToolTip(text if enabled else ('Cierre primero la compatibilidad Tkinter.' if self.legacy_process else reason))
            action.setStatusTip(action.toolTip())
        if unavailable:
            blocked=menu.addMenu('Otras acciones · requisitos');blocked.setToolTipsVisible(True)
            for text,reason in unavailable:
                action=blocked.addAction(text);action.setEnabled(False)
                reason='Cierre primero la compatibilidad Tkinter.' if self.legacy_process else reason
                action.setToolTip(reason);action.setStatusTip(reason)
                explanation=blocked.addAction('↳ '+reason);explanation.setEnabled(False)
        return menu
    def create_variant_ui(self,derive=False,field_adjustment=False):
        if not self.row or not self.resolve_work():return
        if field_adjustment:
            version=self.api.version(self.row['version_id'])
            if version['state']!='APPROVED':
                QMessageBox.warning(self,'Ajuste no disponible','Seleccione una revisión vigente.');return
            existing={v['code'].upper() for v in self.api.variants(self.row['version_id'])}
            number=next((i for i in range(1,10000) if f'CAMPOS-{i:03d}' not in existing),None)
            if number is None:
                QMessageBox.warning(self,'Ajuste no disponible','No queda ningún identificador de ajuste libre.');return
            defaults=[('code','Código de variante (propuesto)',f'CAMPOS-{number:03d}'),
                      ('name','Denominación (propuesta)',f'Ajuste de campos variables {number:03d}'),
                      ('reason','Motivo del ajuste (obligatorio)','')]
            title='Ajustar campos · crear variante en borrador'
        else:
            defaults=[('code','Identificación única',''),
                      ('name','Denominación',''),('reason','Motivo','')]
            title='Nueva variante de diseño'
        fields=self.ask_form(title,defaults)
        if fields is None:return
        # Report each missing input before reaching the repository. An empty
        # reason is never generated by the software: the operator supplies it.
        for key,description in [('code','Código'),('name','Denominación'),('reason','Motivo')]:
            if not fields.get(key,'').strip():
                QMessageBox.warning(self,'Datos obligatorios',description+' obligatorio. La variante no se ha creado.');return
        try:
            row=self.api.create_variant(self.row['version_id'],fields['code'],fields['name'],fields['reason'],self.api.setting('operator'),self.library_variant_id if derive else None)
            self.library_variant_id=row['id'];self.selected();self.open_editor()
            if field_adjustment:self.statusBar().showMessage('Variante de campos '+row['code']+' creada en BORRADOR: aprobación documental pendiente.',9000)
        except (ValueError,PermissionError,OSError) as ex:QMessageBox.warning(self,'Variante no creada',str(ex))
    def edit_nominal_size(self):
        if self.library_variant_id is None or not self.resolve_work():return
        row=self.api.variant(self.library_variant_id);design=json.loads(row['design_json']);size=design['nominal_size_mm']
        fields=self.ask_form('Formato nominal de la variante',[('width','Ancho nominal (mm)',size['width']),('height','Alto nominal (mm)',size['height'])])
        if not fields:return
        try:
            design['nominal_size_mm']={k:float(fields[k].replace(',','.')) for k in ('width','height')}
            self.api.save_variant(row['id'],row['generation'],design,self.api.setting('operator'));self.reload_variant()
        except (ValueError,PermissionError,OSError) as ex:QMessageBox.warning(self,'Formato no guardado',str(ex))

    def variant_transition(self,target):
        if self.library_variant_id is None or not self.resolve_work():return
        row=self.api.variant(self.library_variant_id);reason=''
        if target in ('DRAFT','RETIRED'):
            fields=self.ask_form('Motivo obligatorio',[('reason','Motivo','')])
            if not fields:return
            reason=fields['reason']
        if QMessageBox.question(self,'Confirmar estado',f"{row['code']} → {STATES[target]}?")!=QMessageBox.StandardButton.Yes:return
        self.mutate(lambda:self.api.transition_variant(row['id'],row['generation'],target,self.api.setting('operator'),reason))
        self.reload_variant()
    def approve_variant_ui(self):
        if self.library_variant_id is None or not self.resolve_work():return
        row=self.api.variant(self.library_variant_id)
        fields=self.ask_form('Registrar aprobación documental externa',[('reviewer','Responsable externo',''),('reference','Referencia documental',''),('date','Fecha documental AAAA-MM-DD','')])
        if not fields:return
        path,_=QFileDialog.getOpenFileName(self,'Seleccionar evidencia externa','','Evidencia (*.pdf *.txt *.docx *.zip);;Todos (*)')
        if not path:return
        if QMessageBox.question(self,'Confirmar registro',f"Registrar aprobación externa de {row['code']} y del diseño {row['design_sha256'][:12]}?\nNo equivale a firma electrónica.")!=QMessageBox.StandardButton.Yes:return
        self.mutate(lambda:self.api.approve_variant(row['id'],row['generation'],fields['reviewer'],fields['reference'],fields['date'],path,self.api.setting('operator')))
        self.reload_variant()
    def reload_variant(self):
        self.selected()
        if self.current_variant_id is not None:
            self.variant_generation=self.api.variant(self.current_variant_id)['generation'];self.editor_version=self.editor_record()
            self.design=LayoutHistory(layout_from_version(self.editor_version));self.draw_editor()
    def compare_variant(self):
        if self.library_variant_id is None:return
        row=self.api.variant(self.library_variant_id);revision=dict(self.api.version(row['revision_id']))
        dialog=QDialog(self);dialog.setWindowTitle('Comparación documental · Revisión / Variante');dialog.resize(1000,650);layout=vbox(dialog);columns=QHBoxLayout()
        from PySide6.QtWidgets import QTableWidget,QTableWidgetItem,QHeaderView
        from PySide6.QtGui import QColor
        table=QTableWidget(0,3);table.setHorizontalHeaderLabels(['Dato','Revisión documental','Variante de diseño'])
        design=json.loads(row['design_json']);base=design_from_revision(revision)
        items=[('Identificación',revision['version'],row['code']),('Denominación',revision['name'],row['name']),
            ('Estado',{'APPROVED':'Vigente','PENDING':'Pendiente','RETIRED':'Retirada'}[revision['state']],STATES[row['state']]),('UID',revision['uid'],row['uid']),('Motivo',revision['notes'],row['reason']),
            ('Original',revision['original_file'],revision['original_file']),('Hash original',revision['source_sha256'],revision['source_sha256']),
            ('PDF maestro',revision['master_pdf'],revision['master_pdf']),('Hash PDF',revision['pdf_sha256'],revision['pdf_sha256']),
            ('Responsable aprobación',revision['approved_by'],row['approved_by']),('Referencia aprobación',revision['approval_ref'],row['approval_ref']),
            ('Fecha aprobación',revision['approved_at'],row['approval_date']),('Evidencia',None,row['evidence_path']),('Hash evidencia',None,row['evidence_sha256']),
            ('Campos variables',str(len(base['layout']['fields'])),str(len(design['layout']['fields']))),
            ('Recorte',str(base['layout']['crop']),str(design['layout']['crop'])),('Zona de estado',str(base['layout']['area']),str(design['layout']['area'])),
            ('Formato nominal (mm)',f"{base['nominal_size_mm']['width']:.2f} × {base['nominal_size_mm']['height']:.2f}",f"{design['nominal_size_mm']['width']:.2f} × {design['nominal_size_mm']['height']:.2f}"),
            ('Diseño',digest(base),row['design_sha256']),('Retirada',None,row['retirement_reason'])]
        base_fields={f['key']:f for f in base['layout']['fields']};variant_fields={f['key']:f for f in design['layout']['fields']}
        def describe(field,size):
            if field is None:return 'No incluido'
            return (f"{field['label']} · X {field['x']*size['width']:.2f}, Y {field['y']*size['height']:.2f}, "
                f"ancho {field['w']*size['width']:.2f}, alto {field['h']*size['height']:.2f} mm · {field['font_pt']} pt"
                + (' · Negrita' if field.get('bold') else '')+(' · Obligatorio' if field.get('required') else '')+(' · Bloqueado' if field.get('locked') else ''))
        for key in sorted(set(base_fields)|set(variant_fields)):
            a=base_fields.get(key);b=variant_fields.get(key)
            if digest(a)!=digest(b):items.append(('Campo '+key,describe(a,base['nominal_size_mm']),describe(b,design['nominal_size_mm'])))
        for title,a,b in items:
            index=table.rowCount();table.insertRow(index)
            for column,value in enumerate((title,a,b)):
                cell=QTableWidgetItem(str(value) if value is not None else 'Sin registro');cell.setToolTip(cell.text());table.setItem(index,column,cell)
                if column and a!=b:cell.setBackground(QColor('#FFF0D5'))
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers);table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.resizeRowsToContents();columns.addWidget(table)
        layout.addLayout(columns);buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);buttons.rejected.connect(dialog.reject);layout.addWidget(buttons);dialog.exec()
    def open_variant_evidence(self):
        if self.library_variant_id is None:return
        try:QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.api.variant_evidence(self.library_variant_id))))
        except (ValueError,OSError) as ex:QMessageBox.warning(self,'Evidencia no disponible',str(ex))
