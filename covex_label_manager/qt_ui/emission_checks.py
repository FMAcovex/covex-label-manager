"""R3C acceptance: real Qt on source/frozen Windows, strictly synthetic data."""
import json
import sys
from pathlib import Path
from datetime import date
import fitz
from PySide6.QtWidgets import QApplication,QMessageBox,QFileDialog,QDialog,QLineEdit,QPushButton
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest
from .demo import DemoSession
from .functional import FunctionalWindow
from ..storage import sha256
from ..canonical import digest


def run(report,captures=None):
    app=QApplication.instance() or QApplication([]);app.setStyle('Fusion');session=DemoSession();session.fictional=True
    w=FunctionalWindow(session);w.resize(1560,960);w.show();app.processEvents();api=session.services
    report=Path(report);captures=Path(captures) if captures else report.parent/'r3c-captures';captures.mkdir(parents=True,exist_ok=True)
    result={'synthetic_only':True,'platform':sys.platform,'native_windows_monitor_acceptance':False};checks=[]
    real_question=QMessageBox.question;real_warning=QMessageBox.warning;real_save=QFileDialog.getSaveFileName;unexpected=[]
    def watchdog():
        modal=QApplication.activeModalWidget()
        if modal:unexpected.append(modal.windowTitle()+' '+getattr(modal,'text',lambda:'')());modal.reject()
    timer=QTimer();timer.timeout.connect(watchdog);timer.start(10000)
    def check(condition,name):
        assert condition,name;checks.append(name)
    def capture(name):
        app.processEvents();QTest.qWait(30);assert w.grab().save(str(captures/(name+'.png')))
    def pdf_words(path):
        with fitz.open(path) as doc:return [[(word[4].replace('\xad','-'),*[round(v,2) for v in word[:4]]) for word in page.get_text('words') if word[4].replace('\xad','-').startswith('R3C-')] for page in doc]
    try:
        vid=next(r['version_id'] for r in api.library.entries() if r['state']=='APPROVED');before=dict(api.version(vid));source_hash=sha256(api.asset_path(before['master_pdf']))
        schema=[tuple(r) for r in api._repository.db.execute('SELECT type,name,sql FROM sqlite_master ORDER BY type,name')]
        variant=api.create_variant(vid,'R3C-DEMO','Formato sintético reutilizable','Evaluación del centro Qt','Revisor ficticio')
        variant=api.transition_variant(variant['id'],variant['generation'],'PENDING','Revisor ficticio')
        evidence=Path(session.temp.name)/'external-approval.txt';evidence.write_text('SYNTHETIC EXTERNAL APPROVAL R3C',encoding='utf-8')
        variant=api.approve_variant(variant['id'],variant['generation'],'Revisor externo ficticio','SYNTH-R3C-REF',date.today().isoformat(),evidence,'Operador ficticio')
        work=api.work.create(vid,variant['id'],'Lote R3C · datos ficticios')
        work=api.work.save(work['uid'],1,{'values':{'lote':'R3C-LOTE-SINTETICO','pn':'0,350','pb':'0,500'},'count':'6','copies':'2','selection':'1-3,5-6',
            'profile':dict(work['profile'],width_mm='90',height_mm='80',orientation='portrait',margin_mm='8',gap_mm='3',start_slot='2',crop_marks='1',printer_name='Impresora ficticia'),
            'per_container':{'2':{'lote':'R3C-RECIPIENTE-2','pn':'0,360','pb':'0,510'},'5':{'lote':'R3C-RECIPIENTE-5'}}})
        uid=work['uid'];w.load_emission_work(uid);w.navigate('emission');capture('01-centro-datos-lote')
        panel=w.emission_panel;panel.value_inputs['lote'].setText('R3C-LOTE-QT');panel.changed();QTest.qWait(600)
        check(api.work.get(uid)['values']['lote']=='R3C-LOTE-QT','autosave_from_actual_input')
        check(w.editor_work_panel.value_inputs['lote'].text()=='R3C-LOTE-QT','editor_emission_shared_data')
        panel.tabs.setCurrentIndex(1);capture('02-tabla-recipientes');check(panel.containers.rowCount()==6,'recipient_table')
        panel.tabs.setCurrentIndex(2);capture('03-formato-perfil');check(panel.capture()['profile']['start_slot']=='2','format_kept_separate')
        panel.tabs.setCurrentIndex(0)
        check(w.preview_emission_work(),'native_actual_pdf_preview');capture('04-vista-previa-A4')
        proof=w.work_preview['path'];words=pdf_words(proof);check(bool(words),'preview_contains_actual_work_data')
        check(w.work_preview['result']['physical']==10 and w.work_preview['result']['pages']==2,'A4_selection_copies_start_slot')
        with fitz.open(proof) as pdf:check('PRUEBA' in pdf[0].get_text(),'unambiguous_proof_watermark')
        export=Path(session.temp.name)/'PRUEBA-exportada.pdf';QFileDialog.getSaveFileName=lambda *a,**k:(str(export),'PDF')
        check(w.proof_emission_work() and sha256(export)==sha256(proof) and not api.issues(),'proof_export_no_registration')
        QMessageBox.question=lambda *a,**k:QMessageBox.StandardButton.Cancel
        check(not w.issue_emission_work() and not api.issues(),'definitive_cancel_no_effect')
        saved=api.work.get(uid);w.close();w=FunctionalWindow(session);w.resize(1560,960);w.show();app.processEvents();w.load_emission_work(uid);w.navigate('emission')
        check(api.work.get(uid)==saved,'restart_draft_recovery');check(w.preview_emission_work(),'preview_after_restart')
        QMessageBox.question=lambda *a,**k:QMessageBox.StandardButton.Yes
        check(w.issue_emission_work(),'native_definitive_issue');capture('05-PDF-definitivo-registrado')
        first=w.emission_work['issue_id'];issue=api.issue(first);snapshot=json.loads(issue['design_snapshot_json'])
        check(snapshot['work']['uid']==uid and snapshot['variant_id']==variant['id'] and digest(snapshot)==issue['design_snapshot_sha256'],'immutable_snapshot_and_variant')
        check(pdf_words(api.asset_path(issue['pdf_path']))==words,'preview_and_definitive_text_geometry_match')
        check(not w.issue_emission_work() and len(api.issues())==1,'duplicate_work_issue_blocked')
        w.copy_emission_work();check(w.emission_work['uid']!=uid and w.emission_work['phase']=='DRAFT','independent_copy')
        stale=w.emission_work;api.work.save(stale['uid'],stale['generation'],{'values':dict(stale['values'],lote='R3C-OTHER-PROCESS')})
        p=w.emission_panel;p.value_inputs['lote'].setText('R3C-LOCAL-CONFLICT');p.changed();check(not w.flush_emission_work() and p.value_inputs['lote'].text()=='R3C-LOCAL-CONFLICT','stale_generation_keeps_input')
        w.work_timer.stop();w.work_dirty_panel=None;w.reload_emission_work()
        pending=next(r['version_id'] for r in api.library.entries() if r['state']=='PENDING');draft=api.work.create(pending,name='Pendiente sintético',template=saved)
        w.load_emission_work(draft['uid']);check(w.preview_emission_work() and not w.native_issue.isEnabled(),'pending_proof_without_definitive');capture('06-pendiente-bloqueada')
        w.load_emission_work(uid);w.navigate('history');w.history_table.selectRow(0)
        check(w.stack.currentWidget() is w.history_page and w.preview_native_issue(),'native_history_verified_pdf');capture('07-historial-y-PDF')
        check('R3C-RECIPIENTE-2' in w.history_text['containers'].toPlainText(),'historical_recipient_data')
        report0=api.history.inspect(first)
        _,rp,_=api.history.reproduce(first,'2-3','Rotura ficticia','Operador ficticio',expected_token=report0['token'],proof=True)
        check(len(api.issues())==1 and rp.exists(),'reprint_proof_no_registration')
        # Actual native dialog, actual confirm and production service, no Tk.
        def complete_reprint():
            dialog=QApplication.activeModalWidget()
            if not isinstance(dialog,QDialog):return
            fields=dialog.findChildren(QLineEdit);fields[0].setText('2-3');fields[1].setText('Rotura ficticia durante evaluación')
            next(b for b in dialog.findChildren(QPushButton) if b.text()=='Registrar reimpresión…').click()
        QTimer.singleShot(100,complete_reprint);w.native_reprint()
        check(len(api.issues())==2 and api.issues()[0]['source_issue_id']==first,'native_controlled_reprint');capture('08-reimpresion-controlada')
        check(json.loads(api.issues()[0]['selected_indices'])==[2,3],'original_reprint_numbers')
        check(api.issue(first)['design_snapshot_json']==issue['design_snapshot_json'],'historical_snapshot_preserved')
        w.navigate('emission');w.load_emission_work(uid);check(w.preview_emission_work(),'issued_work_proof_for_geometry_review')
        resolution=[]
        for width,height in [(1920,1080),(1366,768)]:
            scale=w.screen().devicePixelRatio();target=(int(width/scale)-16,int(height/scale)-44);w.resize(*target);app.processEvents()
            check(w.width()<=target[0] and w.height()<=target[1],f'emission_fits_{width}x{height}')
            capture(f'09-centro-{width}x{height}')
            if w.height()<650:
                check(w.emission_compact.isVisible() and w.emission_pdf.view.height()>70,'compact_preview_not_collapsed')
                w.emission_compact.setCurrentIndex(0);app.processEvents();capture(f'10-datos-compactos-{width}x{height}');check(w.emission_left.isVisible() and not w.emission_right.isVisible(),'compact_data_accessible');w.emission_compact.setCurrentIndex(1)
            resolution.append({'target':[width,height],'logical':[w.width(),w.height()],'scale':scale})
        check(dict(api.version(vid))==before and sha256(api.asset_path(before['master_pdf']))==source_hash,'original_master_untouched')
        check([tuple(r) for r in api._repository.db.execute('SELECT type,name,sql FROM sqlite_master ORDER BY type,name')]==schema,'sqlite_v4_schema_unchanged')
        check('tkinter' not in sys.modules,'native_flow_does_not_import_tkinter');check(not unexpected,'no_unexpected_dialogs')
        result.update(ok=True,count=len(checks),checks=checks,resolution=resolution,captures=sorted(p.name for p in captures.glob('*.png')))
    except Exception:
        import traceback
        result.update(ok=False,checks=checks,error=traceback.format_exc());print(result['error'])
    finally:
        timer.stop();QMessageBox.question=real_question;QMessageBox.warning=real_warning;QFileDialog.getSaveFileName=real_save
        w.work_dirty_panel=None;w.dirty=False
        if w.design:w.design.mark_clean()
        w.close();app.processEvents();session.close()
    report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    return 0 if result['ok'] else 1
