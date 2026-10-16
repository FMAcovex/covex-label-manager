"""Stepwise Qt folder import using the existing service, with explicit per-file outcomes."""
from pathlib import Path
from PySide6.QtCore import QTimer,Qt
from PySide6.QtWidgets import (
    QDialog,QFileDialog,QMessageBox,QProgressBar,QTableWidget,QTableWidgetItem,
    QAbstractItemView,QHeaderView,QDialogButtonBox,QHBoxLayout,QCheckBox,
)
from .window import vbox,label,button
from ..importer import proposed_identity
from ..catalog_migration import inventory,guarded_import,export_inventory_csv

class FolderImportDialog(QDialog):
    def __init__(self,parent,api,folder,paths=None):
        super().__init__(parent)
        self.api=api;self.folder=Path(folder)
        self.paths=list(paths) if paths is not None else list(api.importable_files(folder))
        self.done=0;self.ok=0;self.failures=[];self.running=False;self.cancelled=False
        self.inventory=inventory(api,self.paths)
        self.setWindowTitle('R5A · Inventario y migración controlada')
        self.resize(930,610)
        lay=vbox(self,14,9)
        lay.addWidget(label('Archivos encontrados: '+str(len(self.paths)), 'panelTitle'))
        note=label('Se importarán uno por uno, siempre como revisiones PENDIENTES. '
                   'Cancelar detiene los siguientes archivos: no revierte los ya importados. '
                   'Revise individualmente los recortes y campos antes de aprobar.', 'subtle')
        note.setWordWrap(True);lay.addWidget(note)
        self.table=QTableWidget(len(self.paths),6)
        self.table.setHorizontalHeaderLabels(['Archivo','Nombre propuesto','Revisión','Categoría','Resultado','Importar'])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.data=[];self.include=[]
        for i,p in enumerate(self.paths):
            candidate=self.inventory[i]
            identity={'name':candidate['name'],'version':candidate['version'],
                      'category':candidate['category']}
            row=dict(name=identity['name'],version=identity['version'],category=identity['category'],
                     code='',annex='',origin='COVEX',customer='',ref_customer='')
            self.data.append(row)
            for j,t in enumerate((p.name,row['name'],row['version'],row['category'],
                                   candidate['status']+' · '+candidate['reason'])):
                cell=QTableWidgetItem(str(t));cell.setToolTip(str(p)+' / '+candidate['reason']);self.table.setItem(i,j,cell)
            checked=QTableWidgetItem()
            safe=candidate['status']=='NEW'
            checked.setFlags(Qt.ItemFlag.ItemIsEnabled|Qt.ItemFlag.ItemIsUserCheckable
                             if safe else Qt.ItemFlag.NoItemFlags)
            checked.setCheckState(Qt.CheckState.Checked if safe else Qt.CheckState.Unchecked)
            checked.setToolTip('NUEVO: importar como PENDING' if safe else 'Requiere conciliación: '+candidate['reason'])
            self.table.setItem(i,5,checked);self.include.append(checked)
        lay.addWidget(self.table,1)
        self.progress=QProgressBar();self.progress.setRange(0,len(self.paths));lay.addWidget(self.progress)
        self.status=label('Revise la lista antes de empezar.','subtle');self.status.setWordWrap(True);lay.addWidget(self.status)
        row=QHBoxLayout();self.start_button=button('Comenzar importación',self.start,'primary')
        self.stop_button=button('Detener tras archivo actual',self.stop);self.stop_button.setEnabled(False)
        row.addWidget(self.start_button);row.addWidget(self.stop_button);row.addStretch()
        row.addWidget(button('Exportar inventario CSV…',self.export_report))
        row.addWidget(button('Cerrar',self.close_requested));lay.addLayout(row)
        self.timer=QTimer(self);self.timer.setSingleShot(True);self.timer.timeout.connect(self.step)

    def start(self):
        if self.running or self.done or not self.paths:return
        selected=sum(c.checkState()==Qt.CheckState.Checked for c in self.include)
        if not selected:
            self.status.setText('No hay archivos NUEVOS seleccionados. Exporte el inventario.')
            return
        if QMessageBox.question(self,'Confirmar R5A',
                f'Importar hasta {selected} nuevos documentos como PENDING. '
                'Duplicados y coincidencias no se importarán. '
                'Lo incorporado no se revierte al detener. ¿Continuar?',
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Yes:return
        self.running=True;self.start_button.setEnabled(False);self.stop_button.setEnabled(True)
        self.status.setText('Importando… No cierre la aplicación durante la conversión de un documento.')
        self.timer.start(0)

    def step(self):
        if not self.running:return
        if self.cancelled or self.done>=len(self.paths):
            self.finish();return
        index=self.done;path=self.paths[index];candidate=self.inventory[index]
        if self.include[index].checkState()!=Qt.CheckState.Checked and candidate['status']!='ERROR':
            status=candidate['status']+' · omitido para conciliación'
        else:
            try:
                if candidate['status']=='ERROR':
                    raise ValueError(candidate['reason'])
                guarded_import(self.api,candidate,self.data[index])
                self.ok+=1;status='Importado · PENDING, revisar documento'
            except Exception as ex:
                msg=f'{path.name}: {str(ex)}'
                self.failures.append(msg);status='Incidencia: '+str(ex)
        candidate['outcome']=status
        self.table.item(index,4).setText(status)
        self.table.item(index,4).setToolTip(status)
        self.done+=1;self.progress.setValue(self.done)
        self.status.setText(f'{self.done}/{len(self.paths)} revisados · {self.ok} importados · {len(self.failures)} incidencias')
        self.timer.start(0)

    def stop(self):
        self.cancelled=True
        self.stop_button.setEnabled(False)
        self.status.setText('Se detendrá antes del siguiente archivo. Espere si una conversión está en curso.')

    def finish(self):
        self.timer.stop();self.running=False;self.stop_button.setEnabled(False)
        result='Detenido por el usuario' if self.cancelled else 'Finalizado'
        self.status.setText(f'{result}: {self.ok} importados, {len(self.failures)} con incidencias, '
                            f'{len(self.paths)-self.done} sin procesar. '
                            'Todos los incorporados están pendientes de revisión.')
        if self.failures:self.status.setToolTip('\n'.join(self.failures))
    def export_report(self):
        if self.running:
            self.status.setText('Detenga primero la importación para exportar resultados.')
            return
        target,_=QFileDialog.getSaveFileName(self,'Guardar inventario R5A','Inventario_R5A.csv','CSV (*.csv)')
        if not target:return
        try:
            export_inventory_csv(self.inventory,target,self.api.location())
            self.status.setText('Inventario guardado; no constituye aprobación documental.')
        except (OSError,ValueError,PermissionError) as ex:
            self.status.setText('No se pudo guardar CSV: '+str(ex))

    def close_requested(self):
        if self.running:self.stop();return
        self.accept()
    def reject(self):
        if self.running:self.stop();return
        super().reject()


class FolderImportMixin:
    def import_folder_native(self):
        if self.legacy_process is not None or not self.flush_emission_work() or not self.resolve_work():return
        folder=QFileDialog.getExistingDirectory(self,'Seleccionar carpeta de etiquetas')
        if not folder:return
        try:
            paths=list(self.api.importable_files(folder))
            if not paths:
                QMessageBox.information(self,'Sin documentos','No hay archivos compatibles en la carpeta.')
                return
            dialog=FolderImportDialog(self,self.api,folder,paths)
            dialog.exec()
            if dialog.done:
                self.refresh_facets();self.refresh();self.recheck_actions()
                self.statusBar().showMessage(f'Importación: {dialog.ok} pendientes incorporadas; '
                                            f'{len(dialog.failures)} incidencias.')
        except (ValueError,OSError) as ex:
            QMessageBox.warning(self,'Importación no iniciada',str(ex))
