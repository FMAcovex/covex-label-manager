"""CAS, atomic, integrity protected sidecar profiles. No SQLite schema change."""
import json
import re
from .canonical import digest, parse
from .migration_v4 import atomic_json
from .emission_work import file_lock, WorkConflict
from .engine import plan_sheet
from .storage import now

class LayoutProfiles:
    def __init__(self,root):
        (root/'emission_work').mkdir(exist_ok=True)
        self.root=root/'layout_profiles';self.root.mkdir(exist_ok=True)
        if self.root.is_symlink():raise ValueError('Carpeta de perfiles inválida.')
        self.invalid_files=[]
    def path(self,uid):
        if not re.fullmatch('[a-zA-Z0-9_-]{1,64}',uid):raise ValueError('Identificador de perfil inválido.')
        return self.root/(uid+'.json')
    def get(self,uid):
        path=self.path(uid)
        if path.is_symlink():raise ValueError('Perfil inválido.')
        raw=path.read_text(encoding='utf-8');parse(raw);e=json.loads(raw)
        if e.get('contract')!=1 or e.get('hash')!=digest(e['payload']):raise ValueError('Integridad o versión de perfil inválida.')
        plan_sheet(e['payload']['profile'],1)
        return e['payload']
    def save(self,uid,name,profile,expected=0):
        if 'trial_appearance' in profile:
            raise ValueError('Los perfiles guardan formato físico, no apariencia temporal. Use Copiar trabajo o una variante documental para conservarla.')
        path=self.path(uid)
        if not name.strip():raise ValueError('Nombre obligatorio.')
        plan_sheet(profile,1)
        with file_lock(self.root.parent/'emission_work'/'catalog.lock'), file_lock(self.root/'catalog.lock'):
            previous=self.get(uid) if path.exists() else None
            if (previous['generation'] if previous else 0)!=expected:raise WorkConflict('El perfil cambió. Recargue antes de guardar.')
            p=dict(uid=uid,name=name.strip(),profile=profile,generation=expected+1,updated_at=now())
            atomic_json(path,dict(contract=1,payload=p,hash=digest(p)))
            return p
    def list(self, *, tolerate_corrupt=False):
        """Keep valid profiles usable when an unrelated sidecar is corrupt.

        The strict default still fails closed for callers requiring full
        catalog integrity. Tolerant UI listings never repair or overwrite files.
        """
        found=[];self.invalid_files=[]
        for path in sorted(self.root.glob('*.json')):
            try:found.append(self.get(path.stem))
            except (OSError,ValueError,KeyError,TypeError):
                if not tolerate_corrupt:raise
                self.invalid_files.append(path.name)
        return found
