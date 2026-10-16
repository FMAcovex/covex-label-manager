"""R5A migration inventory with synthetic files, no customer materials."""
import csv
import fitz
import pytest
from covex_label_manager.qt_ui.demo import DemoSession
from covex_label_manager.catalog_migration import inventory,guarded_import,export_inventory_csv


@pytest.fixture
def api():
    session=DemoSession()
    yield session.services
    session.close()


def fake(path,text='SYNTH'):
    with fitz.open() as doc:
        doc.new_page().insert_text((40,80),text)
        doc.save(path)
    return path


def test_new_is_read_only_then_imported_pending(api,tmp_path):
    before=len(api.library_records())
    p=fake(tmp_path/'Synthetic R5 New 00.pdf')
    entry=inventory(api,[p])[0]
    assert entry['status']=='NEW' and len(api.library_records())==before
    values={k:entry[k] for k in ('name','version','category')}
    v=api.version(guarded_import(api,entry,values))
    assert v['state']=='PENDING' and v['source_sha256']==entry['sha256']
    assert inventory(api,[p])[0]['status']=='DUPLICATE'


def test_batch_duplicate_and_version_ambiguity(api,tmp_path):
    a=fake(tmp_path/'Synthetic Unique 00.pdf','ALPHA')
    b=tmp_path/'Synthetic Identical 00.pdf';b.write_bytes(a.read_bytes())
    c=fake(tmp_path/'Synthetic Unique 01.pdf','BETA')
    assert [x['status'] for x in inventory(api,[a,b,c])]==['NEW','DUPLICATE','REVIEW']


def test_existing_label_and_client_folder_need_manual_review(api,tmp_path):
    old=fake(tmp_path/'Solución Alfa · Demo 00.pdf')
    client=fake(tmp_path/'CLIENTE Synthetic Delta 00.pdf')
    statuses=[e['status'] for e in inventory(api,[old,client])]
    assert statuses==['REVIEW','REVIEW']


def test_changed_or_missing_source_fails_closed(api,tmp_path):
    p=fake(tmp_path/'Synthetic Change 00.pdf','ALPHA')
    e=inventory(api,[p])[0]
    p.unlink();fake(p,'BETA')
    with pytest.raises(ValueError,match='cambió'):
        guarded_import(api,e,{k:e[k] for k in ('name','version','category')})
    missing=tmp_path/'Fictional Missing 00.pdf'
    assert inventory(api,[missing])[0]['status']=='ERROR'


def test_symlink_empty_and_multipage_review(api,tmp_path):
    empty=tmp_path/'Empty 00.pdf';empty.write_bytes(b'')
    assert inventory(api,[empty])[0]['status']=='ERROR'
    multi=tmp_path/'Multi Synthetic 00.pdf'
    with fitz.open() as doc:
        doc.new_page();doc.new_page();doc.save(multi)
    assert inventory(api,[multi])[0]['status']=='REVIEW'
    link=tmp_path/'Linked 00.pdf'
    try:link.symlink_to(multi)
    except (OSError,NotImplementedError):return
    assert inventory(api,[link])[0]['status']=='ERROR'


def test_export_csv_atomic_outside_protected_catalog(api,tmp_path):
    p=fake(tmp_path/'Synthetic Report 00.pdf')
    rows=inventory(api,[p])
    target=tmp_path/'report.csv'
    export_inventory_csv(rows,target,api.location())
    with target.open(encoding='utf-8-sig',newline='') as f:
        entries=list(csv.DictReader(f))
    assert entries[0]['sha256']==rows[0]['sha256']
    assert entries[0]['status']=='NEW'
    with pytest.raises(PermissionError):
        export_inventory_csv(rows,api._repository.root/'blocked.csv',api.location())
