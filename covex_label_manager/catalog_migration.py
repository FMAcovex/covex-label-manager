"""R5B preview and explicit PENDING-only import, no schema changes."""
from pathlib import Path
from collections import defaultdict
from .catalog_exchange import _existing
from .importer import proposed_identity,docx_to_pdf,auto_crop
from .storage import sha256
import tempfile,shutil,fitz,hashlib

SUFFIXES={'.docx','.doc','.pdf','.png','.jpg','.jpeg'}
def safe(root,name):
    if not isinstance(name,str) or not name or '\\' in name:raise ValueError('Ruta inválida.')
    rel=Path(name)
    if rel.is_absolute() or '..' in rel.parts or '.' in rel.parts:raise ValueError('Ruta no autorizada.')
    path=root/rel
    if path.suffix.lower() not in SUFFIXES or not path.is_file():raise ValueError('Archivo inexistente o no admitido.')
    if path.is_symlink() or any(p.is_symlink() for p in path.parents if p.is_relative_to(root) and p!=root):raise ValueError('Enlace simbólico no permitido.')
    if not path.resolve().is_relative_to(root):raise ValueError('Ruta fuera de carpeta.')
    return path

class PreviewCancelled(Exception):
    """A read-only inventory was interrupted before classification finished."""


def _scan_digest(path, interrupt):
    if interrupt is None:
        return sha256(path)
    digest=hashlib.sha256()
    with open(path,'rb') as source:
        while True:
            if interrupt():
                raise PreviewCancelled()
            block=source.read(128*1024)
            if not block:
                return digest.hexdigest()
            digest.update(block)


def preview_existing(existing,folder,interrupt=None):
    """Hash and classify from plain snapshots; never access SQLite in a worker.

    All final imports still revalidate SHA-256 and documentary identity through
    the locked repository. Cancellation never creates or updates any record.
    """
    root=Path(folder).resolve(strict=True)
    if not root.is_dir():raise ValueError('Seleccione carpeta.')
    groups=defaultdict(list);rows=[]
    for p in sorted(root.rglob('*')):
        if interrupt is not None and interrupt():
            raise PreviewCancelled()
        if p.suffix.lower() not in SUFFIXES or p.name.startswith('~$'):continue
        rel=p.relative_to(root).as_posix()
        try:safe(root,rel)
        except (ValueError,OSError):rows.append(dict(source=rel,status='BLOCKED_UNSAFE'));continue
        groups[(str(p.parent.relative_to(root)).casefold(),p.stem.casefold())].append(p)
    for group in groups.values():
        if interrupt is not None and interrupt():
            raise PreviewCancelled()
        originals=[p for p in group if p.suffix.lower() in ('.doc','.docx')]
        pdfs=[p for p in group if p.suffix.lower()=='.pdf']
        images=[p for p in group if p.suffix.lower() in ('.png','.jpg','.jpeg')]
        if len(originals)>1 or len(pdfs)>1 or len(images)>1 or (images and (pdfs or originals)):
            rows.append(dict(source=group[0].relative_to(root).as_posix(),status='BLOCKED_PAIR'));continue
        src=(originals or images or pdfs)[0];pdf=pdfs[0] if pdfs else None
        ident=proposed_identity(src);digest=_scan_digest(src,interrupt);pdigest=_scan_digest(pdf,interrupt) if pdf else None
        exact=[];overlap=[];identities=[]
        for l,v in existing:
            a=v['source_sha256'];b=v['pdf_sha256']
            if digest==a and (not pdigest or pdigest==b):exact.append(v['id'])
            elif digest in (a,b) or (pdigest and pdigest in (a,b)):overlap.append(v['id'])
            if l['name'].casefold()==ident['name'].casefold() and v['version'].casefold()==ident['version'].casefold():identities.append(v['id'])
        status='EXACT_DUPLICATE' if exact else 'HASH_CONFLICT' if overlap else 'IDENTITY_CONFLICT' if identities else 'REVIEW_REQUIRED'
        rows.append(dict(source=src.relative_to(root).as_posix(),pdf=pdf.relative_to(root).as_posix() if pdf else None,
            sha256=digest,pdf_sha256=pdigest,status=status,matches=exact or overlap or identities,**ident))
    seen={}
    for row in sorted(rows,key=lambda x:x['source']):
        h=row.get('sha256')
        if h in seen and row['status']=='REVIEW_REQUIRED':row['status']='BATCH_DUPLICATE'
        if h:seen.setdefault(h,row['source'])
    if interrupt is not None and interrupt():
        raise PreviewCancelled()
    return {'contract':2,'mode':'REVIEW_ONLY','files':sorted(rows,key=lambda x:x['source'])}


def preview(api,folder):
    # Compatibility with R5B service and synchronous non-Qt callers.
    # The GUI snapshots catalog rows on the UI thread before running
    # preview_existing on the worker.
    return preview_existing(_existing(api),folder)


def validate_intent(row, decision):
    """Check user choices without touching a source or a database."""
    if not isinstance(row, dict) or not isinstance(decision, dict):
        raise ValueError('Selección inválida.')
    if row.get('status') not in ('REVIEW_REQUIRED', 'IDENTITY_CONFLICT'):
        raise ValueError('Archivo bloqueado por inventario.')
    mode=decision.get('action')
    if mode not in ('NEW_LABEL','NEW_REVISION'):
        raise ValueError('Acción explícita obligatoria.')
    name=decision.get('name','');version=decision.get('version','')
    origin=decision.get('origin')
    if (not isinstance(name,str) or not name.strip()
            or not isinstance(version,str) or not version.strip()):
        raise ValueError('Nombre y revisión obligatorios.')
    if origin not in ('COVEX','CLIENTE'):
        raise ValueError('Origen inválido.')
    customer=decision.get('customer','')
    if origin=='CLIENTE' and not customer:
        raise ValueError('Cliente obligatorio.')
    if any(not isinstance(decision.get(k,''),str)
           for k in ('code','category','annex','ref_customer','customer')):
        raise ValueError('Metadatos inválidos.')
    return mode


def prepare_source(folder, row, staging_directory):
    """Expensive, *read-only* stage: copy/hash/convert/crop off the GUI thread.

    No catalogue API, Qt object, DB handle or audit log may enter this function.
    Caller owns the staging directory and must keep it alive through commit.
    """
    if not isinstance(row,dict) or row.get('status') not in ('REVIEW_REQUIRED','IDENTITY_CONFLICT'):
        raise ValueError('Archivo bloqueado por inventario.')
    root=Path(folder).resolve(strict=True)
    source=safe(root,row['source'])
    pdf_source=safe(root,row['pdf']) if row.get('pdf') else None
    if sha256(source)!=row.get('sha256') or (
            pdf_source and sha256(pdf_source)!=row.get('pdf_sha256')):
        raise ValueError('Fuente modificada desde previsualización.')
    temp=Path(staging_directory)
    temp.mkdir(parents=True,exist_ok=True)
    original=temp/('original'+source.suffix.lower())
    if original.exists():
        raise FileExistsError('La preparación ya existe.')
    shutil.copyfile(source,original)
    if sha256(original)!=row['sha256']:
        raise ValueError('La copia de origen cambió.')
    if pdf_source and pdf_source!=source:
        pdf=temp/'master.pdf'
        if pdf.exists():
            raise FileExistsError('La preparación PDF ya existe.')
        shutil.copyfile(pdf_source,pdf)
        if sha256(pdf)!=row['pdf_sha256']:
            raise ValueError('La copia PDF cambió.')
    elif source.suffix.lower()=='.pdf':
        pdf=original
    else:
        pdf=docx_to_pdf(original,temp/'converted')
    with fitz.open(pdf) as doc:
        if doc.page_count!=1:
            raise ValueError('Separe etiquetas multipágina.')
    crop,_=auto_crop(pdf)
    return {'original':str(original),'pdf':str(pdf),'crop':crop,
            'staged_pdf_sha256':sha256(pdf)}


def commit_prepared(api, folder, row, decision, prepared):
    """Fast catalogue transaction on owner thread, rechecking original + stage.

    This preserves the same hash, lock, duplicate and pending-only safeguards
    used by apply(). No approval or overwrite can occur.
    """
    mode=validate_intent(row,decision)
    root=Path(folder).resolve(strict=True)
    source=safe(root,row['source'])
    pdf_source=safe(root,row['pdf']) if row.get('pdf') else None
    if sha256(source)!=row.get('sha256') or (
            pdf_source and sha256(pdf_source)!=row.get('pdf_sha256')):
        raise ValueError('Fuente modificada desde previsualización.')
    original=Path(prepared['original'])
    pdf=Path(prepared['pdf'])
    if sha256(original)!=row['sha256'] or sha256(pdf)!=prepared['staged_pdf_sha256']:
        raise ValueError('La preparación ha cambiado desde la conversión.')
    crop=prepared['crop']
    name=decision['name'];version=decision['version']
    origin=decision['origin'];customer=decision.get('customer','')
    with api.work.catalog_lock():
        for l,v in _existing(api):
            if row['sha256'] in (v['source_sha256'],v['pdf_sha256']) or (
                    row.get('pdf_sha256') and row['pdf_sha256'] in
                    (v['source_sha256'],v['pdf_sha256'])):
                raise ValueError('Documento ya registrado; revisar coincidencia.')
        if mode=='NEW_LABEL':
            for l in api.labels():
                if (l['origin'].casefold()==origin.casefold()
                        and l['customer'].casefold()==customer.casefold()
                        and (l['name'].casefold()==name.strip().casefold()
                             or (decision.get('code') and
                                 l['code'].casefold()==decision['code'].casefold()))):
                    raise ValueError('Etiqueta existente: vincule una revisión, no duplique el maestro.')
            vid=api._repository.add_label(
                name,decision.get('code',''),decision.get('category',''),
                decision.get('annex',''),origin,customer,version,pdf,original,
                crop,[],'R5B · importar pendiente, revisar campos y recorte. SHA-256 '+
                row['sha256'],decision.get('ref_customer',''))
        else:
            target=decision.get('target_label_id')
            if (not isinstance(target,int) or isinstance(target,bool)
                    or not any(l['id']==target for l in api.labels())):
                raise ValueError('Seleccione etiqueta de destino válida.')
            if any(v['version'].casefold()==version.casefold()
                   for v in api.versions(target)):
                raise ValueError('Revisión existente.')
            vid=api._repository.add_version(
                target,version,pdf,original,crop,[],
                'R5B · revisión pendiente, revisar campos y recorte. SHA-256 '+
                row['sha256'])
    result=api.version(vid)
    return {'label_id':result['label_id'],'version_id':vid,'state':result['state']}


def apply(api, folder, row, decision):
    """Backwards-compatible synchronous service entrypoint."""
    validate_intent(row,decision)
    with tempfile.TemporaryDirectory(prefix='covex_r5b_') as directory:
        prepared=prepare_source(folder,row,directory)
        return commit_prepared(api,folder,row,decision,prepared)
