"""Generated fictional test samples using a disposable database."""
import sys,json,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from synthetic_fixtures import activate_for_script
_synthetic=activate_for_script()
from covex_label_manager.storage import Store
from covex_label_manager.engine import render_emission,render_calibration_page

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'test-results'/'synthetic-samples';DEST.mkdir(parents=True,exist_ok=True)

def main():
 with tempfile.TemporaryDirectory() as temp:
  store=Store(Path(temp)/'data')
  versions={r['name']:store.version(r['version_id']) for r in store.labels()}
  p={'width_mm':156,'height_mm':172,'orientation':'portrait','margin_mm':8,'gap_mm':3,'start_slot':1,'offset_x_mm':0,'offset_y_mm':0}
  ed={'lote':'CV/EDR/TEST-001','pn':'0,1000','pb':'0,2000','conservacion':'Envasar en atmosfera de nitrogeno'}
  ac={'lote':'CV/S-60/TEST-A','cantidad':'25 kg','proveedor':'Proveedor de prueba','direccion':'Madrid','telefono':'900 000 000','observaciones':'Control de prueba','fecha':'08/10/2026','recibido_por':'Operador','muestreado_por':'QC'}
  results=[]
  def emit(name,v,values,prof,indices,total,copies=1,**kw):
   path=DEST/(name+'.pdf');r=render_emission(v,store.root,values,prof,indices,total,copies,path,True,**kw)
   results.append({'file':path.name,**{k:r[k] for k in ('pages','physical','warnings')}})
  for kind in ('sin_analizar','aprobado','rechazado'):
   status={'kind':kind,'fecha':'08/10/2026','persona':'GC','caducidad_reanalisis':'Noviembre-2026','placement':'integrada'}
   emit('EDROFONIO_'+kind,versions['EDROFONIO'],ed,p,[1],1,status=status,status_master=store.status_master(kind))
   emit('ESTADO_'+kind+'_independiente',versions['EDROFONIO'],ed,{**p,'width_mm':153,'height_mm':30},[1,2],2,status={**status,'placement':'independiente'},status_master=store.status_master(kind))
  emit('ACETONA_campos_y_numeracion',versions['ACETONA'],ac,{**p,'width_mm':165,'height_mm':242},[1,2,50],50)
  emit('ACETONA_sin_analizar',versions['ACETONA'],ac,{**p,'width_mm':165,'height_mm':242},[1],1,status={'kind':'sin_analizar','fecha':'08/10/2026','placement':'integrada'},status_master=store.status_master('sin_analizar'))
  emit('EDROFONIO_2_envases_R1',versions['EDROFONIO'],ed,{'width_mm':versions['EDROFONIO']['base_w_mm'],'height_mm':versions['EDROFONIO']['base_h_mm'],**{k:v for k,v in p.items() if k not in ('width_mm','height_mm')}},[1,2],2)
  individual={'2':{'pn':'0,1500','pb':'0,2500'},'3':{'pn':'0,0500','pb':'0,1800'}}
  emit('EDROFONIO_3_envases_2_copias',versions['EDROFONIO'],ed,p,[1,2,3],3,2,per_container=individual,status={'kind':'aprobado','fecha':'08/10/2026','placement':'integrada','caducidad_reanalisis':'Noviembre-2026'},status_master=store.status_master('aprobado'))
  render_calibration_page({**p,'width_mm':80,'height_mm':50},DEST/'CALIBRACION_A4.pdf')
  (DEST/'resultados.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
  store.close()
if __name__=='__main__':main()
