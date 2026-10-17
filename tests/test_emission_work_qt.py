"""Actual Qt inputs autosave, conflict preservation and shared editor/emission values."""
from types import SimpleNamespace
import pytest
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication,QMessageBox
from PySide6.QtTest import QTest
from covex_label_manager.qt_ui.demo import DemoSession
from covex_label_manager.qt_ui.functional import FunctionalWindow

@pytest.fixture
def studio(monkeypatch):
    app=QApplication.instance() or QApplication([]);s=DemoSession();s.fictional=True
    w=FunctionalWindow(s);w.show();app.processEvents()
    monkeypatch.setattr(QMessageBox,'warning',lambda *a,**k:QMessageBox.StandardButton.Ok)
    yield w,s.services,app
    w.preview_timer.stop();w.preview_pending=False
    if w.preview_task:
        assert w.preview_task.wait(30000)
        app.processEvents()
    w.work_dirty_panel=None;w.legacy_process=None;w.dirty=False
    if w.design:w.design.mark_clean()
    w.close();app.processEvents();s.close()


def test_autosave_restart_panels_and_document_identity(studio):
    w,api,app=studio;vid=next(r['version_id'] for r in api.library.entries() if r['state']=='APPROVED')
    w.select_version(vid);work=api.work.create(vid,name='Lote Qt sintético');assert w.load_emission_work(work['uid'])
    w.navigate('emission');p=w.emission_panel
    p.value_inputs['lote'].setFocus();QTest.keyClicks(p.value_inputs['lote'],'SYNTHETIC-QT')
    assert p.value_inputs['lote'].text()=='SYNTHETIC-QT'
    # Wait for durable completion, not a fixed 200 ms scheduling margin on a
    # loaded Windows runner. Do not call explicit save: this tests autosave.
    for _ in range(100):
        if api.work.get(work['uid'])['values'].get('lote')=='SYNTHETIC-QT':break
        QTest.qWait(30)
    saved=api.work.get(work['uid']);assert saved['values']['lote']=='SYNTHETIC-QT'
    assert w.editor_work_panel.value_inputs['lote'].text()=='SYNTHETIC-QT'
    p.inputs['count'].setText('2');p.changed();assert w.flush_emission_work()
    p.tabs.setCurrentIndex(1);assert p.containers.rowCount()==2
    p.containers.item(1,1).setText('LOTE-2');assert w.flush_emission_work()
    saved=api.work.get(work['uid']);assert saved['per_container']['2']['lote']=='LOTE-2'
    assert not api.issues()
    w.open_editor();w.show_editor_work();app.processEvents()
    assert w.editor_work_panel.value_inputs['lote'].text()=='SYNTHETIC-QT'
    assert w.current_editor_id==vid and w.emission_work['binding']['revision_id']==vid


def test_stale_autosave_keeps_screen_and_requires_explicit_reload(studio):
    w,api,app=studio;vid=next(r['version_id'] for r in api.library.entries() if r['state']=='APPROVED')
    work=api.work.create(vid,name='Conflicto Qt');w.load_emission_work(work['uid']);p=w.emission_panel
    api.work.save(work['uid'],work['generation'],{'values':{'lote':'OTRO PROCESO'}})
    p.value_inputs['lote'].setText('DATOS LOCALES');p.changed()
    assert not w.flush_emission_work() and p.value_inputs['lote'].text()=='DATOS LOCALES'
    assert 'NO GUARDADO' in p.note.text() and w.work_dirty_panel is p
    current=w.stack.currentWidget();w.navigate('emission');assert w.stack.currentWidget() is current
    w.work_timer.stop();w.work_dirty_panel=None;w.load_emission_work(work['uid'])
    assert w.emission_panel.value_inputs['lote'].text()=='OTRO PROCESO'
