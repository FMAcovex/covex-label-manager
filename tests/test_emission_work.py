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


def test_tk_persistence_wraps_legacy_methods():
    from covex_label_manager.gui import Application
    from covex_label_manager.work_tk import WorkTkMixin
    for name in ('show','_quit','page_emit','_emit_label_change','select_emission_version'):
        assert getattr(Application,name) is getattr(WorkTkMixin,name)


def test_unknown_contract_symlink_and_no_rollback_of_issued(work):
    api,w=work;path=api.work.path(w['uid']);raw=path.read_text()
    path.write_text(raw.replace('"contract":1','"contract":2'))
    with pytest.raises(WorkCorrupt):api.work.get(w['uid'])
    unknown=path.read_bytes()
    with pytest.raises(WorkCorrupt):api.work.recover_previous(w['uid'])
    assert path.read_bytes()==unknown
    path.write_text(raw)
    issued,_,_=api.work.issue(w['uid'],w['generation'],'Synthetic')
    path.write_bytes(b'corrupted after commit')
    with pytest.raises(PermissionError):api.work.recover_previous(w['uid'])
    assert len(api.issues())==1


@pytest.mark.parametrize('phase',['INTENT','RENDERED','COMMITTED','WRITE_BEFORE','WRITE_AFTER'])
def test_real_process_exit_during_issue(work,phase):
    api,w=work
    script="""import os,sys
from covex_label_manager.storage import Store
from covex_label_manager.services import LocalServices
api=LocalServices(Store(sys.argv[1]))
if sys.argv[4].startswith('WRITE_'):
 real=os.replace;target=api.work.path(sys.argv[2])
 def replace(src,dest):
  if str(dest)==str(target) and sys.argv[4]=='WRITE_BEFORE':os._exit(73)
  real(src,dest)
  if str(dest)==str(target) and sys.argv[4]=='WRITE_AFTER':os._exit(73)
 os.replace=replace
 api.work.save(sys.argv[2],int(sys.argv[3]),{'count':'3'})
else:api.work.issue(sys.argv[2],int(sys.argv[3]),'Synthetic process',lambda phase,w:os._exit(73) if phase==sys.argv[4] else None)
"""
    p=subprocess.run([sys.executable,'-c',script,api.location(),w['uid'],str(w['generation']),phase],capture_output=True,text=True,timeout=30)
    assert p.returncode==73,p.stderr
    recovered=api.work.get(w['uid'])
    if phase.startswith('WRITE_'):
        assert recovered['phase']=='DRAFT' and recovered['count']==('3' if phase=='WRITE_AFTER' else w['count'])
        assert recovered['generation']==w['generation']+int(phase=='WRITE_AFTER')
        assert not api.issues();return
    assert recovered['phase']==('ISSUED' if phase=='COMMITTED' else 'EMITTING')
    assert len(api.issues())==int(phase=='COMMITTED')


def test_schema_unchanged_and_document_withdrawn_after_render(work):
    api,w=work;db=api._repository.db
    before=db.execute("SELECT type,name,sql FROM sqlite_master ORDER BY type,name").fetchall()
    vid=w['binding']['revision_id']
    def withdraw(phase,_):
        if phase=='RENDERED':
            with closing(Store(api.location())) as other:
                other.db.execute("UPDATE versions SET state='RETIRED' WHERE id=?",(vid,));other.db.commit()
    with pytest.raises(WorkConflict):api.work.issue(w['uid'],w['generation'],'Synthetic',withdraw)
    assert not api.issues() and api.work.get(w['uid'])['phase']=='EMITTING'
    assert db.execute('PRAGMA user_version').fetchone()[0]==4
    assert db.execute("SELECT type,name,sql FROM sqlite_master ORDER BY type,name").fetchall()==before



def test_canonical_unicode_work_matches_document_and_render(work):
    import fitz
    api,w=work;vid=api.clone_version(w['binding']['revision_id'],'UNICODE','Synthetic Unicode vector')
    v=api.version(vid);fields=json.loads(v['fields_json']);fields[0]['key']='cafe\u0301'
    api.replace_pending_fields(vid,fields)
    api.approve(vid,'Re\u0301viseur','SYNTHETIC UNICODE APPROVAL')
    created=api.work.create(vid,name='Cafe\u0301 synthe\u0301tique')
    created=api.work.save(created['uid'],1,{'values':dict(w['values'],**{'cafe\u0301':'VECTOR-12345'}),'profile':dict(w['profile'])})
    loaded=api.work.get(created['uid']);assert loaded['name']=='Café synthétique'
    issued,path,_=api.work.issue(loaded['uid'],loaded['generation'],'Synthetic')
    with fitz.open(path) as pdf:assert 'VECTOR-12345' in ''.join(p.get_text() for p in pdf)
    assert json.loads(api.version(vid)['fields_json'])[0]['key']=='cafe\u0301'
    assert api.version(vid)['approved_by']=='Re\u0301viseur'



def test_backup_excludes_concurrent_work_cutover(work,tmp_path,monkeypatch):
    import zipfile
    api,w=work;original=zipfile.ZipFile.write;blocked=[]
    def write(archive,filename,*args,**kwargs):
        if str(filename).endswith(w['uid']+'.json'):
            with pytest.raises(WorkConflict):api.work.issue(w['uid'],w['generation'],'Synthetic concurrent issue')
            blocked.append(True)
        return original(archive,filename,*args,**kwargs)
    monkeypatch.setattr(zipfile.ZipFile,'write',write)
    archive=api.backup();assert blocked and not api.issues()
    restored=restore_backup(archive,tmp_path/'restore-consistent')
    with closing(Store(restored)) as s:
        other=LocalServices(s);assert other.work.get(w['uid'])==w and not other.issues()
    def backup_while_issuing(phase,_):
        if phase=='COMMITTED':
            with pytest.raises(WorkConflict):api.backup()
    issued,_,_=api.work.issue(w['uid'],w['generation'],'Synthetic',backup_while_issuing)
    archive=api.backup();restored=restore_backup(archive,tmp_path/'restore-issued')
    with closing(Store(restored)) as s:
        other=LocalServices(s);loaded=other.work.get(w['uid'])
        assert loaded==issued and other.issue(loaded['issue_id']) is not None
