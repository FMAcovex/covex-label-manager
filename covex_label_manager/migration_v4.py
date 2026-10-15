"""Offline v3 -> v4 migration, verified complete backup and restart recovery.

No Store import: no seeds/legacy initializer can run while examining data.
A phase hook is for deterministic interruption tests, never production control.
"""
import json
import os
import shutil
import sqlite3
import uuid
import zipfile
from contextlib import contextmanager, closing
from pathlib import Path
from datetime import datetime
from .canonical import canonical, digest
from .schema_v4 import apply, CHECKSUM, configure

FORMAT='storage-format.json'
JOURNAL='migration-v4.json'
ACTIVE=Path('storage_v4')/'labels.sqlite'
PHASES=('PREPARED','LEGACY_ISOLATED','BARRIER_INSTALLED','PUBLISHED','VERIFIED')


def now():return datetime.now().astimezone().isoformat(timespec='microseconds')
def sha(path):
    import hashlib
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for part in iter(lambda:f.read(131072),b''):h.update(part)
    return h.hexdigest()


def atomic_json(path,value):
    path=Path(path);temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    with open(temp,'x',encoding='utf-8') as f:
        f.write(canonical(value));f.flush();os.fsync(f.fileno())
    os.replace(temp,path)
    if os.name!='nt':
        fd=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(fd)
        finally:os.close(fd)


def read_json(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def ro(path):return sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True,timeout=1)


def integrity(db):
    if db.execute('PRAGMA integrity_check').fetchall()!=[('ok',)]:raise ValueError('Integridad SQLite no conforme.')
    if db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Relaciones SQLite no conformes.')


def old_rows(db):
    out={}
    for (table,) in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
        if not table.replace('_','').isalnum():raise ValueError('Tabla no reconocida.')
        cols=[r[1] for r in db.execute(f'PRAGMA table_info({table})')]
        out[table]={'columns':cols,'rows':sorted([list(r) for r in db.execute(f'SELECT * FROM {table}')],key=canonical)}
    return out


def check_rows(db,before):
    for table,record in before.items():
        cols=','.join('"'+c+'"' for c in record['columns'])
        actual=sorted([list(r) for r in db.execute(f'SELECT {cols} FROM "{table}"')],key=canonical)
        expected=record['rows']
        if table=='settings':actual=[r for r in actual if r[0] not in ('storage_format','minimum_writer_protocol')]
        if actual!=expected:raise ValueError('Contenido histórico modificado: '+table)


def referenced_files(db,root):
    for table in ('versions','status_masters'):
        for row in db.execute(f'SELECT master_pdf,pdf_sha256,original_file,source_sha256 FROM {table}'):
            for rel,expected in ((row[0],row[1]),(row[2],row[3])):
                if rel:
                    path=safe_file(root,rel)
                    if sha(path)!=expected:raise ValueError('Hash fuente no conforme: '+rel)
    issue_cols={r[1] for r in db.execute('PRAGMA table_info(issues)')}
    hash_column='pdf_sha256' if 'pdf_sha256' in issue_cols else "''"
    for rel,expected in db.execute('SELECT pdf_path,'+hash_column+' FROM issues'):
        path=safe_file(root,rel)
        if expected and sha(path)!=expected:raise ValueError('Hash emisión no conforme: '+rel)


def safe_file(root,rel):
    root=Path(root).resolve();p=root/rel
    if Path(rel).is_absolute() or not p.resolve().is_relative_to(root) or not p.is_file() or p.is_symlink():
        raise ValueError('Archivo ausente o fuera de data: '+str(rel))
    return p


def validate_legacy(db):
    version=db.execute('PRAGMA user_version').fetchone()[0]
    if version not in (0,1,2,3):raise ValueError('Formato legacy desconocido.')
    tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    required={'labels','versions','materials','profiles','issues','status_masters','audit','settings'}
    if not required.issubset(tables) or tables-required-{'label_metadata','library_preferences'}:
        raise ValueError('Esquema legacy desconocido/parcial.')
    for table in ('labels','versions','issues','materials'):
        cols={r[1] for r in db.execute(f'PRAGMA table_info({table})')}
        if 'uid' in cols and db.execute(f"SELECT 1 FROM {table} WHERE uid='' OR uid IS NULL").fetchone():raise ValueError('UID existente inválido.')
    integrity(db)


def normalize_legacy_v3(db,root):
    # Existing, tested 0.1/0.2 additive normalizer, applied ONLY to staging.
    # No seeds/files/labels are created; existing nonempty UIDs stay unchanged.
    from .storage import Store
    staging=Store.__new__(Store);staging.db=db;staging.root=Path(root)
    original_factory=db.row_factory;db.row_factory=sqlite3.Row
    try:staging._schema()
    finally:db.row_factory=original_factory
    validate_v3(db)


def validate_v3(db):
    if db.execute('PRAGMA user_version').fetchone()[0]!=3:raise ValueError('Solo se migra el formato 3 reconocido.')
    tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    expected={'labels','versions','materials','profiles','issues','status_masters','audit','settings','label_metadata','library_preferences'}
    if tables!=expected:raise ValueError('Esquema v3 desconocido/parcial; no se modifica.')
    columns={
        'labels':'id name code category annex origin customer ref_customer created_at uid',
        'versions':'id label_id version state master_pdf original_file source_sha256 pdf_sha256 crop_json fields_json base_w_mm base_h_mm notes created_at approved_by approval_ref approved_at status_area_json uid',
        'materials':'id name code category source_ref uid',
        'profiles':'id name width_mm height_mm paper orientation margin_mm gap_mm offset_x_mm offset_y_mm start_slot crop_marks printer_name safety_mm',
        'issues':'id version_id created_at operator count_containers copies_per_container selected_indices variables_json profile_json pdf_path source_issue_id reason status pdf_sha256 per_container_json status_json uid',
        'status_masters':'kind name version state master_pdf original_file pdf_sha256 source_sha256 crop_json approved_by approval_ref approved_at',
        'audit':'id at event subject detail','settings':'key value',
        'label_metadata':'label_id key value source_ref',
        'library_preferences':'label_id favorite last_used last_version_id'}
    for table,names in columns.items():
        if set(names.split())!={r[1] for r in db.execute(f'PRAGMA table_info({table})')}:
            raise ValueError('Columnas v3 desconocidas/parciales: '+table)
    for table,cols in {'labels':{'uid'},'versions':{'uid','status_area_json'},'issues':{'uid','pdf_sha256','per_container_json','status_json'},'profiles':{'safety_mm'}}.items():
        if not cols.issubset({r[1] for r in db.execute(f'PRAGMA table_info({table})')}):raise ValueError('Esquema v3 incompleto.')
    for table in ('labels','versions','issues','materials'):
        if db.execute(f"SELECT 1 FROM {table} WHERE uid='' OR uid IS NULL LIMIT 1").fetchone():raise ValueError('UID histórico vacío.')
    integrity(db)


def validate_v4(path):
    with closing(ro(path)) as db:
        integrity(db)
        if db.execute('PRAGMA user_version').fetchone()[0]!=4:raise ValueError('Formato activo no es v4.')
        row=db.execute('SELECT migration_checksum FROM schema_migrations WHERE version=4').fetchone()
        if row!=(CHECKSUM,):raise ValueError('Contrato de migración incompatible.')
        if dict(db.execute("SELECT key,value FROM settings WHERE key IN ('storage_format','minimum_writer_protocol')"))!={'storage_format':'4','minimum_writer_protocol':'4'}:raise ValueError('Protocolo escritor incompatible.')
        for table in ('design_variants','issues'):
            if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone():raise ValueError('Formato parcial.')
        # Exact required table/index/trigger definitions, not just a user_version marker.
        for sql in __import__('covex_label_manager.schema_v4',fromlist=['STATEMENTS']).STATEMENTS:
            if sql.startswith('ALTER '):continue
            parts=sql.split();name=parts[2].split('(')[0]
            stored=db.execute('SELECT sql FROM sqlite_master WHERE name=?',(name,)).fetchone()
            normalize=lambda s:' '.join(s.split()).lower()
            if not stored or normalize(stored[0])!=normalize(sql):raise ValueError('Esquema v4 alterado: '+name)


@contextmanager
def folder_lock(root):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    path=root/'migration.lock'
    with open(path,'a+b') as file:
        file.seek(0);file.write(b'0');file.flush();file.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(file.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(file,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as e:raise PermissionError('Otra instancia gestiona esta carpeta.') from e
        try:yield
        finally:
            file.seek(0)
            if os.name=='nt':msvcrt.locking(file.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(file,fcntl.LOCK_UN)


@contextmanager
def offline_guard(path):
    """Deny old readers/writers in Windows, before touching any legacy file.

    FILE_SHARE_DELETE permits our rename; absence of READ/WRITE sharing denies
    subsequent SQLite handles. An existing SQLite reader/writer makes this fail.
    Other platforms require offline migration and SQLite EXCLUSIVE for writers.
    """
    if os.name=='nt':
        import ctypes
        from ctypes import wintypes
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        create=kernel.CreateFileW
        create.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,wintypes.LPVOID,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
        create.restype=wintypes.HANDLE
        handles=[];opened=[]
        try:
            for p in (Path(path),Path(str(path)+'-wal'),Path(str(path)+'-shm')):
                if not p.exists():continue
                handle=create(str(p),0x80000000|0x40000000,4,None,3,0x80,None)
                if handle==wintypes.HANDLE(-1).value:raise PermissionError('Cierre todos los procesos: base legacy ocupada.')
                handles.append(handle);opened.append(p)
            import hashlib
            physical={}
            for p,handle in zip(opened,handles):
                h=hashlib.sha256();buf=ctypes.create_string_buffer(131072);count=wintypes.DWORD()
                while True:
                    if not kernel.ReadFile(wintypes.HANDLE(handle),buf,len(buf),ctypes.byref(count),None):
                        raise OSError('No se pudo verificar el handle legacy.')
                    if not count.value:break
                    h.update(buf.raw[:count.value])
                physical[p.name]=h.hexdigest()
            yield physical
        finally:
            for handle in reversed(handles):kernel.CloseHandle(wintypes.HANDLE(handle))
    else:
        # OS advisory locks alone cannot exclude an uncooperative old reader.
        with closing(sqlite3.connect(path,timeout=0)) as db:
            db.execute('BEGIN EXCLUSIVE')
            try:yield {p.name:sha(p) for p in (Path(path),Path(str(path)+'-wal'),Path(str(path)+'-shm')) if p.exists()}
            finally:db.rollback()


def inventory(root):
    out={}
    for p in sorted(Path(root).rglob('*')):
        rel=p.relative_to(root)
        if set(rel.parts)&{'backups','cache','storage_v4'} or rel.name in {FORMAT,JOURNAL,'migration.lock',FORMAT+'.tmp',JOURNAL+'.tmp','labels.sqlite','labels.sqlite-wal','labels.sqlite-shm'}:continue
        if p.is_symlink():raise ValueError('Enlace no admitido en backup: '+str(rel))
        if p.is_file():out[rel.as_posix()]=sha(p)
    return out


def make_backup(root,area,db):
    snap=area/'legacy-snapshot.sqlite'
    with closing(sqlite3.connect(snap)) as target:db.backup(target)
    files=inventory(root);files['labels.sqlite']=sha(snap)
    archive=area/'pre-v4.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
        z.write(snap,'labels.sqlite')
        for rel in files:
            if rel!='labels.sqlite':z.write(root/rel,rel)
        z.writestr('backup-manifest.json',canonical({'contract':1,'files':files}))
    verify_backup(archive)
    return archive,snap,files


def verify_backup(archive):
    import hashlib
    with zipfile.ZipFile(archive) as z:
        manifest=json.loads(z.read('backup-manifest.json'))
        if len(z.namelist())!=len(set(z.namelist())):raise ValueError('Backup con nombres duplicados.')
        if set(z.namelist())!=set(manifest['files'])|{'backup-manifest.json'}:raise ValueError('Inventario backup no coincide.')
        for rel,expected in manifest['files'].items():
            if Path(rel).is_absolute() or '..' in Path(rel).parts or '\\' in rel:raise ValueError('Ruta backup inválida.')
            if hashlib.sha256(z.read(rel)).hexdigest()!=expected:raise ValueError('Backup corrupto: '+rel)
    return manifest


def restore_backup(archive,destination):
    manifest=verify_backup(archive);destination=Path(destination)
    if destination.exists():raise ValueError('Restaurar en una carpeta nueva, nunca sobre datos existentes.')
    destination.mkdir(parents=True)
    with zipfile.ZipFile(archive) as z:
        for rel in manifest['files']:
            p=destination/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(rel))
    if (destination/ACTIVE).is_file():active_path(destination)
    else:
        with closing(ro(destination/'labels.sqlite')) as db:validate_legacy(db)
    return destination


def active_path(root):
    root=Path(root)
    if not (root/FORMAT).exists():
        if (root/ACTIVE).exists() or (root/JOURNAL).exists() or (root/'labels.sqlite').is_dir():raise ValueError('Migración incompleta: use recuperación.')
        return root/'labels.sqlite'
    fmt=read_json(root/FORMAT)
    if fmt.get('storage_format')!=4 or fmt.get('minimum_writer_protocol')!=4:raise ValueError('Versión de almacenamiento incompatible.')
    if not (root/'labels.sqlite').is_dir():raise ValueError('Falta barrera legacy; escritura bloqueada.')
    if not (root/JOURNAL).is_file() or read_json(root/JOURNAL).get('phase')!='VERIFIED':raise ValueError('Corte incompleto: use recuperación.')
    validate_v4(root/ACTIVE)
    return root/ACTIVE


def migrate(root,hook=None):
    """Explicit offline operation. Returns receipt, never seeds a legacy database."""
    root=Path(root).resolve()
    with folder_lock(root):
        if (root/FORMAT).exists():active_path(root);return read_json(root/JOURNAL)
        if (root/JOURNAL).exists():raise ValueError('Migración interrumpida: recuperar antes de reintentar.')
        legacy=root/'labels.sqlite'
        if not legacy.is_file():raise ValueError('No hay base v3 que migrar.')
        # Gather a SQLite-consistent snapshot before OS-exclusive cutover, then
        # lock and compare byte hashes of all legacy files before publishing.
        with closing(ro(legacy)) as db:
            validate_legacy(db);referenced_files(db,root);before=old_rows(db)
            migration_id=uuid.uuid4().hex;area=root/'backups'/('v4-'+migration_id);area.mkdir(parents=True)
            required=sum(p.stat().st_size for p in root.rglob('*') if p.is_file() and 'backups' not in p.relative_to(root).parts)
            if shutil.disk_usage(root).free<required*3+10_000_000:raise OSError('Espacio insuficiente para backup, staging y recuperación.')
            archive,snap,files=make_backup(root,area,db)
        staged=area/'staged.sqlite';shutil.copy2(snap,staged)
        with closing(sqlite3.connect(staged)) as db:
            normalize_legacy_v3(db,root)
            apply(db,now(),'R3B2');integrity(db);check_rows(db,before)
            if db.execute('SELECT count(*) FROM design_variants').fetchone()[0]:raise ValueError('Conversión histórica indebida.')
            if db.execute('SELECT 1 FROM issues WHERE design_variant_id IS NOT NULL OR design_snapshot_json IS NOT NULL OR design_snapshot_sha256 IS NOT NULL').fetchone():raise ValueError('Snapshot histórico modificado.')
        validate_v4(staged)
        receipt={'migration_id':migration_id,'phase':'PREPARED','area':str(area.relative_to(root)),
                 'backup_sha256':sha(archive),'row_digest':digest(before),'files':files,'staged_sha256':sha(staged)}
        def phase(name):
            receipt['phase']=name;atomic_json(root/JOURNAL,receipt)
            if hook:hook(name,root)
        # Files may have changed during backup: compare live rows and contents
        # again, checkpoint/close, then verify physical DB/WAL/SHM under OS guard.
        with closing(sqlite3.connect(legacy,timeout=0)) as db:
            db.execute('BEGIN IMMEDIATE');validate_legacy(db);check_rows(db,before);referenced_files(db,root)
            if inventory(root)!={k:v for k,v in files.items() if k!='labels.sqlite'}:raise ValueError('Archivos cambiaron durante backup.')
            db.rollback()
            result=db.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone()
            if result and result[0]:raise PermissionError('Hay lectores legacy activos.')
        physical={p.name:sha(p) for p in (legacy,Path(str(legacy)+'-wal'),Path(str(legacy)+'-shm')) if p.exists()}
        with offline_guard(legacy) as guarded:
            if (guarded!=physical if os.name=='nt' else guarded.get('labels.sqlite')!=physical.get('labels.sqlite')):raise ValueError('Base cambió antes del corte; vuelva a iniciar.')
            phase('PREPARED')
            for suffix in ('','-wal','-shm'):
                p=Path(str(legacy)+suffix)
                if p.exists():os.rename(p,area/('legacy-original.sqlite'+suffix))
            phase('LEGACY_ISOLATED')
            # mkdir(exist_ok=False): a racing old process creates an unexpected
            # file here -> fail, preserve it, do not publish v4 or delete it.
            legacy.mkdir()
            (legacy/'INCOMPATIBLE.txt').write_text('Formato v4: use el portable R3B2. Restaurar v3 en otra carpeta.',encoding='utf-8')
            phase('BARRIER_INSTALLED')
            (root/ACTIVE).parent.mkdir(exist_ok=False)
            os.rename(staged,root/ACTIVE)
            atomic_json(root/FORMAT,{'storage_format':4,'minimum_writer_protocol':4,'migration_id':migration_id})
            phase('PUBLISHED')
            validate_v4(root/ACTIVE)
            with closing(sqlite3.connect(root/ACTIVE)) as db:
                configure(db);check_rows(db,before)
                db.execute('INSERT INTO audit(at,event,subject,detail) VALUES(?,?,?,?)',(now(),'MIGRATE_V4',migration_id,canonical({'backup_sha256':receipt['backup_sha256'],'row_digest':receipt['row_digest']})));db.commit()
            phase('VERIFIED')
        return receipt


def recover(root):
    """Finish a published valid cut, or restore pre-cut v3. Never merge histories."""
    root=Path(root).resolve()
    with folder_lock(root):
        receipt=read_json(root/JOURNAL)
        area=(root/receipt['area']).resolve()
        if not area.is_relative_to(root/'backups'):raise ValueError('Journal de recuperación inválido.')
        archive=area/'pre-v4.zip'
        if sha(archive)!=receipt['backup_sha256']:raise ValueError('Backup no coincide con recibo.')
        verify_backup(archive)
        if receipt['phase'] in ('PUBLISHED','VERIFIED'):
            if not (root/'labels.sqlite').is_dir():raise ValueError('Barrera ausente: recuperar manualmente en carpeta nueva.')
            validate_v4(root/ACTIVE)
            if read_json(root/FORMAT).get('migration_id')!=receipt['migration_id']:raise ValueError('Identidad de corte no coincide.')
            with closing(sqlite3.connect(root/ACTIVE)) as db:
                configure(db);referenced_files(db,root)
                if not db.execute("SELECT 1 FROM audit WHERE event='MIGRATE_V4' AND subject=?",(receipt['migration_id'],)).fetchone():
                    db.execute('INSERT INTO audit(at,event,subject,detail) VALUES(?,?,?,?)',(now(),'MIGRATE_V4',receipt['migration_id'],canonical({'recovered':True,'backup_sha256':receipt['backup_sha256'],'row_digest':receipt['row_digest']})));db.commit()
            receipt['phase']='VERIFIED';atomic_json(root/JOURNAL,receipt)
            return 'v4'
        legacy=root/'labels.sqlite'
        original=area/'legacy-original.sqlite'
        if legacy.is_file() and original.exists():raise ValueError('Base legacy inesperada: conservar ambas y recuperar en carpeta nueva.')
        if legacy.is_file():
            with closing(ro(legacy)) as db:validate_legacy(db)
        else:
            if (root/ACTIVE).exists():raise ValueError('Existe v4 no publicada: recuperar en carpeta nueva.')
            if legacy.exists():
                if not legacy.is_dir() or set(p.name for p in legacy.iterdir())!={'INCOMPATIBLE.txt'}:raise ValueError('Barrera desconocida.')
                shutil.rmtree(legacy)
            if not original.exists():raise ValueError('Original legacy ausente; restaurar backup en carpeta nueva.')
            for suffix in ('','-wal','-shm'):
                p=area/('legacy-original.sqlite'+suffix)
                if p.exists():os.rename(p,Path(str(legacy)+suffix))
            with closing(ro(legacy)) as db:validate_legacy(db)
        (root/JOURNAL).unlink()
        return 'v3'


def recovery_cli(arguments):
    """Same offline recovery in source and portable entries; no UI/server required."""
    import argparse
    parser=argparse.ArgumentParser(description='Recuperación de una migración interrumpida')
    parser.add_argument('--recover-data',type=Path,required=True)
    parser.add_argument('--recovery-report',type=Path,required=True)
    args=parser.parse_args(arguments)
    result=recover(args.recover_data)
    args.recovery_report.parent.mkdir(parents=True,exist_ok=True)
    args.recovery_report.write_text(json.dumps({'ok':True,'recovered_format':result}),encoding='utf-8')
    return 0


if __name__=='__main__':
    import sys
    sys.exit(recovery_cli(sys.argv[1:]))
