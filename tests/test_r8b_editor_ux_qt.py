"""R8B real Qt interactions; disposable synthetic data, no GMP acceptance."""
import copy
import json
from pathlib import Path
import re
import pytest
pytest.importorskip('PySide6')
from PySide6.QtCore import Qt, QPointF, QSize, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QDialog, QMessageBox, QPushButton
from shiboken6 import isValid
from test_r3a_qt import studio
from test_r7a_status_qt import synthetic_source, add_three
from covex_label_manager.qt_ui.status_fields_dialog import StatusFieldsDialog


SIZES=[(1366,728),(1092,574),(910,472),(1920,1040),(1536,824),(1280,680)]


def test_same_87_capability_ids_and_names_are_retained():
    docs=Path(__file__).resolve().parents[1]/'docs'
    def entries(relative):
        return re.findall(r'^\| ([A-Z][0-9]{2}) \| ([^|]+)\|',(docs/relative).read_text(encoding='utf-8'),re.M)
    historical=entries('R6B_UX_INTEGRATED/CONSERVACION_87.md')
    assert len(historical)==87
    assert entries('R8B_EDITOR_UX/CONSERVACION_87.md')==historical


def test_capture_resizes_after_windows_initial_show_and_rejects_any_remaining_clamp(studio,monkeypatch):
    from covex_label_manager.qt_ui.editor_ux_checks import present_viewport
    from PySide6.QtWidgets import QWidget
    w,s,app=studio
    # A child viewport isolates this harness unit test from the runner's
    # physical desktop limit. Actual main windows are checked at exact sizes
    # by source/frozen offscreen captures AND by the native interaction suite.
    probe=QWidget(w)
    # Deterministically reproduce initial native desktop normalization.
    monkeypatch.setattr(probe,'show',lambda:probe.resize(820,450))
    target=QSize(1280,680)
    present_viewport(probe,target,app.processEvents)
    assert probe.size()==target
    probe.setMaximumSize(820,450)
    with pytest.raises(AssertionError,match='Requested client viewport not available'):
        present_viewport(probe,target,app.processEvents)


@pytest.mark.parametrize('width,height',SIZES)
def test_essential_properties_reachable_without_advanced_and_save_outside_scroll(studio,width,height):
    w,s,app=studio;w.resize(width,height);w.open_editor();app.processEvents()
    w.editor_advanced_button.setChecked(False);w.toggle_editor_advanced()
    assert not w.editor_advanced.isVisible()
    for control in (w.name_input,w.key_input,*w.spins.values(),w.font_size,w.bold,w.required,w.locked,w.draw_mode):
        assert control.isVisibleTo(w) and control.isEnabled()
        w.properties_scroll.ensureWidgetVisible(control);app.processEvents()
        viewport=w.properties_scroll.viewport()
        point=control.mapTo(viewport,control.rect().center())
        assert viewport.rect().contains(point),(control.accessibleName(),point,viewport.size())
    assert not w.properties_scroll.isAncestorOf(w.save_button)
    assert not w.tools_scroll.isAncestorOf(w.save_button)
    assert w.save_button.isVisibleTo(w) and w.save_button.mapTo(w,w.save_button.rect().bottomRight()).y()<w.height()
    assert w.width()<=width and w.height()<=height
    assert w.canvas.width()>=200 and w.canvas.height()>=height*.45
    assert w.properties_scroll.horizontalScrollBar().maximum()==0
    assert w.new_field_button.text()=='Añadir campo' and w.delete_field_button.text()=='Eliminar campo'
    assert w.editor_variant_menu_button.text()=='Gestionar variantes'


def test_add_and_draw_use_real_canvas_without_modal_and_keep_undo(studio,monkeypatch):
    w,s,app=studio;w.open_editor();app.processEvents()
    monkeypatch.setattr(QDialog,'exec',lambda *_:pytest.fail('Common field creation must not open a modal'))
    before=copy.deepcopy(w.design.state);count=len(w.fields)
    w.new_field_button.click();assert len(w.fields)==count+1
    assert w.selected_indices()==[count] and w.name_input.text()==f'Campo 1'
    w.undo_edit();assert w.design.state==before
    w.redo_edit();assert len(w.fields)==count+1
    w.draw_field_button.click();assert w.canvas.drawing
    start=w.canvas.mapFromScene(QPointF(w.image_w*.1,w.image_h*.35))
    end=w.canvas.mapFromScene(QPointF(w.image_w*.5,w.image_h*.45))
    QTest.mousePress(w.canvas.viewport(),Qt.MouseButton.LeftButton,pos=start)
    QTest.mouseMove(w.canvas.viewport(),end)
    QTest.mouseRelease(w.canvas.viewport(),Qt.MouseButton.LeftButton,pos=end)
    app.processEvents()
    assert not w.canvas.drawing and len(w.fields)==count+2
    assert len({f['key'] for f in w.fields})==count+2
    assert w.save_work()
    assert json.loads(s.services.version(w.current_editor_id)['fields_json'])==w.fields


def test_properties_adapt_to_large_label_and_numeric_font_metrics_without_horizontal_scroll(studio):
    w,s,app=studio;w.resize(1366,728);w.open_editor()
    w.properties_scroll.widget().setStyleSheet('QLabel, QDoubleSpinBox { font-size:20px; }')
    app.processEvents()
    assert w.properties_scroll.horizontalScrollBar().maximum()==0
    for control in w.spins.values():
        w.properties_scroll.ensureWidgetVisible(control);app.processEvents()
        assert w.properties_scroll.viewport().rect().contains(control.mapTo(w.properties_scroll.viewport(),control.rect().center()))


def test_replaced_work_note_cannot_overlay_the_canvas_before_deferred_deletion(studio):
    from PySide6.QtWidgets import QLabel
    w,s,app=studio;w.open_editor();app.processEvents()
    old_notes=[label for label in w.editor.findChildren(QLabel)
               if label.text().startswith('Fuente fija protegida · Diseño: guardado explícito')]
    assert all(not label.isVisibleTo(w) for label in old_notes)
    assert w.editor_document_note.isVisibleTo(w)


def test_typing_properties_preserves_items_selection_zoom_and_caret(studio):
    w,s,app=studio;w.open_editor();w.canvas.zoom(1.2);app.processEvents()
    zoom=w.canvas.transform();item=w.field_items[0]
    w.name_input.setFocus();w.name_input.selectAll();QTest.keyClicks(w.name_input,'SYNTHETIC visible name')
    assert w.fields[0]['label']=='SYNTHETIC visible name'
    assert w.name_input.cursorPosition()==len(w.name_input.text())
    assert w.field_items[0] is item and isValid(item)
    w.spins['x'].setValue(w.spins['x'].value()+1)
    assert w.field_items[0] is item and w.canvas.transform()==zoom and w.selected_indices()==[0]
    expected=copy.deepcopy(w.fields[0]);w.field_list.setCurrentRow(1)
    assert w.name_input.text()==w.fields[1]['label']
    w.field_list.setCurrentRow(0);assert w.name_input.text()==expected['label']
    assert w.save_work()
    assert json.loads(s.services.version(w.current_editor_id)['fields_json'])[0]==expected


def test_locked_field_controls_and_read_only_revision_no_bypass(studio,monkeypatch):
    w,s,app=studio;w.open_editor();w.locked.setChecked(True)
    assert not w.spins['x'].isEnabled() and not w.delete_field_button.isEnabled()
    assert 'bloqueado' in w.field_list.item(0).text()
    w.required.setChecked(True);assert 'obligatorio' in w.field_list.item(0).text()
    w.undo_edit();w.undo_edit()
    approved=next(r['version_id'] for r in w.rows if r['state']=='APPROVED')
    w.select_version(approved);w.open_editor()
    before=dict(s.services.version(approved));count=len(w.fields)
    w.quick_add_field();w.draw_new_field()
    assert len(w.fields)==count and not w.canvas.drawing
    assert not w.save_button.isEnabled() and not w.new_field_button.isEnabled()
    assert w.variant_edit_button.isVisibleTo(w) and w.variant_edit_button.isEnabled()
    assert 'Vigente' in w.editor_document_note.text()
    assert dict(s.services.version(approved))==before


def test_uncommitted_numeric_text_survives_selection_and_close_guard(studio,monkeypatch):
    w,s,app=studio;w.open_editor()
    before=w.fields[0]['x'];target=w.spins['x'].value()+1
    w.spins['x'].lineEdit().setText(f'{target:.3f} mm')
    w.field_list.setCurrentRow(1)
    assert w.fields[0]['x']>before
    w.spins['x'].lineEdit().setText(f'{w.spins["x"].value()+1:.3f} mm')
    monkeypatch.setattr(QMessageBox,'question',lambda *args:QMessageBox.StandardButton.Cancel)
    assert not w.resolve_work() and w.dirty
    assert w.save_work()
    assert json.loads(s.services.version(w.current_editor_id)['fields_json'])==w.fields


def test_existing_technical_tools_and_compatibility_remain_accessible(studio,monkeypatch):
    w,s,app=studio;w.open_editor()
    w.editor_advanced_button.setChecked(True);w.toggle_editor_advanced()
    for toggle,content in w.tool_sections.values():toggle.setChecked(True)
    tools={b.text():b for b in w.editor_advanced.findChildren(QPushButton)}
    for caption in ('Recorte visual / mm','Anclar a referencia','Relocalizar referencias',
                    'Borrado y continuación','Aplicar a selección','Reajuste proporcional',
                    'Formato físico y prueba','Zona de estado visual / mm','Añadir campo especial…',
                    'Editor anterior (compatibilidad)…','Restablecer diseño guardado'):
        assert caption in tools and tools[caption].isVisibleTo(w)
        w.tools_scroll.ensureWidgetVisible(tools[caption]);app.processEvents()
        assert w.tools_scroll.viewport().rect().contains(tools[caption].mapTo(w.tools_scroll.viewport(),tools[caption].rect().center()))
    calls=[];monkeypatch.setattr(w,'open_legacy',lambda target:calls.append(target))
    w.editor_legacy_button.click();assert calls==['editor']


def test_variant_command_opens_actual_menu_and_context_help(studio,monkeypatch):
    from PySide6.QtWidgets import QMenu
    w,s,app=studio;w.open_editor();menus=[];help_messages=[]
    class CapturedMenu(QMenu):
        def exec(self,*args):
            menus.append(self)
    monkeypatch.setattr('covex_label_manager.qt_ui.variants.QMenu',CapturedMenu)
    monkeypatch.setattr(QMessageBox,'information',lambda *args:help_messages.append(args[2]))
    w.editor_variant_menu_button.click()
    assert len(menus)==1
    menus[0].popup(w.mapToGlobal(w.rect().center()));app.processEvents()
    assert menus[0].isVisible();menus[0].hide()
    help_action=next(a for a in menus[0].actions() if a.text()=='¿Qué puedo hacer con este diseño?')
    help_action.trigger();assert 'pendiente' in help_messages[0].lower()
    assert not any(a.menu() for a in menus[0].actions())
    assert not s.services.issues()


def status_dialog(studio,tmp_path):
    w,s,app=studio
    uid=add_three(s.services.status_catalog,synthetic_source(tmp_path))[0]
    return StatusFieldsDialog(s.services,s.services.status_catalog.get(uid),w)


def test_status_numeric_selection_pending_properties_undo_and_reopen(studio,tmp_path):
    w,s,app=studio;d=status_dialog(studio,tmp_path);d.show();app.processEvents()
    d.quick_add_field();assert len(d.design['fields'])==1
    d.name.setText('SYNTHETIC retained on selection');d.quick_add_field()
    assert len(d.design['fields'])==2 and d.design['fields'][0]['label']=='SYNTHETIC retained on selection'
    d.items.setCurrentRow(0)
    old=copy.deepcopy(d.design);shape=d.shapes[0]
    d.spins['w'].setValue(d.spins['w'].value()*.9)
    assert d.apply_properties() and d.design!=old and isValid(shape)
    after=copy.deepcopy(d.design);d.undo_edit();assert d.design==old
    d.redo_edit();assert d.design==after
    d.save();assert d.result()==QDialog.DialogCode.Accepted
    again=StatusFieldsDialog(s.services,s.services.status_catalog.get(d.revision['uid']),w)
    assert again.design==after;again.reject()


def test_status_invalid_geometry_does_not_discard_pending_values_on_selection(studio,tmp_path,monkeypatch):
    w,s,app=studio;d=status_dialog(studio,tmp_path)
    d.quick_add_field();d.quick_add_field();d.items.setCurrentRow(0)
    before=copy.deepcopy(d.design);warnings=[]
    monkeypatch.setattr(QMessageBox,'warning',lambda *args:warnings.append(args))
    d.spins['w'].setValue(999);d.items.setCurrentRow(1)
    assert d.items.currentRow()==0 and d.spins['w'].value()==999
    assert d.design==before and warnings
    d.spins['w'].setValue(d.geometry_reference['w']);d.design=json.loads(d.revision['layout_json']);d.draw();d.reject()


def test_status_invalid_drag_restores_same_native_item_and_keeps_undo_available(studio,tmp_path):
    w,s,app=studio;d=status_dialog(studio,tmp_path);d.quick_add_field()
    before=copy.deepcopy(d.design);shape=d.shapes[0];position=shape.pos()
    shape.moveBy(-10000,0);shape.released()
    assert d.design==before and shape.pos()==position and isValid(shape)
    assert 'Cambio no realizado' in d.draw_hint.text()
    assert d.undo_button.isEnabled();d.undo_edit();assert not d.design['fields']
    d.reject()


@pytest.mark.parametrize('width,height',SIZES)
def test_status_properties_scroll_and_persistent_save(studio,tmp_path,width,height):
    w,s,app=studio;d=status_dialog(studio,tmp_path)
    d.show();d.fit_available(QSize(width-24,height-24));app.processEvents()
    assert d.width()<=width and d.height()<=height
    for widget in d.footer_widgets:
        assert widget.isVisibleTo(d) and widget.mapTo(d,widget.rect().bottomRight()).y()<d.height()
    assert d.properties_scroll.widget().layout() is not None
    assert d.properties_scroll.horizontalScrollBar().maximum()==0
    d.quick_add_field()
    for control in (d.key,d.name,*d.spins.values(),d.font_size,d.bold,d.required):
        d.properties_scroll.ensureWidgetVisible(control);app.processEvents()
        assert d.properties_scroll.viewport().rect().contains(control.mapTo(d.properties_scroll.viewport(),control.rect().center()))
    assert d.view.width()>=160
    d.design=json.loads(d.revision['layout_json']);d.draw()
    d.reject()
