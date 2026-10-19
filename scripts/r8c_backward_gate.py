"""Unmodified R8B readers must not silently reinterpret R8C render contracts."""
import argparse
from datetime import date
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from covex_label_manager.qt_ui.demo import DemoSession
from covex_label_manager.typography import DEFAULT

p=argparse.ArgumentParser();p.add_argument('--previous-source',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
session=DemoSession()
try:
    api=session.services;vid=next(v['id'] for v in api.versions(api.version(session.initial_id)['label_id']) if v['state']=='APPROVED')
    row=api.create_variant(vid,'R8C-SYN','SYNTHETIC contract','SYNTHETIC fixture only','SYN')
    design=json.loads(row['design_json']);field=next(f for f in design['layout']['fields'] if f['key']=='lote')
    field.update(typography=DEFAULT,font_pt=9)
    row=api.save_variant(row['id'],row['generation'],design,'SYN')
    row=api.transition_variant(row['id'],row['generation'],'PENDING','SYN')
    evidence=session.root/'SYNTHETIC-EVIDENCE.txt';evidence.write_text('SYNTHETIC external approval fixture only',encoding='utf-8')
    row=api.approve_variant(row['id'],row['generation'],'SYN QA','SYN EXTERNAL',date.today().isoformat(),evidence,'SYN')
    w=api.work.create(vid,row['id'],'SYNTHETIC R8C backwards')
    w=api.work.save(w['uid'],w['generation'],{'values':{'lote':'SYN-01','cantidad':'1 kg','proveedor':'SYN','direccion':'SYN','telefono':'123','observaciones':'SYN'}})
    issued,path,result=api.work.issue(w['uid'],w['generation'],'SYN')
    assert api.history.inspect(issued['issue_id'])['reprint_allowed']
    code='''import json,sys
from pathlib import Path
from covex_label_manager.qt_transition import TransitionServices
from covex_label_manager.storage import Store
from covex_label_manager.emission_work import WorkUnsupported
api=TransitionServices(Store(Path(sys.argv[1]),seed=False));checks={}
try:api.work.get(sys.argv[2])
except WorkUnsupported:checks['old_work_reader_rejects']=True
result=api.history.inspect(int(sys.argv[3]));checks['old_reproduction_rejects']=not result['reprint_allowed']
api.close();print(json.dumps(checks));assert len(checks)==2 and all(checks.values())
'''
    run=subprocess.run([sys.executable,'-c',code,api.location(),w['uid'],str(issued['issue_id'])],cwd=a.previous_source.resolve(),text=True,capture_output=True,timeout=45)
    print(run.stdout);print(run.stderr);assert run.returncode==0
    result=dict(ok=True,synthetic_only=True,checks=json.loads(run.stdout))
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2),encoding='utf-8')
finally:session.close()
