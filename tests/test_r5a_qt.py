"""R5A Qt preview, explicit selection, non-destructive report."""
import pytest
pytest.importorskip('PySide6')
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog,QMessageBox
from test_r3a_qt import studio
from covex_label_manager.qt_ui.folder_import import FolderImportDialog
from test_r5a_catalog import fake


def test_new_and_duplicate_are_visibly_distinguished(studio,tmp_path,monkeypatch):
    w,s,app=studio
    a=fake(tmp_path/'Fictional A 00.pdf')
    b=tmp_path/'Fictional B 00.pdf';b.write_bytes(a.read_bytes())
    dialog=FolderImportDialog(w,s.services,tmp_path,[a,b])
    assert dialog.inventory[0]['status']=='NEW'
    assert dialog.inventory[1]['status']=='DUPLICATE'
    assert dialog.include[0].checkState()==Qt.CheckState.Checked
    assert dialog.include[1].checkState()==Qt.CheckState.Unchecked
    monkeypatch.setattr(QMessageBox,'question',lambda *args:QMessageBox.StandardButton.Yes)
    dialog.start();dialog.timer.stop();dialog.step();dialog.timer.stop()
    dialog.step();dialog.timer.stop();dialog.finish()
    assert dialog.ok==1 and not dialog.failures


def test_csv_before_import_does_not_mutate(studio,tmp_path,monkeypatch):
    w,s,app=studio
    p=fake(tmp_path/'Fictional Survey 00.pdf')
    count=len(s.services.library_records())
    d=FolderImportDialog(w,s.services,tmp_path,[p])
    path=tmp_path/'preflight.csv'
    monkeypatch.setattr(QFileDialog,'getSaveFileName',lambda *args:(str(path),'CSV'))
    d.export_report()
    assert path.exists() and count==len(s.services.library_records())
