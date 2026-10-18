"""R7B native Qt binding: synthetic approved state master only."""
import json
import fitz
import pytest

pytest.importorskip("PySide6")
from test_r3a_qt import studio
from covex_label_manager.status_design import make_layout


def test_operator_explicitly_selects_independent_approved_state_revision(studio, tmp_path):
    window, session, app = studio
    src = tmp_path / "R7B-FICTICIO.pdf"
    with fitz.open() as pdf:
        page = pdf.new_page(width=420,height=300)
        page.insert_text((25,55),"ETIQUETA SINTETICA SIN ANALIZAR")
        pdf.save(src)
    layout = make_layout(src, "sin_analizar")
    layout["fields"] = [
        {"key":"firma","label":"Firma de prueba","rect":[20,100,230,132],
         "font_size":11,"bold":False,"required":True}
    ]
    catalog = session.services.status_catalog
    uid = catalog.import_many(src,[{
        "kind":"sin_analizar","revision":"00","layout":layout
    }])[0]
    catalog.submit(uid)
    catalog.approve(uid,"Revisor sintético","DOC-FICTICIO-R7B-00",confirmation=True)
    vid = session.initial_id
    work = session.services.work.create(vid,name="R7B trabajo ficticio")
    window.load_emission_work(work["uid"])
    panel = window.emission_panel
    panel.status_kind.setCurrentIndex(panel.status_kind.findData("sin_analizar"))
    index = panel.status_revision.findData(uid)
    assert index > 0
    panel.status_revision.setCurrentIndex(index)
    assert "firma" in panel.r7b_field_widgets
    panel.r7b_field_widgets["firma"].setText("OPERADOR DEMO")
    status = panel.capture()["status"]
    assert status["revision_uid"] == uid
    assert status["kind"] == "sin_analizar"
    assert status["fields"] == {"firma":"OPERADOR DEMO"}
    panel.status_revision.setCurrentIndex(0)
    assert "revision_uid" not in panel.capture()["status"]
