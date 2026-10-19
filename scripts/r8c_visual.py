"""Same synthetic fixture against verified R8B and R8C; no user data."""
import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source-root',type=Path,default=Path(__file__).resolve().parents[1])
p.add_argument('--baseline',action='store_true')
p.add_argument('--report',type=Path,required=True);p.add_argument('--capture',type=Path,required=True)
a=p.parse_args();sys.path.insert(0,str(a.source_root.resolve()))
commit=subprocess.run(['git','-C',str(a.source_root),'rev-parse','HEAD'],capture_output=True,text=True)
top=subprocess.run(['git','-C',str(a.source_root),'rev-parse','--show-toplevel'],capture_output=True,text=True)
source_commit=commit.stdout.strip() if commit.returncode==0 and top.returncode==0 and Path(top.stdout.strip()).resolve()==a.source_root.resolve() else None
path=Path(__file__).resolve().parents[1]/'covex_label_manager/qt_ui/typography_checks.py'
spec=importlib.util.spec_from_file_location('covex_label_manager.qt_ui._typography_checks',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
sys.exit(module.run(a.report,a.capture,baseline=a.baseline,source_commit=source_commit))
