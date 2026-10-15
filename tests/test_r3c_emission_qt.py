"""Native operator workflow: synthetic documents, real widgets and PDFs, no Tk."""
import json
import fitz
import pytest
from test_emission_work_qt import studio
from PySide6.QtWidgets import QMessageBox,QFileDialog
from covex_label_manager.storage import sha256


def prepared(studio):
    w,api,app=studio
    vid=next(r['version_id'] for r in api.library.entries() if r['state']=='APPROVED')
    work=api.work.create(vid,name='R3C · lote sintético')
    work=api.work.save(work['uid'],1,{'values':{'lote':'SYNTHETIC-R3C','pn':'1','pb':'2'},'count':'3','selection':'1-3',
        'per_container':{'2':{'lote':'SYNTHETIC-RECIPIENTE-2','pn':'0,5','pb':'0,7'}}})
    w.load_emission_work(work['uid']);w.navigate('emission');app.processEvents()
    return w,api,work


def test_native_preview_export_cancel_issue_and_recovery(studio,monkeypatch,tmp_path):
    w,api,work=prepared(studio)
    monkeypatch.setattr('covex_label_manager.qt_ui.functional.launch_legacy',lambda *a,**k:pytest.fail('Native emission launched Tk'))
    assert w.preview_emission_work(),w.emission_feedback.text()
    assert not api.issues() and w.native_issue.isEnabled(),w.emission_feedback.text()
    with fitz.open(w.work_preview['path']) as pdf:
        text=''.join(p.get_text() for p in pdf)
        assert 'PRUEBA' in text and 'SYNTHETIC-R3C' in text and 'SYNTHETIC-RECIPIENTE-2' in text
    dest=tmp_path/'PRUEBA.pdf';monkeypatch.setattr(QFileDialog,'getSaveFileName',lambda *a,**k:(str(dest),'PDF'))
    assert w.proof_emission_work() and sha256(dest)==w.work_preview['sha256'] and not api.issues()
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Cancel)
    assert not w.issue_emission_work() and not api.issues()
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
    assert w.issue_emission_work(),w.emission_feedback.text()
    issue=api.issues()[0];snap=json.loads(issue['design_snapshot_json'])
    assert snap['work']['uid']==work['uid'] and json.loads(issue['selected_indices'])==[1,2,3]
    with fitz.open(api.asset_path(issue['pdf_path'])) as pdf:
        text=''.join(p.get_text() for p in pdf)
        assert 'PRUEBA' not in text and 'SYNTHETIC-RECIPIENTE-2' in text
    assert api.work.get(work['uid'])['phase']=='ISSUED'
    assert not w.issue_emission_work() and len(api.issues())==1


def test_changed_after_confirmation_and_tampered_preview_block(studio,monkeypatch):
    w,api,work=prepared(studio);assert w.preview_emission_work()
    def changed(*args,**kwargs):
        api.work.save(work['uid'],w.emission_work['generation'],{'values':{'lote':'CONCURRENT'}})
        return QMessageBox.StandardButton.Yes
    monkeypatch.setattr(QMessageBox,'question',changed)
    assert not w.issue_emission_work() and not api.issues()
    w.reload_emission_work();assert w.preview_emission_work()
    w.work_preview['path'].write_bytes(b'changed')
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
    assert not w.issue_emission_work() and not api.issues()


def test_inline_checks_pending_invalid_format_and_long_fields(studio):
    w,api,work=prepared(studio)
    panel=w.emission_panel;panel.inputs['count'].setText('0');panel.changed();assert w.flush_emission_work()
    assert panel.error_labels['count'].text() and not w.native_issue.isEnabled()
    panel.inputs['count'].setText('3');panel.value_inputs['lote'].setText('EXTENSO '*500);panel.changed();assert w.flush_emission_work()
    w.preview_emission_work()
    w.recheck_actions();assert not w.native_issue.isEnabled()
    assert not api.issues()
