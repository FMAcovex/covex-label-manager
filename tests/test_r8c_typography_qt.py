"""R8C native UI contracts; only isolated synthetic documents and approvals."""
import copy
import json
import sys
from datetime import date
import fitz
import pytest
pytest.importorskip('PySide6')
from PySide6.QtCore import Qt,QCoreApplication,QEvent
from PySide6.QtWidgets import QDialog,QInputDialog,QDialogButtonBox
from PySide6.QtTest import QTest
from test_r3a_qt import studio
from test_r7a_status_qt import synthetic_source,add_three
from covex_label_manager.qt_ui.emission_appearance import EmissionAppearanceDialog
from covex_label_manager.qt_ui.status_fields_dialog import StatusFieldsDialog
from covex_label_manager.typography import DEFAULT


def test_r8c_preserves_all_87_ids_and_names():
    from pathlib import Path
    import re
    docs=Path(__file__).resolve().parents[1]/'docs'
    def entries(path):return re.findall(r'^\| ([A-Z][0-9]{2}) \| ([^|]+)\|',(docs/path).read_text(encoding='utf-8'),re.M)
    before=entries('R6B_UX_INTEGRATED/CONSERVACION_87.md')
    assert len(before)==87 and entries('R8C_TYPOGRAPHY_SCALING/CONSERVACION_87.md')==before


def test_new_controls_do_not_shadow_native_qwidget_queries(studio):
    from PySide6.QtWidgets import QStyle
    from PySide6.QtCore import QSize
    from covex_label_manager.qt_ui.text_appearance import TextAppearance
    w,s,app=studio;make_work(w);dialog=EmissionAppearanceDialog(w)
    assert isinstance(dialog.size(),QSize)
    assert dialog.window() is dialog and isinstance(dialog.style(),QStyle)
    appearance=TextAppearance();assert isinstance(appearance.style(),QStyle)
    dialog.reject();dialog.deleteLater();appearance.deleteLater()


def select(combo,data):
    combo.setCurrentIndex(combo.findData(data));combo.activated.emit(combo.currentIndex())


def make_work(w):
    approved=next(v['id'] for v in w.api.versions(w.row['id']) if v['state']=='APPROVED')
    work=w.api.work.create(approved,name='SYNTHETIC-R8C')
    work=w.api.work.save(work['uid'],1,{'values':{'lote':'SYN-01','cantidad':'1 kg','proveedor':'SYN','direccion':'SYN','telefono':'123','observaciones':'SYN'}})
    w.emission_work=work;w.refresh_work_panels();w.preview_timer.stop();return work


@pytest.mark.parametrize('width,height',[(1366,728),(1092,574),(910,472),(1920,1040),(1536,824),(1280,680)])
def test_new_appearance_controls_reachable_and_scene_survives(studio,width,height):
    w,s,app=studio;w.resize(width,height);w.open_editor();app.processEvents()
    item=w.field_items[0];transform=w.canvas.transform()
    select(w.text_appearance.family,'serif')
    assert w.fields[0]['typography']['family']=='serif'
    w.text_appearance.color.setText('#123456');w.text_appearance.color.editingFinished.emit()
    assert w.fields[0]['typography']['color']=='#123456' and w.field_items[0] is item and w.canvas.transform()==transform
    for control in (w.text_appearance.family,w.text_appearance.color,w.text_appearance.italic,w.text_appearance.wrap,w.example_input,*w.spins.values()):
        w.properties_scroll.ensureWidgetVisible(control);app.processEvents()
        assert w.properties_scroll.viewport().rect().contains(control.mapTo(w.properties_scroll.viewport(),control.rect().center()))
    assert w.properties_scroll.horizontalScrollBar().maximum()==0
    after=copy.deepcopy(w.design.state);w.undo_edit();assert w.design.state!=after
    w.redo_edit();assert w.design.state==after
    assert w.save_work();assert json.loads(w.api.version(w.current_editor_id)['fields_json'])[0]['typography']['color']=='#123456'


def test_editor_real_pdf_preserves_canvas_and_renders_sample(studio):
    w,s,app=studio;w.open_editor();item=w.field_items[0]
    select(w.text_appearance.family,'sans')
    w.example_input.setText('SYN-EXAMPLE');w.example_input.editingFinished.emit()
    w.editor_pdf_toggle.setChecked(True);w.editor_pdf_timer.stop();w.refresh_editor_pdf()
    assert w.editor_pdf.path is not None
    with fitz.open(w.editor_pdf.path) as doc:
        assert 'SYN-EXAMPLE' in doc[0].get_text() and 'PRUEBA' in doc[0].get_text()
        assert any(font[4].startswith('R8C_') for font in doc[0].get_fonts())
    w.editor_pdf_toggle.setChecked(False);assert w.field_items[0] is item


def test_trial_live_pdf_cancel_apply_reopen_restore_and_definitive_guard(studio,tmp_path):
    w,s,app=studio;work=make_work(w);original=dict(w.api.version(work['binding']['revision_id']))
    dialog=EmissionAppearanceDialog(w);dialog.field.setCurrentIndex(dialog.field.findData('lote'))
    select(dialog.appearance.family,'sans');dialog.font_size.setValue(9);dialog.changed();dialog.timer.stop();dialog.preview()
    assert dialog.pdf.path
    with fitz.open(dialog.pdf.path) as doc:assert 'SYN-01' in doc[0].get_text() and 'PRUEBA' in doc[0].get_text()
    dialog.reject();assert w.api.work.get(work['uid'])==work
    dialog=EmissionAppearanceDialog(w);dialog.field.setCurrentIndex(dialog.field.findData('lote'))
    select(dialog.appearance.family,'mono');dialog.font_size.setValue(9);dialog.changed();dialog.timer.stop();dialog.apply()
    saved=w.api.work.get(work['uid']);assert saved['profile']['trial_appearance']['fields']['lote']['typography']['family']=='mono'
    assert saved['values']==work['values'] and dict(w.api.version(original['id']))==original
    assert not w.api.review_work(saved['uid'],saved['generation'])['production_allowed']
    with pytest.raises(PermissionError):w.api.work.issue(saved['uid'],saved['generation'],'SYN')
    assert w.api.work.get(saved['uid'])['phase']=='DRAFT' and not w.api.issues()
    reopened=EmissionAppearanceDialog(w);reopened.field.setCurrentIndex(reopened.field.findData('lote'))
    assert reopened.appearance.family.currentData()=='mono'
    reopened.restore_all();reopened.apply()
    assert 'trial_appearance' not in w.api.work.get(saved['uid'])['profile']
    for d in (dialog,reopened):d.hide();d.deleteLater()


def test_trial_can_only_create_documentary_draft_then_requires_external_evidence(studio,tmp_path,monkeypatch):
    w,s,app=studio;work=make_work(w)
    dialog=EmissionAppearanceDialog(w);dialog.field.setCurrentIndex(dialog.field.findData('lote'))
    select(dialog.appearance.family,'sans');dialog.font_size.setValue(9);dialog.changed();dialog.timer.stop()
    answers=iter(['R8C-SYN','SYNTHETIC typography','SYNTHETIC documentary reason'])
    monkeypatch.setattr(QInputDialog,'getText',lambda *_:(next(answers),True))
    dialog.create_variant();variant=w.api.variant(w.emission_work['binding']['variant_id'])
    assert variant['state']=='DRAFT' and not variant['approval_ref']
    assert w.emission_work['values']==work['values'] and 'trial_appearance' not in w.emission_work['profile']
    with pytest.raises(PermissionError):w.api.work.issue(w.emission_work['uid'],w.emission_work['generation'],'SYN')
    pending=w.api.transition_variant(variant['id'],variant['generation'],'PENDING','SYN')
    evidence=tmp_path/'SYNTHETIC-EXTERNAL.txt';evidence.write_text('SYNTHETIC isolated approval fixture',encoding='utf-8')
    approved=w.api.approve_variant(pending['id'],pending['generation'],'SYN QA','SYN EXTERNAL',date.today().isoformat(),evidence,'SYN')
    current=w.api.work.refresh_binding(w.emission_work['uid'],w.emission_work['generation'])
    issued,path,result=w.api.work.issue(current['uid'],current['generation'],'SYN')
    snap=json.loads(w.api.issue(issued['issue_id'])['design_snapshot_json'])
    assert snap['design']['layout']['fields'][0]['typography']['family']=='sans'
    assert snap['variant_approval']['evidence_sha256']==approved['evidence_sha256']
    historical=w.api.history.inspect(issued['issue_id']);assert historical['reprint_allowed']
    assert w.api._repository.db.execute('PRAGMA user_version').fetchone()[0]==4


def test_status_advanced_properties_saved_as_contract2_and_real_pdf(studio,tmp_path):
    w,s,app=studio;source=synthetic_source(tmp_path);uids=add_three(s.services.status_catalog,source)
    dialog=StatusFieldsDialog(s.services,s.services.status_catalog.get(uids[0]),w)
    dialog.quick_add_field();index=dialog.property_index
    item=dialog.shapes[index];select(dialog.text_appearance.family,'sans')
    dialog.example.setText('SYN-STATUS');dialog.commit_properties()
    assert dialog.design['contract']==2 and dialog.shapes[index] is item
    dialog.pdf_toggle.setChecked(True);dialog.pdf_timer.stop();dialog.refresh_pdf();assert dialog.pdf_preview.path
    with fitz.open(dialog.pdf_preview.path) as doc:assert 'SYN-STATUS' in doc[0].get_text()
    dialog.save();rec=s.services.status_catalog.get(uids[0]);saved=json.loads(rec['layout_json'])
    assert saved['contract']==2 and saved['fields'][index]['example']=='SYN-STATUS'
    reopened=StatusFieldsDialog(s.services,rec,w);assert reopened.design==saved
    reopened.reject();dialog.deleteLater();reopened.deleteLater()


def test_canvas_destruction_has_no_python_callback_exception(studio,monkeypatch):
    w,s,app=studio;w.open_editor();errors=[]
    monkeypatch.setattr(sys,'excepthook',lambda *args:errors.append(args))
    w.canvas.deleteLater();QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete);app.processEvents()
    assert not errors


def test_hidden_pdf_minimum_does_not_enlarge_status_geometry_and_tools_wrap(studio,tmp_path):
    w,s,app=studio;source=synthetic_source(tmp_path);uids=add_three(s.services.status_catalog,source)
    dialog=StatusFieldsDialog(s.services,s.services.status_catalog.get(uids[0]),w)
    dialog.pdf_preview.setMinimumWidth(1200) # hidden page must NOT widen canvas
    dialog.resize(1068,550);dialog.show();app.processEvents();dialog.resize(1068,550);app.processEvents()
    assert dialog.width()<=1068
    dialog.pdf_preview.setMinimumWidth(0);dialog.pdf_toggle.setChecked(True)
    dialog.resize(886,550);app.processEvents()
    pane=dialog.pdf_preview
    assert pane._editor_narrow and pane._editor_tool_grid.rowCount()>=2
    for control in (*pane._editor_tool_controls,pane.pages,pane.expand_button):
        assert pane.rect().contains(control.mapTo(pane,control.rect().center())),(control,pane.size())
    dialog.reject();dialog.deleteLater()


def test_status_native_scene_teardown_does_not_call_deleted_shapes(studio,tmp_path,monkeypatch):
    w,s,app=studio;source=synthetic_source(tmp_path);uids=add_three(s.services.status_catalog,source)
    dialog=StatusFieldsDialog(s.services,s.services.status_catalog.get(uids[0]),w);dialog.quick_add_field()
    errors=[];monkeypatch.setattr(sys,'excepthook',lambda *args:errors.append(args))
    dialog.view.deleteLater();QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
    app.processEvents();assert not errors
    dialog.deleteLater()


def test_proof_timers_stop_on_dialog_close_and_runtime_shutdown(studio):
    w,s,app=studio;make_work(w)
    dialog=EmissionAppearanceDialog(w);dialog.timer.start(10000);dialog.reject()
    assert not dialog.timer.isActive()
    w.editor_pdf_timer.start(10000);w.shutdown_runtime()
    assert not w.editor_pdf_timer.isActive()
    dialog.deleteLater()


def test_text_controls_follow_drawing_mode_without_reselecting(studio):
    w,s,app=studio;w.open_editor();select(w.text_appearance.family,'sans')
    select(w.draw_mode,'baseline')
    assert not w.text_appearance.wrap.isEnabled() and not w.text_appearance.valign.isEnabled()
    select(w.draw_mode,'textbox')
    assert w.text_appearance.wrap.isEnabled() and w.text_appearance.valign.isEnabled()
