"""Native R3F comparison and folder import with only synthetic isolated data."""
import pytest
pytest.importorskip('PySide6')
from pathlib import Path
from PySide6.QtWidgets import QMessageBox
from test_r3a_qt import studio
from covex_label_manager.qt_ui.compare import CompareDialog
from covex_label_manager.qt_ui.folder_import import FolderImportDialog


def test_native_comparison_does_not_mutate_document(studio):
    w,session,app=studio
    a=session.services.version(session.initial_id)
    records=list(session.services.versions(a['label_id']))
    assert len(records)>=2
    before=[(v['id'],v['state'],v['pdf_sha256']) for v in records]
    d=CompareDialog(w,session.services,a['label_id'],session.initial_id)
    assert d.images is not None
    d.first.setCurrentIndex(0);d.second.setCurrentIndex(1)
    assert d.documentary_differences() is not None
    d.opacity.setValue(85)
    assert d.overlay.scene().items()
    assert before==[(v['id'],v['state'],v['pdf_sha256']) for v in session.services.versions(a['label_id'])]


def test_compare_prevents_same_revision(studio):
    w,s,app=studio
    a=s.services.version(s.initial_id)
    d=CompareDialog(w,s.services,a['label_id'])
    d.second.setCurrentIndex(d.first.currentIndex())
    assert d.images is None
    assert 'dos revisiones' in d.summary.text().lower()


def test_folder_import_creates_only_pending_and_counts_failures(studio,tmp_path,monkeypatch):
    w,session,app=studio
    from covex_label_manager.importer import proposed_identity
    good=tmp_path/'SYNTHETIC_LABEL_00.pdf'
    import fitz
    with fitz.open() as doc:
        doc.new_page().insert_text((40,70),'SYNTHETIC TEST DOCUMENT')
        doc.save(good)
    bad=tmp_path/'INEXISTENTE_00.pdf'
    d=FolderImportDialog(w,session.services,tmp_path,[good,bad])
    monkeypatch.setattr(QMessageBox,'question',lambda *args:QMessageBox.StandardButton.Yes)
    d.start();d.timer.stop();d.step();d.timer.stop();d.step();d.timer.stop();d.finish()
    assert d.ok==1 and len(d.failures)==1 and d.done==2
    assert any(v['state']=='PENDING' for v in session.services.labels() if 'Synthetic_Label' in v['name'] or 'Synthetic Label' in v['name'])


def test_folder_import_cancel_does_not_rollback_committed(studio,tmp_path,monkeypatch):
    w,s,app=studio
    paths=[tmp_path/'SYNTH_00.pdf',tmp_path/'SYNTH_01.pdf']
    for p in paths:
        import fitz
        with fitz.open() as doc:
            doc.new_page().insert_text((40,70),'FICTITIOUS '+p.name)
            doc.save(p)
    d=FolderImportDialog(w,s.services,tmp_path,paths)
    monkeypatch.setattr(QMessageBox,'question',lambda *args:QMessageBox.StandardButton.Yes)
    d.start();d.timer.stop();d.step();d.timer.stop();d.stop();d.step()
    assert d.ok==1 and d.done==1 and d.cancelled
    assert '1 sin procesar' in d.status.text()
