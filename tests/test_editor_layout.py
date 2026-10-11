"""Synthetic coordinate/command regression independent of the Qt runtime."""
import copy
import json
import math
import pytest
from covex_label_manager.editor_layout import (LayoutHistory, recrop, move_field,
    align_fields, scale_fields, anchor_field, relocate_anchors, validate_layout,
    check_locked_changes, layout_from_version, source_identity, MM_PER_POINT)


@pytest.fixture
def layout():
    return dict(crop=[10,20,410,320],area=[.7,.8,.2,.1],fields=[
        dict(key='a',label='A',x=.15,y=.2,w=.15,h=.08,font_pt=12,draw='continuation',
             erase=[.14,.19,.17,.1],second_x=.12,next_w=.3,max_lines=3),
        dict(key='b',label='B',x=.5,y=.5,w=.15,h=.08,font_pt=12),
        dict(key='c',label='C',x=.75,y=.65,w=.12,h=.08,font_pt=12)])


def absolute(f,c):
    return [c[0]+f['x']*(c[2]-c[0]),c[1]+f['y']*(c[3]-c[1]),f['w']*(c[2]-c[0]),f['h']*(c[3]-c[1])]


def test_recrop_preserves_absolute_special_geometry_and_original(layout):
    before=copy.deepcopy(layout); result=recrop(layout,[20,30,400,310])
    for a,b in zip(layout['fields'],result['fields']):
        assert absolute(a,layout['crop'])==pytest.approx(absolute(b,result['crop']),abs=1e-6)
    a=layout['fields'][0]; b=result['fields'][0]
    assert 10+a['second_x']*400==pytest.approx(20+b['second_x']*380)
    assert a['next_w']*400==pytest.approx(b['next_w']*380)
    assert layout==before


def test_recrop_exclusion_is_atomic(layout):
    before=copy.deepcopy(layout)
    with pytest.raises(ValueError): recrop(layout,[150,30,400,310])
    assert layout==before
    with pytest.raises(ValueError): recrop(layout,[10,20,25,320])


@pytest.mark.parametrize('mode',['left','right','top','bottom','center_x','center_y','distribute_y'])
def test_alignment_keeps_special_geometry_relative_to_field(layout,mode):
    result=align_fields(layout,[0,1,2],mode)
    old=layout['fields'][0]; new=result['fields'][0]
    assert new['erase'][0]-new['x']==pytest.approx(old['erase'][0]-old['x'])
    assert new['erase'][1]-new['y']==pytest.approx(old['erase'][1]-old['y'])
    assert new['second_x']-new['x']==pytest.approx(old['second_x']-old['x'])


def test_distribution_and_locked_selection(layout):
    result=align_fields(layout,[0,1,2],'distribute_x'); a,b,c=result['fields']
    assert b['x']-(a['x']+a['w'])==pytest.approx(c['x']-(b['x']+b['w']))
    layout['fields'][1]['locked']=True
    with pytest.raises(ValueError): align_fields(layout,[0,1],'left')
    with pytest.raises(ValueError): scale_fields(layout,[0,1],.9)


def test_proportional_transform_includes_erase_continuation_and_status(layout):
    result=scale_fields(layout,[0,1,2],.8,True,True)
    f=result['fields'][0]
    assert f['w']==pytest.approx(layout['fields'][0]['w']*.8)
    assert f['next_w']==pytest.approx(.3*.8)
    assert f['font_pt']==pytest.approx(12*.8)
    assert result['area'][2]==pytest.approx(.2*.8)
    assert result['crop']==layout['crop']


def test_locked_absolute_geometry_can_be_recropped_but_not_deleted_or_moved(layout):
    layout['fields'][0]['locked']=True
    check_locked_changes(layout,recrop(layout,[20,30,400,310]))
    changed=copy.deepcopy(layout); changed['fields'].pop(0)
    with pytest.raises(ValueError): check_locked_changes(layout,changed)
    changed=copy.deepcopy(layout); changed['fields'][0]['x']+=.01
    with pytest.raises(ValueError): check_locked_changes(layout,changed)


def test_complete_history_save_point_and_redo_branch(layout):
    history=LayoutHistory(layout); changed=recrop(layout,[20,30,400,310]); changed['area']=[]
    history.push(changed,'crop+state'); history.mark_clean(); assert not history.dirty
    history.undo(); assert history.state==layout and history.dirty
    history.redo(); assert history.state==changed and not history.dirty
    history.undo(); history.push(scale_fields(layout,[1],.9),'new command'); assert not history.redo_states


@pytest.mark.parametrize('value',[float('nan'),float('inf'),-1])
def test_invalid_geometry_is_not_added_to_history(layout,value):
    history=LayoutHistory(layout); bad=copy.deepcopy(layout); bad['fields'][0]['x']=value
    with pytest.raises(ValueError): history.push(bad,'invalid')
    assert history.state==layout and not history.undo_states


def test_anchor_identity_ambiguity_offset_and_source_guard(layout):
    layout['fields'][0].pop('erase'); layout['fields'][0].pop('second_x'); layout['fields'][0].pop('next_w')
    span=dict(text='SYNTHETIC LOT:',bbox=[35,60,100,72],origin=[35,70],size=10,font='Helvetica')
    anchored=anchor_field(layout,0,span,0,'synthetic-hash')
    assert anchored['fields'][0]['x']==pytest.approx((101.5-10)/400)
    moved=copy.deepcopy(anchored); move_field(moved['fields'][0],-.02,.01,moved['crop'])
    restored=relocate_anchors(moved,[span],'synthetic-hash')
    assert restored['fields'][0]['x']==pytest.approx(moved['fields'][0]['x'])
    with pytest.raises(ValueError): relocate_anchors(anchored,[span,span],'synthetic-hash')
    with pytest.raises(ValueError): relocate_anchors(anchored,[span],'different-source')


def test_service_save_is_atomic_and_detects_external_crop_change(tmp_path,layout):
    import fitz
    from covex_label_manager.storage import Store
    from covex_label_manager.qt_transition import TransitionServices
    source=tmp_path/'synthetic.pdf'
    with fitz.open() as d:
        p=d.new_page(width=450,height=350); p.insert_text((30,40),'SYNTHETIC SOURCE'); d.save(source)
    store=Store(tmp_path/'data',seed=False); api=TransitionServices(store)
    vid=api.add_label('Synthetic','SYN','','','COVEX','','00',source,None,layout['crop'],layout['fields'],'Synthetic only')
    v=api.version(vid); expected=layout_from_version(v); identity=source_identity(v)
    candidate=copy.deepcopy(expected); candidate['area']=layout['area']
    version_before=dict(v); schema=store.db.execute('PRAGMA user_version').fetchone()[0]
    api.save_editor_layout(vid,candidate,expected,identity)
    assert layout_from_version(api.version(vid))==candidate
    assert source_identity(api.version(vid))==identity
    assert store.db.execute('PRAGMA user_version').fetchone()[0]==schema==3
    with pytest.raises(ValueError): api.save_editor_layout(vid,expected,expected,identity)
    assert layout_from_version(api.version(vid))==candidate
    invalid=copy.deepcopy(candidate); invalid['crop']=[0,0,999,999]
    with pytest.raises(ValueError): api.save_editor_layout(vid,invalid,candidate,identity)
    assert layout_from_version(api.version(vid))==candidate
    api.approve(vid,'Synthetic reviewer','SYNTHETIC APPROVAL REFERENCE')
    with pytest.raises(PermissionError): api.save_editor_layout(vid,candidate,candidate,identity)
    api.close()
