"""Local application boundary. UI has no SQLite connection or data-root access.

The whitelist retains existing use cases while the library has its own explicit
contract. This is an incremental extraction, not a network service.
"""
from pathlib import Path
from datetime import datetime
import tempfile
import zipfile
import sqlite3
from contextlib import closing
import fitz
from .storage import Store,sha256
from .library_service import LibraryService
from .engine import render_emission,render_label_thumbnail,render_calibration_page
from .importer import auto_crop,docx_to_pdf

class LocalServices:
    OPERATIONS=frozenset('add_issue add_label add_profile approve approve_status_master audit clone_version close import_materials issue issues labels material_duplicates profile_list replace_pending_fields set_setting setting stats status_master status_masters version versions audit_entries library_records set_favorite mark_recent set_label_metadata'.split())
    def __init__(self,repository=None,*,migration_confirmation=None):
        self._repository=repository or Store(migration_confirmation=migration_confirmation)
        self.library=LibraryService(self._repository)
        from .emission_work import WorkRepository
        self.work=WorkRepository(self)
    def __getattr__(self,name):
        if name in self.OPERATIONS:return getattr(self._repository,name)
        raise AttributeError(name)
    def asset_path(self,relative):
        root=self._repository.root.resolve();p=(root/relative).resolve()
        if not p.is_relative_to(root):raise ValueError('Ruta fuera de los datos de la aplicación.')
        return p
    def file_exists(self,path):return Path(path).exists()
    def read_cm(self,path):
        from .cm import parse_cm
        return parse_cm(path)
    def importable_files(self,path):
        from .importer import list_importable_files
        return list_importable_files(path)
    def location(self):return str(self._repository.root)
    def output_path(self,kind,name):
        if kind not in ('cache','emissions','backups'):raise ValueError('Destino no permitido.')
        if Path(name).name!=name:raise ValueError('Nombre de salida inválido.')
        return self.asset_path(str(Path(kind)/name))
    def render(self,version,*args,**kwargs):
        from .emission_contract import render
        return render(self,version,*args,**kwargs)
    def emission_version(self,version_id):
        variant_id=getattr(self,'selected_variant_id',None)
        if variant_id is not None and self._repository.variants.get(variant_id)['revision_id']!=version_id:
            self.selected_variant_id=None;variant_id=None
        return self._repository.variants.resolve(version_id,variant_id,False)[0]
    def variants(self,revision_id):return self._repository.variants.list(revision_id)
    def variant(self,variant_id):return self._repository.variants.get(variant_id)
    def create_variant(self,*args,**kwargs):return self._repository.variants.create(*args,**kwargs)
    def save_variant(self,*args,**kwargs):return self._repository.variants.save(*args,**kwargs)
    def transition_variant(self,*args,**kwargs):return self._repository.variants.transition(*args,**kwargs)
    def approve_variant(self,*args,**kwargs):return self._repository.variants.approve(*args,**kwargs)
    def variant_evidence(self,variant_id):return self._repository.variants.verify_evidence(self.variant(variant_id))
    def resolved_design(self,revision_id,variant_id=None,production=False):
        return self._repository.variants.resolve(revision_id,variant_id,production)[0]
    def sheet_plan(self,profile,count):
        from .engine import plan_sheet
        return plan_sheet(profile,count)
    def preview_pdf(self,path,**kwargs):
        from .engine import preview_pdf
        return preview_pdf(path,**kwargs)
    def calibration(self,profile,destination):return render_calibration_page(profile,destination)
    def thumbnail(self,version,**kwargs):return render_label_thumbnail(version,self._repository.root,**kwargs)
    def master_preview(self,version,width=470,height=560):
        from PIL import Image
        with fitz.open(self.asset_path(version['master_pdf'])) as d:
            rect=d[0].rect;zoom=min(width/rect.width,height/rect.height)
            pix=d[0].get_pixmap(matrix=fitz.Matrix(zoom,zoom),alpha=False)
            return Image.frombytes('RGB',(pix.width,pix.height),pix.samples),rect,zoom
    def master_spans(self,version):
        with fitz.open(self.asset_path(version['master_pdf'])) as d:
            return [sp for bl in d[0].get_text('dict')['blocks'] for line in bl.get('lines',[]) for sp in line['spans'] if sp['text'].strip()]
    def locate_fields(self,version,crop):
        from .geometry import acetona_template,edrofonio_template
        from .geometry import span_for
        with fitz.open(self.asset_path(version['master_pdf'])) as document:
            try:corrected=version['name']=='EDROFONIO' and span_for(document[0],'Nº de envase/Total de envases')['bbox'][2]<475
            except ValueError:corrected=False
        if corrected:
            import json
            from .geometry import rebase_layout
            fields=json.loads(version['fields_json']);area=json.loads(version['status_area_json'])
            saved_crop=json.loads(version['crop_json'])
            return (fields,area) if saved_crop==crop else rebase_layout(fields,area,saved_crop,crop)
        mode=acetona_template if version['name'].upper()=='ACETONA' else edrofonio_template
        return mode(self.asset_path(version['master_pdf']),crop)
    def intact_emission(self,issue):return not issue['pdf_sha256'] or sha256(self.asset_path(issue['pdf_path']))==issue['pdf_sha256']
    def import_label(self,path,data):
        with tempfile.TemporaryDirectory(prefix='covex_import_') as temp:
            pdf=docx_to_pdf(path,temp);crop,info=auto_crop(pdf)
            if info['page_count']>1:raise ValueError('Documento multipágina: prepare la página concreta en PDF antes de importar.')
            return self.add_label(data['name'],data.get('code',''),data.get('category',''),data.get('annex',''),data.get('origin','COVEX'),data.get('customer',''),data['version'],pdf,path,crop,[],
                'Importacion inicial. Revisar recorte y campos; documento de origen: '+Path(path).name+'.',data.get('ref_customer',''))
    def backup(self):
        from .migration_v4 import inventory,verify_backup
        from .canonical import canonical
        target=self.output_path('backups',f'covex_labels_backup_{datetime.now():%Y%m%d_%H%M%S_%f}.zip')
        with tempfile.TemporaryDirectory() as temp:
            snapshot=Path(temp)/'snapshot.sqlite'
            with closing(sqlite3.connect(snapshot)) as db:self._repository.db.backup(db)
            root=self._repository.root
            # Capture every durable file, including approval evidence and the
            # legacy barrier. Exclude both the live v4 DB/WAL and old backups.
            files={}
            for f in sorted(root.rglob('*')):
                rel=f.relative_to(root)
                if {'backups','cache'} & set(rel.parts) or f.name.endswith('.lock') or f.name.endswith('.tmp'):continue
                if f.is_symlink():raise ValueError('No se incluyen enlaces en una copia controlada.')
                if f.is_file() and f not in (self._repository.db_file,Path(str(self._repository.db_file)+'-wal'),Path(str(self._repository.db_file)+'-shm')):
                    files[rel.as_posix()]=sha256(f)
            database=self._repository.db_file.relative_to(root).as_posix();files[database]=sha256(snapshot)
            with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED) as archive:
                archive.write(snapshot,database)
                for rel in files:
                    if rel!=database:archive.write(root/rel,rel)
                archive.writestr('backup-manifest.json',canonical({'contract':1,'files':files}))
            verify_backup(target)
        self.audit('BACKUP','ZIP',target.name)
        return target
