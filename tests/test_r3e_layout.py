"""R3E synthetic geometric contracts, including actual PDF output and recovery."""
import copy
import json
import math
import pytest
import fitz
from covex_label_manager.engine import plan_sheet,render_emission,MM,LayoutError
from covex_label_manager.sheet_layout import slots,template,paper_size,require_legacy
from covex_label_manager.layout_profiles import LayoutProfiles
from covex_label_manager.emission_work import parameters,WorkConflict
from covex_label_manager.qt_ui.demo import DemoSession


def profile(paper='A4',n=5):
    p=dict(layout_version=1,paper=paper,orientation='portrait',layout_mode='free',width_mm=80,height_mm=50,margin_mm=8,gap_mm=3,start_slot=1,safety_mm=0,offset_x_mm=0,offset_y_mm=0,crop_marks=1,printer_name='')
    if paper=='custom':p.update(paper_width_mm=240,paper_height_mm=350)
    p['slots']=template(p,n);return p

@pytest.fixture
def demo():
    s=DemoSession();yield s;s.close()

@pytest.mark.parametrize('orientation',['portrait','landscape'])
@pytest.mark.parametrize('w,h',[(100,70),(140,100),(40,30)])
def test_historical_a4_arithmetic_exact(orientation,w,h):
    p=dict(width_mm=w,height_mm=h,orientation=orientation,margin_mm=8,gap_mm=3,start_slot=2)
    pw,ph=(210,297) if orientation=='portrait' else (297,210)
    cols=math.floor((pw-16+3+1e-9)/(w+3));rows=math.floor((ph-16+3+1e-9)/(h+3))
    p['start_slot']=min(2,cols*rows)
    first_space=cols*rows-p['start_slot']+1
    plan=plan_sheet(p,17);assert (plan.cols,plan.rows,plan.capacity)==(cols,rows,cols*rows)
    assert plan.pages==1+math.ceil(max(0,17-first_space)/(cols*rows))
    for i,b in enumerate(slots(p)):
        assert (b.x,b.y,b.width,b.height)==(8+(i%cols)*(w+3),8+(i//cols)*(h+3),w,h)

@pytest.fixture(scope='module')
def pdf_demo():
    # These cases only render a copied revision into independent tmp_paths.
    # Reuse the read-only synthetic library, not mutable work/profile fixtures.
    s=DemoSession();yield s;s.close()

@pytest.mark.parametrize('paper',['A4','A3','A5','Carta','custom'])
@pytest.mark.parametrize('n',[1,2,5])
@pytest.mark.parametrize('copies',[1,2])
def test_actual_pdf_box_geometry_and_pagination(pdf_demo,tmp_path,paper,n,copies):
    demo=pdf_demo
    p=profile(paper,n);p['start_slot']=min(2,n);v=dict(demo.services.version(demo.initial_id));v['fields_json']='[]'
    out=tmp_path/'proof.pdf';result=render_emission(v,demo.services._repository.root,{},p,[1,3,7],7,copies,out,True)
    boxes=slots(p);plan=plan_sheet(p,3*copies)
    with fitz.open(out) as pdf:
        assert len(pdf)==plan.pages==result['pages']
        rectangles=[]
        for page in pdf:
            assert (page.rect.width/MM,page.rect.height/MM)==pytest.approx(paper_size(p),abs=.001)
            assert 'PRUEBA' in page.get_text()
            for d in page.get_drawings():
                if d.get('color') and d['color'][0]>.7:
                    rectangles.append(tuple(x/MM for x in d['rect']))
        assert len(rectangles)==3*copies
        for i,r in enumerate(rectangles):
            b=boxes[(i+p['start_slot']-1)%n]
            assert r==pytest.approx((b.x,b.y,b.x+b.width,b.y+b.height),abs=.1)

@pytest.mark.parametrize('change',[{'paper':'other'},{'layout_version':2},{'layout_mode':'bad'},{'orientation':'other'},{'margin_mm':float('nan')}])
def test_unknown_contracts_fail_closed(change):
    p=profile();p.update(change)
    with pytest.raises(LayoutError):plan_sheet(p,1)

def test_collisions_limits_and_copy_limit():
    p=profile();p['slots'][1]=copy.deepcopy(p['slots'][0])
    with pytest.raises(LayoutError,match='Solapamiento'):plan_sheet(p,1)
    p=profile();p['slots'][0]['x']=-1
    with pytest.raises(LayoutError,match='límites'):plan_sheet(p,1)
    with pytest.raises(ValueError):parameters(dict(profile=profile(),count='5',copies='5',selection=''))
    with pytest.raises(ValueError,match='Qt'):require_legacy(profile())

def test_profiles_cas_hash_and_backup(demo):
    root=demo.services._repository.root;r=LayoutProfiles(root);p=profile('A3')
    first=r.save('synthetic','Synthetic only',p);assert r.get('synthetic')['profile']==p
    with pytest.raises(WorkConflict):r.save('synthetic','Changed',p,0)
    r.save('synthetic','Changed',p,first['generation'])
    path=demo.services.backup()
    import zipfile
    with zipfile.ZipFile(path) as z:assert any(n.endswith('layout_profiles/synthetic.json') for n in z.namelist())
    data=json.loads(r.path('synthetic').read_text());data['payload']['name']='tampered';r.path('synthetic').write_text(json.dumps(data))
    with pytest.raises(ValueError,match='Integridad'):r.get('synthetic')

def test_work_restart_proof_issue_and_reprint(demo,tmp_path):
    api=demo.services;vid=next(v['id'] for v in api.versions(api.version(demo.initial_id)['label_id']) if v['state']=='APPROVED')
    w=api.work.create(vid,None,'Synthetic R3E');w=api.work.save(w['uid'],w['generation'],{'profile':profile('A3'),'count':'7','copies':'2','selection':'1,3,7','values':{'lote':'SYNTH','pn':'1','pb':'2'}})
    from covex_label_manager.emission_work import WorkRepository
    reopened=WorkRepository(api).get(w['uid']);assert reopened['profile']==w['profile']
    api.work.proof(w['uid'],w['generation'],tmp_path/'proof.pdf')
    with pytest.raises(WorkConflict):api.work.save(w['uid'],w['generation']-1,{'profile':profile()})
    result=api.work.issue(w['uid'],w['generation'],'Synthetic operator')
    assert result


def test_backup_restores_work_profiles_and_conflicting_writer(demo,tmp_path):
    from covex_label_manager.emission_work import file_lock
    from covex_label_manager.storage import Store
    from covex_label_manager.services import LocalServices
    import zipfile
    api=demo.services;repo=LayoutProfiles(api._repository.root);p=profile('A3')
    repo.save('restore-test','Synthetic restore',p)
    with file_lock(repo.root/'catalog.lock'):
        with pytest.raises(WorkConflict):repo.save('restore-test','Conflict',p,1)
    w=api.work.create(demo.initial_id,None,'Synthetic restore');w=api.work.save(w['uid'],w['generation'],{'profile':p})
    archive=api.backup();restored=tmp_path/'restored';restored.mkdir()
    with zipfile.ZipFile(archive) as z:z.extractall(restored)
    recovered=LocalServices(Store(restored,seed=False))
    try:
        assert recovered.work.get(w['uid'])['profile']==p
        assert LayoutProfiles(restored).get('restore-test')['profile']==p
        recovered.work.proof(w['uid'],w['generation'],recovered.output_path('cache','restore-proof.pdf'))
    finally:recovered.close()


def test_corrupt_layout_profile_is_isolated_without_silent_repair(demo):
    root=demo.services._repository.root
    repo=LayoutProfiles(root)
    good=repo.save('known-good','Perfil sintético válido',profile('A3',5))
    bad=repo.root/'corrupt-r3e.json'
    bad.write_text('{"contract":1,"payload":',encoding='utf-8')
    original=bad.read_bytes()
    with pytest.raises(ValueError):
        repo.list()
    available=repo.list(tolerate_corrupt=True)
    assert [entry['uid'] for entry in available]==['known-good']
    assert repo.invalid_files==['corrupt-r3e.json']
    assert repo.get('known-good')==good
    assert bad.read_bytes()==original


def test_mini_sheet_slots_have_explicit_five_mm_minimum():
    p=profile('A4',1)
    p['slots'][0].update(width=7,height=7)
    with pytest.raises(ValueError,match='mínimo 10 mm'):
        slots(p)
    p['mini_mode']=True
    assert slots(p)[0].width==7
    p['slots'][0]['width']=4.99
    with pytest.raises(ValueError,match='mínimo 5 mm'):
        slots(p)


def test_mini_grid_can_be_smaller_than_old_ten_mm_minimum():
    base={'layout_version':1,'layout_mode':'grid','paper':'A4',
          'width_mm':7,'height_mm':7,'margin_mm':8,'gap_mm':3,
          'start_slot':1,'safety_mm':0}
    with pytest.raises(ValueError):
        plan_sheet(base,1)
    allowed={**base,'mini_mode':True}
    plan=plan_sheet(allowed,3)
    assert plan.count_physical==3
    assert plan.capacity>=3


def test_mini_does_not_accept_broken_geometry_or_malformed_flag():
    p=profile('A4',1)
    p['mini_mode']='True'
    with pytest.raises(ValueError,match='booleano'):
        slots(p)
    p['mini_mode']=True;p['slots'][0]['x']=-30
    with pytest.raises(ValueError,match='límites'):
        slots(p)
