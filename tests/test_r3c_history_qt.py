"""Native history selection, verified actual PDF, filter and controlled dialog."""
import pytest
from test_emission_work_qt import studio
from test_r3c_emission_qt import prepared
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication,QDialog,QLineEdit,QPushButton,QMessageBox


def test_native_history_view_and_reprint_confirmation(studio,monkeypatch):
    w,api,work=prepared(studio)
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
    assert w.preview_emission_work() and w.issue_emission_work()
    w.navigate('history');assert w.stack.currentWidget() is w.history_page
    w.history_table.selectRow(0);assert w.history_report['reprint_allowed']
    assert w.preview_native_issue() and w.history_pdf.page_count>0
    assert 'Snapshot de diseño verificado' in w.history_text['summary'].toPlainText()
    def complete():
        dialog=QApplication.activeModalWidget();assert isinstance(dialog,QDialog)
        inputs=dialog.findChildren(QLineEdit);inputs[0].setText('2-3');inputs[1].setText('Daño sintético comprobado')
        button=next(b for b in dialog.findChildren(QPushButton) if b.text()=='Registrar reimpresión…');assert button.isEnabled();button.click()
    QTimer.singleShot(50,complete);w.native_reprint()
    assert len(api.issues())==2 and api.issues()[0]['source_issue_id']==1
    w.history_search.setText('no matches');assert all(w.history_table.isRowHidden(r) for r in range(2))
    w.history_search.clear();assert not any(w.history_table.isRowHidden(r) for r in range(2))
    api.asset_path(api.issue(1)['pdf_path']).write_bytes(b'changed')
    w.history_id=1;assert not w.preview_native_issue()
