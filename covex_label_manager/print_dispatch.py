"""Read-only preflight for dispatching a registered PDF to a physical printer.

Print dispatch is NOT a new issue, a reprint record or proof of physical output.
No Qt dependencies; all verification is performed before touching a spooler.
"""
import hashlib
import json
import math
from pathlib import Path

import fitz

from .sheet_layout import paper_size

MM_PER_POINT = 25.4 / 72.0
MAX_SPOOL_BYTES = 100 * 1024 * 1024
MAX_RASTER_PIXELS = 40_000_000


def close_size(actual, expected, tolerance=0.6):
    return len(actual) == len(expected) and all(
        math.isfinite(float(v)) and abs(float(v)-float(w)) <= tolerance
        for v,w in zip(actual, expected)
    )


def prepare_registered(api, issue_id):
    """Acquire a verified immutable-in-memory copy of an issued PDF."""
    report=api.history.inspect(issue_id)
    row=report['issue']
    if report.get('blocked'):
        raise PermissionError('No puede enviarse a impresión: '+str(report['blocked']))
    if not report.get('snapshot'):
        raise PermissionError('PDF histórico sin snapshot documental verificado. Requiere revisión.')
    digest=row['pdf_sha256']
    if not isinstance(digest,str) or len(digest)!=64:
        raise PermissionError('No se imprime un PDF sin huella de integridad registrada.')
    path=Path(report['path'])
    if path.stat().st_size > MAX_SPOOL_BYTES:
        raise ValueError('PDF demasiado grande para un único envío controlado.')
    data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=digest:
        raise ValueError('El PDF cambió durante la preparación de impresión.')
    profile=json.loads(row['profile_json'])
    expected=paper_size(profile)
    with fitz.open(stream=data,filetype='pdf') as document:
        if document.page_count<1 or document.page_count>1000:
            raise ValueError('Número de páginas no permitido para impresión controlada.')
        for i,page in enumerate(document):
            actual=(page.rect.width*MM_PER_POINT,page.rect.height*MM_PER_POINT)
            if not close_size(actual,expected):
                raise ValueError(f'Página {i+1}: el papel PDF no coincide con el formato registrado.')
        pages=document.page_count
    return {
        'issue_id':int(row['id']),
        'pdf_bytes':data,
        'pdf_sha256':digest,
        'token':report['token'],
        'profile':profile,
        'paper_mm':tuple(expected),
        'pages':pages,
        'printer_reference':str(profile.get('printer_name','')).strip(),
        'partially_used_first_page':bool(profile.get('occupied_slots') or int(profile.get('start_slot',1))>1),
    }


def validate_device(plan, name, paper_mm, native=True):
    """Reject incompatible device selection before any print-job transmission."""
    name=str(name).strip()
    if not native or not name:
        raise ValueError('Seleccione una impresora real del sistema, no un archivo PDF de salida.')
    if not close_size(paper_mm,plan['paper_mm']):
        raise ValueError('El papel seleccionado no coincide con el PDF: '+str(plan['paper_mm'])+' mm.')
    profile=plan['profile']
    if profile.get('printer_calibration') and name.casefold()!=plan['printer_reference'].casefold():
        raise ValueError('Perfil calibrado para otra impresora. Seleccione su cola exacta o vuelva a calibrar.')
    return True


def raster_size(paper_mm,dpi):
    if not isinstance(dpi,int) or not 72<=dpi<=1200:
        raise ValueError('Resolución de impresión fuera del intervalo seguro 72–1200 dpi.')
    w,h=(math.ceil(float(mm)*dpi/25.4) for mm in paper_mm)
    if w<=0 or h<=0 or w*h>MAX_RASTER_PIXELS:
        raise ValueError('La hoja excede el tamaño de rasterización seguro para impresión.')
    return w,h
