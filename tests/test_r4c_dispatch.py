"""R4C printer preflight, without touching a physical driver."""
import hashlib
import json
from types import SimpleNamespace

import fitz
import pytest

from covex_label_manager.print_dispatch import (
    prepare_registered,validate_device,raster_size
)


def synthetic(tmp_path,paper=(210,297),bad_size=False):
    path=tmp_path/'fictional-label.pdf'
    with fitz.open() as pdf:
        pdf.new_page(width=(190 if bad_size else paper[0])*72/25.4,
                     height=paper[1]*72/25.4)
        pdf.save(path)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    row={'id':2,'pdf_sha256':digest,'profile_json':json.dumps(
        {'paper':'A4','orientation':'portrait','start_slot':1,'margin_mm':8})}
    report={'issue':row,'path':path,'snapshot':{'verified':'fixture'},
            'token':'fictional-token','blocked':None}
    return SimpleNamespace(history=SimpleNamespace(inspect=lambda number:report)),report


def test_preflight_from_registered_snapshot_is_read_only(tmp_path):
    api,report=synthetic(tmp_path)
    before=report['path'].read_bytes()
    plan=prepare_registered(api,2)
    assert plan['issue_id']==2 and plan['pages']==1 and plan['paper_mm']==(210,297)
    assert plan['pdf_bytes']==before and report['path'].read_bytes()==before
    assert not plan['partially_used_first_page']


def test_used_sheet_requires_explicit_operator_check(tmp_path):
    api,report=synthetic(tmp_path)
    profile=json.loads(report['issue']['profile_json'])
    profile.update(start_slot=2,occupied_slots=[3])
    report['issue']['profile_json']=json.dumps(profile)
    assert prepare_registered(api,2)['partially_used_first_page']


@pytest.mark.parametrize('modification',['tamper','missing_hash','blocked','no_snapshot','paper_mismatch'])
def test_unverifiable_documents_are_never_dispatched(tmp_path,modification):
    api,report=synthetic(tmp_path)
    if modification=='tamper':report['path'].write_bytes(b'changed')
    elif modification=='missing_hash':report['issue']['pdf_sha256']=''
    elif modification=='blocked':report['blocked']='Revisión retirada'
    elif modification=='no_snapshot':report['snapshot']=None
    else:
        profile=json.loads(report['issue']['profile_json'])
        profile['paper']='A3'
        report['issue']['profile_json']=json.dumps(profile)
    with pytest.raises((ValueError,PermissionError)):
        prepare_registered(api,2)


def test_printer_name_and_physical_paper_are_checked(tmp_path):
    api,_=synthetic(tmp_path)
    plan=prepare_registered(api,2)
    assert validate_device(plan,'Fictional Queue',(210,297))
    for name,paper,native in [('',(210,297),True),
                              ('Queue',(148,210),True),
                              ('Queue',(210,297),False)]:
        with pytest.raises(ValueError):
            validate_device(plan,name,paper,native)
    plan['profile']['printer_calibration']={'contract':1}
    plan['printer_reference']='Synthetic Exact Queue'
    with pytest.raises(ValueError,match='otra impresora'):
        validate_device(plan,'Other Queue',(210,297))
    assert validate_device(plan,'Synthetic Exact Queue',(210,297))


def test_raster_memory_and_resolution_guard():
    assert raster_size((210,297),300)==(2481,3508)
    with pytest.raises(ValueError):raster_size((1000,1000),1200)
    with pytest.raises(ValueError):raster_size((210,297),71)
