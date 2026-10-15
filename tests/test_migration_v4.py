"""Migration gate: synthetic-only; no Store v4 integration until Windows proof."""
import json
import sqlite3
from contextlib import closing
from decimal import Decimal
from pathlib import Path
import pytest
from covex_label_manager.storage import Store
from covex_label_manager.canonical import canonical,digest,parse
from covex_label_manager.migration_v4 import (migrate,recover,active_path,restore_backup,
    validate_v4,old_rows,check_rows,ro,PHASES,sha)


def fixture(root):
    with closing(Store(root)) as s:
        s.set_setting('synthetic','preserve');before=old_rows(s.db)
    return before


def test_canonical_vectors():
    vectors=[({'z':-0.0,'é':Decimal('1.2300'),'a':[1e-7,'e\u0301']},'{"a":[0.0000001,"é"],"z":0,"é":1.23}'),
             ({'x':Decimal('100000000000000000000.00')},'{"x":100000000000000000000}')]
    for value,expected in vectors:
        assert canonical(value)==expected
        assert digest(value)==digest(parse(expected))
    assert digest({'n':1})==digest({'n':1.0})==digest({'n':Decimal('1.000')})
    for value in (float('nan'),float('inf'),{'e\u0301':1,'é':2},'\ud800'):
        with pytest.raises((ValueError,UnicodeError)):canonical(value)
    with pytest.raises(ValueError):parse('{"x":1,"x":2}')


def test_preserve_backup_restore(tmp_path):
    root=tmp_path/'v3';before=fixture(root)
    receipt=migrate(root)
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
    assert migrate(root)==receipt
    # Old unmodified Store: connect fails before _schema/seed.
    original_hash=sha(active_path(root))
    with pytest.raises(sqlite3.OperationalError):Store(root)
    assert sha(active_path(root))==original_hash


@pytest.mark.parametrize('phase',PHASES)
def test_interrupt_each_phase(tmp_path,phase):
    root=tmp_path/'data';fixture(root)
    def crash(name,_):
        if name==phase:raise RuntimeError('synthetic interruption')
    with pytest.raises(RuntimeError):migrate(root,crash)
    outcome=recover(root)
    assert outcome==('v4' if phase in ('PUBLISHED','VERIFIED') else 'v3')
    if outcome=='v3':migrate(root)
    validate_v4(active_path(root))


def test_racing_old_creator_preserved(tmp_path):
    root=tmp_path/'data';fixture(root)
    def race(name,root):
        if name=='LEGACY_ISOLATED':(root/'labels.sqlite').write_bytes(b'old-writer-must-not-be-deleted')
    with pytest.raises(FileExistsError):migrate(root,race)
    assert not (root/'storage_v4').exists()
    with pytest.raises(ValueError):recover(root)
    assert (root/'labels.sqlite').read_bytes()==b'old-writer-must-not-be-deleted'


def test_unknown_and_corruption_abort(tmp_path):
    root=tmp_path/'data';fixture(root)
    with sqlite3.connect(root/'labels.sqlite') as db:db.execute('PRAGMA user_version=999')
    with pytest.raises(ValueError):migrate(root)
    assert not (root/'storage_v4').exists()
    with sqlite3.connect(root/'labels.sqlite') as db:db.execute('PRAGMA user_version=3')
    source=next((root/'sources').glob('*'));source.write_bytes(b'corrupted')
    with pytest.raises(ValueError):migrate(root)
    assert not (root/'migration-v4.json').exists()
