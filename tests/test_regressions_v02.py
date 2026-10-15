from contextlib import closing
import json
import sqlite3
import fitz
import pytest
from test_v02 import store, ver, data, profile, approved
from covex_label_manager.engine import render_emission, LayoutError
from covex_label_manager.geometry import rebase_layout
from covex_label_manager.vessels import parse_tabular_vessels


def test_lot_prefix_checked_without_state(store,tmp_path):
    with pytest.raises(LayoutError,match='prefijo diferente'):
        render_emission(ver(store,'EDROFONIO'),store.root,{**data(),'lote':'CV/VP/2610'},profile(),[1],1,1,tmp_path/'bad.pdf',True)


@pytest.mark.parametrize('date',['31/02/2026','1/10/2026','2026-10-08'])
def test_status_date_rejects_invalid(store,tmp_path,date):
    with pytest.raises(LayoutError,match='Fecha de estado'):
        render_emission(ver(store,'EDROFONIO'),store.root,data(),profile(),[1],1,1,tmp_path/'bad.pdf',True,status={**approved(),'fecha':date},status_master=store.status_master('aprobado'))


def test_paste_rejects_duplicate_vessels():
    with pytest.raises(ValueError,match='repetido'):
        parse_tabular_vessels('1;ABC;0,2;0,3\n1;ABC;0,4;0,5',2)


def test_first_word_moves_below_caption(store,tmp_path):
    v=ver(store,'EDROFONIO');out=tmp_path/'wrap.pdf'
    render_emission(v,store.root,{**data(),'conservacion':'NITROGENO_SECO_ATMOSFERA'},profile(),[1],1,1,out,True)
    with fitz.open(out) as d:
        caption=d[0].search_for('Condiciones de conservación')[0]
        content=d[0].search_for('NITROGENO_SECO_ATMOSFERA')[0]
        assert content.y0>caption.y0+5
        assert content.x0<caption.x0+5


def test_long_conservation_blocks_overflow(store,tmp_path):
    with pytest.raises(LayoutError,match='demasiado largas'):
        render_emission(ver(store,'EDROFONIO'),store.root,{**data(),'conservacion':'Nitrógeno '*100},profile(),[1],1,1,tmp_path/'bad.pdf',True)


def test_crop_change_preserves_absolute_anchors(store):
    v=ver(store,'EDROFONIO');crop=json.loads(v['crop_json']);fields=json.loads(v['fields_json']);area=json.loads(v['status_area_json'])
    new=[crop[0]-5,crop[1]-5,crop[2]+5,crop[3]+5]
    result,zone=rebase_layout(fields,area,crop,new)
    for original,updated in zip(fields,result):
        for key,start,end in [('x',0,2),('y',1,3)]:
            assert new[start]+updated[key]*(new[end]-new[start])==pytest.approx(crop[start]+original[key]*(crop[end]-crop[start]))
    assert zone[2]*(new[2]-new[0])==pytest.approx(area[2]*(crop[2]-crop[0]))
    with pytest.raises(ValueError,match='excluye'):
        rebase_layout(fields,area,crop,[crop[0],crop[1],crop[2]-150,crop[3]])


def test_migration_backup_keeps_legacy_schema(tmp_path):
    from covex_label_manager.storage import Store
    from v3_fixture import create
    root=tmp_path/'old';s=create(root);s.set_setting('operator','Operador legado');s.close()
    with closing(sqlite3.connect(root/'labels.sqlite')) as c:
        c.execute('ALTER TABLE versions DROP COLUMN status_area_json');c.commit()
    s=Store(root)
    backups=list((root/'backups').glob('v4-*/legacy-snapshot.sqlite'))
    assert len(backups)==1
    with sqlite3.connect(backups[0]) as c:
        assert 'status_area_json' not in {r[1] for r in c.execute('PRAGMA table_info(versions)')}
        assert c.execute("SELECT value FROM settings WHERE key='operator'").fetchone()[0]=='Operador legado'
    assert s.setting('operator')=='Operador legado';s.close()

