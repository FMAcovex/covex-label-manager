"""Read-only preparation checks. Definitive authority stays in work.issue + SQLite."""
import json
import math
import unicodedata
from .emission_work import parameters
from .engine import validate_fields,_status_settings
from .status_combined import resolve_status
from .vessels import validate_vessel_masses,parse_mass


def review(api,uid,generation):
    w=api.work.get(uid)
    result={'errors':[],'warnings':[],'summary':None,'proof_allowed':False,'production_allowed':False}
    def error(target,message,recipient=None):
        item={'target':target,'message':str(message),'recipient':recipient}
        if item not in result['errors'] and len(result['errors'])<30:result['errors'].append(item)
    if w['generation']!=generation:error('work','El trabajo cambió en otra ventana. Recargue antes de continuar.');return result
    try:api.work.assert_current(w,False)
    except (ValueError,OSError) as ex:error('document',ex);return result
    b=w['binding'];version=api.resolved_design(b['revision_id'],b['variant_id'],False)
    for key,title,maximum in [('count','Recipientes',10000),('copies','Copias por recipiente',2)]:
        try:
            value=int(w[key])
            if not 1<=value<=maximum:raise ValueError()
        except (ValueError,TypeError):error(key,f'{title}: indique un entero entre 1 y {maximum}.')
    if result['errors']:return result
    from .emission_work import selection_indices
    try:selection_indices(w.get('selection',''),int(w['count']))
    except ValueError as ex:error('selection',ex);return result
    for key in ('width_mm','height_mm','margin_mm','gap_mm','offset_x_mm','offset_y_mm','safety_mm','start_slot'):
        try:
            number=float(str(w['profile'].get(key,0)).replace(',','.'))
            if not math.isfinite(number):raise ValueError()
        except (ValueError,TypeError):error(key,'Introduzca una medida numérica válida.')
    if result['errors']:return result
    try:
        p,indices,count,copies=parameters(w)
        for key in ('width_mm','height_mm','margin_mm','gap_mm','offset_x_mm','offset_y_mm','safety_mm'):
            if not math.isfinite(float(p.get(key,0))):raise ValueError('Formato: use medidas finitas.')
        plan=api.sheet_plan(p,len(indices)*copies)
        result['summary']={'containers':count,'selected':len(indices),'copies':copies,'physical':plan.count_physical,
            'pages':plan.pages,'capacity':plan.capacity,'cols':plan.cols,'rows':plan.rows,'start_slot':p['start_slot'],
            'width_mm':p['width_mm'],'height_mm':p['height_mm'],'orientation':p.get('orientation','portrait')}
        result['proof_allowed']=True
    except (ValueError,OverflowError,TypeError) as ex:
        keys=['start_slot'] if 'casilla' in str(ex).lower() else ['width_mm','height_mm','margin_mm','gap_mm']
        for key in keys:error(key,ex)
        return result
    if w['phase']!='DRAFT':error('work','Trabajo emitido o interrumpido. Copie o recupere antes de emitir.')
    try:api.work.assert_current(w,True)
    except (ValueError,OSError) as ex:error('document',ex)
    fields=json.loads(version['fields_json'])
    normalized=lambda data:{unicodedata.normalize('NFC',k):v for k,v in data.items()}
    for field in fields:field['key']=unicodedata.normalize('NFC',field['key'])
    version=dict(version,fields_json=json.dumps(fields))
    from .sheet_layout import slots
    boxes=slots(p,plan.cols,plan.rows)
    smallest=min(boxes,key=lambda box:min(box.width/version['base_w_mm'],box.height/version['base_h_mm']))
    effective={**p,'width_mm':smallest.width,'height_mm':smallest.height}
    for number in indices:
        overrides=w['per_container'].get(str(number),{})
        values=normalized(w['values']);values.update(normalized(overrides))
        for message in validate_fields(version,values,effective,strict=False):
            field=next((f for f in fields if f.get('label',f['key']) in message),None)
            key=field['key'] if field else 'format'
            error('container:'+key if key in overrides else 'value:'+key,message,number if key in overrides else None)
        valid_masses=True
        for key in ('pn','pb'):
            try:parse_mass(values.get(key))
            except ValueError as ex:
                valid_masses=False
                error('container:'+key if key in overrides else 'value:'+key,ex,number if key in overrides else None)
        if valid_masses:
            try:validate_vessel_masses(values,number)
            except ValueError as ex:error('container:pb' if 'pb' in overrides else 'value:pb',ex,number if 'pb' in overrides else None)
    state=w['status'];kind=state.get('kind','ninguna')
    if kind!='ninguna':
        try:
            document,_,_=_status_settings(state,resolve_status(api._repository,state),api._repository.root,version,False)
            if document:document.close()
        except (ValueError,OSError) as ex:error('status:fecha' if 'fecha' in str(ex).lower() else 'status',ex)
    from .canonical import digest
    result['token']=digest([w,dict(resolve_status(api._repository,state)) if kind!='ninguna' and resolve_status(api._repository,state) is not None else None])
    result['production_allowed']=not result['errors']
    if p.get('trial_appearance') is not None:
        result['production_allowed']=False
        result['warnings'].append('PRUEBA / NO GMP · Apariencia temporal. Restablezca el diseño o cree una variante para revisión y aprobación externa.')
    if not any(f['key']=='numero' for f in fields) and len(indices)>1:
        result['warnings'].append('La plantilla no tiene numeración: varios recipientes producirán etiquetas con el mismo aspecto.')
    return result
