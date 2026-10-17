"""Integrated UX regression on the existing disposable synthetic fixture."""
import copy
import pytest
pytest.importorskip('PySide6')
from PySide6.QtCore import QSize
from test_r3a_qt import studio
from covex_label_manager.qt_ui.acceptance_dialog import ReadinessDialog
from covex_label_manager.qt_ui.uat_session_dialog import UatSessionDialog
from covex_label_manager.qt_ui.master_reconcile_ui import MasterReconciliationDialog
from covex_label_manager.qt_ui.revision_browser import RevisionBrowserDialog


@pytest.mark.parametrize('width,height',[(1366,728),(1092,574),(910,472),
                                       (1920,1040),(1536,824),(1280,680)])
def test_editor_canvas_and_explicit_panel_recovery(studio,width,height):
    w,s,app=studio
    w.resize(width,height);w.open_editor();app.processEvents()
    assert w.width()<=width and w.height()<=height
    assert w.canvas.height()>=height*.45
    assert w.tools_scroll.isVisible() and w.editor_context.isVisible()
    w.canvas_focus.click();app.processEvents()
    assert not w.tools_scroll.isVisible() and not w.editor_context.isVisible()
    w.canvas_focus.click();app.processEvents()
    assert w.tools_scroll.isVisible() and w.editor_context.isVisible()
    assert w.editor_reset_button.text()=='Restablecer diseño guardado'


@pytest.mark.parametrize('destination',['library','emission','history','settings'])
def test_work_panel_is_editor_local_and_navigation_retains_data(studio,destination):
    w,s,app=studio
    api=s.services
    work=api.work.create(s.initial_id,name='SYNTHETIC-UX-WORK')
    w.load_emission_work(work['uid']);w.open_editor();w.show_editor_work();app.processEvents()
    w.editor_work_panel.value_inputs['lote'].setText('SYNTHETIC-RETAINED')
    w.navigate(destination);app.processEvents()
    assert not w.work_dock.isVisible()
    assert api.work.get(work['uid'])['values']['lote']=='SYNTHETIC-RETAINED'
    w.open_editor();app.processEvents()
    assert w.editor_work_panel.value_inputs['lote'].text()=='SYNTHETIC-RETAINED'
    assert w.work_dock.isVisible()


@pytest.mark.parametrize('kind',['uat','reconcile','readiness'])
def test_large_dialog_has_scroll_content_and_reachable_footer(studio,tmp_path,kind):
    w,s,app=studio
    if kind=='uat':dialog=UatSessionDialog(w,s.services)
    elif kind=='readiness':dialog=ReadinessDialog(w,s.services)
    else:
        path=tmp_path/'synthetic.csv';path.write_text('Nombre,Revisión\nDEMO,00\n')
        dialog=MasterReconciliationDialog(w,s.services,path)
    dialog.prepare_layout();dialog.fit_available(QSize(886,448));dialog.show()
    dialog.fit_available(QSize(886,448));app.processEvents()
    assert dialog.width()<=886 and dialog.height()<=448
    assert dialog.content_scroll.isVisible()
    assert dialog.footer_widgets
    if kind=='uat':assert not dialog.content_scroll.isAncestorOf(dialog.save_button)
    for footer in dialog.footer_widgets:
        assert footer.isVisibleTo(dialog)
        assert footer.mapTo(dialog,footer.rect().bottomRight()).y()<dialog.height()
    dialog.reject()


def test_compact_pdf_keeps_tools_and_context(studio):
    w,s,app=studio
    w.resize(910,472);w.navigate('emission');w.emission_compact.setCurrentIndex(1)
    app.processEvents()
    assert w.emission_pdf.tools.isVisible()
    assert w.emission_pdf.note.isVisible()
    assert w.emission_pdf.open_button.isVisible()
    assert w.emission_pdf.view.height()>70


def test_inspector_commands_are_outside_scroll_and_disable_when_empty(studio):
    w,s,app=studio
    w.resize(910,472);w.set_inspector(True);app.processEvents()
    for button in (w.prepare_button,w.test_button,w.native_approval_button):
        assert not w.inspector_scroll.isAncestorOf(button)
        assert button.isVisibleTo(w)
        assert button.mapTo(w,button.rect().bottomRight()).y()<w.height()
    w.search.setText('SYNTHETIC-NO-MATCH');app.processEvents()
    assert not w.inspector_panel.isEnabled() and not w.test_button.isEnabled()


def test_document_controls_open_sources_not_approval(studio,monkeypatch):
    from PySide6.QtWidgets import QPushButton
    w,s,app=studio;calls=[]
    monkeypatch.setattr(w,'open_document',lambda original=False:calls.append(original))
    monkeypatch.setattr(w,'approve_revision',lambda:pytest.fail('Source consultation approved a revision'))
    for text in ('Abrir PDF maestro','Abrir documento original'):
        next(b for b in w.inspector.findChildren(QPushButton) if b.text()==text).click()
    assert calls==[False,True]
    assert len([b for b in w.inspector_panel.findChildren(QPushButton) if 'aprobación' in b.text()])==1


def test_native_revision_browser_selects_variant_without_mutating_documents(studio):
    from PySide6.QtCore import Qt
    w,s,app=studio;api=s.services
    vid=next(v['id'] for v in api.versions(w.row['id']) if v['state']=='APPROVED')
    variant=api.create_variant(vid,'UX-SELECT','Variante sintética','Prueba de selección','Synthetic tester')
    before=[dict(v) for v in api.versions(w.row['id'])]
    cancelled=RevisionBrowserDialog(w);cancelled.reject()
    assert api.versions(w.row['id']) and [dict(v) for v in api.versions(w.row['id'])]==before
    dialog=RevisionBrowserDialog(w)
    dialog.revisions.setCurrentIndex(dialog.revisions.findData(vid))
    row=next(i for i in range(dialog.table.rowCount()) if dialog.table.item(i,0).data(Qt.ItemDataRole.UserRole)==variant['id'])
    dialog.table.selectRow(row);dialog.select(True);app.processEvents()
    assert w.current_editor_id==vid and w.current_variant_id==variant['id']
    assert [dict(v) for v in api.versions(w.row['id'])]==before
    assert api.variant(variant['id'])['state']=='DRAFT' and not api.issues()


@pytest.mark.parametrize('state',['DRAFT','PENDING','RETIRED'])
def test_variant_menu_explains_available_transitions(studio,state):
    w,s,app=studio;api=s.services
    variant=api.create_variant(s.initial_id,'UX-MENU','Variante sintética','Prueba de menú','Synthetic tester')
    if state!='DRAFT':variant=api.transition_variant(variant['id'],variant['generation'],state,'Synthetic tester','Motivo ficticio')
    w.library_variant_id=variant['id']
    actions={a.text():a for a in w.build_variant_menu().actions()}
    assert actions['Enviar a revisión'].isEnabled()==(state=='DRAFT')
    assert actions['Devolver a borrador'].isEnabled()==(state=='PENDING')
    assert actions['Tamaño nominal reutilizable'].isEnabled()==(state=='DRAFT')
    assert not actions['Registrar aprobación externa'].isEnabled() # base revision is pending
    assert actions['Registrar aprobación externa'].toolTip()
    assert api.variant(variant['id'])['state']==state


def test_pretty_dimensions_preserve_exact_profile_and_calibration(studio):
    from covex_label_manager.qt_ui.printer_calibration_ui import CalibrationDialog
    w,s,app=studio;api=s.services
    vid=next(r['version_id'] for r in api.library.entries() if r['state']=='APPROVED')
    work=api.work.create(vid,name='SYNTHETIC-EXACT')
    profile=copy.deepcopy(work['profile'])
    calibration=CalibrationDialog(w,api,profile)
    calibration.printer.setText('Synthetic Printer')
    calibration.accept_calibration()
    profile=calibration.profile
    work=api.work.save(work['uid'],work['generation'],{'profile':profile})
    w.load_emission_work(work['uid']);panel=w.emission_panel
    assert panel.profile_inputs['width_mm'].text()=='152.4'
    assert panel.profile_inputs['height_mm'].text()=='105.833'
    panel.value_inputs['lote'].setText('SYNTHETIC-NO-ROUNDING');panel.changed()
    assert w.flush_emission_work()
    saved=api.work.get(work['uid'])['profile']
    assert saved==profile # includes raw floats, signature, measurements, printer and offsets
    assert api.sheet_plan(saved,1)


def test_contextual_menus_retain_all_exchange_commands(studio,monkeypatch):
    w,s,app=studio;called=[]
    methods=['import_document','import_folder_native','review_catalog_folder','reconcile_master','export_entire_library']
    for name in methods:monkeypatch.setattr(w,name,lambda n=name:called.append(n))
    menu=w.build_exchange_menu()
    for action in menu.actions():
        if not action.isSeparator():action.trigger()
    assert called==methods


def test_spanish_standard_buttons_and_explicit_accessibility(studio):
    from PySide6.QtWidgets import QDialogButtonBox
    w,s,app=studio
    buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Save)
    assert buttons.button(QDialogButtonBox.StandardButton.Cancel).text()=='Cancelar'
    assert buttons.button(QDialogButtonBox.StandardButton.Save).text()=='Guardar'
    w.resize(910,472);app.processEvents()
    assert all(w.nav[k].text() and w.nav[k].accessibleName() for k in ('history','settings'))
    assert w.search.accessibleName() and w.font_size.accessibleName()


def test_normal_secondary_text_has_readable_contrast(studio):
    from PySide6.QtGui import QPalette,QColor
    w,s,app=studio;app.processEvents()
    text=w.library_subtitle.palette().color(QPalette.ColorRole.WindowText)
    def luminance(color):
        channels=[color.redF(),color.greenF(),color.blueF()]
        linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in channels]
        return sum(a*b for a,b in zip(linear,[.2126,.7152,.0722]))
    for background in (QColor('#FFFFFF'),QColor('#F3F6F7')):
        light,dark=sorted([luminance(text),luminance(background)],reverse=True)
        assert (light+.05)/(dark+.05)>=4.5


def test_inventory_human_summary_preserves_full_technical_report(studio):
    import json
    from PySide6.QtWidgets import QPushButton
    from covex_label_manager.qt_ui.catalog_exchange_ui import InventoryReportDialog
    w,s,app=studio
    report={'mode':'READ_ONLY','counts':{'BLOCKED_SYMLINK':1,'REVIEW_REQUIRED':1},'files':[
        {'path':'synthetic-link','status':'BLOCKED_SYMLINK'},
        {'path':'synthetic.pdf','name':'Demo','version':'00','status':'REVIEW_REQUIRED'}]}
    original=copy.deepcopy(report)
    dialog=InventoryReportDialog(w,report);dialog.show();app.processEvents()
    assert not dialog.details.isVisible()
    assert 'Requiere revisión: 1' in dialog.summary.text()
    assert dialog.table.item(0,3).text()=='Enlace bloqueado'
    next(b for b in dialog.findChildren(QPushButton) if b.text()=='Mostrar detalle técnico JSON').click()
    assert dialog.details.isVisible() and dialog.details.isReadOnly()
    assert json.loads(dialog.details.toPlainText())==original==report
    dialog.reject()
