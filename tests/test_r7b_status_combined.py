"""R7B combined emission contract: synthetic documents only.

No company masters or production databases enter these tests.
"""
import json

import fitz
import pytest

from covex_label_manager.storage import Store, sha256
from covex_label_manager.services import LocalServices
from covex_label_manager.status_catalog import StatusCatalogue
from covex_label_manager.status_design import make_layout
from covex_label_manager.status_combined import resolve_status, field_values


@pytest.fixture
def context(tmp_path):
    store = Store(tmp_path / "data")
    api = LocalServices(store)
    catalog = StatusCatalogue(store.root)
    document = tmp_path / "SYNTHETIC-COMBINED.pdf"
    with fitz.open() as pdf:
        page = pdf.new_page(width=600, height=820)
        for i, (name, color) in enumerate(
                (("SIN ANALIZAR", (1, .92, .3)),
                 ("APROBADO", (.25, .8, .4)),
                 ("RECHAZADO", (.9, .3, .3)))):
            y = 45 + i * 240
            page.draw_rect(fitz.Rect(55, y, 545, y+170), fill=color)
            page.insert_text((65, y+32), "FICTICIO " + name)
        pdf.save(document)
    entries = []
    for i, kind in enumerate(("sin_analizar", "aprobado", "rechazado")):
        y = 45 + i*240
        layout = make_layout(document, kind, crop=[55, y, 545, y+170])
        layout["fields"] = [
            {"key":"lote", "label":"Lote", "rect":[88, y+64, 310, y+88],
             "font_size":12.0, "bold":False, "required":kind!="rechazado"},
            {"key":"firma", "label":"Operador", "rect":[330, y+64, 515, y+88],
             "font_size":11.0, "bold":False, "required":True},
        ]
        entries.append({"kind":kind,"revision":"00","layout":layout})
    uids = catalog.import_many(document, entries)
    for uid in uids:
        catalog.submit(uid)
        catalog.approve(uid, "Calidad ficticia", "APROBACION-EXTERNA-FICTICIA",
                        confirmation=True)
    version = next(
        store.version(r["version_id"])
        for r in store.labels() if r["name"] == "EDROFONIO")
    profile = {"width_mm":156,"height_mm":172,"orientation":"portrait",
               "margin_mm":8,"gap_mm":3,"start_slot":1,
               "offset_x_mm":0,"offset_y_mm":0}
    values = {"lote":"LOTE-SINTETICO","pn":"0,1000","pb":"0,2000",
              "conservacion":"Ambiente seco"}
    yield store, api, catalog, version, profile, values, uids
    store.close()


@pytest.mark.parametrize("number", [0, 1, 2])
def test_combined_selected_r7a_revision_uses_exact_crop_and_fields(context, tmp_path, number):
    store, api, catalog, version, profile, values, uids = context
    kind = ("sin_analizar","aprobado","rechazado")[number]
    status = {"kind":kind,"placement":"integrada",
              "revision_uid":uids[number],
              "fields":{"firma":"OPERADOR SINTETICO"}}
    resolved = resolve_status(store,status)
    assert resolved["r7b_uid"] == uids[number]
    original_hash = sha256(store.root / resolved["master_pdf"])
    path = tmp_path / (kind + ".pdf")
    result = api.render(version, values, profile,[1],1,1,path,True,status=status)
    assert result["physical"] == 1
    with fitz.open(path) as pdf:
        words = pdf[0].get_text()
        assert "FICTICIO " + kind.upper().replace("_"," ") in words
        assert "OPERADOR SINTETICO" in words
        assert "LOTE-SINTETICO" in words
        assert "PRUEBA" in words
    assert sha256(store.root / resolved["master_pdf"]) == original_hash


def test_explicit_revision_cannot_silently_substitute_legacy_or_other_kind(context,tmp_path):
    store,api,catalog,v,p,values,uids=context
    for kind,uid in [("aprobado",uids[0]),("rechazado",uids[1])]:
        with pytest.raises(ValueError,match="pertenece a otro"):
            resolve_status(store,{"kind":kind,"revision_uid":uid})
    with pytest.raises(ValueError,match="inválida"):
        resolve_status(store,{"kind":"aprobado","revision_uid":"not-a-uid"})
    rec=resolve_status(store,{"kind":"aprobado","revision_uid":uids[1]})
    assert rec["r7b_layout"]["page"] == 0
    # The legacy master still exists and is selected only without an UID.
    old=resolve_status(store,{"kind":"aprobado"})
    assert old is not None and old["kind"]=="aprobado"


def test_required_fields_must_be_supplied_by_actual_layout(context):
    store,api,catalog,v,p,values,uids=context
    status={"kind":"aprobado","revision_uid":uids[1],"fields":{}}
    lay=resolve_status(store,status)["r7b_layout"]
    with pytest.raises(ValueError,match="obligatorio"):
        field_values(lay,values,status,strict=True)
    assert field_values(lay,values,{**status,"fields":{"firma":"Operador"}},strict=True)["lote"]=="LOTE-SINTETICO"


def test_retiring_selected_revision_blocks_new_combined_emission(context,tmp_path):
    store,api,catalog,v,p,values,uids=context
    state={"kind":"aprobado","revision_uid":uids[1],"placement":"integrada",
           "fields":{"firma":"PERSONA SINTETICA"}}
    catalog.retire(uids[1],"Sustituida documentalmente")
    with pytest.raises(PermissionError,match="no está vigente"):
        api.render(v,values,p,[1],1,1,tmp_path/"retired.pdf",True,status=state)
    assert not (tmp_path/"retired.pdf").exists()


def test_record_combined_snapshot_freezes_source_identity(context):
    store,api,catalog,v,p,values,uids=context
    store.approve(v["id"],"Calidad","APROBACION-PRINCIPAL-FICTICIA")
    version=store.version(v["id"])
    status={"kind":"aprobado","revision_uid":uids[1],"placement":"integrada",
            "fields":{"firma":"PERSONA SINTETICA"}}
    output=store.root/"emissions"/"FICTICIA_R7B.pdf"
    api.render(version,values,p,[1],1,1,output,False,status=status)
    issue=store.add_issue(version["id"],"Operador",1,1,[1],values,p,output,status=status)
    snap=json.loads(store.issue(issue)["design_snapshot_json"])
    assert snap["status_master"]["r7b_uid"] == uids[1]
    assert snap["status_master"]["r7b_layout_sha"] == catalog.get(uids[1])["layout_sha"]
    assert snap["status"]["revision_uid"] == uids[1]
    with fitz.open(output) as doc:
        assert "OPERADOR" not in doc[0].get_text() or "PERSONA SINTETICA" in doc[0].get_text()


def test_archived_approved_revision_stays_verifiable_only_for_historical_snapshot(context):
    store,api,catalog,v,p,values,uids=context
    state={"kind":"aprobado","revision_uid":uids[1]}
    original=resolve_status(store,state)
    catalog.retire(uids[1],"Version sustituida")
    with pytest.raises(PermissionError,match="no está vigente"):
        resolve_status(store,state)
    assert resolve_status(store,state,historical=original)==original
    altered={**original,"r7b_layout_sha":"0"*64}
    with pytest.raises(ValueError,match="histórica"):
        resolve_status(store,state,historical=altered)
