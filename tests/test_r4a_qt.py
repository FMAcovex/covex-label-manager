"""Actual PySide6 used-stock controls and nonmutating cancel."""
import copy
import pytest
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QDialog
from test_r3a_qt import studio
from covex_label_manager.qt_ui.sheet_designer import SheetDesigner,OccupiedSlotsDialog
from covex_label_manager.engine import plan_sheet


def test_used_slots_picker_and_undo_and_cancel(studio,monkeypatch):
    w,s,app=studio
    p=dict(layout_version=1,paper='A4',layout_mode='grid',orientation='portrait',
           width_mm=90,height_mm=60,margin_mm=8,gap_mm=3,offset_x_mm=0,
           offset_y_mm=0,start_slot=1,safety_mm=0)
    source=copy.deepcopy(p)
    d=SheetDesigner(w,p)
    number=plan_sheet(p,1).capacity
    def select(dialog):
        dialog.checks[2].setChecked(True)
        return QDialog.DialogCode.Accepted
    monkeypatch.setattr(OccupiedSlotsDialog,'exec',select)
    d.mark_used_slots()
    assert d.profile['occupied_slots']==[2]
    assert d.profile['layout_version']==1
    assert plan_sheet(d.profile,1).capacity==number
    assert source==p
    d.undo()
    assert not d.profile.get('occupied_slots')
    d.redo()
    assert d.profile['occupied_slots']==[2]
    d.reject()
    assert source==p


def test_used_slots_picker_marks_start_slot_unavailable(studio):
    w,s,app=studio
    d=OccupiedSlotsDialog(w,6,3,[5])
    assert d.checks[1].isChecked() and not d.checks[1].isEnabled()
    assert d.checks[2].isChecked() and not d.checks[2].isEnabled()
    assert d.checks[5].isChecked()
    assert d.occupied()==[5]
