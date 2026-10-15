"""Packaged/source native editor proof on the existing synthetic demo only."""
import copy
import json
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtWidgets import QDialog, QListWidget, QPushButton
from .advanced_editor import RectangleDialog
from ..editor_layout import recrop, anchor_field, relocate_anchors, align_fields, scale_fields


def exercise_advanced(w,app,captures=None):
    checks=[]
    def check(value,title):
        assert value,title
        checks.append('R3B1: '+title)
    def settle():
        for _ in range(3): app.processEvents(); QTest.qWait(25)
    def snap(title):
        settle()
        if captures: assert w.grab().save(str(captures/title))
    w.resize(1500,980); w.select_version(w.session.initial_id); w.open_editor(); settle()
    original=copy.deepcopy(w.design.state); source=w.editor_version['pdf_sha256']; previous=len(w.api.issues())
    w.editor_advanced_button.setChecked(True); w.toggle_editor_advanced()
    w.tool_sections['Documento'][0].setChecked(True); settle()
    check(w.tool_sections['Documento'][1].isVisible(),'Native document section opens')
    snap('R3B1_Editor_Documento_Pendiente.png')
    def capture_dialog(method,title,prepare=None):
        errors=[]; seen=[]
        def visit():
            dialog=app.activeModalWidget()
            try:
                assert isinstance(dialog,QDialog),'Expected native modal dialog'
                if prepare: prepare(dialog)
                settle(); seen.append(dialog.windowTitle())
                if captures: assert dialog.grab().save(str(captures/title))
            except Exception as error: errors.append(str(error))
            finally:
                if dialog: dialog.reject()
        QTimer.singleShot(150,visit); method()
        check(bool(seen) and not errors,'Native dialog captured: '+title+' '+str(errors))
    def select_anchor(dialog):
        ls=dialog.findChild(QListWidget)
        row=next(i for i in range(ls.count()) if 'LOTE' in ls.item(i).text())
        ls.setCurrentRow(row)
    capture_dialog(w.edit_crop,'R3B1_Dialogo_Recorte_Visual.png',lambda d:d.from_drag([5,5,427,295]))
    capture_dialog(w.edit_anchor,'R3B1_Dialogo_Anclaje.png',select_anchor)
    capture_dialog(w.edit_scale,'R3B1_Dialogo_Reajuste_Proporcional.png')
    capture_dialog(w.edit_status_area,'R3B1_Dialogo_Zona_Estado.png',lambda d:d.from_drag([300,245,400,280]))
    def preview_from_output(dialog):
        # Capture the actual nested preview; cancel both dialogs without saving a profile.
        capture_dialog(lambda:next(b for b in dialog.findChildren(QPushButton) if b.text()=='Ver PDF de prueba').click(),
                       'R3B1_Dialogo_PDF_Prueba.png')
    capture_dialog(w.edit_output,'R3B1_Dialogo_Formato_Fisico.png',preview_from_output)
    image,bounds,_=w.api.master_preview(w.editor_version)
    dialog=RectangleDialog(w,'Recorte sintético',image,list(bounds),original['crop'],20)
    dialog.show(); settle(); dialog.from_drag([5,5,427,295]); dialog.accept_valid()
    check(dialog.result()==dialog.DialogCode.Accepted,'Visual crop coordinates accepted')
    candidate=recrop(original,dialog.rect); candidate['area']=[.7,.82,.2,.1]
    check(w.command('Crop and status',candidate),'Crop+status command applies')
    check(w.dirty and w.save_button.isEnabled(),'Pending layout dirty/save enabled')
    snap('R3B1_Recorte_Zona_Cambios_Pendientes.png')
    w.undo_edit(); check(w.design.state==original,'Undo restores fields/crop/status')
    w.redo_edit(); check(w.design.state==candidate,'Redo restores complete design')
    check(w.save_work(),'Full layout saves through service')
    saved=w.api.version(w.current_editor_id)
    check(json.loads(saved['crop_json'])==candidate['crop'],'Crop persisted')
    check(json.loads(saved['status_area_json'])==candidate['area'],'Status area persisted')
    check(saved['pdf_sha256']==source,'Original source hash unchanged')
    span=next(s for s in w.api.editor_spans(w.current_editor_id) if s['text']=='LOTE')
    anchored=anchor_field(w.design.state,0,span,0,source)
    check(w.command('Anchor',anchored),'Native extracted-text anchor applies')
    check(w.fields[0]['draw']=='baseline' and w.fields[0]['anchor']['text']=='LOTE','Anchor/baseline retained')
    snap('R3B1_Anclaje_Linea_Base.png')
    relocated=relocate_anchors(w.design.state,w.api.editor_spans(w.current_editor_id),source)
    check(relocated==w.design.state,'Unambiguous saved reference relocates without drift')
    w.undo_edit(); w.field_list.clearSelection(); w.field_list.item(1).setSelected(True); w.field_list.item(3).setSelected(True)
    check(w.selected_indices()==[1,3],'Multiple native selection')
    check(w.command('Align',align_fields(w.design.state,[1,3],'right')),'Native alignment applies')
    check(abs(w.fields[1]['x']+w.fields[1]['w']-w.fields[3]['x']-w.fields[3]['w'])<1e-9,'Aligned coordinates agree')
    check(w.command('Scale',scale_fields(w.design.state,[1,3],.9)),'Proportional selected-field scale applies')
    w.tool_sections['Documento'][0].setChecked(False); w.tool_sections['Composición'][0].setChecked(True)
    snap('R3B1_Composicion_Seleccion_Multiple.png')
    w.undo_edit(); w.undo_edit(); w.field_list.clearSelection(); w.field_list.setCurrentRow(0)
    w.locked.setChecked(True); check(not w.spins['x'].isEnabled(),'Locked geometry inputs disabled')
    snap('R3B1_Campo_Bloqueado.png'); w.undo_edit()
    before=copy.deepcopy(w.design.state); item=w.field_items[1]; start=w.canvas.mapFromScene(item.sceneBoundingRect().center())
    QTest.mousePress(w.canvas.viewport(),Qt.MouseButton.LeftButton,pos=start)
    QTest.mouseMove(w.canvas.viewport(),start+QPoint(10,6),delay=20)
    QTest.mouseRelease(w.canvas.viewport(),Qt.MouseButton.LeftButton,pos=start+QPoint(10,6)); settle()
    check(w.design.state!=before,'Real graphical drag commits')
    w.undo_edit(); check(w.design.state==before,'Single undo recovers drag')
    p=dict(name='Synthetic proof',width_mm=100,height_mm=70,orientation='portrait',margin_mm=8,gap_mm=3,safety_mm=0,start_slot=1)
    path,_=w.api.preview_editor_layout(w.current_editor_id,w.design.state,p)
    check(path.exists(),'Existing engine creates proof')
    check(len(w.api.issues())==previous,'Editor proof does not create definitive issue')
    w.command('Restore initial synthetic design',original); check(w.save_work(),'Restore synthetic test state')
    approved=next(v['id'] for v in w.api.versions(w.row['id']) if v['state']=='APPROVED')
    w.select_version(approved); w.open_editor(); settle()
    check(not w.undo_button.isEnabled() and not w.save_button.isEnabled(),'Approved layout cannot undo/write')
    check(all(not b.isEnabled() for b in w.design_buttons),'Advanced mutations disabled in read-only state')
    snap('R3B1_Editor_Vigente_Bloqueado.png')
    w.select_version(w.session.initial_id); w.open_editor()
    w.resize(1100,760); settle(); snap('R3B1_Editor_Compacto.png')
    check('Centro nativo Qt' in w.nav['emission'].toolTip(),'Native emission is identified in navigation')
    return checks
