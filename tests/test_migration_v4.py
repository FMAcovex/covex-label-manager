"""Migration gate: synthetic-only; no Store v4 integration until Windows proof."""
import json
import sqlite3
from contextlib import closing
from decimal import Decimal
from pathlib import Path
import pytest
from covex_label_manager.storage import Store
from v3_fixture import create as create_v3,add_legacy_issue
from covex_label_manager.canonical import canonical,digest,parse
from covex_label_manager.migration_v4 import (migrate,recover,active_path,restore_backup,
    validate_v4,old_rows,check_rows,ro,PHASES,sha)


def fixture(root):
    with closing(create_v3(root)) as s:
        s.set_setting('synthetic','preserve')
        import fitz
        selected=s.db.execute("SELECT id FROM versions WHERE version='00' ORDER BY id LIMIT 1").fetchone()[0]
        s.approve(selected,'Synthetic reviewer','SYNTHETIC APPROVAL REF')
        path=root/'emissions'/'synthetic-history.pdf'
        with fitz.open() as doc:
            doc.new_page().insert_text((10,40),'SYNTHETIC HISTORICAL OUTPUT');doc.save(path)
        issue=add_legacy_issue(s,selected,'Synthetic operator',2,1,[1,2],{'lote':'DEMO'}, {'width_mm':80},path,per_container={'1':{'peso':'10'}},status={})
        add_legacy_issue(s,selected,'Synthetic operator',2,1,[1],{'lote':'DEMO'}, {'width_mm':80},path,source_issue_id=issue,reason='Synthetic reprint')
        evidence=root/'approval_evidence'/'synthetic';evidence.mkdir(parents=True)
        (evidence/'evidence.txt').write_text('SYNTHETIC EXTERNAL EVIDENCE',encoding='utf-8')
        before=old_rows(s.db)
    return before


def test_canonical_vectors():
    vectors=[({'z':-0.0,'é':Decimal('1.2300'),'a':[1e-7,'e\u0301']},'{"a":[0.0000001,"é"],"z":0,"é":1.23}'),
             ({'x':Decimal('100000000000000000000.00')},'{"x":100000000000000000000}')]
    for value,expected in vectors:
        assert canonical(value)==expected
        assert digest(value)==digest(parse(expected))
    assert digest(vectors[0][0])=='c59ed642cbc30ff3b0fbcea26eb3c0e32718a6ebfc1a4ce16959401d83ce33ad'
    assert digest({'n':1})==digest({'n':1.0})==digest({'n':Decimal('1.000')})
    for value in (float('nan'),float('inf'),{'e\u0301':1,'é':2},'\ud800'):
        with pytest.raises((ValueError,UnicodeError)):canonical(value)
    with pytest.raises(ValueError):parse('{"x":1,"x":2}')


def test_preserve_backup_restore(tmp_path):
    root=tmp_path/'v3';before=fixture(root)
    receipt=migrate(root,confirmed=True)
    assert (root/'labels.sqlite').is_dir()
    assert active_path(root)==root/'storage_v4'/'labels.sqlite'
    with closing(ro(active_path(root))) as db:
        integrity=old_rows(db);check_rows(db,{k:v for k,v in before.items() if k!='audit'})
        assert db.execute('SELECT count(*) FROM design_variants').fetchone()[0]==0
        assert db.execute("SELECT state FROM versions WHERE version='00-R1'").fetchone()==('PENDING',)
        assert db.execute('SELECT count(*) FROM schema_migrations').fetchone()[0]==1
    archive=root/receipt['area']/'pre-v4.zip'
    restored=restore_backup(archive,tmp_path/'restored')
    with closing(ro(restored/'labels.sqlite')) as db:assert old_rows(db)==before
    assert migrate(root,confirmed=True)==receipt
    # Old unmodified Store: connect fails before _schema/seed.
    original_hash=sha(active_path(root))
    with pytest.raises(sqlite3.OperationalError):sqlite3.connect(root/'labels.sqlite')
    assert sha(active_path(root))==original_hash


@pytest.mark.parametrize('phase',PHASES)
def test_interrupt_each_phase(tmp_path,phase):
    root=tmp_path/'data';fixture(root)
    def crash(name,_):
        if name==phase:raise RuntimeError('synthetic interruption')
    with pytest.raises(RuntimeError):migrate(root,crash,confirmed=True)
    outcome=recover(root)
    assert outcome==('v4' if phase in ('PUBLISHED','VERIFIED') else 'v3')
    if outcome=='v3':migrate(root,confirmed=True)
    validate_v4(active_path(root))


def test_racing_old_creator_preserved(tmp_path):
    root=tmp_path/'data';fixture(root)
    def race(name,root):
        if name=='LEGACY_ISOLATED':(root/'labels.sqlite').write_bytes(b'old-writer-must-not-be-deleted')
    with pytest.raises(FileExistsError):migrate(root,race,confirmed=True)
    assert not (root/'storage_v4').exists()
    with pytest.raises(ValueError):recover(root)
    assert (root/'labels.sqlite').read_bytes()==b'old-writer-must-not-be-deleted'


def test_unknown_and_corruption_abort(tmp_path):
    root=tmp_path/'data';fixture(root)
    with sqlite3.connect(root/'labels.sqlite') as db:db.execute('PRAGMA user_version=999')
    with pytest.raises(ValueError):migrate(root,confirmed=True)
    assert not (root/'storage_v4').exists()
    with sqlite3.connect(root/'labels.sqlite') as db:db.execute('PRAGMA user_version=3')
    source=next((root/'sources').glob('*'));source.write_bytes(b'corrupted')
    with pytest.raises(ValueError):migrate(root,confirmed=True)
    assert not (root/'migration-v4.json').exists()


def test_failed_ddl_transaction_rolls_back(tmp_path,monkeypatch):
    from covex_label_manager import schema_v4
    root=tmp_path/'data';before=fixture(root)
    monkeypatch.setattr(schema_v4,'STATEMENTS',schema_v4.STATEMENTS+['INVALID SYNTHETIC SQL'])
    with pytest.raises(sqlite3.Error):migrate(root,confirmed=True)
    with closing(ro(root/'labels.sqlite')) as db:assert old_rows(db)==before
    staged=next((root/'backups').glob('*/staged.sqlite'))
    with closing(ro(staged)) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0]==3
        assert not db.execute("SELECT 1 FROM sqlite_master WHERE name='design_variants'").fetchone()


def test_backup_corruption_rejected(tmp_path):
    root=tmp_path/'data';fixture(root);receipt=migrate(root,confirmed=True)
    archive=root/receipt['area']/'pre-v4.zip';archive.write_bytes(b'broken backup')
    with pytest.raises(ValueError):recover(root)


def test_missing_barrier_future_schema_and_changed_schema(tmp_path):
    root=tmp_path/'data';fixture(root);migrate(root,confirmed=True)
    with sqlite3.connect(root/'storage_v4'/'labels.sqlite') as db:
        db.execute('DROP TRIGGER issues_snapshot_insert')
    with pytest.raises(ValueError):active_path(root)


def test_new_issue_cannot_omit_snapshot_at_sql_boundary(tmp_path):
    from covex_label_manager.schema_v4 import configure
    root=tmp_path/'data';fixture(root);migrate(root,confirmed=True)
    with sqlite3.connect(active_path(root)) as db:
        configure(db)
        sql="""INSERT INTO issues(version_id,created_at,operator,count_containers,copies_per_container,
             selected_indices,variables_json,profile_json,pdf_path) SELECT version_id,created_at,operator,
             count_containers,copies_per_container,selected_indices,variables_json,profile_json,pdf_path FROM issues LIMIT 1"""
        with pytest.raises(sqlite3.IntegrityError,match='snapshot'):db.execute(sql)
        assert db.execute('SELECT count(*) FROM issues WHERE design_snapshot_json IS NULL').fetchone()[0]==2


def test_backup_includes_evidence_and_hashes(tmp_path):
    import zipfile
    from covex_label_manager.migration_v4 import verify_backup
    root=tmp_path/'data';fixture(root);receipt=migrate(root,confirmed=True)
    archive=root/receipt['area']/'pre-v4.zip'
    manifest=verify_backup(archive)
    assert 'approval_evidence/synthetic/evidence.txt' in manifest['files']
    restored=restore_backup(archive,tmp_path/'restored')
    assert (root/'approval_evidence/synthetic/evidence.txt').read_bytes()==(restored/'approval_evidence/synthetic/evidence.txt').read_bytes()


def test_backup_failure_and_disk_full_leave_legacy_untouched(tmp_path,monkeypatch):
    from covex_label_manager import migration_v4 as module
    root=tmp_path/'data';before=fixture(root)
    monkeypatch.setattr(module.shutil,'disk_usage',lambda _:type('Usage',(),{'free':0})())
    with pytest.raises(OSError,match='Espacio'):migrate(root,confirmed=True)
    with closing(ro(root/'labels.sqlite')) as db:assert old_rows(db)==before
    assert not (root/'migration-v4.json').exists()


def test_sqlite_backup_includes_uncheckpointed_wal(tmp_path):
    from covex_label_manager.migration_v4 import make_backup,verify_backup
    root=tmp_path/'data';fixture(root)
    area=root/'backups'/'wal-test';area.mkdir()
    with closing(sqlite3.connect(root/'labels.sqlite')) as db:
        db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA wal_autocheckpoint=0')
        db.execute("INSERT INTO settings VALUES('wal-only','SYNTHETIC WAL DATA')");db.commit()
        assert Path(str(root/'labels.sqlite')+'-wal').stat().st_size>0
        archive,snap,_=make_backup(root,area,db)
    restore_backup(archive,tmp_path/'restored-wal')
    with closing(ro(tmp_path/'restored-wal'/'labels.sqlite')) as db:
        assert db.execute("SELECT value FROM settings WHERE key='wal-only'").fetchone()==('SYNTHETIC WAL DATA',)


def test_migration_audit_recovered_exactly_once(tmp_path):
    root=tmp_path/'data';fixture(root)
    def crash(name,_):
        if name=='PUBLISHED':raise RuntimeError('synthetic')
    with pytest.raises(RuntimeError):migrate(root,crash,confirmed=True)
    recover(root);recover(root)
    with closing(ro(active_path(root))) as db:
        assert db.execute("SELECT count(*) FROM audit WHERE event='MIGRATE_V4'").fetchone()[0]==1


@pytest.mark.skipif(__import__('os').name!='nt',reason='Windows sharing semantics require a Windows runner')
def test_windows_refuses_existing_old_sqlite_reader(tmp_path):
    root=tmp_path/'data';fixture(root)
    with closing(sqlite3.connect(root/'labels.sqlite')) as reader:
        reader.execute('SELECT * FROM settings').fetchall()
        with pytest.raises(PermissionError):migrate(root,confirmed=True)
    assert (root/'labels.sqlite').is_file()
    assert not (root/'storage_v4').exists()
