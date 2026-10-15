"""R4A first-page used-slot stock: exact geometry and historical parity."""
import copy

import fitz
import pytest

from covex_label_manager.engine import plan_sheet, render_emission, LayoutError, MM
from covex_label_manager.sheet_layout import (
    available_first_page, physical_placements, slots
)
from covex_label_manager.qt_ui.demo import DemoSession


def standard(capacity_two=True):
    return dict(width_mm=90,height_mm=60,margin_mm=8,gap_mm=3,
                offset_x_mm=0,offset_y_mm=0,safety_mm=0,
                paper='A4',orientation='portrait',layout_mode='grid',
                layout_version=1,start_slot=1,crop_marks=1)


def test_new_slot_mask_skips_only_first_sheet_and_preserves_sequence():
    p=standard();initial=plan_sheet(p,1);n=initial.capacity
    assert n>=4
    p['occupied_slots']=[2,3,n]
    first=[i for i in range(n) if i+1 not in {2,3,n}]
    physical_count=len(first)+2
    plan=plan_sheet(p,physical_count)
    assert plan.pages==2
    places=list(physical_placements(p,plan.capacity,physical_count))
    assert places[:len(first)]==[(0,i) for i in first]
    assert places[len(first):]==[(1,0),(1,1)]


def test_start_slot_and_occupied_are_orthogonal():
    p=standard();p['start_slot']=2;p['occupied_slots']=[3]
    n=plan_sheet(p,1).capacity
    expected=[i for i in range(1,n) if i!=2]
    assert available_first_page(p,n)==expected
    assert list(physical_placements(p,n,1))==[(0,expected[0])]


@pytest.mark.parametrize('invalid',[
    '1,2',None,[1,1],[0],[9999],[True],[1.0],[-1]
])
def test_occupation_invalid_shapes_fail_closed(invalid):
    p=standard();p['occupied_slots']=invalid
    with pytest.raises(LayoutError):plan_sheet(p,1)


def test_refuse_fully_occupied_first_page_and_incompatible_legacy():
    p=standard();n=plan_sheet(p,1).capacity
    p['occupied_slots']=list(range(1,n+1))
    with pytest.raises(LayoutError,match='no tiene casillas libres'):plan_sheet(p,1)
    from covex_label_manager.sheet_layout import require_legacy
    with pytest.raises(ValueError):require_legacy(p)
    q=standard();q.pop('layout_version');q['occupied_slots']=[1]
    with pytest.raises(LayoutError):plan_sheet(q,1)


def test_legacy_a4_layout_unchanged_with_no_occupation():
    p=standard();p.pop('layout_version');p.pop('layout_mode');p.pop('paper')
    p['start_slot']=2
    plan=plan_sheet(p,5)
    assert list(physical_placements(p,plan.capacity,5))==[
        (0,1),(0,2),(0,3),(0,4),(0,5)
    ]


def test_pdf_skips_used_boxes_but_preserves_number_and_pages(tmp_path):
    demo=DemoSession()
    try:
        p=standard();p['occupied_slots']=[1,3]
        v=dict(demo.services.version(demo.initial_id));v['fields_json']='[]'
        total=5;out=tmp_path/'synthetic-proof.pdf'
        result=render_emission(v,demo.services._repository.root,{},p,list(range(1,total+1)),
                               total,1,out,True)
        plan=plan_sheet(p,total)
        with fitz.open(out) as pdf:
            assert len(pdf)==plan.pages==result['pages']
            expected=list(physical_placements(p,plan.capacity,total))
            slots_on_sheet=slots(p,plan.cols,plan.rows)
            rectangles=[]
            for pgno,page in enumerate(pdf):
                for d in page.get_drawings():
                    if d.get('color') and d['color'][0]>.7:
                        rect=d['rect']
                        rectangles.append((pgno,rect.x0/MM,rect.y0/MM))
            assert len(rectangles)==total
            for actual,(page_no,slot) in zip(rectangles,expected):
                box=slots_on_sheet[slot]
                assert actual==(page_no,pytest.approx(box.x,abs=.1),pytest.approx(box.y,abs=.1))
    finally:
        demo.close()
