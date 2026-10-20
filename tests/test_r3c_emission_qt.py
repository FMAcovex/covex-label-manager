"""Native operator workflow: synthetic documents, real widgets and PDFs, no Tk."""
import json
import fitz
import pytest
from test_emission_work_qt import studio
from PySide6.QtWidgets import QMessageBox,QFileDialog
from covex_label_manager.storage import sha256


def prepared(studio):
    w,api,app=studio
    vid=next(r['version_id'] for r in api.library.entries() if r['state']=='APPROVED')
    work=api.work.create(vid,name='R3C · lote sintético')
    work=api.work.save(work['uid'],1,{'values':{'lote':'SYNTHETIC-R3C','pn':'1','pb':'2'},'count':'3','selection':'1-3',
        'per_container':{'2':{'lote':'SYNTHETIC-RECIPIENTE-2','pn':'0,5','pb':'0,7'}}})
    w.load_emission_work(work['uid']);w.navigate('emission');app.processEvents()
    return w,api,work


def test_native_preview_export_cancel_issue_and_recovery(studio,monkeypatch,tmp_path):
    w,api,work=prepared(studio)
    monkeypatch.setattr('covex_label_manager.qt_ui.functional.launch_legacy',lambda *a,**k:pytest.fail('Native emission launched Tk'))
    assert not w.emission_pdf.expand_button.isEnabled()
    assert w.preview_emission_work(),w.emission_feedback.text()
    assert w.emission_pdf.expand_button.isEnabled()
    assert not api.issues() and w.native_issue.isEnabled(),w.emission_feedback.text()
    with fitz.open(w.work_preview['path']) as pdf:
        text=''.join(p.get_text() for p in pdf).replace('\xad','-').replace('\xa0',' ')
        assert 'PRUEBA' in text and 'SYNTHETIC-R3C' in text and 'SYNTHETIC-RECIPIENTE-2' in text
    dest=tmp_path/'PRUEBA.pdf';monkeypatch.setattr(QFileDialog,'getSaveFileName',lambda *a,**k:(str(dest),'PDF'))
    assert w.proof_emission_work() and sha256(dest)==w.work_preview['sha256'] and not api.issues()
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Cancel)
    assert not w.issue_emission_work() and not api.issues()
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
    assert w.issue_emission_work(),w.emission_feedback.text()
    issue=api.issues()[0];snap=json.loads(issue['design_snapshot_json'])
    assert snap['work']['uid']==work['uid'] and json.loads(issue['selected_indices'])==[1,2,3]
    with fitz.open(api.asset_path(issue['pdf_path'])) as pdf:
        text=''.join(p.get_text() for p in pdf).replace('\xad','-').replace('\xa0',' ')
        assert 'PRUEBA' not in text and 'SYNTHETIC-RECIPIENTE-2' in text
    assert api.work.get(work['uid'])['phase']=='ISSUED'
    assert not w.issue_emission_work() and len(api.issues())==1


def test_changed_after_confirmation_and_tampered_preview_block(studio,monkeypatch):
    w,api,work=prepared(studio);assert w.preview_emission_work()
    def changed(*args,**kwargs):
        api.work.save(work['uid'],w.emission_work['generation'],{'values':{'lote':'CONCURRENT'}})
        return QMessageBox.StandardButton.Yes
    monkeypatch.setattr(QMessageBox,'question',changed)
    assert not w.issue_emission_work() and not api.issues()
    w.reload_emission_work();assert w.preview_emission_work()
    w.work_preview['path'].write_bytes(b'changed')
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
    assert not w.issue_emission_work() and not api.issues()


def test_inline_checks_pending_invalid_format_and_long_fields(studio):
    w,api,work=prepared(studio)
    panel=w.emission_panel;panel.inputs['count'].setText('0');panel.changed();assert w.flush_emission_work()
    assert panel.error_labels['count'].text() and not w.native_issue.isEnabled()
    panel.inputs['count'].setText('3');panel.value_inputs['lote'].setText('EXTENSO '*500);panel.changed();assert w.flush_emission_work()
    w.preview_emission_work()
    w.recheck_actions();assert not w.native_issue.isEnabled()
    assert not api.issues()


def test_format_ratio_restore_profile_and_multiline_preservation(studio,monkeypatch):
    from PySide6.QtWidgets import QInputDialog
    w,api,work=prepared(studio);p=w.emission_panel
    p.value_inputs['lote'].setText('LÍNEA UNO\nLÍNEA DOS');p.changed();assert w.flush_emission_work()
    assert '\n' in api.work.get(work['uid'])['values']['lote']
    p.profile_inputs['width_mm'].setText('80');p.scale_size('width_mm');assert w.flush_emission_work()
    v=api.resolved_design(work['binding']['revision_id'])
    assert float(w.emission_work['profile']['height_mm'])==pytest.approx(80*v['base_h_mm']/v['base_w_mm'],abs=1e-5)
    p.restore_size();assert w.flush_emission_work()
    monkeypatch.setattr(QInputDialog,'getText',lambda *a,**k:('Perfil R3C sintético',True))
    w.save_emission_profile();assert any(r['name']=='Perfil R3C sintético' for r in api.profile_list())
    p.profile_choice.setCurrentIndex(next(i for i in range(p.profile_choice.count()) if p.profile_choice.itemText(i)=='Perfil R3C sintético'));p.apply_profile()
    assert w.flush_emission_work() and not api.issues()


@pytest.mark.parametrize('phase',['RENDERED','COMMITTED'])
def test_native_failure_reconciliation_and_no_duplicate(studio,monkeypatch,phase):
    w,api,work=prepared(studio);assert w.preview_emission_work()
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
    real=api.work.issue
    def issue(uid,generation,operator):
        def crash(point,_):
            if point==phase:raise RuntimeError('synthetic failure')
        return real(uid,generation,operator,crash)
    monkeypatch.setattr(api.work,'issue',issue)
    assert not w.issue_emission_work()
    latest=api.work.get(work['uid']);assert latest['phase']==('ISSUED' if phase=='COMMITTED' else 'EMITTING')
    assert len(api.issues())==int(phase=='COMMITTED')
    if phase=='RENDERED':
        w.recover_emission_work();assert w.emission_work['phase']=='DRAFT'
    else:assert 'ya está registrada' in w.emission_feedback.text()


def test_editor_pdf_summary_is_readable_and_close_translated(studio,monkeypatch):
    from PySide6.QtWidgets import QDialog,QPushButton,QLabel,QDialogButtonBox
    w,api,app=studio;w.open_editor();seen=[]
    def execute(dialog):
        if dialog.windowTitle()=='Formato físico y prueba PDF':
            next(b for b in dialog.findChildren(QPushButton) if b.text()=='Ver PDF de prueba').click()
        elif dialog.windowTitle()=='PDF de prueba — sin emisión definitiva':
            texts=' '.join(l.text() for l in dialog.findChildren(QLabel))
            assert 'hojas A4' in texts and 'physical' not in texts and 'path' not in texts
            assert dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Close).text()=='Cerrar'
            seen.append(True)
        return QDialog.DialogCode.Rejected
    monkeypatch.setattr(QDialog,'exec',execute);w.edit_output();assert seen and not api.issues()


def test_compact_centre_keeps_work_actions_and_pdf_controls(studio):
    w,api,work=prepared(studio);app=studio[2]
    w.resize(1000,590);app.processEvents()
    assert w.emission_compact.isVisible()
    assert not w.emission_heading.isVisible()
    assert w.emission_panel._compact and w.emission_panel.top_actions.count()>=5
    assert all(action.isVisible() for action in w.emission_panel.shortcut_buttons)
    assert w.preview_work_button.parent() is w.emission_right
    assert w.emission_footer.layout().contentsMargins().top()<=8
    assert w.emission_left.isVisible() and not w.emission_right.isVisible()
    assert w.preview_emission_work()
    assert w.emission_pdf.view.height()>70
    assert w.emission_pdf.expand_button.text()=='Ampliar PDF'
    assert w.emission_pdf.title.toolTip()=='Vista previa · PDF de prueba'
    w.emission_compact.setCurrentIndex(0);app.processEvents()
    assert w.emission_left.isVisible()
    w.resize(1500,940);app.processEvents()
    assert not w.emission_panel._compact
    assert w.emission_panel.action_row.count()==3
    assert w.emission_heading.isVisible()


def test_work_format_help_explains_physical_dimensions_without_writing(studio,monkeypatch):
    from PySide6.QtWidgets import QMenu
    w,api,work=prepared(studio)
    panel=w.emission_panel
    panel.tabs.setCurrentIndex(2)
    assert 'Cuadrícula' in panel.format_context.text()
    assert 'No es el zoom' in panel.profile_inputs['height_mm'].toolTip()
    assert not panel.format_help_toggle.isChecked()
    panel.format_help_toggle.setChecked(True)
    assert not panel.format_help.isHidden()
    assert 'Casilla inicial' in panel.format_help.text()
    # Inspect the real native popup: it must return immediately instead of
    # entering a nested modal event loop, and its actions must be discoverable.
    w.work_options()
    menus=w.native_options.findChildren(QMenu)
    assert len(menus)==1
    menu=menus[0]
    actions=[action.text() for action in menu.actions()]
    assert menu.isVisible()
    menu.close()
    assert 'FORMATO FÍSICO' in actions
    assert any('numeración' in title.lower() for title in actions)
    assert 'TRABAJO Y TRAZABILIDAD' in actions
    assert 'Cambiar tamaño y distribuir etiquetas…' in actions
    assert not api.issues()
    assert api.work.get(work['uid'])['profile']==work['profile']


def test_free_sheet_format_help_points_to_actual_slot_editor(studio):
    from covex_label_manager.sheet_layout import template
    w,api,work=prepared(studio)
    p=dict(work['profile'],layout_version=1,layout_mode='free',
           paper='A4',margin_mm=8,gap_mm=3)
    p['slots']=template(p,2)
    committed=api.work.save(work['uid'],work['generation'],{'profile':p})
    w.load_emission_work(committed['uid'])
    panel=w.emission_panel
    assert 'Distribución libre' in panel.format_context.text()
    assert not panel.profile_inputs['width_mm'].isEnabled()
    assert 'Modificar tamaño y posiciones' in panel.design_sheet_button.text()
    assert api.work.get(committed['uid'])['profile']==committed['profile']
