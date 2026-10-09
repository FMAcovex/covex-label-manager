"""Opt-in R3A Qt entry; legacy main.py/distribution remain unchanged."""
import argparse
import json
import os
import sys
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from covex_label_manager.qt_transition import TransitionServices
from covex_label_manager.qt_ui.functional import FunctionalWindow

class LocalSession:
    fictional=False
    initial_id=None
    def __init__(self):self.services=TransitionServices()
    def close(self):self.services.close()

def main():
    p=argparse.ArgumentParser();p.add_argument('--demo',action='store_true');p.add_argument('--data-dir',type=Path)
    p.add_argument('--verify-bridge',action='store_true');p.add_argument('--capture',type=Path);p.add_argument('--self-check',type=Path);a=p.parse_args()
    if a.data_dir:os.environ['COVEX_LABEL_DATA']=str(a.data_dir.resolve())
    app=QApplication(sys.argv[:1]);app.setStyle('Fusion')
    if a.demo or a.self_check or a.capture:
        from covex_label_manager.qt_ui.demo import DemoSession
        session=DemoSession();session.fictional=True
    else:session=LocalSession()
    try:
        w=FunctionalWindow(session);w.show()
        if a.capture or a.self_check:
            def verify():
                try:
                    from covex_label_manager.qt_ui.checks import exercise
                    result=exercise(w,app,a.capture)
                    if a.verify_bridge:
                        from covex_label_manager.qt_legacy import launch_legacy
                        vid=next(v['id'] for v in session.services.versions(w.row['id']) if v['state']=='APPROVED')
                        report=session.services.output_path('cache','bridge-check.json')
                        process=launch_legacy(session.services,'emitir',vid,'test',smoke_report=report)
                        if process.wait(timeout=40)!=0:raise RuntimeError('Legacy bridge process failed')
                        bridge=json.loads(report.read_text());assert bridge['ok'],bridge
                        result['legacy_bridge']=bridge
                    if a.self_check:a.self_check.parent.mkdir(parents=True,exist_ok=True);a.self_check.write_text(json.dumps(result,indent=2),encoding='utf-8')
                except Exception:
                    import traceback
                    traceback.print_exc()
                    if a.self_check:a.self_check.parent.mkdir(parents=True,exist_ok=True);a.self_check.write_text(json.dumps({'ok':False,'error':traceback.format_exc()}),encoding='utf-8')
                    app.exit(1);return
                app.exit(0)
            QTimer.singleShot(250,verify)
        return app.exec()
    finally:session.close()
if __name__=='__main__':sys.exit(main())
