"""Post-NO-CONFORME regressions: real services, PDFs, widgets and event loop."""
import json
import os
from pathlib import Path
import subprocess
import sys
import fitz
import pytest
pytest.importorskip('PySide6')
from PySide6.QtCore import QSize
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QDialog,QMessageBox,QLineEdit,QCheckBox,QAbstractButton
from test_r3a_qt import studio
from covex_label_manager.qt_ui.controlled_import import ControlledImportDialog


def source(folder,name='SYNTHETIC 00.pdf'):
    folder.mkdir(exist_ok=True)
    with fitz.open() as pdf:
        pdf.new_page().insert_text((40,70),'SYNTHETIC ONLY '+name);pdf.save(folder/name)
    return folder/name


def test_importers_close_in_real_application_process(tmp_path):
    repo=Path(__file__).resolve().parents[1];report=tmp_path/'report.json'
    run=subprocess.run([sys.executable,'-u','-X','faulthandler','main_qt.py','--import-check',str(report)],
        cwd=repo,capture_output=True,text=True,timeout=120,env={**os.environ,'PYTHONIOENCODING':'utf-8'})
    assert run.returncode==0,(run.returncode,run.stdout,run.stderr,report.read_text() if report.exists() else 'missing report')
    result=json.loads(report.read_text(encoding='utf-8'))
    assert result['ok'] and len(result['cases'])==18 and not result['errors']
    assert all(r['navigable'] for r in result['cases'])


@pytest.mark.parametrize('size',[(1342,680),(1068,526),(886,424),(1896,992),(1512,776),(1256,632)])
@pytest.mark.parametrize('stage',['review','summary'])
def test_wizard_row_controls_fit_and_footer_remains_reachable(studio,tmp_path,size,stage):
    w,s,app=studio;source(tmp_path)
    d=ControlledImportDialog(w,s.services,tmp_path);d.next_page();d.show();d.fit_available(QSize(*size));app.processEvents()
    assert d.width()<=size[0] and d.height()<=size[1]
    assert d.table.rowHeight(0)>=d.actions[0].sizeHint().height()+8
    assert d.table.horizontalScrollBar().maximum()>0
    assert d.table.item(0,7).text()=='Revisar identidad y elegir acción'
    assert not d.targets[0].isEnabled() and not d.go.isEnabled()
    if stage=='summary':
        d.pages.setCurrentIndex(2);d.finish();d.fit_available(QSize(*size));app.processEvents()
    assert all(f.mapTo(d,f.rect().bottomRight()).y()<d.height() for f in d.footer_widgets if f.isVisibleTo(d))
    assert all(f.mapTo(d,f.rect().bottomRight()).y()<d.height()
               for f in d.wizard_footer.findChildren(QAbstractButton) if f.isVisibleTo(d))
    assert d.width()<=size[0] and d.height()<=size[1]
    d.reject()


def test_wizard_folder_identity_confirm_pending_summary_editor(studio,tmp_path,monkeypatch):
    w,s,app=studio;folder=tmp_path/'SYNTHETIC Categoria';path=source(folder)
    d=ControlledImportDialog(w,s.services);assert not d.next.isEnabled()
    d.set_folder(folder);assert d.folder_path.text()==str(folder)
    assert d.metadata[0]['category']==folder.name
    d.next_page();d.actions[0].setCurrentIndex(1)
    d.table.item(0,1).setText('SYNTHETIC editable');d.table.item(0,5).setText('SYN-CODE');d.table.item(0,2).setText('12')
    d.confirm_identity.setChecked(True)
    d.table.item(0,6).setText('SYNTHETIC confirmed category');assert not d.confirm_identity.isChecked()
    d.confirm_identity.setChecked(True);before=path.read_bytes()
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
    d.start();d.timer.stop();d.step();d.timer.stop();d.finish()
    assert d.ok==1 and d.processed==1 and d.pages.currentIndex()==2
    version=s.services.version(d.imported[0]['version_id'])
    assert version['state']=='PENDING' and version['name']=='SYNTHETIC editable' and version['version']=='12'
    assert path.read_bytes()==before and not s.services.issues()
    d.open_editor();assert d.editor_version_id==version['id']
    w.refresh();w.select_version(d.editor_version_id);w.open_editor();assert w.current_editor_id==version['id']


def test_wizard_revision_target_and_safe_hash_rejection(studio,tmp_path,monkeypatch):
    w,s,app=studio;path=source(tmp_path)
    d=ControlledImportDialog(w,s.services,tmp_path);d.next_page();d.actions[0].setCurrentIndex(2)
    assert d.targets[0].isEnabled()
    with pytest.raises(ValueError,match='destino'):d.selected()
    d.targets[0].setCurrentIndex(1);d.table.item(0,2).setText('SYN-NEW')
    assert d.selected()[0][1]['action']=='NEW_REVISION'
    path.write_bytes(b'SYNTHETIC changed since preview')
    d.confirm_identity.setChecked(True);monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
    d.start();d.timer.stop();d.step();d.timer.stop();d.finish()
    assert d.ok==0 and len(d.failures)==1 and 'modificada' in d.failures[0]


def test_wizard_bulk_edits_only_checked_fields(studio,tmp_path,monkeypatch):
    w,s,app=studio;source(tmp_path,'SYNTHETIC A 00.pdf');source(tmp_path,'SYNTHETIC B 00.pdf')
    d=ControlledImportDialog(w,s.services,tmp_path);names=[m['name'] for m in d.metadata]
    def accept(dialog):
        check=next(c for c in dialog.findChildren(QCheckBox) if c.text()=='Categoría / tipo sugerido')
        check.setChecked(True)
        edits=dialog.findChildren(QLineEdit);edits[5].setText('SYNTHETIC BULK')
        return QDialog.DialogCode.Accepted
    monkeypatch.setattr(QDialog,'exec',accept);d.identity_form([0,1],True)
    assert [m['name'] for m in d.metadata]==names
    assert all(m['category']=='SYNTHETIC BULK' for m in d.metadata)
    assert not d.confirm_identity.isChecked()


@pytest.mark.parametrize('open_editor',[True,False])
def test_post_import_selection_with_excluding_library_filters(studio,tmp_path,monkeypatch,open_editor):
    w,s,app=studio;source(tmp_path,'SYNTHETIC outside filter 00.pdf')
    w.search.setText('Solución Alfa');w.refresh();previous=w.row['version_id'];created=[]
    def execute(dialog):
        dialog.set_folder(tmp_path)
        decision={**dialog.metadata[0],'action':'NEW_LABEL'}
        result=s.services.catalog_migration_apply(tmp_path,dialog.rows[0],decision)
        created.append(result['version_id']);dialog.processed=1;dialog.ok=1
        if open_editor:dialog.editor_version_id=result['version_id']
        return QDialog.DialogCode.Accepted
    monkeypatch.setattr(ControlledImportDialog,'exec',execute)
    w.import_folder_native()
    if open_editor:
        assert w.current_editor_id==created[0] and w.stack.currentWidget() is w.editor
        assert w.row['version_id']==created[0] and not w.search.text()
    else:
        assert w.search.text()=='Solución Alfa' and w.row['version_id']==previous
        assert w.current_editor_id!=created[0]
    assert s.services.version(created[0])['state']=='PENDING' and not s.services.issues()


def prepared(studio):
    w,s,app=studio;api=s.services
    vid=next(r['version_id'] for r in api.library.entries() if r['state']=='APPROVED')
    work=api.work.create(vid,name='SYNTHETIC automatic preview')
    work=api.work.save(work['uid'],work['generation'],{'values':{'lote':'SYNTHETIC-AUTO','pn':'350 g','pb':'500000 mg'}})
    w.load_emission_work(work['uid']);w.navigate('emission')
    return w,api,app


def await_preview(w):
    for _ in range(400):
        QTest.qWait(25)
        if w.work_preview and w.preview_task is None and not w.preview_timer.isActive():return
    pytest.fail('Automatic preview did not settle: '+w.emission_pdf.note.text())


def test_automatic_preview_debounce_inputs_format_count_and_no_issue(studio):
    w,api,app=prepared(studio);await_preview(w)
    assert w.preview_matches() and not api.issues()
    panel=w.emission_panel
    for text in ('SYNTHETIC-1','SYNTHETIC-2','SYNTHETIC-FINAL'):
        panel.value_inputs['lote'].setText(text);panel.changed();QTest.qWait(30)
    assert not w.native_issue.isEnabled() and w.work_preview is None
    await_preview(w)
    with fitz.open(w.work_preview['path']) as pdf:assert 'SYNTHETIC-FINAL' in ''.join(p.get_text() for p in pdf)
    panel.inputs['count'].setText('2');panel.changed();await_preview(w)
    assert w.work_review['summary']['physical']==2
    panel.profile_inputs['gap_mm'].setText('4');panel.changed();await_preview(w)
    assert w.emission_work['profile']['gap_mm']=='4'
    assert not api.issues() and api._repository.db.execute('PRAGMA user_version').fetchone()[0]==4


def test_automatic_preview_invalid_mass_stops_and_recovers(studio):
    w,api,app=prepared(studio);await_preview(w)
    w.emission_panel.value_inputs['pn'].setText('SYNTHETIC invalid unit');w.emission_panel.changed();QTest.qWait(800)
    assert w.work_preview is None and not w.native_issue.isEnabled()
    assert 'Revise errores' in w.emission_pdf.note.text()
    assert w.emission_panel.error_labels['value:pn'].text()
    w.emission_panel.value_inputs['pn'].setText('350g');w.emission_panel.changed();await_preview(w)
    assert w.preview_matches() and not api.issues()


def test_stale_async_result_is_discarded_and_next_request_runs(studio,monkeypatch):
    from covex_label_manager.qt_ui.preview_task import PreviewTask
    w,api,app=prepared(studio);w.preview_timer.stop()
    real=PreviewTask.run
    def delayed(task):
        task.msleep(200);real(task)
    monkeypatch.setattr(PreviewTask,'run',delayed)
    w.automatic_preview();old=w.preview_task;path=old.request[4]
    w.emission_panel.value_inputs['lote'].setText('SYNTHETIC-NEWEST');w.emission_panel.changed()
    assert w.preview_task is old and not w.issue_emission_work()
    await_preview(w)
    assert not path.exists() and w.preview_matches()
    with fitz.open(w.work_preview['path']) as pdf:assert 'SYNTHETIC-NEWEST' in ''.join(p.get_text() for p in pdf)
    assert not api.issues()


def test_worker_runs_in_another_process_without_shared_sqlite_or_mupdf(studio):
    w,api,app=prepared(studio);w.preview_timer.stop();results=[]
    w.automatic_preview();w.preview_task.completed.connect(results.append);await_preview(w)
    assert results and results[0]['child_pid']!=os.getpid()
    assert w.preview_matches() and not api.issues()


def test_worker_retries_short_read_contention_without_ignoring_failure():
    from covex_label_manager.preview_render import retry_read
    from covex_label_manager.emission_work import WorkConflict
    calls=[];waits=[]
    def collide():
        calls.append(1)
        if len(calls)<3:raise WorkConflict('SYNTHETIC short contention')
        return 'SYNTHETIC read'
    assert retry_read(collide,waits.append)=='SYNTHETIC read'
    assert len(calls)==3 and waits==[.05,.05]
    def always_busy():raise WorkConflict('SYNTHETIC busy')
    with pytest.raises(WorkConflict):retry_read(always_busy,waits.append)


def test_main_close_during_render_does_not_destroy_worker(studio,monkeypatch):
    from covex_label_manager.qt_ui.preview_task import PreviewTask
    w,api,app=prepared(studio);w.preview_timer.stop();real=PreviewTask.run
    def delayed(task):task.msleep(250);real(task)
    monkeypatch.setattr(PreviewTask,'run',delayed);w.automatic_preview()
    w.close();assert w.isVisible() and w.preview_task is not None
    await_preview(w);assert w.preview_matches() and not api.issues()


def test_preview_child_crash_blocks_issue_but_keeps_main_window(studio,monkeypatch):
    from types import SimpleNamespace
    w,api,app=prepared(studio);w.preview_timer.stop()
    monkeypatch.setattr('covex_label_manager.qt_ui.preview_task.subprocess.run',
        lambda *a,**k:SimpleNamespace(returncode=-1073740791))
    w.automatic_preview()
    for _ in range(200):
        QTest.qWait(25)
        if w.preview_task is None:break
    assert w.preview_task is None and w.isVisible() and w.work_preview is None
    assert not w.native_issue.isEnabled() and 'sin informe' in w.emission_pdf.note.text()
    assert not api.issues()
