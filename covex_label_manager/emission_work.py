"""Portable local drafts. SQLite remains the sole authority for issued output."""
import copy
import json
import os
import re
import uuid
from contextlib import contextmanager
from pathlib import Path
from .canonical import canonical,digest
from .migration_v4 import atomic_json
from .editor_layout import source_identity
from .variants import design_from_revision
from .storage import now


class WorkConflict(ValueError):pass
class WorkCorrupt(ValueError):pass


@contextmanager
def file_lock(path):
    """Nonblocking OS lock: process death releases it, no stale timestamp leases."""
    path=Path(path)
    with open(path,'a+b') as f:
        if f.tell()==0:f.write(b'0');f.flush()
        try:
            if os.name=='nt':
                import msvcrt
                f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as ex:raise WorkConflict('Trabajo ocupado por otro proceso. Reintente sin cerrar sus datos.') from ex
        try:yield
        finally:
            if os.name=='nt':f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(f.fileno(),fcntl.LOCK_UN)


def profile_numbers(raw):
    out=dict(raw)
    for k in ('width_mm','height_mm','margin_mm','gap_mm','offset_x_mm','offset_y_mm','safety_mm'):
        if k in out:out[k]=float(str(out[k]).replace(',','.'))
    out['start_slot']=int(out.get('start_slot',1));out['crop_marks']=int(out.get('crop_marks',0))
    return out


def parameters(work):
    count=int(work['count']);copies=int(work['copies'])
    if not 1<=count<=10000 or not 1<=copies<=100:raise ValueError('Recipientes: 1–10000; copias: 1–100.')
    selection=work.get('selection','').strip()
    indices=[int(n.strip()) for n in selection.split(',')] if selection else list(range(1,count+1))
    if not indices or len(set(indices))!=len(indices) or any(n<1 or n>count for n in indices):raise ValueError('Selección de recipientes inválida.')
    return profile_numbers(work['profile']),indices,count,copies


class WorkRepository:
    EDITABLE={'name','values','per_container','profile','count','copies','selection','status'}
    def __init__(self,api):
        self.api=api;self.root=api._repository.root/'emission_work'
        self.root.mkdir(exist_ok=True)
    def path(self,uid):
        if not isinstance(uid,str) or not re.fullmatch('[a-f0-9]{32}',uid):raise ValueError('UID de trabajo inválido.')
        return self.root/(uid+'.json')
    @contextmanager
    def lock(self,uid):
        path=self.path(uid)
        with file_lock(path.with_suffix('.lock')):yield
    def _read(self,path):
        try:
            from .canonical import parse
            # Parse duplicate keys strictly, then plain JSON keeps engine numbers native.
            raw=path.read_text(encoding='utf-8');parse(raw);envelope=json.loads(raw)
            if envelope.get('contract')!=1:raise ValueError('Contrato de trabajo desconocido.')
            w=envelope['payload']
            if digest(w)!=envelope['sha256']:raise ValueError('Checksum de trabajo incorrecto.')
            self.validate(w)
            if path.name not in (w['uid']+'.json',w['uid']+'.previous.json'):raise ValueError('Identidad de archivo incorrecta.')
            return w
        except (OSError,ValueError,KeyError,TypeError) as ex:
            raise WorkCorrupt('Trabajo no legible; no se ha sobrescrito: '+str(path)+'. '+str(ex)) from ex
    def validate(self,w):
        self.path(w['uid'])
        if type(w['generation']) is not int or w['generation']<1 or w['phase'] not in ('DRAFT','EMITTING','ISSUED'):raise ValueError('Generación/estado inválido.')
        for k in ('values','per_container','profile','status','binding'):
            if not isinstance(w[k],dict):raise ValueError('Objeto de trabajo inválido: '+k)
        for k in ('name','count','copies','selection','created_at','updated_at'):
            if not isinstance(w[k],str):raise ValueError('Texto de trabajo inválido: '+k)
        if not w['name'].strip():raise ValueError('Indique una denominación de trabajo.')
        if any(not isinstance(v,str) for v in w['values'].values()):raise ValueError('Valores comunes deben ser texto.')
        for number,values in w['per_container'].items():
            if not number.isdigit() or int(number)<1 or not isinstance(values,dict) or any(not isinstance(v,str) for v in values.values()):raise ValueError('Datos por recipiente inválidos.')
        if w['phase']!='DRAFT' and not re.fullmatch('[a-f0-9]{32}',w.get('operation_uid') or ''):raise ValueError('Falta intención de emisión.')
        canonical(w)
    def binding(self,revision_id,variant_id):
        v=dict(self.api.version(revision_id) or {})
        if not v:raise ValueError('Revisión inexistente.')
        variant=self.api.variant(variant_id) if variant_id is not None else None
        if variant and variant['revision_id']!=revision_id:raise ValueError('Variante de otra revisión.')
        design=json.loads(variant['design_json']) if variant else design_from_revision(v)
        return {'revision_id':revision_id,'revision_uid':v['uid'],'variant_id':variant_id,
            'variant_uid':variant['uid'] if variant else None,'source':source_identity(v),
            'design_sha256':digest(design),'revision_state':v['state'],
            'revision_approval':{k:v[k] for k in ('approved_by','approval_ref','approved_at')},
            'variant_generation':variant['generation'] if variant else None}
    def assert_current(self,w,production=False):
        b=w['binding']
        if self.binding(b['revision_id'],b['variant_id'])!=b:raise WorkConflict('El documento o la variante cambió. Conserve el trabajo y actualice explícitamente el vínculo documental.')
        self.api.resolved_design(b['revision_id'],b['variant_id'],production)
    def _write(self,w,previous=None):
        self.validate(w);path=self.path(w['uid'])
        if previous is not None:
            atomic_json(path.with_suffix('.previous.json'),{'contract':1,'payload':previous,'sha256':digest(previous)})
        atomic_json(path,{'contract':1,'payload':w,'sha256':digest(w)})
        return copy.deepcopy(w)
    def create(self,revision_id,variant_id=None,name='Nuevo trabajo',template=None):
        stamp=now();uid=uuid.uuid4().hex
        v=self.api.resolved_design(revision_id,variant_id,False)
        w={'uid':uid,'generation':1,'name':name.strip(),'created_at':stamp,'updated_at':stamp,
           'binding':self.binding(revision_id,variant_id),'phase':'DRAFT','operation_uid':None,'issue_id':None,
           'values':{},'per_container':{},'count':'1','copies':'1','selection':'','status':{'kind':'ninguna'},
           'profile':{'width_mm':v['base_w_mm'],'height_mm':v['base_h_mm'],'orientation':'portrait',
                'margin_mm':8,'gap_mm':3,'offset_x_mm':0,'offset_y_mm':0,'start_slot':1,'crop_marks':0,'safety_mm':0,'printer_name':''}}
        if template:
            for k in self.EDITABLE-{'name'}:w[k]=copy.deepcopy(template[k])
        with self.lock(uid):return self._write(w)
    def _committed(self,w):
        if not w.get('operation_uid'):return None
        row=self.api._repository.db.execute("SELECT id FROM issues WHERE json_extract(design_snapshot_json,'$.work.operation_uid')=?",(w['operation_uid'],)).fetchone()
        return row[0] if row else None
    def _reconcile(self,w):
        if w['phase']=='EMITTING':
            issue=self._committed(w)
            if issue:
                previous=copy.deepcopy(w);w.update(phase='ISSUED',issue_id=issue,generation=w['generation']+1,updated_at=now())
                return self._write(w,previous)
        return w
    def get(self,uid):
        with self.lock(uid):return self._reconcile(self._read(self.path(uid)))
    def list(self):
        rows=[]
        for path in sorted(self.root.glob('*.json')):
            if path.name.endswith('.previous.json'):continue
            try:rows.append(self.get(path.stem))
            except (WorkCorrupt,WorkConflict) as ex:rows.append({'uid':path.stem,'name':path.stem,'phase':'ERROR','error':str(ex)})
        return rows
    def save(self,uid,generation,changes):
        if set(changes)-self.EDITABLE:raise ValueError('No se permite modificar identidad, documento o estado del trabajo.')
        with self.lock(uid):
            old=self._reconcile(self._read(self.path(uid)))
            if old['generation']!=generation:raise WorkConflict('Generación de trabajo obsoleta. Recargue antes de guardar; los datos de pantalla se conservan.')
            if old['phase']!='DRAFT':raise PermissionError('Trabajo emitido o interrumpido: copie o recupere antes de editar.')
            new=copy.deepcopy(old);new.update(copy.deepcopy(changes));new.update(generation=generation+1,updated_at=now())
            return self._write(new,old)
    def refresh_binding(self,uid,generation):
        with self.lock(uid):
            old=self._read(self.path(uid))
            if old['generation']!=generation or old['phase']!='DRAFT':raise WorkConflict('Trabajo obsoleto o no editable.')
            b=old['binding'];new=copy.deepcopy(old);new['binding']=self.binding(b['revision_id'],b['variant_id'])
            new.update(generation=generation+1,updated_at=now());return self._write(new,old)
    def recover_previous(self,uid):
        with self.lock(uid):
            if self.api._repository.db.execute("SELECT 1 FROM issues WHERE json_extract(design_snapshot_json,'$.work.uid')=?",(uid,)).fetchone():raise PermissionError('Trabajo con emisión registrada; no restaure un borrador anterior.')
            path=self.path(uid);previous=self._read(path.with_suffix('.previous.json'))
            # Refuse rollback of an emission, even if its current JSON is corrupt.
            if previous['phase']!='DRAFT':raise PermissionError('La copia es un intento de emisión; recupérelo por su operación.')
            if path.exists():
                current_bytes=path.read_bytes()
                try:
                    current=self._read(path)
                    if current['phase']!='DRAFT':raise PermissionError('No retroceda un intento o emisión registrada.')
                    previous['generation']=max(previous['generation'],current['generation'])
                except WorkCorrupt:pass
                forensic=path.with_name(uid+'.corrupt-'+uuid.uuid4().hex+'.txt');forensic.write_bytes(current_bytes)
            previous.update(generation=max(previous['generation']+1,__import__('time').time_ns()),updated_at=now())
            return self._write(previous)
    def recover_attempt(self,uid,generation):
        with self.lock(uid):
            old=self._reconcile(self._read(self.path(uid)))
            if old['phase']=='ISSUED':return old
            if old['generation']!=generation or old['phase']!='EMITTING':raise WorkConflict('El intento ya cambió.')
            # Recover as a NEW draft: never reuse an operation or hide its failed PDF.
            new=copy.deepcopy(old);new.update(phase='DRAFT',operation_uid=None,issue_id=None,
                generation=generation+1,updated_at=now())
            return self._write(new,old)
    def proof(self,uid,generation,destination):
        with self.lock(uid):
            w=self._read(self.path(uid))
            if w['generation']!=generation:raise WorkConflict('Trabajo obsoleto.')
            self.assert_current(w);p,indices,count,copies=parameters(w);b=w['binding']
            return self.api.render(self.api.resolved_design(b['revision_id'],b['variant_id']),w['values'],p,
                indices,count,copies,destination,True,per_container=w['per_container'],status=w['status'])
    def issue(self,uid,generation,operator,hook=None):
        with self.lock(uid):
            old=self._reconcile(self._read(self.path(uid)))
            if old['phase']=='ISSUED':raise PermissionError('Trabajo ya emitido. Copie para preparar otro lote.')
            if old['generation']!=generation or old['phase']!='DRAFT':raise WorkConflict('Trabajo obsoleto o intento interrumpido.')
            if not operator.strip():raise ValueError('Responsable obligatorio.')
            self.assert_current(old,True);p,indices,count,copies=parameters(old)
            w=copy.deepcopy(old);w.update(phase='EMITTING',operation_uid=uuid.uuid4().hex,
                generation=generation+1,updated_at=now())
            self._write(w,old)
            if hook:hook('INTENT',w)
            b=w['binding'];context={'uid':uid,'operation_uid':w['operation_uid'],'generation':w['generation'],
                'data_sha256':digest({k:w[k] for k in sorted(self.EDITABLE)})}
            path=self.api.output_path('emissions','EM_WORK_'+w['operation_uid']+'.pdf')
            result=self.api.render(self.api.resolved_design(b['revision_id'],b['variant_id']),w['values'],p,
                indices,count,copies,path,False,per_container=w['per_container'],status=w['status'],work_context=context)
            if hook:hook('RENDERED',w)
            self.assert_current(w,True)
            pk=self.api.add_issue(b['revision_id'],operator,count,copies,indices,w['values'],p,path,
                per_container=w['per_container'],status=w['status'])
            if hook:hook('COMMITTED',w)
            issued=copy.deepcopy(w);issued.update(phase='ISSUED',issue_id=pk,generation=w['generation']+1,updated_at=now())
            self._write(issued,w)
            return issued,path,result
