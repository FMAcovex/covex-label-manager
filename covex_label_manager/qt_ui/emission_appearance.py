"""Isolated trial editing. Applying changes saves a recoverable PROOF work only."""
from copy import deepcopy
import json
import uuid
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget,QFormLayout,QComboBox,QDoubleSpinBox,QCheckBox,QLineEdit,QScrollArea,QSplitter,QDialogButtonBox,QMessageBox,QInputDialog
from .responsive import AdaptiveDialog
from .window import vbox,label,button
from .pdf_view import PdfPane
from .text_appearance import TextAppearance
from ..typography import apply_trial
from ..emission_work import parameters


class EmissionAppearanceDialog(AdaptiveDialog):
    def __init__(self,window):
        super().__init__(window);self.controller=window;self.api=window.api
        self.work=deepcopy(window.emission_work);self.loading=False;self.input_valid=True
        b=self.work['binding'];self.version=self.api.resolved_design(b['revision_id'],b['variant_id'])
        self.fields={f['key']:f for f in json.loads(self.version['fields_json']) if f['key'] not in ('texto_fijo','numero')}
        self.trial=deepcopy(self.work['profile'].get('trial_appearance',dict(contract=1,fields={})))
        self.setWindowTitle('Ajustar apariencia del campo · PRUEBA / NO GMP');self.resize(1050,740)
        root=vbox(self);note=label('Los valores de lote no cambian. Estos ajustes NO modifican la revisión aprobada y bloquean la emisión definitiva. Restablézcalos o prepare una variante para revisión y aprobación externa.','subtle');note.setWordWrap(True);root.addWidget(note)
        split=QSplitter();panel=QWidget();form=QFormLayout(panel);form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        self.field=QComboBox()
        for key,f in self.fields.items():self.field.addItem(f['label']+' · '+key,key)
        form.addRow('Campo variable',self.field)
        self.value=QLineEdit();self.value.setReadOnly(True);form.addRow('Valor (sin modificar)',self.value)
        self.font_size=QDoubleSpinBox();self.font_size.setRange(3,80);self.font_size.setSuffix(' pt');self.font_size.setKeyboardTracking(False);form.addRow('Tamaño',self.font_size)
        self.bold=QCheckBox('Negrita');form.addRow(self.bold)
        self.appearance=TextAppearance();form.addRow(self.appearance)
        self.spins={}
        for key,title in [('x','Posición X'),('y','Posición Y'),('w','Anchura'),('h','Altura')]:
            control=QDoubleSpinBox();control.setRange(0,1000);control.setDecimals(3);control.setSuffix(' mm');control.setKeyboardTracking(False)
            self.spins[key]=control;form.addRow(title,control);control.valueChanged.connect(self.changed)
        form.addRow(button('Restablecer este campo',self.restore_field))
        form.addRow(button('Restablecer diseño de origen',self.restore_all))
        self.variant_button=button('Crear variante documental…',self.create_variant);form.addRow(self.variant_button)
        help_text=label('Reutilizar: Copiar trabajo conserva formato, composición y ajustes de prueba sin aprobarlos. Las variantes conservan diseños documentales; los perfiles sólo guardan formato físico.','subtle');help_text.setWordWrap(True);form.addRow(help_text)
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(panel);scroll.setMinimumWidth(270);scroll.setMaximumWidth(355);split.addWidget(scroll)
        self.pdf=PdfPane(self.api);split.addWidget(self.pdf);split.setStretchFactor(1,1);root.addWidget(split,1)
        self.error=label('','subtle');self.error.setWordWrap(True);root.addWidget(self.error)
        self.buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Apply|QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Apply).setText('Aplicar sólo al trabajo de prueba')
        self.buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply)
        self.buttons.rejected.connect(self.reject);root.addWidget(self.buttons)
        self.timer=QTimer(self);self.timer.setSingleShot(True);self.timer.timeout.connect(self.preview)
        self.field.currentIndexChanged.connect(self.load_field);self.font_size.valueChanged.connect(self.changed);self.bold.toggled.connect(self.changed);self.appearance.edited.connect(self.changed)
        self.load_field();self.preview()

    def load_field(self,*_):
        key=self.field.currentData();valid=key in self.fields
        self.buttons.button(QDialogButtonBox.StandardButton.Apply).setEnabled(valid)
        if not valid:return
        self.loading=True
        field=deepcopy(self.fields[key]);field.update(self.trial['fields'].get(key,{}))
        self.value.setText(self.work['values'].get(key,''));self.value.setToolTip('Los valores específicos por recipiente se conservan y se renderizan en el PDF de prueba.')
        self.font_size.setValue(field['font_pt']);self.bold.setChecked(field.get('bold',False));self.appearance.load(field)
        for k,c in self.spins.items():
            c.setValue(field[k]*self.version['base_w_mm' if k in ('x','w') else 'base_h_mm']);c.setEnabled(not field.get('locked'))
        self.loading=False;self.input_valid=True

    def changed(self,*_):
        if self.loading or self.field.currentData() not in self.fields:return
        key=self.field.currentData();patch=deepcopy(self.trial['fields'].get(key,{}))
        patch.update(font_pt=self.font_size.value(),bold=self.bold.isChecked())
        try:
            style=self.appearance.configuration()
            if style is not None:patch['typography']=style
            elif 'typography' in self.fields[key]:patch['typography']=None
            else:patch.pop('typography',None)
            source=self.fields[key]
            if not source.get('locked'):
                for k,c in self.spins.items():
                    value=c.value()/self.version['base_w_mm' if k in ('x','w') else 'base_h_mm']
                    # Do not round untouched source geometry through mm display.
                    if abs(value-source[k])>0.0005/self.version['base_w_mm' if k in ('x','w') else 'base_h_mm']:patch[k]=value
            candidate=deepcopy(self.trial);candidate['fields'][key]=patch
            apply_trial(self.version,candidate);self.trial=candidate
            self.input_valid=True
            self.buttons.button(QDialogButtonBox.StandardButton.Apply).setEnabled(True);self.variant_button.setEnabled(True)
            self.error.setText('PRUEBA / NO GMP · Sin modificación documental.');self.timer.start(350)
        except (ValueError,PermissionError) as ex:
            self.input_valid=False
            self.timer.stop();self.buttons.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False);self.variant_button.setEnabled(False)
            self.error.setText('Ajuste no aplicado: '+str(ex));self.pdf.clear(self.error.text())

    def profile(self):
        profile=deepcopy(self.work['profile'])
        if self.trial['fields']:profile['trial_appearance']=deepcopy(self.trial)
        else:profile.pop('trial_appearance',None)
        return profile

    def preview(self):
        try:
            if not self.input_valid:return
            self.verify_origin()
            work=deepcopy(self.work);work['profile']=self.profile();profile,indices,count,copies=parameters(work)
            path=self.api.output_path('cache','r8c-appearance-'+uuid.uuid4().hex+'.pdf')
            result=self.api.render(self.version,work['values'],profile,indices,count,copies,path,True,per_container=work['per_container'],status=work['status'])
            self.verify_origin()
            self.pdf.load(path,'PDF real · PRUEBA / NO GMP','Los datos y el diseño aprobado permanecen intactos. '+ ' · '.join(result['warnings']))
        except (ValueError,OSError,RuntimeError) as ex:self.pdf.clear('Prueba bloqueada: '+str(ex))

    def verify_origin(self):
        if self.api.work.get(self.work['uid'])['generation']!=self.work['generation']:
            raise ValueError('El trabajo cambió en otra ventana. Cierre y recargue antes de ajustar.')
        self.api.work.assert_current(self.work)

    def restore_field(self):
        self.trial['fields'].pop(self.field.currentData(),None);self.load_field();self.preview()

    def restore_all(self):
        self.trial=dict(contract=1,fields={});self.load_field();self.preview()

    def apply(self):
        try:
            for control in (self.font_size,*self.spins.values()):control.interpretText()
            if not self.input_valid:return
            w=self.work
            self.controller.emission_work=self.api.work.save(w['uid'],w['generation'],{'profile':self.profile()})
            self.controller.refresh_work_panels();self.accept()
        except (ValueError,OSError) as ex:self.error.setText(str(ex))

    def create_variant(self):
        if not self.input_valid:return
        if not self.trial['fields']:
            self.error.setText('No hay ajustes que trasladar a una variante.');return
        answers=[]
        for title in ('Código de variante','Nombre de variante','Motivo documental'):
            value,ok=QInputDialog.getText(self,'Nueva variante en borrador',title+':')
            if not ok:return
            answers.append(value)
        try:
            self.verify_origin()
            from ..variants import update_design_layout,design_from_revision
            from ..editor_layout import layout_from_version
            effective=apply_trial(self.version,self.trial);layout=layout_from_version(effective)
            origin=self.work['binding']['variant_id']
            base=json.loads(self.api.variant(origin)['design_json']) if origin else design_from_revision(self.version)
            design=update_design_layout(base,layout)
            # Validate BEFORE creating the auditable draft. No approval shortcut.
            self.api._repository.variants.validate(self.version,design)
            row=self.api.create_variant(self.version['id'],*answers,self.api.setting('operator'),origin_id=origin)
            row=self.api.save_variant(row['id'],row['generation'],design,self.api.setting('operator'))
            template=deepcopy(self.work);template['profile']=self.profile();template['profile'].pop('trial_appearance',None)
            self.controller.emission_work=self.api.work.create(self.version['id'],row['id'],self.work['name']+' · '+row['code'],template)
            self.controller.refresh_work_panels();self.controller.refresh()
            self.controller.select_version(self.version['id']);self.controller.library_variant_id=row['id']
            self.controller.fill_variants(self.controller.variant_selector,self.version['id'],row['id'])
            self.accept();self.controller.open_editor()
        except (ValueError,OSError,PermissionError) as ex:self.error.setText('Variante no completada: '+str(ex))
