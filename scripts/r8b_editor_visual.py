"""Compare retained R8A and current R8B widgets using the SAME synthetic fixture."""
import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root',type=Path,default=Path(__file__).resolve().parents[1])
parser.add_argument('--baseline',action='store_true')
parser.add_argument('--report',type=Path,required=True)
parser.add_argument('--capture',type=Path,required=True)
parser.add_argument('--svg-dir',type=Path)
args=parser.parse_args();sys.path.insert(0,str(args.source_root.resolve()))
commit=subprocess.run(['git','-C',str(args.source_root),'rev-parse','HEAD'],text=True,capture_output=True)
path=Path(__file__).resolve().parents[1]/'covex_label_manager/qt_ui/editor_ux_checks.py'
spec=importlib.util.spec_from_file_location('_editor_ux_checks',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
sys.exit(module.run(args.report,args.capture,baseline=args.baseline,svg_dir=args.svg_dir,
                    source_commit=commit.stdout.strip() if commit.returncode==0 else None))
