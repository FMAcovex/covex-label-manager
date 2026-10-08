import json
import fitz
import pytest
from covex_label_manager.engine import render_emission, LayoutError
from covex_label_manager.storage import Store,sha256
from test_v02 import profile,data


def test_r1_number_inside_true_outer_frame_and_sources_preserved(tmp_path):
    s=Store(tmp_path/'data')
    try:
        row=next(r for r in s.labels() if r['name']=='EDROFONIO');vs=s.versions(row['id'])
        original=s.version(next(v['id'] for v in vs if v['version']=='00'))
        v=s.version(row['version_id']);assert v['version']=='00-R1' and v['state']=='PENDING'
        assert v['base_w_mm']==pytest.approx(137.44,.001)
        assert v['base_h_mm']==pytest.approx(167.99,.001)
        before=sha256(s.root/original['master_pdf']);p=profile(w=v['base_w_mm'],h=v['base_h_mm'])
        path=tmp_path/'r1.pdf';render_emission(v,s.root,data(),p,[1,2],2,1,path,True)
        with fitz.open(path) as doc:
            nums=[fitz.Rect(span['bbox']) for page in doc for b in page.get_text('dict')['blocks'] for line in b.get('lines',[]) for span in line['spans'] if span['text'] in ('1/2','2/2')]
            assert len(nums)==2
            assert all(box.x1<(8+v['base_w_mm']-1)*72/25.4 for box in nums)
        assert sha256(s.root/original['master_pdf'])==before
        custom=json.loads(original['fields_json']);custom[0]['font_pt']=20
        s.replace_pending_fields(original['id'],custom);s.close();s=Store(tmp_path/'data')
        assert json.loads(s.version(original['id'])['fields_json'])[0]['font_pt']==20
        assert len(s.versions(row['id']))==2
    finally:s.close()


def test_safety_and_actual_ascender_block_generation(tmp_path):
    s=Store(tmp_path/'data')
    try:
        v=dict(s.version(next(r['version_id'] for r in s.labels() if r['name']=='ACETONA')))
        v['fields_json']=json.dumps([{'key':'numero','label':'Número','x':.1,'y':.001,'w':.2,'h':.01,'font_pt':14,'draw':'baseline'}])
        target=tmp_path/'no.pdf'
        with pytest.raises(LayoutError,match='límites'):render_emission(v,s.root,{},profile(),[1],1,1,target,True)
        assert not target.exists()
        v['fields_json']=json.dumps([{'key':'numero','label':'Número','x':.001,'y':.1,'w':.2,'h':.1,'font_pt':14,'draw':'baseline'}])
        with pytest.raises(LayoutError,match='seguridad'):render_emission(v,s.root,{},dict(profile(),safety_mm=2),[1],1,1,target,True)
    finally:s.close()


def test_safety_profile_persisted(tmp_path):
    s=Store(tmp_path/'data')
    try:
        p=dict(s.profile_list()[0]);p['safety_mm']=1.2;s.add_profile(p)
        assert next(x for x in s.profile_list() if x['name']==p['name'])['safety_mm']==1.2
    finally:s.close()
