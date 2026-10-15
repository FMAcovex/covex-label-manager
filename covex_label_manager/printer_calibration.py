"""Non-productive printer calibration: physical measurement, strict profile binding."""
import math
from .sheet_layout import paper_size, slots
from .engine import plan_sheet


def numeric(value):
    try: v=float(str(value).replace(',', '.'))
    except (TypeError,ValueError) as ex:raise ValueError('Medición numérica inválida.') from ex
    if not math.isfinite(v):raise ValueError('Medición no finita.')
    return v


def signature(profile,printer):
    printer=str(printer).strip()
    if not printer or len(printer)>160:raise ValueError('Identifique la impresora antes de calibrar.')
    plan=plan_sheet(profile,1)
    boxes=slots(profile,plan.cols,plan.rows)
    return {
        'printer':printer,
        'paper':profile.get('paper','A4'),
        'orientation':profile.get('orientation','portrait'),
        'paper_size_mm':list(paper_size(profile)),
        'layout_mode':profile.get('layout_mode','grid'),
        'boxes_mm':[[round(s.x-numeric(profile.get('offset_x_mm',0)),6),
                     round(s.y-numeric(profile.get('offset_y_mm',0)),6),
                     round(s.width,6),round(s.height,6)] for s in boxes],
    }


def calibrated(profile,printer,measured_x,measured_y,reference_x,reference_y):
    """Correction = reference - measured; measured values in millimetres."""
    from copy import deepcopy
    p=deepcopy(profile)
    # Only small mechanical registration corrections, not scaled redesign.
    shift_x=numeric(reference_x)-numeric(measured_x)
    shift_y=numeric(reference_y)-numeric(measured_y)
    if max(abs(shift_x),abs(shift_y))>10:
        raise ValueError('Corrección superior a 10 mm; revise escala, orientación y papel antes de continuar.')
    p['offset_x_mm']=round(numeric(p.get('offset_x_mm',0))+shift_x,6)
    p['offset_y_mm']=round(numeric(p.get('offset_y_mm',0))+shift_y,6)
    p['printer_name']=str(printer).strip()
    p['printer_calibration']={
        'contract':1,
        'measured_mm':[numeric(measured_x),numeric(measured_y)],
        'reference_mm':[numeric(reference_x),numeric(reference_y)],
        'correction_mm':[round(shift_x,6),round(shift_y,6)],
    }
    # Store a fingerprint of final physical geometry, but do not require a
    # new DB table or change the historical numeric offset semantics.
    p['printer_calibration']['signature']=signature(p,p['printer_name'])
    return p


def validate(profile):
    entry=profile.get('printer_calibration')
    if not entry:return
    if not isinstance(entry,dict) or entry.get('contract')!=1:
        raise ValueError('Contrato de calibración no soportado.')
    if entry.get('signature')!=signature(profile,profile.get('printer_name','')):
        raise ValueError('La impresora, el papel o la geometría cambió desde la calibración. Retire el ajuste y recalibre.')
