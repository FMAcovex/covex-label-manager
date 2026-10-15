"""Run the unchanged R3D readers against disposable R3E contracts."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from covex_label_manager.qt_ui.demo import DemoSession
from covex_label_manager.sheet_layout import template

p=argparse.ArgumentParser();p.add_argument('--previous-source',type=Path,required=True);a=p.parse_args()
s=DemoSession()
try:
    api=s.services;vid=next(r['version_id'] for r in api.library.entries() if r['state']=='APPROVED');w=api.work.create(vid,None,'Synthetic compatibility')
    profile=dict(w['profile'],layout_version=1,paper='A3',layout_mode='free');profile['slots']=template(profile,5)
    w=api.work.save(w['uid'],w['generation'],{'profile':profile,'values':{'lote':'SYNTH','pn':'1','pb':'2'}})
    issued,path,result=api.work.issue(w['uid'],w['generation'],'Synthetic operator')
    code='''import json,sys
from pathlib import Path
from covex_label_manager.qt_transition import TransitionServices
from covex_label_manager.storage import Store
from covex_label_manager.emission_work import WorkUnsupported
from covex_label_manager.emission_history import HistoryService
api=TransitionServices(Store(Path(sys.argv[1]),seed=False));checks={}
try:api.work.get(sys.argv[2])
except WorkUnsupported:checks['old_work_reader_rejects']=True
report=HistoryService(api).inspect(int(sys.argv[3]));checks['old_reproduction_rejects']=not report['reprint_allowed']
api.close();print(json.dumps(checks));assert len(checks)==2 and all(checks.values())
'''
    r=subprocess.run([sys.executable,'-c',code,str(api._repository.root),w['uid'],str(issued['issue_id'])],cwd=a.previous_source.resolve(),capture_output=True,text=True,timeout=45)
    print(r.stdout);print(r.stderr);assert r.returncode==0
finally:s.close()
