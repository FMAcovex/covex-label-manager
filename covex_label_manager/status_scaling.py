"""R8C uniform source-space composition, with conservative crop protection."""
import math
import fitz

DEFAULT = dict(contract=1, mode='fit', align_x='center', align_y='middle')


def validate(settings):
    if (not isinstance(settings, dict) or set(settings) != set(DEFAULT)
            or type(settings.get('contract')) is not int or settings['contract'] != 1
            or settings['mode'] not in ('fit','fill')
            or settings['align_x'] not in ('left','center','right')
            or settings['align_y'] not in ('top','middle','bottom')):
        raise ValueError('Contrato de composición de estado no reconocido.')
    return dict(settings)


def geometry(crop, target, settings=None):
    settings = validate(DEFAULT if settings is None else settings)
    crop, target = fitz.Rect(crop), fitz.Rect(target)
    if crop.is_empty or target.is_empty or not all(math.isfinite(v) for v in (*crop,*target)):
        raise ValueError('Área de composición inválida.')
    fill = settings['mode']=='fill'
    factor = (max if fill else min)(target.width/crop.width,target.height/crop.height)
    ax = {'left':0,'center':.5,'right':1}[settings['align_x']]
    ay = {'top':0,'middle':.5,'bottom':1}[settings['align_y']]
    if fill:
        width, height = target.width/factor, target.height/factor
        x, y = crop.x0+(crop.width-width)*ax, crop.y0+(crop.height-height)*ay
        clip = fitz.Rect(x,y,x+width,y+height); placed = target
    else:
        width, height = crop.width*factor,crop.height*factor
        x, y = target.x0+(target.width-width)*ax,target.y0+(target.height-height)*ay
        clip = crop; placed = fitz.Rect(x,y,x+width,y+height)
    return dict(mode=settings['mode'], scale=factor, source_clip=list(clip),
                target=list(target), placed=list(placed),
                effective_mm=[placed.width*25.4/72,placed.height*25.4/72],
                free_mm=[(target.width-placed.width)*25.4/72,(target.height-placed.height)*25.4/72],
                cropped_mm=[(crop.width-clip.width)*25.4/72,(crop.height-clip.height)*25.4/72])


def _contains(outer, inner):
    outer,inner=fitz.Rect(outer),fitz.Rect(inner)
    return (outer.x0-.02<=inner.x0 and outer.y0-.02<=inner.y0
            and outer.x1+.02>=inner.x1 and outer.y1+.02>=inner.y1)


def critical_losses(source_page, layout, clip):
    crop=fitz.Rect(layout['crop']); losses=[]
    def check(box,name):
        box=fitz.Rect(box)&crop
        if not box.is_empty and not _contains(clip,box):
            losses.append(dict(content=name, rect=list(box)))
    for block in source_page.get_text('dict')['blocks']:
        if block.get('type')==1:
            check(block['bbox'],'imagen / símbolo')
        for line in block.get('lines',[]):
            for span in line['spans']:
                # PDF extraction boxes can omit italic overhangs. Reserve an
                # em around fixed text conservatively; never authorize a cut
                # tangent to a glyph merely because advance widths fit.
                box=fitz.Rect(span['bbox']);pad=span['size']
                check(fitz.Rect(box.x0-pad,box.y0-pad,box.x1+pad,box.y1+pad),
                      'texto fijo: '+span['text'][:60])
    for drawing in source_page.get_drawings():
        rect=fitz.Rect(drawing['rect'])
        # Ignore only a single solid, axis-aligned rectangle enclosing the crop,
        # with NO stroked edge. Lines/borders/logos remain critical.
        background=(drawing.get('type')=='f' and drawing.get('fill') is not None
                    and len(drawing['items'])==1 and drawing['items'][0][0]=='re'
                    and _contains(rect,crop))
        if not background:
            # Zero-height/width lines still carry critical geometry.
            pad=max(.05,float(drawing.get('width') or 0)/2)
            check(fitz.Rect(rect.x0-pad,rect.y0-pad,rect.x1+pad,rect.y1+pad),'trazo / límite / símbolo')
    for field in layout['fields']:
        check(field['rect'],'campo variable: '+field['label'])
    return losses


def paint(page, source, layout, values, target, *, settings=None, strict=True,
          default_color=(0,0,0)):
    """Compose in source points THEN transform background and fields together."""
    from .typography import paint as paint_text, contrast_warning
    report=geometry(layout['crop'],target,settings)
    source_page=source[layout['page']]
    losses=critical_losses(source_page,layout,report['source_clip']) if report['mode']=='fill' else []
    report['critical_losses']=losses
    if losses:
        details='; '.join(item['content'] for item in losses[:4])
        raise ValueError('Relleno bloqueado: se recortaría contenido crítico ('+details+'). Use Ajustar sin deformar, amplíe el área o prepare una variante documental.')
    crop=fitz.Rect(layout['crop']); warnings=[]
    visible=fitz.Rect(report['source_clip'])
    for block in source_page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            for span in line['spans']:
                if span['text'].strip() and not (fitz.Rect(span['bbox'])&visible).is_empty and span['size']*report['scale']<6:
                    message=f"Texto fijo demasiado pequeño ({span['size']*report['scale']:.2f} pt): "+span['text'][:60]+'. Amplíe el área o prepare una revisión de origen.'
                    if strict:raise ValueError(message)
                    warnings.append(message)
    with fitz.open() as composed:
        layer=composed.new_page(width=source_page.rect.width,height=source_page.rect.height)
        layer.show_pdf_page(layer.rect,source,layout['page'])
        for field in layout['fields']:
            text=values.get(field['key'],'')
            if not text:continue
            rect=fitz.Rect(field['rect']); size=field['font_size']
            if 'typography' in field:
                warning=contrast_warning(source_page,rect,field['typography']['color'])
                if warning:
                    if strict:raise ValueError(field['label']+': '+warning)
                    warnings.append(field['label']+': '+warning)
                # The layer is in source points. Minimum legibility is checked
                # below in FINAL physical points, not before scaling.
                warnings.extend(paint_text(layer,text,rect,size,field['bold'],field['typography'],strict=False,check_minimum=False))
            else:
                # Explicit composition may be used with an old layout: preserve
                # the historical source baseline/font/color and block overflow.
                font='hebo' if field['bold'] else 'helv'
                if size*1.2>rect.height or fitz.get_text_length(text,fontname=font,fontsize=size)>rect.width-2:
                    raise ValueError('El dato excede el campo de estado '+field['label']+'.')
                layer.insert_text((rect.x0+1,rect.y0+size*1.1),text,fontname=font,fontsize=size,color=default_color)
            if size*report['scale']<6:
                message=field['label']+f": texto final demasiado pequeño ({size*report['scale']:.2f} pt); mínimo 6 pt."
                if strict:raise ValueError(message)
                warnings.append(message)
        # Also check actual new glyphs against their SOURCE boxes before crop.
        # The typography renderer has already measured its full ascent/descent.
        page.show_pdf_page(fitz.Rect(report['placed']),composed,0,clip=fitz.Rect(report['source_clip']),keep_proportion=True)
    report['warnings']=sorted(set(warnings))
    return report


def describe(report):
    free=report['free_mm']; cut=report['cropped_mm']; size=report['effective_mm']
    return (('Rellenar el área' if report['mode']=='fill' else 'Ajustar sin deformar')+
            f" · {size[0]:.2f} × {size[1]:.2f} mm · escala {report['scale']*100:.1f} %"+
            (f' · margen libre total {free[0]:.2f} × {free[1]:.2f} mm' if max(free)>.01 else '')+
            (f' · recorte del original {cut[0]:.2f} × {cut[1]:.2f} mm (sólo fondo no crítico)' if max(cut)>.01 else ''))
