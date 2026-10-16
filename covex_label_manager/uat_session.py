"""R6B field UAT: explicit evidence record, never software GMP approval."""
import hashlib,json,os,re,uuid,zipfile
from pathlib import Path
from datetime import date
from .canonical import canonical,parse
from .acceptance_preflight import MANUAL

VALID=('NOT_EXECUTED','PASS','FAIL','BLOCKED','NOT_APPLICABLE')
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for part in iter(lambda:f.read(131072),b''):h.update(part)
    return h.hexdigest()
def load_r6a(p):
    with zipfile.ZipFile(p) as z:
        expected={'diagnostico.json','protocolo_aceptacion.csv','integrity-manifest.json'}
        if set(z.namelist())!=expected or len(z.namelist())!=3:raise ValueError('Paquete R6A desconocido.')
        if any(info.file_size>10000000 for info in z.infolist()):raise ValueError('Paquete demasiado grande.')
        manifest=parse(z.read('integrity-manifest.json').decode('utf8'))
        report=parse(z.read('diagnostico.json').decode('utf8'))
        if manifest.get('type')!='R6A_TEMPLATE_NOT_GMP_ACCEPTANCE' or report.get('type')!='R6A_PREACCEPTANCE' or report.get('acceptance')!='NOT_ACCEPTED':raise ValueError('Origen R6A no permitido.')
        if set(manifest['files'])!={'diagnostico.json','protocolo_aceptacion.csv'}:raise ValueError('Manifest incompleto.')
        if any(hashlib.sha256(z.read(n)).hexdigest()!=d for n,d in manifest['files'].items()):raise ValueError('Manifest R6A corrupto.')
        if manifest['fingerprint']!=report['data_fingerprint']:raise ValueError('Huella R6A inconsistente.')
        if [x['id'] for x in report['manual']]!=[x[0] for x in MANUAL]:raise ValueError('Protocolo diferente.')
    return {'sha256':sha(p),'fingerprint':report['data_fingerprint']}
def _outside(api,p):
    p=Path(p).absolute()
    if p.resolve().is_relative_to(api._repository.root.resolve()):raise PermissionError('Guardar fuera de data.')
    return p
def _save_new(p,data):
    with p.open('x',encoding='utf-8') as f:
        f.write(canonical(data));f.flush();os.fsync(f.fileno())
def create(api,pack,destination,environment):
    p=_outside(api,destination)
    if p.suffix.lower()!='.json':raise ValueError('Sesión JSON obligatoria.')
    if not p.parent.is_dir():raise ValueError('Carpeta destino ausente.')
    if any(not str(environment.get(k,'')).strip() for k in ('machine','windows','tester','commit','portable_sha256')):raise ValueError('Identifique el entorno, operador, commit y hash del portable.')
    if not re.fullmatch(r'[a-fA-F0-9]{40}',str(environment['commit'])) or not re.fullmatch(r'[a-fA-F0-9]{64}',str(environment['portable_sha256'])):raise ValueError('Commit/hash no válidos.')
    source=load_r6a(pack)
    report={'contract':1,'type':'R6B_FIELD_UAT','acceptance':'NOT_ACCEPTED','uid':uuid.uuid4().hex,'generation':1,'origin':source,'environment':environment,'cases':[{'id':a,'area':b,'criterion':c,'status':'NOT_EXECUTED','tester':'','date':'','notes':'','evidence':[]} for a,b,c in MANUAL]}
    _save_new(p,report)
    return report
def read(path):
    with Path(path).open(encoding='utf8') as f:report=parse(f.read())
    if (report.get('contract')!=1 or report.get('type')!='R6B_FIELD_UAT' or report.get('acceptance')!='NOT_ACCEPTED' or type(report.get('generation')) is not int or report['generation']<1 or [x['id'] for x in report.get('cases',[])]!=[x[0] for x in MANUAL] or any(x.get('status') not in VALID for x in report['cases'])):raise ValueError('Sesión incompatible.')
    return report
def update(api,path,generation,case,status,tester='',when='',notes='',evidence=None):
    if status not in VALID:raise ValueError('Estado UAT inválido.')
    p=_outside(api,path);r=read(p)
    if r['generation']!=generation:raise ValueError('Generación obsoleta.')
    item=next((c for c in r['cases'] if c['id']==case),None)
    if item is None:raise ValueError('Caso inexistente.')
    if status!='NOT_EXECUTED':
        if not tester.strip() or not when:raise ValueError('Responsable y fecha obligatorios.')
        if date.fromisoformat(when)>date.today():raise ValueError('Fecha futura.')
    if status in ('FAIL','BLOCKED','NOT_APPLICABLE') and not notes.strip():raise ValueError('Motivo obligatorio.')
    references=list(item['evidence'])
    if evidence:
        f=Path(evidence).resolve(strict=True)
        if not f.is_file() or f.is_relative_to(api._repository.root.resolve()) or not 0<f.stat().st_size<=25000000:raise ValueError('Evidencia no autorizada o demasiado grande.')
        references.append({'name':f.name,'path':str(f),'sha256':sha(f),'bytes':f.stat().st_size})
    if status=='PASS' and not references:raise ValueError('Conforme requiere evidencia.')
    if status=='PASS' and verify_evidence({'cases':[{'id':case,'evidence':references}]}):
        raise ValueError('La evidencia está ausente o su SHA-256 ha cambiado.')
    data={**r,'cases':[dict(c) for c in r['cases']],'generation':generation+1}
    next(c for c in data['cases'] if c['id']==case).update(status=status,tester=tester,date=when,notes=notes,evidence=references)
    target=p.with_name(p.stem+'.g'+str(generation+1)+'.json')
    _save_new(target,data)
    return str(target)
def verify_evidence(report):
    issues=[]
    for case in report['cases']:
        for evidence in case['evidence']:
            path=Path(evidence['path'])
            try:
                if (not path.is_file() or path.stat().st_size!=evidence['bytes']
                    or sha(path)!=evidence['sha256']):
                    issues.append(case['id'])
            except (OSError,KeyError,TypeError,ValueError):
                issues.append(case['id'])
    return sorted(set(issues))
