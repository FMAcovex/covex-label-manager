"""R6B Qt workflow: synthetic evidence and session generations."""
import pytest
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QMessageBox,QFileDialog
from test_r3a_qt import studio
from covex_label_manager.qt_ui.uat_session_dialog import UatSessionDialog

def make_session(studio,tmp_path):
    w,s,app=studio;api=s.services
    pack=tmp_path/'r6a.zip';api.acceptance_export(api.acceptance_preflight(),pack)
    env={'machine':'FICTIONAL-PC','windows':'Windows 11','tester':'Fictional',
         'commit':'a'*40,'portable_sha256':'b'*64}
    destination=tmp_path/'uat.json';api.uat_create(pack,destination,env)
    return api,destination

def test_r6b_qt_open_and_explicit_failure(studio,tmp_path,monkeypatch):
    api,path=make_session(studio,tmp_path)
    dialog=UatSessionDialog(studio[0],api)
    assert not dialog.save_button.isEnabled()
    dialog.load(path)
    assert dialog.table.rowCount()==14
    assert 'NO ACEPTADO' in dialog.summary.text()
    dialog.outcome.setCurrentIndex(dialog.outcome.findData('FAIL'))
    dialog.tester.setText('Responsable ficticio')
    dialog.when.setText('2026-10-01')
    dialog.notes.setPlainText('Incidencia de prueba sintética')
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
    dialog.save_case()
    assert dialog.report['generation']==2
    assert dialog.report['cases'][0]['status']=='FAIL'
    assert dialog.path!=str(path)
    assert api.uat_read(path)['cases'][0]['status']=='NOT_EXECUTED'
    assert 'NO ACEPTADO' in dialog.summary.text()
    dialog.close()

def test_r6b_qt_pass_requires_evidence(studio,tmp_path,monkeypatch):
    api,path=make_session(studio,tmp_path)
    dialog=UatSessionDialog(studio[0],api);dialog.load(path)
    dialog.outcome.setCurrentIndex(dialog.outcome.findData('PASS'))
    dialog.tester.setText('Responsable ficticio');dialog.when.setText('2026-10-01')
    messages=[]
    monkeypatch.setattr(QMessageBox,'warning',lambda *a,**k:messages.append(str(a[2])))
    dialog.save_case()
    assert messages and dialog.report['generation']==1
    evidence=tmp_path/'receipt.txt';evidence.write_text('Evidence purely fictional')
    dialog.evidence_path=str(evidence)
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
    dialog.save_case()
    assert dialog.report['generation']==2 and dialog.report['cases'][0]['status']=='PASS'
    evidence.write_text('tampered')
    dialog.verify()
    assert len(messages)==2
    dialog.close()
