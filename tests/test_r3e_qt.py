"""Real PySide6 mouse and numeric interactions on disposable synthetic data."""
import copy
import pytest
pytest.importorskip('PySide6')
from PySide6.QtCore import Qt,QPoint,QPointF
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QDialog,QLineEdit,QDialogButtonBox,QMessageBox
from test_r3a_qt import studio
from test_r3e_layout import profile
from covex_label_manager.qt_ui.sheet_designer import SheetDesigner
from covex_label_manager.qt_ui.advanced_editor import RectangleDialog


def test_create_field_by_button_draw_save_reopen_and_undo(studio,monkeypatch):
    w,s,app=studio;w.open_editor();before=copy.deepcopy(w.design.state)
    monkeypatch.setattr(QDialog,'exec',lambda *_:pytest.fail('R8B drawing is on the canvas, not a modal'))
    w.draw_field_button.click();app.processEvents();assert w.canvas.drawing
    start=w.canvas.mapFromScene(QPointF(w.image_w*.1,w.image_h*.3))
    end=w.canvas.mapFromScene(QPointF(w.image_w*.4,w.image_h*.4))
    QTest.mousePress(w.canvas.viewport(),Qt.MouseButton.LeftButton,pos=start)
    QTest.mouseMove(w.canvas.viewport(),end)
    QTest.mouseRelease(w.canvas.viewport(),Qt.MouseButton.LeftButton,pos=end);app.processEvents()
    assert not w.canvas.drawing and len(w.fields)==len(before['fields'])+1
    after=copy.deepcopy(w.design.state);w.undo_edit();assert w.design.state==before
    w.redo_edit();assert w.design.state==after;assert w.save_work()
    w.design=None;w.current_editor_id=None;w.open_editor();assert w.design.state==after


def test_eight_field_handles_mouse_resize_is_single_command(studio):
    w,s,app=studio;w.open_editor();app.processEvents();before=copy.deepcopy(w.design.state)
    item=w.field_items[0];assert len(item.handles)==8
    handle=item.handles[4];start=w.canvas.mapFromScene(handle.scenePos())
    QTest.mousePress(w.canvas.viewport(),Qt.MouseButton.LeftButton,pos=start)
    QTest.mouseMove(w.canvas.viewport(),start+QPoint(10,0),delay=30)
    QTest.mouseRelease(w.canvas.viewport(),Qt.MouseButton.LeftButton,pos=start+QPoint(10,0));app.processEvents()
    assert w.fields[0]['w']!=before['fields'][0]['w'];assert len(w.design.undo_states)==1
    w.undo_edit();assert w.design.state==before


def test_sheet_mouse_geometry_undo_cancel_and_errors(studio):
    w,s,app=studio;d=SheetDesigner(w,profile('A3'),root=s.services._repository.root);d.show();app.processEvents();d.view.fit()
    before=copy.deepcopy(d.profile);item=d.items[0];item.setSelected(True)
    # shrink with actual right handle; no collision
    start=d.view.mapFromScene(item.handles[4].scenePos())
    QTest.mousePress(d.view.viewport(),Qt.MouseButton.LeftButton,pos=start)
    QTest.mouseMove(d.view.viewport(),start-QPoint(14,0),delay=30)
    QTest.mouseRelease(d.view.viewport(),Qt.MouseButton.LeftButton,pos=start-QPoint(14,0));app.processEvents()
    assert d.profile['slots'][0]['width']<before['slots'][0]['width']
    d.undo();assert d.profile==before;d.redo();assert d.profile!=before
    bad=copy.deepcopy(d.profile);bad['slots'][0]['x']=-5;d.push(bad,'Synthetic invalid')
    assert not d.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled();assert 'límites' in d.error.text()
    d.reject();assert before==profile('A3')


def test_approved_revision_only_offers_variant(studio):
    w,s,app=studio;vid=next(v['id'] for v in s.services.versions(w.row['id']) if v['state']=='APPROVED');w.select_version(vid);w.open_editor()
    assert not w.new_field_button.isEnabled();assert not w.draw_field_button.isEnabled();assert w.variant_edit_button.isVisible()
    assert all(not i.handles for i in w.field_items)
    w.resize(910,512);app.processEvents()
    assert w.new_field_button.isVisible() and w.draw_field_button.isVisible() and w.variant_edit_button.isVisible()


def test_designer_applies_by_repository_and_invalidates_pdf(studio,monkeypatch):
    w,s,app=studio;work=w.api.work.create(w.row['version_id'],None,'Synthetic designer integration');w.load_emission_work(work['uid'])
    def accept(d):
        d.paper.setCurrentText('A3');d.count.setValue(5);d.arrange();return QDialog.DialogCode.Accepted
    monkeypatch.setattr(SheetDesigner,'exec',accept)
    w.emission_panel.design_sheet()
    saved=w.api.work.get(work['uid']);assert saved['generation']==work['generation']+1
    assert saved['profile']['paper']=='A3' and len(saved['profile']['slots'])==5
    assert w.work_preview is None


def test_sheet_light_palette_even_with_dark_application(studio):
    from PySide6.QtGui import QPalette,QColor
    w,s,app=studio;original=app.palette();dark=QPalette(original)
    dark.setColor(QPalette.ColorRole.Window,QColor('#101010'));dark.setColor(QPalette.ColorRole.Base,QColor('#121212'));app.setPalette(dark)
    try:
        d=SheetDesigner(w,profile());assert d.palette().color(QPalette.ColorRole.Window).lightness()>220
        assert d.palette().color(QPalette.ColorRole.Base).lightness()>220
    finally:app.setPalette(original)


def test_sheet_canvas_keeps_calibration_offsets_in_mm(studio):
    from covex_label_manager.sheet_layout import slots
    w,s,app=studio;p=profile('A3',1);p.update(offset_x_mm=2,offset_y_mm=3)
    p['slots'][0].update(width=100,height=60)
    d=SheetDesigner(w,p);b=slots(p)[0];item=d.items[0]
    assert (item.x(),item.y())==(b.x,b.y)
    item.setSelected(True);item.moveBy(4,5);d.gesture()
    assert d.profile['slots'][0]['x']==p['slots'][0]['x']+4
    assert d.profile['slots'][0]['y']==p['slots'][0]['y']+5
    assert (d.items[0].x(),d.items[0].y())==(b.x+4,b.y+5)
    d.items[0].setSelected(True);d.box_inputs['x'].setValue(20);d.numeric_box()
    assert d.items[0].x()==20 and d.profile['slots'][0]['x']==18


def test_designer_proof_rejects_document_changed_while_open(studio,monkeypatch):
    import json
    from covex_label_manager.emission_work import WorkConflict
    w,s,app=studio;vid=w.row['version_id'];work=w.api.work.create(vid,None,'Synthetic stale proof');w.load_emission_work(work['uid'])
    def stale(d):
        fields=json.loads(w.api.version(vid)['fields_json']);fields[0]['x']+=.01
        w.api.replace_pending_fields(vid,fields)
        with pytest.raises(WorkConflict):d.proof(d.profile,d)
        return QDialog.DialogCode.Rejected
    monkeypatch.setattr(SheetDesigner,'exec',stale)
    monkeypatch.setattr(w.api,'render',lambda *a,**k:pytest.fail('Stale work must not reach renderer'))
    w.emission_panel.design_sheet()
    assert w.api.work.get(work['uid'])['generation']==work['generation']


def test_corrupt_visual_profile_does_not_prevent_native_windows(studio):
    from covex_label_manager.layout_profiles import LayoutProfiles
    from covex_label_manager.qt_ui.work import WorkPanel
    w,s,app=studio
    root=s.services._repository.root
    valid=LayoutProfiles(root).save('good-r3e','Perfil válido',profile('A3',5))
    damaged=root/'layout_profiles'/'bad-r3e.json'
    damaged.write_text('not valid JSON',encoding='utf-8')
    original=damaged.read_bytes()
    panel=WorkPanel(w)
    assert any(panel.profile_choice.itemText(i)=='Perfil válido' for i in range(panel.profile_choice.count()))
    assert 'no legibles' in panel.profile_corruption_warning.text()
    dialog=SheetDesigner(w,profile('A4'),root=root)
    assert any(dialog.saved.itemText(i)=='Perfil válido' for i in range(dialog.saved.count()))
    assert 'no legibles' in dialog.profile_corruption_warning.text()
    assert LayoutProfiles(root).get('good-r3e')==valid
    assert damaged.read_bytes()==original


def test_mass_fields_accept_kg_in_native_work_without_altering_saved_text(studio):
    from PySide6.QtWidgets import QLineEdit
    from covex_label_manager.vessels import validate_vessel_masses
    w,s,app=studio
    work=s.services.work.create(s.initial_id,name='Pesos sintéticos con kg')
    assert w.load_emission_work(work['uid'])
    panel=w.emission_panel
    assert isinstance(panel.value_inputs['pn'],QLineEdit)
    assert isinstance(panel.value_inputs['pb'],QLineEdit)
    assert 'kg' in panel.value_inputs['pn'].placeholderText()
    panel.value_inputs['pn'].setText('0,3558 kg')
    panel.value_inputs['pb'].setText('0,500 KG')
    panel.changed()
    assert w.flush_emission_work()
    saved=s.services.work.get(work['uid'])
    assert saved['values']['pn']=='0,3558 kg'
    assert saved['values']['pb']=='0,500 KG'
    validate_vessel_masses(saved['values'],1)
    w.refresh_work_panels()
    assert w.emission_panel.value_inputs['pn'].text()=='0,3558 kg'
    assert w.editor_work_panel.value_inputs['pb'].text()=='0,500 KG'

def test_approved_field_adjustment_guides_to_draft_variant(studio,monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    w,s,app=studio
    approved=next(v['id'] for v in s.services.versions(w.row['id']) if v['state']=='APPROVED')
    w.select_version(approved);w.open_editor()
    original=s.services.version(approved)
    assert w.variant_edit_button.isEnabled()
    assert not w.spins['x'].isEnabled()
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**kw:QMessageBox.StandardButton.Yes)
    monkeypatch.setattr(w,'ask_form',lambda title,fields:{
        'code':'AJUSTE-001','name':'Ajuste ficticio de campos','reason':'Prueba de posición'})
    w.editable_variant()
    assert w.current_variant_id is not None
    variant=s.services.variant(w.current_variant_id)
    assert variant['state']=='DRAFT'
    assert w.spins['x'].isEnabled()
    assert not s.services.eligibility(approved,True,w.current_variant_id)[0]
    assert s.services.version(approved)['pdf_sha256']==original['pdf_sha256']
    assert s.services.version(approved)['fields_json']==original['fields_json']

def test_guided_field_adjustment_prefills_identity_and_requires_reason(studio,monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    w,s,app=studio
    approved=next(v['id'] for v in s.services.versions(w.row['id']) if v['state']=='APPROVED')
    w.select_version(approved);w.open_editor()
    original=s.services.version(approved)
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**kw:QMessageBox.StandardButton.Yes)
    forms=[]
    def empty_reason(title,fields):
        forms.append((title,fields))
        return {key:value for key,text,value in fields}
    monkeypatch.setattr(w,'ask_form',empty_reason)
    warnings=[]
    monkeypatch.setattr(QMessageBox,'warning',lambda *a: warnings.append(str(a[-1])))
    count=len(s.services.variants(approved))
    w.editable_variant()
    assert forms and forms[0][1][0][2]=='CAMPOS-001'
    assert forms[0][1][1][2]=='Ajuste de campos variables 001'
    assert warnings and 'Motivo obligatorio' in warnings[-1]
    assert len(s.services.variants(approved))==count
    def justified(title,fields):
        return {**{key:value for key,text,value in fields},'reason':'Reubicación operativa ficticia'}
    monkeypatch.setattr(w,'ask_form',justified)
    w.editable_variant()
    variant=s.services.variant(w.current_variant_id)
    assert variant['code']=='CAMPOS-001' and variant['state']=='DRAFT'
    assert s.services.version(approved)['fields_json']==original['fields_json']
    assert s.services.version(approved)['pdf_sha256']==original['pdf_sha256']
    assert not s.services.eligibility(approved,True,w.current_variant_id)[0]
