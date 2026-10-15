"""Independent draft durability, concurrency, and issue boundary, synthetic only."""
import copy
import json
import os
import subprocess
import sys
from contextlib import closing
import pytest
from covex_label_manager.storage import Store
from covex_label_manager.services import LocalServices
from covex_label_manager.emission_work import WorkConflict,WorkCorrupt,file_lock
from covex_label_manager.migration_v4 import restore_backup

@pytest.fixture
def work(tmp_path):
    s=Store(tmp_path/'data');api=LocalServices(s)
    vid=next(r['version_id'] for r in api.library_records() if r['name']=='ACETONA')
    api.approve(vid,'Synthetic QA','SYNTHETIC EXTERNAL REF')
    w=api.work.create(vid,None,'Lote sintético')
    w=api.work.save(w['uid'],w['generation'],{'values':{'lote':'SYNTH-ñ','cantidad':'1 kg','proveedor':'SYNTH','direccion':'SYNTH','telefono':'123','observaciones':'DEMO'},'count':'2',
        'per_container':{'2':{'lote':'SYNTH-2','pn':'0,35','pb':'0,50'}},'profile':dict(w['profile'],width_mm='100',height_mm='150')})
    yield api,w
    s.close()


def test_restart_cas_copy_incomplete_and_no_issue(work):
    api,w=work
    with closing(Store(api.location())) as other:
        repo=LocalServices(other).work
        loaded=repo.get(w['uid']);assert loaded==w
        changed=repo.save(w['uid'],w['generation'],{'count':'','values':dict(w['values'],lote='otro lote')})
    with pytest.raises(WorkConflict):api.work.save(w['uid'],w['generation'],{'count':'5'})
    assert api.work.get(w['uid'])==changed and not api.issues()
    duplicate=api.work.create(w['binding']['revision_id'],name='Copia',template=changed)
    assert duplicate['uid']!=w['uid'] and duplicate['values']==changed['values'] and duplicate['phase']=='DRAFT'
    with pytest.raises(ValueError):api.work.proof(duplicate['uid'],1,api.output_path('cache','invalid.pdf'))


def test_os_lock_cross_process_and_death_releases(work):
    api,w=work;path=api.work.path(w['uid']).with_suffix('.lock')
    cmd=[sys.executable,'-c',"from covex_label_manager.emission_work import file_lock; import sys;\nwith file_lock(sys.argv[1]): print('locked',flush=True);sys.stdin.read()",str(path)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        assert p.stdout.readline().strip()=='locked'
        with pytest.raises(WorkConflict):api.work.get(w['uid'])
    finally:p.kill();p.wait(timeout=10)
    assert api.work.get(w['uid'])==w


def test_atomic_failure_corruption_previous_and_backup(work,tmp_path,monkeypatch):
    api,w=work;path=api.work.path(w['uid']);before=path.read_bytes()
    import covex_label_manager.migration_v4 as migration
    real=migration.os.replace
    def fail(src,dest):
        if str(dest)==str(path):raise OSError('synthetic disk failure')
        return real(src,dest)
    monkeypatch.setattr(migration.os,'replace',fail)
    with pytest.raises(OSError):api.work.save(w['uid'],w['generation'],{'count':'3'})
    assert path.read_bytes()==before
    monkeypatch.setattr(migration.os,'replace',real)
    path.write_bytes(b'partial bytes')
    with pytest.raises(WorkCorrupt):api.work.get(w['uid'])
    assert api.work.list()[0]['phase']=='ERROR'
    recovered=api.work.recover_previous(w['uid']);assert recovered['values']==w['values']
    assert list(path.parent.glob('*.corrupt-*.txt'))
    archive=api.backup();restored=restore_backup(archive,tmp_path/'restored')
    with closing(Store(restored)) as s:assert LocalServices(s).work.get(w['uid'])==recovered


@pytest.mark.parametrize('phase',['INTENT','RENDERED','COMMITTED'])
def test_interrupted_emission_reconciles_once(work,phase):
    api,w=work
    def crash(name,_):
        if name==phase:raise RuntimeError('synthetic power loss')
    with pytest.raises(RuntimeError):api.work.issue(w['uid'],w['generation'],'Synthetic operator',crash)
    with closing(Store(api.location())) as s:
        other=LocalServices(s);loaded=other.work.get(w['uid'])
        if phase=='COMMITTED':
            assert loaded['phase']=='ISSUED' and loaded['issue_id'] and len(other.issues())==1
            with pytest.raises(PermissionError):other.work.issue(loaded['uid'],loaded['generation'],'Synthetic')
            with pytest.raises(PermissionError):other.work.save(loaded['uid'],loaded['generation'],{'count':'3'})
        else:
            assert loaded['phase']=='EMITTING' and not other.issues()
            with pytest.raises(WorkConflict):other.work.issue(loaded['uid'],loaded['generation'],'Synthetic')
            recovered=other.work.recover_attempt(loaded['uid'],loaded['generation'])
            issued,path,result=other.work.issue(recovered['uid'],recovered['generation'],'Synthetic')
            assert issued['phase']=='ISSUED' and len(other.issues())==1
        snap=json.loads(other.issues()[0]['design_snapshot_json'])
        assert snap['work']['uid']==w['uid'] and len(snap['work']['operation_uid'])==32


def test_document_change_pending_retired_and_refresh(work):
    api,w=work;b=w['binding'];vid=b['revision_id']
    variant=api.create_variant(vid,'WORK','Synthetic','Synthetic','Synthetic')
    draft=api.work.create(vid,variant['id'],'Variante pendiente',w)
    with pytest.raises(PermissionError):api.work.issue(draft['uid'],1,'Synthetic')
    draft=api.work.save(draft['uid'],1,{'values':w['values']})
    api.transition_variant(variant['id'],variant['generation'],'PENDING','Synthetic')
    with pytest.raises(WorkConflict):api.work.proof(draft['uid'],draft['generation'],api.output_path('cache','stale.pdf'))
    fresh=api.work.refresh_binding(draft['uid'],draft['generation']);assert fresh['values']==w['values']
    api.work.proof(fresh['uid'],fresh['generation'],api.output_path('cache','pending.pdf'))
    api.clone_version(vid,'01','Synthetic');api._repository.db.execute("UPDATE versions SET state='RETIRED' WHERE id=?",(vid,));api._repository.db.commit()
    with pytest.raises(WorkConflict):api.work.issue(w['uid'],w['generation'],'Synthetic')
    assert not api.issues()
