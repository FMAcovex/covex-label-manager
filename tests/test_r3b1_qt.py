"""Native advanced editor regression, exclusively on disposable synthetic PDFs."""
import copy
import json
import pytest
pytest.importorskip('PySide6')
from PySide6.QtCore import Qt, QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QMessageBox, QDialog, QApplication
from test_r3a_qt import studio
from covex_label_manager.editor_layout import recrop, anchor_field, source_identity
from covex_label_manager.qt_ui.advanced_editor import RectangleDialog


def test_geometry_undo_redo_save_and_navigation(studio):
    w,s,app=studio; w.open_editor(); before=copy.deepcopy(w.design.state)
    w.spins['x'].setValue(w.spins['x'].value()+1)
    after=copy.deepcopy(w.design.state); assert after!=before and w.undo_button.isEnabled()
    w.undo_button.click(); assert w.design.state==before and not w.dirty
    w.redo_button.click(); assert w.design.state==after
    w.navigate('library'); w.navigate('editor'); assert w.design.state==after
    assert w.save_work(); w.undo_edit(); assert w.design.state==before and w.dirty
    w.redo_edit(); assert not w.dirty


def test_crop_status_one_command_and_atomic_exclusion(studio,monkeypatch):
    w,s,app=studio; w.open_editor(); before=copy.deepcopy(w.design.state)
    candidate=recrop(before,[5,5,427,295]); candidate['area']=[.1,.1,.2,.1]
    assert w.command('crop+state',candidate)
    assert w.editor_version['base_w_mm']==pytest.approx(422*25.4/72)
    w.undo_edit(); assert w.design.state==before
    w.redo_edit(); assert w.design.state==candidate and w.save_work()
    saved=s.services.version(w.current_editor_id)
    assert json.loads(saved['status_area_json'])==candidate['area']
    assert json.loads(saved['crop_json'])==candidate['crop']
    assert s.services.version(w.current_editor_id)['state']=='PENDING'


def test_stale_status_and_integrity_are_blocked(studio,monkeypatch):
    w,s,app=studio; w.open_editor(); w.spins['x'].setValue(w.spins['x'].value()+1)
    monkeypatch.setattr(QMessageBox,'warning',lambda *a,**k:None)
    original=s.services.version(w.current_editor_id)
    s.services.replace_pending_fields(w.current_editor_id,json.loads(original['fields_json']),status_area=[.1,.1,.2,.1])
    assert not w.save_work() and w.dirty


def test_locked_numeric_multi_alignment_and_template_cannot_move(studio,monkeypatch):
    w,s,app=studio; w.open_editor(); w.locked.setChecked(True)
    assert not w.spins['x'].isEnabled()
    before=copy.deepcopy(w.design.state)
    w.spins['x'].setValue(99); assert w.design.state==before
    w.field_list.item(1).setSelected(True)
    monkeypatch.setattr(QMessageBox,'warning',lambda *a,**k:None)
    w.align_selection(); assert w.design.state==before
    candidate=copy.deepcopy(before); candidate['fields'][0]['x']+=.1
    assert not w.command('locked bypass',candidate) and w.design.state==before


def test_canvas_and_list_keep_multiple_selection(studio):
    w,s,app=studio; w.open_editor()
    w.field_list.item(1).setSelected(True)
    assert w.selected_indices()==[0,1]
    assert {i.index for i in w.canvas.scene().selectedItems()}=={0,1}
    w.canvas.scene().clearSelection(); w.field_items[2].setSelected(True); w.field_items[3].setSelected(True)
    assert w.selected_indices()==[2,3]


def test_graphical_drag_is_one_command_and_undo(studio):
    w,s,app=studio; w.open_editor(); app.processEvents(); before=copy.deepcopy(w.design.state)
    item=w.field_items[0]; start=w.canvas.mapFromScene(item.sceneBoundingRect().center())
    QTest.mousePress(w.canvas.viewport(),Qt.MouseButton.LeftButton,pos=start)
    QTest.mouseMove(w.canvas.viewport(),start+QPoint(12,8),delay=20)
    QTest.mouseRelease(w.canvas.viewport(),Qt.MouseButton.LeftButton,pos=start+QPoint(12,8)); app.processEvents()
    assert w.design.state!=before and len(w.design.undo_states)==1
    w.undo_edit(); assert w.design.state==before


def test_anchor_saved_and_relocatable_without_schema_change(studio):
    w,s,app=studio; w.open_editor(); span=next(x for x in s.services.editor_spans(w.current_editor_id) if x['text']=='LOTE')
    candidate=anchor_field(w.design.state,0,span,0,w.editor_version['pdf_sha256'])
    assert w.command('anchor',candidate) and w.save_work()
    field=json.loads(s.services.version(w.current_editor_id)['fields_json'])[0]
    assert field['anchor']['text']=='LOTE' and field['draw']=='baseline'
    assert 'anchor' not in json.loads(s.services.version(next(v['id'] for v in s.services.versions(w.row['id']) if v['state']=='APPROVED'))['fields_json'])[0]


def test_native_crop_dialog_coordinate_selection(studio,monkeypatch):
    w,s,app=studio; w.open_editor(); before=copy.deepcopy(w.design.state)
    image,bounds,_=s.services.master_preview(w.editor_version)
    dialog=RectangleDialog(w,'Synthetic crop',image,list(bounds),before['crop'],20)
    dialog.from_drag([5,5,427,295]); dialog.accept_valid()
    assert dialog.result()==QDialog.DialogCode.Accepted
    assert dialog.rect==pytest.approx([5,5,427,295],abs=.002)
    dialog.from_drag([0,0,1,1]); dialog.setResult(0); dialog.accept_valid()
    assert dialog.result()!=QDialog.DialogCode.Accepted


def test_proof_uses_engine_and_never_saves_design_or_issues(studio):
    import fitz
    w,s,app=studio; w.open_editor(); before=dict(s.services.version(w.current_editor_id)); issues=len(s.services.issues())
    profile=dict(name='Synthetic',width_mm=100,height_mm=70,margin_mm=8,gap_mm=3,safety_mm=0,orientation='portrait',start_slot=1)
    path,warnings=s.services.preview_editor_layout(w.current_editor_id,w.design.state,profile)
    with fitz.open(path) as pdf:
        text=pdf[0].get_text(); assert 'PRUEBA' in text.upper()
    assert dict(s.services.version(w.current_editor_id))==before and len(s.services.issues())==issues


def test_retired_and_companion_block_new_editor_operations(studio,monkeypatch):
    w,s,app=studio; w.open_editor(); before=copy.deepcopy(w.design.state)
    w.legacy_process=object(); w.recheck_actions()
    candidate=copy.deepcopy(before); candidate['fields'][0]['x']+=.01
    assert not w.command('busy',candidate) and not w.undo_button.isEnabled()
    w.legacy_process=None
    vid=next(r['version_id'] for r in w.rows if r['state']=='RETIRED'); w.select_version(vid); w.open_editor()
    assert not w.editable() and all(not b.isEnabled() for b in w.design_buttons)
    with pytest.raises(ValueError): s.services.preview_editor_layout(vid,w.design.state,dict(width_mm=100,height_mm=70))


def test_unrecognized_template_does_not_fall_back_to_another_document(studio):
    w,s,app=studio; w.open_editor()
    with pytest.raises(ValueError,match='Sin plantilla reconocida'):
        s.services.editor_template_layout(w.current_editor_id,w.design.state['crop'])


def test_pdf_baseline_matches_editor_coordinates_and_physical_scale(studio):
    import fitz
    from covex_label_manager.engine import render_emission, MM
    from covex_label_manager.editor_layout import version_with_layout
    w,s,app=studio; w.open_editor()
    span=next(x for x in s.services.editor_spans(w.current_editor_id) if x['text']=='LOTE')
    candidate=anchor_field(w.design.state,0,span,0,w.editor_version['pdf_sha256'])
    v=version_with_layout(w.editor_version,candidate)
    profile=dict(width_mm=100,height_mm=70,margin_mm=8,gap_mm=3,safety_mm=0,orientation='portrait',start_slot=1)
    path=s.services.output_path('cache','synthetic-position-proof.pdf')
    render_emission(v,s.services._repository.root,{'lote':'SYNLOT','pn':'1','pb':'2'},profile,[1],1,1,path,test_mode=True)
    crop=candidate['crop']; factor=min(100*MM/(crop[2]-crop[0]),70*MM/(crop[3]-crop[1]))
    dw=(crop[2]-crop[0])*factor; dh=(crop[3]-crop[1])*factor
    x0=8*MM+(100*MM-dw)/2; y0=8*MM+(70*MM-dh)/2
    with fitz.open(path) as pdf:
        spans=[sp for b in pdf[0].get_text('dict')['blocks'] for line in b.get('lines',[]) for sp in line['spans']]
        emitted=next(sp for sp in spans if sp['text']=='SYNLOT')
        expected=(x0+candidate['fields'][0]['x']*dw,y0+candidate['fields'][0]['y']*dh)
        assert emitted['origin']==pytest.approx(expected,abs=.02)  # 0.0071 mm in PDF coordinates
        assert emitted['size']==pytest.approx(candidate['fields'][0]['font_pt']*factor,abs=.02)


def test_status_dialog_commits_and_undo_recovers_entire_design(studio,monkeypatch):
    w,s,app=studio; w.open_editor(); before=copy.deepcopy(w.design.state)
    def accept(dialog):
        dialog.from_drag([10,200,100,240]); return QDialog.DialogCode.Accepted
    monkeypatch.setattr(RectangleDialog,'exec',accept)
    w.edit_status_area(); assert w.design.state['area'] and w.dirty
    w.undo_edit(); assert w.design.state==before


def test_crop_dialog_cancellation_does_not_change_design(studio,monkeypatch):
    w,s,app=studio; w.open_editor(); before=copy.deepcopy(w.design.state)
    monkeypatch.setattr(RectangleDialog,'exec',lambda *_:QDialog.DialogCode.Rejected)
    w.edit_crop(); assert w.design.state==before and not w.dirty


def test_output_dialog_opens_with_real_sheet_plan(studio,monkeypatch):
    w,s,app=studio; w.open_editor(); opened=[]
    def cancel(dialog):
        from PySide6.QtWidgets import QLabel
        text=' '.join(x.text() for x in dialog.findChildren(QLabel))
        opened.append(text); return QDialog.DialogCode.Rejected
    monkeypatch.setattr(QDialog,'exec',cancel)
    w.edit_output(); assert any('Etiqueta impresa:' in x and 'casillas' in x for x in opened)
