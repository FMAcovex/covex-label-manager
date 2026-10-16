"""R5A conservative inventory and guarded local migration, no real catalog data."""
import csv
import hashlib
import os
import re
import unicodedata
import uuid
from pathlib import Path
from .importer import proposed_identity

MAX_BYTES=60*1024*1024
COLUMNS=('path','name','version','category','sha256','size_bytes','status','reason','outcome')


def normalize(value):
    return ' '.join(unicodedata.normalize('NFKC',str(value)).casefold().split())


def fingerprint(path):
    path=Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('Archivo inexistente o enlace no permitido.')
    size=path.stat().st_size
    if not 0<size<=MAX_BYTES:raise ValueError('Archivo vacío o superior a 60 MB.')
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for piece in iter(lambda:stream.read(1024*1024),b''):
            digest.update(piece)
    if path.stat().st_size!=size:raise ValueError('El archivo cambió durante el inventario.')
    return digest.hexdigest(),size


def inventory(api,paths):
    """Read-only classification against every existing revision and earlier files."""
    hashes=set();names=set()
    for row in api.library_records():
        names.add(normalize(row['name']))
        version=api.version(row['version_id'])
        if version and version['source_sha256']:
            hashes.add(version['source_sha256'].lower())
    batch_hashes=set();batch_names=set();result=[]
    for path in paths:
        p=Path(path);identity=proposed_identity(p)
        item={'path':str(p),'name':identity['name'],'version':identity['version'],
              'category':identity['category'],'sha256':'','size_bytes':0,
              'status':'ERROR','reason':'','outcome':''}
        try:
            if p.suffix.lower() not in ('.pdf','.doc','.docx','.png','.jpg','.jpeg'):
                raise ValueError('Extensión no soportada.')
            digest,size=fingerprint(p);item.update(sha256=digest,size_bytes=size)
            name=normalize(item['name'])
            if not name or not re.fullmatch(r'\d{2,3}',item['version']):
                raise ValueError('Nombre/revisión no identificables.')
            if digest in hashes or digest in batch_hashes:
                item.update(status='DUPLICATE',reason='Mismo archivo en el catálogo o en la selección.')
            elif name in names or name in batch_names:
                item.update(status='REVIEW',reason='Nombre ya identificado: conciliar revisión y producto.')
            elif any(word in str(p).upper() for word in ('ANULAD','CLIENTE','CUSTOMER')):
                item.update(status='REVIEW',reason='Posible anulada o etiqueta de cliente; no inferir vigencia/origen.')
            elif p.suffix.lower()=='.pdf':
                import fitz
                with fitz.open(p) as pdf:
                    item.update(status='NEW' if pdf.page_count==1 else 'REVIEW',
                                reason='PDF de una página, requiere revisión documental.' if pdf.page_count==1
                                else 'PDF multipágina; seleccionar página manualmente.')
            else:
                item.update(status='NEW',reason='Origen nuevo; requiere conversión y revisión visual.')
            batch_hashes.add(digest);batch_names.add(name)
        except (ValueError,OSError,RuntimeError) as ex:
            item.update(status='ERROR',reason=str(ex))
        result.append(item)
    return result


def guarded_import(api,entry,metadata):
    if entry['status']!='NEW':
        raise PermissionError('Solo NEW puede importarse automáticamente.')
    current_hash,size=fingerprint(entry['path'])
    if (current_hash,size)!=(entry['sha256'],entry['size_bytes']):
        raise ValueError('El origen cambió desde el inventario.')
    if any(metadata[k]!=entry[k] for k in ('name','version','category')):
        raise ValueError('Los metadatos cambiaron; repita el inventario.')
    current=inventory(api,[entry['path']])[0]
    if current['status']!='NEW' or current['sha256']!=current_hash:
        raise ValueError('El catálogo cambió; revise duplicados antes de importar.')
    vid=api.import_label(entry['path'],metadata)
    v=api.version(vid)
    if v['state']!='PENDING' or v['source_sha256']!=current_hash:
        raise ValueError('Importación anómala: revisión PENDING requiere investigación.')
    return vid


def export_inventory_csv(rows,path,protected_root):
    target=Path(path).resolve();root=Path(protected_root).resolve()
    if target.suffix.lower()!='.csv':raise ValueError('Use un destino CSV.')
    if target.is_relative_to(root):
        raise PermissionError('No exportar sobre la carpeta de datos protegidos.')
    temp=target.with_name(target.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        with temp.open('x',encoding='utf-8-sig',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=COLUMNS,extrasaction='ignore')
            writer.writeheader();writer.writerows(rows);stream.flush();os.fsync(stream.fileno())
        os.replace(temp,target)
    finally:temp.unlink(missing_ok=True)
    return target
