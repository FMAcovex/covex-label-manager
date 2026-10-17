"""Explicit mass conversion preserves approved documentary suffixes and inputs."""
import fitz
import pytest

from covex_label_manager.vessels import (
    parse_mass, mass_numeric_text, validate_vessel_masses, parse_tabular_vessels,
)
from covex_label_manager.engine import _overlay_field


@pytest.mark.parametrize('raw,expected',[
    ('0,3558',.3558), ('0,3558 kg',.3558),
    ('0,3558kg',.3558), ('0.3558 KG',.3558),
    (' 0,3558 Kg  ',.3558), ('1 kg',1), ('1e3 kg',1000),
    ('350 g',.35),('350000 mg',.35),('0,5 G',.0005),('1.5mg',.0000015),
])
def test_mass_accepts_optional_kg_without_changing_numeric_meaning(raw,expected):
    assert parse_mass(raw)==pytest.approx(expected)


@pytest.mark.parametrize('raw',[
    'kg', '0,3558 lb', '0,3558 t', '0,3558kgkg',
    '1 kg extra', '0,35 kg/l', 'NaN kg', '-1 kg', 'inf kg',
])
def test_invalid_or_unsupported_units_are_rejected(raw):
    with pytest.raises(ValueError):parse_mass(raw)


def test_gross_vs_net_compares_kilograms_in_all_notations():
    validate_vessel_masses({'pn':'0,3558 kg','pb':'0,5000'},1)
    validate_vessel_masses({'pn':'0,3558','pb':'0,5000 KG'},1)
    with pytest.raises(ValueError,match='menor que su peso neto'):
        validate_vessel_masses({'pn':'0,5000 kg','pb':'0,3558kg'},2)


def test_excel_import_keeps_original_unit_and_supports_overrides():
    source='Nº\tLote\tPN\tPB\tConservación\n1\tSYNTH\t0,3558 kg\t0,500 kg\t'
    data=parse_tabular_vessels(source,2)
    assert data['1']['pn']=='0,3558 kg'
    assert data['1']['pb']=='0,500 kg'
    validate_vessel_masses(data['1'],1)


@pytest.mark.parametrize('entered',('0,3558','0,3558kg','0,3558 kg','0,3558 KG'))
def test_word_master_field_keeps_approved_kg_suffix_once(entered):
    with fitz.open() as pdf:
        page=pdf.new_page(width=400,height=300)
        field=dict(key='pn',label='Peso neto',x=.1,y=.1,w=.75,h=.15,
                   font_pt=12,draw='textbox',suffix=' KG')
        _overlay_field(page,field,{'pn':entered,'_label_scale':1.0},
                       1,1,fitz.Rect(0,0,350,250),None,None,[],True)
        text=page.get_text()
        assert text.count('KG')==1
        assert '0,3558 KG' in text


def test_field_without_document_suffix_can_render_explicit_kg():
    with fitz.open() as pdf:
        page=pdf.new_page(width=400,height=300)
        field=dict(key='pb',label='Peso bruto',x=.1,y=.1,w=.75,h=.15,
                   font_pt=12,draw='textbox')
        _overlay_field(page,field,{'pb':'0,500 kg','_label_scale':1.0},
                       1,1,fitz.Rect(0,0,350,250),None,None,[],True)
        assert '0,500 kg' in page.get_text()


def test_mass_numeric_text_does_not_mutate_text_without_kg():
    assert mass_numeric_text('0,3558kg')=='0,3558'
    assert mass_numeric_text('0,3558')=='0,3558'


@pytest.mark.parametrize('entered,suffix,expected',[
    ('350g',' KG','0.35 KG'),('350000 mg',' KG','0.35 KG'),
    ('0,35 kg',' g','350 g'),('350g',' mg','350000 mg'),
    ('0,35',' g','350 g'),('350 g',' g','350 g'),
])
def test_render_converts_to_documentary_unit_exactly_once(entered,suffix,expected):
    with fitz.open() as pdf:
        page=pdf.new_page(width=400,height=300)
        field=dict(key='pn',label='Peso neto',x=.1,y=.1,w=.75,h=.15,font_pt=12,draw='textbox',suffix=suffix)
        before=dict(field);values={'pn':entered,'_label_scale':1.0}
        _overlay_field(page,field,values,1,1,fitz.Rect(0,0,350,250),None,None,[],True)
        assert expected in page.get_text()
        assert page.get_text().strip()==expected
        assert field==before and values['pn']==entered


def test_mixed_mass_units_and_excel_compare_in_canonical_kg():
    validate_vessel_masses({'pn':'350g','pb':'0,5 kg'},1)
    validate_vessel_masses({'pn':'350000mg','pb':'500g'},1)
    with pytest.raises(ValueError,match='menor que su peso neto'):
        validate_vessel_masses({'pn':'350g','pb':'349999mg'},1)
    data=parse_tabular_vessels('Nº\tPN\tPB\n1\t350 g\t500000 mg',1)
    validate_vessel_masses(data['1'],1)
    assert data['1']=={'pn':'350 g','pb':'500000 mg'}


def test_excel_declared_header_units_and_explicit_cell_override():
    data=parse_tabular_vessels('Nº\tPN (g)\tPeso bruto mg\n1\t350\t500000\n2\t0,35 kg\t500000',2)
    assert data['1']=={'pn':'350 g','pb':'500000 mg'}
    assert data['2']=={'pn':'0,35 kg','pb':'500000 mg'}
    for number,values in data.items():validate_vessel_masses(values,number)
