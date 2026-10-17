"""Controlled batch import: default skip, explicit per-row approval to PENDING."""
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QDialog,QFileDialog,QMessageBox,QComboBox,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QProgressBar,QHBoxLayout,QDialogButtonBox,QLineEdit,QFormLayout
from .window import vbox,label,button
from .responsive import AdaptiveDialog as QDialog

class ControlledImportDialog(QDialog):
    def __init__(self,parent,api,folder):
        super().__init__(parent);self.api=api;self.folder=folder
        self.rows=api.catalog_migration_preview(folder)['files']
        self.done=0;self.ok=0;self.failures=[];self.running=False;self.cancelled=False;self.queue=[]
        self.setWindowTitle('R5B · Importación y conciliación documental');self.resize(1000,610)
        layout=vbox(self);tip=label('Por defecto se omite todo. Seleccione cada acción y confirme la identidad. Todas las incorporaciones quedan PENDIENTES.','subtle');tip.setWordWrap(True);layout.addWidget(tip)
        self.table=QTableWidget(len(self.rows),5);self.table.setHorizontalHeaderLabels(['Documento','Diagnóstico','Acción','Destino','Resultado'])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.metadata=[];self.actions=[];self.targets=[]
        for i,r in enumerate(self.rows):
            self.metadata.append(dict(name=r.get('name',''),version=r.get('version','00'),category=r.get('category',''),origin='COVEX',code='',annex='',customer='',ref_customer=''))
            for j,s in ((0,r['source']),(1,r['status']),(4,'Omitido')):self.table.setItem(i,j,QTableWidgetItem(s))
            a=QComboBox();a.addItem('Omitir',None)
            if r['status'] in ('REVIEW_REQUIRED','IDENTITY_CONFLICT'):
                a.addItem('Nueva etiqueta','NEW_LABEL');a.addItem('Nueva revisión','NEW_REVISION')
            self.table.setCellWidget(i,2,a);self.actions.append(a)
            t=QComboBox();t.addItem('Seleccionar existente',None)
            for l in api.labels():t.addItem(l['name']+' / '+l['code'],l['id'])
            self.table.setCellWidget(i,3,t);self.targets.append(t)
        layout.addWidget(self.table,1)
        layout.addWidget(button('Editar identidad de la fila',self.edit_identity))
        self.progress=QProgressBar();layout.addWidget(self.progress)
        self.status=label('Sin cambios hasta confirmar.','subtle');layout.addWidget(self.status)
        bar=QHBoxLayout();self.go=button('Confirmar importación seleccionada',self.start,'primary');bar.addWidget(self.go)
        self.stop_button=button('Detener tras archivo actual',self.stop);self.stop_button.setEnabled(False);bar.addWidget(self.stop_button)
        bar.addWidget(button('Cerrar',self.close_requested));layout.addLayout(bar)
        self.timer=QTimer(self);self.timer.setSingleShot(True);self.timer.timeout.connect(self.step)
    def edit_identity(self):
        i=self.table.currentRow()
        if i<0 or self.running:return
        dlg=QDialog(self);dlg.setWindowTitle('Identidad documental');lay=vbox(dlg);form=QFormLayout();inputs={}
        for k,title in [('name','Nombre'),('version','Revisión'),('code','Código'),('origin','Origen COVEX/CLIENTE'),('customer','Cliente'),('category','Categoría'),('annex','Anexo'),('ref_customer','Referencia cliente')]:
            e=QLineEdit(self.metadata[i][k]);inputs[k]=e;form.addRow(title,e)
        lay.addLayout(form);buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(dlg.accept);buttons.rejected.connect(dlg.reject);lay.addWidget(buttons)
        if dlg.exec()==QDialog.DialogCode.Accepted:self.metadata[i]={k:v.text().strip() for k,v in inputs.items()}
    def selected(self):
        items=[]
        for i,a in enumerate(self.actions):
            if not a.currentData():continue
            d={**self.metadata[i],'action':a.currentData(),'target_label_id':self.targets[i].currentData()}
            if a.currentData()=='NEW_REVISION' and d['target_label_id'] is None:raise ValueError(f'Fila {i+1}: seleccione destino.')
            items.append((i,d))
        return items
    def start(self):
        if self.running or self.done:return
        try:self.queue=self.selected()
        except ValueError as ex:QMessageBox.warning(self,'Destino obligatorio',str(ex));return
        if not self.queue:return
        if QMessageBox.question(self,'Confirmar importación',f'Se incorporarán hasta {len(self.queue)} revisiones PENDIENTES. No se reemplaza documentación. ¿Continuar?',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Yes:return
        self.running=True;self.go.setEnabled(False);self.table.setEnabled(False);self.stop_button.setEnabled(True);self.timer.start(0)
    def step(self):
        if not self.running:return
        if self.cancelled or self.done>=len(self.queue):self.finish();return
        i,d=self.queue[self.done]
        try:
            result=self.api.catalog_migration_apply(self.folder,self.rows[i],d)
            self.ok+=1;msg='PENDIENTE #'+str(result['version_id'])
        except Exception as ex:
            msg='Incidencia: '+str(ex);self.failures.append(msg)
        self.table.item(i,4).setText(msg);self.done+=1;self.progress.setMaximum(len(self.queue));self.progress.setValue(self.done)
        self.status.setText(f'{self.done}/{len(self.queue)} · {self.ok} incorporados · {len(self.failures)} incidencias')
        self.timer.start(0)
    def stop(self):self.cancelled=True;self.stop_button.setEnabled(False)
    def finish(self):
        self.timer.stop();self.running=False;self.stop_button.setEnabled(False)
        self.status.setText(f'Importación finalizada o detenida: {self.ok} incorporados; {len(self.failures)} incidencias; {len(self.queue)-self.done} pendientes.')
    def close_requested(self):
        if self.running:self.stop();return
        self.accept()
    def reject(self):
        if self.running:self.stop();return
        super().reject()
