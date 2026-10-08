import json
from pathlib import Path
import shutil
import fitz
import pytest

from covex_label_manager.storage import Store,sha256
from covex_label_manager.engine import plan_sheet,render_emission,render_calibration_page,validate_fields,LayoutError
from covex_label_manager.importer import auto_crop,docx_to_pdf,proposed_identity
from covex_label_manager.cm import parse_cm

ROOT=Path(__file__).resolve().parents[1]
RESOURCE=ROOT/'resources'


@pytest.fixture
def store(tmp_path):
    s=Store(tmp_path/'local')
    yield s
    s.close()


def vals():
    return {'lote':'TEST-A','cantidad':'25 kg','proveedor':'Proveedor A',
            'direccion':'Madrid','telefono':'900 000 000','observaciones':'Ensayo'}


def profile(w=165,h=242):
    return {'width_mm':w,'height_mm':h,'margin_mm':8,'gap_mm':3,'start_slot':1,
            'orientation':'portrait','offset_x_mm':0,'offset_y_mm':0,'crop_marks':0}


def test_seed_cm_materials(store):
    assert store.stats()['materials']==224
    assert store.stats()['labels']==2
    dup={x['code'] for x in store.material_duplicates()}
    assert 'DUP001' in dup
    assert 'DUP002' in dup


def test_paper_distribution_and_partial_sheets():
    a=plan_sheet(profile(80,50),50)
    assert a.capacity==10
    assert a.pages==5
    p=profile(80,50);p['start_slot']=3
    a=plan_sheet(p,17)
    assert a.pages==2
    with pytest.raises(LayoutError):plan_sheet({**p,'width_mm':210},2)
    with pytest.raises(LayoutError):plan_sheet({**p,'start_slot':99},1)


def test_synthetic_master_crop():
    crop,info=auto_crop(RESOURCE/'ACETONA_MASTER_00.pdf')
    assert crop[0]<68 and crop[1]<60
    assert crop[2]>527 and crop[3]>737
    assert info['page_count']==1


def test_original_is_immutable_and_test_watermark(store,tmp_path):
    v=store.version(store.labels()[0]['version_id'])
    source=store.root/v['master_pdf'];before=sha256(source)
    res=render_emission(v,store.root,vals(),profile(),[1,2,50],50,1,tmp_path/'demo.pdf',True)
    assert res['pages']==3
    doc=fitz.open(tmp_path/'demo.pdf')
    for page,index in zip(doc,[1,2,50]):
        assert f'{index}/50' in page.get_text()
        assert 'PRUEBA - NO APTO PARA USO GMP' in page.get_text()
        assert 'SYNTHETIC FIXTURE' in page.get_text()
    doc.close()
    assert sha256(source)==before


def test_approved_issuance_and_double_labels(store,tmp_path):
    v=store.version(store.labels()[0]['version_id'])
    with pytest.raises(LayoutError):
        render_emission(v,store.root,vals(),profile(),[1],1,1,tmp_path/'fail.pdf',False)
    with pytest.raises(ValueError):
        store.approve(v['id'],'AB','12')
    store.approve(v['id'],'Tecnico GC','TEST-APPROVAL-001 - synthetic reference')
    v=store.version(v['id'])
    emitted=store.root/'emissions'/'ok.pdf'
    res=render_emission(v,store.root,vals(),profile(),[1,2],2,2,emitted,False)
    assert res['pages']==4 and res['physical']==4
    d=fitz.open(emitted)
    assert '1/2' in d[0].get_text() and '1/2' in d[1].get_text()
    assert '2/2' in d[2].get_text() and '2/2' in d[3].get_text()
    assert 'PRUEBA - NO APTO' not in d[0].get_text()
    d.close()
    k=store.add_issue(v['id'],'Operador',2,2,[1,2],vals(),profile(),emitted)
    issue=store.issue(k)
    assert issue['pdf_sha256']==sha256(emitted)
    reprinted=store.root/'emissions'/'reprint.pdf'
    res2=render_emission(v,store.root,vals(),profile(),[2],2,2,reprinted,False)
    assert res2['physical']==2
    r=store.add_issue(v['id'],'Operador',2,2,[2],vals(),profile(),reprinted,source_issue_id=k,reason='Etiqueta danada')
    assert store.issue(r)['source_issue_id']==k
    assert '2/2' in fitz.open(reprinted)[0].get_text()
    assert store.version(v['id'])['state']=='APPROVED'
    with pytest.raises(PermissionError):
        store.replace_pending_fields(v['id'],[])
    new=store.clone_version(v['id'],'01','Cambio de posicion de los datos variables')
    assert store.version(new)['state']=='PENDING'
    assert store.version(v['id'])['state']=='APPROVED'


def test_source_integrity(store,tmp_path):
    v=store.version(store.labels()[0]['version_id'])
    source=store.root/v['master_pdf']
    with open(source,'ab') as f:f.write(b'\nexternal change')
    with pytest.raises(LayoutError,match='Integridad comprometida'):
        render_emission(v,store.root,vals(),profile(),[1],1,1,tmp_path/'tampered.pdf',True)


def test_approval_closed_customer_pdf(store,tmp_path):
    master=RESOURCE/'ACETONA_MASTER_00.pdf'
    box=fitz.open(master)[0].rect
    vid=store.add_label('Diseno externo','-', 'Cliente','', 'CLIENTE','Laboratorio A','C-01',master,None,
                [0,0,box.width,box.height],[], 'Etiqueta cerrada', 'REF-101')
    store.approve(vid,'Control calidad','Aprobacion documental CLIENTE-REF-101')
    v=store.version(vid)
    assert v['state']=='APPROVED'
    out=tmp_path/'customer.pdf'
    result=render_emission(v,store.root,{},profile(),[1,2,3],3,1,out,False)
    assert result['pages']==3


def test_validation_blocks_missing_and_small(store):
    v=store.version(store.labels()[0]['version_id'])
    with pytest.raises(LayoutError,match='Campo obligatorio'):
        validate_fields(v,{},profile())
    small=validate_fields(v,vals(),profile(80,50),strict=False)
    assert any('pequeno' in text for text in small)
    with pytest.raises(LayoutError):
        validate_fields(v,vals(),profile(80,50),strict=True)


@pytest.mark.skipif(__import__('os').environ.get('COVEX_TEST_WORD')!='1', reason='Word conversion requires explicit real environment test; not certified by CI')
def test_word_import_as_pdf_if_converter_exists(tmp_path):
    src=RESOURCE/'ACETONA_MASTER_00.docx'
    pdf=docx_to_pdf(src,tmp_path)
    assert pdf.exists()
    assert fitz.open(pdf).page_count==1


def test_import_name_parsing():
    i=proposed_identity('ACETONA VERSION 00.docx')
    assert i['name']=='Acetona' and i['version']=='00'
    i=proposed_identity('Cliente XYZ VERSION 12.pdf')
    assert i['version']=='12'


def test_persist_store_and_audit(tmp_path):
    root=tmp_path/'instance'
    s=Store(root)
    s.set_setting('operator','Personal LG')
    s.close()
    t=Store(root)
    assert t.setting('operator')=='Personal LG'
    assert t.stats()['labels']==2
    assert t.db.execute('SELECT COUNT(*) FROM audit').fetchone()[0]>=1
    t.close()


def test_calibration_sheet_marks(tmp_path):
    result=render_calibration_page(profile(80,50),tmp_path/'calibration.pdf')
    assert Path(result).exists()
    doc=fitz.open(result)
    assert len(doc)==1
    t=doc[0].get_text()
    assert 'POS. 1' in t and 'POS. 10' in t
    assert '50 mm' in t
    doc.close()
