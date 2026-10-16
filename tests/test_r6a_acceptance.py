"""Synthetic R6A tests: never use real labels."""
import json,hashlib,zipfile
import pytest
from covex_label_manager.qt_ui.demo import DemoSession
@pytest.fixture
def api():
    s=DemoSession()
    yield s.services
    s.close()
def test_no_approval_even_when_integrity_passes(api):
    before=[(v['id'],v['state']) for l in api.labels() for v in api.versions(l['id'])]
    r=api.acceptance_preflight()
    assert r['acceptance']=='NOT_ACCEPTED' and r['summary']['pass']>0
    assert r['summary']['manual_open']==14
    assert all(x['result']=='NOT_EXECUTED' for x in r['manual'])
    assert before==[(v['id'],v['state']) for l in api.labels() for v in api.versions(l['id'])]
def test_corrupt_master_blocks_stale_export(api,tmp_path):
    report=api.acceptance_preflight();v=api.version(api.initial_id) if hasattr(api,'initial_id') else api.version(api.versions(api.labels()[0]['id'])[0]['id'])
    api.asset_path(v['master_pdf']).write_bytes(b'corrupted synthetic PDF')
    after=api.acceptance_preflight()
    assert any(c['code']=='MASTER_SHA256' and c['status']=='FAIL' and c['subject']=='revision:'+str(v['id']) for c in after['checks'])
    with pytest.raises(ValueError,match='cambió'):api.acceptance_export(report,tmp_path/'test.zip')
def test_export_integrity_and_never_overwrite(api,tmp_path):
    report=api.acceptance_preflight();p=tmp_path/'report.zip'
    output=api.acceptance_export(report,p)
    assert output['acceptance']=='NOT_ACCEPTED'
    with zipfile.ZipFile(p) as z:
        manifest=json.loads(z.read('integrity-manifest.json'))
        assert manifest['type']=='R6A_TEMPLATE_NOT_GMP_ACCEPTANCE'
        assert all(hashlib.sha256(z.read(k)).hexdigest()==v for k,v in manifest['files'].items())
        assert b'NOT_EXECUTED' in z.read('protocolo_aceptacion.csv')
    with pytest.raises(FileExistsError):api.acceptance_export(report,p)
    with pytest.raises(PermissionError):api.acceptance_export(report,api._repository.root/'wrong.zip')
