"""Versioned millimetre geometry shared by native canvas and PDF renderer.

Profiles without layout_version retain the historical grid arithmetic.
"""
import math
from dataclasses import dataclass

PAPERS={'A4':(210.,297.),'A3':(297.,420.),'A5':(148.,210.),'Carta':(215.9,279.4)}

@dataclass(frozen=True)
class LayoutSlot:
    x:float
    y:float
    width:float
    height:float


def number(value):
    result=float(value)
    if not math.isfinite(result):raise ValueError('Medida no finita.')
    return result


def paper_size(profile):
    paper=profile.get('paper','A4'); orientation=profile.get('orientation','portrait')
    if orientation not in ('portrait','landscape'):raise ValueError('Orientación desconocida.')
    if paper=='custom':
        size=tuple(number(profile[k]) for k in ('paper_width_mm','paper_height_mm'))
        if not all(50<=v<=1000 for v in size):raise ValueError('Papel personalizado: 50–1000 mm por lado.')
    elif paper in PAPERS:size=PAPERS[paper]
    else:raise ValueError('Formato de papel no soportado.')
    return size if orientation=='portrait' else size[::-1]


def validate_profile(profile):
    if 'layout_version' in profile and (type(profile['layout_version']) is not int or profile['layout_version']!=1):raise ValueError('Versión de distribución no soportada.')
    mode=profile.get('layout_mode','grid')
    if mode not in ('grid','free'):raise ValueError('Modo de distribución desconocido.')
    if (mode!='grid' or profile.get('paper','A4')!='A4') and profile.get('layout_version')!=1:raise ValueError('Distribución nueva sin versión.')
    paper_size(profile)
    for k in ('width_mm','height_mm','margin_mm','gap_mm','offset_x_mm','offset_y_mm','safety_mm'):
        if k in profile:number(profile[k])
    if number(profile.get('safety_mm',0))<0:raise ValueError('Seguridad negativa.')
    return mode


def slots(profile, cols=0, rows=0):
    mode=validate_profile(profile); pw,ph=paper_size(profile)
    m=number(profile.get('margin_mm',8)); ox=number(profile.get('offset_x_mm',0));oy=number(profile.get('offset_y_mm',0))
    if mode=='free':
        raw=profile.get('slots')
        if not isinstance(raw,list) or not 1<=len(raw)<=1000:raise ValueError('Defina entre 1 y 1000 posiciones.')
        result=[]
        for s in raw:
            if not isinstance(s,dict) or set(s)!={'x','y','width','height'}:raise ValueError('Posición inválida.')
            x,y,w,h=(number(s[k]) for k in ('x','y','width','height'))
            result.append(LayoutSlot(x+ox,y+oy,w,h))
    else:
        w=number(profile['width_mm']);h=number(profile['height_mm']);g=number(profile.get('gap_mm',3))
        if not cols:cols=math.floor((pw-2*m+g+1e-9)/(w+g));rows=math.floor((ph-2*m+g+1e-9)/(h+g))
        result=[LayoutSlot(m+c*(w+g)+ox,m+r*(h+g)+oy,w,h) for r in range(rows) for c in range(cols)]
    if not 0<=m<=40:raise ValueError('Margen: 0–40 mm.')
    for i,s in enumerate(result):
        # Legacy offsets used the paper boundary. Versioned profiles use printable margins.
        # An explicitly calibrated profile can require a small mechanical
        # shift inside the usual design margin. Keep the paper boundary strict.
        # plan_sheet() checks calibration integrity before calling slots().
        edge=m if profile.get('layout_version') and not profile.get('printer_calibration') else 0
        if min(s.width,s.height)<10 or s.x<edge-1e-8 or s.y<edge-1e-8 or s.x+s.width>pw-edge+1e-8 or s.y+s.height>ph-edge+1e-8:raise ValueError(f'Posición {i+1} fuera de límites o margen (mínimo 10 mm).')
        if mode=='free':
            for other in result[:i]:
                if min(s.x+s.width,other.x+other.width)-max(s.x,other.x)>1e-8 and min(s.y+s.height,other.y+other.height)-max(s.y,other.y)>1e-8:raise ValueError(f'Solapamiento en posición {i+1}.')
    return result


def template(profile,count):
    """Exactly count ordered boxes; never alters vessel count or copies."""
    from dataclasses import asdict
    if not 1<=count<=1000:raise ValueError('Número de posiciones inválido.')
    pw,ph=paper_size(profile);m=number(profile.get('margin_mm',8));g=number(profile.get('gap_mm',3))
    cols=max(1,math.ceil(math.sqrt(count*pw/ph)));rows=math.ceil(count/cols)
    w=(pw-2*m-(cols-1)*g)/cols;h=(ph-2*m-(rows-1)*g)/rows
    return [asdict(LayoutSlot(m+(i%cols)*(w+g),m+(i//cols)*(h+g),w,h)) for i in range(count)]


def available_first_page(profile,capacity):
    """Zero-based printable slots on sheet one. Other sheets remain pristine.

    Existing profiles without occupied_slots use precisely the old ordering.
    """
    start=profile.get('start_slot',1)
    if type(start) is not int or not 1<=start<=capacity:
        raise ValueError(f'La casilla inicial debe estar entre 1 y {capacity}.')
    raw=profile.get('occupied_slots',[])
    if type(raw) is not list:
        raise ValueError('Las casillas utilizadas deben ser una lista.')
    if raw and profile.get('layout_version')!=1:
        raise ValueError('Casillas utilizadas requieren el diseñador Qt versionado.')
    if any(type(v) is not int or not 1<=v<=capacity for v in raw):
        raise ValueError('Casilla utilizada fuera del número de posiciones de la hoja.')
    if len(raw)!=len(set(raw)):
        raise ValueError('Hay casillas utilizadas repetidas.')
    occupied=set(raw)
    result=[i for i in range(start-1,capacity) if i+1 not in occupied]
    if not result:
        raise ValueError('La primera hoja no tiene casillas libres. Use una hoja nueva o desmarque una posición.')
    return result


def physical_placements(profile,capacity,count):
    """(page number, zero-based slot): first sheet skips only marked positions."""
    first=available_first_page(profile,capacity)
    for index in range(count):
        if index<len(first):
            yield 0,first[index]
        else:
            following=index-len(first)
            yield 1+following//capacity,following%capacity


def require_legacy(profile):
    if profile.get('occupied_slots') or profile.get('layout_version') or profile.get('layout_mode','grid')!='grid' or profile.get('paper','A4')!='A4':raise ValueError('Este formato requiere el Centro de emisión nativo Qt. No se puede abrir en Tkinter.')
