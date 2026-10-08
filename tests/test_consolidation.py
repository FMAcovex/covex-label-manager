"""Approval and update regression scenarios, using disposable local data."""
import json
import pytest
from covex_label_manager.storage import Store
from covex_label_manager.services import LocalServices
from covex_label_manager.engine import LayoutError, render_emission
from test_v02 import data, profile

def label_version(store, name, revision=None):
    label=next(x for x in store.labels() if x['name']==name)
    if revision:
        return store.version(next(x['id'] for x in store.versions(label['id']) if x['version']==revision))
    return store.version(label['version_id'])

def test_defective_pdf_cannot_be_laundered_by_revision_or_name(tmp_path):
    s=Store(tmp_path/'data')
    try:
        original=label_version(s,'EDROFONIO','00')
        cloned=s.clone_version(original['id'],'01','Disposable regression copy')
        with pytest.raises(ValueError,match='desborda'):
            s.approve(cloned,'Test operator','Test documentary reference')
        assert s.version(cloned)['state']=='PENDING'
        renamed=dict(s.version(cloned),name='OTHER',code='OTHER')
        target=tmp_path/'blocked.pdf'
        with pytest.raises(LayoutError,match='desborda'):
            render_emission(renamed,s.root,data(),profile(),[1],1,1,target,True)
        assert not target.exists()
    finally:s.close()

def test_approval_and_clone_reject_tampered_master(tmp_path):
    s=Store(tmp_path/'data')
    try:
        v=label_version(s,'ACETONA');pdf=s.root/v['master_pdf']
        pdf.write_bytes(pdf.read_bytes()+b'\nmodified')
        with pytest.raises(ValueError,match='Integridad'):
            s.approve(v['id'],'Test operator','Test reference')
        with pytest.raises(ValueError,match='Integridad'):
            s.clone_version(v['id'],'01','Test copy')
        assert s.version(v['id'])['state']=='PENDING'
    finally:s.close()

def test_retired_ui_snapshot_cannot_emit(tmp_path):
    api=LocalServices(Store(tmp_path/'data'))
    try:
        v=label_version(api._repository,'ACETONA')
        api.approve(v['id'],'Test operator','Test reference')
        stale=dict(api.version(v['id']))
        new=api.clone_version(v['id'],'01','Test revision')
        api.approve(new,'Test operator','New test reference')
        with pytest.raises(LayoutError,match='aprobación'):
            api.render(stale,data(),profile(),[1],1,1,tmp_path/'blocked.pdf')
        assert not (tmp_path/'blocked.pdf').exists()
    finally:api.close()

def test_pending_r1_only_test_pdf_then_explicit_approval(tmp_path):
    api=LocalServices(Store(tmp_path/'data'))
    try:
        v=label_version(api._repository,'EDROFONIO','00-R1')
        p=profile(v['base_w_mm'],v['base_h_mm'])
        with pytest.raises(LayoutError,match='aprobación'):
            api.render(v,data(),p,[1],1,1,tmp_path/'blocked.pdf')
        api.render(v,data(),p,[1],1,1,tmp_path/'test.pdf',True)
        api.approve(v['id'],'Test operator','Disposable test approval, not COVEX approval')
        api.render(v,data(),p,[1],1,1,tmp_path/'approved.pdf')
        assert (tmp_path/'approved.pdf').exists()
    finally:api.close()

def test_reopen_preserves_all_controlled_data_and_single_r1(tmp_path):
    root=tmp_path/'data';s=Store(root)
    v=label_version(s,'EDROFONIO','00-R1')
    fields=json.loads(v['fields_json']);fields[0]['font_pt']=15
    s.replace_pending_fields(v['id'],fields)
    s.set_setting('operator','Test local operator')
    p=dict(s.profile_list()[0]);p['safety_mm']=.7;s.add_profile(p)
    s.set_favorite(v['label_id'],True)
    tables=('labels','versions','materials','profiles','settings','status_masters','library_preferences')
    snapshot={t:[tuple(r) for r in s.db.execute('SELECT * FROM '+t+' ORDER BY rowid')] for t in tables}
    s.close();s=Store(root)
    try:
        assert snapshot=={t:[tuple(r) for r in s.db.execute('SELECT * FROM '+t+' ORDER BY rowid')] for t in tables}
        assert len([r for r in s.versions(v['label_id']) if r['version']=='00-R1'])==1
    finally:s.close()
