"""Coordinates grounded in the visible PDF obtained from each provided Word.

The source PDF is the visual authority; every geometry is expressed as a normalized
rectangle/point relative to its approved-label crop. These are review proposals,
NEVER an automatic GMP approval.
"""
from __future__ import annotations
from pathlib import Path
import fitz
from copy import deepcopy


def rebase_layout(fields, area, old_crop, new_crop):
    """Keep absolute PDF anchors when changing the visible master crop."""
    ox,oy,ox1,oy1=old_crop;nx,ny,nx1,ny1=new_crop
    ow,oh=ox1-ox,oy1-oy;nw,nh=nx1-nx,ny1-ny
    if nw<=0 or nh<=0:raise ValueError('Recorte inválido.')
    def box(r):
        x,y,w,h=r
        return [(ox+x*ow-nx)/nw,(oy+y*oh-ny)/nh,w*ow/nw,h*oh/nh]
    result=deepcopy(fields)
    for f in result:
        x,y,w,h=box([f[k] for k in ('x','y','w','h')])
        if min(x,y)<0 or x+w>1.001 or y+h>1.001:
            raise ValueError('El recorte excluye un campo: '+f.get('label',f['key']))
        f.update(x=x,y=y,w=w,h=h)
        if f.get('erase'):f['erase']=box(f['erase'])
        if 'second_x' in f:f['second_x']=(ox+f['second_x']*ow-nx)/nw
        if 'next_w' in f:f['next_w']=f['next_w']*ow/nw
    rebased=box(area) if area else []
    if rebased and (min(rebased[:2])<0 or rebased[0]+rebased[2]>1.001 or rebased[1]+rebased[3]>1.001):
        raise ValueError('El recorte excluye la zona de estado.')
    return result,rebased


STATUS_CROPS = {
    'sin_analizar': [84.8, 91.9, 517.0, 175.2],
    'aprobado': [85.3, 226.4, 517.5, 309.7],
    'rechazado': [85.3, 347.1, 517.5, 430.4],
}
STATUS_NAMES = {'ninguna': 'Sin etiqueta de estado', 'sin_analizar': 'Sin analizar',
                'aprobado': 'Aprobado', 'rechazado': 'Rechazado'}
STATUS_COLORS = {'sin_analizar': (1, 1, 0), 'aprobado': (.57255, .81569, .31373),
                 'rechazado': (1, 0, 0)}


def span_for(page, text):
    """Return exact text span from rendered Word, no OCR or guessed position."""
    for b in page.get_text('dict')['blocks']:
        for line in b.get('lines', []):
            for sp in line['spans']:
                if text in sp['text']:
                    return sp
    raise ValueError(f'No se encuentra referencia en el Word convertido: {text}')


def rel(x, y, w, h, crop):
    x0, y0, x1, y1 = crop
    return [round((x-x0)/(x1-x0), 7), round((y-y0)/(y1-y0), 7),
            round(w/(x1-x0), 7), round(h/(y1-y0), 7)]


def make_field(crop, key, label, rect, size, **extra):
    x, y, w, h = rel(*rect, crop)
    return dict(key=key, label=label, x=x, y=y, w=w, h=h,
                font_pt=size, required=extra.pop('required', False),
                bold=extra.pop('bold', False), **extra)


def anchored_baseline(crop, key, label, x, original_span, xmax, **kw):
    y = original_span['origin'][1]
    return make_field(crop, key, label, (x, y, xmax-x, 1.5),
                      original_span['size'], draw='baseline', **kw)


def rect_for_status_area(crop, coords):
    return rel(coords[0], coords[1], coords[2]-coords[0], coords[3]-coords[1], crop)


def acetona_template(pdf_path, crop):
    """Anchor every text position to ACETONA Word's converted text geometry."""
    with fitz.open(pdf_path) as pdf:
        p=pdf[0]
        lot=span_for(p, 'CV/S-60/')
        obs=span_for(p, 'OBSERVACIONES:')
        fields=[
            anchored_baseline(crop,'lote','Lote (sufijo CV/S-60/)',lot['bbox'][2]+1,lot,502,
                              required=True,bold=True,strip_prefix='CV/S-60/'),
            make_field(crop,'observaciones','Observaciones', (77,obs['bbox'][3]+6,410-77,87),
                       13,draw='textbox'),
            anchored_baseline(crop,'numero','Numeración correlativa',405,
                              {'origin':(405,510),'size':13},502,align='right',bold=True),
        ]
        for key, label, search, xlast, required in [
            ('cantidad','Cantidad','CANTIDAD:',503,True),
            ('proveedor','Proveedor','PROVEEDOR:',503,False),
            ('direccion','Dirección','DIRECCIÓN:',503,False),
            ('telefono','Teléfono','TELÉFONO:',503,False),
        ]:
            sp=span_for(p,search)
            fields.append(anchored_baseline(crop,key,label,sp['bbox'][2]+3,sp,xlast,
                                            required=required))
        # Free cell after the printed caption. Do not erase signature placeholders.
        for key,label,search,right in [
            ('fecha','Fecha de recepción','Fecha:',180),
            ('recibido_por','Recibido por','Recibido por:',336),
            ('muestreado_por','Muestreado por','Muestreado por:',503),
        ]:
            sp=span_for(p,search)
            fields.append(make_field(crop,key,label,(sp['bbox'][0]+2,546.5,right-sp['bbox'][0]-3,23),
                                     9.5,draw='textbox'))
    return fields, rect_for_status_area(crop,[72.1,575.0,504.3,658.3])


def edrofonio_template(pdf_path, crop):
    """Use Word text baselines and the physical status placeholder boundaries."""
    with fitz.open(pdf_path) as pdf:
        p=pdf[0]
        lot=span_for(p,'Lote: CV/EDR/')
        pn=span_for(p,'PN-__________ KG')
        pb=span_for(p,'PB-__________ KG')
        num=span_for(p,'Nº de envase/Total de envases')
        cond=span_for(p,'Condiciones de conservación')
        fields=[
            anchored_baseline(crop,'lote','Lote (sufijo CV/EDR/)',lot['bbox'][2]+1,lot,513,
                               required=True,bold=True,strip_prefix='CV/EDR/'),
            anchored_baseline(crop,'pn','PN - Peso neto (kg)',131,pn,502,required=True,bold=True,
                              suffix=' KG',erase=rel(128,pn['bbox'][1]-1,211,32,crop)),
            anchored_baseline(crop,'pb','PB - Peso bruto (kg)',131,pb,502,required=True,bold=True,
                              suffix=' KG',erase=rel(128,pb['bbox'][1]-1,211,32,crop)),
            anchored_baseline(crop,'numero','Nº envase / total',339,num,515,
                              align='right',bold=True,
                              erase=rel(337,num['bbox'][1]-1,179,18,crop)),
            make_field(crop,'conservacion','Condiciones de conservación, humedad, riqueza',
                        (cond['bbox'][2]+3,cond['origin'][1],516.2-cond['bbox'][2]-3,35),
                        12,draw='continuation', second_x=rel(88.4,0,0,0,crop)[0],
                        next_w=rel(0,0,427.5,0,crop)[2], max_lines=3),
        ]
        # Signature areas are intentionally left empty for manual records.
        # Do NOT insert an electronic approval or electronic signature.
    return fields, rect_for_status_area(crop,[84.8,514.3,516.9,597.6])
