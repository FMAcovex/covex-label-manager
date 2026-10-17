"""Folder wizard over the unchanged R5B pending-only, hash-checked service."""
from pathlib import Path
import uuid
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (QFileDialog,QMessageBox,QComboBox,QTableWidget,
    QTableWidgetItem,QHeaderView,QAbstractItemView,QProgressBar,QHBoxLayout,
    QDialogButtonBox,QLineEdit,QFormLayout,QStackedWidget,QWidget,QCheckBox,QApplication)
from .window import vbox,label,button
from .responsive import AdaptiveDialog as QDialog,retain_screens

DIAGNOSES={
    'REVIEW_REQUIRED':'Revisar identidad y elegir acción',
    'IDENTITY_CONFLICT':'Coincide nombre/revisión: compruebe el destino',
    'EXACT_DUPLICATE':'Ya incorporado: se omite',
    'HASH_CONFLICT':'Contenido coincidente: requiere conciliación',
    'BATCH_DUPLICATE':'Duplicado en esta carpeta: se omite',
    'BLOCKED_PAIR':'Varias fuentes ambiguas: separar documentos',
    'BLOCKED_UNSAFE':'Ruta no segura: bloqueada',
}


class ControlledImportDialog(QDialog):
    def __init__(self,parent,api,folder=None):
        super().__init__(parent)
        self.api=api;self.folder=None;self.rows=[];self.metadata=[];self.actions=[];self.targets=[]
        # Never shadow QDialog.done(int): Qt calls this virtual method on closing.
        self.processed=0;self.ok=0;self.failures=[];self.running=False;self.cancelled=False
        self.queue=[];self.imported=[];self.editor_version_id=None;self.close_when_stopped=False
        self.setWindowTitle('Importar carpeta · Asistente documental');self.resize(1050,650)
        layout=vbox(self);self.heading=label('1 · Seleccionar carpeta','panelTitle');layout.addWidget(self.heading)
        self.pages=QStackedWidget();layout.addWidget(self.pages,1)
        first=QWidget();fl=vbox(first,0,6)
        note=label('Seleccione una carpeta local. No se modifica ningún original ni se aprueba documentación.','subtle');note.setWordWrap(True);fl.addWidget(note)
        self.folder_path=QLineEdit();self.folder_path.setReadOnly(True);self.folder_path.setAccessibleName('Carpeta seleccionada');fl.addWidget(self.folder_path)
        self.choose_button=button('Seleccionar / cambiar carpeta…',self.choose_folder);fl.addWidget(self.choose_button)
        self.folder_summary=label('PDF, Word e imágenes; se incluyen subcarpetas.','subtle');self.folder_summary.setWordWrap(True);fl.addWidget(self.folder_summary);fl.addStretch();self.pages.addWidget(first)
        review=QWidget();rl=vbox(review,0,6)
        self.review_path=label('','subtle');self.review_path.setWordWrap(True);rl.addWidget(self.review_path)
        hint=label('Sugerencias no confirmadas: edite identidad y elija acción. En Nueva revisión se conserva la identidad del destino; solo cambia la revisión. Desplace la tabla para ver código, categoría y comprobaciones.','subtle');hint.setWordWrap(True);rl.addWidget(hint)
        self.table=QTableWidget(0,9);self.table.setAccessibleName('Documentos e identidad editable')
        self.table.setHorizontalHeaderLabels(['Archivo','Nombre editable','Revisión','Acción','Destino existente','Código','Categoría / tipo','Comprobación previa','Resultado'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.verticalHeader().hide();self.table.setMinimumHeight(100)
        for col,width in enumerate((150,180,80,160,210,130,180,250,250)):self.table.setColumnWidth(col,width)
        self.table.itemChanged.connect(self.identity_changed);rl.addWidget(self.table,1)
        tools=QHBoxLayout();tools.addWidget(button('Identidad de la fila…',self.edit_identity))
        tools.addWidget(button('Datos a filas seleccionadas…',self.bulk_identity))
        tools.addWidget(button('Vista previa…',self.preview_selected));rl.addLayout(tools)
        self.confirm_identity=QCheckBox('He revisado identidades, sugerencias y destinos seleccionados.')
        self.confirm_identity.toggled.connect(self.update_buttons);self.pages.addWidget(review)
        result=QWidget();sl=vbox(result,0,6)
        self.results=QTableWidget(0,2);self.results.setHorizontalHeaderLabels(['Documento','Resultado por archivo'])
        self.results.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch);sl.addWidget(self.results,1)
        self.pages.addWidget(result)
        self.wizard_footer=QWidget()
        footer=vbox(self.wizard_footer,0,6);layout.addWidget(self.wizard_footer)
        self.progress=QProgressBar();self.progress.setRange(0,1);footer.addWidget(self.progress)
        self.status=label('Sin cambios hasta revisar y confirmar la importación.','subtle');self.status.setWordWrap(True);footer.addWidget(self.status)
        footer.addWidget(self.confirm_identity)
        self.editor_actions=QWidget();editor_bar=QHBoxLayout(self.editor_actions);editor_bar.setContentsMargins(0,0,0,0)
        self.editor_choice=QComboBox();self.editor_choice.setAccessibleName('Revisión importada para abrir en Editor');editor_bar.addWidget(self.editor_choice,1)
        self.editor_button=button('Abrir pendiente en Editor',self.open_editor,'primary');self.editor_button.setEnabled(False);editor_bar.addWidget(self.editor_button);footer.addWidget(self.editor_actions)
        bar=QHBoxLayout();self.back=button('Atrás',self.previous_page);bar.addWidget(self.back)
        self.next=button('Revisar documentos →',self.next_page,'primary');bar.addWidget(self.next)
        self.go=button('Importar como pendientes',self.start,'primary');bar.addWidget(self.go)
        self.stop_button=button('Detener tras archivo actual',self.stop);bar.addWidget(self.stop_button)
        bar.addStretch();self.close_button=button('Cerrar',self.close_requested);bar.addWidget(self.close_button);footer.addLayout(bar)
        self.timer=QTimer(self);self.timer.setSingleShot(True);self.timer.timeout.connect(self.step)
        self.pages.currentChanged.connect(self.update_buttons)
        if folder is not None:self.set_folder(folder)
        self.update_buttons()

    def update_buttons(self,*_):
        page=self.pages.currentIndex()
        self.confirm_identity.setVisible(page==1);self.editor_actions.setVisible(page==2);self.progress.setVisible(page==2)
        self.heading.setText(['1 · Seleccionar carpeta','2 · Revisar e identificar documentos','3 · Importación y acceso al Editor'][page])
        self.back.setVisible(page==1);self.next.setVisible(page==0);self.next.setEnabled(bool(self.rows))
        self.go.setVisible(page==1);self.go.setEnabled(self.confirm_identity.isChecked() and not self.running and not self.processed)
        self.stop_button.setVisible(page==2);self.stop_button.setEnabled(self.running and not self.cancelled)
        QTimer.singleShot(0,self.fit_footer)

    def prepare_layout(self):
        # This wizard already has scrollable tables and its own persistent
        # footer. Do not wrap the whole stack in another height-for-width scroll
        # area: changing pages can otherwise push footer children off-screen.
        retain_screens(QApplication.instance())
        self._adaptive_ready=True;self.footer_widgets=[self.wizard_footer]
        self.setMinimumSize(0,0)

    def fit_footer(self):
        """Reserve wrapped status + all actions, not just QWidget's one-line hint."""
        margins=self.layout().contentsMargins()
        width=max(100,self.width()-margins.left()-margins.right())
        footer_layout=self.wizard_footer.layout();footer_layout.invalidate()
        height=max(footer_layout.minimumSize().height(),footer_layout.totalHeightForWidth(width))
        self.wizard_footer.setMinimumHeight(height)
        self.wizard_footer.updateGeometry()
        self.layout().invalidate()
        self.layout().setGeometry(self.rect())

    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,'wizard_footer'):self.fit_footer()

    def choose_folder(self):
        folder=QFileDialog.getExistingDirectory(self,'Seleccionar carpeta de documentos',str(self.folder or ''))
        if folder:
            try:self.set_folder(folder)
            except (ValueError,OSError) as ex:QMessageBox.warning(self,'Carpeta no disponible',str(ex))

    def set_folder(self,folder):
        if self.running or self.processed:return
        rows=self.api.catalog_migration_preview(folder)['files'];self.folder=Path(folder);self.rows=rows
        self.folder_path.setText(str(self.folder));self.folder_path.setToolTip(str(self.folder));self.review_path.setText('Carpeta: '+str(self.folder))
        self.folder_summary.setText(f'{len(rows)} documentos detectados. Continúe para revisar identidades y coincidencias.')
        self.confirm_identity.setChecked(False);self.metadata=[];self.actions=[];self.targets=[]
        self.table.blockSignals(True);self.table.setRowCount(len(rows));labels=list(self.api.labels())
        for i,r in enumerate(rows):
            meta=dict(name=r.get('name',''),version=r.get('version','00'),category=r.get('category',''),origin='COVEX',code='',annex='',customer='',ref_customer='');self.metadata.append(meta)
            texts={0:r['source'],7:DIAGNOSES.get(r['status'],'Revisar diagnóstico'),1:meta['name'],5:meta['code'],2:meta['version'],6:meta['category'],8:'Omitido'}
            for col,text in texts.items():
                item=QTableWidgetItem(str(text));item.setToolTip(str(text))
                if col not in (1,2,5,6):item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(i,col,item)
            action=QComboBox();action.addItem('Omitir',None)
            if r['status'] in ('REVIEW_REQUIRED','IDENTITY_CONFLICT'):
                action.addItem('Nueva etiqueta','NEW_LABEL');action.addItem('Nueva revisión','NEW_REVISION')
            action.setAccessibleName(f'Acción documento {i+1}');self.table.setCellWidget(i,3,action);self.actions.append(action)
            target=QComboBox();target.addItem('Seleccione etiqueta existente',None)
            for entry in labels:target.addItem(entry['name']+' / '+entry['code'],entry['id'])
            target.setEnabled(False);target.setAccessibleName(f'Destino documento {i+1}');self.table.setCellWidget(i,4,target);self.targets.append(target)
            action.currentIndexChanged.connect(lambda _,n=i:self.action_changed(n))
            target.currentIndexChanged.connect(lambda _,n=i:self.target_changed(n))
            self.table.setRowHeight(i,max(action.sizeHint().height(),target.sizeHint().height(),self.table.fontMetrics().height())+10)
        self.table.blockSignals(False);self.update_buttons()

    def action_changed(self,i):
        self.targets[i].setEnabled(self.actions[i].currentData()=='NEW_REVISION');self.confirm_identity.setChecked(False)
        for col in (1,5,6):
            item=self.table.item(i,col)
            editable=self.actions[i].currentData()!='NEW_REVISION'
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable if editable else item.flags() & ~Qt.ItemFlag.ItemIsEditable)

    def target_changed(self,i):
        self.targets[i].setToolTip(self.targets[i].currentText());self.confirm_identity.setChecked(False)

    def identity_changed(self,item):
        key={1:'name',5:'code',2:'version',6:'category'}.get(item.column())
        if key:
            self.metadata[item.row()][key]=item.text().strip();item.setToolTip(item.text());self.confirm_identity.setChecked(False)

    def next_page(self):
        if self.rows:self.pages.setCurrentIndex(1)

    def previous_page(self):
        if not self.running and not self.processed:self.pages.setCurrentIndex(0)

    def edit_identity(self):
        i=self.table.currentRow()
        if i>=0:self.identity_form([i],False)

    def bulk_identity(self):
        indices=sorted({i.row() for i in self.table.selectedIndexes()})
        if indices:self.identity_form(indices,True)
        else:self.status.setText('Seleccione filas antes de aplicar datos comunes.')

    def identity_form(self,indices,bulk):
        if self.running or self.processed:return
        dlg=QDialog(self);dlg.setWindowTitle('Datos comunes · Solo campos marcados' if bulk else 'Identidad documental completa')
        lay=vbox(dlg);form=QFormLayout();inputs={};checks={}
        action_check=None
        if bulk:
            action_check=QCheckBox('Aplicar acción a filas seleccionadas')
            action=QComboBox();action.addItem('Omitir',None);action.addItem('Nueva etiqueta','NEW_LABEL');action.addItem('Nueva revisión','NEW_REVISION')
            form.addRow(action_check,action)
        for key,title in [('name','Nombre'),('version','Revisión'),('code','Código'),('origin','Origen COVEX/CLIENTE'),('customer','Cliente'),('category','Categoría / tipo sugerido'),('annex','Anexo'),('ref_customer','Referencia cliente')]:
            edit=QLineEdit('' if bulk else self.metadata[indices[0]][key]);inputs[key]=edit
            if bulk:
                check=QCheckBox(title);checks[key]=check;form.addRow(check,edit)
            else:form.addRow(title,edit)
        lay.addLayout(form);buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dlg.accept);buttons.rejected.connect(dlg.reject);lay.addWidget(buttons)
        if dlg.exec()!=QDialog.DialogCode.Accepted:return
        for i in indices:
            for key,edit in inputs.items():
                if not bulk or checks[key].isChecked():self.metadata[i][key]=edit.text().strip()
            for col,key in ((1,'name'),(5,'code'),(2,'version'),(6,'category')):self.table.item(i,col).setText(self.metadata[i][key])
            if bulk and action_check.isChecked():
                choice=self.actions[i].findData(action.currentData())
                if choice>=0:self.actions[i].setCurrentIndex(choice)
        self.confirm_identity.setChecked(False)

    def preview_selected(self):
        i=self.table.currentRow()
        if i<0 or self.running:return
        try:
            from ..catalog_migration import safe
            from ..importer import docx_to_pdf
            from .pdf_view import PdfPane
            row=self.rows[i];path=safe(self.folder.resolve(),row.get('pdf') or row['source'])
            if path.suffix.lower()!='.pdf':path=docx_to_pdf(path,self.api.output_path('cache','import-preview-'+uuid.uuid4().hex))
            dlg=QDialog(self);dlg.setWindowTitle('Vista previa de origen · Sin importar');dlg.resize(900,620);lay=vbox(dlg)
            pane=PdfPane(self.api);lay.addWidget(pane,1);pane.load(path,'Documento de origen','Compruebe identidad y legibilidad. No se ha importado ni aprobado este documento.')
            buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);buttons.rejected.connect(dlg.reject);lay.addWidget(buttons);dlg.exec()
        except Exception as ex:QMessageBox.warning(self,'Vista previa no disponible',str(ex))

    def selected(self):
        items=[]
        for i,action in enumerate(self.actions):
            if not action.currentData():continue
            meta={**self.metadata[i],'action':action.currentData(),'target_label_id':self.targets[i].currentData()}
            if not meta['name'] or not meta['version']:raise ValueError(f'Fila {i+1}: nombre y revisión obligatorios.')
            if meta['action']=='NEW_REVISION' and meta['target_label_id'] is None:raise ValueError(f'Fila {i+1}: seleccione destino.')
            items.append((i,meta))
        return items

    def start(self):
        if self.running or self.processed or not self.confirm_identity.isChecked():return
        try:self.queue=self.selected()
        except ValueError as ex:QMessageBox.warning(self,'Revise la identidad',str(ex));return
        if not self.queue:self.status.setText('Elija Nueva etiqueta o Nueva revisión en al menos un documento.');return
        if QMessageBox.question(self,'Confirmar importación',f'Se incorporarán hasta {len(self.queue)} revisiones PENDIENTES. No se reemplaza documentación. Detener conserva lo ya importado. ¿Continuar?',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Yes:return
        self.running=True;self.table.setEnabled(False);self.pages.setCurrentIndex(2);self.results.setRowCount(len(self.queue));self.progress.setRange(0,len(self.queue))
        for n,(i,_) in enumerate(self.queue):
            self.results.setItem(n,0,QTableWidgetItem(self.rows[i]['source']));self.results.setItem(n,1,QTableWidgetItem('Sin procesar'))
        self.status.setText('Importando por archivo. Detener conserva las incorporaciones completadas.');self.update_buttons();self.timer.start(0)

    def step(self):
        if not self.running:return
        if self.cancelled or self.processed>=len(self.queue):self.finish();return
        i,decision=self.queue[self.processed]
        try:
            result=self.api.catalog_migration_apply(self.folder,self.rows[i],decision)
            self.ok+=1;self.imported.append(result);msg='Importado · PENDIENTE · Revisar campos y recorte'
            self.editor_choice.addItem(decision['name']+' / '+decision['version'],result['version_id'])
        except Exception as ex:
            msg='No importado: '+str(ex);self.failures.append(self.rows[i]['source']+': '+str(ex))
        self.table.item(i,8).setText(msg);self.results.item(self.processed,1).setText(msg);self.results.item(self.processed,1).setToolTip(msg)
        self.processed+=1;self.progress.setValue(self.processed);self.status.setText(f'{self.processed}/{len(self.queue)} · {self.ok} incorporados · {len(self.failures)} incidencias');self.timer.start(0)

    def stop(self):
        self.cancelled=True;self.stop_button.setEnabled(False);self.status.setText('Deteniendo antes del siguiente archivo. Se conserva lo ya importado.')

    def finish(self):
        self.timer.stop();self.running=False;self.update_buttons();self.editor_button.setEnabled(bool(self.imported))
        self.status.setText(f'{"Detenido" if self.cancelled else "Finalizado"}: {self.ok} incorporados; {len(self.failures)} incidencias; {len(self.queue)-self.processed} sin procesar. Todo lo incorporado queda PENDIENTE de revisión documental.')
        self.fit_footer()
        if self.close_when_stopped:super().reject()

    def open_editor(self):
        if self.running or not self.imported:return
        self.editor_version_id=self.editor_choice.currentData();self.accept()

    def close_requested(self):self.reject()

    def reject(self):
        if self.running:self.close_when_stopped=True;self.stop();return
        super().reject()

    def closeEvent(self,event):
        if self.running:self.close_when_stopped=True;self.stop();event.ignore();return
        super().closeEvent(event)
