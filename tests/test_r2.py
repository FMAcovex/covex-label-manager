import json
import sqlite3
import zipfile
from covex_label_manager.storage import Store
from covex_label_manager.services import LocalServices


def test_combined_search_filters_metadata_and_document_state(tmp_path):
    s=Store(tmp_path/'data');api=LocalServices(s)
    try:
        row=next(r for r in api.library.entries() if r['name']=='EDROFONIO' and r['version']=='00-R1')
        api.library.update_metadata(row['id'],{'country':'España','language':'ES','family':'Ejemplo de prueba'},'Fuente de prueba, no catálogo real')
        matches=api.library.entries('edrofonio espana',{'state':'PENDING','country':'España','version':'00-R1'})
        assert len(matches)==1 and matches[0]['version_id']==row['version_id']
        assert not api.library.entries('edrofonio',{'state':'APPROVED'})
        api.approve(row['version_id'],'Operador de prueba','Referencia documental de prueba')
        assert api.library.entries('edrofonio',{'state':'APPROVED'})[0]['name']=='EDROFONIO'
        assert not api.library.entries('edrofonio',{'country':'Portugal'})
        assert api.library.facets()['country']==['España']
        assert api.library.facets()['type']==[]
    finally:api.close()


def test_favorites_recent_specific_revision_and_uids_survive_restart(tmp_path):
    s=Store(tmp_path/'data');api=LocalServices(s)
    row=next(r for r in api.library.entries() if r['version']=='00-R1')
    api.library.favorite(row);api.library.opened(row);api.close()
    api=LocalServices(Store(tmp_path/'data'))
    try:
        assert len(api.library.entries(view='favorites'))==2 # two revisions, one label
        recent=api.library.entries(view='recent');assert len(recent)==1
        assert recent[0]['version_uid']==row['version_uid']
        assert recent[0]['label_uid']==row['label_uid']
        assert recent[0]['version_id']==row['version_id']
        assert all(r.get('country','')=='' for r in api.library.entries())
    finally:api.close()


def test_services_hide_sqlite_and_backup_retains_catalog(tmp_path):
    api=LocalServices(Store(tmp_path/'data'))
    try:
        import pytest
        with pytest.raises(AttributeError):api.db
        with pytest.raises(AttributeError):api.root
        row=api.library.entries()[0];api.library.favorite(row)
        path=api.backup()
        with zipfile.ZipFile(path) as z:
            assert 'storage_v4/labels.sqlite' in z.namelist();z.extract('storage_v4/labels.sqlite',tmp_path/'restored')
        with sqlite3.connect(tmp_path/'restored'/'storage_v4'/'labels.sqlite') as db:
            assert db.execute('SELECT COUNT(*) FROM library_preferences WHERE favorite=1').fetchone()[0]==1
            assert db.execute('SELECT COUNT(DISTINCT uid) FROM labels').fetchone()[0]==2
    finally:api.close()


def test_metadata_requires_source_and_does_not_change_approved_design(tmp_path):
    import pytest
    api=LocalServices(Store(tmp_path/'data'))
    try:
        row=api.library.entries()[0];api.approve(row['version_id'],'Operador de prueba','Referencia de prueba externa')
        before=dict(api.version(row['version_id']))
        with pytest.raises(ValueError,match='fuente'):api.library.update_metadata(row['id'],{'language':'ES'},'')
        api.library.update_metadata(row['id'],{'language':'ES'},'Referencia documental real requerida en uso')
        after=dict(api.version(row['version_id']))
        assert before==after
    finally:api.close()


def test_upgrade_from_legacy_schema_preserves_custom_fields_and_profile(tmp_path):
    import pytest
    from v3_fixture import create
    root=tmp_path/'legacy';s=create(root,seed=False);s.seed_data()
    label=next(r for r in s.labels() if r['name']=='EDROFONIO');v=s.version(label['version_id'])
    custom=json.loads(v['fields_json']);custom[0]['font_pt']=21
    s.replace_pending_fields(v['id'],custom)
    s.set_setting('operator','Operador anterior')
    s.close()
    with sqlite3.connect(root/'labels.sqlite') as db:
        for table in ('labels','versions','materials','issues'):
            db.execute(f'DROP TRIGGER {table}_assign_uid')
            db.execute(f'DROP INDEX {table}_uid')
            db.execute(f'ALTER TABLE {table} DROP COLUMN uid')
        db.execute('ALTER TABLE profiles DROP COLUMN safety_mm')
        db.execute('DROP TABLE label_metadata');db.execute('DROP TABLE library_preferences')
    s=Store(root)
    try:
        assert s.setting('operator')=='Operador anterior'
        assert json.loads(s.version(v['id'])['fields_json'])==custom
        assert len(s.profile_list())==2
        assert s.version(v['id'])['uid']
        backups=list((root/'backups').glob('v4-*/legacy-snapshot.sqlite'));assert len(backups)==1
        with sqlite3.connect(backups[0]) as db:
            assert 'uid' not in {r[1] for r in db.execute('PRAGMA table_info(labels)')}
            assert db.execute("SELECT value FROM settings WHERE key='operator'").fetchone()[0]=='Operador anterior'
    finally:s.close()

