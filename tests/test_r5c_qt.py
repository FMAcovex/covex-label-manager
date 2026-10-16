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
