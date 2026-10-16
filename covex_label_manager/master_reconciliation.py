"""R5C: read-only master-list reconciliation and verified ZIP report.

CSV/TSV/XLSX are parsed without new dependencies. No change to documentary
status, SQLite, originals, SharePoint, or production data.
"""
import csv
import hashlib
import io
import os
import posixpath
import re
import uuid
import zipfile
from collections import Counter,defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

from .canonical import canonical,digest
from .library_service import searchable
from .storage import sha256

MAX_BYTES=30_000_000
MAX_XML=35_000_000
MAX_ROWS=20000
MAX_COLUMNS=250
FIELDS=('name','version','code','origin','customer','product','language','state')
STATES={'vigente':'APPROVED','aprobada':'APPROVED','aprobado':'APPROVED',
        'approved':'APPROVED','pending':'PENDING','pendiente':'PENDING',
        'retired':'RETIRED','retirada':'RETIRED','retirado':'RETIRED'}
RESULTS=('MATCHED','MISSING_LABEL','MISSING_REVISION','METADATA_DIFFERENCE',
         'STATE_DIFFERENCE','AMBIGUOUS','DUPLICATE_MASTER_ROW','INVALID_MASTER_ROW')


def norm(x):return searchable(str(x or '').strip())


def source(path):
    file=Path(path).resolve(strict=True)
    if not file.is_file() or file.suffix.lower() not in ('.csv','.tsv','.xlsx'):
        raise ValueError('Seleccione CSV, TSV o XLSX; no se aceptan libros con macros.')
    if not 0<file.stat().st_size<=MAX_BYTES:
        raise ValueError('Archivo máster vacío o superior a 30 MB.')
    return file


def xml(z,name):
    info=z.getinfo(name)
    if info.file_size>MAX_XML:raise ValueError('XML del XLSX demasiado grande.')
    return ET.fromstring(z.read(name))


def tag(node):return node.tag.rsplit('}',1)[-1]


def sheets_in(z):
    book=xml(z,'xl/workbook.xml')
    rels=xml(z,'xl/_rels/workbook.xml.rels')
    paths={}
    for rel in rels:
        if tag(rel)!='Relationship' or rel.get('TargetMode')=='External':continue
        target=rel.get('Target','')
        path=(target.lstrip('/') if target.startswith('/')
              else posixpath.normpath('xl/'+target))
        if not path.startswith('xl/') or '..' in path.split('/'):
            raise ValueError('Enlace externo o ruta XLSX insegura.')
        paths[rel.get('Id')]=path
    out=[]
    for item in book.iter():
        if tag(item)!='sheet':continue
        name=item.get('name')
        rid=next((v for k,v in item.attrib.items() if k.endswith('}id')),None)
        if not name or rid not in paths:raise ValueError('Hoja Excel no disponible.')
        if name in [v[0] for v in out]:raise ValueError('Hojas duplicadas.')
        out.append((name,paths[rid]))
    if not out:raise ValueError('No se encontraron hojas Excel.')
    return out


def source_sheets(path):
    file=source(path)
    if file.suffix.lower()!='.xlsx':return ['CSV/TSV']
    with zipfile.ZipFile(file) as z:return [name for name,_ in sheets_in(z)]


def shape(rows,sheet):
    if not rows:raise ValueError('No hay cabecera en el máster.')
    _,fields,_,_=rows[0]
    width=max(fields)+1
    headers=[fields.get(i,'').strip() for i in range(width)]
    if (not all(headers) or len({norm(k) for k in headers})!=len(headers)):
        raise ValueError('Cabeceras vacías o repetidas; corrija el libro.')
    items=[]
    for number,values,numeric,formulas in rows[1:]:
        entry={'row':number,'values':{h:values.get(i,'').strip() for i,h in enumerate(headers)},
               'numeric':[headers[i] for i in numeric if i<width],
               'formulas':[headers[i] for i in formulas if i<width]}
        if any(entry['values'].values()) or entry['formulas']:items.append(entry)
    return {'sheet':sheet,'headers':headers,'rows':items}


def read_csv(path):
    data=path.read_bytes()
    try:text=data.decode('utf-8-sig')
    except UnicodeDecodeError:text=data.decode('cp1252')
    try:dialect=csv.Sniffer().sniff(text[:8192],delimiters=',;\t')
    except csv.Error:dialect=csv.excel_tab if path.suffix.lower()=='.tsv' else csv.excel
    rows=[]
    for number,cols in enumerate(csv.reader(io.StringIO(text,newline=''),dialect),1):
        if len(cols)>MAX_COLUMNS:raise ValueError('Demasiadas columnas.')
        if not any(v.strip() for v in cols):continue
        rows.append((number,{i:str(v).strip() for i,v in enumerate(cols)},set(),set()))
        if len(rows)>MAX_ROWS+1:raise ValueError('Máster con demasiadas filas.')
    return shape(rows,'CSV/TSV')


def read_xlsx(path,sheet=None):
    with zipfile.ZipFile(path) as z:
        names=sheets_in(z)
        if sheet is None:sheet=names[0][0]
        chosen=[target for name,target in names if name==sheet]
        if len(chosen)!=1:raise ValueError('Seleccione una hoja del archivo.')
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            string_root=xml(z,'xl/sharedStrings.xml')
            for item in string_root:
                if tag(item)=='si':
                    strings.append(''.join(part.text or '' for part in item.iter() if tag(part)=='t'))
        root=xml(z,chosen[0])
        rows=[];cells=0
        for item in root.iter():
            if tag(item)!='row':continue
            fields={};numeric=set();formulas=set()
            try:number=int(item.get('r',str(len(rows)+1)))
            except ValueError:raise ValueError('Número de fila Excel inválido.')
            for cell in item:
                if tag(cell)!='c':continue
                match=re.match(r'([A-Z]+)',cell.get('r',''))
                if not match:raise ValueError('Referencia de celda inválida.')
                index=0
                for char in match.group(1):index=index*26+ord(char)-64
                index-=1
                if index>=MAX_COLUMNS:raise ValueError('Demasiadas columnas Excel.')
                if index in fields:raise ValueError('Celda XLSX repetida.')
                mode=cell.get('t','')
                formula=any(tag(ch)=='f' for ch in cell)
                if formula:
                    value='';formulas.add(index)
                elif mode=='inlineStr':
                    value=''.join(ch.text or '' for ch in cell.iter() if tag(ch)=='t')
                else:
                    value=next((ch.text or '' for ch in cell if tag(ch)=='v'),'')
                    if mode=='s':
                        try:value=strings[int(value)]
                        except (ValueError,IndexError):raise ValueError('Texto compartido de Excel inválido.')
                    elif value and mode not in ('str','e','b'):numeric.add(index)
                fields[index]=str(value).strip()
                cells+=1
                if cells>400000:raise ValueError('Demasiadas celdas Excel.')
            if (fields and any(fields.values())) or formulas:
                rows.append((number,fields,numeric,formulas))
                if len(rows)>MAX_ROWS+1:raise ValueError('Demasiadas filas Excel.')
    return shape(rows,sheet)


def read_master(path,sheet=None):
    file=source(path)
    return read_xlsx(file,sheet) if file.suffix.lower()=='.xlsx' else read_csv(file)


def checked_mapping(table,mapping):
    if not isinstance(mapping,dict):raise ValueError('Configure columnas.')
    fields={key:mapping.get(key) or None for key in FIELDS}
    if not fields['name'] or not fields['version']:
        raise ValueError('Indique las columnas de nombre y revisión.')
    selected=[v for v in fields.values() if v]
    if len(selected)!=len(set(selected)) or any(v not in table['headers'] for v in selected):
        raise ValueError('Columnas duplicadas o inexistentes.')
    return fields


def master_values(entry,mapping):
    values={key:entry['values'].get(col,'').strip() if col else '' for key,col in mapping.items()}
    errors=[]
    for name in ('name','code','version'):
        if mapping[name] in entry['numeric']:
            errors.append(name+': celda numérica Excel; guarde como texto para conservar ceros.')
    if any(col in entry['formulas'] for col in mapping.values() if col):
        errors.append('Fórmula Excel no evaluada. Pegue valores como texto.')
    if not values['name'] or not values['version']:errors.append('Nombre y revisión obligatorios.')
    if values['state']:
        state=STATES.get(norm(values['state']))
        if not state:errors.append('Estado del máster no reconocido.')
        else:values['state']=state
    return values,errors


def catalog_rows(api):
    return [{key:row.get(key,'') for key in
        ('id','version_id','name','version','code','origin','customer',
         'product','language','state','category','annex')}
        for row in api.library_records()]


def match_identity(master,catalog):
    found=set()
    for item in catalog:
        if master['origin'] and norm(item['origin'])!=norm(master['origin']):continue
        if master['customer'] and norm(item['customer'])!=norm(master['customer']):continue
        if norm(item['name'])==norm(master['name']) or (master['code'] and norm(item['code'])==norm(master['code'])):
            found.add(item['id'])
    return found


def item_result(entry,master,status,revision_ids=(),differences=()):
    return {'source_row':entry['row'],'status':status,'master':master,
            'catalog_revision_ids':sorted(set(revision_ids)),
            'differences':list(differences)}


def reconcile(api,path,sheet,mapping):
    master_file=source(path)
    table=read_master(master_file,sheet)
    mapping=checked_mapping(table,mapping)
    catalog=catalog_rows(api)
    by_label=defaultdict(list)
    for item in catalog:by_label[item['id']].append(item)
    results=[];matched=set();seen=set()
    for entry in table['rows']:
        master,errors=master_values(entry,mapping)
        if errors:
            results.append(item_result(entry,master,'INVALID_MASTER_ROW',differences=errors));continue
        key=tuple(norm(master[k]) for k in ('name','code','origin','customer','version'))
        if key in seen:
            results.append(item_result(entry,master,'DUPLICATE_MASTER_ROW'));continue
        seen.add(key)
        possibilities=match_identity(master,catalog)
        if not possibilities:
            results.append(item_result(entry,master,'MISSING_LABEL'));continue
        if len(possibilities)>1:
            results.append(item_result(entry,master,'AMBIGUOUS',differences=[
                'Posibles registros de etiqueta: '+', '.join(map(str,sorted(possibilities)))]));continue
        label_id=next(iter(possibilities))
        revision=[item for item in by_label[label_id]
                  if norm(item['version'])==norm(master['version'])]
        if len(revision)!=1:
            results.append(item_result(entry,master,'MISSING_REVISION',differences=[
                'Etiqueta encontrada; no existe la revisión '+master['version']]));continue
        item=revision[0];matched.add(item['version_id'])
        differences=[]
        for field in ('name','code','origin','customer','product','language'):
            if master[field] and norm(master[field])!=norm(item[field]):
                differences.append(field+': máster «'+master[field]+'» / aplicación «'+str(item[field])+'»')
        if master['state'] and master['state']!=item['state']:
            results.append(item_result(entry,master,'STATE_DIFFERENCE',[item['version_id']],[
                'Estado máster '+master['state']+' / aplicación '+item['state']]+differences))
        elif differences:
            results.append(item_result(entry,master,'METADATA_DIFFERENCE',[item['version_id']],differences))
        else:
            results.append(item_result(entry,master,'MATCHED',[item['version_id']]))
    extra=[{'label_id':item['id'],'version_id':item['version_id'],'name':item['name'],
            'code':item['code'],'revision':item['version'],'state':item['state']}
           for item in catalog if item['version_id'] not in matched]
    counts=Counter(r['status'] for r in results)
    compared=sum(counts.get(name,0) for name in
                 ('MATCHED','MISSING_LABEL','MISSING_REVISION','METADATA_DIFFERENCE',
                  'STATE_DIFFERENCE','AMBIGUOUS'))
    return {'contract':1,'type':'R5C_READ_ONLY_RECONCILIATION',
            'input':{'name':master_file.name,'sha256':sha256(master_file),
                     'sheet':table['sheet'],'mapping':mapping,'rows':len(table['rows'])},
            'catalog_sha256':digest(catalog),
            'summary':{'master_rows':len(results),'compared':compared,
                       'matched':counts['MATCHED'],
                       'coverage_percent':round(counts['MATCHED']*100/compared,2) if compared else None,
                       'extra_app_revisions':len(extra),
                       'counts':{name:counts.get(name,0) for name in RESULTS}},
            'results':results,'only_in_app':extra,
            'warning':('Conciliación informativa, no equivale a aprobación GMP. '
                       'Listado máster posiblemente parcial: elementos SOLO EN APP no deben borrarse.')}


def csv_safe(value):
    value=str(value if value is not None else '')
    return "'"+value if value.lstrip().startswith(('=','+','-','@','\t','\r')) else value


def report_csv(report):
    file=io.StringIO(newline='')
    writer=csv.writer(file,delimiter=';',lineterminator='\r\n')
    writer.writerow(['Fuente','Fila','Resultado','Nombre','Código','Revisión','Origen',
                     'Cliente','IDs de revisión','Diferencias'])
    for record in report['results']:
        m=record['master']
        writer.writerow([csv_safe(x) for x in
            ('LIBRO MÁSTER',record['source_row'],record['status'],m['name'],m['code'],
             m['version'],m['origin'],m['customer'],
             ','.join(map(str,record['catalog_revision_ids'])),' | '.join(record['differences']))])
    for row in report['only_in_app']:
        writer.writerow([csv_safe(x) for x in
            ('SOLO EN APLICACIÓN','','ONLY_IN_APP',row['name'],row['code'],
             row['revision'],'','',row['version_id'],
             'Verificar alcance del listado; no retirar automáticamente')])
    return ('\ufeff'+file.getvalue()).encode('utf-8')


def export_report(api,master,report,destination):
    if sha256(source(master))!=report['input']['sha256']:
        raise ValueError('El libro máster ha cambiado. Repita la conciliación.')
    if digest(catalog_rows(api))!=report['catalog_sha256']:
        raise ValueError('El catálogo ha cambiado. Repita la conciliación.')
    target=Path(destination).absolute()
    if target.suffix.lower()!='.zip':raise ValueError('Elija un archivo ZIP.')
    if target.resolve().is_relative_to(api._repository.root.resolve()):
        raise PermissionError('No se exporta dentro de los datos protegidos.')
    if target.exists():raise FileExistsError('No se sobrescriben informes.')
    if not target.parent.is_dir():raise FileNotFoundError('Carpeta de destino inexistente.')
    contents={'conciliacion.csv':report_csv(report),
              'conciliacion.json':canonical(report).encode('utf-8')}
    manifest={'contract':1,'type':'R5C_REPORT_NOT_BACKUP',
              'source_sha256':report['input']['sha256'],
              'catalog_sha256':report['catalog_sha256'],
              'files':{k:hashlib.sha256(v).hexdigest() for k,v in contents.items()}}
    tmp=target.with_name(target.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        with zipfile.ZipFile(tmp,'x',compression=zipfile.ZIP_DEFLATED) as z:
            for k,v in contents.items():z.writestr(k,v)
            z.writestr('report-manifest.json',canonical(manifest))
        with zipfile.ZipFile(tmp) as z:
            for k,expected in manifest['files'].items():
                if hashlib.sha256(z.read(k)).hexdigest()!=expected:
                    raise ValueError('Error en integridad del informe.')
        os.replace(tmp,target)
    finally:
        if tmp.exists():tmp.unlink()
    return {'path':str(target),'rows':len(report['results']),'assets':len(contents)}
