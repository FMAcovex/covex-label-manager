"""Synthetic regression: measured state text and lossless fit/fill safety."""
import fitz
import pytest
from covex_label_manager.status_scaling import draw_legacy_field, critical_losses, geometry


def test_single_digit_fits_short_box_by_actual_ink():
    with fitz.open() as document:
        page=document.new_page(width=100,height=100)
        # 10pt glyph occupies ~7.3pt; old 1.2em check rejected 8.5pt.
        draw_legacy_field(page,"1",fitz.Rect(10,10,24,18.5),10,False,"Lote")
        assert "1" in page.get_text()


def test_tall_glyph_does_not_silently_overflow():
    with fitz.open() as document:
        page=document.new_page(width=100,height=100)
        with pytest.raises(ValueError,match="excede"):
            draw_legacy_field(page,"Á",fitz.Rect(10,10,24,16),10,False,"Lote")


def test_unknown_glyph_is_blocked_not_substituted():
    with fitz.open() as document:
        page=document.new_page(width=100,height=100)
        with pytest.raises(ValueError,match="no disponible"):
            draw_legacy_field(page,"汉",fitz.Rect(10,10,50,30),10,False,"Lote")


def test_fixed_text_inside_safe_clip_does_not_trigger_false_loss():
    with fitz.open() as source:
        page=source.new_page(width=200,height=200)
        page.insert_text((50,100),"ESTADO",fontsize=10)
        crop=[10,10,190,190]
        layout={"crop":crop,"fields":[]}
        assert critical_losses(page,layout,fitz.Rect(40,40,160,160)) == []


def test_cutting_printed_text_remains_blocked():
    with fitz.open() as source:
        page=source.new_page(width=200,height=200)
        page.insert_text((50,100),"ESTADO",fontsize=10)
        assert critical_losses(page,{"crop":[10,10,190,190],"fields":[]},
                               fitz.Rect(10,10,51,190))
