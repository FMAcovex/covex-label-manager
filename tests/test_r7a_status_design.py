"""R7A design contract: synthetic documents only, no production data."""
import copy
import fitz
import pytest

from covex_label_manager.status_design import (
    StatusDesignError, make_layout, render_proof, validate_layout, validate_values,
)


@pytest.fixture
def source(tmp_path):
    p = tmp_path / "ficticio.pdf"
    with fitz.open() as doc:
        for _ in range(3):
            page = doc.new_page(width=600, height=450)
            page.insert_text((15, 18), "SYNTHETIC - FICTIONAL", fontsize=10)
        doc.save(p)
    return p


@pytest.mark.parametrize("kind", ["sin_analizar", "aprobado", "rechazado"])
def test_create_three_distinct_pending_designs(source, kind):
    layout = make_layout(source, kind, page=1, crop=[30, 40, 560, 190])
    assert layout["kind"] == kind
    assert layout["page"] == 1
    assert layout["size_mm"][0] > 150


def test_layout_has_per_design_fields_and_proof(source, tmp_path):
    layout = make_layout(source, "aprobado", crop=[30, 40, 560, 190])
    layout["fields"] = [
        {"key": "lote", "label": "Lote", "rect": [55, 90, 240, 120],
         "font_size": 11, "bold": True, "required": True},
        {"key": "fecha", "label": "Fecha", "rect": [270, 90, 460, 120],
         "font_size": 9, "required": False},
    ]
    with fitz.open(source) as doc:
        layout = validate_layout(layout, doc)
    assert validate_values(layout, {"lote": "ABC123"}) == {"lote": "ABC123", "fecha": ""}
    dest = tmp_path / "proof.pdf"
    render_proof(source, layout, {"lote": "LOTE FICTICIO"}, dest)
    with fitz.open(dest) as proof:
        assert len(proof) == 1
        text = proof[0].get_text()
        assert "LOTE FICTICIO" in text
        assert "PRUEBA - NO APTO" in text
    with pytest.raises(FileExistsError):
        render_proof(source, layout, {}, dest)


def test_does_not_modify_original(source, tmp_path):
    original = source.read_bytes()
    layout = make_layout(source, "rechazado")
    render_proof(source, layout, {}, tmp_path / "out.pdf")
    assert source.read_bytes() == original


def test_reject_unsafe_crop_and_page(source):
    with pytest.raises(StatusDesignError):
        make_layout(source, "aprobado", page=9)
    for crop in [[10, 10, 999, 100], [12, 12, 12, 40], [0, 0, 2, 2]]:
        with pytest.raises(StatusDesignError):
            make_layout(source, "sin_analizar", crop=crop)


def test_overlap_duplicates_invalid_fields(source):
    layout = make_layout(source, "sin_analizar")
    layout["fields"] = [
        {"key": "lote", "rect": [10, 20, 100, 40]},
        {"key": "lote", "rect": [200, 20, 300, 40]},
    ]
    with fitz.open(source) as doc, pytest.raises(StatusDesignError):
        validate_layout(layout, doc)
    layout["fields"][1]["key"] = "fecha"
    layout["fields"][1]["rect"] = [50, 20, 130, 40]
    with fitz.open(source) as doc, pytest.raises(StatusDesignError):
        validate_layout(layout, doc)


def test_reject_missing_required_and_overflow(source, tmp_path):
    layout = make_layout(source, "sin_analizar")
    layout["fields"] = [{"key": "lote", "rect": [20, 50, 65, 70],
                         "font_size": 10, "required": True}]
    with fitz.open(source) as doc:
        layout = validate_layout(layout, doc)
    with pytest.raises(StatusDesignError):
        validate_values(layout, {}, strict=True)
    with pytest.raises(StatusDesignError):
        render_proof(source, layout, {"lote": "TEXTO FICTICIO DEMASIADO LARGO"}, tmp_path / "invalid.pdf")
    assert not (tmp_path / "invalid.pdf").exists()


def test_guard_against_source_overwrite_and_bad_values(source):
    layout = make_layout(source, "rechazado")
    with pytest.raises(StatusDesignError):
        render_proof(source, layout, {}, source)
    with pytest.raises(StatusDesignError):
        validate_values(layout, {"another": "x"}, strict=True)
    field_layout = {**layout, "fields": [{"key": "another", "label": "Another", "required": False}]}
    with pytest.raises(StatusDesignError):
        validate_values(field_layout, {"another": "x\n"}, strict=False)
