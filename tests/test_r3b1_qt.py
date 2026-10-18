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
    assert dialog.selection_rect==pytest.approx([5,5,427,295],abs=.002)
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


@pytest.mark.parametrize('operation',['crop','anchor','move','scale'])
@pytest.mark.parametrize('physical_size',[(100,70),(140,100)])
def test_representative_payloads_after_layout_changes(studio,operation,physical_size):
    """Real engine, long lot, EU masses, quantity and five-digit vessel numbers."""
    import fitz
    from covex_label_manager.engine import render_emission
    from covex_label_manager.editor_layout import version_with_layout,move_field,scale_fields
    w,s,app=studio; w.open_editor(); layout=copy.deepcopy(w.design.state)
    layout['fields'].append(dict(key='cantidad',label='Cantidad sintética',x=.6,y=.79,w=.28,h=.07,font_pt=10))
    if operation=='crop': layout=recrop(layout,[5,5,427,295])
    elif operation=='anchor':
        span=next(x for x in s.services.editor_spans(w.current_editor_id) if x['text']=='LOTE')
        layout=anchor_field(layout,0,span,0,w.editor_version['pdf_sha256'])
    elif operation=='move': move_field(layout['fields'][0],.02,.02,layout['crop'])
    else: layout=scale_fields(layout,list(range(len(layout['fields']))),.95)
    version=version_with_layout(w.editor_version,layout)
    profile=dict(width_mm=physical_size[0],height_mm=physical_size[1],margin_mm=8,gap_mm=3,safety_mm=0)
    path=s.services.output_path('cache',f'payload-{operation}-{physical_size[0]}.pdf')
    values=dict(lote='LOT-2026-SINTETICO-ABC-000123',pn='1000000,125',pb='1000010,875',cantidad='123456,789')
    before=dict(s.services.version(w.current_editor_id)); issues=len(s.services.issues())
    render_emission(version,s.services._repository.root,values,profile,[1,12345],12345,1,path,test_mode=True,
                    per_container={'12345':dict(pn='0,3558',pb='0,4558',cantidad='99999,999')})
    with fitz.open(path) as pdf:
        # Arial's PDF Unicode map extracts its hyphen glyph as U+00AD on Windows.
        # Normalize this representation only; do not discard or shorten payload text.
        text=' '.join(p.get_text() for p in pdf).replace('\u00ad','-')
        for value in [values['lote'],values['pn'],values['pb'],values['cantidad'],'12345/12345','0,3558','99999,999']:
            assert value in text
        assert 'PRUEBA' in text
    assert dict(s.services.version(w.current_editor_id))==before
    assert len(s.services.issues())==issues


@pytest.mark.parametrize('operation',['crop','anchor','move','scale'])
@pytest.mark.parametrize('overflow_field',['lote','cantidad','pn','numero'])
def test_pdf_rejects_overflow_after_layout_changes(studio,operation,overflow_field):
    from covex_label_manager.engine import render_emission,LayoutError
    from covex_label_manager.editor_layout import version_with_layout,move_field,scale_fields
    w,s,app=studio; w.open_editor(); layout=copy.deepcopy(w.design.state)
    layout['fields'].append(dict(key='cantidad',label='Cantidad',x=.6,y=.88,w=.2,h=.07,font_pt=12))
    target=next(f for f in layout['fields'] if f['key']==overflow_field)
    target['draw']='baseline'
    if overflow_field in ('pn','numero'): target['w']=.012
    if operation=='crop': layout=recrop(layout,[5,5,427,295])
    elif operation=='anchor':
        span=next(x for x in s.services.editor_spans(w.current_editor_id) if x['text']=='LOTE')
        layout=anchor_field(layout,0,span,0,w.editor_version['pdf_sha256'])
    elif operation=='move': move_field(layout['fields'][0],.02,.02,layout['crop'])
    else: layout=scale_fields(layout,list(range(len(layout['fields']))),.8)
    path=s.services.output_path('cache','must-not-exist.pdf'); issues=len(s.services.issues())
    with pytest.raises(LayoutError,match='no cabe'):
        render_emission(version_with_layout(w.editor_version,layout),s.services._repository.root,
                        dict(lote='X'*200 if overflow_field=='lote' else 'LOT-SYN',cantidad='X'*200 if overflow_field=='cantidad' else '1',
                             pn='9999999' if overflow_field=='pn' else '1',pb='99999999'),
                        dict(width_mm=100,height_mm=70),[12345],12345,1,path,test_mode=True)
    assert not path.exists() and len(s.services.issues())==issues


def test_saved_pending_layout_survives_window_and_database_reopen(studio,monkeypatch):
    from types import SimpleNamespace
    from covex_label_manager.storage import Store
    from covex_label_manager.qt_transition import TransitionServices
    from covex_label_manager.qt_ui.functional import FunctionalWindow
    from covex_label_manager.editor_layout import layout_from_version,move_field
    w,s,app=studio; w.open_editor(); initial=copy.deepcopy(w.design.state); vid=w.current_editor_id
    monkeypatch.setattr(QMessageBox,'warning',lambda *a,**k:None)
    span=next(x for x in s.services.editor_spans(vid) if x['text']=='LOTE')
    candidate=anchor_field(initial,0,span,0,w.editor_version['pdf_sha256'])
    candidate['fields'][1].update(draw='continuation',erase=[.1,.59,.33,.1],second_x=.1,next_w=.3,max_lines=2)
    candidate=recrop(candidate,[5,5,430,295]); candidate['area']=[.7,.82,.2,.1]
    assert w.command('Full pending design',candidate)
    w.undo_edit(); assert w.design.state==initial
    w.redo_edit(); assert w.design.state==candidate
    assert w.save_work(); w.undo_edit(); assert w.dirty and w.design.state==initial
    w.redo_edit(); assert not w.dirty and w.design.state==candidate
    assert w.close(); w.legacy_timer.stop(); w.poll_timer.stop()
    root=s.services._repository.root; s.services.close()
    services=TransitionServices(Store(root,seed=False)); s.services=services
    reopened=FunctionalWindow(SimpleNamespace(services=services,initial_id=vid,fictional=True))
    try:
        reopened.show(); reopened.open_editor(); app.processEvents()
        assert reopened.editor_version['state']=='PENDING'
        assert reopened.design.state==candidate==layout_from_version(services.version(vid))
        # Undo history is session-local, not a persistent design/work archive.
        assert not reopened.undo_button.isEnabled() and not reopened.redo_button.isEnabled()
        changed=copy.deepcopy(candidate); move_field(changed['fields'][0],-.01,0,changed['crop'])
        assert reopened.command('Move after reopening',changed)
        reopened.undo_edit(); assert reopened.design.state==candidate and not reopened.dirty
        reopened.redo_edit(); assert reopened.design.state==changed and reopened.dirty
        assert reopened.save_work()
        reopened.undo_edit(); assert reopened.design.state==candidate and reopened.dirty
        reopened.redo_edit(); assert reopened.design.state==changed and not reopened.dirty
    finally:
        reopened.dirty=False; reopened.legacy_timer.stop(); reopened.poll_timer.stop()
        reopened.close(); reopened.deleteLater(); app.processEvents()


def test_relocation_confirmation_and_scale_descriptions(studio,monkeypatch):
    from PySide6.QtWidgets import QPushButton
    w,s,app=studio; w.open_editor(); messages=[]
    monkeypatch.setattr(QMessageBox,'question',lambda parent,title,message,*a:(messages.append(message),QMessageBox.StandardButton.No)[1])
    w.relocate()
    span=next(x for x in s.services.editor_spans(w.current_editor_id) if x['text']=='LOTE')
    assert w.command('Anchor',anchor_field(w.design.state,0,span,0,w.editor_version['pdf_sha256']))
    w.relocate()
    assert 'plantilla reconocida' in messages[0] and 'anclas verificables' in messages[1]
    assert all('No adapta automáticamente' in m and 'Word/PDF' in m for m in messages)
    buttons={b.text():b for b in w.editor_advanced.findChildren(QPushButton)}
    assert 'campos seleccionados' in buttons['Reajuste proporcional'].toolTip()
    assert 'etiqueta completa' in w.format_button.toolTip()
