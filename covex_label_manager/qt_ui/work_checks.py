"""Native synthetic R3B2+B3 acceptance exercise, source and frozen portable."""
import copy
import json
import sys
from datetime import date
from pathlib import Path
from PySide6.QtWidgets import QApplication,QMessageBox
from PySide6.QtCore import QTimer
from .demo import DemoSession
from .functional import FunctionalWindow
from ..canonical import digest
from ..storage import sha256
from ..qt_legacy import launch_legacy


def run(report,captures=None,verify_bridge=False):
    app=QApplication.instance() or QApplication([]);session=DemoSession();session.fictional=True
    w=FunctionalWindow(session);w.resize(1560,960);w.show();app.processEvents();api=session.services
    report=Path(report);captures=Path(captures) if captures else report.parent/'work-captures';captures.mkdir(parents=True,exist_ok=True)
    unexpected=[]
    def watchdog():
        modal=QApplication.activeModalWidget()
        if modal:unexpected.append(modal.windowTitle()+' '+getattr(modal,'text',lambda:'')());modal.reject()
    timer=QTimer();timer.timeout.connect(watchdog);timer.start(5000)
    def capture(name):app.processEvents();w.grab().save(str(captures/(name+'.png')))
    result={'synthetic_only':True,'platform':sys.platform,'sqlite_version':4}
    try:
        vid=next(r['version_id'] for r in api.library.entries() if r['state']=='APPROVED');w.select_version(vid)
        original=dict(api.version(vid));source=api.asset_path(original['master_pdf']);sourcehash=sha256(source)
        variant=api.create_variant(vid,'WORK-DEMO','Variante sintética reutilizable','Prueba integrada de lote y recipiente','Revisor ficticio')
        variant=api.transition_variant(variant['id'],variant['generation'],'PENDING','Revisor ficticio')
        evidence=Path(session.temp.name)/'approval.txt';evidence.write_text('SYNTHETIC EXTERNAL APPROVAL',encoding='utf-8')
        variant=api.approve_variant(variant['id'],variant['generation'],'Revisor externo ficticio','SYNTH-WORK-REF',date.today().isoformat(),evidence,'Operador ficticio')
        w.selected();w.variant_selector.setCurrentIndex(w.variant_selector.findData(variant['id']))
        work=api.work.create(vid,variant['id'],'Lote sintético B3');w.load_emission_work(work['uid']);w.navigate('emission')
        p=w.emission_panel;p.value_inputs['lote'].setText('QT-SYNTH');p.value_inputs['pn'].setText('0,350');p.value_inputs['pb'].setText('0,500')
        p.inputs['count'].setText('2');p.profile_inputs['width_mm'].setText('100');p.profile_inputs['height_mm'].setText('80');p.changed();assert w.flush_emission_work()
        capture('01-emission-batch')
        p.tabs.setCurrentIndex(1);p.containers.item(1,1).setText('QT-2');p.containers.item(1,2).setText('0,360');p.containers.item(1,3).setText('0,510');assert w.flush_emission_work();capture('02-container-data')
        p.tabs.setCurrentIndex(2);capture('03-format-configuration')
        work=copy.deepcopy(w.emission_work);uid=work['uid'];assert not api.issues()
        w.open_editor();w.show_editor_work();app.processEvents();capture('04-editor-variable-panel')
        assert w.current_variant_id==variant['id'] and not w.editable()
        w.work_dock.hide();w.navigate('emission')
        # Restart controller while keeping the same synthetic local repository.
        w.close();w=FunctionalWindow(session);w.resize(1560,960);w.show();app.processEvents()
        assert w.emission_work is None and api.work.get(uid)==work
        w.load_emission_work(uid);w.navigate('emission');capture('05-recovered-after-restart')
        result['restart_recovered']=True
        if verify_bridge:
            for definitive in (False,True):
                work=api.work.get(uid);api.selected_variant_id=variant['id'];bridge_report=api.output_path('cache','work-bridge-'+str(definitive)+'.json')
                process=launch_legacy(api,'emitir',vid,'production' if definitive else 'test',smoke_report=bridge_report,
                    smoke_issue=definitive,work_uid=uid,work_generation=work['generation'])
                w.legacy_process=process;w.set_mutations_enabled(False)
                assert not w.emission_page.isEnabled() and not w.work_dock.isEnabled()
                assert process.wait(timeout=55)==0,'Bridge failed'
                bridge=json.loads(bridge_report.read_text(encoding='utf-8'));assert bridge['ok'],bridge
                w.legacy_process=None;w.set_mutations_enabled(True);w.load_emission_work(uid)
                loaded=w.emission_work;assert loaded['values']['lote']=='TK-SYNTH' and loaded['per_container']['2']['lote']=='TK-2'
                assert loaded['profile']['offset_x_mm']=='0.5' and loaded['phase']==('ISSUED' if definitive else 'DRAFT')
                result['definitive_bridge' if definitive else 'proof_bridge']=bridge
                capture('06-return-from-tk-issued' if definitive else '06-return-from-tk-draft')
            issue=api.issue(w.emission_work['issue_id']);snap=json.loads(issue['design_snapshot_json'])
            assert snap['work']['uid']==uid and snap['variant_id']==variant['id'] and issue['design_snapshot_sha256']==digest(snap)
            assert len(api.issues())==1
            result['snapshot_sha256']=issue['design_snapshot_sha256'];result['work_issued_once']=True
        else:
            work=api.work.get(uid);out=api.output_path('cache','work-synthetic-proof.pdf');api.work.proof(uid,work['generation'],out)
            result['proof_sha256']=sha256(out)
        assert dict(api.version(vid))==original and sha256(source)==sourcehash
        assert not unexpected,unexpected
        result.update(ok=True,source_unchanged=True,work_uid=uid,variant_id=variant['id'],captures=sorted(p.name for p in captures.glob('*.png')))
    except Exception:
        import traceback
        result.update(ok=False,error=traceback.format_exc());print(result['error'])
    finally:
        timer.stop();w.legacy_process=None;w.work_dirty_panel=None;w.close();app.processEvents();session.close()
    report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    return 0 if result['ok'] else 1
