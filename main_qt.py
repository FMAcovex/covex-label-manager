"""Opt-in R3A Qt entry; legacy main.py/distribution remain unchanged."""
import argparse
import json
import os
import sys
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from covex_label_manager.qt_transition import TransitionServices
from covex_label_manager.qt_ui.functional import FunctionalWindow

class LocalSession:
    fictional=False
    initial_id=None
    def __init__(self):
        from covex_label_manager.migration_consent import qt_confirmation
        self.services=TransitionServices(migration_confirmation=qt_confirmation)
    def close(self):self.services.close()

def main():
    if '--recover-data' in sys.argv[1:]:
        from covex_label_manager.migration_v4 import recovery_cli
        return recovery_cli(sys.argv[1:])
    p=argparse.ArgumentParser();p.add_argument('--r3e-check',type=Path);p.add_argument('--emission-check',type=Path);p.add_argument('--work-check',type=Path);p.add_argument('--variant-check',type=Path);p.add_argument('--demo',action='store_true');p.add_argument('--data-dir',type=Path)
    p.add_argument('--import-check',type=Path)
    p.add_argument('--preview-job',type=Path)
    p.add_argument('--stability-check',type=Path)
    p.add_argument('--stability-rounds',type=int,default=4)
    p.add_argument('--editor-ux-check',type=Path)
    p.add_argument('--typography-check',type=Path)
    p.add_argument('--verify-bridge',action='store_true');p.add_argument('--capture',type=Path);p.add_argument('--self-check',type=Path);a=p.parse_args()
    if a.import_check:
        from covex_label_manager.qt_ui.import_checks import run
        return run(a.import_check)
    if a.preview_job:
        from covex_label_manager.preview_render import run_job
        try:return run_job(a.preview_job)
        except Exception:
            # Never open a bootloader error dialog in the headless child.
            # A failed/missing result is explicitly rejected by PreviewTask.
            return 1
    if a.stability_check:
        from covex_label_manager.qt_ui.stability_checks import run
        return run(a.stability_check, rounds=a.stability_rounds)
    if a.editor_ux_check:
        from covex_label_manager.qt_ui.editor_ux_checks import run
        return run(a.editor_ux_check,a.capture)
    if a.typography_check:
        from covex_label_manager.qt_ui.typography_checks import run
        return run(a.typography_check,a.capture)
    if a.r3e_check:
        from covex_label_manager.qt_ui.r3e_checks import run
        return run(a.r3e_check,a.capture)
    if a.emission_check:
        from covex_label_manager.qt_ui.emission_checks import run
        return run(a.emission_check,a.capture)
    if a.work_check:
        from covex_label_manager.qt_ui.work_checks import run
        return run(a.work_check,a.capture,a.verify_bridge)
    if a.variant_check:
        from covex_label_manager.qt_ui.variant_checks import run
        return run(a.variant_check,a.capture,a.verify_bridge)
    if a.data_dir:os.environ['COVEX_LABEL_DATA']=str(a.data_dir.resolve())
    from covex_label_manager.diagnostics import Diagnostics
    from covex_label_manager.paths import data_dir
    import tempfile
    temporary = tempfile.TemporaryDirectory(prefix='covex_synthetic_diagnostics_') if a.demo or a.self_check or a.capture else None
    diagnostic = Diagnostics(Path(temporary.name) if temporary else data_dir(create=False))
    normal = False
    try:
        result = run_application(a, diagnostic)
        normal = True
        return result
    except Exception as ex:
        diagnostic.exception('python_error', ex)
        if not (a.demo or a.self_check or a.capture) and QApplication.instance():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(None, 'Aplicación no disponible',
                'No se ha podido iniciar o finalizar la aplicación de forma segura. '
                'Conserve la carpeta de datos y revise el historial antes de repetir una emisión. '
                'Reinicie y exporte el diagnóstico desde Configuración; si persiste, solicite asistencia.')
        return 1
    finally:
        diagnostic.close(normal=normal)
        if temporary:temporary.cleanup()


def run_application(a, diagnostic):
    app=QApplication(sys.argv[:1]);app.setStyle('Fusion')
    from covex_label_manager.qt_ui.responsive import install_translation
    install_translation(app)
    # Apply a consistent light palette before opening any native Qt modal.
    palette=app.palette()
    for role,colour in (
        (QPalette.ColorRole.Window,'#F3F6F7'),(QPalette.ColorRole.WindowText,'#223B40'),
        (QPalette.ColorRole.Base,'#FFFFFF'),(QPalette.ColorRole.AlternateBase,'#F8FAFA'),
        (QPalette.ColorRole.Text,'#223B40'),(QPalette.ColorRole.Button,'#FFFFFF'),
        (QPalette.ColorRole.ButtonText,'#223B40'),(QPalette.ColorRole.Highlight,'#147D71'),
        (QPalette.ColorRole.HighlightedText,'#FFFFFF'),(QPalette.ColorRole.ToolTipBase,'#FFFFFF'),
        (QPalette.ColorRole.ToolTipText,'#223B40')
    ):
        palette.setColor(role,QColor(colour))
    app.setPalette(palette)
    if a.demo or a.self_check or a.capture:
        from covex_label_manager.qt_ui.demo import DemoSession
        session=DemoSession();session.fictional=True
    else:
        from covex_label_manager.migration_v4 import MigrationCancelled
        try:session=LocalSession()
        except MigrationCancelled:return 0
    try:
        w=FunctionalWindow(session);w.diagnostics=diagnostic;w.show()
        from covex_label_manager.qt_ui.diagnostic_ui import ErrorNotifier, install_qt_diagnostics
        notifier=ErrorNotifier(w)
        diagnostic.notifier=notifier.failed.emit
        restore_qt_handler=install_qt_diagnostics(diagnostic)
        if diagnostic.previous_unfinished:
            w.statusBar().showMessage('Se encontró una sesión sin cierre normal; puede deberse a un corte, otra sesión o un fallo. Exporte el informe desde Configuración.')
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
                    error=traceback.format_exc()
                    # Persist evidence before writing to the platform's console.
                    if a.self_check:a.self_check.parent.mkdir(parents=True,exist_ok=True);a.self_check.write_text(json.dumps({'ok':False,'error':error}),encoding='utf-8')
                    print(error,file=sys.stderr,flush=True)
                    app.exit(1);return
                app.exit(0)
            QTimer.singleShot(250,verify)
        return app.exec()
    finally:
        if 'restore_qt_handler' in locals():restore_qt_handler()
        if 'w' in locals():w.shutdown_runtime()
        session.close()
if __name__=='__main__':sys.exit(main())

