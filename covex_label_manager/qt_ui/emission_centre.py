"""Native emission orchestration on the existing recoverable work contract."""
import json
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from PySide6.QtCore import Qt,QTimer
from PySide6.QtWidgets import (QApplication,QWidget,QScrollArea,QHBoxLayout,QVBoxLayout,QFormLayout,QSplitter,
    QDialog,QDialogButtonBox,QComboBox,QLineEdit,QMessageBox,QFileDialog,QInputDialog,QPushButton,QMenu)
from .window import label,button,vbox,box
from .responsive import AdaptiveDialog as QDialog
from .work import WorkPanel
from .pdf_view import PdfPane
from ..canonical import digest
from ..emission_work import parameters,profile_numbers,WorkCorrupt
from ..storage import sha256


class EmissionCentreMixin:
    def __init__(self,session):
        self.native_ready=False;self.native_busy=False;self.work_preview=None;self.work_review=None
        super().__init__(session)
        self.preview_serial=0;self.preview_task=None;self.preview_pending=False
        self.preview_timer=QTimer(self);self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.automatic_preview)
        self.native_ready=True;self.refresh_emission_review()
        self.setWindowTitle('COVEX Label Manager · Centro de emisión')
        self.statusBar().showMessage('Emisión e historial nativos · Fuentes originales protegidas')
    def build_emission_page(self):
        page=QWidget();layout=vbox(page,20,10)
        head=QHBoxLayout();titles=QVBoxLayout();self.emission_heading=label('Centro de emisión','title');titles.addWidget(self.emission_heading)
        self.emission_subtitle=label('Prepare, compruebe y emita etiquetas desde un trabajo recuperable.','subtle');titles.addWidget(self.emission_subtitle);head.addLayout(titles,1);head.addStretch()
        self.emission_compact=QComboBox();self.emission_compact.addItems(['Datos del trabajo','Vista previa PDF']);self.emission_compact.currentIndexChanged.connect(self.adapt_emission_layout);self.emission_compact.hide();head.addWidget(self.emission_compact)
        head.addWidget(button('Biblioteca',lambda:self.navigate('library')));layout.addLayout(head)
        self.emission_document=label('Seleccione un trabajo o cree uno nuevo.','subtle');self.emission_document.setWordWrap(True);layout.addWidget(self.emission_document)
        split=QSplitter(Qt.Orientation.Horizontal);self.emission_split=split
        left=box();ll=vbox(left,10,6);self.emission_panel=WorkPanel(self);self.work_panels.append(self.emission_panel);ll.addWidget(self.emission_panel,1)
        # The editor retains its shared panel. Emission has one persistent footer.
        for child in (self.emission_panel.save,self.emission_panel.proof,self.emission_panel.issue,
                      self.emission_panel.recover,self.emission_panel.binding_button):child.hide()
        tools=QHBoxLayout();tools.setSpacing(4)
        tools.addWidget(button('Pegar Excel…',self.paste_work_containers))
        tools.addWidget(button('Guardar perfil…',self.save_emission_profile))
        pattern=button('Hoja patrón…',self.calibrate_emission)
        pattern.setToolTip('Generar un PDF de referencia no productivo. Imprimir y medir en papel antes de aplicar una calibración.')
        tools.addWidget(pattern);ll.insertLayout(0,tools)
        self.emission_panel.setMinimumHeight(320);left.setMinimumWidth(330);left_scroll=QScrollArea();left_scroll.setWidgetResizable(True);left_scroll.setWidget(left);left_scroll.setFrameShape(QScrollArea.Shape.NoFrame);split.addWidget(left_scroll);self.emission_left=left_scroll
        right=box();rl=vbox(right,14,8);toolbar=QHBoxLayout();self.emission_check_heading=label('COMPROBAR ANTES DE EMITIR','section');toolbar.addWidget(self.emission_check_heading);toolbar.addStretch()
        self.preview_work_button=button('Actualizar vista previa',self.preview_emission_work);toolbar.addWidget(self.preview_work_button);rl.addLayout(toolbar)
        self.emission_pdf=PdfPane(self.api);rl.addWidget(self.emission_pdf,1);split.addWidget(right);self.emission_right=right;split.setSizes([490,960]);split.setStretchFactor(1,1);layout.addWidget(split,1)
        footer=box();self.emission_footer=footer;footer.setObjectName('emissionFooter');fl=vbox(footer,12,5)
        self.emission_summary=label('Sin trabajo seleccionado.','emissionSummary');self.emission_summary.setObjectName('emissionSummary');self.emission_summary.setWordWrap(True);fl.addWidget(self.emission_summary)
        self.emission_feedback=label('Guardar borrador no registra una emisión.','subtle');self.emission_feedback.setWordWrap(True);fl.addWidget(self.emission_feedback)
        actions=QHBoxLayout();self.native_save=button('Guardar trabajo',self.flush_emission_work);actions.addWidget(self.native_save)
        self.native_proof=button('PDF de prueba',self.proof_emission_work);actions.addWidget(self.native_proof)
        self.native_options=button('Opciones…',self.work_options);actions.addWidget(self.native_options);actions.addStretch()
        self.native_issue=button('Emitir definitivamente',self.issue_emission_work,'primary');actions.addWidget(self.native_issue)
        self.native_print=button('Imprimir PDF registrado…',self.print_emission_pdf);self.native_print.setEnabled(False);actions.addWidget(self.native_print)
        fl.addLayout(actions);layout.addWidget(footer)
        return page
    def refresh_work_panels(self):
        super().refresh_work_panels()
        if getattr(self,'native_ready',False):
            self.invalidate_work_preview();self.refresh_emission_review();self.schedule_preview()
    def work_changed(self,panel):
        super().work_changed(panel)
        if getattr(self,'native_ready',False):
            self.invalidate_work_preview();self.native_issue.setEnabled(False);self.schedule_preview()
    def flush_emission_work(self):
        result=super().flush_emission_work()
        if not result and getattr(self,'preview_task',None) is not None:
            self.work_timer.start(100)
        if getattr(self,'native_ready',False) and not self.native_busy:self.refresh_emission_review()
        return result
    def invalidate_work_preview(self):
        if hasattr(self,'preview_serial'):self.preview_serial+=1
        self.work_preview=None
        if hasattr(self,'emission_pdf'):self.emission_pdf.clear('Vista previa desactualizada · Se actualizará al terminar de editar.')
    def schedule_preview(self):
        self.preview_pending=True
        self.preview_timer.start(450)
    def automatic_preview(self):
        if self.preview_task is not None:return # finished starts the latest request
        self.preview_pending=False
        w=self.emission_work
        if not w or w['phase']!='DRAFT' or self.native_busy or self.legacy_process:return
        if not self.flush_emission_work():
            self.emission_pdf.clear('Revise errores · '+self.work_dirty_panel.note.text());return
        review=self.refresh_emission_review()
        if not review or not review['proof_allowed'] or any(e['target']!='document' for e in review['errors']):
            self.emission_pdf.clear('Revise errores · '+self.emission_feedback.text());return
        if self.preview_matches(review):return
        from .preview_task import PreviewTask
        w=self.emission_work;out=self.api.output_path('cache','qt-auto-proof-'+uuid.uuid4().hex+'.pdf')
        task=PreviewTask(self,self.api.location(),w['uid'],w['generation'],review['token'],out,self.preview_serial)
        self.preview_task=task;self.native_issue.setEnabled(False)
        self.emission_pdf.clear('Actualizando vista previa… Puede seguir editando.')
        task.completed.connect(self.automatic_preview_completed)
        task.finished.connect(self.automatic_preview_finished)
        task.start()
    def automatic_preview_completed(self,payload):
        w=self.emission_work
        current=(w and w['uid']==payload['uid'] and w['generation']==payload['generation']
                 and payload['serial']==self.preview_serial and not self.work_dirty_panel)
        review=self.refresh_emission_review() if current else None
        if not current or not review or review.get('token')!=payload['stamp']:
            Path(payload['path']).unlink(missing_ok=True)
            if current:self.emission_pdf.clear('Vista previa desactualizada · La documentación cambió. Revise el vínculo documental.')
            return
        if payload.get('error'):
            Path(payload['path']).unlink(missing_ok=True)
            self.emission_pdf.clear('Revise errores · '+self.operator_error(ValueError(payload['error'])))
            self.native_issue.setEnabled(False);return
        self.work_preview={k:payload[k] for k in ('uid','stamp','path','sha256','result')}
        self.emission_pdf.validator=lambda:self.verify_work_preview_pdf()
        try:
            self.emission_pdf.load(payload['path'],'Vista previa actualizada · PDF de prueba',
                'PRUEBA · No apto para uso productivo · Actualización automática sin registrar emisión.')
        except (ValueError,OSError,RuntimeError) as ex:
            self.work_preview=None;self.emission_pdf.clear('Revise errores · '+self.operator_error(ex));return
        self.refresh_emission_review()
        if payload['result']['warnings']:
            self.native_issue.setEnabled(False);self.emission_feedback.setText('Revise antes de emitir: '+' · '.join(payload['result']['warnings'][:5]))
    def automatic_preview_finished(self):
        task=self.preview_task;self.preview_task=None
        if task:task.deleteLater()
        self.refresh_emission_review()
        if self.preview_pending:self.preview_timer.start(450)
    def recheck_actions(self):
        super().recheck_actions()
        if getattr(self,'native_ready',False) and not self.native_busy:self.refresh_emission_review()
    def refresh_emission_review(self):
        w=self.emission_work;self.native_issue.setEnabled(False)
        self.native_print.setEnabled(bool(w and w['phase']=='ISSUED' and w.get('issue_id') and not self.native_busy and not self.legacy_process))
        self.native_save.setEnabled(bool(w and w['phase']=='DRAFT' and not self.native_busy))
        self.native_proof.setEnabled(bool(w and not self.native_busy));self.preview_work_button.setEnabled(bool(w and not self.native_busy))
        if not w:
            self._emission_document_full='Seleccione un trabajo o cree uno nuevo.'
            self.refresh_emission_caption()
            self.emission_summary.setText('Sin trabajo seleccionado.');self.work_review=None;return None
        try:review=self.api.review_work(w['uid'],w['generation'])
        except (ValueError,OSError,sqlite3.Error) as ex:
            review={'errors':[{'target':'work','message':self.operator_error(ex),'recipient':None}], 'warnings':[], 'summary':None,'proof_allowed':False,'production_allowed':False}
        self.work_review=review
        b=w['binding'];v=self.api.version(b['revision_id']);variant=self.api.variant(b['variant_id']) if b['variant_id'] else None
        self._emission_document_full=f"{v['name']} · Revisión {v['version']} · "+(f"Variante {variant['code']}" if variant else 'Diseño heredado')+' · '+w['name']
        self.refresh_emission_caption()
        s=review['summary']
        if s:self.emission_summary.setText(f"{s['selected']} de {s['containers']} recipientes · {s['copies']} copias · {s['physical']} etiquetas · {s['pages']} hojas {w['profile'].get('paper','A4')} · {s['capacity']} etiquetas por hoja")
        else:self.emission_summary.setText('Revise los datos y el formato antes de generar el PDF.')
        self.emission_panel.show_errors(review['errors'])
        for panel in self.work_panels:
            if panel is not self.emission_panel:panel.show_errors(review['errors'])
        messages=[e['message'] for e in review['errors']]+review['warnings']
        self.emission_feedback.setText('\n'.join(list(dict.fromkeys(messages))[:2])+('\nRevise los demás avisos junto a los campos.' if len(messages)>2 else '') if messages else 'Datos preparados. Compruebe la vista previa antes de emitir. La impresión física no se confirma aquí.')
        self.native_proof.setEnabled(review['proof_allowed'] and not self.native_busy);self.preview_work_button.setEnabled(review['proof_allowed'] and not self.native_busy)
        valid=self.preview_matches(review)
        self.native_issue.setEnabled(review['production_allowed'] and valid and not self.work_preview['result']['warnings'] and not self.native_busy and not self.legacy_process and self.preview_task is None)
        self.native_issue.setToolTip('Confirmar y registrar la emisión definitiva.' if valid else 'Espere la vista previa automática o revise los errores del trabajo.')
        return review
    def refresh_emission_caption(self):
        """Elide the identifier only in compact view; the full identity stays in its tooltip."""
        if not hasattr(self,'emission_document'):return
        full=getattr(self,'_emission_document_full','Seleccione un trabajo o cree uno nuevo.')
        compact=self.height()<650
        self.emission_document.setWordWrap(not compact)
        self.emission_document.setToolTip(full)
        shown=self.emission_document.fontMetrics().elidedText(
            full,Qt.TextElideMode.ElideRight,max(100,self.emission_page.width()-35)
        ) if compact else full
        if self.emission_document.text()!=shown:self.emission_document.setText(shown)

    def verify_work_preview_pdf(self):
        if not self.work_preview or sha256(self.work_preview['path'])!=self.work_preview['sha256']:raise ValueError('La vista previa cambió. Genérela de nuevo.')
    def preview_matches(self,review=None):
        if self.work_preview is None or self.emission_work is None:return False
        review=review or self.work_review
        return bool(review and self.work_preview['stamp']==review.get('token') and self.work_preview['uid']==self.emission_work['uid'] and not self.work_dirty_panel)
    @contextmanager
    def emission_busy(self):
        if self.native_busy:raise ValueError('Hay una operación en curso.')
        self.native_busy=True;self.header.setEnabled(False);self.set_mutations_enabled(False);QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor);QApplication.processEvents()
        try:yield
        finally:QApplication.restoreOverrideCursor();self.native_busy=False;self.header.setEnabled(True);self.set_mutations_enabled(True)
    def operator_error(self,ex):
        if isinstance(ex,WorkCorrupt):return 'El trabajo no se puede leer. Conserve sus archivos y use Recuperar trabajo o una versión compatible.'
        if isinstance(ex,sqlite3.Error):return 'No se ha completado la operación en la base de datos. Revise el historial y recupere el trabajo antes de reintentar.'
        return str(ex).replace(self.api.location(),'la carpeta de datos')
    def emission_error(self,ex):
        self.invalidate_work_preview();w=self.emission_work
        if w and not self.work_dirty_panel:
            try:
                latest=self.api.work.get(w['uid'])
                if latest['phase'] in ('EMITTING','ISSUED'):
                    self.emission_work=latest;self.refresh_work_panels()
                    if latest['phase']=='ISSUED':
                        self.emission_feedback.setText(f"La emisión #{latest['issue_id']} ya está registrada. Consulte Historial; no la repita.");return
            except (ValueError,OSError,sqlite3.Error):pass
        self.refresh_emission_review();message=self.operator_error(ex);self.emission_feedback.setText(message)
        QMessageBox.warning(self,'Operación no completada',message)
    def preview_emission_work(self):
        if self.preview_task is not None:
            self.emission_feedback.setText('Actualizando vista previa. Espere a que termine el cálculo.');return False
        self.preview_timer.stop();self.preview_pending=False
        if self.native_busy or self.legacy_process or not self.emission_work or not self.flush_emission_work():return False
        review=self.refresh_emission_review()
        if not review or not review['proof_allowed']:return False
        try:
            w=self.emission_work;out=self.api.output_path('cache','qt-work-proof-'+uuid.uuid4().hex+'.pdf')
            with self.emission_busy():result=self.api.work.proof(w['uid'],w['generation'],out)
            current=self.api.review_work(w['uid'],w['generation'])
            if current.get('token')!=review.get('token'):raise ValueError('El trabajo o los documentos cambiaron durante la vista previa. Actualícela.')
            self.work_preview={'uid':w['uid'],'stamp':current['token'],'path':out,'sha256':sha256(out),'result':result}
            self.emission_pdf.validator=lambda:self.verify_work_preview_pdf()
            self.emission_compact.setCurrentIndex(1);self.emission_pdf.load(out,'Vista previa · PDF de prueba','PRUEBA · No apto para uso productivo · Los datos y la geometría proceden del motor PDF.')
            self.refresh_emission_review()
            if result['warnings']:
                self.native_issue.setEnabled(False);self.emission_feedback.setText('Revise antes de emitir: '+' · '.join(result['warnings'][:5]))
            return True
        except Exception as ex:self.emission_error(ex);return False
    def proof_emission_work(self):
        if not self.preview_matches() and not self.preview_emission_work():return False
        target,_=QFileDialog.getSaveFileName(self,'Guardar PDF de prueba','PRUEBA_etiquetas.pdf','PDF (*.pdf)')
        if not target:return False
        try:
            self.api.export_proof(self.work_preview['path'],target,self.work_preview['sha256'])
            self.emission_feedback.setText('PDF de prueba guardado con marca visible. No se ha registrado una emisión.');return True
        except Exception as ex:self.emission_error(ex);return False
    def issue_emission_work(self):
        if self.preview_task is not None:return False
        if self.native_busy or self.legacy_process or not self.emission_work or not self.flush_emission_work():return False
        review=self.refresh_emission_review()
        if not self.preview_matches(review):
            self.navigate('emission');self.preview_emission_work();return False
        if not review['production_allowed'] or self.work_preview['result']['warnings']:return False
        w=self.emission_work;s=review['summary']
        text=f"Registrar definitivamente «{w['name']}»?\n\n{self.emission_document.text()}\n{s['physical']} etiquetas · {s['pages']} hojas {w['profile'].get('paper','A4')}\n\nGuardar un borrador no emite. Generar este PDF registra la emisión, sin confirmar la impresión física."
        if QMessageBox.question(self,'Confirmar emisión definitiva',text,QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Yes:return False
        try:
            latest=self.api.review_work(w['uid'],w['generation'])
            if not latest['production_allowed'] or latest.get('token')!=self.work_preview['stamp']:raise ValueError('El trabajo o la documentación cambió después de la vista previa. Vuelva a comprobarlo.')
            if sha256(self.work_preview['path'])!=self.work_preview['sha256']:raise ValueError('La vista previa ha sido modificada. Genérela de nuevo.')
            with self.emission_busy():issued,path,result=self.api.work.issue(w['uid'],w['generation'],self.api.setting('operator'))
            self.emission_work=issued;self.refresh_work_panels();self.emission_pdf.validator=lambda:self.api.history.inspect(issued['issue_id']);self.emission_compact.setCurrentIndex(1);self.emission_pdf.load(path,'PDF definitivo generado','Emisión registrada · Impresión física no confirmada. Imprima al 100 %, sin ajustar a página.')
            self.emission_feedback.setText(f"Emisión #{issued['issue_id']} registrada · {result['physical']} etiquetas · {result['pages']} hojas. El trabajo queda cerrado; copie para preparar otro lote.")
            if hasattr(self,'refresh_native_history'):self.refresh_native_history()
            return True
        except Exception as ex:self.emission_error(ex);return False
    def open_legacy(self,target='maestro',mode='production'):
        if target=='emitir':
            if self.new_emission_work():
                self.navigate('emission')
                if mode=='test':self.preview_emission_work()
            return
        return super().open_legacy(target,mode)
    def new_emission_work(self):
        if self.native_busy or self.legacy_process or not self.flush_emission_work():return
        dialog=QDialog(self);dialog.setWindowTitle('Nuevo trabajo de emisión');dialog.resize(620,330);layout=vbox(dialog)
        layout.addWidget(label('El diseño elegido se fija en un trabajo nuevo.','subtle'));form=QFormLayout()
        revision=QComboBox();variant=QComboBox();name=QLineEdit();name.setPlaceholderText('Identificación del lote o finalidad del trabajo')
        from .window import STATE
        rows=self.api.library_records()
        revisions=[]
        for row in rows:
            for version in self.api.versions(row['id']):
                if version['id'] in revisions:continue
                revisions.append(version['id']);revision.addItem(f"{row['name']} / {version['version']} · {STATE[version['state']][0]}",version['id'])
        def variants(*_):
            variant.clear();variant.addItem('Diseño heredado de la revisión',None)
            for v in self.api.variants(revision.currentData()):variant.addItem(v['code']+' · '+v['name']+' · '+{'DRAFT':'Borrador','PENDING':'Pendiente','APPROVED':'Aprobada','RETIRED':'Retirada'}[v['state']],v['id'])
        revision.currentIndexChanged.connect(variants)
        try:vid,var=self.selected_work_design();revision.setCurrentIndex(max(0,revision.findData(vid)))
        except ValueError:var=None
        variants();variant.setCurrentIndex(max(0,variant.findData(var)))
        form.addRow('Revisión documental',revision);form.addRow('Variante de diseño',variant);form.addRow('Nombre del trabajo',name);layout.addLayout(form)
        error=label('');error.setObjectName('fieldError');layout.addWidget(error)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.button(QDialogButtonBox.StandardButton.Ok).setText('Crear borrador');buttons.button(QDialogButtonBox.StandardButton.Cancel).setText('Cancelar')
        def create():
            try:
                if not name.text().strip():raise ValueError('Indique el nombre del trabajo.')
                self.emission_work=self.api.work.create(revision.currentData(),variant.currentData(),name.text());self.refresh_work_panels();dialog.accept()
            except (ValueError,OSError) as ex:error.setText(self.operator_error(ex))
        buttons.accepted.connect(create);buttons.rejected.connect(dialog.reject);layout.addWidget(buttons);return dialog.exec()==QDialog.DialogCode.Accepted
    def work_options(self):
        menu=QMenu(self);menu.addAction('Recuperar trabajo…',self.recover_emission_work);menu.addAction('Actualizar vínculo documental…',self.refresh_work_binding);menu.exec(self.cursor().pos())
    def paste_work_containers(self):
        if not self.emission_work or not self.flush_emission_work():return
        from ..vessels import parse_tabular_vessels
        text,ok=QInputDialog.getMultiLineText(self,'Pegar datos por recipiente','Nº | Lote | PN | PB | Conservación. Pesos: kg, g o mg; sin unidad = kg. Pegue columnas de Excel:',QApplication.clipboard().text())
        if not ok:return
        try:
            w=self.emission_work;per=parse_tabular_vessels(text,int(w['count']),w['per_container'])
            self.emission_work=self.api.work.save(w['uid'],w['generation'],{'per_container':per});self.refresh_work_panels();self.emission_panel.tabs.setCurrentIndex(1)
        except Exception as ex:self.emission_error(ex)
    def save_emission_profile(self):
        if not self.emission_work or not self.flush_emission_work():return
        if self.emission_work['profile'].get('layout_version'):
            self.emission_panel.design_sheet();return
        name,ok=QInputDialog.getText(self,'Guardar perfil reutilizable','Nombre del perfil:')
        if not ok or not name.strip():return
        try:
            p=profile_numbers(self.emission_work['profile']);p['name']=name.strip();self.api.sheet_plan(p,1)
            if any(r['name']==p['name'] for r in self.api.profile_list()):
                if QMessageBox.question(self,'Actualizar perfil','Actualizar este perfil reutilizable? El diseño documental conserva su aprobación.',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Yes:return
            self.api.add_profile(p)
            for panel in self.work_panels:
                panel.profile_choice.blockSignals(True);panel.profile_choice.clear();panel.profile_choice.addItem('Aplicar perfil guardado…',None)
                for profile in self.api.profile_list():panel.profile_choice.addItem(profile['name'],dict(profile))
                panel.profile_choice.blockSignals(False)
            self.emission_feedback.setText('Perfil guardado. Puede aplicarlo a otros trabajos sin modificar sus diseños.')
        except Exception as ex:self.emission_error(ex)
    def calibrate_emission(self):
        if not self.emission_work or not self.flush_emission_work():return
        try:
            out=self.api.output_path('cache','qt-calibration-'+uuid.uuid4().hex+'.pdf');self.api.calibration(profile_numbers(self.emission_work['profile']),out)
            self.invalidate_work_preview();self.emission_pdf.load(out,'Hoja de calibración','Imprima al 100 %, sin ajustar a página. Compruebe las reglas físicas antes de emitir.');self.refresh_emission_review()
        except Exception as ex:self.emission_error(ex)
    def adapt_emission_layout(self,*_):
        if not hasattr(self,'emission_right'):return
        compact=self.height()<650
        self.emission_compact.setVisible(compact);self.emission_subtitle.setVisible(not compact)
        self.emission_heading.setVisible(not compact)
        self.emission_heading.setStyleSheet('font-size:21px;' if compact else '')
        self.emission_page.layout().setContentsMargins(*([10]*4 if compact else [20]*4));self.emission_page.layout().setSpacing(6 if compact else 10)
        self.emission_panel.set_compact(compact)
        self.emission_check_heading.setVisible(not compact);self.emission_pdf.compact(compact)
        footer_layout=self.emission_footer.layout()
        footer_layout.setContentsMargins(*(10,7,10,7) if compact else (12,12,12,12))
        footer_layout.setSpacing(3 if compact else 5)
        self.emission_summary.setStyleSheet('font-size:13px;' if compact else '')
        for action in (self.native_save,self.native_proof,self.native_options,self.native_issue,self.native_print):
            action.setStyleSheet('padding:6px 10px;' if compact else '')
        self.refresh_emission_caption()
        self.emission_left.setVisible(not compact or self.emission_compact.currentIndex()==0)
        self.emission_right.setVisible(not compact or self.emission_compact.currentIndex()==1)
    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,'emission_split'):self.adapt_emission_layout()
        if hasattr(self,'nav'):self.nav['emission'].setToolTip('Emisión · Centro nativo Qt')
    def closeEvent(self,event):
        if self.preview_task is not None and self.preview_task.isRunning():
            self.statusBar().showMessage('Espere a que termine la vista previa antes de cerrar. No se ha registrado ninguna emisión.')
            event.ignore();return
        self.preview_timer.stop();self.preview_pending=False
        super().closeEvent(event)
