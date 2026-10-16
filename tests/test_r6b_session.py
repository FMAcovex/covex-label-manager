import pytest,zipfile
from covex_label_manager.qt_ui.demo import DemoSession
from covex_label_manager.uat_session import load_r6a,create,read,update,verify_evidence
@pytest.fixture
def case(tmp_path):
    session=DemoSession();api=session.services
    pack=tmp_path/'r6a.zip';api.acceptance_export(api.acceptance_preflight(),pack)
    meta={'machine':'FICTIONAL-PC','windows':'Windows 11','tester':'Demo','commit':'a'*40,'portable_sha256':'b'*64}
    yield api,pack,meta,tmp_path
    session.close()
def test_verified_origin_and_pending_by_default(case):
    api,pack,meta,tmp=case
    report=create(api,pack,tmp/'uat.json',meta)
    assert report['acceptance']=='NOT_ACCEPTED'
    assert len(report['cases'])==14 and all(r['status']=='NOT_EXECUTED' for r in report['cases'])
    assert len(load_r6a(pack)['sha256'])==64
def test_evidence_and_generations(case):
    api,pack,meta,tmp=case;path=tmp/'uat.json';create(api,pack,path,meta)
    with pytest.raises(ValueError,match='evidencia'):update(api,path,1,'UAT-01','PASS','Demo','2026-10-01')
    receipt=tmp/'demo.txt';receipt.write_text('synthetic')
    next_path=update(api,path,1,'UAT-01','PASS','Demo','2026-10-01',evidence=receipt)
    report=read(next_path)
    assert report['cases'][0]['status']=='PASS' and report['acceptance']=='NOT_ACCEPTED'
    assert not verify_evidence(report)
    assert read(path)['cases'][0]['status']=='NOT_EXECUTED'
    receipt.write_text('tampered');assert verify_evidence(report)==['UAT-01']
    with pytest.raises(ValueError,match='obsoleta'):update(api,path,2,'UAT-02','FAIL','Demo','2026-10-01','reason')
def test_origin_tamper_and_no_overwrite(case):
    api,pack,meta,tmp=case
    with zipfile.ZipFile(pack,'a') as z:z.writestr('bad.txt','untrusted')
    with pytest.raises(ValueError,match='desconocido'):create(api,pack,tmp/'uat.json',meta)
