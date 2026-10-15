"""Reproducible synthetic migration gate; Windows old source and real frozen entrypoints."""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from contextlib import closing

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from covex_label_manager.migration_v4 import migrate,recover,active_path,sha,ro,old_rows,restore_backup,PHASES
from covex_label_manager.canonical import digest,canonical


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--crash',nargs=2)
    parser.add_argument('--legacy-source',type=Path);parser.add_argument('--legacy-tk',type=Path);parser.add_argument('--legacy-qt',type=Path)
    parser.add_argument('--report',type=Path);args=parser.parse_args()
    if args.crash:
        root,phase=args.crash
        migrate(root,lambda name,_:os._exit(73) if name==phase else None)
        raise RuntimeError('Crash hook did not execute')
    from synthetic_fixtures import activate_for_script
    fixture=activate_for_script()
    from v3_fixture import create as Store
    from decimal import Decimal
    vector={'z':-0.0,'é':Decimal('1.2300'),'a':[1e-7,'e\u0301']}
    assert digest(vector)=='c59ed642cbc30ff3b0fbcea26eb3c0e32718a6ebfc1a4ce16959401d83ce33ad'
    results={'canonical_vector':{'text':canonical(vector),'sha256':digest(vector)},'synthetic_only':True,'platform':sys.platform,'crashes':[],'old_writers':[]}
    with tempfile.TemporaryDirectory(prefix='r3b2-migration-gate-') as temp:
        temp=Path(temp)
        for phase in PHASES:
            root=temp/phase
            with closing(Store(root)) as s:before=digest(old_rows(s.db))
            process=subprocess.run([sys.executable,__file__,'--crash',str(root),phase],capture_output=True,text=True,timeout=45)
            assert process.returncode==73,(phase,process.stdout,process.stderr)
            outcome=recover(root)
            if outcome=='v3':
                with closing(ro(root/'labels.sqlite')) as db:assert digest(old_rows(db))==before
                migrate(root)
            receipt=json.loads((root/'migration-v4.json').read_text())
            archive=root/receipt['area']/'pre-v4.zip'
            restored=restore_backup(archive,temp/(phase+'-restore'))
            with closing(ro(restored/'labels.sqlite')) as db:assert digest(old_rows(db))==before
            results['crashes'].append({'phase':phase,'exit_code':73,'recovered':outcome,'restored_row_digest':before,'backup_sha256':sha(archive),'restore_exact':True})
        root=temp/'old-writer-proof'
        with closing(Store(root)):pass
        commands=[]
        if args.legacy_source:
            commands += [('source-tk',[sys.executable,str(args.legacy_source.resolve()/'main.py')]),('source-qt',[sys.executable,str(args.legacy_source.resolve()/'main_qt.py')])]
        for name,path in [('exe-tk',args.legacy_tk),('exe-qt',args.legacy_qt)]:
            if path:commands.append((name,[str(path.resolve())]))
        env=dict(os.environ,COVEX_LABEL_DATA=str(root),QT_QPA_PLATFORM='offscreen')
        def old_attempts(stage):
            for name,cmd in commands:
                before={p.relative_to(root).as_posix():sha(p) for p in root.rglob('*') if p.is_file() and 'backups' not in p.relative_to(root).parts and p.name!='migration.lock'}
                p=subprocess.run(cmd,capture_output=True,text=True,timeout=40,env=env,cwd=temp)
                output=p.stdout+p.stderr
                assert p.returncode!=0 and ('unable to open database' in output or 'database is locked' in output),(stage,name,p.returncode,output)
                after={p.relative_to(root).as_posix():sha(p) for p in root.rglob('*') if p.is_file() and 'backups' not in p.relative_to(root).parts and p.name!='migration.lock'}
                assert before==after,(stage,name,'old executable changed data')
                results['old_writers'].append({'stage':stage,'entrypoint':name,'exit_code':p.returncode,'blocked':True,'data_unchanged':True,'diagnostic':output[-1800:]})
        def hook(phase,_):
            # Under Windows OS guard, reading DB by a second handle is denied.
            if phase=='PREPARED' and sys.platform=='win32':
                for name,cmd in commands:
                    p=subprocess.run(cmd,capture_output=True,text=True,timeout=40,env=env,cwd=temp)
                    assert p.returncode!=0 and 'unable to open database' in p.stdout+p.stderr,(name,p.stderr)
                    results['old_writers'].append({'stage':'OS_GUARDED','entrypoint':name,'exit_code':p.returncode,'blocked':True})
        migrate(root,hook)
        old_attempts('V4_BARRIER')
        results['active_v4_sha256']=sha(active_path(root))
        results['windows_old_executables_proven']=sys.platform=='win32' and len(commands)==4
        if sys.platform=='win32':assert results['windows_old_executables_proven']
    fixture.cleanup();results['ok']=True
    if args.report:args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(results,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
