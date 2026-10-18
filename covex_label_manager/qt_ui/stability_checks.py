"""Bounded R8A synthetic stability exercise, source and extracted Windows EXE.

No fixed sleep determines success: rendering waits for an observable predicate
with an explicit deadline. The watchdog makes native hangs fail the CI job.
"""
import copy
import json
from pathlib import Path
import sys
import time
import traceback

import fitz
from PySide6.QtCore import QEventLoop, QRectF, QTimer
from PySide6.QtWidgets import QApplication


def until(predicate, timeout_ms=30000):
    if predicate():return
    loop = QEventLoop()
    poll = QTimer();poll.setInterval(10)
    deadline = QTimer();deadline.setSingleShot(True)
    poll.timeout.connect(lambda:loop.quit() if predicate() else None)
    deadline.timeout.connect(loop.quit)
    poll.start();deadline.start(timeout_ms)
    loop.exec()
    poll.stop();deadline.stop()
    assert predicate(), 'Stability condition exceeded its deadline'


def run(report, rounds=4):
    if type(rounds) is not int or not 1 <= rounds <= 100:
        raise ValueError('Stability rounds must be between 1 and 100 per resolution')
    from .demo import DemoSession
    from .functional import FunctionalWindow
    from .responsive import install_translation
    from .status_fields_dialog import StatusFieldsDialog
    from ..diagnostics import Diagnostics
    from ..status_design import make_layout
    from ..emission_work import WorkConflict
    import zipfile
    app = QApplication.instance() or QApplication([])
    app.setStyle('Fusion');install_translation(app)
    app.setQuitOnLastWindowClosed(False)
    session = DemoSession();session.fictional = True
    api = session.services
    diagnostic = Diagnostics(api.location())
    window = FunctionalWindow(session);window.diagnostics = diagnostic
    result = dict(ok=False, synthetic_only=True, cycles=0,
                  scale=__import__('os').environ.get('QT_SCALE_FACTOR', '1'))
    errors = []
    def hook(kind, error, tb):
        diagnostic.sys_hook(kind, error, tb)
        errors.append(kind.__name__)
    sys.excepthook = hook
    watchdog = QTimer();watchdog.setSingleShot(True)
    watchdog.timeout.connect(lambda:app.exit(2))
    watchdog.start(120000)

    def exercise():
        try:
            window.show();app.processEvents()
            result['normal_start_close'] = window.isVisible()
            source = session.root/'SYNTHETIC-STABILITY.pdf'
            with fitz.open() as pdf:
                page = pdf.new_page(width=432, height=300)
                page.insert_text((30, 40), 'SYNTHETIC STABILITY ONLY')
                pdf.save(source)
            catalog = api.status_catalog
            uid = catalog.import_many(source, [dict(kind='sin_analizar', revision='SYN-00',
                layout=make_layout(source, 'sin_analizar', crop=[0, 0, 432, 300]))])[0]
            # Explicit approval of a synthetic fixture, not any operator data.
            catalog.submit(uid)
            catalog.approve(uid, 'SYNTHETIC', 'SYNTHETIC-REFERENCE', confirmation=True)
            status_issue, status_pdf = catalog.emit(uid, {}, 'SYNTHETIC')
            assert status_pdf.is_file() and catalog.issues()[0]['uid'] == status_issue
            result['synthetic_status_issue'] = True
            scale = float(result['scale'])
            result['resolutions_physical'] = [[1366, 768], [1920, 1080]]
            result['sizes_logical'] = []
            for width, height in result['resolutions_physical']:
                size = (int(width/scale), int(height/scale)-40)
                window.resize(*size);app.processEvents()
                assert window.width() <= size[0] and window.height() <= size[1]
                result['sizes_logical'].append([window.width(),window.height()])
                for index in range(rounds):
                    for module in ('library', 'editor', 'status-manager', 'emission', 'history', 'settings'):
                        window.navigate(module);app.processEvents()
                        assert window.isVisible()
                    window.navigate('library')
                    # Native product editor: model committed before deferred redraw.
                    window.select_version(session.initial_id);window.open_editor()
                    shape = window.field_items[0]
                    shape.setPos(shape.x()+1, shape.y())
                    shape.released();app.processEvents()
                    assert window.save_work()
                    draft = catalog.new_revision(uid, 'SYN-'+str(result['cycles']+1), 'SYNTHETIC stress')
                    editor = StatusFieldsDialog(api, catalog.get(draft), window)
                    editor.show();app.processEvents()
                    assert callable(editor.geometry) and callable(editor.layout)
                    editor.add_field_from_drag(QRectF(60, 60, 120, 50))
                    shape = editor.shapes[0];shape.setPos(shape.x()+1, shape.y()+1);shape.released()
                    shape.setRect(shape.rect().adjusted(0, 0, 2, 2));shape.released()
                    editor.save();assert not editor.isVisible()
                    proof = catalog.preview(draft, {'campo_1':''})
                    with fitz.open(proof) as pdf:
                        assert 'PRUEBA' in ''.join(page.get_text() for page in pdf)
                    editor.deleteLater();app.processEvents()
                    result['cycles'] += 1
            vid = next(row['version_id'] for row in api.library.entries() if row['state']=='APPROVED')
            work = api.work.create(vid, name='SYNTHETIC-STABILITY')
            work = api.work.save(work['uid'], work['generation'], dict(values={
                'lote':'SYNTHETIC-ONE', 'pn':'350 g', 'pb':'500 g'}))
            window.load_emission_work(work['uid']);window.navigate('emission')
            window.preview_timer.stop();window.automatic_preview()
            # Change while the child is alive: old PDF must never become current.
            panel = window.emission_panel
            panel.value_inputs['lote'].setText('SYNTHETIC-TWO');panel.changed()
            assert window.flush_emission_work()
            until(lambda:window.preview_task is None and window.preview_matches() and
                  not window.preview_timer.isActive())
            assert api.work.get(work['uid'])['values']['lote'] == 'SYNTHETIC-TWO'
            with fitz.open(window.work_preview['path']) as pdf:
                text = ''.join(page.get_text() for page in pdf).replace('\xad','-')
                assert 'SYNTHETIC-TWO' in text and 'SYNTHETIC-ONE' not in text
            result['stale_preview_rejected'] = True
            saved = window.emission_work
            api.work.save(saved['uid'], saved['generation'], dict(name='SYNTHETIC concurrent'))
            try:api.work.save(saved['uid'], saved['generation'], dict(name='SYNTHETIC stale'))
            except WorkConflict:pass
            else:raise AssertionError('Concurrent work update was accepted')
            window.load_emission_work(saved['uid'])
            assert window.emission_work['name'] == 'SYNTHETIC concurrent'
            result['recovery_concurrency'] = True
            window.preview_timer.stop();window.invalidate_work_preview();window.automatic_preview()
            assert window.preview_task is not None
            window.close();assert window.isVisible()
            window.shutdown_runtime();app.processEvents()
            assert window.preview_task is None
            result['close_during_preview_safe'] = True
            assert not api.issues(), 'No product emission is allowed in the stress exercise'
            result['sqlite_integrity'] = api._repository.db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
            with catalog._connect() as db:
                assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
                assert not db.execute('PRAGMA foreign_key_check').fetchall()
            from ..vessels import parse_mass
            try:parse_mass('SYNTHETIC-PRIVATE-ERROR-VALUE')
            except ValueError as ex:diagnostic.exception('operation_error', ex)
            archive = diagnostic.export(session.root/'SYNTHETIC-diagnostic.zip')
            with zipfile.ZipFile(archive) as zip_report:
                text = ''.join(zip_report.read(name).decode() for name in zip_report.namelist())
                assert all(secret not in text for secret in ('SYNTHETIC-TWO', str(session.root), 'SYNTHETIC-REFERENCE', 'SYNTHETIC-PRIVATE-ERROR-VALUE'))
                assert 'vessels.py' in text, 'Frozen diagnostics must retain safe source/line evidence'
            result['diagnostic_export_private'] = True
            result['diagnostic_source_frames'] = True
            assert not errors, errors
            window.close();assert not window.isVisible()
            result['ok'] = True
        except BaseException:
            result['error'] = traceback.format_exc()
        finally:
            watchdog.stop()
            window.shutdown_runtime()
            sys.excepthook = diagnostic.sys_hook
            diagnostic.close(normal=result['ok'])
            Path(report).parent.mkdir(parents=True, exist_ok=True)
            Path(report).write_text(json.dumps(result, indent=2), encoding='utf-8')
            window.hide();window.deleteLater();app.processEvents();session.close()
            app.exit(0 if result['ok'] else 1)
    QTimer.singleShot(0, exercise)
    return app.exec()
