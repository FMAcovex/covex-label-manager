"""Independent R7A catalogue regression tests using only synthetic PDF sources."""
import json
from pathlib import Path

import fitz
import pytest

from covex_label_manager.status_catalog import StatusCatalogue
from covex_label_manager.status_design import make_layout


@pytest.fixture
def catalogue(tmp_path):
    return StatusCatalogue(tmp_path / "data")


@pytest.fixture
def combined_pdf(tmp_path):
    path = tmp_path / "SYNTHETIC-THREE-REGIONS.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=595, height=842)
        colors = [(1, 1, 0), (0.55, 0.85, 0.45), (1, 0.2, 0.2)]
        for index, (name, color) in enumerate(zip(("Sin analizar", "Aprobado", "Rechazado"), colors)):
            y = 50 + index * 220
            page.draw_rect(fitz.Rect(55, y, 540, y + 175), fill=color)
            page.insert_text((65, y + 26), "SYNTHETIC " + name, fontsize=17)
        doc.save(path)
    return path


def _entries(path, revision="00"):
    entries = []
    for i, kind in enumerate(("sin_analizar", "aprobado", "rechazado")):
        crop = [55, 50 + 220 * i, 540, 225 + 220 * i]
        layout = make_layout(path, kind, crop=crop)
        entries.append({"kind": kind, "revision": revision, "layout": layout})
    return entries


def test_one_source_three_independent_revisions(catalogue, combined_pdf):
    uid = catalogue.import_many(combined_pdf, _entries(combined_pdf))
    assert len(uid) == 3 and len(set(uid)) == 3
    records = [catalogue.verify(x) for x in uid]
    assert {r["kind"] for r in records} == {"sin_analizar", "aprobado", "rechazado"}
    assert {r["source_sha"] for r in records}.__len__() == 1
    assert len({r["layout_sha"] for r in records}) == 3
    assert all(r["state"] == "DRAFT" for r in records)
    assert catalogue.current("aprobado") is None
    with pytest.raises(ValueError):
        catalogue.import_many(combined_pdf, _entries(combined_pdf))
    assert len(catalogue.list_revisions()) == 3


def test_independent_approval_and_replacement(catalogue, combined_pdf):
    ids = catalogue.import_many(combined_pdf, _entries(combined_pdf))
    for uid in ids:
        catalogue.submit(uid)
    with pytest.raises(PermissionError):
        catalogue.approve(ids[1], "Revisor", "DOC-VALIDO-01")
    catalogue.approve(ids[1], "Revisor", "DOC-VALIDO-01", confirmation=True)
    assert catalogue.current("aprobado")["uid"] == ids[1]
    assert catalogue.current("sin_analizar") is None
    with pytest.raises(PermissionError):
        catalogue.save_draft(ids[1], json.loads(catalogue.get(ids[1])["layout_json"]))
    second = catalogue.import_many(combined_pdf, [_entries(combined_pdf, revision="01")[1]])[0]
    catalogue.submit(second)
    with pytest.raises(ValueError):
        catalogue.approve(second, "Revisor", "DOC-VALIDO-02", confirmation=True)
    catalogue.approve(second, "Revisor", "DOC-VALIDO-02", confirmation=True,
                      replacement_reason="Nueva revision autorizada")
    assert catalogue.current("aprobado")["uid"] == second
    assert catalogue.get(ids[1])["state"] == "RETIRED"


def test_proof_does_not_approve_and_emission_is_blocked(catalogue, combined_pdf):
    uid = catalogue.import_many(combined_pdf, [_entries(combined_pdf)[2]])[0]
    proof = catalogue.preview(uid, count=2, width_mm=55)
    assert proof.exists()
    with fitz.open(proof) as doc:
        assert "PRUEBA - NO APTO" in doc[0].get_text()
    with pytest.raises(PermissionError):
        catalogue.emit(uid, {}, "Operador", width_mm=55)
    catalogue.submit(uid)
    catalogue.approve(uid, "Calidad", "DOC-VALIDO-03", confirmation=True)
    issued, pdf = catalogue.emit(uid, {}, "Operador", count=2, width_mm=55)
    assert pdf.exists()
    assert catalogue.issues()[0]["uid"] == issued


def test_reprint_historic_pdf_after_retirement(catalogue, combined_pdf):
    uid = catalogue.import_many(combined_pdf, [_entries(combined_pdf)[0]])[0]
    catalogue.submit(uid)
    catalogue.approve(uid, "Calidad", "DOC-VALIDO-04", confirmation=True)
    issued, original = catalogue.emit(uid, {}, "Operador", width_mm=55)
    from covex_label_manager.storage import sha256
    former = sha256(original)
    catalogue.retire(uid, "Version obsoleta y sustituida")
    copy_id, copied = catalogue.reprint(issued, "Operador", "Reimpresion justificada")
    assert copied != original and sha256(copied) == former
    entry = catalogue.issues()[0]
    assert entry["uid"] == copy_id and entry["origin_issue_uid"] == issued
    assert entry["revision_uid"] == uid


def test_tampering_blocks_records(catalogue, combined_pdf):
    uid = catalogue.import_many(combined_pdf, [_entries(combined_pdf)[0]])[0]
    rec = catalogue.get(uid)
    (catalogue.root / rec["pdf_path"]).write_bytes(b"not-a-pdf")
    with pytest.raises(ValueError):
        catalogue.submit(uid)
    with pytest.raises(ValueError):
        catalogue.preview(uid)


def test_single_state_independent_of_catalogue_materials(catalogue, combined_pdf):
    uid = catalogue.import_many(combined_pdf, [_entries(combined_pdf)[1]])[0]
    catalogue.submit(uid)
    catalogue.approve(uid, "Calidad", "DOC-VALIDO-05", confirmation=True)
    issue, output = catalogue.emit(uid, {}, "Operador", width_mm=60)
    assert output.is_file()
    assert issue
    # Status issues are not fictional product issues in the legacy SQLite v4.
    assert (catalogue.root / "status_catalog.sqlite").is_file()
    assert not (catalogue.root / "storage_v4" / "labels.sqlite").exists()


def test_catalogue_closes_sqlite_handles_for_windows_cleanup(catalogue, combined_pdf):
    """The application must release sidecar handles when a Qt demo closes."""
    catalogue.import_many(combined_pdf, [_entries(combined_pdf)[0]])
    catalogue.list_revisions()
    catalogue.current("sin_analizar")
    import os
    relocated = catalogue.db_path.with_suffix(".relocated")
    os.replace(catalogue.db_path, relocated)
    os.replace(relocated, catalogue.db_path)
    assert catalogue.db_path.is_file()


def test_clone_creates_new_draft_without_mutating_original(catalogue, combined_pdf):
    uid = catalogue.import_many(combined_pdf, [_entries(combined_pdf)[1]])[0]
    catalogue.submit(uid)
    catalogue.approve(uid, "Revisor", "EVIDENCIA-REV00", confirmation=True)
    old = catalogue.get(uid)
    new_uid = catalogue.new_revision(uid, "01", "Nueva geometria propuesta")
    fresh = catalogue.get(new_uid)
    assert fresh["state"] == "DRAFT" and fresh["kind"] == "aprobado"
    assert fresh["source_sha"] == old["source_sha"]
    assert fresh["layout_sha"] == old["layout_sha"]
    assert fresh["approval_ref"] is None
    assert catalogue.current("aprobado")["uid"] == uid
    assert catalogue.get(uid) == old
    with pytest.raises(ValueError):
        catalogue.new_revision(uid, "01", "Intento duplicado")
