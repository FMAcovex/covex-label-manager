"""R6A read-only technical preacceptance. Never grants GMP approval."""
import csv
import hashlib
import io
import os
import uuid
import zipfile
from collections import Counter
from pathlib import Path
import fitz
from .canonical import canonical,digest,json_digest
from .storage import sha256
from .integrity import verify_renderable

MANUAL=(
('UAT-01','Windows','Abrir/cerrar portable sin Python en Windows 10/11; rutas con espacios/tildes'),
('UAT-02','IT','Antivirus, SmartScreen, permisos y origen/hash del ejecutable'),
('UAT-03','Respaldo','Copia íntegra, restauración en carpeta aislada y rollback'),
('UAT-04','Word','DOC/DOCX reales: tablas, fuentes, conversión, bordes y recortes'),
('UAT-05','Maestros','Identidad, producto, código, cliente, revisión e idioma'),
('UAT-06','Diseño','Escalado proporcional, ajuste avanzado y revisión de la plantilla'),
('UAT-07','Impresora','Driver, calibración X/Y, papel y tamaño real'),
('UAT-08','Salida física','100 %, legibilidad, márgenes, adhesivo y códigos de barras'),
('UAT-09','Hoja usada','Casillas ocupadas y páginas nuevas posteriores'),
('UAT-10','Emisión','Lotes, numeración, PDF registrado, historial y reimpresión'),
('UAT-11','Seguridad GMP','Bloqueo PENDING/RETIRED/alterado y 00-R1 pendiente'),
('UAT-12','R5','Conciliación y cobertura contra libro máster autorizado'),
('UAT-13','Distribución','Prueba IT, accesos, soporte y ubicaciones autorizadas'),
('UAT-14','Cierre GMP','Evidencias, incidencias, fecha, responsable y autorización documental'),
)

def result(group,subject,code,status,detail):
    return dict(group=group,subject=str(subject),code=code,status=status,detail=str(detail))

def file_guard(root,relative,expected,subject,code,checks,required=True):
    if not relative:
        checks.append(result('FILE',subject,code,'FAIL' if required else 'REVIEW','Documento no asociado.'))
        return None
    try:
        relative=Path(relative)
        if relative.is_absolute() or '..' in relative.parts:raise ValueError('Ruta inválida.')
        path=root
        for component in relative.parts:
            path=path/component
            if path.is_symlink():raise ValueError('Enlace simbólico.')
        path=path.resolve()
        if not path.is_relative_to(root) or not path.is_file():raise ValueError('Documento ausente.')
        if not expected or sha256(path)!=expected:raise ValueError('SHA-256 no conforme.')
    except (ValueError,OSError) as ex:
        checks.append(result('FILE',subject,code,'FAIL',str(ex)));return None
    checks.append(result('FILE',subject,code,'PASS','Documento y hash conformes.'))
    return path

def pdf_guard(path,subject,checks):
    if path is None:return
    try:
        with fitz.open(path) as doc:
            if not doc.page_count:raise ValueError('Sin páginas.')
            if any(p.rect.width<=0 or p.rect.height<=0 for p in doc):
                raise ValueError('Geometría inválida.')
        checks.append(result('PDF',subject,'PDF_READABLE','PASS','PDF legible.'))
    except (Exception) as ex:
        checks.append(result('PDF',subject,'PDF_READABLE','FAIL',str(ex)))

def inspect(api):
    """The full check is read-only; NOT_ACCEPTED remains mandatory."""
    store=api._repository;root=store.root.resolve();checks=[];labels=set();nversions=0
    try:
        rows=store.db.execute('PRAGMA integrity_check').fetchall()
        foreign=store.db.execute('PRAGMA foreign_key_check').fetchall()
        good=(len(rows)==1 and rows[0][0]=='ok' and not foreign)
        checks.append(result('DB','sqlite-v4','SQLITE_INTEGRITY',
                             'PASS' if good else 'FAIL','SQLite integrity/foreign key check.'))
    except Exception as ex:checks.append(result('DB','sqlite-v4','SQLITE_INTEGRITY','FAIL',str(ex)))
    for record in api.library_records():
        row=api.version(record['version_id']);nversions+=1;labels.add(row['label_id'])
        subject='revision:'+str(row['id']);state=row['state']
        if state=='APPROVED':
            ok=bool(row['approved_by'] and row['approval_ref'] and row['approved_at'])
            checks.append(result('REVISION',subject,'APPROVAL_FIELDS','PASS' if ok else 'FAIL',
                                 'Datos de aprobación registrados; verificar evidencia externa.' if ok
                                 else 'Datos de aprobación incompletos.'))
        elif state in ('PENDING','RETIRED'):
            checks.append(result('REVISION',subject,'DOCUMENTARY_REVIEW','REVIEW',
                                 'Pendiente: no emitir.' if state=='PENDING' else 'Retirada: consulta histórica.'))
        else:checks.append(result('REVISION',subject,'STATE','FAIL','Estado desconocido.'))
        pdf_guard(file_guard(root,row['master_pdf'],row['pdf_sha256'],
                  subject,'MASTER_SHA256',checks),subject,checks)
        file_guard(root,row['original_file'],row['source_sha256'],subject,
                   'ORIGINAL_SHA256',checks,False)
        try:verify_renderable(row)
        except ValueError as ex:
            checks.append(result('REVISION',subject,'KNOWN_OVERFLOW',
                                 'FAIL' if state=='APPROVED' else 'REVIEW',str(ex)))
    status_masters=api.status_masters()
    for row in status_masters:
        subject='status:'+row['kind']
        pdf_guard(file_guard(root,row['master_pdf'],row['pdf_sha256'],
                  subject,'STATUS_PDF_SHA256',checks),subject,checks)
        file_guard(root,row['original_file'],row['source_sha256'],subject,
                   'STATUS_ORIGINAL_SHA256',checks)
        if row['state']=='PENDING':
            checks.append(result('STATUS',subject,'DOCUMENTARY_REVIEW','REVIEW','No aprobado.'))
    variants=0
    for row in store.db.execute('SELECT * FROM design_variants'):
        variants+=1;subject='variant:'+str(row['id'])
        try:
            if json_digest(row['design_json'])!=row['design_sha256']:
                raise ValueError('Diseño alterado.')
            checks.append(result('VARIANT',subject,'DESIGN_SHA256','PASS','Hash conforme.'))
            if row['state'] in ('APPROVED','RETIRED') and row['approved_design_sha256']:
                api.variant_evidence(row['id'])
                checks.append(result('VARIANT',subject,'APPROVAL_EVIDENCE',
                                     'PASS','Evidencia vinculada íntegra.'))
            else:checks.append(result('VARIANT',subject,'DOCUMENTARY_REVIEW',
                                      'REVIEW','Sin aprobación de producción acreditada.'))
        except (ValueError,KeyError,TypeError,OSError) as ex:
            checks.append(result('VARIANT',subject,'VARIANT_INTEGRITY','FAIL',str(ex)))
    issues=0
    for row in api.issues():
        issues+=1;subject='issue:'+str(row['id'])
        try:
            from .emission_history import original
            issue,path,snapshot,token=original(store,row['id'])
            checks.append(result('ISSUE',subject,'PDF_SHA256',
                'PASS' if issue['pdf_sha256'] else 'REVIEW',
                'PDF verificado.' if issue['pdf_sha256'] else 'PDF heredado sin hash.'))
            checks.append(result('ISSUE',subject,'SNAPSHOT',
                'PASS' if snapshot else 'REVIEW',
                'Snapshot verificado.' if snapshot else 'Snapshot heredado ausente.'))
        except (ValueError,KeyError,TypeError,OSError) as ex:
            checks.append(result('ISSUE',subject,'ISSUE_INTEGRITY','FAIL',str(ex)))
    counts=Counter(item['status'] for item in checks)
    signature=digest({'checks':checks,'labels':len(labels),'revisions':nversions,
                      'variants':variants,'issues':issues})
    return {'contract':1,'type':'R6A_PREACCEPTANCE','acceptance':'NOT_ACCEPTED',
      'data_fingerprint':signature,
      'scope':{'labels':len(labels),'revisions':nversions,'variants':variants,
               'issues':issues,'status_masters':len(status_masters)},
      'summary':{'pass':counts['PASS'],'fail':counts['FAIL'],
                 'review':counts['REVIEW'],'manual_open':len(MANUAL)},
      'checks':checks,'manual':[{'id':code,'area':area,'criterion':text,
          'result':'NOT_EXECUTED','evidence':'','tester':'','date':'','observations':''}
          for code,area,text in MANUAL],
      'warning':'CI y comprobaciones automáticas no acreditan uso GMP, Word ni impresión física.'}

def csv_protocol(report):
    s=io.StringIO(newline='');w=csv.writer(s,delimiter=';',lineterminator='\r\n')
    keys=('id','area','criterion','result','evidence','tester','date','observations')
    w.writerow(('ID','Área','Criterio','Resultado','Evidencia','Responsable','Fecha','Observaciones'))
    for row in report['manual']:w.writerow([row[k] for k in keys])
    return ('\ufeff'+s.getvalue()).encode('utf-8')

def export(api,report,destination):
    if not isinstance(report,dict) or report.get('type')!='R6A_PREACCEPTANCE':
        raise ValueError('Informe inválido.')
    if inspect(api)['data_fingerprint']!=report['data_fingerprint']:
        raise ValueError('La biblioteca cambió; repita el diagnóstico.')
    target=Path(destination).absolute()
    if target.suffix.lower()!='.zip':raise ValueError('Seleccione un ZIP.')
    if target.resolve().is_relative_to(api._repository.root.resolve()):
        raise PermissionError('Exporte fuera de data.')
    if target.exists():raise FileExistsError('No se sobrescribe un informe previo.')
    if not target.parent.is_dir():raise FileNotFoundError('Carpeta de destino ausente.')
    files={'diagnostico.json':canonical(report).encode('utf-8'),
           'protocolo_aceptacion.csv':csv_protocol(report)}
    manifest={'contract':1,'type':'R6A_TEMPLATE_NOT_GMP_ACCEPTANCE',
              'fingerprint':report['data_fingerprint'],
              'files':{k:hashlib.sha256(v).hexdigest() for k,v in files.items()}}
    tmp=target.with_name(target.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        with zipfile.ZipFile(tmp,'x',compression=zipfile.ZIP_DEFLATED) as z:
            for k,v in files.items():z.writestr(k,v)
            z.writestr('integrity-manifest.json',canonical(manifest))
        with zipfile.ZipFile(tmp) as z:
            for name,checksum in manifest['files'].items():
                if hashlib.sha256(z.read(name)).hexdigest()!=checksum:
                    raise ValueError('Integridad ZIP no conforme.')
        os.replace(tmp,target)
    finally:
        if tmp.exists():tmp.unlink()
    return {'path':str(target),'checks':len(report['checks']),
            'manual':len(MANUAL),'acceptance':'NOT_ACCEPTED'}
