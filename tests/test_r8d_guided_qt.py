"""R8D real controls, real services/PDFs; exclusively private synthetic data."""
import copy
import json
from pathlib import Path
import fitz
import pytest
pytest.importorskip('PySide6')
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox,QFileDialog
from PySide6.QtTest import QTest
from test_r3a_qt import studio


@pytest.fixture(autouse=True)
def deterministic_documentary_fixture(studio,tmp_path):
    """New exact-text assertions use the R8C embedded font contract, not
    Windows historical Arial (whose hyphen ToUnicode is U+00AD). Never alter
    historical rendering or normalize extracted text to pass an assertion.
    """
    from datetime import date
    from covex_label_manager.typography import DEFAULT
    w,s,app=studio
    approved=next(v['id'] for v in w.api.versions(w.row['id']) if v['state']=='APPROVED')
    variant=w.api.create_variant(approved,'SYN-EMBEDDED','SYN R8D embedded','SYNTHETIC isolated font fixture','SYN')
    design=json.loads(variant['design_json'])
    for field in design['layout']['fields']:field['typography']=dict(DEFAULT)
    variant=w.api.save_variant(variant['id'],variant['generation'],design,'SYN')
    variant=w.api.transition_variant(variant['id'],variant['generation'],'PENDING','SYN')
    evidence=tmp_path/'SYNTHETIC-EXTERNAL.txt';evidence.write_text('SYNTHETIC TEST ONLY: external approval fixture',encoding='utf-8')
    variant=w.api.approve_variant(variant['id'],variant['generation'],'SYN QA','SYN EXTERNAL',date.today().isoformat(),evidence,'SYN')
    w.r8d_fixture_variant=variant['id']


def click(widget):
    assert widget.isEnabled(),widget.text()
    QTest.mouseClick(widget,Qt.MouseButton.LeftButton)


def select_design(w,state='APPROVED'):
    g=w.guided;assert g.begin()
    variant_id=w.r8d_fixture_variant if state=='APPROVED' else None
    index=next(i for i,(r,v) in enumerate(g.choices) if r['state']==state and (v['id'] if v else None)==variant_id and r['id']==w.row['id'])
    g.results.selectRow(index);click(g.next_button)
    assert g.step==1 and w.emission_work
    w.preview_timer.stop();return w.emission_work


def enter(w,values=None,count='1',copies='1'):
    panel=w.guided.panel
    values=values or {'lote':'SYN-R8D','cantidad':'1 kg','proveedor':'SYN','direccion':'SYN','telefono':'123','observaciones':'SYN'}
    for key,e in panel.value_inputs.items():
        e.setText(values.get(key,''));e.textEdited.emit() if key not in ('pn','pb') else e.textEdited.emit(e.text())
    for key,text in [('count',count),('copies',copies)]:panel.inputs[key].setText(text);panel.inputs[key].textEdited.emit(text)
    assert w.flush_emission_work();w.preview_timer.stop()
    return w.emission_work


def render(w):
    w.preview_timer.stop();w.preview_pending=False
    if w.preview_task is not None:
        assert w.preview_task.wait(30000)
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
    assert w.preview_emission_work()
    w.guided.sync(w.work_review)


def test_four_steps_back_values_quantities_and_same_advanced_work(studio):
    w,s,app=studio;work=select_design(w);saved=enter(w,count='2',copies='2')
    g=w.guided;click(g.next_button);assert g.step==2,g.feedback.text()
    assert '(Vigente)' in g.identity.toolTip() and 'Trabajo: Borrador' in g.identity.toolTip()
    render(w);assert g.pdf.path
    with fitz.open(g.pdf.path) as doc:
        assert 'PRUEBA' in doc[0].get_text() and 'SYN-R8D' in doc[0].get_text()
        assert any(font[4].startswith('R8C_') for font in doc[0].get_fonts())
    click(g.back_button);assert g.step==1
    assert g.panel.value_inputs['lote'].text()=='SYN-R8D'
    click(g.back_button);assert g.step==0
    index=next(i for i,(r,v) in enumerate(g.choices) if r['version_id']==work['binding']['revision_id'] and (v['id'] if v else None)==work['binding']['variant_id'])
    g.results.selectRow(index);click(g.next_button)
    assert w.emission_work['uid']==saved['uid'] and w.emission_work['values']==saved['values']
    click(g.advanced_button);assert w.stack.currentWidget() is w.emission_page
    before=copy.deepcopy(w.emission_work);click(g.assistant_button)
    assert w.stack.currentWidget() is g.page and w.emission_work==before


def test_pending_proof_allowed_but_definitive_blocked(studio,tmp_path):
    w,s,app=studio;select_design(w,'PENDING');enter(w);g=w.guided
    click(g.next_button);render(w);click(g.next_button)
    assert g.step==3 and not g.issue_button.isEnabled() and g.proof_button.isEnabled()
    assert '(Pendiente)' in g.identity.toolTip() and 'Trabajo: Borrador' in g.identity.toolTip()
    from covex_label_manager.engine import LayoutError
    with pytest.raises(LayoutError,match='pendiente de aprobación o retirada'):w.api.work.issue(w.emission_work['uid'],w.emission_work['generation'],'SYN')
    assert not w.api.issues()


def test_authorized_issue_proof_export_history_duplicate_and_reprint(studio,tmp_path,monkeypatch):
    w,s,app=studio;select_design(w);enter(w);g=w.guided
    click(g.next_button);render(w);click(g.next_button);assert g.step==3
    target=tmp_path/'SYNTHETIC-R8D-proof.pdf'
    monkeypatch.setattr(QFileDialog,'getSaveFileName',lambda *args:(str(target),'PDF'))
    click(g.proof_button);assert target.exists() and not w.api.issues()
    with fitz.open(target) as doc:assert 'PRUEBA' in doc[0].get_text()
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
    click(g.issue_button);issued=w.emission_work
    assert issued['phase']=='ISSUED' and len(w.api.issues())==1
    report=w.api.history.inspect(issued['issue_id']);original=report['path'].read_bytes()
    assert not g.issue_button.isEnabled() and not g.issue()
    assert len(w.api.issues())==1
    pk,path,_=w.api.history.reproduce(issued['issue_id'],'1','SYN R8D regression','SYN',expected_token=report['token'])
    assert report['path'].read_bytes()==original and path.exists()
    assert w.api.issue(pk)['source_issue_id']==issued['issue_id']
    click(g.history_button);assert w.stack.currentWidget() is w.history_page


def test_resume_saved_work_no_critical_defaults_for_new_lot(studio):
    w,s,app=studio;select_design(w);saved=enter(w)
    w.navigate('home');g=w.guided
    g.recent.setCurrentIndex(g.recent.findData(saved['uid']));click(g.continue_button)
    assert w.emission_work==saved and g.panel.value_inputs['lote'].text()=='SYN-R8D'
    select_design(w);assert w.emission_work['uid']!=saved['uid'] and not any(w.emission_work['values'].values())
    assert w.api.work.get(saved['uid'])==saved


@pytest.mark.parametrize('width,height',[(1366,728),(1092,574),(910,472),(1920,1040),(1536,824),(1280,680)])
def test_four_pages_fit_keyboard_and_persistent_actions(studio,width,height):
    w,s,app=studio;w.resize(width,height);g=w.guided
    w.navigate('home');app.processEvents()
    assert w.width()==width and w.height()==height
    click(g.new_button);select_design(w);enter(w)
    # Shortcut is a real Qt action, no direct step manipulation.
    g.panel.inputs['copies'].setFocus()
    QTest.keyClick(g.panel.inputs['copies'],Qt.Key.Key_Right,Qt.KeyboardModifier.AltModifier)
    app.processEvents();assert g.step==2
    render(w);click(g.next_button);app.processEvents();assert g.step==3
    for control in (g.next_button,g.back_button,g.cancel_button,g.advanced_button):
        if control.isVisible():assert g.page.rect().contains(control.mapTo(g.page,control.rect().center()))
    click(g.back_button);app.processEvents()
    assert g.pdf.view.height()>=110,(g.pdf.view.size(),g.pdf.note.text())
    assert g.pdf.rect().contains(g.pdf.note.mapTo(g.pdf,g.pdf.note.rect().center()))
    QTest.keyClick(g.pdf,Qt.Key.Key_Left,Qt.KeyboardModifier.AltModifier)
    app.processEvents();assert g.step==1
    assert w.width()==width


def test_unapproved_appearance_stays_trial_in_wizard(studio,tmp_path):
    w,s,app=studio;select_design(w);work=enter(w);g=w.guided
    profile=copy.deepcopy(work['profile']);profile['trial_appearance']={'contract':1,'fields':{'lote':{'font_pt':9}}}
    w.emission_work=w.api.work.save(work['uid'],work['generation'],{'profile':profile});w.refresh_work_panels()
    click(g.next_button);render(w);click(g.next_button)
    assert not g.issue_button.isEnabled() and 'PRUEBA' in g.feedback.text()
    with pytest.raises(PermissionError):w.api.work.issue(w.emission_work['uid'],w.emission_work['generation'],'SYN')
    assert not w.api.issues()


def test_ambiguous_results_require_explicit_selection_and_retired_block(studio):
    w,s,app=studio;g=w.guided;g.begin()
    assert len(g.choices)>1 and g.selection() is None and not g.next_button.isEnabled()
    retired=next((i for i,(r,v) in enumerate(g.choices) if r['state']=='RETIRED' and v is None),None)
    if retired is not None:
        g.results.selectRow(retired);assert not g.next_button.isEnabled() and not g.next_step()
    assert w.emission_work is None


def test_private_errors_and_cancel_keep_saved_work(studio):
    from covex_label_manager.qt_ui.guided_workflow import safe_message
    w,s,app=studio;select_design(w);work=enter(w);g=w.guided
    g.failure(RuntimeError('Traceback C:\\corporate\\secret.py failure'))
    assert 'corporate' not in g.feedback.text() and 'Traceback' not in g.feedback.text()
    assert not g.issue_button.isEnabled()
    assert 'corporate' not in safe_message('/corporate/private/lot.pdf')
    click(g.cancel_button);assert w.stack.currentWidget() is g.home
    assert w.api.work.get(work['uid'])==work and not w.api.issues()
    assert w.api._repository.db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'


def test_mass_units_and_recipient_overrides_real_pdf(studio):
    from PySide6.QtWidgets import QTableWidgetItem
    w,s,app=studio;select_design(w);g=w.guided
    enter(w,{'lote':'SYN-MASS','pn':'350 g','pb':'500000 mg'},count='2')
    g.panel.tabs.setCurrentIndex(1)
    g.panel.containers.setItem(1,1,QTableWidgetItem('SYN-SECOND'))
    g.panel.containers.setItem(1,2,QTableWidgetItem('0,4 kg'))
    g.panel.containers.setItem(1,3,QTableWidgetItem('600 g'))
    assert w.flush_emission_work();click(g.next_button);render(w)
    assert w.emission_work['values']['pn']=='350 g'
    assert w.emission_work['per_container']['2']['pn']=='0,4 kg'
    with fitz.open(g.pdf.path) as doc:
        text=''.join(p.get_text() for p in doc)
        assert 'SYN-MASS' in text and 'SYN-SECOND' in text and '350 g' in text and '0,4 kg' in text


def test_status_revision_and_both_scaling_modes_real_pdf(studio,tmp_path):
    from covex_label_manager.status_design import make_layout
    w,s,app=studio;select_design(w);enter(w);g=w.guided
    source=tmp_path/'SYNTHETIC-R8D-status.pdf'
    with fitz.open() as doc:
        page=doc.new_page(width=200,height=100)
        page.draw_rect(page.rect,fill=(.25,.8,.4),color=None)
        page.insert_text((80,35),'SYN',fontsize=8);doc.save(source)
    design=make_layout(source,'aprobado');design['fields']=[dict(key='lote',label='Lote',rect=[75,40,125,60],font_size=8.,bold=False,required=True)]
    uid=w.api.status_catalog.import_many(source,[dict(kind='aprobado',revision='SYN-00',layout=design)])[0]
    w.api.status_catalog.submit(uid);w.api.status_catalog.approve(uid,'SYN QA','SYN EXTERNAL FIXTURE',confirmation=True)
    panel=g.panel;panel.tabs.setCurrentIndex(3)
    panel.status_kind.setCurrentIndex(panel.status_kind.findData('aprobado'))
    panel.status_revision.setCurrentIndex(panel.status_revision.findData(uid))
    assert panel.status_revision.currentData()==uid
    panel.placement.setCurrentIndex(panel.placement.findData('independiente'))
    for mode in ('fit','fill'):
        panel.composition.setCurrentIndex(panel.composition.findData(mode));assert w.flush_emission_work()
        render(w);assert g.pdf.path
        with fitz.open(g.pdf.path) as doc:
            text=''.join(page.get_text() for page in doc);assert 'SYN' in text and 'SYN-R8D' in text
        assert w.work_preview['result']['composition'][0]['mode']==mode
    assert w.emission_work['status']['revision_uid']==uid and not w.api.issues()


def test_real_cas_conflict_blocks_navigation_and_keeps_unsaved_input(studio):
    w,s,app=studio;select_design(w);saved=enter(w);g=w.guided
    latest=w.api.work.save(saved['uid'],saved['generation'],{'values':{**saved['values'],'lote':'SYN-EXTERNAL'}})
    g.panel.value_inputs['lote'].setText('SYN-UNSAVED');g.panel.value_inputs['lote'].textEdited.emit()
    click(g.advanced_button)
    assert w.stack.currentWidget() is g.page and w.work_dirty_panel is g.panel
    assert g.panel.value_inputs['lote'].text()=='SYN-UNSAVED'
    assert w.api.work.get(saved['uid'])==latest
    # Explicitly restore only this test's local screen before fixture teardown.
    w.work_timer.stop();w.work_dirty_panel=None


def test_preview_tampering_never_registers_a_definitive_issue(studio,monkeypatch):
    w,s,app=studio;select_design(w);enter(w);g=w.guided
    click(g.next_button);render(w);click(g.next_button)
    path=Path(w.work_preview['path']);path.write_bytes(path.read_bytes()+b'\nSYNTHETIC-TAMPER')
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
    monkeypatch.setattr(QMessageBox,'warning',lambda *a,**k:QMessageBox.StandardButton.Ok)
    click(g.issue_button);assert not w.api.issues() and w.emission_work['phase']=='DRAFT'


def test_87_ids_preserved_and_no_new_contract_store():
    import re
    docs=Path(__file__).resolve().parents[1]/'docs'
    def entries(p):return re.findall(r'^\| ([A-Z][0-9]{2}) \| ([^|]+)\|',(docs/p).read_text(encoding='utf-8'),re.M)
    before=entries('R8C_TYPOGRAPHY_SCALING/CONSERVACION_87.md')
    assert len(before)==87 and entries('R8D_GUIDED_WORKFLOW/CONSERVACION_87.md')==before


def test_variant_specific_required_fields_and_unapproved_choice(studio):
    w,s,app=studio;work=select_design(w)
    variant=w.api.create_variant(work['binding']['revision_id'],'SYN-R8D','SYN Custom','SYN isolated fixture','SYN')
    design=json.loads(variant['design_json'])
    design['layout']['fields']=[dict(key='custom_date',label='Fecha requerida de prueba',x=.1,y=.4,w=.7,h=.15,font_pt=10,bold=False,required=True,locked=False)]
    variant=w.api.save_variant(variant['id'],variant['generation'],design,'SYN')
    g=w.guided;g.begin()
    index=next(i for i,(r,v) in enumerate(g.choices) if v and v['id']==variant['id'])
    g.results.selectRow(index);click(g.next_button)
    assert set(g.panel.value_inputs)=={'custom_date'} and not w.emission_work['values']
    assert g.panel.common_form.labelForField(g.panel.value_inputs['custom_date'].parentWidget()).text().endswith('*')
    g.panel.value_inputs['custom_date'].setText('SYN 01');g.panel.value_inputs['custom_date'].textEdited.emit()
    assert w.flush_emission_work();render(w)
    assert not w.work_review['production_allowed'] and not g.issue_button.isEnabled()


def test_human_cancels_definitive_confirmation_without_issue(studio,monkeypatch):
    w,s,app=studio;select_design(w);enter(w);g=w.guided
    click(g.next_button);render(w);click(g.next_button)
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Cancel)
    click(g.issue_button)
    assert not w.api.issues() and w.emission_work['phase']=='DRAFT'
