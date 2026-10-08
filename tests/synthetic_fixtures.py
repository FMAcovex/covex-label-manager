"""Entirely generated test documents. No original artwork or production data.

Historical fixture filenames exercise legacy source adapters. Visible designs
are plain DEMO diagrams, generated from scratch, never shipped as real masters.
"""
import json
from pathlib import Path
import fitz
from docx import Document

def generate(root):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    def pdf(name,draw):
        with fitz.open() as document:
            page=document.new_page(width=595,height=842)
            draw(page)
            document.set_metadata({'title':'Synthetic software test fixture','author':'Test generator'})
            document.save(root/(name+'.pdf'))
        doc=Document();doc.core_properties.author='Test generator'
        doc.add_paragraph('SYNTHETIC TEST DOCUMENT - NOT A COVEX MASTER')
        doc.save(root/(name+'.docx'))
    def text(p,x,y,s,size=12):p.insert_text((x,y),s,fontsize=size,fontname='helv')
    def a(p):
        p.draw_rect(fitz.Rect(65,55,530,741))
        text(p,75,90,'DEMO A - SYNTHETIC TEST ONLY',15)
        text(p,75,140,'CV/S-60/')
        for y,s in [(180,'CANTIDAD:'),(210,'PROVEEDOR:'),(240,'DIRECCIÓN:'),(270,'TELÉFONO:'),(315,'OBSERVACIONES:')]:text(p,75,y,s)
        for x,s in [(75,'Fecha:'),(190,'Recibido por:'),(350,'Muestreado por:')]:text(p,x,530,s,9)
        text(p,75,700,'SYNTHETIC FIXTURE',10)
    def b(p):
        p.draw_rect(fitz.Rect(84.8,133.60077,474.4,609.80078))
        p.draw_rect(fitz.Rect(84.8,259.60077,516.9,597.80078))
        for y in (320,400,480,514.3):p.draw_line((84.8,y),(516.9,y))
        text(p,90,200,'DEMO B - SYNTHETIC TEST ONLY',14)
        text(p,90,295,'Lote: CV/EDR/')
        text(p,90,345,'PN-__________ KG',13)
        text(p,90,380,'PB-__________ KG',13)
        text(p,340,420,'Nº de envase/Total de envases',8)
        text(p,90,455,'Condiciones de conservación, humedad, riqueza, controles DEMO:',10)
    def states(p):
        from covex_label_manager.geometry import STATUS_CROPS,STATUS_NAMES,STATUS_COLORS
        for kind,crop in STATUS_CROPS.items():
            box=fitz.Rect(crop);p.draw_rect(box,fill=STATUS_COLORS[kind])
            text(p,90,box.y0+35,STATUS_NAMES[kind],13)
            text(p,90,box.y0+50,'SYNTHETIC STATE DIAGRAM',8)
    pdf('ACETONA_MASTER_00',a);pdf('EDROFONIO_MASTER_00',b);pdf('ESTADOS_MASTER_00',states)
    materials=[{'name':f'DEMO material {i:03}','code':f'DEMO{i:03}','category':'Synthetic','source_ref':'Generated fictional test record'} for i in range(224)]
    for i,code in [(0,'DUP001'),(1,'DUP001'),(2,'DUP002'),(3,'DUP002')]:materials[i]['code']=code
    (root/'cm_materials.json').write_text(json.dumps(materials),encoding='utf-8')
    return root


def activate_for_script():
    """Install disposable fixtures for standalone manual smoke scripts only."""
    import tempfile
    import hashlib
    import covex_label_manager.storage as storage
    import covex_label_manager.integrity as integrity
    temporary=tempfile.TemporaryDirectory(prefix='covex_synthetic_')
    root=generate(temporary.name)
    storage.resource_dir=lambda:root
    integrity.KNOWN_OVERFLOW_PDF=hashlib.sha256((root/'EDROFONIO_MASTER_00.pdf').read_bytes()).hexdigest()
    return temporary
