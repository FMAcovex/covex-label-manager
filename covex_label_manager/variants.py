"""Independent variant lifecycle; original revision files and layouts are never written."""
import json
import math
import os
import re
import shutil
import uuid
from datetime import date
from pathlib import Path
from contextlib import contextmanager
import fitz
from .canonical import canonical,digest,json_digest
from .editor_layout import layout_from_version,version_with_layout,validate_layout,source_identity,MM_PER_POINT
from .integrity import verify_documents,verify_renderable
from .storage import now,sha256


def design_from_revision(version):
    layout=layout_from_version(version);crop=layout['crop']
    return {'layout':layout,'nominal_size_mm':{'width':(crop[2]-crop[0])*MM_PER_POINT,'height':(crop[3]-crop[1])*MM_PER_POINT}}


def update_design_layout(design,layout):
    old=design['layout']['crop'];new=layout['crop']
    factor=design['nominal_size_mm']['width']/(old[2]-old[0])
    return {'layout':layout,'nominal_size_mm':{'width':factor*(new[2]-new[0]),'height':factor*(new[3]-new[1])}}


def revision_hash(version):
    return digest({'source':source_identity(version),'layout':layout_from_version(version),
                   'document':{k:version[k] for k in ('label_id','version','origin','customer','ref_customer')}})


class VariantRepository:
    def __init__(self,store):self.store=store
    def get(self,variant_id):
        row=self.store.db.execute('SELECT * FROM design_variants WHERE id=?',(variant_id,)).fetchone()
        if not row:raise ValueError('Variante inexistente.')
        return dict(row)
    def list(self,revision_id):
        return [dict(r) for r in self.store.db.execute('SELECT * FROM design_variants WHERE revision_id=? ORDER BY id DESC',(revision_id,))]
    @contextmanager
    def transaction(self):
        with self.store.txn() as db:
            db.execute('BEGIN IMMEDIATE');yield db
    def audit(self,db,event,before,after,actor,reason=''):
        db.execute('INSERT INTO audit(at,event,subject,detail) VALUES(?,?,?,?)',(now(),event,'variant:'+after['uid'],canonical({'actor':actor,'reason':reason,'before':before,'after':after})))
    def actor(self,value):
        value=str(value).strip()
        if not value:raise ValueError('Indique el responsable.')
        return value
    def checked(self,variant_id,generation):
        row=self.get(variant_id)
        if row['generation']!=generation:raise ValueError('Generación obsoleta; recargue la variante.')
        return row
    def base(self,row,production=False):
        version=self.store.version(row['revision_id'])
        if not version:raise ValueError('Revisión inexistente.')
        verify_documents(version,self.store.root)
        if revision_hash(version)!=row['base_revision_sha256']:raise ValueError('La revisión base cambió; cree una variante desde la revisión actual.')
        if version['state']=='RETIRED':raise PermissionError('La revisión base está retirada.')
        if production:
            if version['state']!='APPROVED':raise PermissionError('La revisión base no está aprobada.')
            verify_renderable(version)
        return version
    def validate(self,version,design):
        if set(design)!={'layout','nominal_size_mm'}:raise ValueError('Contrato de diseño inválido.')
        with fitz.open(self.store.root/version['master_pdf']) as doc:validate_layout(design['layout'],list(doc[0].rect))
        size=design['nominal_size_mm'];w,h=size['width'],size['height'];crop=design['layout']['crop']
        if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0 for v in (w,h)):
            raise ValueError('Dimensiones nominales positivas y finitas obligatorias.')
        if abs(w/h-(crop[2]-crop[0])/(crop[3]-crop[1]))>1e-6:raise ValueError('El tamaño nominal deformaría el fondo fijo.')
        canonical(design)
    def create(self,revision_id,code,name,reason,actor,origin_id=None):
        code=code.strip().upper();name=name.strip();reason=reason.strip();actor=self.actor(actor)
        if not re.fullmatch(r'[A-Z0-9][A-Z0-9._-]{0,39}',code) or not name or not reason:raise ValueError('Código, denominación y motivo obligatorios.')
        with self.transaction() as db:
            version=self.store.version(revision_id)
            if not version or version['state']=='RETIRED':raise ValueError('Seleccione una revisión no retirada.')
            verify_documents(version,self.store.root)
            design=design_from_revision(version)
            if origin_id is not None:
                origin=self.get(origin_id)
                if origin['revision_id']!=revision_id:raise ValueError('El origen pertenece a otra revisión.')
                if origin['base_revision_sha256']!=revision_hash(version):raise ValueError('La base del origen cambió; cree desde la revisión.')
                if json_digest(origin['design_json'])!=origin['design_sha256']:raise ValueError('Diseño de origen alterado.')
                design=json.loads(origin['design_json'])
            self.validate(version,design);at=now()
            cur=db.execute('''INSERT INTO design_variants(uid,revision_id,origin_variant_id,code,name,reason,design_json,
                design_sha256,base_revision_sha256,created_at,created_by,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
                (uuid.uuid4().hex,revision_id,origin_id,code,name,reason,canonical(design),digest(design),revision_hash(version),at,actor,at))
            result=self.get(cur.lastrowid);self.audit(db,'CREATE_VARIANT',None,result,actor,reason)
            return result
    def save(self,variant_id,generation,design,actor):
        actor=self.actor(actor)
        with self.transaction() as db:
            old=self.checked(variant_id,generation)
            if old['state']!='DRAFT':raise PermissionError('Solo se edita una variante en borrador.')
            version=self.base(old);self.validate(version,design)
            db.execute('UPDATE design_variants SET design_json=?,design_sha256=?,generation=generation+1,updated_at=? WHERE id=? AND generation=?',
                       (canonical(design),digest(design),now(),variant_id,generation))
            result=self.get(variant_id);self.audit(db,'SAVE_VARIANT',old,result,actor)
            return result
    def transition(self,variant_id,generation,target,actor,reason=''):
        actor=self.actor(actor);reason=reason.strip()
        with self.transaction() as db:
            old=self.checked(variant_id,generation)
            allowed={'DRAFT':{'PENDING','RETIRED'},'PENDING':{'DRAFT','RETIRED'},'APPROVED':{'RETIRED'}}
            if target not in allowed.get(old['state'],set()):raise PermissionError('Transición no permitida.')
            if target in ('DRAFT','RETIRED') and not reason:raise ValueError('Indique el motivo.')
            if target=='PENDING':
                version=self.base(old);self.validate(version,json.loads(old['design_json']))
            at=now()
            values={'state':target,'generation':generation+1,'updated_at':at}
            if target=='RETIRED':values.update(retired_at=at,retired_by=actor,retirement_reason=reason)
            db.execute('UPDATE design_variants SET '+','.join(k+'=?' for k in values)+' WHERE id=?',(*values.values(),variant_id))
            result=self.get(variant_id);self.audit(db,{'PENDING':'SUBMIT_VARIANT','DRAFT':'RETURN_VARIANT','RETIRED':'RETIRE_VARIANT'}[target],old,result,actor,reason)
            return result
    def verify_evidence(self,row):
        p=(self.store.root/row['evidence_path']).resolve()
        if not p.is_relative_to(self.store.root.resolve()) or not p.is_file() or sha256(p)!=row['evidence_sha256']:
            raise ValueError('Evidencia documental ausente o alterada.')
        return p
    def approve(self,variant_id,generation,reviewer,reference,approval_date,evidence,actor):
        reviewer=self.actor(reviewer);actor=self.actor(actor);reference=reference.strip()
        if not reference:raise ValueError('Referencia documental obligatoria.')
        if date.fromisoformat(approval_date)>date.today():raise ValueError('La fecha documental no puede ser futura.')
        source=Path(evidence)
        if not source.is_file():raise ValueError('Seleccione la evidencia documental externa.')
        # Copy first into a unique, fsynced local file; never overwrite an attachment.
        old=self.checked(variant_id,generation)
        if old['state']!='PENDING':raise PermissionError('Solo se aprueba una variante pendiente.')
        self.base(old,True)
        parent=self.store.root/'approval_evidence'
        if parent.is_symlink() or not parent.resolve().is_relative_to(self.store.root.resolve()):raise ValueError('Carpeta de evidencia fuera de data.')
        parent.mkdir(exist_ok=True);folder=parent/old['uid']
        if folder.is_symlink():raise ValueError('Carpeta de evidencia no segura.')
        folder.mkdir(exist_ok=True)
        target=folder/(uuid.uuid4().hex+source.suffix.lower())
        try:
            expected=sha256(source)
            with source.open('rb') as inp,target.open('xb') as out:
                shutil.copyfileobj(inp,out);out.flush();os.fsync(out.fileno())
            if sha256(target)!=expected or sha256(source)!=expected:raise ValueError('La evidencia cambió durante la copia.')
            with self.transaction() as db:
                old=self.checked(variant_id,generation)
                if old['state']!='PENDING':raise PermissionError('La variante ya no está pendiente.')
                version=self.base(old,True);design=json.loads(old['design_json']);self.validate(version,design)
                if digest(design)!=old['design_sha256']:raise ValueError('El diseño no coincide con su hash.')
                at=now();values={'state':'APPROVED','approved_by':reviewer,'approval_ref':reference,'approval_date':approval_date,
                    'approval_recorded_at':at,'approval_recorded_by':actor,'approved_design_sha256':old['design_sha256'],
                    'evidence_path':target.relative_to(self.store.root).as_posix(),'evidence_sha256':expected,'generation':generation+1,'updated_at':at}
                db.execute('UPDATE design_variants SET '+','.join(k+'=?' for k in values)+' WHERE id=?',(*values.values(),variant_id))
                result=self.get(variant_id);self.verify_evidence(result);self.audit(db,'APPROVE_VARIANT',old,result,actor,reference)
                return result
        except Exception as ex:
            # Preserve the unreferenced file for explicit inspection; no approval
            # survives failed SQL/audit. Retrying creates a different attachment.
            raise ValueError(str(ex)+' Archivo de evidencia conservado sin aprobación: '+str(target)) from ex
    def resolve(self,revision_id,variant_id=None,production=False):
        version=self.store.version(revision_id)
        if not version:raise ValueError('Revisión inexistente.')
        verify_documents(version,self.store.root);verify_renderable(version)
        if version['state']=='RETIRED' or (production and version['state']!='APPROVED'):raise __import__('covex_label_manager.engine',fromlist=['LayoutError']).LayoutError('La revisión está pendiente de aprobación o retirada.')
        variant=None;design=design_from_revision(version)
        if variant_id is not None:
            variant=self.get(variant_id)
            if variant['revision_id']!=revision_id:raise ValueError('Variante de otra revisión.')
            self.base(variant,production)
            if variant['state']=='RETIRED' or (production and variant['state']!='APPROVED'):raise PermissionError('Variante no aprobada o retirada.')
            design=json.loads(variant['design_json'])
            if digest(design)!=variant['design_sha256']:raise ValueError('Diseño alterado.')
            self.validate(version,design)
            if variant['state']=='APPROVED':self.verify_evidence(variant)
        effective=version_with_layout(version,design['layout'])
        effective['_variant_id']=variant_id
        if variant:effective['_variant_code']=variant['code'];effective['_variant_state']=variant['state']
        return effective,design,variant
