"""Synthetic lifecycle, approval evidence, immutable snapshots and concurrency."""
import copy
import json
import sqlite3
from contextlib import closing
from datetime import date
import fitz
import pytest
from covex_label_manager.storage import Store,sha256
from covex_label_manager.qt_transition import TransitionServices
from covex_label_manager.variants import design_from_revision
from covex_label_manager.canonical import digest


@pytest.fixture
def context(tmp_path):
    s=Store(tmp_path/'data');api=TransitionServices(s)
    v=next(r for r in s.library_records() if r['name']=='ACETONA')
    s.approve(v['version_id'],'Synthetic QA','SYNTHETIC REVISION APPROVAL')
    evidence=tmp_path/'approval.txt';evidence.write_text('SYNTHETIC EXTERNAL APPROVAL',encoding='utf-8')
    yield s,api,v['version_id'],evidence
    s.close()


def create(api,vid,code='BOTTLE',origin=None):return api.create_variant(vid,code,'Synthetic bottle','Synthetic reuse format','Test QA',origin)
def approve(api,row,evidence):
    row=api.transition_variant(row['id'],row['generation'],'PENDING','Test QA')
    return api.approve_variant(row['id'],row['generation'],'External QA','SYNTHETIC-APPROVAL',date.today().isoformat(),evidence,'Test operator')
def profile():return {'width_mm':100,'height_mm':150,'orientation':'portrait','margin_mm':8,'gap_mm':3,'start_slot':1,'safety_mm':0}
def values():return {'lote':'DEMO','cantidad':'1 kg','proveedor':'DEMO','direccion':'DEMO','telefono':'DEMO','observaciones':'DEMO'}


def test_coexistence_freeze_derivation_and_evidence(context):
    s,api,vid,evidence=context;before=dict(s.version(vid));sources={p:sha256(p) for p in (s.root/'pdf_masters').glob('*')}
    first=approve(api,create(api,vid,'ONE'),evidence);second=approve(api,create(api,vid,'TWO'),evidence)
    assert api.variant(first['id'])['state']==api.variant(second['id'])['state']=='APPROVED'
    assert sha256(api.variant_evidence(first['id']))==sha256(evidence)
    for original in (first,second):
        with pytest.raises(PermissionError):api.save_variant(original['id'],original['generation'],json.loads(original['design_json']),'Test QA')
        with pytest.raises(sqlite3.IntegrityError):
            s.db.execute("UPDATE design_variants SET name='tampered',generation=generation+1 WHERE id=?",(original['id'],))
        s.db.rollback()
    derived=create(api,vid,'THREE',first['id'])
    assert derived['state']=='DRAFT' and derived['origin_variant_id']==first['id'] and derived['approved_by'] is None and derived['evidence_path'] is None
    retired=api.transition_variant(first['id'],first['generation'],'RETIRED','Test QA','Superseded fixture')
    assert retired['approved_by']==first['approved_by'] and api.variant(second['id'])['state']=='APPROVED'
    assert dict(s.version(vid))==before
    assert all(sha256(p)==h for p,h in sources.items())


def test_stale_generation_and_transactional_audit(context,monkeypatch):
    s,api,vid,evidence=context;row=create(api,vid)
    design=json.loads(row['design_json']);design['layout']['fields'][0]['font_pt']=10
    newer=api.save_variant(row['id'],row['generation'],design,'Test QA')
    with pytest.raises(ValueError,match='obsoleta'):api.save_variant(row['id'],row['generation'],design,'Test QA')
    with closing(Store(s.root)) as other:
        latest=other.variants.transition(newer['id'],newer['generation'],'PENDING','Other operator')
    with pytest.raises(ValueError,match='obsoleta'):api.transition_variant(newer['id'],newer['generation'],'PENDING','Test QA')
    monkeypatch.setattr(s.variants,'audit',lambda *a:(_ for _ in ()).throw(RuntimeError('synthetic audit failure')))
    with pytest.raises(ValueError,match='sin aprobación'):
        api.approve_variant(latest['id'],latest['generation'],'External QA','SYNTHETIC REF',date.today().isoformat(),evidence,'Test QA')
    assert api.variant(row['id'])['state']=='PENDING'
    assert list((s.root/'approval_evidence'/row['uid']).glob('*'))  # explicit retained orphan; never falsely approved


def test_emission_snapshots_legacy_and_variant(context):
    s,api,vid,evidence=context;row=approve(api,create(api,vid),evidence)
    for variant_id in (None,row['id']):
        v=api.resolved_design(vid,variant_id);path=s.root/'emissions'/('output-'+str(variant_id)+'.pdf')
        api.render(v,values(),profile(),[1],1,1,path)
        key=api.add_issue(vid,'Test QA',1,1,[1],values(),profile(),path)
        issue=api.issue(key);snap=json.loads(issue['design_snapshot_json'])
        assert snap['variant_id']==variant_id and issue['design_snapshot_sha256']==digest(snap)
        assert snap['design_sha256']==digest(snap['design']) and issue['pdf_sha256']==sha256(path)
        with pytest.raises(sqlite3.IntegrityError):s.db.execute("UPDATE issues SET design_snapshot_json='{}' WHERE id=?",(key,))
        s.db.rollback()
    proof=s.root/'cache'/'proof.pdf';draft=create(api,vid,'DRAFT')
    v=api.resolved_design(vid,draft['id']);api.render(v,values(),profile(),[1],1,1,proof,True)
    with fitz.open(proof) as doc:assert 'PRUEBA' in doc[0].get_text()
    with pytest.raises(PermissionError):api.render(v,values(),profile(),[1],1,1,s.root/'emissions'/'blocked.pdf')
    api.transition_variant(row['id'],row['generation'],'RETIRED','Test QA','Retired fixture')
    with pytest.raises(PermissionError):api.resolved_design(vid,row['id'],True)


def test_retired_between_render_and_register_and_pdf_tamper(context):
    s,api,vid,evidence=context;row=approve(api,create(api,vid),evidence);v=api.resolved_design(vid,row['id'])
    path=s.root/'emissions'/'not-registered.pdf';api.render(v,values(),profile(),[1],1,1,path)
    api.transition_variant(row['id'],row['generation'],'RETIRED','Test QA','Retired while form open')
    with pytest.raises(PermissionError):api.add_issue(vid,'Test QA',1,1,[1],values(),profile(),path)
    assert not api.issues()
    plain=s.root/'emissions'/'plain.pdf';api.render(api.version(vid),values(),profile(),[1],1,1,plain)
    plain.write_bytes(b'tampered')
    with pytest.raises(ValueError,match='alterado'):api.add_issue(vid,'Test QA',1,1,[1],values(),profile(),plain)
    assert not api.issues()


def test_backup_restore_contains_approval_evidence(context,tmp_path):
    from covex_label_manager.migration_v4 import restore_backup
    s,api,vid,evidence=context;row=approve(api,create(api,vid),evidence)
    archive=api.backup();restored=restore_backup(archive,tmp_path/'restored')
    with closing(Store(restored)) as other:
        assert other.variants.get(row['id'])==row
        assert sha256(other.variants.verify_evidence(row))==sha256(evidence)


def test_pending_parent_cannot_approve_and_changed_evidence_blocks(context):
    s,api,vid,evidence=context;pending=api.clone_version(vid,'01','Synthetic pending document')
    row=create(api,pending);row=api.transition_variant(row['id'],row['generation'],'PENDING','Test QA')
    with pytest.raises(PermissionError):api.approve_variant(row['id'],row['generation'],'External QA','SYNTHETIC',date.today().isoformat(),evidence,'Test QA')
    r1=s.db.execute("SELECT id,state FROM versions WHERE version='00-R1'").fetchone()
    assert r1['state']=='PENDING' and not api.variants(r1['id'])
    row=approve(api,create(api,vid,'APPROVED'),evidence)
    api.variant_evidence(row['id']).write_bytes(b'changed evidence')
    with pytest.raises(ValueError,match='Evidencia'):api.resolved_design(vid,row['id'],True)


def test_variant_geometry_matches_pdf_without_changing_source(context):
    s,api,vid,evidence=context;row=create(api,vid);design=json.loads(row['design_json'])
    field=design['layout']['fields'][0];delta=0.03 if field['x']+field['w']+0.03<1 else -0.03
    field['x']+=delta
    row=api.save_variant(row['id'],row['generation'],design,'Test QA');row=approve(api,row,evidence)
    text=values();text['lote']='VARIANT-ONLY'
    files=[]
    for variant_id in (None,row['id']):
        path=s.root/'cache'/('geometry-'+str(variant_id)+'.pdf')
        api.render(api.resolved_design(vid,variant_id),text,profile(),[1],1,1,path,True)
        with fitz.open(path) as doc:
            boxes=doc[0].search_for('VARIANT-ONLY');assert len(boxes)==1;files.append(boxes[0])
    crop=design['layout']['crop'];scale=min(profile()['width_mm']*72/25.4/(crop[2]-crop[0]),profile()['height_mm']*72/25.4/(crop[3]-crop[1]))
    assert files[1].x0-files[0].x0==pytest.approx(delta*(crop[2]-crop[0])*scale,abs=0.1*72/25.4)


def test_reprint_uses_snapshot_and_original_number_link(context):
    s,api,vid,evidence=context;row=approve(api,create(api,vid),evidence);v=api.resolved_design(vid,row['id'])
    original=s.root/'emissions'/'original.pdf';api.render(v,values(),profile(),[1,2],2,1,original)
    first=api.add_issue(vid,'Test QA',2,1,[1,2],values(),profile(),original);snap=json.loads(api.issue(first)['design_snapshot_json'])
    output=s.root/'emissions'/'reprint.pdf';api.render(v,values(),profile(),[2],2,1,output,history_snapshot=snap)
    second=api.add_issue(vid,'Test QA',2,1,[2],values(),profile(),output,source_issue_id=first,reason='Damaged synthetic label')
    assert api.issue(second)['source_issue_id']==first and api.issue(second)['design_variant_id']==row['id']
    assert json.loads(api.issue(second)['design_snapshot_json'])['design']==snap['design']
