"""R5A read-only catalog inventory and verified library export.

Not a portable database backup. Never changes approval state or imports files.
"""
import hashlib
import json
import os
import tempfile
import uuid
import zipfile
from pathlib import Path

from .canonical import canonical
from .storage import sha256
from .importer import proposed_identity, list_importable_files


def file_hash(path):
    return sha256(path)


def _existing(api):
    result=[]
    for label in api.labels():
        for ver in api.versions(label['id']):
            result.append((dict(label),dict(ver)))
    return result


def inventory_folder(api,folder):
    """Preview local files against known hashes and names; never mutate."""
    root=Path(folder).resolve(strict=True)
    if not root.is_dir():raise ValueError('Seleccione una carpeta válida.')
    existing=_existing(api)
    exact={}
    keys={}
    for label,version in existing:
        for key in ('source_sha256','pdf_sha256'):
            if version[key]:exact.setdefault(version[key],set()).add((label['id'],version['id']))
        identity=(label['name'].strip().casefold(),version['version'].strip().casefold())
        keys.setdefault(identity,[]).append((label['id'],version['id']))
    entries=[]
    paths=sorted(list_importable_files(root))
    for path in paths:
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            entries.append({'path':str(path.relative_to(root)),'status':'BLOCKED_SYMLINK'})
            continue
        identity=proposed_identity(path)
        digest=file_hash(path)
        matches=sorted(exact.get(digest,set()))
        clash=keys.get((identity['name'].strip().casefold(),identity['version'].strip().casefold()),[])
        status='EXACT_DUPLICATE' if matches else 'IDENTITY_CONFLICT' if clash else 'REVIEW_REQUIRED'
        entries.append({'path':path.relative_to(root).as_posix(),'name':identity['name'],
                        'version':identity['version'],'category':identity['category'],
                        'sha256':digest,'size':path.stat().st_size,'status':status,
                        'matching_revisions':[list(item) for item in (matches or clash)]})
    return {'contract':1,'mode':'READ_ONLY','files':entries,
            'counts':{key:sum(row['status']==key for row in entries)
                      for key in ('EXACT_DUPLICATE','IDENTITY_CONFLICT','REVIEW_REQUIRED','BLOCKED_SYMLINK')}}


def export_library(api,destination):
    """Manifest with all revisions and assets; fail closed on corruption."""
    target=Path(destination).absolute()
    if target.suffix.lower()!='.zip':raise ValueError('Seleccione un ZIP de destino.')
    root=api._repository.root.resolve()
    if target.resolve().is_relative_to(root):raise PermissionError('Exporte fuera de la carpeta de datos de la aplicación.')
    if target.exists():raise FileExistsError('No se sobrescribe una exportación existente.')
    rows=[];blobs={}
    for label,ver in _existing(api):
        assets={}
        for role,key,checksum in (('master_pdf','master_pdf','pdf_sha256'),('original','original_file','source_sha256')):
            rel=ver[key]
            if not rel:continue
            path=(root/rel).resolve()
            if not path.is_relative_to(root) or not path.is_file() or path.is_symlink():
                raise ValueError('Documento ausente o fuera de datos controlados: '+str(rel))
            actual=sha256(path)
            if actual!=ver[checksum]:raise ValueError('Integridad comprometida en '+str(rel))
            arc='assets/'+rel.replace('\\','/')
            if arc in blobs and blobs[arc][1]!=actual:raise ValueError('Ruta de activo duplicada con distinta huella.')
            blobs[arc]=(path,actual)
            assets[role]={'path':arc,'sha256':actual,'bytes':path.stat().st_size}
        rows.append({'label':{'id':label['id'],'name':label['name'],'code':label['code'],
                               'category':label['category'],'origin':label['origin'],'customer':label['customer']},
                     'revision':{'id':ver['id'],'version':ver['version'],'state':ver['state'],
                                 'notes':ver['notes'],'created_at':ver['created_at']},
                     'assets':assets})
    manifest={'contract':1,'type':'CATALOG_EXPORT_NOT_BACKUP','documents':rows,
              'files':{arc:digest for arc,(_,digest) in sorted(blobs.items())}}
    target.parent.mkdir(parents=True,exist_ok=True)
    tmp=target.with_name(target.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        with zipfile.ZipFile(tmp,'x',compression=zipfile.ZIP_DEFLATED) as z:
            for arc,(path,_) in sorted(blobs.items()):z.write(path,arc)
            z.writestr('catalog-manifest.json',canonical(manifest))
        with zipfile.ZipFile(tmp) as z:
            if len(z.namelist())!=len(set(z.namelist())):raise ValueError('Rutas ZIP duplicadas.')
            for arc,digest in manifest['files'].items():
                if hashlib.sha256(z.read(arc)).hexdigest()!=digest:
                    raise ValueError('Fallo de verificación ZIP: '+arc)
        os.replace(tmp,target)
    finally:
        if tmp.exists():tmp.unlink()
    return {'path':str(target),'revisions':len(rows),'assets':len(blobs)}
