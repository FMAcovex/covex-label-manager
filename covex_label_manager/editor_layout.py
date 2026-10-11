"""Complete pending-design commands; no GUI, database or source-file writes."""
from copy import deepcopy
import json
import math
from .geometry import rebase_layout

MM_PER_POINT = 25.4 / 72


def layout_from_version(version):
    return dict(fields=json.loads(version['fields_json']),
                crop=json.loads(version['crop_json']),
                area=json.loads(version['status_area_json'] or '[]'))


def source_identity(version):
    return {k: version[k] for k in ('uid', 'master_pdf', 'pdf_sha256', 'original_file', 'source_sha256')}


def version_with_layout(version, layout):
    result = dict(version)
    result.update(fields_json=json.dumps(layout['fields']), crop_json=json.dumps(layout['crop']),
                  status_area_json=json.dumps(layout['area']),
                  base_w_mm=(layout['crop'][2]-layout['crop'][0])*MM_PER_POINT,
                  base_h_mm=(layout['crop'][3]-layout['crop'][1])*MM_PER_POINT)
    return result


def numbers(values):
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError('Coordenadas numéricas finitas obligatorias.')


def validate_box(box, title):
    if len(box) != 4:
        raise ValueError('Rectángulo inválido: '+title)
    numbers(box)
    x, y, w, h = box
    if min(x, y) < 0 or min(w, h) <= 0 or x+w > 1.001 or y+h > 1.001:
        raise ValueError('Fuera de los límites: '+title)


def validate_layout(layout, page_rect=None):
    crop = layout['crop']
    if len(crop) != 4:
        raise ValueError('Recorte inválido.')
    numbers(crop)
    x0, y0, x1, y1 = crop
    if min(x0, y0) < 0 or x1 <= x0 or y1 <= y0:
        raise ValueError('Recorte inválido.')
    if page_rect is not None and (x0 < page_rect[0] or y0 < page_rect[1] or
                                  x1 > page_rect[2]+.001 or y1 > page_rect[3]+.001):
        raise ValueError('Recorte fuera del documento de referencia.')
    keys = []
    for f in layout['fields']:
        key = f.get('key', '')
        if not isinstance(key, str) or not key.strip():
            raise ValueError('Identificador de campo obligatorio.')
        keys.append(key.strip())
        validate_box([f[k] for k in ('x', 'y', 'w', 'h')], key)
        numbers([f.get('font_pt', 12)])
        if not 3 <= f.get('font_pt', 12) <= 80:
            raise ValueError('Fuente fuera de intervalo (3–80 pt).')
        if f.get('erase'):
            validate_box(f['erase'], 'borrado '+key)
        if f.get('draw', 'textbox') not in ('textbox', 'baseline', 'continuation', 'paragraph'):
            raise ValueError('Modo de dibujo no reconocido: '+key)
        if 'second_x' in f or 'next_w' in f:
            sx, nw = f.get('second_x', f['x']), f.get('next_w', f['w'])
            numbers([sx, nw])
            if sx < 0 or nw <= 0 or sx+nw > 1.001:
                raise ValueError('Continuación fuera de límites: '+key)
    if len(keys) != len(set(keys)):
        raise ValueError('Identificadores de campo únicos obligatorios.')
    if layout['area']:
        validate_box(layout['area'], 'zona de estado')


def check_locked_changes(before, after):
    """Locked geometry is compared in source PDF points, including crop changes."""
    def absolute(f, crop):
        x0,y0,x1,y1=crop; w=x1-x0; h=y1-y0
        return [x0+f['x']*w,y0+f['y']*h,f['w']*w,f['h']*h]
    candidates={f['key']:f for f in after['fields']}
    for f in before['fields']:
        if not f.get('locked'): continue
        replacement=candidates.get(f['key'])
        if replacement is None:
            raise ValueError('Desbloquee el campo antes de eliminarlo o cambiar su identificador: '+f['key'])
        old=absolute(f,before['crop']); new=absolute(replacement,after['crop'])
        if any(abs(a-b)>1e-5 for a,b in zip(old,new)):
            raise ValueError('La geometría del campo está bloqueada: '+f['key'])
        for key in ('erase','second_x','next_w'):
            if key=='erase':
                old=f.get(key); new=replacement.get(key)
                if bool(old)!=bool(new): raise ValueError('Zona de borrado bloqueada: '+f['key'])
                if old:
                    a=absolute(dict(zip(('x','y','w','h'),old)),before['crop'])
                    b=absolute(dict(zip(('x','y','w','h'),new)),after['crop'])
                    if any(abs(x-y)>1e-5 for x,y in zip(a,b)): raise ValueError('Zona de borrado bloqueada: '+f['key'])
            elif key in f:
                old=f[key]*(before['crop'][2]-before['crop'][0])+(before['crop'][0] if key=='second_x' else 0)
                new=replacement.get(key,f[key])*(after['crop'][2]-after['crop'][0])+(after['crop'][0] if key=='second_x' else 0)
                if abs(old-new)>1e-5: raise ValueError('Continuación bloqueada: '+f['key'])


def recrop(layout, crop):
    if crop[2]-crop[0] < 20 or crop[3]-crop[1] < 20:
        raise ValueError('El recorte necesita al menos 20 puntos por lado (7,06 mm).')
    result = deepcopy(layout)
    result['fields'], result['area'] = rebase_layout(layout['fields'], layout['area'], layout['crop'], crop)
    result['crop'] = list(crop)
    validate_layout(result)
    return result


def move_field(field, dx, dy, crop):
    if field.get('locked') and (dx or dy):
        raise ValueError('Campo bloqueado: '+field['key'])
    field['x'] += dx
    field['y'] += dy
    if field.get('erase'):
        field['erase'][0] += dx
        field['erase'][1] += dy
    if 'second_x' in field:
        field['second_x'] += dx
    if field.get('anchor'):
        field['anchor']['dx_pt'] += dx*(crop[2]-crop[0])
        field['anchor']['dy_pt'] += dy*(crop[3]-crop[1])


def align_fields(layout, indices, mode):
    result = deepcopy(layout)
    fields = [result['fields'][i] for i in sorted(set(indices))]
    if len(fields) < (3 if mode.startswith('distribute') else 2):
        raise ValueError('Seleccione al menos '+('tres' if mode.startswith('distribute') else 'dos')+' campos.')
    if any(f.get('locked') for f in fields):
        raise ValueError('Desbloquee los campos seleccionados antes de alinearlos.')
    left = min(f['x'] for f in fields); top = min(f['y'] for f in fields)
    right = max(f['x']+f['w'] for f in fields); bottom = max(f['y']+f['h'] for f in fields)
    if mode.startswith('distribute'):
        axis, size = ('x', 'w') if mode == 'distribute_x' else ('y', 'h')
        fields.sort(key=lambda f: f[axis])
        start = fields[0][axis]; end = fields[-1][axis]+fields[-1][size]
        gap = (end-start-sum(f[size] for f in fields))/(len(fields)-1)
        if gap < 0:
            raise ValueError('No hay espacio para distribuir sin solapamientos.')
        for f in fields:
            move_field(f, start-f['x'] if axis == 'x' else 0,
                       start-f['y'] if axis == 'y' else 0, result['crop'])
            start += f[size]+gap
    else:
        for f in fields:
            dx = {'left': left-f['x'], 'right': right-f['w']-f['x'],
                  'center_x': (left+right-f['w'])/2-f['x']}.get(mode, 0)
            dy = {'top': top-f['y'], 'bottom': bottom-f['h']-f['y'],
                  'center_y': (top+bottom-f['h'])/2-f['y']}.get(mode, 0)
            if mode not in ('left', 'right', 'center_x', 'top', 'bottom', 'center_y'):
                raise ValueError('Alineación no reconocida.')
            move_field(f, dx, dy, result['crop'])
    validate_layout(result)
    return result


def scale_fields(layout, indices, factor, scale_font=True, include_area=False):
    numbers([factor])
    if factor <= 0:
        raise ValueError('Escala positiva obligatoria.')
    result = deepcopy(layout)
    fields = [result['fields'][i] for i in sorted(set(indices))]
    if not fields:
        raise ValueError('Seleccione campos para reajustar.')
    if any(f.get('locked') for f in fields):
        raise ValueError('El reajuste no modifica campos bloqueados.')
    ox = min(f['x'] for f in fields); oy = min(f['y'] for f in fields)
    if include_area and result['area']:
        ox = min(ox, result['area'][0]); oy = min(oy, result['area'][1])
    def box(b):
        x, y, w, h = b
        return [ox+(x-ox)*factor, oy+(y-oy)*factor, w*factor, h*factor]
    for f in fields:
        old_x, old_y = f['x'], f['y']
        f['x'], f['y'], f['w'], f['h'] = box([f[k] for k in ('x', 'y', 'w', 'h')])
        if f.get('erase'): f['erase'] = box(f['erase'])
        if 'second_x' in f: f['second_x'] = ox+(f['second_x']-ox)*factor
        if 'next_w' in f: f['next_w'] *= factor
        if scale_font: f['font_pt'] *= factor
        if f.get('anchor'):
            f['anchor']['dx_pt'] += (f['x']-old_x)*(result['crop'][2]-result['crop'][0])
            f['anchor']['dy_pt'] += (f['y']-old_y)*(result['crop'][3]-result['crop'][1])
    if include_area and result['area']: result['area'] = box(result['area'])
    validate_layout(result)
    return result


def anchor_field(layout, index, span, occurrence, pdf_sha256):
    result = deepcopy(layout); f = result['fields'][index]
    if f.get('locked'): raise ValueError('El campo está bloqueado.')
    c = result['crop']; w = c[2]-c[0]; h = c[3]-c[1]
    x = span['bbox'][2]+1.5; y = span['origin'][1]
    # Preserve auxiliary erase/continuation geometry by translating it atomically.
    move_field(f, (x-c[0])/w-f['x'], (y-c[1])/h-f['y'], c)
    f.update(w=(c[2]-x-4)/w, h=1.5/h, font_pt=float(span['size']),
             draw='baseline', bold='bold' in span.get('font', '').lower())
    f['anchor'] = dict(pdf_sha256=pdf_sha256, page=0, text=span['text'],
                       occurrence=occurrence, bbox=list(span['bbox']), origin=list(span['origin']),
                       dx_pt=1.5, dy_pt=0)
    validate_layout(result)
    return result


def relocate_anchors(layout, spans, pdf_sha256):
    result = deepcopy(layout); count = 0
    for f in result['fields']:
        a = f.get('anchor')
        if not a: continue
        if f.get('locked'): raise ValueError('Ancla bloqueada: '+f['key'])
        if a.get('pdf_sha256') != pdf_sha256 or a.get('page') != 0:
            raise ValueError('La fuente del ancla ha cambiado; vuelva a seleccionarla.')
        candidates = [s for s in spans if s['text'] == a['text'] and
                      all(abs(x-y) < .01 for x,y in zip(s['bbox'], a['bbox']))]
        if len(candidates) != 1:
            raise ValueError('Referencia ausente o ambigua: '+a['text'])
        sp = candidates[0]; c = result['crop']
        dx = (sp['bbox'][2]+a['dx_pt']-c[0])/(c[2]-c[0])-f['x']
        dy = (sp['origin'][1]+a['dy_pt']-c[1])/(c[3]-c[1])-f['y']
        move_field(f, dx, dy, c); count += 1
    if not count: raise ValueError('No hay anclas guardadas; seleccione una referencia o una plantilla reconocida.')
    validate_layout(result)
    return result


class LayoutHistory:
    """Snapshots encompass every design component; one push is one user command."""
    def __init__(self, state):
        self.state = deepcopy(state); self.clean = deepcopy(state)
        self.undo_states = []; self.redo_states = []

    def push(self, state, title):
        validate_layout(state)
        if state == self.state: return False
        self.undo_states.append((deepcopy(self.state), title)); self.redo_states.clear()
        self.state = deepcopy(state)
        return True

    def undo(self):
        if self.undo_states:
            state, title = self.undo_states.pop()
            self.redo_states.append((deepcopy(self.state), title)); self.state = state

    def redo(self):
        if self.redo_states:
            state, title = self.redo_states.pop()
            self.undo_states.append((deepcopy(self.state), title)); self.state = state

    @property
    def dirty(self): return self.state != self.clean

    def mark_clean(self): self.clean = deepcopy(self.state)
