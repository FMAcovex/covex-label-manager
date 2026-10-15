"""Real PySide6 mouse and numeric interactions on disposable synthetic data."""
import copy
import pytest
pytest.importorskip('PySide6')
from PySide6.QtCore import Qt,QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QDialog,QLineEdit,QDialogButtonBox,QMessageBox
from test_r3a_qt import studio
from test_r3e_layout import profile
from covex_label_manager.qt_ui.sheet_designer import SheetDesigner
from covex_label_manager.qt_ui.advanced_editor import RectangleDialog


def test_create_field_by_button_draw_save_reopen_and_undo(studio,monkeypatch):
    w,s,app=studio;w.open_editor();before=copy.deepcopy(w.design.state)
    def fill(d):
        if isinstance(d,RectangleDialog):
            d.from_drag([40,80,140,105]);return QDialog.DialogCode.Accepted
        entries=d.findChildren(QLineEdit);entries[0].setText('synthetic_extra');entries[1].setText('Synthetic extra');return QDialog.DialogCode.Accepted
    monkeypatch.setattr(QDialog,'exec',fill)
    w.draw_field_button.click();assert len(w.fields)==len(before['fields'])+1
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
