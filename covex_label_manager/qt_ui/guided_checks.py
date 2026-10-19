"""Synthetic R8D source/frozen acceptance and reproducible interaction traces."""
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import traceback


def run(report,capture=None,*,baseline=False,source_commit=None):
    import fitz
    from PySide6.QtCore import Qt,QSize,QTimer,QElapsedTimer,QCoreApplication,QEvent
    from PySide6.QtWidgets import QApplication,QMessageBox,QDialog,QLineEdit,QPushButton
    from PySide6.QtTest import QTest
    from .demo import DemoSession
    from .functional import FunctionalWindow
    from .editor_ux_checks import present_viewport
    app=QApplication.instance() or QApplication([]);app.setStyle('Fusion')
    session=DemoSession();session.fictional=True;w=FunctionalWindow(session)
    api=session.services;records=[];pdfs=[];traces=[];actions=[]
    report=Path(report);out=Path(capture) if capture else report.with_suffix('')
    out.mkdir(parents=True,exist_ok=True)
    result=dict(ok=False,baseline=baseline,synthetic_only=True,source_commit=source_commit,
                os=sys.platform,qt_platform=app.platformName(),scale=float(os.environ.get('QT_SCALE_FACTOR','1')),
                captures=records,pdfs=pdfs,tasks=traces)
    def settle():
        for _ in range(4):app.processEvents()
    def snapshot(name):
        settle();path=out/(name+'.png');assert w.grab().save(str(path))
        records.append(dict(view=name,size=[w.width(),w.height()],sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        print('R8D CAPTURE',name,w.width(),w.height(),flush=True)
    def click(control,name):
        assert control.isEnabled(),name
        action=dict(action=name,kind='activation');actions.append(action)
        QTest.mouseClick(control,Qt.MouseButton.LeftButton);settle()
        return action
    def edit(control,text,name):
        actions.append(dict(action=name,kind='edit'))
        control.setFocus();QTest.keyClick(control,Qt.Key.Key_A,Qt.KeyboardModifier.ControlModifier)
        QTest.keyClicks(control,text);settle()
    def trace(task,initial):
        traces.append(dict(task=task,initial=initial,actions=list(actions),count=len(actions),
                           screens=sum(a['kind']=='screen' for a in actions),
                           dialogs=sum(a['kind']=='dialog' for a in actions)))
        actions.clear()
    def yes():
        modal=app.activeModalWidget()
        if isinstance(modal,QMessageBox):
            actions.append(dict(action='Confirmar registro',kind='dialog'))
            QTest.mouseClick(modal.button(QMessageBox.StandardButton.Yes),Qt.MouseButton.LeftButton)
        else:QTimer.singleShot(20,yes)
    def wait_preview():
        clock=QElapsedTimer();clock.start()
        while (w.preview_task is not None or not w.preview_matches()) and clock.elapsed()<20000:
            app.processEvents();QTest.qWait(10)
        assert w.preview_matches() and w.preview_task is None,w.emission_feedback.text()
    def review():
        if baseline:
            # R8C already has automatic previews. Wait for its disposable
            # reader before invoking the existing manual button, as instructed
            # by the UI. Waiting is not an additional user action.
            w.preview_timer.stop();w.preview_pending=False
            clock=QElapsedTimer();clock.start()
            while w.preview_task is not None and clock.elapsed()<20000:
                app.processEvents();QTest.qWait(10)
            assert w.preview_task is None
            click(w.preview_work_button,'Actualizar PDF real')
        else:
            click(g.next_button,'Revisar etiqueta');actions[-1]['kind']='screen'
            wait_preview();g.sync(w.work_review)
        assert w.preview_matches(),w.emission_feedback.text()
    def task_work(name,values=None):
        # Benchmark begins with an explicitly bound, blank work in data view.
        # Binding/search itself is exercised/captured separately below.
        work=api.work.create(approved,name='SYNTHETIC-R8D-'+name)
        if values:work=api.work.save(work['uid'],work['generation'],{'values':values})
        w.emission_work=work;w.refresh_work_panels()
        if baseline:w.navigate('emission')
        else:g.resume()
        w.preview_timer.stop();w.preview_pending=False
        actions.clear();return w.emission_panel if baseline else g.panel
    try:
        approved=next(v['id'] for v in api.versions(w.row['id']) if v['state']=='APPROVED')
        original=dict(api.version(approved));g=None if baseline else w.guided
        from ..status_design import make_layout
        source=session.root/'SYNTHETIC-R8D-state.pdf'
        with fitz.open() as doc:
            page=doc.new_page(width=200,height=100);page.draw_rect(page.rect,fill=(.25,.8,.4),color=None)
            page.insert_text((80,30),'SYN',fontsize=8);doc.save(source)
        design=make_layout(source,'aprobado')
        design['fields']=[dict(key='lote',label='Lote',rect=[75,40,125,60],font_size=8.,bold=False,required=True)]
        status_uid=api.status_catalog.import_many(source,[dict(kind='aprobado',revision='SYN-00',layout=design)])[0]
        api.status_catalog.submit(status_uid);api.status_catalog.approve(status_uid,'SYN QA','SYNTHETIC EXTERNAL FIXTURE ONLY',confirmation=True)
        for viewport in (1366,1920):
            scale=result['scale'];size=QSize(math.floor(viewport/scale),math.floor((768 if viewport==1366 else 1080)/scale)-40)
            present_viewport(w,size,settle)
            if baseline:w.navigate('library');snapshot(f'{viewport}-library')
            else:
                w.navigate('home');snapshot(f'{viewport}-home');click(g.new_button,'Nueva emisión')
                snapshot(f'{viewport}-select')
                index=next(i for i,(row,var) in enumerate(g.choices) if row['version_id']==approved and var is None)
                item=g.results.item(index,0);g.results.scrollToItem(item);settle()
                QTest.mouseClick(g.results.viewport(),Qt.MouseButton.LeftButton,pos=g.results.visualItemRect(item).center())
                assert g.selection()==(approved,None)
                click(g.next_button,'Continuar con etiqueta');assert g.step==1
                assert w.emission_work['binding']['revision_id']==approved
            panel=task_work('single')
            edit(panel.value_inputs['lote'],'SYN-R8D','Introducir lote')
            review()
            if not baseline:
                snapshot(f'{viewport}-review');click(g.next_button,'Continuar a emisión');actions[-1]['kind']='screen'
                snapshot(f'{viewport}-issue')
            QTimer.singleShot(20,yes)
            click(w.native_issue if baseline else g.issue_button,'Emitir definitiva')
            assert w.emission_work['phase']=='ISSUED' and w.emission_work['issue_id']
            issued=w.emission_work;historical=api.history.inspect(issued['issue_id']);saved=historical['path'].read_bytes()
            trace('producto_lote','Trabajo nuevo ya vinculado; pantalla de datos; sólo falta lote')
            proof=out/f'{viewport}-registered.pdf';proof.write_bytes(saved)
            with fitz.open(proof) as doc:
                assert 'SYN-R8D' in doc[0].get_text() and 'PRUEBA' not in doc[0].get_text()
                pdfs.append(dict(name=proof.name,sha256=hashlib.sha256(saved).hexdigest(),pages=len(doc)))
            # Multiple containers, values particular to the second vessel.
            panel=task_work('multiple',{'lote':'SYN-COMMON','pn':'350 g','pb':'500000 mg'})
            edit(panel.inputs['count'],'2','Número de recipientes')
            actions.append(dict(action='Datos por recipiente',kind='screen'))
            panel.tabs.setCurrentIndex(1);settle();assert panel.containers.rowCount()==2
            cell=panel.containers.item(1,1);panel.containers.scrollToItem(cell)
            rect=panel.containers.visualItemRect(cell)
            QTest.mouseClick(panel.containers.viewport(),Qt.MouseButton.LeftButton,pos=rect.center())
            QTest.mouseDClick(panel.containers.viewport(),Qt.MouseButton.LeftButton,pos=rect.center());settle()
            editor=next((e for e in panel.containers.findChildren(QLineEdit) if e.isVisible()),None)
            assert editor is not None
            edit(editor,'SYN-SECOND','Lote particular recipiente 2');QTest.keyClick(editor,Qt.Key.Key_Tab);settle()
            assert panel.containers.item(1,1).text()=='SYN-SECOND',repr(panel.containers.item(1,1).text())
            assert w.flush_emission_work();review()
            with fitz.open(w.work_preview['path']) as doc:
                text=''.join(page.get_text() for page in doc)
                assert 'SYN-COMMON' in text and 'SYN-SECOND' in text,(text,w.emission_work['per_container'])
            if not baseline:
                g.back();snapshot(f'{viewport}-data')
                assert g.panel.value_inputs['lote'].text()=='SYN-COMMON'
            trace('varios_recipientes','Trabajo vinculado con valores comunes; cambiar cantidad y lote recipiente 2, revisar PDF')
            # Explicit revision selection in the existing real catalogue.
            panel=task_work('status',{'lote':'SYN-STATE'})
            actions.append(dict(action='Añadir etiqueta de estado',kind='screen'));panel.tabs.setCurrentIndex(3)
            panel.status_kind.setCurrentIndex(panel.status_kind.findData('aprobado'))
            actions.append(dict(action='Tipo Aprobado',kind='selection'))
            panel.status_revision.setCurrentIndex(panel.status_revision.findData(status_uid))
            actions.append(dict(action='Revisión de estado autorizada',kind='selection'))
            panel.placement.setCurrentIndex(panel.placement.findData('independiente'))
            actions.append(dict(action='Estado independiente',kind='selection'))
            panel.composition.setCurrentIndex(panel.composition.findData('fit'))
            actions.append(dict(action='Ajustar sin deformar',kind='selection'))
            assert w.flush_emission_work();review()
            assert w.emission_work['status']['kind']=='aprobado'
            trace('anadir_estado','Trabajo vinculado con lote; seleccionar tipo, revisión, ubicación y composición, revisar PDF')
            # Recovery uses the actual list/open/continue controls.
            pending=w.emission_work;w.navigate('emission' if baseline else 'home');actions.clear()
            choice=w.emission_panel.choice if baseline else g.recent
            choice.setCurrentIndex(choice.findData(pending['uid']));actions.append(dict(action='Elegir trabajo guardado',kind='selection'))
            if baseline:w.emission_panel.open_selected();actions.append(dict(action='Abrir trabajo',kind='activation'))
            else:click(g.continue_button,'Continuar trabajo');actions[-1]['kind']='screen'
            assert w.emission_work['uid']==pending['uid'] and w.emission_work['values']==pending['values']
            trace('recuperar_trabajo','Selector de trabajos visible con el borrador guardado en disco')
            w.navigate('history');actions.clear();w.refresh_native_history()
            row=next(r for r in range(w.history_table.rowCount()) if w.history_table.item(r,0).data(Qt.ItemDataRole.UserRole)==issued['issue_id'])
            w.history_table.selectRow(row);actions.append(dict(action='Elegir emisión original',kind='selection'))
            assert w.preview_native_issue();actions.append(dict(action='Verificar PDF histórico',kind='activation'))
            # Real dialog, human reason and confirmation, not a substitute for
            # the actual historical service integration.
            def fill_reprint():
                dialog=app.activeModalWidget()
                if not isinstance(dialog,QDialog) or not dialog.windowTitle().startswith('Reimpresión controlada'):
                    QTimer.singleShot(20,fill_reprint);return
                fields=dialog.findChildren(QLineEdit)
                edit(fields[1],'SYNTHETIC R8D REPRINT','Motivo de reimpresión')
                control=next(b for b in dialog.findChildren(QPushButton) if b.text()=='Registrar reimpresión…')
                QTimer.singleShot(20,yes);click(control,'Registrar reimpresión')
            QTimer.singleShot(20,fill_reprint)
            click(w.reprint_button,'Reimpresión controlada')['kind']='dialog'
            pk=w.history_id;assert pk!=issued['issue_id']
            path=api.history.inspect(pk)['path']
            assert api.issue(pk)['source_issue_id']==issued['issue_id'] and historical['path'].read_bytes()==saved
            with fitz.open(path) as reprint,fitz.open(proof) as first:
                assert reprint[0].get_pixmap().samples==first[0].get_pixmap().samples
            trace('historial_reimpresion','Historial visible; localizar original, verificar PDF, indicar motivo y confirmar reimpresión')
            snapshot(f'{viewport}-history')
            w.navigate('emission');snapshot(f'{viewport}-advanced')
            if not baseline:
                same=json.loads(json.dumps(w.emission_work));g.resume()
                assert w.emission_work==same
            assert w.size()==size
        assert dict(api.version(approved))==original
        result.update(ok=True,sqlite_v4=api._repository.db.execute('PRAGMA user_version').fetchone()[0]==4,
                      integrity=api._repository.db.execute('PRAGMA integrity_check').fetchone()[0]=='ok',
                      four_steps=not baseline,same_work=not baseline,exact_viewports=True,
                      approved_revision_unchanged=True,registered_pdf_verified=True,reprint_verified=True)
    except Exception as ex:
        result['error']=repr(ex);result['traceback']=traceback.format_exc();print(result['traceback'],flush=True)
    finally:
        try:
            w.shutdown_runtime();w.close();assert not w.isVisible()
            result['normal_start_close']=True;w.deleteLater()
            QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete);app.processEvents();session.close()
        except Exception as ex:result['ok']=False;result['shutdown_error']=repr(ex)
        report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    return 0 if result['ok'] else 1
