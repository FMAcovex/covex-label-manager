"""Design resolution and immutable render-to-history contract for all UI paths."""
import json
import uuid
from pathlib import Path
from .canonical import canonical,digest,json_digest
from .editor_layout import source_identity,version_with_layout
from .storage import now,sha256
from .integrity import verify_documents


def snapshot(store,revision_id,variant_id,profile,status,asset):
    effective,design,variant=store.variants.resolve(revision_id,variant_id,True)
    state=dict(asset) if asset is not None else None
    if status.get('kind','ninguna')!='ninguna':
        current=store.status_master(status['kind'])
        if current is None or current['state']!='APPROVED':raise PermissionError('Maestro de estado no aprobado.')
        verify_documents(current,store.root)
        state=dict(current)
    return {'contract':1,'revision_id':revision_id,'revision_uid':effective['uid'],'variant_id':variant_id,
        'variant_uid':variant['uid'] if variant else None,'generation':variant['generation'] if variant else None,
        'design':design,'design_sha256':digest(design),'source':source_identity(effective),
        'revision_approval':{k:effective[k] for k in ('approved_by','approval_ref','approved_at')},
        'variant_approval':{k:variant[k] for k in ('approved_by','approval_ref','approval_date','evidence_path','evidence_sha256')} if variant else None,
        'profile':profile,'status':status,'status_master':state,'build':__import__('covex_label_manager').__version__}


def render(api,version,values,profile,indices,count,copies,destination,test_mode=False,per_container=None,status=None,status_master=None,variant_id=None,history_snapshot=None,work_context=None):
    from .engine import render_emission
    store=api._repository;variant_id=version.get('_variant_id',variant_id) if isinstance(version,dict) else variant_id
    effective,design,variant=store.variants.resolve(version['id'],variant_id,not test_mode)
    if history_snapshot:
        if history_snapshot['revision_id']!=version['id'] or history_snapshot['variant_id']!=variant_id:raise ValueError('Snapshot de otra identidad.')
        if history_snapshot['source']!=source_identity(effective):raise ValueError('La fuente histórica no coincide.')
        effective=version_with_layout(effective,history_snapshot['design']['layout'])
        # A reprint can change only sheet placement (e.g. start_slot) and chosen indices.
        if status_master is not None and dict(status_master)!=history_snapshot['status_master']:raise ValueError('Maestro de estado histórico cambió.')
    status=status or {};profile=dict(profile);path=Path(destination).resolve()
    store._render_receipts.pop(str(path),None)
    if not test_mode and path.exists():raise FileExistsError('No sobrescriba un PDF existente; elija un nombre nuevo.')
    if status.get('kind','ninguna')!='ninguna':
        current_asset=store.status_master(status['kind'])
        if status_master is not None and dict(status_master)!=dict(current_asset):raise ValueError('El maestro de estado cambió.')
        status_master=current_asset
    snap=None if test_mode else snapshot(store,version['id'],variant_id,profile,status,status_master)
    if history_snapshot and snap:
        snap['design']=history_snapshot['design'];snap['design_sha256']=history_snapshot['design_sha256']
    if snap and work_context:snap['work']=dict(work_context)
    try:
        result=render_emission(effective,store.root,values,profile,indices,count,copies,path,test_mode,per_container,status,status_master)
        if snap:
            current=snapshot(store,version['id'],variant_id,profile,status,status_master)
            if digest({k:v for k,v in current.items() if k not in ('design','design_sha256','work')})!=digest({k:v for k,v in snap.items() if k not in ('design','design_sha256','work')}):raise ValueError('El estado documental cambió durante el render.')
            store._render_receipts[str(path)]={'snapshot':snap,'pdf_sha256':sha256(path),'data_hash':digest([values,profile,indices,count,copies,per_container or {},status])}
        return result
    except Exception:
        # Output is never declared issued. Preserve failed renders only in cache;
        # remove this newly generated destination to avoid an apparently valid PDF.
        if path.exists():path.unlink()
        raise


def record_issue(store,version_id,operator,count,copies,indices,values,profile,pdf_path,source_issue_id,reason,per_container,status):
    path=Path(pdf_path).resolve();root=store.root.resolve()
    if not path.is_relative_to(root/'emissions'):raise ValueError('La emisión definitiva debe estar en emissions.')
    receipt=store._render_receipts.get(str(path))
    if not receipt:raise PermissionError('Falta el contrato del PDF renderizado; genere mediante el servicio de emisión.')
    expected=digest([values,dict(profile),indices,count,copies,per_container or {},status or {}])
    if expected!=receipt['data_hash'] or receipt['snapshot']['revision_id']!=version_id:raise ValueError('Los datos no corresponden al PDF renderizado.')
    snap=receipt['snapshot'];variant_id=snap['variant_id']
    with store.txn() as db:
        db.execute('BEGIN IMMEDIATE')
        current=snapshot(store,version_id,variant_id,dict(profile),status or {},store.status_master((status or {}).get('kind','ninguna')))
        # For reprints the saved design can predate a mutable inherited pending
        # layout; approved revision layouts cannot be edited by application routes.
        if digest(current)!=digest({k:v for k,v in snap.items() if k!='work'}):raise ValueError('Revisión, variante o estado cambió antes de registrar la emisión.')
        if 'work' in snap and db.execute("SELECT 1 FROM issues WHERE json_extract(design_snapshot_json,'$.work.operation_uid')=?",(snap['work']['operation_uid'],)).fetchone():raise ValueError('Operación de trabajo ya registrada.')
        if sha256(path)!=receipt['pdf_sha256']:raise ValueError('PDF alterado antes del registro.')
        if source_issue_id is not None:
            origin=store.issue(source_issue_id)
            if not origin or origin['version_id']!=version_id or origin['design_variant_id']!=variant_id:raise ValueError('Origen de reimpresión incompatible.')
            if not reason.strip() or not set(indices).issubset(json.loads(origin['selected_indices'])):raise ValueError('Motivo y números originales obligatorios.')
        cur=db.execute('''INSERT INTO issues(uid,version_id,created_at,operator,count_containers,copies_per_container,
            selected_indices,variables_json,profile_json,pdf_path,source_issue_id,reason,per_container_json,status_json,pdf_sha256,
            design_variant_id,design_snapshot_json,design_snapshot_sha256) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (uuid.uuid4().hex,version_id,now(),operator,count,copies,canonical(indices),canonical(values),canonical(dict(profile)),
             path.relative_to(root).as_posix(),source_issue_id,reason,canonical(per_container or {}),canonical(status or {}),receipt['pdf_sha256'],
             variant_id,canonical(snap),digest(snap)))
        pk=cur.lastrowid
        db.execute('INSERT INTO audit(at,event,subject,detail) VALUES(?,?,?,?)',(now(),'ISSUE',str(pk),canonical({'variant_id':variant_id,'snapshot':digest(snap),'source_issue_id':source_issue_id})))
    store._render_receipts.pop(str(path),None)
    return pk
