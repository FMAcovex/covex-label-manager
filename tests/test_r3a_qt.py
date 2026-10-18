"""Optional Qt regression suite; all data and PDFs are fictional and isolated."""
import copy
import json
import pytest
pytest.importorskip('PySide6')
from PySide6.QtCore import QCoreApplication,QEvent
from PySide6.QtWidgets import QApplication,QMessageBox
from covex_label_manager.qt_ui.demo import DemoSession
from covex_label_manager.qt_ui.functional import FunctionalWindow
from covex_label_manager.qt_legacy import launch_legacy

@pytest.fixture
def studio():
    app=QApplication.instance() or QApplication([])
    session=DemoSession();session.fictional=True
    w=FunctionalWindow(session);w.show();app.processEvents()
    yield w,session,app
    if getattr(w,'preview_timer',None):w.preview_timer.stop();w.preview_pending=False
    if getattr(w,'preview_task',None):
        assert w.preview_task.wait(30000)
        app.processEvents()
    w.dirty=False;w.legacy_process=None;w.legacy_timer.stop();w.poll_timer.stop()
    for name in ('work_timer','_gesture_redraw'):
        timer=getattr(w,name,None)
        if timer is not None:timer.stop()
    w.hide();w.deleteLater()
    # processEvents() alone does not deliver DeferredDelete without app.exec().
    # Destroy native widgets before releasing SQLite and the synthetic session.
    QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
    app.processEvents();session.close()

def test_filter_preference_and_hidden_summary(studio):
    w,s,app=studio
    assert w.advanced.isHidden()
    w.toggle_advanced();w.remember_filters.setChecked(True);w.save_filter_preference()
    w.filters['language'].setCurrentIndex(1);w.toggle_advanced()
    assert 'Idioma:' in w.active_filter_text.text() and w.active_filter_text.isVisible()
    assert s.services.filter_preferences()==(True,False)
    w.toggle_advanced();w.save_filter_preference()
    other=FunctionalWindow(s);other.show();app.processEvents()
    assert other.advanced.isVisible() and other.remember_filters.isChecked()
    other.dirty=False;other.legacy_timer.stop();other.poll_timer.stop();other.hide();other.deleteLater();app.processEvents()

def test_three_actions_have_documentary_states(studio):
    w,s,app=studio
    assert not w.prepare_button.isEnabled() and w.test_button.isEnabled()
    approved=next(v['id'] for v in s.services.versions(w.row['id']) if v['state']=='APPROVED')
    w.select_version(approved)
    assert w.prepare_button.isEnabled() and w.test_button.isEnabled()

def test_open_editor_is_not_emission(studio):
    w,s,app=studio
    previous=len(s.services.issues());w.open_editor();app.processEvents()
    assert w.stack.currentWidget() is w.editor
    assert len(s.services.issues())==previous

def test_dirty_work_persists_navigation_and_saves(studio):
    w,s,app=studio;w.open_editor();before=json.loads(s.services.version(w.current_editor_id)['fields_json'])
    w.spins['x'].setValue(w.spins['x'].value()+1);new=w.fields[0]['x']
    assert w.dirty
    w.navigate('library');w.navigate('editor')
    assert w.fields[0]['x']==new and json.loads(s.services.version(w.current_editor_id)['fields_json'])==before
    assert w.save_work() and not w.dirty
    assert json.loads(s.services.version(w.current_editor_id)['fields_json'])[0]['x']==new

def test_cancel_revision_change_retains_dirty_work(studio,monkeypatch):
    w,s,app=studio;w.open_editor();old=w.current_editor_id
    w.spins['x'].setValue(w.spins['x'].value()+1)
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Cancel)
    w.select_version(next(r['version_id'] for r in w.rows if r['version_id']!=old));w.open_editor()
    assert w.current_editor_id==old and w.dirty

def test_stale_documentary_state_blocks_saved_work(studio,monkeypatch):
    w,s,app=studio;w.open_editor();w.spins['x'].setValue(w.spins['x'].value()+1)
    old=json.loads(s.services.version(w.current_editor_id)['fields_json'])
    s.services.approve(w.current_editor_id,'Demo reviewer','Fictional approval reference')
    monkeypatch.setattr(QMessageBox,'warning',lambda *a,**k:None)
    assert not w.save_work()
    assert json.loads(s.services.version(w.current_editor_id)['fields_json'])==old

def test_metadata_source_validation_and_persistence(studio):
    w,s,app=studio
    with pytest.raises(ValueError):s.services.library.update_metadata(w.row['id'],{'country':'Fictitious'},'')
    s.services.library.update_metadata(w.row['id'],{'country':'Fictitious'},'Fictional supplier declaration')
    w.refresh_facets();w.refresh()
    assert w.row['country']=='Fictitious'

def test_clone_is_pending_and_approval_retires_previous(studio):
    w,s,app=studio
    previous=next(v['id'] for v in s.services.versions(w.row['id']) if v['state']=='APPROVED')
    new=s.services.clone_version(previous,'00-R1','Fictional revision')
    assert s.services.version(new)['state']=='PENDING'
    assert not s.services.eligibility(new)[0] and s.services.eligibility(new,False)[0]
    s.services.approve(new,'Demo reviewer','Fictional approval reference')
    assert s.services.version(previous)['state']=='RETIRED'
    assert not s.services.eligibility(previous)[0] and not s.services.eligibility(previous,False)[0]

def test_integrity_blocks_bridge_before_process(studio,monkeypatch):
    w,s,app=studio
    approved=next(v['id'] for v in s.services.versions(w.row['id']) if v['state']=='APPROVED')
    version=s.services.version(approved);s.services.asset_path(version['master_pdf']).write_bytes(b'corrupt demo PDF')
    started=[]
    monkeypatch.setattr('covex_label_manager.qt_legacy.subprocess.Popen',lambda *a,**k:started.append(a))
    with pytest.raises(ValueError):launch_legacy(s.services,'emitir',approved)
    assert not started

def test_bridge_selects_same_data_and_explicit_test(studio,monkeypatch):
    w,s,app=studio;calls=[]
    monkeypatch.setattr('covex_label_manager.qt_legacy.subprocess.Popen',lambda cmd,env:calls.append((cmd,env)))
    launch_legacy(s.services,'emitir',w.row['version_id'],'test')
    command,env=calls[0]
    assert command[command.index('--version-id')+1]==str(w.row['version_id'])
    assert command[command.index('--writer-protocol')+1]=='4'
    assert '--mode' in command and 'test' in command
    assert env['COVEX_LABEL_DATA']==s.services.location()

def test_import_pdf_remains_pending(studio,tmp_path):
    w,s,app=studio
    source=s.services.open_document(w.row['version_id'])
    version=s.services.import_label(source,dict(name='Fictional import',version='00',origin='CLIENTE',customer='Demo customer'))
    assert s.services.version(version)['state']=='PENDING'
    assert not s.services.eligibility(version)[0]

def test_missing_metadata_is_not_invented(studio):
    w,s,app=studio
    source=s.services.open_document(w.row['version_id'])
    vid=s.services.import_label(source,dict(name='No deduced metadata',version='00'))
    row=next(r for r in s.services.library.entries() if r['version_id']==vid)
    assert not row.get('country') and not row.get('language') and not row.get('product')


def test_native_add_remove_and_identifiers(studio,monkeypatch):
    from PySide6.QtWidgets import QDialog,QLineEdit
    w,s,app=studio;w.open_editor();before=len(w.fields)
    def fill(dialog):
        entries=dialog.findChildren(QLineEdit);entries[0].setText('fictional_new_key');entries[1].setText('Fictional new field')
        return QDialog.DialogCode.Accepted
    monkeypatch.setattr(QDialog,'exec',fill)
    w.add_field();assert len(w.fields)==before+1 and w.dirty
    assert w.save_work()
    w.field_list.setCurrentRow(before)
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
    w.remove_field();assert len(w.fields)==before and w.save_work()

def test_approval_dialog_cancel_does_not_approve(studio,monkeypatch):
    from covex_label_manager.qt_ui.revision_approval import RevisionApprovalDialog
    from PySide6.QtWidgets import QDialog
    w,s,app=studio;vid=w.row['version_id']
    monkeypatch.setattr(RevisionApprovalDialog,'exec',lambda self:QDialog.DialogCode.Rejected)
    w.approve_revision();assert s.services.version(vid)['state']=='PENDING'

def test_guarded_ui_approval_and_clone(studio,monkeypatch):
    from covex_label_manager.qt_ui.revision_approval import RevisionApprovalDialog
    from PySide6.QtWidgets import QDialog
    w,s,app=studio;vid=w.row['version_id']
    def approve(dialog):
        dialog.reviewer.setText('Demo reviewer')
        dialog.reference.setText('Fictional approval reference')
        assert not dialog.accept_button.isEnabled()
        dialog.confirm.setChecked(True)
        assert dialog.accept_button.isEnabled()
        monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
        dialog.commit()
        return dialog.result()
    monkeypatch.setattr(RevisionApprovalDialog,'exec',approve)
    w.approve_revision();assert s.services.version(vid)['state']=='APPROVED'
    monkeypatch.setattr(w,'ask_form',lambda *a,**k:{'version':'fictional-R1','notes':'Fictional clone review'})
    w.clone_revision();assert w.row['version']=='fictional-R1' and w.row['state']=='PENDING'

def test_native_approval_requires_confirmation_and_keeps_state_on_cancel(studio,monkeypatch):
    from covex_label_manager.qt_ui.revision_approval import RevisionApprovalDialog
    w,s,app=studio;vid=w.row['version_id']
    dialog=RevisionApprovalDialog(w,s.services,s.services.version(vid))
    assert not dialog.accept_button.isEnabled()
    dialog.reviewer.setText('Synthetic reviewer')
    dialog.reference.setText('Evidence document for demonstration')
    assert not dialog.accept_button.isEnabled()
    dialog.confirm.setChecked(True);assert dialog.accept_button.isEnabled()
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Cancel)
    dialog.commit()
    assert s.services.version(vid)['state']=='PENDING'
    dialog.close()



def test_compact_auto_fold_does_not_forget_manual_preference(studio):
    w,s,app=studio
    w.resize(1500,980);app.processEvents()
    w.toggle_advanced();w.remember_filters.setChecked(True)
    assert s.services.filter_preferences()==(True,True)
    w.resize(1100,760);app.processEvents()
    assert w.advanced.isHidden()
    w.save_filter_preference()
    assert s.services.filter_preferences()==(True,True)


def test_enter_opens_only_from_table_not_search(studio):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    w,s,app=studio
    w.search.setFocus();app.processEvents();QTest.keyClick(w.search,Qt.Key.Key_Return);app.processEvents()
    assert w.stack.currentWidget() is w.library
    w.table.setFocus();app.processEvents();QTest.keyClick(w.table,Qt.Key.Key_Return);app.processEvents()
    assert w.stack.currentWidget() is w.editor


def test_save_state_tracks_dirty_work_and_legacy_lock(studio):
    w,s,app=studio;w.open_editor()
    assert not w.save_button.isEnabled() and 'Sin cambios' in w.save_button.toolTip()
    w.spins['x'].setValue(w.spins['x'].value()+1)
    assert w.save_button.isEnabled()
    w.legacy_process=object();w.update_dirty()
    assert not w.save_button.isEnabled() and 'bloqueada' in w.save_button.toolTip()
    assert not w.save_work()
    w.legacy_process=None;w.recheck_actions()
    assert w.save_button.isEnabled() and w.save_work()
    assert not w.save_button.isEnabled()

def test_disabled_prepare_click_cannot_open_legacy(studio,monkeypatch):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    w,s,app=studio;started=[]
    monkeypatch.setattr('covex_label_manager.qt_ui.functional.launch_legacy',lambda *a,**k:started.append(a))
    for vid in [w.session.initial_id,next(r['version_id'] for r in w.rows if r['state']=='RETIRED')]:
        w.select_version(vid);app.processEvents()
        assert not w.prepare_button.isEnabled()
        QTest.mouseClick(w.prepare_button,Qt.MouseButton.LeftButton)
    assert not started

