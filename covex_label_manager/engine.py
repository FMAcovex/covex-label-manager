from __future__ import annotations
import json
import math
import os
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from collections.abc import Iterable
import fitz

MM=72.0/25.4
A4=(210.,297.)


class LayoutError(ValueError):
    pass


def is_mini_advisory(message):
    """Only font legibility warnings, never real clipping/contrast/document guards."""
    text=str(message).strip().casefold()
    # Accept only exact families emitted by the font-size validators.
    # Unrelated data loss or pictogram alerts must never be downgraded.
    return (
        (text.startswith('texto pequeno (') and ' pt) en ' in text
         and text.endswith(': requiere revisar el formato.'))
        or (text.startswith('texto demasiado pequeño (')
            and text.endswith('; mínimo operativo 6 pt.'))
        or (text.startswith('texto fijo demasiado pequeño (')
            and ' pt): ' in text
            and text.endswith('amplíe el área o prepare una revisión de origen.'))
        or (': texto final demasiado pequeño (' in text
            and text.endswith('; mínimo 6 pt.'))
        or (text.startswith('campo de estado demasiado pequeño (')
            and text.endswith('compruebe la legibilidad física al 100 %.'))
        or (text.startswith('estado histórico demasiado pequeño tras la composición;')
            and text.endswith('comprobar legibilidad física al 100 %.'))
        or (text.startswith('texto pequeño en etiqueta de estado (')
            and text.endswith('pt): revise el tamaño.'))
    )


def blocking_render_warnings(warnings,profile):
    """Mini opt-in downgrades size notices, never actual PDF content loss."""
    return [msg for msg in warnings if not
            (profile.get('mini_mode',False) and is_mini_advisory(msg))]


@dataclass(frozen=True)
class SheetPlan:
    cols: int
    rows: int
    capacity: int
    pages: int
    count_physical: int
    paper_w_mm: float
    paper_h_mm: float


def _plan_sheet(profile, physical_count):
    from .sheet_layout import validate_profile, paper_size, slots, available_first_page
    mode=validate_profile(profile)
    from .printer_calibration import validate as validate_printer_calibration
    validate_printer_calibration(profile)
    w=float(profile['width_mm']); h=float(profile['height_mm'])
    m=float(profile.get('margin_mm',8)); gap=float(profile.get('gap_mm',3))
    first=int(profile.get('start_slot',1))
    p_w,p_h=paper_size(profile)
    minimum=5 if profile.get('mini_mode',False) else 10
    if not (0<=m<=40 and 0<=gap<=50 and (mode=='free' or (minimum<=w<=p_w and minimum<=h<=p_h))):
        raise LayoutError('Compruebe el tamano de etiqueta, margenes y separacion.')
    cols=math.floor((p_w-2*m+gap+1e-9)/(w+gap))
    rows=math.floor((p_h-2*m+gap+1e-9)/(h+gap))
    boxes=slots(profile,cols,rows)
    capacity=len(boxes)
    if mode=='free':cols=capacity;rows=1
    if capacity<1:
        raise LayoutError('No cabe ninguna etiqueta en la hoja con estos ajustes.')
    if first<1 or first>capacity:
        raise LayoutError(f'La casilla inicial debe estar entre 1 y {capacity}.')
    n=int(physical_count)
    if n<1 or n>10000:
        raise LayoutError('Numero de etiquetas fuera del rango permitido (1 a 10000).')
    first_space=len(available_first_page({**profile,'start_slot':first},capacity))
    pages=1 if n<=first_space else 1+math.ceil((n-first_space)/capacity)
    return SheetPlan(cols,rows,capacity,pages,n,p_w,p_h)


def plan_sheet(profile, physical_count):
    try:return _plan_sheet(profile,physical_count)
    except (ValueError,KeyError,TypeError,OverflowError) as ex:raise LayoutError(str(ex)) from ex


def text_from_field(field, values, number, total):
    key=field['key']
    if key=='numero':
        return f'{number}/{total}'
    if key=='texto_fijo':
        return str(field.get('text',''))
    return str(values.get(key,'')).strip()


def validate_fields(version, values, profile, strict=True):
    fields=json.loads(version['fields_json']) if isinstance(version['fields_json'],str) else version['fields_json']
    result=[]
    crop=json.loads(version['crop_json']) if isinstance(version['crop_json'],str) else version['crop_json']
    crop_w=crop[2]-crop[0]; crop_h=crop[3]-crop[1]
    scale=min(float(profile['width_mm'])*MM/crop_w,float(profile['height_mm'])*MM/crop_h)
    for f in fields:
        k=f.get('key','')
        if f.get('required') and not str(values.get(k,'')).strip():
            result.append(f'Campo obligatorio sin completar: {f.get("label",k)}')
        if float(f.get('x',0))<0 or float(f.get('y',0))<0 or float(f.get('w',0))<=0 or float(f.get('h',0))<=0 or float(f['x'])+float(f['w'])>1.001 or float(f['y'])+float(f['h'])>1.001:
            result.append(f'Campo fuera de la etiqueta: {f.get("label",k)}')
        font=float(f.get('font_pt',10))*scale
        if font<6 and (k=='numero' or k=='texto_fijo' or str(values.get(k,''))):
            result.append(f'Texto pequeno ({font:.1f} pt) en {f.get("label",k)}: requiere revisar el formato.')
    # A closed template can legitimately contain no variable fields.
    if strict and result:
        raise LayoutError('\n'.join(result))
    return result


def _fonts():
    paths=[
      ('C:/Windows/Fonts/arial.ttf','C:/Windows/Fonts/arialbd.ttf'),
      ('/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
       '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf'),
      ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
       '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
    ]
    for regular,bold in paths:
        if os.path.exists(regular):
            return regular, bold if os.path.exists(bold) else regular
    return None,None


def _loaded_json(value, fallback):
    return json.loads(value) if isinstance(value,str) else (value if value is not None else fallback)


def normalized_lot(value, prefix=''):
    value=str(value or '').strip()
    if not value:return ''
    if not prefix or value.upper().startswith(prefix.upper()):return value
    if value.upper().startswith('CV/'):
        raise LayoutError('El lote tiene un prefijo diferente del asignado a la plantilla ('+prefix+').')
    return prefix+value


def _font(fontpath, text, fontsize):
    if fontpath:
        return fitz.Font(fontfile=fontpath).text_length(text,fontsize=fontsize)
    return fitz.get_text_length(text,fontsize=fontsize,fontname='helv')


def _wrap_words(txt,max_width,fontpath,fontsize):
    lines=[];current=''
    for word in txt.replace('\n',' \n ').split(' '):
        if word=='\n':lines.append(current);current='';continue
        if _font(fontpath,word,fontsize)>max_width:
            raise LayoutError('Una palabra no cabe en el recuadro: '+word)
        candidate=(current+' '+word).strip()
        if _font(fontpath,candidate,fontsize)<=max_width:
            current=candidate
        elif current:
            lines.append(current);current=word
        else:
            raise LayoutError('Una palabra no cabe en el recuadro: '+word)
    if current:lines.append(current)
    return lines


def _overlay_field(page,field,values,number,total,view_rect,font_regular,font_bold,warnings,test_mode):
    key=field['key']
    if key=='numero':
        txt=f'{number}/{total}'
    elif key=='texto_fijo':
        txt=str(field.get('text',''))
    else:
        txt=str(values.get(key,'')).strip()
        # The approved suffix fixes the documentary unit, not the input unit.
        # Convert the amount, never simply strip "g" and append "KG".
        if key in ('pn','pb') and str(field.get('suffix','')).strip().lower() in ('kg','g','mg'):
            from .vessels import mass_numeric_text
            txt=mass_numeric_text(txt,field['suffix'])
        if field.get('strip_prefix') and txt.upper().startswith(field['strip_prefix'].upper()):
            txt=txt[len(field['strip_prefix']):]
        if txt and field.get('suffix') and not txt.upper().endswith(field['suffix'].upper()):
            txt+=field['suffix']
        if txt and field.get('prefix'):
            txt=field['prefix']+txt
    if not txt:
        return
    w,h=view_rect.width,view_rect.height
    x=view_rect.x0+float(field['x'])*w
    y=view_rect.y0+float(field['y'])*h
    maxw=float(field['w'])*w
    maxh=float(field['h'])*h
    # View is a fitted rendering of the original crop; scale is supplied separately.
    size=float(field.get('font_pt',10))*float(values['_label_scale'])
    fontpath=font_bold if field.get('bold') else font_regular
    fname=('CovexBold' if field.get('bold') else 'CovexRegular') if font_regular else ('hebo' if field.get('bold') else 'helv')
    if field.get('erase'):
        xx,yy,ww,hh=map(float,field['erase'])
        mask=fitz.Rect(view_rect.x0+xx*w,view_rect.y0+yy*h,view_rect.x0+(xx+ww)*w,view_rect.y0+(yy+hh)*h)
        page.draw_rect(mask,fill=(1,1,1),color=None,overlay=True)
    if 'typography' in field:
        from .typography import paint
        continuation=None
        if field.get('draw')=='continuation':
            continuation=(view_rect.x0+field['second_x']*w,field['next_w']*w,int(field.get('max_lines',3)))
        try:
            warnings.extend(paint(page,txt,fitz.Rect(x,y,x+maxw,y+maxh),size,
                field.get('bold',False),field['typography'],strict=not test_mode,
                baseline=field.get('draw') in ('baseline','continuation'),continuation=continuation,
                check_minimum=not values.get('_mini_mode',False)))
        except ValueError as exc:
            raise LayoutError(field.get('label',key)+': '+str(exc)) from exc
        return
    if field.get('draw')=='baseline':
        try:
            width=_font(fontpath,txt,size)
        except ValueError as ex:
            raise LayoutError('Texto inválido en '+key+': '+str(ex))
        if width>maxw+2*float(values['_label_scale']):
            msg=f'El campo {field["label"]} no cabe ({number}/{total})'
            raise LayoutError(msg)
        if field.get('align')=='right':
            x+=maxw-width
        elif field.get('align')=='center':
            x+=(maxw-width)/2
        page.insert_text(fitz.Point(x,y),txt,fontname=fname,fontsize=size,overlay=True,
                         color=(.04,.05,.08))
        return
    if field.get('draw')=='continuation':
        # Preserve the Word's bold fixed caption. Add only its changing content,
        # and continue subsequent lines from the original table's left margin.
        words=txt.split()
        lines=[];cur='';available=maxw
        full_width=float(field['next_w'])*w
        for word in words:
            candidate=(cur+' '+word).strip()
            if _font(fontpath,candidate,size)<=available:
                cur=candidate
            else:
                # An empty first line is intentional when the caption leaves
                # too little room. Continue under the caption, not over it.
                lines.append(cur)
                available=full_width
                if _font(fontpath,word,size)>available:
                    raise LayoutError(f'Una palabra no cabe en condiciones: {word}')
                cur=word
        if cur:lines.append(cur)
        if (len(lines)>int(field.get('max_lines',3)) or
                (len(lines)-1)*size*1.13+size*.3>maxh):
            raise LayoutError(f'Condiciones demasiado largas para la etiqueta {number}/{total}')
        for j,line in enumerate(lines):
            posx=x if j==0 else view_rect.x0+float(field['second_x'])*w
            page.insert_text((posx,y+j*size*1.13),line,fontname=fname,fontsize=size,overlay=True)
        return
    if field.get('draw')=='paragraph':
        lines=_wrap_words(txt,maxw-3*values['_label_scale'],fontpath,size)
        baseline=y+size*1.05
        lineh=size*1.13
        if baseline+(len(lines)-1)*lineh>y+maxh-1:
            msg=f'El texto de {field["label"]} supera el espacio disponible ({number}/{total})'
            raise LayoutError(msg)
        for line in lines:
            page.insert_text((x,baseline),line,fontname=fname,fontsize=size,overlay=True)
            baseline+=lineh
        return
    rect=fitz.Rect(x,y,x+maxw,y+maxh)
    available=page.insert_textbox(rect,txt,fontname=fname,fontsize=size,color=(.04,.05,.08),
                                   align={'right':fitz.TEXT_ALIGN_RIGHT,'center':fitz.TEXT_ALIGN_CENTER}.get(field.get('align'),fitz.TEXT_ALIGN_LEFT),
                                   lineheight=1.05,overlay=True)
    if available<0:
        msg=f'El campo {field["label"]} no cabe en la etiqueta ({number}/{total})'
        raise LayoutError(msg)


def _paint_status_r7b(page, source, asset, target, material, status, test_mode, warnings):
    """Render a verified R7A revision with its own page/crop/field positions."""
    from .status_combined import field_values
    layout = asset["r7b_layout"]
    if status.get('composition') is not None or layout['contract']==2:
        from .status_scaling import paint, describe
        data=field_values(layout,material,status,strict=not test_mode)
        try:
            report=paint(page,source,layout,data,target,settings=status.get('composition'),
                         strict=not test_mode,allow_mini=material.get('_mini_mode',False),
                         default_color=(1,1,1) if asset['kind']=='rechazado' else (0,0,0))
        except ValueError as exc:raise LayoutError(str(exc)) from exc
        warnings.extend(report['warnings'])
        material.setdefault('_composition_reports',[]).append(report)
        return
    crop = fitz.Rect(layout["crop"])
    if not all(math.isfinite(v) for v in target) or target.is_empty:
        raise LayoutError("Área de etiqueta de estado inválida.")
    factor = min(target.width / crop.width, target.height / crop.height)
    if factor <= 0:
        raise LayoutError("La etiqueta de estado no cabe en su zona.")
    width, height = crop.width * factor, crop.height * factor
    rect = fitz.Rect(
        target.x0 + (target.width - width) / 2,
        target.y0 + (target.height - height) / 2,
        target.x0 + (target.width + width) / 2,
        target.y0 + (target.height + height) / 2,
    )
    try:
        data = field_values(layout, material, status, strict=not test_mode)
    except ValueError as err:
        raise LayoutError(str(err)) from err
    # Never erase printed content or invent fixed text. Preserve original
    # vector artwork and exact source crop selected in R7A.
    page.show_pdf_page(rect, source, layout["page"], clip=crop, overlay=True,
                       keep_proportion=True)
    for field in layout["fields"]:
        text = data[field["key"]]
        if not text:
            continue
        box = fitz.Rect(field["rect"])
        size = field["font_size"] * factor
        if size < 6:
            message = "Campo de estado demasiado pequeño (" + field["label"] + "): compruebe la legibilidad física al 100 %."
            if not test_mode and not material.get('_mini_mode',False):
                raise LayoutError(message)
            warnings.append(message)
        x = rect.x0 + (box.x0 - crop.x0) * factor
        y = rect.y0 + (box.y0 - crop.y0) * factor
        # R8-RC3B/3C already measure the real glyph ink in independent
        # state emission. The combined/integrated R7B route must apply that
        # SAME guard, rather than the obsolete 1.2-em height heuristic.
        # Keep the approved font, size, field and source design unchanged.
        from .status_scaling import draw_legacy_field
        color = (1, 1, 1) if asset["kind"] == "rechazado" else (0, 0, 0)
        try:
            draw_legacy_field(page, text,
                              fitz.Rect(x, y, x + box.width * factor,
                                        y + box.height * factor),
                              size, field["bold"], field["label"], color)
        except ValueError as exc:
            raise LayoutError(str(exc)) from exc


def _paint_status(page,status_source,status_master,view_rect,values,status,font_regular,font_bold,warnings,test_mode):
    """Vector-copy the EXACT three colored Word designs, then fill variable spaces."""
    if isinstance(status_master, dict) and status_master.get("r7b_uid"):
        return _paint_status_r7b(page,status_source,status_master,view_rect,values,status,test_mode,warnings)
    if status.get('composition') is not None:
        from .status_scaling import geometry, critical_losses
        crop=fitz.Rect(_loaded_json(status_master['crop_json'],[]))
        report=geometry(crop,view_rect,status['composition'])
        if 8.2*report['scale']<6:
            message='Estado histórico demasiado pequeño tras la composición; comprobar legibilidad física al 100 %.'
            if not test_mode and not values.get('_mini_mode',False):raise LayoutError(message)
            warnings.append(message)
        with fitz.open() as composed:
            layer=composed.new_page(width=status_source[0].rect.width,height=status_source[0].rect.height)
            if font_regular:
                layer.insert_font(fontname='CovexRegular',fontfile=font_regular)
                layer.insert_font(fontname='CovexBold',fontfile=font_bold)
            original=dict(status);original.pop('composition')
            _paint_status(layer,status_source,status_master,crop,values,original,font_regular,font_bold,warnings,test_mode)
            if report['mode']=='fill' and critical_losses(layer,{'crop':list(crop),'fields':[]},report['source_clip']):
                raise LayoutError('Relleno bloqueado: recorta texto o límites del maestro histórico. Use Ajustar o prepare una revisión de estado.')
            page.show_pdf_page(fitz.Rect(report['placed']),composed,0,clip=fitz.Rect(report['source_clip']),keep_proportion=True)
        values.setdefault('_composition_reports',[]).append(report)
        return
    from .geometry import STATUS_COLORS
    kind=status['kind'];source_crop=fitz.Rect(*_loaded_json(status_master['crop_json'],[]))
    # Keep the natural aspect ratio to avoid silently deforming an approved design.
    ratio=source_crop.width/source_crop.height
    factor=min(view_rect.width/source_crop.width,view_rect.height/source_crop.height)
    if 8.2*factor<6:
        msg=f'Texto pequeño en etiqueta de estado ({8.2*factor:.1f} pt): revise el tamaño.'
        if not test_mode and not values.get('_mini_mode',False):raise LayoutError(msg)
        warnings.append(msg)
    ww,hh=source_crop.width*factor,source_crop.height*factor
    dest=fitz.Rect(view_rect.x0+(view_rect.width-ww)/2,view_rect.y0+(view_rect.height-hh)/2,
                   view_rect.x0+(view_rect.width+ww)/2,view_rect.y0+(view_rect.height+hh)/2)
    page.show_pdf_page(dest,status_source,0,clip=source_crop,overlay=True,keep_proportion=True)
    color=STATUS_COLORS[kind]
    font_color=(0,0,0) if kind!='rechazado' else (1,1,1)
    def xy(sx,sy):return fitz.Point(dest.x0+(sx-source_crop.x0)*factor,dest.y0+(sy-source_crop.y0)*factor)
    def erase(bbox):
        a,b,c,d=bbox
        page.draw_rect(fitz.Rect(xy(a,b),xy(c,d)),color=None,fill=color,overlay=True)
    def write(x,y,txt,size=13,bold=True,right_bound=None):
        if not txt:return
        path=font_bold if bold else font_regular
        fn=('CovexBold' if bold else 'CovexRegular') if font_regular else ('hebo' if bold else 'helv')
        fs=size*factor
        tw=_font(path,txt,fs)
        if right_bound and tw>(right_bound-x)*factor:
            msg='El dato de estado excede el área prevista: '+txt[:32]
            raise LayoutError(msg)
        font=fitz.Font(fontfile=path) if path else fitz.Font(fontname='hebo' if bold else 'helv')
        # Baseline is constrained by real font metrics, including fallback fonts.
        y=min(y,source_crop.y1-abs(font.descender)*size-.5)
        page.insert_text(xy(x,y),txt,fontname=fn,fontsize=fs,color=font_color,overlay=True)
    lot=values.get('lote','').strip()
    prefix=''
    for f in _loaded_json(values.get('_fields_json','[]'),[]):
        if f.get('key')=='lote':prefix=f.get('strip_prefix','');break
    lot=normalized_lot(lot,prefix) if lot else ''
    fecha=str(status.get('fecha','')).strip()
    persona=str(status.get('persona','')).strip()
    expiry=str(status.get('caducidad_reanalisis','')).strip()
    if kind=='aprobado':
        erase((87.7,281.5,128,298.0))
        write(88.9,297.0,lot,17.5,right_bound=387)
        write(435,241.8,fecha,9.8,False,right_bound=516)
        write(394,296,persona,12.0,right_bound=516)
        write(237,308.2,expiry,8.2,False,right_bound=389)
    elif kind=='sin_analizar':
        erase((87.7,145.5,127.8,161.0))
        write(88.9,158.4,lot,17.5,right_bound=387)
        write(434.3,107.7,fecha,9.8,False,right_bound=516)
        # 'Pendiente análisis:' is fixed text, no imaginary approval/signature added.
    elif kind=='rechazado':
        write(435,362.0,fecha,9.8,False,right_bound=516)
        write(394,417,persona,12.0,right_bound=516)


def _status_settings(status,status_master,root,version,test_mode):
    from .storage import sha256
    status=status or {}
    kind=status.get('kind','ninguna')
    if kind=='ninguna':return None,None,None
    from .geometry import STATUS_CROPS
    if kind not in STATUS_CROPS:raise LayoutError('Tipo de estado no reconocido.')
    if status_master is None or status_master['kind']!=kind:
        raise LayoutError('No existe la versión maestra de esa etiqueta de estado.')
    if not test_mode and status_master['state']!='APPROVED':
        raise LayoutError('La etiqueta de estado está pendiente de comprobación documental: solo PDF de prueba.')
    pdf=Path(root)/status_master['master_pdf'];source=Path(root)/status_master['original_file']
    if not pdf.exists() or sha256(pdf)!=status_master['pdf_sha256'] or not source.exists() or sha256(source)!=status_master['source_sha256']:
        raise LayoutError('Integridad comprometida en la etiqueta de estado.')
    placement=status.get('placement','integrada')
    if placement not in ('integrada','independiente'):
        raise LayoutError('Posición de estado no reconocida.')
    area=_loaded_json(version['status_area_json'],[]) if 'status_area_json' in version.keys() else []
    if placement=='integrada' and (len(area)!=4 or min(area[2:])<=0):
        raise LayoutError('Esta plantilla no tiene zona de estado configurada. Revísela en el editor.')
    if placement=='integrada' and (min(area[:2])<0 or area[0]+area[2]>1.001 or area[1]+area[3]>1.001):
        raise LayoutError('La zona de estado queda fuera de la etiqueta principal.')
    fecha=str(status.get('fecha','')).strip()
    if fecha:
        try:
            parsed=datetime.strptime(fecha,'%d/%m/%Y')
            if parsed.strftime('%d/%m/%Y')!=fecha:raise ValueError()
        except ValueError:
            raise LayoutError('Fecha de estado inválida. Utilice DD/MM/AAAA y una fecha real.') from None
    if not test_mode and not (isinstance(status_master,dict) and status_master.get('r7b_uid')) and not str(status.get('fecha','')).strip():
        raise LayoutError('La fecha de la etiqueta de estado es obligatoria.')
    return fitz.open(pdf),area,placement


def check_rendered_bounds(page, view, previous_spans, safety_mm=0):
    """Verify actual variable glyphs, including baseline ascenders/descenders."""
    safety=float(safety_mm)*MM
    if not math.isfinite(safety) or safety<0 or safety*2>=min(view.width,view.height):
        raise LayoutError('Zona de seguridad inválida para el tamaño elegido.')
    safe=fitz.Rect(view.x0+safety,view.y0+safety,view.x1-safety,view.y1-safety)
    spans=[]
    for b in page.get_text('dict')['blocks']:
        for line in b.get('lines',[]):spans.extend(line['spans'])
    for span in spans:
        signature=(span['text'],tuple(span['bbox']))
        if signature in previous_spans:continue
        box=fitz.Rect(span['bbox'])
        if not safe.contains(box):
            raise LayoutError('Texto fuera de los límites o zona de seguridad: '+span['text'])


def span_count(page):
    return {(span['text'],tuple(span['bbox'])) for b in page.get_text('dict')['blocks'] for line in b.get('lines',[]) for span in line['spans']}


def render_emission(version,root,values,profile,indices,count_containers,copies_per_container,
                    destination,test_mode=False,per_container=None,status=None,status_master=None):
    """A4 output from untouched Word master + per-vessel data + original status overlays.

    TEST prints are watermarked. The existence of a stored PDF does not certify
    that its physical printing or a QA material disposition actually occurred.
    """
    from .storage import sha256
    if not indices:raise LayoutError('No se han seleccionado recipientes.')
    if profile.get('trial_appearance') is not None:
        if not test_mode:
            raise LayoutError('Ajustes temporales de PRUEBA: restaure el diseño o cree una variante documental antes de emitir.')
        from .typography import apply_trial
        version=apply_trial(version,profile['trial_appearance'])
    if any(not isinstance(i,int) or i<1 or i>count_containers for i in indices):
        raise LayoutError('Numeración fuera del intervalo definido.')
    if copies_per_container not in (1,2):raise LayoutError('Solo se permiten una o dos etiquetas por recipiente.')
    if len(indices)!=len(set(indices)):raise LayoutError('Hay números de envase repetidos.')
    physical=[i for i in indices for _ in range(copies_per_container)]
    plan=plan_sheet(profile,len(physical))
    if not test_mode and version['state']!='APPROVED':
        raise LayoutError('El máster está pendiente de aprobación documental. Solo PDF de prueba.')
    source_path=Path(root)/version['master_pdf']
    if sha256(source_path)!=version['pdf_sha256']:
        raise LayoutError('Integridad comprometida: el PDF maestro no coincide con el original registrado.')
    if version['original_file']:
        original_path=Path(root)/version['original_file']
        if not original_path.exists() or sha256(original_path)!=version['source_sha256']:
            raise LayoutError('Integridad comprometida: el Word original ha cambiado.')
    per_container={str(k):v for k,v in (per_container or {}).items()}
    for k,v in per_container.items():
        if not k.isdecimal() or not (1<=int(k)<=count_containers) or not isinstance(v,dict):
            raise LayoutError('Tabla individual de envases inválida.')
    orig=fitz.open(source_path)
    if orig.page_count<1:raise LayoutError('El PDF maestro no contiene páginas.')
    crop=fitz.Rect(*_loaded_json(version['crop_json'],[]))
    if crop not in orig[0].rect:raise LayoutError('Recorte fuera del PDF original.')
    fields=_loaded_json(version['fields_json'],[])
    from .integrity import verify_renderable
    try:verify_renderable(version)
    except ValueError as error:raise LayoutError(str(error)) from error
    status_doc,status_area,placement=_status_settings(status,status_master,root,version,test_mode)
    rootfont,boldfont=_fonts()
    out=fitz.open()
    width_mm=float(profile['width_mm']);height_mm=float(profile['height_mm'])
    margin=float(profile.get('margin_mm',8));gap=float(profile.get('gap_mm',3))
    ox=float(profile.get('offset_x_mm',0));oy=float(profile.get('offset_y_mm',0))
    start=int(profile.get('start_slot',1))
    aspect=crop.width/crop.height
    status_crop=fitz.Rect(*_loaded_json(status_master['crop_json'],[])) if status_doc else None
    base_crop=status_crop if placement=='independiente' else crop
    aspect=base_crop.width/base_crop.height
    from .sheet_layout import slots, physical_placements
    boxes=slots(profile,plan.cols,plan.rows)
    issues=[];composition_reports=[]
    for (page_index,slot),number in zip(physical_placements(profile,plan.capacity,len(physical)),physical):
        if page_index>=len(out):
            page=out.new_page(width=plan.paper_w_mm*MM,height=plan.paper_h_mm*MM)
            if rootfont:
                page.insert_font(fontname='CovexRegular',fontfile=rootfont)
                page.insert_font(fontname='CovexBold',fontfile=boldfont)
            if test_mode and placement=='independiente':
                page.insert_text((2,10),'PRUEBA - NO APTO PARA USO GMP',fontsize=7,
                                 fontname='helv',color=(.86,.12,.15),overlay=True)
        else:page=out[-1]
        box=boxes[slot]; width_mm=box.width; height_mm=box.height
        xslot=box.x*MM; yslot=box.y*MM
        if width_mm/height_mm>aspect:
            draw_h=height_mm*MM;draw_w=draw_h*aspect
        else:
            draw_w=width_mm*MM;draw_h=draw_w/aspect
        fit_scale=draw_w/base_crop.width
        if xslot<0 or yslot<0 or xslot+width_mm*MM>page.rect.width+.01 or yslot+height_mm*MM>page.rect.height+.01:
            raise LayoutError('La calibración desplaza una etiqueta fuera de la hoja.')
        view=fitz.Rect(xslot+(width_mm*MM-draw_w)/2,yslot+(height_mm*MM-draw_h)/2,
                       xslot+(width_mm*MM+draw_w)/2,yslot+(height_mm*MM+draw_h)/2)
        if profile.get('crop_marks'):
            page.draw_rect(fitz.Rect(xslot,yslot,xslot+width_mm*MM,yslot+height_mm*MM),
                            color=(.60,.69,.79),width=.45,overlay=True)
        item=dict(values);item.update(per_container.get(str(number),{}))
        for field in fields:
            if field.get('key')=='lote' and field.get('strip_prefix'):
                item['lote']=normalized_lot(item.get('lote',''),field['strip_prefix'])
        from .vessels import validate_vessel_masses
        try:validate_vessel_masses(item,number)
        except ValueError as ex:raise LayoutError(str(ex)) from ex
        item['_label_scale']=fit_scale
        item['_mini_mode']=bool(profile.get('mini_mode',False))
        item['_fields_json']=fields
        item['_label_name']=version['name']
        item['_crop_x0']=crop.x0
        item['_crop_width']=crop.width
        if placement!='independiente':
            page.show_pdf_page(view,orig,0,clip=crop,overlay=True,keep_proportion=True)
            warn=validate_fields(version,item,{**profile,'width_mm':width_mm,'height_mm':height_mm},strict=False)
            blocking=blocking_render_warnings(warn,profile)
            if blocking and not test_mode:raise LayoutError('; '.join(blocking))
            issues.extend(warn)
            before_spans=span_count(page)
            for f in fields:
                if 'typography' in f:
                    from .typography import contrast_warning
                    x=crop.x0+f['x']*crop.width;y=crop.y0+f['y']*crop.height
                    # Baseline fields have no ordinary box above the anchor;
                    # decline a contrast claim rather than sample the wrong area.
                    if f.get('draw') not in ('baseline','continuation'):
                        message=contrast_warning(orig[0],fitz.Rect(x,y,x+f['w']*crop.width,y+f['h']*crop.height),f['typography']['color'])
                        if message:
                            if not test_mode:raise LayoutError(f['label']+': '+message)
                            issues.append(f['label']+': '+message)
                _overlay_field(page,f,item,number,count_containers,view,rootfont,boldfont,issues,test_mode)
            check_rendered_bounds(page,view,before_spans,profile.get('safety_mm',0))
        if status_doc:
            if not test_mode and status['kind'] in ('sin_analizar','aprobado') and not item.get('lote','').strip():
                raise LayoutError('El estado de un material necesita su identificación de lote.')
            # Independent explicit composition fills/fits the selected physical
            # slot, not the already proportionally fitted historical view.
            place=fitz.Rect(xslot,yslot,xslot+width_mm*MM,yslot+height_mm*MM) if placement=='independiente' and (status or {}).get('composition') else view
            if placement=='integrada':
                sx,sy,sw,sh=map(float,status_area)
                place=fitz.Rect(view.x0+view.width*sx,view.y0+view.height*sy,
                                view.x0+view.width*(sx+sw),view.y0+view.height*(sy+sh))
            before_status=span_count(page)
            _paint_status(page,status_doc,status_master,place,item,status,rootfont,boldfont,issues,test_mode)
            composition_reports.extend(item.get('_composition_reports',[]))
            # Include the integrated status variables in the label-boundary check.
            check_rendered_bounds(page,place if placement=='independiente' and (status or {}).get('composition') else view,before_status,profile.get('safety_mm',0))
        if test_mode:
            page.draw_rect(fitz.Rect(xslot,yslot,xslot+width_mm*MM,yslot+height_mm*MM),
                color=(.78,.27,.27),width=.6,overlay=True)
            if placement!='independiente':
                page.insert_text((xslot+2,yslot+10),'PRUEBA - NO APTO PARA USO GMP',fontsize=7,
                    fontname='helv',color=(.86,.12,.15),overlay=True)
    target=Path(destination);target.parent.mkdir(parents=True,exist_ok=True)
    out.set_metadata({'title':'COVEX Label Manager - '+('PRUEBA' if test_mode else 'Emisión'),
                      'subject':f'{count_containers} recipientes, {copies_per_container} copias; estado={(status or {}).get("kind","ninguna")}',
                      'creator':'COVEX Label Manager '+__import__('covex_label_manager').__version__})
    out.save(target,garbage=4,deflate=True)
    out.close();orig.close()
    if status_doc:status_doc.close()
    result={'pages':plan.pages,'per_page':plan.capacity,'physical':len(physical),
            'warnings':sorted(set(issues)),'path':str(target)}
    if composition_reports:result['composition']=composition_reports
    return result


def render_label_thumbnail(version,root,values=None,number=1,total=1,width_px=500):
    crop=fitz.Rect(*json.loads(version['crop_json']))
    d=fitz.open(Path(root)/version['master_pdf'])
    page=d[0]
    clip=crop
    scale=min(2,width_px/clip.width)
    pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),clip=clip,alpha=False)
    from PIL import Image
    im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    d.close()
    return im


def preview_pdf(path, maxwidth=630):
    from PIL import Image
    doc=fitz.open(path)
    p=doc[0]
    scale=maxwidth/p.rect.width
    pix=p.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
    img=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    count=doc.page_count
    doc.close()
    return img,count


def render_calibration_page(profile,destination):
    """Generate a 100% scale test sheet; never a production label."""
    plan=plan_sheet(profile,1)
    m=float(profile.get('margin_mm',8));gap=float(profile.get('gap_mm',3))
    w=float(profile['width_mm']);h=float(profile['height_mm'])
    ox=float(profile.get('offset_x_mm',0));oy=float(profile.get('offset_y_mm',0))
    d=fitz.open()
    p=d.new_page(width=plan.paper_w_mm*MM,height=plan.paper_h_mm*MM)
    from .sheet_layout import slots
    for index,box in enumerate(slots(profile,plan.cols,plan.rows)):
        w,h=box.width,box.height;x=box.x*MM;y=box.y*MM
        rect=fitz.Rect(x,y,x+w*MM,y+h*MM)
        if rect not in p.rect:
            d.close();raise LayoutError('La calibracion desplaza casillas fuera del papel.')
        p.draw_rect(rect,color=(.24,.41,.63),width=.9,dashes='[5 3] 0')
        txt=f'POS. {index+1}  |  {w:g} x {h:g} mm'
        p.insert_text((x+8,y+15),txt,fontsize=8,color=(.11,.29,.48))
        p.draw_line((x-4,y),(x+4,y),color=(.82,.24,.24),width=.6)
        p.draw_line((x,y-4),(x,y+4),color=(.82,.24,.24),width=.6)
        p.draw_line((x+w*MM-4,y+h*MM),(x+w*MM+4,y+h*MM),color=(.82,.24,.24),width=.6)
        p.draw_line((x+w*MM,y+h*MM-4),(x+w*MM,y+h*MM+4),color=(.82,.24,.24),width=.6)
    # The reference ruler is visible when the margin accommodates it.
    ry=p.rect.height-10
    p.draw_line((18,ry),(18+50*MM,ry),color=(0,0,0),width=1)
    for mm in (0,25,50):
        x=18+mm*MM
        p.draw_line((x,ry-5),(x,ry+3),color=(0,0,0),width=.8)
    p.insert_text((18,ry-8),'Regla de referencia 50 mm | imprimir al 100%',fontsize=6.5)
    d.set_metadata({'title':'COVEX - HOJA DE CALIBRACION - NO PRODUCTIVA','creator':'COVEX Label Manager'})
    dest=Path(destination);dest.parent.mkdir(parents=True,exist_ok=True)
    d.save(dest,deflate=True,garbage=4);d.close()
    return str(dest)
