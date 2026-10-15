"""Printer calibration is nonproductive, bound to exact geometry and identity."""
import pytest
from covex_label_manager.printer_calibration import calibrated,validate
from covex_label_manager.engine import plan_sheet


def profile():
    return {'width_mm':80,'height_mm':50,'margin_mm':8,'gap_mm':3,
            'offset_x_mm':0,'offset_y_mm':0,'safety_mm':0,
            'orientation':'portrait','start_slot':1}


def test_reference_minus_measured_applies_correct_sign():
    p=calibrated(profile(),'Synthetic Desk Printer',9,7,8,8)
    assert p['offset_x_mm']==-1 and p['offset_y_mm']==1
    assert p['printer_name']=='Synthetic Desk Printer'
    validate(p);assert plan_sheet(p,1).capacity>0


@pytest.mark.parametrize('changed',[
    ('printer_name','Other Printer'),('orientation','landscape'),
    ('width_mm',79),('paper','A3'),('offset_x_mm',2),
])
def test_mismatched_profile_refuses_emission(changed):
    p=calibrated(profile(),'SYNTHETIC',8,8,8,8)
    p[changed[0]]=changed[1]
    with pytest.raises(ValueError):plan_sheet(p,1)


@pytest.mark.parametrize('measured',[
    float('nan'),float('inf'),'-inf','text'
])
def test_nonfinite_measurements_rejected(measured):
    with pytest.raises(ValueError):
        calibrated(profile(),'Synthetic Printer',measured,8,8,8)


def test_large_correction_and_blank_printer_blocked():
    with pytest.raises(ValueError,match='10 mm'):
        calibrated(profile(),'Synthetic Printer',25,8,8,8)
    with pytest.raises(ValueError,match='impresora'):
        calibrated(profile(),' ',8,8,8,8)


def test_legacy_profile_unmodified():
    old=profile()
    assert 'printer_calibration' not in old
    plan_sheet(old,1)
