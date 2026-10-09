"""Legacy companion entry. Production main.py remains unchanged."""
import argparse
from covex_label_manager.qt_legacy import run_legacy
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--target',choices=['maestro','editor','emitir','centro','historial','admin'],default='maestro')
    p.add_argument('--version-id',type=int);p.add_argument('--mode',choices=['production','test'],default='production')
    p.add_argument('--smoke-report');a=p.parse_args();run_legacy(a.target,a.version_id,a.mode,a.smoke_report)
