import pytest
pytest.importorskip('PySide6')
from test_r3a_qt import studio
from covex_label_manager.qt_ui.acceptance_dialog import ReadinessDialog
def test_r6a_native_dialog_is_explicit_and_non_approving(studio):
    window,session,app=studio
    dialog=ReadinessDialog(window,session.services)
    assert not dialog.export_button.isEnabled()
    dialog.run()
    assert dialog.report['acceptance']=='NOT_ACCEPTED'
    assert dialog.export_button.isEnabled()
    assert 'NO ACEPTADO' in dialog.status.text()
    dialog.close()
