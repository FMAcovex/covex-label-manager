"""R8C opt-in text contract. Legacy fields never enter this renderer.

Fonts are the deterministic Base-14 resources supplied by the pinned MuPDF,
embedded explicitly in output. No system font lookup or silent substitution.
"""
from copy import deepcopy
from functools import lru_cache
import math
import re
import hashlib

import fitz

FAMILIES = {'sans': 'Helvetica · alternativa Arial', 'serif': 'Times', 'mono': 'Courier'}
DEFAULT = dict(contract=1, family='sans', italic=False, color='#000000',
               align='left', valign='top', wrap='word', overflow='block')
FONT_SHA256 = {
    'helv':'366720e054067fa49d030f58005c739fc787dcc9727a9327a28767777791d706',
    'hebo':'d4ea80d1d0e29a1e950808009ca8f96fe07a0670b60b556f6b2cf0705337fa9f',
    'heit':'fa6acc6f51b5935a6b7defbc3ead480cd4906e3b198930470335db9a9bff6590',
    'hebi':'9cdfc2d0947339dce76f99bdf9e2d9fe01e472a384cf683007e6a0bb35634623',
    'tiro':'eb609a306b81357853ba91c2a3c47f3bba04f3a8cfdeedc733b1aa4af5d03d4c',
    'tibo':'219011281845fd509a0042c1b70bf98d49e0f562815a6b4a2549ef2ca14fa70a',
    'tiit':'9deed810d473df0bfe15f426b2e69e560bcb756b801a9cbcebdd5cd82519ffa6',
    'tibi':'12b53139c10085e8fdc7d427ee00f49fa80ac7d0c578fd9ca9196c80e2cbf59f',
    'cour':'2e8380cc08f257fb0b301079323a442918ec9d69582c95607da5543b362aa6d6',
    'cobo':'aba820052e08d413b94465af8f1401e942234b57ac091a9c0e0a1dc10bb3f091',
    'coit':'b8bce31c935e0888435387d6ec610700afcc06a778433004e56348d374a3bf3a',
    'cobi':'9edb0d4b29b122a9f9f8098815ca99e5d3a00b8a106e3c659d66c5ccadde2c9e',
}


def validate(style):
    if not isinstance(style, dict) or set(style) != set(DEFAULT) or type(style.get('contract')) is not int or style['contract'] != 1:
        raise ValueError('Contrato tipográfico no reconocido.')
    if not isinstance(style['family'],str) or style['family'] not in FAMILIES or type(style['italic']) is not bool:
        raise ValueError('Familia o estilo tipográfico no admitido; no se sustituye la fuente.')
    if not isinstance(style['color'], str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', style['color']):
        raise ValueError('Color: utilice #RRGGBB.')
    if style['align'] not in ('left', 'center', 'right') or style['valign'] not in ('top', 'middle', 'bottom'):
        raise ValueError('Alineación tipográfica no admitida.')
    if style['wrap'] not in ('none', 'word') or style['overflow'] != 'block':
        raise ValueError('El desbordamiento debe bloquearse; no se recorta ni reduce texto automáticamente.')
    return dict(style)


def rgb(hex_color):
    if not isinstance(hex_color, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', hex_color):
        raise ValueError('Color: utilice #RRGGBB.')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (1, 3, 5))


@lru_cache(maxsize=12)
def font_resource(family, bold=False, italic=False):
    try:
        codes = {'sans': ('helv', 'hebo', 'heit', 'hebi'),
                 'serif': ('tiro', 'tibo', 'tiit', 'tibi'),
                 'mono': ('cour', 'cobo', 'coit', 'cobi')}
        code = codes[family][int(bool(bold)) + 2*int(bool(italic))]
        font = fitz.Font(fontname=code)
        if hashlib.sha256(font.buffer).hexdigest()!=FONT_SHA256[code]:
            raise ValueError('El recurso no corresponde al contrato tipográfico 1')
        return font, 'R8C_' + code
    except (KeyError, RuntimeError, ValueError) as exc:
        raise ValueError('Fuente documental no disponible. No se permite sustituirla; repare el portable o prepare una variante.') from exc


def ink_width(text,font,size):
    """Include side bearings/italic overhangs, not just advance widths."""
    pen=0.;left=0.;right=0.
    for char in text:
        box=font.glyph_bbox(ord(char))
        if not box.is_empty:
            left=min(left,pen+box.x0);right=max(right,pen+box.x1)
        pen+=font.glyph_advance(ord(char))
    return left*size,max(right,pen)*size


def _lines(text, width, font, size, wrap):
    def measured(value):
        left,right=ink_width(value,font,size)
        return right-left
    if width <= 0:
        raise ValueError('Anchura de texto insuficiente.')
    output = []
    for paragraph in text.split('\n'):
        if wrap == 'none':
            output.append(paragraph)
            continue
        current = ''
        for word in paragraph.split():
            if measured(word) > width + .001:
                raise ValueError('Una palabra no cabe en el campo; amplíelo o prepare una variante.')
            candidate = (current + ' ' + word).strip()
            if current and measured(candidate) > width:
                output.append(current); current = word
            else:
                current = candidate
        output.append(current)
    if any(measured(line) > width + .001 for line in output):
        raise ValueError('El texto excede la anchura del campo.')
    return output


def paint(page, text, rect, size, bold, style, *, strict=True, baseline=False,
          continuation=None, check_minimum=True):
    """Lay out and measure the SAME embedded glyphs that will enter the PDF.

    No silent shrink or truncation. Baseline/continuation preserve their source
    anchors; vertical alignment applies only to boxes/paragraphs.
    """
    style = validate(style); rect = fitz.Rect(rect)
    if type(bold) is not bool or isinstance(size, bool) or not math.isfinite(size) or size <= 0 or rect.is_empty:
        raise ValueError('Tipografía o geometría inválida.')
    if baseline and style['valign'] != 'top':
        raise ValueError('La alineación vertical sólo se admite en cajas o párrafos, no en líneas base.')
    font, name = font_resource(style['family'], bold, style['italic'])
    if any(c not in '\n\t' and not font.has_glyph(ord(c)) for c in text):
        raise ValueError('La fuente no contiene todos los caracteres. Elija otra familia o documente una variante; no se sustituyen glifos.')
    ascent, descent = font.ascender*size, -font.descender*size
    line_height = max(size*1.2, ascent+descent)
    # Coordinates are the source design units; transform only after composition.
    if continuation is not None:
        full_x, full_w, maximum = continuation
        lines = []; current = ''; width = rect.width
        for word in text.split():
            candidate = (current+' '+word).strip()
            il,ir=ink_width(candidate,font,size)
            if ir-il <= width:
                current = candidate
            else:
                lines.append(current); width = full_w; current = word
                il,ir=ink_width(word,font,size)
                if ir-il > width:
                    raise ValueError('Una palabra no cabe en la continuación.')
        if current:lines.append(current)
        if len(lines) > maximum:
            raise ValueError('Demasiadas líneas en la continuación.')
    else:
        lines = _lines(text, rect.width, font, size, 'none' if baseline else style['wrap'])
    height = ascent+descent+(len(lines)-1)*line_height
    if baseline:
        first_y = rect.y0
        if len(lines)>1 and (len(lines)-1)*line_height+descent > rect.height+.001:
            raise ValueError('La continuación excede la altura del campo.')
    else:
        if height > rect.height+.001:
            raise ValueError('El texto excede la altura del campo; no se reduce automáticamente.')
        free = rect.height-height
        first_y = rect.y0+ascent+({'top':0, 'middle':.5, 'bottom':1}[style['valign']])*free
    warnings = []
    if check_minimum and size < 6:
        message = f'Texto demasiado pequeño ({size:.2f} pt); mínimo operativo 6 pt.'
        if strict:raise ValueError(message)
        warnings.append(message)
    page.insert_font(fontname=name, fontbuffer=font.buffer)
    for i, line in enumerate(lines):
        left = continuation[0] if i and continuation else rect.x0
        width = continuation[1] if i and continuation else rect.width
        offset = (width-font.text_length(line, fontsize=size))*{'left':0,'center':.5,'right':1}[style['align']]
        ink_left,ink_right=ink_width(line,font,size)
        if ink_right-ink_left>width+.001:
            raise ValueError('Los trazos reales del texto exceden el campo; amplíelo, sin recortar cursivas.')
        # Preserve logical alignment whenever it is safe. Only compensate a
        # side bearing that would otherwise escape the authorized rectangle.
        origin=min(max(left+offset,left-ink_left),left+width-ink_right)
        page.insert_text((origin, first_y+i*line_height), line, fontname=name,
                         fontsize=size, color=rgb(style['color']), overlay=True)
    return warnings


def contrast_warning(source_page, box, color):
    """Only claim detectable contrast on a uniformly coloured source region.

    A complex background returns 'unknown', never an invented compliance claim.
    """
    pix = source_page.get_pixmap(clip=fitz.Rect(box), matrix=fitz.Matrix(1,1), alpha=False)
    if not pix.width or not pix.height:return None
    # Check every raster sample, not just corners that could miss a logo or
    # coloured patch under the text. Complex backgrounds remain unknown.
    pixels=pix.samples
    if any(max(pixels[i::pix.n])-min(pixels[i::pix.n])>4 for i in range(3)):
        return None
    def luminance(values):
        linear = [c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in values]
        return sum(a*b for a,b in zip(linear,(.2126,.7152,.0722)))
    front = luminance(rgb(color)); back = luminance([n/255 for n in pix.pixel(0,0)[:3]])
    ratio = (max(front,back)+.05)/(min(front,back)+.05)
    return f'Contraste insuficiente ({ratio:.2f}:1; referencia 4,5:1).' if ratio < 4.5 else None


def validate_trial(trial):
    if not isinstance(trial, dict) or set(trial) != {'contract','fields'} or type(trial['contract']) is not int or trial['contract'] != 1 or not isinstance(trial['fields'], dict):
        raise ValueError('Contrato de ajustes temporales no reconocido.')
    allowed = {'typography','font_pt','bold','x','y','w','h'}
    for key, patch in trial['fields'].items():
        if not isinstance(key,str) or key in ('texto_fijo','numero') or not isinstance(patch,dict) or set(patch)-allowed:
            raise ValueError('Sólo puede ajustarse la apariencia de campos variables definidos.')
        if 'bold' in patch and type(patch['bold']) is not bool:
            raise ValueError('Negrita inválida.')
        if patch.get('typography') is not None:validate(patch['typography'])
        for name in ('font_pt','x','y','w','h'):
            if name in patch and (isinstance(patch[name],bool) or not isinstance(patch[name],(int,float)) or not math.isfinite(patch[name])):
                raise ValueError('Medida de prueba inválida.')
    return trial


def apply_trial(version, trial):
    """Appearance only, no variable values/source/fixed artwork changes."""
    from .editor_layout import layout_from_version, version_with_layout, validate_layout, check_locked_changes, move_field
    validate_trial(trial)
    before = layout_from_version(version); after = deepcopy(before)
    indexed = {field['key']:field for field in after['fields']}
    for key, patch in trial['fields'].items():
        if key not in indexed:raise ValueError('Campo variable de prueba inexistente: '+key)
        field=indexed[key]
        # Use the existing geometry command so a moved anchored field carries
        # its offset, continuation and authorized mask WITH it into a variant.
        # Direct assignment would leave those contracts at the old position.
        move_field(field,patch.get('x',field['x'])-field['x'],patch.get('y',field['y'])-field['y'],after['crop'])
        field.update(deepcopy(patch))
        if 'typography' in patch and patch['typography'] is None:indexed[key].pop('typography',None)
    validate_layout(after); check_locked_changes(before, after)
    return version_with_layout(version, after)
