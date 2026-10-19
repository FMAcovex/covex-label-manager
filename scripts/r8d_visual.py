"""Execute identical synthetic task traces against verified R8C and R8D."""
import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source-root',type=Path,default=Path(__file__).resolve().parents[1])
p.add_argument('--baseline',action='store_true');p.add_argument('--report',type=Path,required=True)
p.add_argument('--capture',type=Path,required=True);a=p.parse_args()
sys.path.insert(0,str(a.source_root.resolve()))
commit=subprocess.run(['git','-C',str(a.source_root),'rev-parse','HEAD'],capture_output=True,text=True)
path=Path(__file__).resolve().parents[1]/'covex_label_manager/qt_ui/guided_checks.py'
spec=importlib.util.spec_from_file_location('covex_label_manager.qt_ui._guided_checks',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
sys.exit(module.run(a.report,a.capture,baseline=a.baseline,source_commit=commit.stdout.strip() if commit.returncode==0 else None))
