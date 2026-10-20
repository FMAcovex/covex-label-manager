"""R8-RC3E: staged imports preserve R5B safeguards without a SQLite worker."""
import hashlib
import tempfile
import fitz
import pytest
from covex_label_manager.catalog_migration import prepare_source,commit_prepared
from covex_label_manager.qt_ui.demo import DemoSession


def test_staged_import_synthetic_pdf_is_pending(tmp_path):
    session=DemoSession()
    try:
        api=session.services
        source=tmp_path/'FAKE Label 00.pdf'
        with fitz.open() as doc:
            p=doc.new_page();p.insert_text((30,30),'DEMO')
            doc.save(source)
        row=api.catalog_migration_preview(tmp_path)['files'][0]
        intent=dict(action='NEW_LABEL',name='DEMO STATUS',version='00',
                    origin='COVEX',customer='',code='DEMO-ONLY',category='DEMO')
        with tempfile.TemporaryDirectory() as stage:
            prepared=prepare_source(tmp_path,row,stage)
            assert prepared['staged_pdf_sha256']==hashlib.sha256(
                open(prepared['pdf'],'rb').read()).hexdigest()
            record=commit_prepared(api,tmp_path,row,intent,prepared)
        assert record['state']=='PENDING'
        with tempfile.TemporaryDirectory() as stage:
            prepared=prepare_source(tmp_path,row,stage)
            with pytest.raises(ValueError,match='registrado'):
                commit_prepared(api,tmp_path,row,intent,prepared)
    finally:
        session.close()


def test_staging_detects_source_modification(tmp_path):
    src=tmp_path/'FICTICIA.pdf'
    src.write_bytes(b'fictional')
    row=dict(source=src.name,status='REVIEW_REQUIRED',sha256=hashlib.sha256(src.read_bytes()).hexdigest())
    src.write_bytes(b'modified')
    with tempfile.TemporaryDirectory() as stage:
        with pytest.raises(ValueError,match='modificada'):
            prepare_source(tmp_path,row,stage)
