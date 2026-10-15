"""Exercise native calibration controls with synthetic data only."""
import pytest
pytest.importorskip('PySide6')
from test_r3a_qt import studio
from covex_label_manager.qt_ui.printer_calibration_ui import CalibrationDialog
from covex_label_manager.engine import plan_sheet


def test_native_calibration_applies_offset_without_modifying_input(studio):
    w,s,app=studio
    base={'width_mm':80,'height_mm':50,'margin_mm':8,'gap_mm':3,
          'offset_x_mm':0,'offset_y_mm':0,'safety_mm':0,
          'orientation':'portrait','start_slot':1}
    dialog=CalibrationDialog(w,s.services,base)
    dialog.printer.setText('Synthetic Printer')
    dialog.inputs['measured_x'].setText('9')
    dialog.inputs['measured_y'].setText('8')
    dialog.inputs['reference_x'].setText('8')
    dialog.inputs['reference_y'].setText('8')
    dialog.accept_calibration()
    assert dialog.profile['offset_x_mm']==-1
    assert base['offset_x_mm']==0
    assert plan_sheet(dialog.profile,1)

def test_calibration_dialog_versioned_profile_negative_shift(studio):
    w,s,app=studio
    p={'layout_version':1,'layout_mode':'grid','paper':'A4',
       'width_mm':80,'height_mm':50,'margin_mm':8,'gap_mm':3,
       'offset_x_mm':0,'offset_y_mm':0,'safety_mm':0,
       'orientation':'portrait','start_slot':1}
    dialog=CalibrationDialog(w,s.services,p)
    dialog.printer.setText('Synthetic Versioned Printer')
    dialog.inputs['measured_x'].setText('9')
    dialog.inputs['measured_y'].setText('8')
    dialog.inputs['reference_x'].setText('8')
    dialog.inputs['reference_y'].setText('8')
    dialog.accept_calibration()
    assert dialog.profile['offset_x_mm']==-1
    assert plan_sheet(dialog.profile,1).capacity>0
    assert 'printer_calibration' not in p
