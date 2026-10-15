"""Operate/capture the real Qt variant UI with generated fictional artwork only."""
from types import SimpleNamespace
import copy
import json
import os
import sys
from datetime import date
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication,QMessageBox
from covex_label_manager.qt_ui.demo import DemoSession
from covex_label_manager.qt_ui.functional import FunctionalWindow
from covex_label_manager.qt_legacy import launch_legacy


def run(report,capture=None,verify_bridge=False):
    a=SimpleNamespace(report=Path(report),capture=Path(capture) if capture else Path(report).parent/'variant-captures',verify_bridge=verify_bridge)
    app=QApplication.instance() or QApplication([]);session=DemoSession();session.fictional=True
    window=FunctionalWindow(session);window.resize(1560,960);window.show();app.processEvents()
    api=session.services;api.set_setting('operator','Operador ficticio');a.capture.mkdir(parents=True,exist_ok=True);results={}
    def capture(name):
        app.processEvents();window.grab().save(str(a.capture/(name+'.png')))
    unexpected=[]
    def watchdog():
        modal=QApplication.activeModalWidget()
        if modal:
            unexpected.append(modal.windowTitle()+' '+getattr(modal,'text',lambda:'' )());modal.reject()
    timer=QTimer();timer.timeout.connect(watchdog);timer.start(5000)
    try:
        revision=next(r for r in api.library.entries() if r['state']=='APPROVED');vid=revision['version_id'];window.select_version(vid)
        before=dict(api.version(vid));row=api.create_variant(vid,'BOTTLE-DEMO','Envase sintético','Formato reutilizable para demostración','Revisor ficticio')
        window.selected();window.variant_selector.setCurrentIndex(window.variant_selector.findData(row['id']));window.open_editor();app.processEvents()
        assert window.current_variant_id==row['id'] and window.editable()
        candidate=copy.deepcopy(window.design.state);candidate['fields'][0]['font_pt']=11
        assert window.command('Cambio sintético de tipografía',candidate);assert window.save_work()
        assert dict(api.version(vid))==before;capture('01-draft-editor')
        row=api.variant(row['id']);row=api.transition_variant(row['id'],row['generation'],'PENDING','Revisor ficticio');window.reload_variant()
        assert not window.editable() and not window.save_button.isEnabled();capture('02-pending-frozen')
        # Capture an actual approval form before cancelling; then register the
        # fictional external evidence through the same public application service.
        def modal_capture(name='03-external-approval-dialog'):
            modal=QApplication.activeModalWidget();assert modal is not None
            modal.grab().save(str(a.capture/(name+'.png')));modal.reject()
        QTimer.singleShot(200,modal_capture);window.approve_variant_ui()
        evidence=Path(session.temp.name)/'synthetic-external-approval.txt';evidence.write_text('SYNTHETIC EXTERNAL DOCUMENTARY APPROVAL',encoding='utf-8')
        row=api.approve_variant(row['id'],row['generation'],'Revisor externo ficticio','DEMO-APPROVAL-001',date.today().isoformat(),evidence,'Operador ficticio')
        window.reload_variant();assert not window.editable();capture('04-approved-read-only')
        other=api.create_variant(vid,'OTHER-DEMO','Otro envase sintético','Segunda variante coexistente','Revisor ficticio')
        other=api.transition_variant(other['id'],other['generation'],'PENDING','Revisor ficticio')
        other=api.approve_variant(other['id'],other['generation'],'Revisor externo ficticio','DEMO-APPROVAL-002',date.today().isoformat(),evidence,'Operador ficticio')
        derived=api.create_variant(vid,'DERIVED-DEMO','Derivada sintética','Derivación explícita sin heredar aprobación','Revisor ficticio',row['id'])
        assert derived['approved_by'] is None and derived['state']=='DRAFT'
        window.selected();window.navigate('library');capture('05-library-variants')
        QTimer.singleShot(200,lambda:modal_capture('06-document-comparison'));window.compare_variant()
        if a.verify_bridge:
            api.selected_variant_id=row['id'];report=api.output_path('cache','variant-bridge-smoke.json')
            proc=launch_legacy(api,'emitir',vid,'test',report)
            assert proc.wait(timeout=60)==0
            bridge=json.loads(report.read_text());assert bridge['selected_variant']==row['id'] and bridge['no_definitive_issue'];results['legacy_bridge']=bridge
            definitive=api.output_path('cache','variant-bridge-definitive.json')
            proc=launch_legacy(api,'emitir',vid,'production',definitive,smoke_issue=True)
            assert proc.wait(timeout=60)==0
            result=json.loads(definitive.read_text());assert result['snapshot_registered'] and result['selected_variant']==row['id'];results['legacy_definitive_bridge']=result
        api.transition_variant(row['id'],row['generation'],'RETIRED','Revisor ficticio','Retirada de demostración')
        window.reload_variant();capture('06-retired-consultation')
        assert not window.prepare_button.isEnabled() and api.variant(other['id'])['state']=='APPROVED'
        assert dict(api.version(vid))==before
        assert not unexpected,unexpected
        results.update(ok=True,synthetic_only=True,revision_unchanged=True,coexistence=True,derivation_without_approval=True,captures=sorted(p.name for p in a.capture.glob('*.png')))
        a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(results,indent=2),encoding='utf-8');print(json.dumps(results))
    finally:
        if window.design:window.design.mark_clean()
        window.close();session.close()
    return 0
