"""R4C Qt controls: fake spooler, never a real printer on CI."""
import pytest
pytest.importorskip('PySide6')

from PySide6.QtWidgets import QMessageBox
from test_r3a_qt import studio
from test_r3c_emission_qt import prepared


def test_no_production_print_from_draft(studio,monkeypatch):
    w,api,work=prepared(studio)
    assert not w.native_print.isEnabled()
    called=[]
    monkeypatch.setattr('covex_label_manager.qt_ui.print_control.print_registered_pdf',
                        lambda *args:called.append(args) or True)
    assert not w.print_emission_pdf()
    assert not called and not api.issues()


def test_registered_emission_and_history_share_verified_print(studio,monkeypatch):
    w,api,work=prepared(studio)
    monkeypatch.setattr(QMessageBox,'question',
                        lambda *a,**k:QMessageBox.StandardButton.Yes)
    assert w.preview_emission_work() and w.issue_emission_work()
    assert w.native_print.isEnabled()
    called=[]
    def fake(_api,issue,parent):
        called.append(issue)
        return {'printer':'SYNTHETIC DRIVER','pages':1}
    monkeypatch.setattr('covex_label_manager.qt_ui.print_control.print_registered_pdf',fake)
    assert w.print_emission_pdf()
    assert 'NO se confirma' in w.emission_feedback.text()
    w.navigate('history')
    w.history_table.selectRow(0)
    assert w.print_history_button.isEnabled()
    assert w.print_historical_pdf()
    assert called==[work['issue_id'] or api.issues()[0]['id']]*2
    assert len(api.issues())==1  # Printing does not manufacture reprints.


def test_tampered_history_pdf_blocks_before_driver(studio,monkeypatch):
    w,api,work=prepared(studio)
    monkeypatch.setattr(QMessageBox,'question',
                        lambda *a,**k:QMessageBox.StandardButton.Yes)
    monkeypatch.setattr(QMessageBox,'warning',lambda *a,**k:None)
    assert w.preview_emission_work() and w.issue_emission_work()
    issue_id=api.issues()[0]['id']
    api.asset_path(api.issue(issue_id)['pdf_path']).write_bytes(b'modified')
    called=[]
    monkeypatch.setattr('covex_label_manager.qt_ui.print_control.print_registered_pdf',
                        lambda *args:called.append(1) or True)
    assert not w.print_emission_pdf()
    assert not called
