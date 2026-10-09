"""Launch the isolated Qt visual proof. The production main.py stays unchanged."""
import argparse
import json
import sys
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from prototypes.industrial_qt.demo import DemoSession
from prototypes.industrial_qt.window import StudioProof

def main():
    parser=argparse.ArgumentParser(description='Industrial Moderno / datos ficticios temporales')
    parser.add_argument('--capture',type=Path,help='Capture real Qt widget windows then close')
    parser.add_argument('--self-check',type=Path,help='Check packaged Qt/services/rendering without user data')
    args=parser.parse_args()
    app=QApplication(sys.argv[:1]);app.setStyle('Fusion')
    session=DemoSession()
    try:
        window=StudioProof(session);window.show()
        if args.capture or args.self_check:
            def verify_and_capture():
                try:
                    from prototypes.industrial_qt.verify import exercise
                    result=exercise(window,app,args.capture)
                    if args.self_check:
                        args.self_check.parent.mkdir(parents=True,exist_ok=True)
                        args.self_check.write_text(json.dumps(result,indent=2),encoding='utf-8')
                except Exception:
                    import traceback
                    traceback.print_exc();app.exit(1);return
                app.exit(0)
            QTimer.singleShot(250,verify_and_capture)
        return app.exec()
    finally:
        session.close()

if __name__=='__main__':sys.exit(main())
