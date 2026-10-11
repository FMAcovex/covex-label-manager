from __future__ import annotations
import json
import shutil
import sqlite3
import hashlib
import re
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
from .paths import data_dir, resource_dir


def now():
    return datetime.now().astimezone().isoformat(timespec='seconds')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(128 * 1024), b''):
            h.update(block)
    return h.hexdigest()


class Store:
    def __init__(self, root=None, seed=True):
        self.root = Path(root) if root else data_dir()
        self.root.mkdir(parents=True, exist_ok=True)
        for sub in ['sources', 'pdf_masters', 'emissions', 'backups', 'cache', 'status_masters']:
            (self.root / sub).mkdir(exist_ok=True)
        self.db_file = self.root / 'labels.sqlite'
        self.db = sqlite3.connect(self.db_file)
        self.db.row_factory = sqlite3.Row
        self._backup_before_migration()
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA journal_mode=WAL')
        self._schema()
        if seed:
            self.seed_data()
            self._seed_r1_variant()

    def _seed_r1_variant(self):
        """Add a pending rendition, preserving all prior versions and custom fields."""
        if self.setting('r1_edrofonio_variant')=='1':return
        from .render_geometry import corrected_edrofonio
        import tempfile
        from .integrity import KNOWN_OVERFLOW_PDF,verify_documents
        row=self.db.execute("SELECT id FROM labels WHERE name='EDROFONIO' AND code='EDR' AND origin='COVEX'").fetchone()
        if not row:return
        base=self.db.execute("SELECT * FROM versions WHERE label_id=? AND version='00'",(row['id'],)).fetchone()
        if not base or base['pdf_sha256']!=KNOWN_OVERFLOW_PDF:return
        try:verify_documents(base,self.root)
        except ValueError:return
        source=self.root/base['master_pdf']
        original=self.root/base['original_file'] if base['original_file'] else None
        if not self.db.execute("SELECT 1 FROM versions WHERE label_id=? AND version='00-R1'",(row['id'],)).fetchone():
            with tempfile.TemporaryDirectory() as temp:
                derived=Path(temp)/'EDROFONIO_R1.pdf'
                crop,fields,area=corrected_edrofonio(source,derived)
                self.add_version(row['id'],'00-R1',derived,original,crop,fields,
                    'Variante de prueba R1: tabla interior adaptada al marco exterior del Word. Requiere revisión; los originales 00 no cambian.',status_area=area)
        self.set_setting('r1_edrofonio_variant','1')

    def _backup_before_migration(self):
        """Take a consistent SQLite snapshot before altering an older schema."""
        tables={r[0] for r in self.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        required={'versions':{'status_area_json','uid'},
                  'issues':{'pdf_sha256','per_container_json','status_json','uid'},
                  'profiles':{'safety_mm'},'labels':{'uid'},'materials':{'uid'}}
        needs=any(table in tables and not cols.issubset(
            {r[1] for r in self.db.execute(f'PRAGMA table_info({table})')})
            for table,cols in required.items())
        if needs:
            dest=self.root/'backups'/('ANTES_MIGRACION_0_2_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.sqlite')
            with sqlite3.connect(dest) as backup:
                self.db.backup(backup)

    @contextmanager
    def txn(self):
        try:
            yield self.db
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def _schema(self):
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS labels (
          id INTEGER PRIMARY KEY, name TEXT NOT NULL, code TEXT DEFAULT '',
          category TEXT DEFAULT '', annex TEXT DEFAULT '', origin TEXT NOT NULL DEFAULT 'COVEX',
          customer TEXT DEFAULT '', ref_customer TEXT DEFAULT '', created_at TEXT NOT NULL,
          UNIQUE(name, category, origin, customer)
        );
        CREATE TABLE IF NOT EXISTS versions (
          id INTEGER PRIMARY KEY, label_id INTEGER NOT NULL REFERENCES labels(id),
          version TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'PENDING',
          master_pdf TEXT NOT NULL, original_file TEXT,
          source_sha256 TEXT NOT NULL, pdf_sha256 TEXT NOT NULL,
          crop_json TEXT NOT NULL, fields_json TEXT NOT NULL DEFAULT '[]',
          base_w_mm REAL NOT NULL, base_h_mm REAL NOT NULL,
          notes TEXT DEFAULT '', created_at TEXT NOT NULL,
          approved_by TEXT, approval_ref TEXT, approved_at TEXT,
          status_area_json TEXT NOT NULL DEFAULT '[]',
          UNIQUE(label_id, version)
        );
        CREATE TABLE IF NOT EXISTS materials (
          id INTEGER PRIMARY KEY, name TEXT NOT NULL, code TEXT NOT NULL,
          category TEXT DEFAULT '', source_ref TEXT DEFAULT '',
          UNIQUE(name, code, category)
        );
        CREATE TABLE IF NOT EXISTS profiles (
          id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE,
          width_mm REAL NOT NULL, height_mm REAL NOT NULL,
          paper TEXT NOT NULL DEFAULT 'A4', orientation TEXT NOT NULL DEFAULT 'portrait',
          margin_mm REAL NOT NULL DEFAULT 8, gap_mm REAL NOT NULL DEFAULT 3,
          offset_x_mm REAL NOT NULL DEFAULT 0, offset_y_mm REAL NOT NULL DEFAULT 0,
          start_slot INTEGER NOT NULL DEFAULT 1, crop_marks INTEGER NOT NULL DEFAULT 0,
          printer_name TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS issues (
          id INTEGER PRIMARY KEY, version_id INTEGER NOT NULL REFERENCES versions(id),
          created_at TEXT NOT NULL, operator TEXT NOT NULL,
          count_containers INTEGER NOT NULL, copies_per_container INTEGER NOT NULL,
          selected_indices TEXT NOT NULL, variables_json TEXT NOT NULL,
          profile_json TEXT NOT NULL, pdf_path TEXT NOT NULL,
          source_issue_id INTEGER REFERENCES issues(id), reason TEXT DEFAULT '',
          status TEXT NOT NULL DEFAULT 'PDF_GENERATED',
          pdf_sha256 TEXT NOT NULL DEFAULT '',
          per_container_json TEXT NOT NULL DEFAULT '{}',
          status_json TEXT NOT NULL DEFAULT '{}'
        );
        CREATE TABLE IF NOT EXISTS status_masters (
          kind TEXT PRIMARY KEY, name TEXT NOT NULL, version TEXT NOT NULL,
          state TEXT NOT NULL DEFAULT 'PENDING', master_pdf TEXT NOT NULL,
          original_file TEXT NOT NULL, pdf_sha256 TEXT NOT NULL, source_sha256 TEXT NOT NULL,
          crop_json TEXT NOT NULL, approved_by TEXT, approval_ref TEXT, approved_at TEXT
        );
        CREATE TABLE IF NOT EXISTS audit (
          id INTEGER PRIMARY KEY, at TEXT NOT NULL, event TEXT NOT NULL,
          subject TEXT NOT NULL, detail TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        ''')
        # Versioned migrations: preserve previous installations and user-entered data.
        for table, name, definition in [
            ('profiles','safety_mm','REAL NOT NULL DEFAULT 0'),
            ('issues','pdf_sha256',"TEXT NOT NULL DEFAULT ''"),
            ('issues','per_container_json',"TEXT NOT NULL DEFAULT '{}'"),
            ('issues','status_json',"TEXT NOT NULL DEFAULT '{}'"),
            ('versions','status_area_json',"TEXT NOT NULL DEFAULT '[]'"),
        ]:
            if name not in [r['name'] for r in self.db.execute(f'PRAGMA table_info({table})')]:
                self.db.execute(f'ALTER TABLE {table} ADD COLUMN {name} {definition}')
        for table in ('labels','versions','materials','issues'):
            if 'uid' not in {r['name'] for r in self.db.execute(f'PRAGMA table_info({table})')}:
                self.db.execute(f"ALTER TABLE {table} ADD COLUMN uid TEXT NOT NULL DEFAULT ''")
            self.db.execute(f"UPDATE {table} SET uid=lower(hex(randomblob(16))) WHERE uid=''")
            self.db.execute(f'CREATE UNIQUE INDEX IF NOT EXISTS {table}_uid ON {table}(uid)')
            self.db.executescript(f"""CREATE TRIGGER IF NOT EXISTS {table}_assign_uid AFTER INSERT ON {table}
                WHEN new.uid='' BEGIN UPDATE {table} SET uid=lower(hex(randomblob(16))) WHERE id=new.id; END;""")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS label_metadata(label_id INTEGER NOT NULL REFERENCES labels(id),
            key TEXT NOT NULL,value TEXT NOT NULL,source_ref TEXT NOT NULL,PRIMARY KEY(label_id,key));
        CREATE TABLE IF NOT EXISTS library_preferences(label_id INTEGER PRIMARY KEY REFERENCES labels(id),
            favorite INTEGER NOT NULL DEFAULT 0,last_used TEXT DEFAULT '',last_version_id INTEGER REFERENCES versions(id));
        """)
        self.db.execute('PRAGMA user_version=3')
        self.db.commit()

    def library_records(self):
        rows=self.db.execute("""SELECT l.*,l.uid label_uid,v.uid version_uid,v.id version_id,v.version,v.state,
            v.base_w_mm,v.base_h_mm,v.notes,COALESCE(p.favorite,0) favorite,COALESCE(p.last_used,'') last_used,
            p.last_version_id FROM labels l JOIN versions v ON v.label_id=l.id
            LEFT JOIN library_preferences p ON p.label_id=l.id ORDER BY l.name,v.id DESC""").fetchall()
        metadata={}
        for m in self.db.execute('SELECT * FROM label_metadata'):
            metadata.setdefault(m['label_id'],{})[m['key']]=m['value']
        result=[]
        for row in rows:
            r=dict(row);r.update(metadata.get(r['id'],{}))
            # Acquisition is provenance; it never substitutes document origin or state.
            r['acquisition']=r.get('acquisition','SIN REGISTRO')
            result.append(r)
        return result

    def set_acquisition(self,label_id,value,source_ref):
        with self.txn() as c:c.execute("INSERT INTO label_metadata VALUES(?,'acquisition',?,?) ON CONFLICT(label_id,key) DO UPDATE SET value=excluded.value,source_ref=excluded.source_ref",(label_id,value,source_ref))

    def set_label_metadata(self,label_id,values,source_ref):
        from .contracts import METADATA_FIELDS
        if not source_ref.strip():raise ValueError('Falta referencia fuente.')
        if not self.db.execute('SELECT 1 FROM labels WHERE id=?',(label_id,)).fetchone():raise ValueError('Etiqueta inexistente.')
        with self.txn() as c:
            for key,value in values.items():
                if key not in METADATA_FIELDS:raise ValueError('Metadato no registrado: '+key)
                c.execute('INSERT INTO label_metadata VALUES(?,?,?,?) ON CONFLICT(label_id,key) DO UPDATE SET value=excluded.value,source_ref=excluded.source_ref',
                    (label_id,key,str(value).strip(),source_ref.strip()))
        self.audit('METADATA',label_id,source_ref)

    def set_favorite(self,label_id,value):
        with self.txn() as c:c.execute('INSERT INTO library_preferences(label_id,favorite) VALUES(?,?) ON CONFLICT(label_id) DO UPDATE SET favorite=excluded.favorite',(label_id,int(value)))

    def mark_recent(self,label_id,version_id):
        v=self.version(version_id)
        if not v or v['label_id']!=label_id:raise ValueError('La revisión no pertenece a la etiqueta.')
        with self.txn() as c:c.execute('INSERT INTO library_preferences(label_id,last_used,last_version_id) VALUES(?,?,?) ON CONFLICT(label_id) DO UPDATE SET last_used=excluded.last_used,last_version_id=excluded.last_version_id',(label_id,datetime.now().astimezone().isoformat(timespec='microseconds'),version_id))

    def audit_entries(self):return self.db.execute('SELECT * FROM audit ORDER BY id DESC LIMIT 8').fetchall()

    def setting(self, key, default=''):
        row = self.db.execute('SELECT value FROM settings WHERE key=?', (key,)).fetchone()
        return row['value'] if row else default

    def set_setting(self, key, value):
        with self.txn() as c:
            c.execute('INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', (key, str(value)))

    def audit(self, event, subject, detail=''):
        with self.txn() as c:
            c.execute('INSERT INTO audit(at,event,subject,detail) VALUES(?,?,?,?)', (now(), event, str(subject), detail))

    def seed_data(self):
        if not self.db.execute('SELECT 1 FROM profiles LIMIT 1').fetchone():
            with self.txn() as c:
                c.execute('''INSERT INTO profiles(name,width_mm,height_mm,orientation,margin_mm,gap_mm)
                             VALUES('A4 - Original (165 x 242)',165,242,'portrait',8,3)''')
                c.execute('''INSERT INTO profiles(name,width_mm,height_mm,orientation,margin_mm,gap_mm)
                             VALUES('Bote pequeno (80 x 50)',80,50,'portrait',8,3)''')
        if not self.db.execute('SELECT 1 FROM materials LIMIT 1').fetchone():
            catalog = resource_dir() / 'cm_materials.json'
            if catalog.exists():
                self.import_materials(json.loads(catalog.read_text(encoding='utf-8')))
        from .geometry import acetona_template, edrofonio_template
        import fitz
        # Demo references are NOT automatically considered approved master designs.
        for name,code,category,annex,filebase,fn in [
            ('ACETONA','S-60','Disolventes y reactivos','Anexo 1','ACETONA_MASTER_00',acetona_template),
            ('EDROFONIO','EDR','Principios activos','Anexo 6','EDROFONIO_MASTER_00',edrofonio_template),
        ]:
            pdf=resource_dir()/(filebase+'.pdf')
            docx=resource_dir()/(filebase+'.docx')
            if not pdf.exists() or self.db.execute('SELECT 1 FROM labels WHERE name=? AND origin=?',(name,'COVEX')).fetchone():
                continue
            from .importer import auto_crop
            crop,_=auto_crop(pdf)
            fields,area=fn(pdf,crop)
            added=self.add_label(name,code,category,annex,'COVEX','','00',pdf,docx,crop,fields,
                'Plantilla procedente del Word proporcionado; posiciones de prueba ancladas en el PDF. Revisar y validar antes de emitir.',
                status_area=area)
            self.set_acquisition(self.version(added)['label_id'],'REFERENCIA INCLUIDA','Word proporcionado: '+docx.name)
        self._seed_status_masters()
        self._upgrade_only_untouched_acetona()
        if not self.setting('operator'):
            self.set_setting('operator','Operador COVEX')

    def _seed_status_masters(self):
        from .geometry import STATUS_CROPS, STATUS_NAMES
        pdf=resource_dir()/'ESTADOS_MASTER_00.pdf'
        source=resource_dir()/'ESTADOS_MASTER_00.docx'
        if not (pdf.exists() and source.exists()):
            return
        target_pdf=self.root/'status_masters'/'ESTADOS_MASTER_00.pdf'
        target_doc=self.root/'status_masters'/'ESTADOS_MASTER_00.docx'
        # Do not overwrite an already imported or potentially modified source.
        if not target_pdf.exists():shutil.copy2(pdf,target_pdf)
        if not target_doc.exists():shutil.copy2(source,target_doc)
        with self.txn() as c:
            for kind,crop in STATUS_CROPS.items():
                c.execute("""INSERT OR IGNORE INTO status_masters(kind,name,version,state,master_pdf,original_file,
                   pdf_sha256,source_sha256,crop_json) VALUES(?,?,?,'PENDING',?,?,?,?,?)""",
                 (kind,STATUS_NAMES[kind],'00','status_masters/ESTADOS_MASTER_00.pdf',
                  'status_masters/ESTADOS_MASTER_00.docx',sha256(target_pdf),sha256(target_doc),json.dumps(crop)))

    def status_master(self,kind):
        return self.db.execute('SELECT * FROM status_masters WHERE kind=?',(kind,)).fetchone()

    def status_masters(self):
        return self.db.execute('SELECT * FROM status_masters ORDER BY kind').fetchall()

    def approve_status_master(self,kind,reviewer,evidence):
        asset=self.status_master(kind)
        if not asset or asset['state']!='PENDING':
            raise ValueError('Etiqueta de estado no encontrada o ya activada.')
        if len(reviewer.strip())<3 or len(evidence.strip())<5:
            raise ValueError('Indique responsable y referencia documental de aprobación.')
        from .storage import sha256
        if sha256(self.root/asset['master_pdf'])!=asset['pdf_sha256'] or sha256(self.root/asset['original_file'])!=asset['source_sha256']:
            raise ValueError('El diseño de estado no coincide con el original.')
        with self.txn() as c:
            c.execute("""UPDATE status_masters SET state='APPROVED',approved_by=?,approval_ref=?,approved_at=?
                         WHERE kind=?""",(reviewer.strip(),evidence.strip(),now(),kind))
        self.audit('APPROVE_STATUS',kind,evidence)

    def _upgrade_only_untouched_acetona(self):
        """Repair v0.1 demo defaults only when not approved and coordinates untouched."""
        from .geometry import acetona_template
        from .importer import auto_crop
        r=self.db.execute("""SELECT v.* FROM versions v JOIN labels l ON l.id=v.label_id
                  WHERE l.name='ACETONA' AND l.origin='COVEX' AND v.version='00' """).fetchone()
        if not r or r['state']!='PENDING':return
        try:
            current=json.loads(r['fields_json'])
            if not (len(current)==7 and current[0]['key']=='lote' and abs(current[0]['x']-.558)<.0001):
                return
            pdf=self.root/r['master_pdf']
            crop=json.loads(r['crop_json'])
            fields,area=acetona_template(pdf,crop)
            self.replace_pending_fields(r['id'],fields,crop,area)
            self.audit('UPGRADE_DEMO',r['id'],'Campos de acetona referenciados en Word (borrador sin modificar)')
        except (OSError,ValueError,KeyError):
            return

    def import_materials(self, items):
        with self.txn() as c:
            for item in items:
                try:
                    c.execute('INSERT OR IGNORE INTO materials(name,code,category,source_ref) VALUES(?,?,?,?)',
                        (item['name'], item['code'], item.get('category',''), item.get('source_ref','CM/V03/03-2026')))
                except (KeyError, ValueError):
                    continue
        self.audit('IMPORT_CM','Catalogo',f'{len(items)} candidatos')

    def material_duplicates(self):
        return self.db.execute('''SELECT code, COUNT(*) total, GROUP_CONCAT(name, ' | ') names FROM materials
          WHERE code <> '' AND code NOT IN ('--------') GROUP BY UPPER(TRIM(code)) HAVING COUNT(*)>1 ORDER BY total DESC,code''').fetchall()

    def materials(self):
        return self.db.execute('SELECT * FROM materials ORDER BY name').fetchall()

    def labels(self, filter_text=''):
        arg=f'%{filter_text.lower()}%'
        return self.db.execute('''SELECT l.*,v.id version_id,v.version,v.state,v.base_w_mm,v.base_h_mm
          FROM labels l LEFT JOIN versions v ON v.id=(SELECT id FROM versions WHERE label_id=l.id
             ORDER BY CASE state WHEN 'APPROVED' THEN 0 WHEN 'PENDING' THEN 1 ELSE 2 END, id DESC LIMIT 1)
          WHERE lower(l.name||' '||l.code||' '||l.category||' '||l.customer) LIKE ? ORDER BY l.name''',(arg,)).fetchall()

    def version(self, id):
        return self.db.execute('''SELECT v.*,l.name,label_id,l.code,l.category,l.annex,l.origin,l.customer,l.ref_customer
          FROM versions v JOIN labels l ON l.id=v.label_id WHERE v.id=?''',(id,)).fetchone()

    def versions(self, label_id):
        return self.db.execute('SELECT * FROM versions WHERE label_id=? ORDER BY id DESC',(label_id,)).fetchall()

    def approved_version(self, label_id):
        return self.db.execute('SELECT * FROM versions WHERE label_id=? AND state="APPROVED" ORDER BY id DESC LIMIT 1',(label_id,)).fetchone()

    def add_label(self,name,code,category,annex,origin,customer,version,pdf,original,crop,fields,notes='',ref_customer='',status_area=None):
        pdf=Path(pdf)
        if not pdf.exists():
            raise FileNotFoundError(pdf)
        with self.txn() as c:
            c.execute('INSERT INTO labels(name,code,category,annex,origin,customer,ref_customer,created_at) VALUES(?,?,?,?,?,?,?,?)',
                (name.strip(),code.strip(),category.strip(),annex.strip(),origin,customer.strip(),ref_customer.strip(),now()))
            label_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
            ver_id=self._add_version(c,label_id,version,pdf,original,crop,fields,notes,status_area)
        self.audit('IMPORT',label_id,f'{name} | {version} | {origin}')
        self.set_acquisition(label_id,'IMPORTADA','Importación local: '+Path(original or pdf).name)
        return ver_id

    def add_version(self,label_id,version,pdf,original,crop,fields,notes='',status_area=None):
        with self.txn() as c:
            v=self._add_version(c,label_id,version,pdf,original,crop,fields,notes,status_area)
        self.audit('NEW_VERSION',v,f'etiqueta={label_id},version={version}')
        return v

    def _add_version(self,c,label_id,version,pdf,original,crop,fields,notes,status_area=None):
        import fitz
        crop=[float(x) for x in crop]
        doc=fitz.open(pdf)
        if not doc.page_count or not (crop[2]>crop[0] and crop[3]>crop[1]):
            raise ValueError('PDF o recorte invalido')
        page=doc[0]
        if crop[0]<0 or crop[1]<0 or crop[2]>page.rect.width+.2 or crop[3]>page.rect.height+.2:
            raise ValueError('El recorte supera los limites del documento')
        mm=25.4/72
        source_hash=sha256(original) if original and Path(original).exists() else sha256(pdf)
        pdf_hash=sha256(pdf)
        if c.execute('SELECT 1 FROM versions WHERE label_id=? AND version=?',(label_id,version)).fetchone():
            raise ValueError('La version ya existe')
        c.execute('''INSERT INTO versions(label_id,version,state,master_pdf,original_file,source_sha256,pdf_sha256,
            crop_json,fields_json,base_w_mm,base_h_mm,notes,created_at,status_area_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (label_id,version,'PENDING','','',source_hash,pdf_hash,json.dumps(crop),json.dumps(fields),
             round((crop[2]-crop[0])*mm,2),round((crop[3]-crop[1])*mm,2),notes,now(),json.dumps(status_area or [])))
        v=c.execute('SELECT last_insert_rowid()').fetchone()[0]
        relpdf=f'pdf_masters/label_{label_id}_v{v}.pdf'
        shutil.copy2(pdf,self.root/relpdf)
        relsource=''
        if original and Path(original).exists():
            relsource=f'sources/label_{label_id}_v{v}{Path(original).suffix.lower()}'
            shutil.copy2(original,self.root/relsource)
        c.execute('UPDATE versions SET master_pdf=?,original_file=? WHERE id=?',(relpdf,relsource,v))
        return v

    def clone_version(self,version_id,version_code,notes):
        v=self.version(version_id)
        if not v:
            raise ValueError('Version no encontrada')
        from .integrity import verify_documents
        verify_documents(v,self.root)
        pdf=self.root/v['master_pdf']
        source=self.root/v['original_file'] if v['original_file'] else None
        return self.add_version(v['label_id'],version_code,pdf,source,json.loads(v['crop_json']),json.loads(v['fields_json']),notes,status_area=json.loads(v['status_area_json'] or '[]'))

    def replace_pending_fields(self,version_id,fields,crop=None,status_area=None):
        v=self.version(version_id)
        if v['state']!='PENDING':
            raise PermissionError('Una version aprobada no se puede editar. Cree una nueva version.')
        crop=json.loads(v['crop_json']) if crop is None else crop
        status_area=json.loads(v['status_area_json'] or '[]') if status_area is None else status_area
        mm=25.4/72
        with self.txn() as c:
            c.execute('UPDATE versions SET fields_json=?,crop_json=?,base_w_mm=?,base_h_mm=?,status_area_json=? WHERE id=?',
               (json.dumps(fields),json.dumps(crop),round((crop[2]-crop[0])*mm,2),round((crop[3]-crop[1])*mm,2),json.dumps(status_area),version_id))
        self.audit('CHANGE_DRAFT',version_id,'Campos y recorte')

    def save_pending_layout(self, version_id, layout, expected, expected_source):
        """Atomic full-layout compare/update for Qt; the schema remains unchanged."""
        from .editor_layout import layout_from_version, validate_layout, source_identity, MM_PER_POINT
        from .integrity import verify_documents
        import fitz
        with self.txn() as c:
            c.execute('BEGIN IMMEDIATE')
            v = self.version(version_id)
            if v is None or v['state'] != 'PENDING':
                raise PermissionError('Solo se guarda el diseño de una revisión pendiente.')
            if layout_from_version(v) != expected:
                raise ValueError('El diseño cambió fuera de Qt; vuelva a abrirlo antes de guardar.')
            if source_identity(v) != expected_source:
                raise ValueError('El documento de referencia cambió; vuelva a abrirlo antes de guardar.')
            verify_documents(v, self.root)
            with fitz.open(self.root/v['master_pdf']) as document:
                validate_layout(layout, list(document[0].rect))
            crop = layout['crop']
            c.execute('UPDATE versions SET fields_json=?,crop_json=?,status_area_json=?,base_w_mm=?,base_h_mm=? WHERE id=?',
                      (json.dumps(layout['fields']), json.dumps(crop), json.dumps(layout['area']),
                       round((crop[2]-crop[0])*MM_PER_POINT, 2), round((crop[3]-crop[1])*MM_PER_POINT, 2), version_id))
            c.execute('INSERT INTO audit(at,event,subject,detail) VALUES(?,?,?,?)',
                      (now(), 'CHANGE_DRAFT', str(version_id), 'Diseño Qt: campos, recorte y zona de estado'))

    def approve(self,version_id,reviewer,evidence):
        v=self.version(version_id)
        if not v or v['state']!='PENDING':
            raise ValueError('Solo se pueden activar versiones pendientes')
        if len(reviewer.strip())<3 or len(evidence.strip())<5:
            raise ValueError('Indique responsable y referencia de aprobacion documental')
        from .integrity import verify_documents,verify_renderable
        verify_documents(v,self.root)
        verify_renderable(v)
        # Closed client PDF labels may intentionally contain no variable fields.
        with self.txn() as c:
            c.execute('UPDATE versions SET state="RETIRED" WHERE label_id=? AND state="APPROVED"',(v['label_id'],))
            c.execute('UPDATE versions SET state="APPROVED",approved_by=?,approval_ref=?,approved_at=? WHERE id=?',
               (reviewer.strip(),evidence.strip(),now(),version_id))
        self.audit('APPROVE',version_id,f'{reviewer} | {evidence}')

    def profile_list(self):
        return self.db.execute('SELECT * FROM profiles ORDER BY name').fetchall()

    def add_profile(self,profile):
        keys=['name','width_mm','height_mm','orientation','margin_mm','gap_mm','offset_x_mm','offset_y_mm','start_slot','crop_marks','printer_name','safety_mm']
        args=[profile.get(k,0) if k=='safety_mm' else profile.get(k) for k in keys]
        with self.txn() as c:
            c.execute('''INSERT INTO profiles(name,width_mm,height_mm,orientation,margin_mm,gap_mm,offset_x_mm,offset_y_mm,start_slot,crop_marks,printer_name,safety_mm)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(name) DO UPDATE SET
               width_mm=excluded.width_mm,height_mm=excluded.height_mm,orientation=excluded.orientation,
               margin_mm=excluded.margin_mm,gap_mm=excluded.gap_mm,offset_x_mm=excluded.offset_x_mm,
               offset_y_mm=excluded.offset_y_mm,start_slot=excluded.start_slot,crop_marks=excluded.crop_marks,
               printer_name=excluded.printer_name,safety_mm=excluded.safety_mm''',args)
        self.audit('PROFILE',profile['name'],'Perfil guardado')

    def add_issue(self,version_id,operator,count,copies,indices,values,profile,pdf_path,source_issue_id=None,reason='',per_container=None,status=None):
        if self.version(version_id)['state']!='APPROVED':
            raise PermissionError('No se puede emitir con una plantilla no aprobada')
        rel=str(Path(pdf_path).relative_to(self.root))
        with self.txn() as c:
            c.execute('''INSERT INTO issues(version_id,created_at,operator,count_containers,copies_per_container,
                selected_indices,variables_json,profile_json,pdf_path,source_issue_id,reason,per_container_json,status_json)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',(version_id,now(),operator,count,copies,json.dumps(indices),
                     json.dumps(values,ensure_ascii=False),json.dumps(profile,ensure_ascii=False),rel,source_issue_id,reason,
                     json.dumps(per_container or {},ensure_ascii=False),json.dumps(status or {},ensure_ascii=False)))
            c.execute('UPDATE issues SET pdf_sha256=? WHERE id=last_insert_rowid()', (sha256(pdf_path),))
            pk=c.execute('SELECT last_insert_rowid()').fetchone()[0]
        self.audit('ISSUE',pk,f'etiqueta={version_id},numeros={indices[:10]},copias={copies},origen={source_issue_id}')
        return pk

    def issues(self):
        return self.db.execute('''SELECT i.*,l.name,v.version,l.origin FROM issues i
           JOIN versions v ON v.id=i.version_id JOIN labels l ON l.id=v.label_id
           ORDER BY i.id DESC''').fetchall()

    def issue(self,id):
        return self.db.execute('SELECT * FROM issues WHERE id=?',(id,)).fetchone()

    def stats(self):
        out={}
        for k,q in [('labels','SELECT COUNT(*) FROM labels'),('approved','SELECT COUNT(*) FROM versions WHERE state="APPROVED"'),
                    ('pending','SELECT COUNT(*) FROM versions WHERE state="PENDING"'),('issues','SELECT COUNT(*) FROM issues'),
                    ('materials','SELECT COUNT(*) FROM materials')]:
            out[k]=self.db.execute(q).fetchone()[0]
        return out

    def close(self):
        self.db.close()
