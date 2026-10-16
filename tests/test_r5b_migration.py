"""R5B synthetic reconciliation without real documents."""
import hashlib
import fitz
import pytest
from covex_label_manager.qt_ui.demo import DemoSession

@pytest.fixture
def demo():
    session=DemoSession();yield session.services;session.close()

def create(path,name='Fictitious'):
    with fitz.open() as pdf:
        p=pdf.new_page();p.insert_text((30,30),name);pdf.save(path)
    return path

def intent(**override):
    return {'action':'NEW_LABEL','name':'Synthetic R5B','version':'00','origin':'COVEX','customer':'','code':'R5B-TEST','category':'Demo','annex':'','ref_customer':'',**override}

def test_controlled_pending_add_and_rerun_rejected(demo,tmp_path):
    create(tmp_path/'Fictitious 00.pdf')
    row=demo.catalog_migration_preview(tmp_path)['files'][0]
    assert row['status']=='REVIEW_REQUIRED'
    previous=len(demo.labels());result=demo.catalog_migration_apply(tmp_path,row,intent())
    assert result['state']=='PENDING' and len(demo.labels())==previous+1
    with pytest.raises(ValueError,match='registrado'):demo.catalog_migration_apply(tmp_path,row,intent(name='Different'))

def test_pair_preserves_word_original_and_pdf(demo,tmp_path):
    (tmp_path/'Label 00.docx').write_bytes(b'SYNTHETIC WORD PLACEHOLDER')
    create(tmp_path/'Label 00.pdf')
    row=demo.catalog_migration_preview(tmp_path)['files'][0]
    assert row['source'].endswith('.docx') and row['pdf']
    out=demo.catalog_migration_apply(tmp_path,row,intent())
    revision=demo.version(out['version_id'])
    assert demo.asset_path(revision['original_file']).read_bytes()==b'SYNTHETIC WORD PLACEHOLDER'

def test_new_revision_existing_target_and_no_state_change(demo,tmp_path):
    label=demo.labels()[0];original={v['id']:v['state'] for v in demo.versions(label['id'])}
    create(tmp_path/'Different 55.pdf');row=demo.catalog_migration_preview(tmp_path)['files'][0]
    with pytest.raises(ValueError,match='destino'):demo.catalog_migration_apply(tmp_path,row,intent(action='NEW_REVISION'))
    result=demo.catalog_migration_apply(tmp_path,row,intent(action='NEW_REVISION',target_label_id=label['id'],version='55'))
    assert result['state']=='PENDING'
    assert all(demo.version(i)['state']==state for i,state in original.items())

def test_changed_file_and_path_escape_blocked(demo,tmp_path):
    f=create(tmp_path/'Original 00.pdf');row=demo.catalog_migration_preview(tmp_path)['files'][0]
    create(f,'Modified')
    with pytest.raises(ValueError,match='modificada'):demo.catalog_migration_apply(tmp_path,row,intent())
    with pytest.raises(ValueError,match='Ruta'):demo.catalog_migration_apply(tmp_path,{**row,'source':'../escape.pdf'},intent())

def test_intra_batch_same_hash_flagged(demo,tmp_path):
    first=create(tmp_path/'One 00.pdf')
    (tmp_path/'Two 00.pdf').write_bytes(first.read_bytes())
    rows=demo.catalog_migration_preview(tmp_path)['files']
    assert len(rows)==2 and any(r['status']=='BATCH_DUPLICATE' for r in rows)

def test_known_hash_and_existing_name_blocked(demo,tmp_path):
    label=demo.labels()[0];existing=demo.version(label['version_id'])
    (tmp_path/'Clone 00.pdf').write_bytes(demo.asset_path(existing['master_pdf']).read_bytes())
    row=demo.catalog_migration_preview(tmp_path)['files'][0]
    assert row['status'] in ('HASH_CONFLICT','EXACT_DUPLICATE')
    with pytest.raises(ValueError,match='bloqueado'):demo.catalog_migration_apply(tmp_path,row,intent())
