"""R5C UI smoke in disposable Qt DemoSession, no private master."""
import pytest
pytest.importorskip('PySide6')
from test_r3a_qt import studio
from covex_label_manager.qt_ui.master_reconcile_ui import MasterReconciliationDialog


def test_master_wizard_maps_and_filters_without_mutations(studio,tmp_path):
    w,session,app=studio
    v=session.services.version(session.initial_id)
    path=tmp_path/'master.csv'
    path.write_text('Denominación;Revisión;Código\n'+
                    f"{v['name']};{v['version']};{v['code']}\n",encoding='utf-8')
    before=[(r['version_id'],r['state']) for r in session.services.library_records()]
    dialog=MasterReconciliationDialog(w,session.services,path)
    assert dialog.inputs['name'].currentData()=='Denominación'
    assert dialog.inputs['version'].currentData()=='Revisión'
    dialog.run_compare()
    assert dialog.report is not None
    assert dialog.export.isEnabled()
    assert dialog.table.rowCount()==1
    assert before==[(r['version_id'],r['state']) for r in session.services.library_records()]
    dialog.close()


def test_reconciliation_plain_language_mapping_and_attention_filter(studio,tmp_path):
    from PySide6.QtCore import Qt
    w,session,app=studio
    api=session.services
    source=api.version(session.initial_id)
    book=tmp_path/'libro-ejemplo.csv'
    book.write_text(
        'Denominación;Revisión;Código\\n'
        +f"{source['name']};{source['version']};{source['code']}\\n"
        +'DOCUMENTO NO EXISTENTE;01;SYN-ABSENT\\n',
        encoding='utf-8')
    initial=[(r['version_id'],r['state']) for r in api.library_records()]
    dialog=MasterReconciliationDialog(w,api,book)
    assert not dialog.optional_columns.isVisible()
    assert dialog.compare.isEnabled()
    dialog.run_compare()
    assert dialog.report is not None
    assert dialog.table.rowCount()==2
    assert dialog.table.item(1,1).text()=='Etiqueta ausente en biblioteca'
    assert dialog.table.item(1,1).data(Qt.ItemDataRole.UserRole)=='MISSING_LABEL'
    filter_id=dialog.filter.findData('__ATTENTION__')
    assert filter_id>=0
    dialog.filter.setCurrentIndex(filter_id)
    assert dialog.table.rowCount()==1
    dialog.table.selectRow(0)
    assert 'puede faltar' in dialog.detail.text()
    assert dialog.export.isEnabled()

    # Changing the mapping invalidates the previous report and ZIP export.
    dialog.inputs['name'].setCurrentIndex(0)
    assert not dialog.compare.isEnabled()
    assert not dialog.export.isEnabled()
    assert dialog.table.rowCount()==0
    dialog.inputs['name'].setCurrentIndex(
        dialog.inputs['name'].findData('Denominación'))
    assert dialog.compare.isEnabled()
    assert initial==[(r['version_id'],r['state']) for r in api.library_records()]
    dialog.reject()


def test_reconciliation_hides_optional_mapping_until_requested(studio,tmp_path):
    w,session,app=studio
    book=tmp_path/'listado.csv'
    book.write_text('Denominación;Revisión;Origen\\nFICTICIA;01;COVEX\\n',encoding='utf-8')
    dialog=MasterReconciliationDialog(w,session.services,book)
    assert dialog.inputs['origin'].currentData()=='Origen'
    assert not dialog.optional_columns.isVisible()
    dialog.show_columns.setChecked(True)
    assert dialog.optional_columns.isVisible() if dialog.isVisible() else dialog.show_columns.isChecked()
    assert 'Ocultar' in dialog.show_columns.text()
    dialog.reject()
