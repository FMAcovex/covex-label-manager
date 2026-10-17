"""Real event-loop/process regression for importer close; synthetic data only."""
import json
import traceback
from PySide6.QtCore import QTimer,Qt
from PySide6.QtWidgets import QApplication,QMessageBox
from PySide6.QtTest import QTest


def run(report):
    from .demo import DemoSession
    from .functional import FunctionalWindow
    from .folder_import import FolderImportDialog
    from .controlled_import import ControlledImportDialog
    app=QApplication.instance() or QApplication([])
    session=DemoSession();session.fictional=True
    window=FunctionalWindow(session);window.show()
    records=[];errors=[];result={'ok':False,'cases':records,'errors':errors}
    modes=('button','escape','titlebar');phases=('before','during','after')
    scenarios=[(cls,phase,mode) for cls in (FolderImportDialog,ControlledImportDialog) for phase in phases for mode in modes]
    work=session.services.work.create(session.initial_id,name='SYNTHETIC retained work')
    work=session.services.work.save(work['uid'],work['generation'],{'values':{'lote':'SYNTHETIC-RETAINED'}})
    window.load_emission_work(work['uid']);window.preview_timer.stop();window.preview_pending=False
    app.aboutToQuit.connect(lambda:result.update(about_to_quit=True))

    def finish():
        result['ok']=not errors and len(records)==18
        report.parent.mkdir(parents=True,exist_ok=True)
        report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        app.exit(0 if result['ok'] else 1)

    def exercise():
        try:
            cls,phase,mode=scenarios[len(records)]
            folder=session.root/f'SYNTHETIC-{len(records)}';folder.mkdir()
            import fitz
            for n in range(2):
                with fitz.open() as pdf:
                    pdf.new_page().insert_text((40,70),f'SYNTHETIC ONLY {len(records)} - {n}')
                    pdf.save(folder/f'SYNTHETIC {len(records)} {n} 00.pdf')
            dialog=cls(window,session.services,folder)
            assert callable(dialog.done),'QDialog.done must not be shadowed'
            if cls is ControlledImportDialog:
                dialog.next_page()
                for action in dialog.actions:action.setCurrentIndex(action.findData('NEW_LABEL'))
                dialog.confirm_identity.setChecked(True)
            if phase!='before':
                original=QMessageBox.question
                try:
                    QMessageBox.question=lambda *a,**k:QMessageBox.StandardButton.Yes
                    dialog.start();dialog.timer.stop()
                finally:QMessageBox.question=original
                dialog.step();dialog.timer.stop()
                if phase=='after':
                    dialog.step();dialog.timer.stop();dialog.finish()
            def close():
                if mode=='button':dialog.close_requested()
                elif mode=='escape':QTest.keyClick(dialog,Qt.Key.Key_Escape)
                else:dialog.close()
                if phase=='during':QTimer.singleShot(0,dialog.step)
            QTimer.singleShot(10,close)
            dialog.exec() # genuine modal loop and native close/virtual dispatch
            assert window.isVisible()
            assert not dialog.running
            expected={'before':0,'during':1,'after':2}[phase]
            assert dialog.ok==expected,(dialog.ok,expected,dialog.failures)
            assert dialog.processed==expected
            if cls is ControlledImportDialog:
                assert all(session.services.version(r['version_id'])['state']=='PENDING' for r in dialog.imported)
            for page in ('history','settings','library'):window.navigate(page)
            assert window.stack.currentWidget() is window.library
            assert session.services.work.get(work['uid'])['values']['lote']=='SYNTHETIC-RETAINED'
            records.append(dict(dialog=cls.__name__,phase=phase,close=mode,imported=expected,navigable=True))
            dialog.deleteLater()
            # Reaching the next queued callback proves QApplication did not quit.
            QTimer.singleShot(10,exercise if len(records)<len(scenarios) else finish)
        except Exception:
            errors.append(traceback.format_exc());finish()
    watchdog=QTimer();watchdog.setSingleShot(True)
    def timeout():errors.append('Timed out: dialog close did not return to the main event loop');finish()
    watchdog.timeout.connect(timeout);watchdog.start(90000)
    QTimer.singleShot(0,exercise)
    code=app.exec();watchdog.stop()
    # An unsolicited quit never supplies the required complete report.
    if not result['ok']:code=1
    window.preview_timer.stop()
    if window.preview_task:window.preview_task.wait(30000)
    window.hide();window.deleteLater();app.processEvents();session.close()
    return code
