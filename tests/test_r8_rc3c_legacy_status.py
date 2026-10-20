"""R8-RC3C: unchanged legacy status contract uses exact glyphs in proof and sheets."""
import fitz
import pytest
from covex_label_manager.status_design import make_layout, render_proof, StatusDesignError
from covex_label_manager.status_catalog import StatusCatalog


def test_legacy_proof_one_character_short_box(tmp_path):
    source=tmp_path/"origin.pdf"
    with fitz.open() as doc:
        doc.new_page(width=150,height=100)
        doc.save(source)
    design=make_layout(source,"sin_analizar")
    design["fields"]=[dict(key="numero",label="Número",rect=[10,10,24,18.5],
                           font_size=10,bold=False,required=True)]
    output=tmp_path/"proof.pdf"
    render_proof(source,design,{"numero":"1"},output)
    with fitz.open(output) as doc:
        assert "1" in doc[0].get_text()


def test_legacy_proof_too_small_remains_blocked(tmp_path):
    source=tmp_path/"origin.pdf"
    with fitz.open() as doc:
        doc.new_page(width=150,height=100)
        doc.save(source)
    design=make_layout(source,"rechazado")
    design["fields"]=[dict(key="numero",label="Número",rect=[10,10,24,16],
                           font_size=10,bold=False,required=True)]
    with pytest.raises(StatusDesignError,match="excede"):
        render_proof(source,design,{"numero":"Á"},tmp_path/"proof.pdf")
