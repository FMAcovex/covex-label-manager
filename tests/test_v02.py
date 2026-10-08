import json
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

import fitz
import pytest

from covex_label_manager.geometry import (
    STATUS_CROPS, acetona_template, edrofonio_template,
)
from covex_label_manager.engine import LayoutError, render_emission, normalized_lot
from covex_label_manager.storage import Store, sha256
from covex_label_manager.vessels import parse_tabular_vessels, validate_vessel_masses


def extracted_text(page):
    # Embedded Arial maps visually identical hyphens/spaces differently on Windows.
    return page.get_text().replace('\u00ad', '-').replace('\u00a0', ' ')


@pytest.fixture
def store(tmp_path):
    s=Store(tmp_path/'instance')
    yield s
    s.close()


def ver(store,name):
    return next(store.version(r['version_id']) for r in store.labels() if r['name']==name)


def profile(w=156,h=172):
    return {'width_mm':w,'height_mm':h,'orientation':'portrait','margin_mm':8,
            'gap_mm':3,'start_slot':1,'offset_x_mm':0,'offset_y_mm':0}


def data():
    return {'lote':'CV/EDR/TEST-001','pn':'0,1000','pb':'0,2000',
            'conservacion':'Envasar en atmosfera de nitrogeno'}


def approved():
    return {'kind':'aprobado','fecha':'27/10/2025','persona':'',
            'caducidad_reanalisis':'Noviembre-2025','placement':'integrada'}


def test_seed_uses_synthetic_documents_and_pending_statuses(store):
    assert store.stats()['labels']==2
    assert {v['kind'] for v in store.status_masters()}==set(STATUS_CROPS)
    assert all(v['state']=='PENDING' for v in store.status_masters())
    assert store.version(ver(store,'EDROFONIO')['id'])['state']=='PENDING'
    for kind in STATUS_CROPS:
        d=store.status_master(kind)
        assert sha256(store.root/d['master_pdf'])==d['pdf_sha256']
        assert sha256(store.root/d['original_file'])==d['source_sha256']
    assert len(json.loads(ver(store,'EDROFONIO')['status_area_json']))==4


def test_geometries_derive_from_word_positions(store):
    for product,build in [('ACETONA',acetona_template),('EDROFONIO',edrofonio_template)]:
        v=ver(store,product)
        if product=='EDROFONIO':v=store.version(next(v['id'] for v in store.versions(v['label_id']) if v['version']=='00'))
        f,area=build(store.root/v['master_pdf'],json.loads(v['crop_json']))
        assert f==json.loads(v['fields_json'])
        assert area==json.loads(v['status_area_json'])
        assert all(0<=x['x']<=1 and 0<=x['y']<=1 for x in f)
    v=ver(store,'EDROFONIO')
    assert any(f['draw']=='continuation' for f in json.loads(v['fields_json']))
    assert all(k in {f['key'] for f in json.loads(v['fields_json'])} for k in ('lote','pn','pb','numero'))


def test_integrated_colored_states_all_three(store,tmp_path):
    v=ver(store,'EDROFONIO')
    for kind in STATUS_CROPS:
        status=dict(approved(),kind=kind)
        path=tmp_path/(kind+'.pdf')
        result=render_emission(v,store.root,data(),profile(),[1],1,1,path,True,
                               status=status,status_master=store.status_master(kind))
        assert result['physical']==1
        d=fitz.open(path);t=extracted_text(d[0])
        assert 'DEMO B' in t
        assert {'aprobado':'Aprobado','rechazado':'Rechazado',
                'sin_analizar':'Sin analizar'}[kind] in t
        assert 'TEST-001' in t and 'CV/EDR/' in t
        assert '0,1000 KG' in t and '0,2000 KG' in t
        assert '1/1' in t
        assert 'PRUEBA - NO APTO' in t
        d.close()


def test_two_vessels_different_lots_and_weights_and_two_copies(store,tmp_path):
    v=ver(store,'EDROFONIO')
    individual={'2':{'lote':'CV/EDR/TEST-002','pn':'0,1500','pb':'0,2500'}}
    pdf=tmp_path/'vary.pdf'
    result=render_emission(v,store.root,data(),profile(),[1,2],2,2,pdf,True,
                           per_container=individual,status=approved(),
                           status_master=store.status_master('aprobado'))
    assert result['physical']==4 and result['pages']==4
    d=fitz.open(pdf)
    for number,lot,pn,pb in [(0,'TEST-001','0,1000','0,2000'),(2,'TEST-002','0,1500','0,2500')]:
        for page in (d[number],d[number+1]):
            text=extracted_text(page)
            assert lot in text and pn in text and pb in text
            assert f'{number//2+1}/2' in text
        assert d[number].get_text()==d[number+1].get_text()
    d.close()


def test_status_only_in_a4_and_original_status_source_preserved(store,tmp_path):
    v=ver(store,'EDROFONIO')
    doc=tmp_path/'status.pdf'
    src=store.root/store.status_master('aprobado')['original_file']
    before=sha256(src)
    result=render_emission(v,store.root,data(),profile(153,30),[1,2],2,1,doc,True,
                           status={**approved(),'placement':'independiente'},
                           status_master=store.status_master('aprobado'))
    assert result['pages']==1 and result['per_page']>=2
    text=extracted_text(fitz.open(doc)[0])
    assert 'Aprobado' in text and 'EDROFONIO' not in text
    assert 'Noviembre-2025' in text
    assert sha256(src)==before


def test_approval_required_for_original_and_status(store,tmp_path):
    v=ver(store,'EDROFONIO')
    with pytest.raises(LayoutError,match='pendiente de aprobación'):
        render_emission(v,store.root,data(),profile(),[1],1,1,tmp_path/'bad.pdf',False)
    store.approve(v['id'],'Garantía Calidad','Aprobación externa documental - ejemplo de prueba')
    v=store.version(v['id'])
    with pytest.raises(LayoutError,match='pendiente de comprobación'):
        render_emission(v,store.root,data(),profile(),[1],1,1,tmp_path/'bad2.pdf',False,
                        status=approved(),status_master=store.status_master('aprobado'))
    store.approve_status_master('aprobado','Garantía Calidad','TEST-STATE-APPROVAL - synthetic reference')
    path=store.root/'emissions'/'ok.pdf'
    r=render_emission(v,store.root,data(),profile(),[1],1,1,path,False,
                       status=approved(),status_master=store.status_master('aprobado'))
    assert not r['warnings']
    assert 'PRUEBA' not in fitz.open(path)[0].get_text()
    i=store.add_issue(v['id'],'Operador',1,1,[1],data(),profile(),path,status=approved(),
                      per_container={'1':{'pn':'0,1000'}})
    assert json.loads(store.issue(i)['status_json'])['kind']=='aprobado'
    assert json.loads(store.issue(i)['per_container_json'])['1']['pn']=='0,1000'


def test_status_asset_integrity_and_empty_status_region(store,tmp_path):
    v=ver(store,'EDROFONIO')
    status=store.status_master('aprobado')
    original_status_bytes=(store.root/status['master_pdf']).read_bytes()
    (store.root/status['master_pdf']).write_bytes(original_status_bytes+b'\nTAMPERED')
    with pytest.raises(LayoutError,match='Integridad comprometida'):
        render_emission(v,store.root,data(),profile(),[1],1,1,tmp_path/'bad.pdf',True,
                        status=approved(),status_master=status)
    (store.root/status['master_pdf']).write_bytes(original_status_bytes)
    other=dict(ver(store,'ACETONA'));other['status_area_json']='[]'
    with pytest.raises(LayoutError,match='no tiene zona'):
        render_emission(other,store.root,{'lote':'2610','cantidad':'10'},profile(),[1],1,1,tmp_path/'bad3.pdf',True,
                        status=approved(),status_master=status)


def test_mass_validation_with_european_commas(store,tmp_path):
    assert normalized_lot('TEST-001','CV/EDR/')=='CV/EDR/TEST-001'
    assert normalized_lot('CV/EDR/TEST-001','CV/EDR/')=='CV/EDR/TEST-001'
    with pytest.raises(LayoutError):normalized_lot('CV/VP/123','CV/EDR/')
    assert validate_vessel_masses({'pn':'0,1000','pb':'0,2000'},1) is None
    with pytest.raises(ValueError,match='menor'):
        validate_vessel_masses({'pn':'0,900','pb':'0,800'},2)
    v=ver(store,'EDROFONIO')
    with pytest.raises(LayoutError,match='menor'):
        render_emission(v,store.root,data(),profile(),[1,2],2,1,tmp_path/'bad.pdf',True,
                        per_container={'2':{'pn':'0,900','pb':'0,800'}})


def test_paste_excel_tsv_and_semicolon_csv():
    table='Nº\tLote\tPN\tPB\tConservación\n1\tCV/EDR/TEST-001\t0,1000\t0,2000\tNitrógeno\n2\tCV/EDR/TEST-002\t0,1500\t0,2500\tNitrógeno'
    rows=parse_tabular_vessels(table,2)
    assert rows['1']['pn']=='0,1000' and rows['2']['pb']=='0,2500'
    assert parse_tabular_vessels('Número;Lote;PN;PB\n1;ABC;0,20;0,30',2)['1']['lote']=='ABC'
    with pytest.raises(ValueError,match='entre 1 y 2'):
        parse_tabular_vessels('3\tABC\t0,20\t0,30',2)


def test_old_database_adds_columns_and_preserves_fields(tmp_path):
    root=tmp_path/'legacy'
    s=Store(root);v=ver(s,'ACETONA')
    s.set_setting('operator','Operador anterior')
    vid=v['id'];oldfields=v['fields_json']
    s.close()
    sql=sqlite3.connect(root/'labels.sqlite')
    # Model v0.1 columns absent. Preserve underlying original labels and user settings.
    for table,col in [('versions','status_area_json'),('issues','per_container_json'),('issues','status_json')]:
        sql.execute(f'ALTER TABLE {table} DROP COLUMN {col}')
    sql.commit();sql.close()
    updated=Store(root)
    assert updated.setting('operator')=='Operador anterior'
    assert updated.version(vid)['fields_json']==oldfields
    assert updated.stats()['labels']==2
    assert 'status_area_json' in updated.version(vid).keys()
    updated.close()


def test_reprint_retains_per_vessel_and_status_exactly(store,tmp_path):
    v=ver(store,'EDROFONIO')
    store.approve(v['id'],'Garantía Calidad','Aprobación externa documental - ejemplo de prueba')
    store.approve_status_master('aprobado','Garantía Calidad','Referencia documental externa de prueba')
    v=store.version(v['id'])
    overrides={'2':{'pn':'0,1500','pb':'0,2500','lote':'CV/EDR/TEST-002'}}
    st=approved();source=store.root/'emissions'/'emitted.pdf'
    render_emission(v,store.root,data(),profile(),[1,2],2,1,source,False,
                    per_container=overrides,status=st,status_master=store.status_master('aprobado'))
    key=store.add_issue(v['id'],'Operador',2,1,[1,2],data(),profile(),source,per_container=overrides,status=st)
    i=store.issue(key)
    reprint=store.root/'emissions'/'reprinted.pdf'
    render_emission(v,store.root,json.loads(i['variables_json']),json.loads(i['profile_json']),[2],2,1,
                    reprint,False,per_container=json.loads(i['per_container_json']),status=json.loads(i['status_json']),
                    status_master=store.status_master('aprobado'))
    text=extracted_text(fitz.open(reprint)[0])
    assert '2/2' in text and '0,1500 KG' in text and '0,2500 KG' in text
    assert 'TEST-002' in text and 'TEST-001' not in text
