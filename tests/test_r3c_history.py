"""Shared Qt/Tk history contract, synthetic fixtures and corruption/failure gates."""
import json
from contextlib import closing
import fitz
import pytest
from test_emission_work import work
from covex_label_manager.storage import Store
from covex_label_manager.services import LocalServices


def allow_synthetic_corruption(db):
    # Deliberately simulate out-of-application file corruption. The production
    # trigger itself is verified elsewhere and remains unchanged by R3C.
    triggers=db.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name='issues'").fetchall()
    for trigger in triggers:db.execute('DROP TRIGGER '+trigger[0])


def emitted(work):
    api,w=work;issued,path,result=api.work.issue(w['uid'],w['generation'],'Synthetic QA')
    return api,issued['issue_id']


def test_reprint_proof_original_numbers_and_document_snapshot(work):
    api,pk=emitted(work);report=api.history.inspect(pk);first=dict(report['issue'])
    _,path,_=api.history.reproduce(pk,'2','Synthetic damage','QA',expected_token=report['token'],proof=True)
    assert len(api.issues())==1
    with fitz.open(path) as pdf:assert 'PRUEBA' in ''.join(p.get_text() for p in pdf)
    second,path,result=api.history.reproduce(pk,'2','Synthetic damage','QA',expected_token=report['token'])
    row=api.issue(second);assert row['source_issue_id']==pk and json.loads(row['selected_indices'])==[2]
    assert row['variables_json']==first['variables_json'] and row['per_container_json']==first['per_container_json']
    assert json.loads(row['design_snapshot_json'])['design']==report['snapshot']['design']
    with fitz.open(path) as pdf:
        text=''.join(p.get_text() for p in pdf);assert '2/2' in text and 'SYNTH-2' in text and 'PRUEBA' not in text
    assert dict(api.issue(pk))==first


@pytest.mark.parametrize('selection,reason',[('3','Damage'),('1-1000000000','Damage'),('1','x'),('','Damage')])
def test_reprint_rejects_invalid_ranges_and_reason(work,selection,reason):
    api,pk=emitted(work)
    with pytest.raises(ValueError):api.history.reproduce(pk,selection,reason,'QA')
    assert len(api.issues())==1


@pytest.mark.parametrize('damage',['pdf','snapshot','retired','origin_changed','failed_insert'])
def test_history_integrity_state_concurrency_and_registration_failure(work,monkeypatch,damage):
    api,pk=emitted(work);report=api.history.inspect(pk);row=report['issue'];db=api._repository.db
    if damage=='pdf':report['path'].write_bytes(b'changed PDF')
    if damage=='snapshot':allow_synthetic_corruption(db);db.execute('UPDATE issues SET design_snapshot_sha256=? WHERE id=?',('0'*64,pk));db.commit()
    if damage=='retired':db.execute("UPDATE versions SET state='RETIRED' WHERE id=?",(row['version_id'],));db.commit()
    if damage=='origin_changed':db.execute('UPDATE issues SET reason=? WHERE id=?',('concurrent change',pk));db.commit()
    if damage=='failed_insert':
        def fail(*a,**k):raise RuntimeError('synthetic insert failure')
        monkeypatch.setattr(api,'add_issue',fail)
    with pytest.raises((ValueError,PermissionError)):api.history.reproduce(pk,'1','Synthetic damage','QA',expected_token=report['token'])
    assert len(api.issues())==1
    if damage=='failed_insert':assert len(list(api.asset_path('emissions').glob('*.pdf')))==1


def test_legacy_null_requires_ack_and_is_not_retrofilled(work):
    api,pk=emitted(work);db=api._repository.db
    allow_synthetic_corruption(db)
    db.execute('UPDATE issues SET design_snapshot_json=NULL,design_snapshot_sha256=NULL WHERE id=?',(pk,));db.commit()
    report=api.history.inspect(pk);assert report['snapshot'] is None and report['warnings']
    with pytest.raises(PermissionError):api.history.reproduce(pk,'2','Synthetic legacy','QA')
    second,_,_=api.history.reproduce(pk,'2','Synthetic legacy','QA',acknowledge_legacy=True,expected_token=report['token'])
    assert api.issue(pk)['design_snapshot_json'] is None and api.issue(second)['design_snapshot_json'] is not None


def test_origin_changed_between_render_and_transaction_is_blocked(work,monkeypatch):
    api,pk=emitted(work);real=api.add_issue
    def altered(*a,**k):
        with closing(Store(api.location())) as other:
            other.db.execute('UPDATE issues SET operator=? WHERE id=?',('CONCURRENT',pk));other.db.commit()
        return real(*a,**k)
    monkeypatch.setattr(api,'add_issue',altered)
    with pytest.raises(ValueError,match='origen'):api.history.reproduce(pk,'1','Synthetic damage','QA')
    assert len(api.issues())==1


def test_schema_and_master_history_unchanged_by_native_services(work):
    api,w=work;s=api._repository
    schema=[tuple(r) for r in s.db.execute('SELECT type,name,sql FROM sqlite_master ORDER BY type,name')]
    before=dict(api.version(w['binding']['revision_id']))
    api,pk=emitted(work);api.history.reproduce(pk,'2','Synthetic reason','QA')
    assert [tuple(r) for r in s.db.execute('SELECT type,name,sql FROM sqlite_master ORDER BY type,name')]==schema
    assert dict(api.version(w['binding']['revision_id']))==before
    assert next(r for r in api.library_records() if r['version']=='00-R1')['state']=='PENDING'


def test_reprint_error_after_commit_keeps_registered_pdf_and_reconciles(work,monkeypatch):
    api,pk=emitted(work);real=api.add_issue
    def committed(*a,**k):
        real(*a,**k);raise OSError('synthetic post-commit failure')
    monkeypatch.setattr(api,'add_issue',committed)
    second,path,_=api.history.reproduce(pk,'2','Synthetic damage','QA')
    assert len(api.issues())==2 and api.issue(second)['source_issue_id']==pk
    assert path.is_file() and api.history.inspect(second)['reprint_allowed']
