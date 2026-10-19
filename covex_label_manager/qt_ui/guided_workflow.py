"""R8D task-oriented presentation of the ONE existing recoverable work.

No persistence or emission engine lives here. Review, preview, proof export,
confirmation, definitive issue and printing all use the advanced controllers.
"""
import json
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QScrollArea, QSplitter, QComboBox,QGridLayout,QSizePolicy)
from .window import label, button, vbox, box
from .work import WorkPanel, PHASE
from .pdf_view import EditorPdfPane


def safe_message(message):
    """Operational text only. Private diagnostics retain the actual exception."""
    import re
    text=str(message)
    if re.search(r'[A-Za-z]:\\|\\\\|(?<!\w)/[\w.-]+|Traceback|Error\b|Exception\b|\binvalid\b|\bvalidation\b|\b[0-9a-f]{32,}\b|\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b',text,re.I):
        return 'No se ha completado la operación. Conserve el trabajo y consulte el diagnóstico desde Configuración.'
    return text


HELP = '''Inicio rápido · Cuatro pasos
1. Seleccione etiqueta, revisión y variante. Vigente significa autorizada externamente; pendiente o borrador sólo permiten prueba cuando sus reglas lo admiten.
2. Introduzca los datos requeridos (*). Un recipiente puede tener valores propios; las copias repiten la misma etiqueta. kg/g/mg se convierten según el diseño documental.
3. Compruebe el PDF real, datos, medidas y avisos. Ajustar conserva proporciones y puede dejar margen; Rellenar recorta sólo fondo no crítico. Si se bloquea, cambie área o prepare una variante.
4. Genere PRUEBA / NO GMP o confirme una emisión autorizada. Guardar trabajo no emite; generar PDF no confirma impresión física.

Una variante es un diseño documental alternativo que sigue su propio ciclo de revisión y aprobación externa. Retirada significa sólo consulta: no nueva emisión. Para modificar un diseño aprobado prepare un borrador, nunca cambie el original.
Los ajustes de apariencia temporales impiden la definitiva hasta restablecerlos o completar el ciclo de una variante. El nombre de estado «Aprobado» no concede autorización documental.

Puede continuar trabajos guardados o usar Centro avanzado con el mismo trabajo. Para otro lote use Nueva emisión; no se copian datos críticos automáticamente. La ayuda no sustituye los procedimientos GMP.'''


class GuidedWorkflow:
    def __init__(self, window):
        self.controller=window;self.api=window.api;self.step=0
        self.choices=[];self.displayed_pdf=None;self.resuming=False
        self.home=self.build_home();window.stack.addWidget(self.home)
        self.page=self.build_wizard();window.stack.addWidget(self.page)
        self.help=self.build_help();window.stack.addWidget(self.help)
        brand=window.brand_title.parentWidget().layout().itemAt(0).layout()
        window.brand_title.hide()
        self.home_button=button('COVEX · Inicio',lambda:window.navigate('home'),'nav')
        self.home_button.setAccessibleName('COVEX · Inicio de operaciones')
        self.home_button.setStyleSheet('padding:6px;');brand.insertWidget(0,self.home_button)
        window.nav['home']=self.home_button;self.home_button.setCheckable(True)
        head=window.emission_page.layout().itemAt(0).layout()
        self.assistant_button=button('Asistente',self.resume)
        head.insertWidget(max(0,head.count()-1),self.assistant_button)
        # Keyboard access is scoped; Escape never closes a writer or discards data.
        self.next_shortcut=QShortcut(QKeySequence('Alt+Right'),self.page)
        self.next_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.next_shortcut.activated.connect(self.next_step)
        self.back_shortcut=QShortcut(QKeySequence('Alt+Left'),self.page)
        self.back_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.back_shortcut.activated.connect(self.back)
        self.timer=QTimer(window);self.timer.setInterval(250);self.timer.timeout.connect(self.poll)
        self.timer.start()
        self.refresh_recent()

    def build_home(self):
        page=QWidget();outer=vbox(page,12,8)
        outer.addWidget(label('COVEX · ¿Qué necesita hacer?','title'))
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        content=QWidget();layout=vbox(content,12,8)
        layout.addWidget(label('OPERACIONES HABITUALES','section'))
        row=QHBoxLayout();self.new_button=button('Nueva emisión',self.begin,'primary')
        row.addWidget(self.new_button);row.addWidget(button('Buscar etiqueta',lambda:self.controller.navigate('library')))
        row.addWidget(button('Consultar historial',lambda:self.controller.navigate('history')));layout.addLayout(row)
        layout.addWidget(label('Continuar trabajo · se conservan sus datos; no crea una emisión','subtle'))
        row=QHBoxLayout();self.recent=QComboBox();self.recent.setMinimumContentsLength(10)
        self.recent.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.recent.setAccessibleName('Trabajos guardados recientes');row.addWidget(self.recent,1)
        self.continue_button=button('Continuar trabajo',self.resume_selected);row.addWidget(self.continue_button);layout.addLayout(row)
        layout.addWidget(label('ADMINISTRACIÓN DE DISEÑOS','section'))
        row=QHBoxLayout()
        for title,callback in [('Biblioteca',lambda:self.controller.navigate('library')),
            ('Editor',lambda:self.controller.navigate('editor')),
            ('Revisiones y variantes',self.documents),
            ('Etiquetas de estado',lambda:self.controller.navigate('status-manager'))]:row.addWidget(button(title,callback))
        layout.addLayout(row)
        layout.addWidget(label('CONFIGURACIÓN Y AYUDA','section'))
        row=QHBoxLayout()
        for title,callback in [('Preferencias y diagnósticos',lambda:self.controller.navigate('settings')),
            ('Formatos y perfiles',self.formats),('Inicio rápido',lambda:self.controller.navigate('quick-help'))]:row.addWidget(button(title,callback))
        layout.addLayout(row)
        note=label('La separación visual no otorga permisos ni aprobación GMP. Centro avanzado y compatibilidad conservan sus verificaciones.','subtle');note.setWordWrap(True);layout.addWidget(note)
        layout.addStretch();scroll.setWidget(content);outer.addWidget(scroll,1)
        return page

    def build_help(self):
        page=QWidget();layout=vbox(page)
        layout.addWidget(label('Ayuda · Inicio rápido','title'))
        scroll=QScrollArea();scroll.setWidgetResizable(True)
        text=label(HELP);text.setWordWrap(True);text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        scroll.setWidget(text);layout.addWidget(scroll,1)
        layout.addWidget(button('Volver a Inicio',lambda:self.controller.navigate('home')))
        return page

    def build_wizard(self):
        page=QWidget();layout=vbox(page,10,6)
        self.page_layout=layout;self.compact_header=False
        head=QHBoxLayout();self.wizard_head=head
        self.heading=label('Nueva emisión · Asistente','title');head.addWidget(self.heading,1)
        head.addWidget(button('Ayuda',lambda:self.controller.navigate('quick-help')))
        self.advanced_button=button('Centro avanzado',self.advanced);head.addWidget(self.advanced_button);layout.addLayout(head)
        self.progress=label('1 Seleccionar → 2 Datos → 3 Revisar → 4 Emitir','section');layout.addWidget(self.progress)
        self.identity=label('Seleccione expresamente la etiqueta y su diseño.','subtle');self.identity.setWordWrap(True);layout.addWidget(self.identity)
        self.identity.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred)
        self.steps=QStackedWidget();layout.addWidget(self.steps,1)
        choose=QWidget();cl=vbox(choose,0,6)
        self.search=QLineEdit();self.search.setPlaceholderText('Buscar nombre, código, producto, país, mercado o tipo…')
        self.search.setAccessibleName('Buscar etiqueta para nueva emisión');self.search.textChanged.connect(self.populate)
        cl.addWidget(self.search)
        split=QSplitter();self.results=QTableWidget(0,4)
        self.results.setHorizontalHeaderLabels(['Etiqueta / código','Revisión','Variante','Uso documental'])
        self.results.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.results.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results.verticalHeader().hide();self.results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results.itemSelectionChanged.connect(self.selected);self.results.setAccessibleName('Resultados: etiqueta, revisión, variante y uso')
        split.addWidget(self.results);self.thumbnail=EditorPdfPane(self.api);split.addWidget(self.thumbnail)
        split.setSizes([650,350]);cl.addWidget(split,1);self.steps.addWidget(choose)
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.panel=WorkPanel(self.controller,context='guided');self.controller.work_panels.append(self.panel)
        scroll.setWidget(self.panel);self.steps.addWidget(scroll)
        review=QWidget();rl=vbox(review,0,6)
        row=QHBoxLayout();self.appearance=button('Ajustar apariencia del campo…',self.adjust_appearance)
        row.addWidget(self.appearance);self.state_button=button('Añadir etiqueta de estado',self.edit_status);row.addWidget(self.state_button);rl.addLayout(row)
        self.pdf=EditorPdfPane(self.api);rl.addWidget(self.pdf,1);self.steps.addWidget(review)
        final=box();fl=vbox(final,12,10)
        self.summary=label('Revise primero el PDF real.');self.summary.setWordWrap(True);fl.addWidget(self.summary)
        notice=label('Prueba: no registra emisión. Definitiva: exige autorización documental y registra historial. Imprimir requiere una acción separada; generar PDF no confirma impresión física.','subtle');notice.setWordWrap(True);fl.addWidget(notice)
        actions=QGridLayout();self.proof_button=button('Generar PDF de prueba',self.proof)
        self.issue_button=button('Emitir etiqueta definitiva',self.issue,'primary')
        self.open_button=button('Abrir PDF generado',self.open_result);self.open_button.setEnabled(False)
        self.print_button=button('Imprimir PDF registrado…',self.print_result)
        self.history_button=button('Consultar historial',lambda:self.controller.navigate('history'))
        self.another_button=button('Preparar otra emisión',self.begin)
        for i,b in enumerate((self.proof_button,self.issue_button,self.open_button,self.print_button,self.history_button,self.another_button)):actions.addWidget(b,i//2,i%2)
        fl.addLayout(actions);fl.addStretch();final_scroll=QScrollArea();final_scroll.setWidgetResizable(True);final_scroll.setWidget(final);self.steps.addWidget(final_scroll)
        self.feedback=label('');self.feedback.setWordWrap(True);self.feedback.setObjectName('fieldError');layout.addWidget(self.feedback)
        row=QHBoxLayout();self.cancel_button=button('Volver a Inicio',lambda:self.controller.navigate('home'));row.addWidget(self.cancel_button)
        self.back_button=button('Anterior',self.back);row.addWidget(self.back_button);row.addStretch()
        self.next_button=button('Continuar con esta etiqueta',self.next_step,'primary');row.addWidget(self.next_button);layout.addLayout(row)
        QWidget.setTabOrder(self.search,self.results);QWidget.setTabOrder(self.results,self.next_button)
        return page

    def editable_operation(self):
        w=self.controller
        return not w.native_busy and not w.legacy_process and not getattr(w,'_runtime_shutting_down',False)

    def prepare_navigation(self):
        return self.editable_operation() and self.controller.flush_emission_work() and self.controller.resolve_work()

    def begin(self):
        if not self.prepare_navigation():return False
        # Do not replace an existing work until an explicit design is chosen.
        self.resuming=False;self.set_step(0);self.populate();self.controller.navigate('guided')
        self.search.setFocus();return True

    def populate(self,*_):
        query=self.search.text().strip().casefold();previous=self.selection()
        candidates=[];seen=set()
        for row in self.api.library_records():
            rid=row['version_id']
            if rid in seen:continue
            seen.add(rid)
            text=' '.join(str(v) for v in row.values()).casefold()
            for variant in [None,*self.api.variants(rid)]:
                variant=dict(variant) if variant else None
                if query and query not in text+' '+str(variant or {}).casefold():continue
                candidates.append((dict(row),variant))
        self.results.blockSignals(True);self.results.setRowCount(len(candidates));self.choices=candidates
        for i,(row,variant) in enumerate(candidates):
            production,_=self.api.eligibility(row['version_id'],True,variant['id'] if variant else None)
            proof,_=self.api.eligibility(row['version_id'],False,variant['id'] if variant else None)
            state='Vigente · emisión autorizada' if production else ('Sólo prueba · no autorizada' if proof else 'Bloqueada · sólo consulta')
            for col,text in enumerate([row['name']+' · '+str(row.get('code','')),str(row['version']),variant['code'] if variant else 'Diseño de revisión',state]):
                item=QTableWidgetItem(text);item.setToolTip(text);self.results.setItem(i,col,item)
        self.results.clearSelection();self.results.setCurrentCell(-1,-1);self.results.blockSignals(False)
        match=next((i for i,(row,var) in enumerate(candidates) if previous==(row['version_id'],var['id'] if var else None)),None)
        # Auto-select only a single unequivocal current result. Never a draft.
        if match is None and len(candidates)==1:
            row,var=candidates[0]
            if self.api.eligibility(row['version_id'],True,var['id'] if var else None)[0]:match=0
        if match is not None:self.results.selectRow(match)
        self.selected()

    def selection(self):
        i=self.results.currentRow() if hasattr(self,'results') else -1
        if 0<=i<len(self.choices):
            row,var=self.choices[i];return row['version_id'],var['id'] if var else None
        return None

    def selected(self):
        choice=self.selection();self.next_button.setEnabled(False)
        if not choice:self.thumbnail.clear('Elija una revisión y variante. Si hay alternativas no se seleccionan silenciosamente.');return
        try:
            version=self.api.resolved_design(*choice);ok,_=self.api.eligibility(choice[0],False,choice[1])
            self.next_button.setEnabled(ok and self.editable_operation())
            self.thumbnail.load(self.api.open_document(choice[0]),'Documento de referencia','Fuente fija. El PDF con sus datos se revisa en el paso 3.')
            self.show_identity(version['name']+' · Revisión '+version['version']+' · '+('Variante '+self.api.variant(choice[1])['code'] if choice[1] else 'Diseño de revisión')+' · '+('Vigente' if self.api.eligibility(choice[0],True,choice[1])[0] else 'Sólo prueba o consulta'))
        except (ValueError,OSError,RuntimeError) as ex:self.failure(ex)

    def next_step(self):
        if not self.prepare_navigation():return False
        w=self.controller
        try:
            if self.step==0:
                choice=self.selection()
                if choice is None:return False
                ok,_=self.api.eligibility(choice[0],False,choice[1])
                if not ok:raise PermissionError('Esta revisión está retirada o no se puede utilizar. Seleccione una revisión vigente.')
                v=self.api.version(choice[0])
                current=w.emission_work
                if not (self.resuming and current and current['binding']['revision_id']==choice[0] and current['binding']['variant_id']==choice[1]):
                    w.emission_work=self.api.work.create(choice[0],choice[1],v['name']+' · preparación')
                    w.refresh_work_panels()
                self.resuming=True
            elif self.step==1:
                review=w.refresh_emission_review()
                # Documentary errors allow proof if the service permits it;
                # actual invalid input never skips the field review.
                if not review or not review['proof_allowed'] or any(e['target']!='document' for e in review['errors']):
                    self.sync(review);return False
            elif self.step==2:
                review=w.refresh_emission_review()
                if not w.preview_matches(review):
                    w.schedule_preview();self.feedback.setText('Espere el PDF actualizado antes de continuar.');return False
            if self.step<3:self.set_step(self.step+1)
            if self.step==2:w.schedule_preview()
            self.sync(w.work_review);return True
        except (ValueError,OSError,RuntimeError) as ex:self.failure(ex);return False

    def set_step(self,index):
        self.step=index;self.steps.setCurrentIndex(index)
        self.progress.setText(f'Paso {index+1} de 4 · '+['Seleccionar etiqueta','Introducir datos','Revisar etiqueta','Emitir o generar prueba'][index])
        self.back_button.setEnabled(index>0);self.next_button.setVisible(index<3)
        self.next_button.setText(['Continuar con esta etiqueta','Revisar etiqueta','Continuar a emisión',''][index])
        self.next_button.setEnabled(index>0 or self.selection() is not None)
        self.feedback.setText('')

    def back(self):
        if self.step and self.prepare_navigation():
            # Step 1 remains bound to the existing work; replacing it creates
            # a NEW work only after another explicit Continue action.
            self.set_step(self.step-1)
            if self.step==0:self.populate()
            else:self.sync(self.controller.work_review)

    def resume_selected(self):
        uid=self.recent.currentData()
        if not uid or not self.prepare_navigation():return False
        if self.controller.load_emission_work(uid):return self.resume()
        return False

    def resume(self):
        if not self.prepare_navigation():return False
        if not self.controller.emission_work:return self.begin()
        self.resuming=True;self.panel.display(self.controller.emission_work)
        self.set_step(3 if self.controller.emission_work['phase']=='ISSUED' else 1)
        self.controller.navigate('guided');self.sync(self.controller.refresh_emission_review());return True

    def advanced(self):
        if self.prepare_navigation():self.controller.navigate('emission')

    def edit_status(self):
        if self.prepare_navigation():self.set_step(1);self.panel.tabs.setCurrentIndex(3)

    def adjust_appearance(self):
        if self.prepare_navigation():self.controller.adjust_field_appearance();self.sync(self.controller.work_review)

    def sync(self,review=None):
        w=self.controller;work=w.emission_work
        if not work or self.step==0:return
        b=work['binding'];version=self.api.version(b['revision_id']);variant=self.api.variant(b['variant_id']) if b['variant_id'] else None
        identity=version['name']+' · Revisión '+version['version']+' · '+('Variante '+variant['code'] if variant else 'Diseño de revisión')
        self.show_identity(identity+' · '+PHASE[work['phase']])
        review=review or w.work_review
        if not review:return
        s=review.get('summary');profile=work['profile'];state=work['status']
        details=identity+'\nLote: '+work['values'].get('lote','(no definido por el diseño)')
        if s:details+=f"\n{s['selected']} recipientes · {s['copies']} copias · {s['physical']} etiquetas · {s['pages']} hojas {profile.get('paper','A4')}\nTamaño {s['width_mm']:g} × {s['height_mm']:g} mm"
        details+='\nEstado: '+{'ninguna':'Sin etiqueta de estado','sin_analizar':'Sin analizar','aprobado':'Aprobado (tipo, no aprobación)','rechazado':'Rechazado'}.get(state.get('kind'),'Sin seleccionar')
        details+=' · '+{'fit':'Ajustar sin deformar','fill':'Rellenar protegido'}.get(state.get('composition',{}).get('mode'),'Composición histórica')
        if state.get('revision_uid'):
            rec=self.api.status_catalog.get(state['revision_uid']);details+=' · Revisión estado '+rec['revision']
        self.summary.setText(details)
        messages=[safe_message(e['message']) for e in review['errors']]+[safe_message(x) for x in review['warnings']]
        if work['phase']=='ISSUED':messages=[f"Emisión #{work['issue_id']} registrada. Impresión física no confirmada. Para otro lote prepare otra emisión."]
        self.feedback.setText('\n'.join(dict.fromkeys(messages))[:1400])
        ready=self.editable_operation() and w.preview_task is None
        self.proof_button.setEnabled(bool(w.native_proof.isEnabled() and ready))
        self.issue_button.setEnabled(bool(w.native_issue.isEnabled() and ready))
        self.issue_button.setToolTip(w.native_issue.toolTip() if review['production_allowed'] else '\n'.join(messages) or 'Esta revisión no está autorizada. Genere una prueba o seleccione una revisión vigente.')
        self.print_button.setEnabled(bool(w.native_print.isEnabled() and ready))
        self.print_button.setToolTip('Requiere una emisión registrada. Generar un PDF no confirma la impresión física.')
        self.appearance.setEnabled(bool(w.appearance_button.isEnabled() and ready))
        preview=w.work_preview
        if preview and w.preview_matches(review):
            stamp=(work['uid'],preview['stamp'],preview['sha256'])
            if self.displayed_pdf!=stamp:
                self.pdf.validator=w.verify_work_preview_pdf
                physical=(f"{s['width_mm']:.2f} × {s['height_mm']:.2f} mm · {s['physical']} etiquetas · {s['pages']} hojas {profile.get('paper','A4')}" if s else '')
                self.pdf.load(preview['path'],'PDF real · PRUEBA / NO GMP',physical+' · '+details.split('\n')[-1])
                if preview['result'].get('composition'):
                    from ..status_scaling import describe
                    self.pdf.note.setText(self.pdf.note.text()+'\n'+describe(preview['result']['composition'][0]))
                self.displayed_pdf=stamp
        elif work['phase']!='ISSUED':
            note=safe_message(w.emission_pdf.note.text())
            self.displayed_pdf=None;self.pdf.clear(note)
            if note.startswith(('Revise errores','PDF bloqueado')):
                self.feedback.setText('No se ha generado el PDF. '+note+' Los datos permanecen en el trabajo; corrija el campo o utilice otra variante autorizada.')
        self.open_button.setEnabled(bool((work['phase']=='ISSUED' and work.get('issue_id')) or w.preview_matches(review)))

    def poll(self):
        w=self.controller
        if getattr(w,'_runtime_shutting_down',False):self.timer.stop();return
        if w.stack.currentWidget() is self.page:
            self.adapt()
            try:self.sync(w.work_review)
            except (ValueError,OSError,RuntimeError) as ex:self.failure(ex)

    def adapt(self):
        compact=self.controller.height()<650
        if compact!=self.compact_header:
            self.compact_header=compact;self.heading.setVisible(not compact)
            if compact:
                self.page_layout.removeWidget(self.progress);self.wizard_head.insertWidget(0,self.progress,1)
            else:
                self.wizard_head.removeWidget(self.progress);self.page_layout.insertWidget(1,self.progress)
        self.identity.setWordWrap(not compact)

    def show_identity(self,text):
        self.identity.setToolTip(text)
        shown=self.identity.fontMetrics().elidedText(text,Qt.TextElideMode.ElideRight,max(100,self.page.width()-25)) if self.compact_header else text
        self.identity.setText(shown)

    def refresh_recent(self):
        selected=self.recent.currentData();self.recent.clear()
        for work in self.api.work.list():
            self.recent.addItem(work['name']+' · '+PHASE[work['phase']],work['uid'])
        if selected:self.recent.setCurrentIndex(self.recent.findData(selected))
        self.continue_button.setEnabled(self.recent.count()>0)

    def refresh(self):
        self.refresh_recent();self.displayed_pdf=None

    def proof(self):
        if not self.prepare_navigation():return False
        result=self.controller.proof_emission_work();self.sync(self.controller.work_review)
        if result:self.feedback.setText('PDF de prueba guardado · PRUEBA / NO GMP. No se ha registrado una emisión.')
        return result

    def print_result(self):
        result=self.controller.print_emission_pdf()
        self.feedback.setText(safe_message(self.controller.emission_feedback.text()))
        return result

    def issue(self):
        if not self.prepare_navigation():return False
        result=self.controller.issue_emission_work();self.sync(self.controller.work_review)
        if result:
            self.pdf.validator=lambda:self.api.history.inspect(self.controller.emission_work['issue_id'])
            self.pdf.load(self.controller.emission_pdf.path,'PDF definitivo registrado','La impresión física no está confirmada.')
        return result

    def open_result(self):
        work=self.controller.emission_work
        if not work:return False
        if work['phase']=='ISSUED':
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QDesktopServices
            try:
                record=self.api.history.inspect(work['issue_id'])
                return QDesktopServices.openUrl(QUrl.fromLocalFile(str(record['path'])))
            except (ValueError,OSError,RuntimeError) as ex:self.failure(ex);return False
        return self.pdf.open_pdf()

    def failure(self,ex):
        from ..diagnostics import error
        error('operation_error',ex)
        self.feedback.setText('No se ha completado la operación. '+self.controller.operator_error(ex)+' Los cambios que no se hayan podido guardar siguen en pantalla. No repita una emisión sin consultar Historial.')
        self.issue_button.setEnabled(False)

    def documents(self):
        self.controller.navigate('library');self.controller.show_access('document')

    def formats(self):
        if not self.controller.emission_work:
            self.begin();self.feedback.setText('Seleccione una etiqueta. Sus formatos y perfiles estarán en «Formato y opciones adicionales» del paso 2.');return
        if self.resume():self.panel.tabs.setCurrentIndex(2)

    def navigate(self,key):
        pages={'home':self.home,'guided':self.page,'quick-help':self.help}
        if key not in pages:return False
        if not self.prepare_navigation():return True
        self.controller.stack.setCurrentWidget(pages[key]);self.controller.work_dock.hide()
        for name,control in self.controller.nav.items():control.setChecked(name=='home')
        if key=='home':self.refresh_recent()
        return True
