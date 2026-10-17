"""Isolated preview protocol rejects output outside cache without touching it."""
import json
from pathlib import Path
import pytest
from covex_label_manager.preview_render import run_job


@pytest.mark.parametrize('target',['sources','emissions','cache/../sources'])
def test_worker_refuses_non_cache_output_before_opening_catalog(tmp_path,target):
    cache=tmp_path/'cache';cache.mkdir();folder=tmp_path/target;folder.mkdir(parents=True,exist_ok=True)
    output=folder/('qt-auto-proof-'+'a'*32+'.pdf');output.write_bytes(b'SYNTHETIC untouched')
    job=cache/'request.json'
    job.write_text(json.dumps(dict(contract=1,root=str(tmp_path),path=str(output),
        uid='b'*32,generation=1,serial=0,token='c'*64)),encoding='utf-8')
    with pytest.raises(ValueError,match='Contrato'):run_job(job)
    assert output.read_bytes()==b'SYNTHETIC untouched'
    assert not list(tmp_path.glob('*.sqlite*'))
