"""Isolated, non-productive PDF worker. Never share MuPDF globals with Qt."""
import json
import os
from pathlib import Path
import re
import time
from .emission_work import WorkConflict,parameters


def retry_read(call,wait=time.sleep):
    for attempt in range(5):
        try:return call()
        except WorkConflict:
            if attempt==4:raise
            wait(.05)


def run_job(job_path):
    from .storage import Store,sha256
    from .services import LocalServices
    from .migration_v4 import atomic_json,active_path
    job_path=Path(job_path).resolve()
    job=json.loads(job_path.read_text(encoding='utf-8'))
    root=Path(job['root']).resolve();path=Path(job['path']).resolve()
    if (job.get('contract')!=1 or job_path.parent!=root/'cache' or path.parent!=root/'cache'
        or not re.fullmatch(r'qt-auto-proof-[a-f0-9]{32}\.pdf',path.name)
        or type(job['generation']) is not int or type(job['serial']) is not int
        or not re.fullmatch(r'[a-f0-9]{64}',job['token'])):
        raise ValueError('Contrato de vista previa inválido.')
    uid=job['uid'];generation=job['generation'];token=job['token']
    payload=dict(uid=uid,generation=generation,stamp=token,path=str(path),serial=job['serial'],child_pid=os.getpid())
    api=None
    try:
        if not active_path(root).is_file():raise ValueError('El catálogo ya no está disponible; no se creará otro.')
        api=LocalServices(Store(root,seed=False))
        before=retry_read(lambda:api.review_work(uid,generation))
        if not before['proof_allowed'] or before.get('token')!=token:
            raise ValueError('El trabajo o los documentos cambiaron. Revise los datos.')
        # Snapshot under short locks; never hold the exclusive work/catalog
        # lock for the render. Autosave can proceed; stale output is discarded.
        work=retry_read(lambda:api.work.get(uid))
        if work['generation']!=generation:raise WorkConflict('Trabajo obsoleto.')
        api.work.assert_current(work)
        profile,indices,count,copies=parameters(work);binding=work['binding']
        payload['result']=api.render(api.resolved_design(binding['revision_id'],binding['variant_id']),
            work['values'],profile,indices,count,copies,path,True,
            per_container=work['per_container'],status=work['status'])
        if retry_read(lambda:api.review_work(uid,generation)).get('token')!=token:
            raise ValueError('El trabajo o los documentos cambiaron durante el cálculo.')
        payload['sha256']=sha256(path)
    except Exception as ex:
        from .diagnostics import technical_exception
        payload['error']=str(ex)
        payload['technical_error']=technical_exception(ex)
    finally:
        if api is not None:api.close()
    atomic_json(job_path.with_suffix('.result.json'),payload)
    return 1 if payload.get('error') else 0
