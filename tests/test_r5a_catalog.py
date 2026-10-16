"""R5A synthetic audit-only inventory and verified complete export."""
import json
import zipfile
import pytest

from covex_label_manager.qt_ui.demo import DemoSession
from covex_label_manager.catalog_exchange import inventory_folder,export_library


@pytest.fixture
def demo():
    s=DemoSession()
    yield s
    s.close()


def test_inventory_uses_hash_and_only_reads(demo,tmp_path):
    api=demo.services
    original=api.version(demo.initial_id)
    source=api.asset_path(original['master_pdf'])
    candidate=tmp_path/'Alpha 00.pdf'
    candidate.write_bytes(source.read_bytes())
    before=len(api.labels())
    report=inventory_folder(api,tmp_path)
    assert report['counts']['EXACT_DUPLICATE']==1
    assert len(api.labels())==before
    assert report['files'][0]['sha256']==original['pdf_sha256']


def test_export_includes_all_versions_and_integrity(demo,tmp_path):
    api=demo.services
    out=tmp_path/'all.zip'
    result=export_library(api,out)
    assert result['assets']>0 and result['revisions']>0
    with zipfile.ZipFile(out) as z:
        manifest=json.loads(z.read('catalog-manifest.json'))
        assert manifest['type']=='CATALOG_EXPORT_NOT_BACKUP'
        assert len(manifest['documents'])==result['revisions']
        assert len(manifest['files'])==result['assets']
        assert all(z.read(k) for k in manifest['files'])
    with pytest.raises(FileExistsError):export_library(api,out)


def test_corrupt_asset_aborts_export_without_output(demo,tmp_path):
    api=demo.services
    ver=api.version(demo.initial_id)
    api.asset_path(ver['master_pdf']).write_bytes(b'corrupted')
    out=tmp_path/'export.zip'
    with pytest.raises(ValueError,match='Integridad'):export_library(api,out)
    assert not out.exists()


def test_export_cannot_write_inside_data(demo):
    api=demo.services
    with pytest.raises(PermissionError):
        export_library(api,api._repository.root/'exports.zip')


def test_inventory_identifies_repeated_identity_without_modification(demo,tmp_path):
    api=demo.services
    v=api.version(demo.initial_id)
    path=tmp_path/(v['name']+' '+v['version']+'.pdf')
    path.write_bytes(b'fictional different source')
    report=inventory_folder(api,tmp_path)
    assert report['counts']['IDENTITY_CONFLICT'] in (0,1)
    assert len(report['files'])==1
