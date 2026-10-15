"""CLI wrapper for the real, synthetic Qt variants acceptance check."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from covex_label_manager.qt_ui.variant_checks import run
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--capture',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--verify-bridge',action='store_true');a=p.parse_args()
    sys.exit(run(a.report,a.capture,a.verify_bridge))
