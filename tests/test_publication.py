"""Distribution privacy and protection of local data during packaging."""
import json
from pathlib import Path
import pytest
from scripts.check_build_destination import ensure_safe

def test_packaging_refuses_default_and_alternate_data(tmp_path):
    destination=tmp_path/'dist'
    ensure_safe(destination)
    with pytest.raises(ValueError):ensure_safe(destination,destination/'custom-data')
    (destination/'data').mkdir(parents=True)
    with pytest.raises(ValueError):ensure_safe(destination)

def test_packaging_refuses_sqlite_in_arbitrary_directory(tmp_path):
    database=tmp_path/'dist'/'custom'/'labels.sqlite'
    database.parent.mkdir(parents=True);database.write_bytes(b'user data sentinel')
    with pytest.raises(ValueError):ensure_safe(tmp_path/'dist')
    assert database.read_bytes()==b'user data sentinel'

def test_empty_distribution_reuses_existing_instance(monkeypatch,tmp_path):
    import covex_label_manager.storage as storage
    from covex_label_manager.storage import Store
    from covex_label_manager.services import LocalServices
    s=Store(tmp_path/'data');api=LocalServices(s)
    row=next(x for x in api.library.entries() if x['version']=='00-R1')
    api.library.favorite(row);api.library.opened(row)
    api.set_setting('operator','Synthetic update operator')
    before={t:[tuple(r) for r in s.db.execute('SELECT * FROM '+t+' ORDER BY rowid')]
            for t in ('versions','materials','profiles','settings','library_preferences')}
    api.close()
    empty=tmp_path/'empty-resources';empty.mkdir()
    monkeypatch.setattr(storage,'resource_dir',lambda:empty)
    s=Store(tmp_path/'data')
    try:
        assert before=={t:[tuple(r) for r in s.db.execute('SELECT * FROM '+t+' ORDER BY rowid')] for t in before}
        assert s.version(row['version_id'])['state']=='PENDING'
    finally:s.close()

def test_new_distribution_has_empty_library(monkeypatch,tmp_path):
    import covex_label_manager.storage as storage
    from covex_label_manager.storage import Store
    empty=tmp_path/'empty-resources';empty.mkdir()
    monkeypatch.setattr(storage,'resource_dir',lambda:empty)
    s=Store(tmp_path/'new-data')
    try:
        assert s.labels()==[] and s.materials()==[] and s.status_masters()==[]
    finally:s.close()

def test_legacy_r1_can_be_derived_only_from_intact_local_source(monkeypatch,tmp_path):
    import covex_label_manager.storage as storage
    from covex_label_manager.storage import Store
    s=Store(tmp_path/'data',seed=False);s.seed_data()
    original=next(r for r in s.labels() if r['name']=='EDROFONIO')
    assert len(s.versions(original['id']))==1
    s.close()
    empty=tmp_path/'empty-resources';empty.mkdir()
    monkeypatch.setattr(storage,'resource_dir',lambda:empty)
    s=Store(tmp_path/'data')
    try:
        r1=next(v for v in s.versions(original['id']) if v['version']=='00-R1')
        assert r1['state']=='PENDING'
    finally:s.close()
