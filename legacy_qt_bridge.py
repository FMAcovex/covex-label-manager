"""Legacy companion entry. Production main.py remains unchanged."""
import argparse
from covex_label_manager.qt_legacy import run_legacy
def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('--target',choices=['maestro','editor','emitir','centro','historial','admin'],default='maestro')
    p.add_argument('--version-id',type=int);p.add_argument('--mode',choices=['production','test'],default='production')
    p.add_argument('--smoke-report');p.add_argument('--variant-id',type=int);p.add_argument('--writer-protocol',type=int,default=4);p.add_argument('--smoke-issue',action='store_true')
    p.add_argument('--work-uid');p.add_argument('--work-generation',type=int)
    a=p.parse_args(argv)
    from covex_label_manager.paths import data_dir
    from covex_label_manager.diagnostics import Diagnostics
    diagnostic=Diagnostics(data_dir(create=False),channel='legacy')
    normal=False
    try:
        run_legacy(a.target,a.version_id,a.mode,a.smoke_report,a.variant_id,a.writer_protocol,a.smoke_issue,a.work_uid,a.work_generation)
        normal=True
    except BaseException as ex:
        diagnostic.exception('python_error',ex)
        raise
    finally:diagnostic.close(normal=normal)


if __name__=='__main__':main()

