"""R8A native lifecycle regressions; no real documents, data or approvals."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
pytest.importorskip('PySide6')
from PySide6.QtCore import QRectF, QTimer
from PySide6.QtWidgets import QMessageBox
from shiboken6 import isValid
from test_r3a_qt import studio
from test_r7a_status_qt import synthetic_source, add_three
from covex_label_manager.qt_ui.status_fields_dialog import StatusFieldsDialog


def status_dialog(studio, tmp_path):
    window, session, app = studio
    uid = add_three(session.services.status_catalog, synthetic_source(tmp_path))[0]
    return StatusFieldsDialog(session.services, session.services.status_catalog.get(uid), window)


def test_native_qwidget_methods_not_hidden_and_dirty_close_guard(studio, tmp_path, monkeypatch):
    dialog = status_dialog(studio, tmp_path)
    assert callable(dialog.layout) and callable(dialog.geometry) and callable(dialog.done)
    dialog.show()
    dialog.add_field_from_drag(QRectF(50, 50, 100, 50))
    monkeypatch.setattr(QMessageBox, 'question', lambda *a, **k:QMessageBox.StandardButton.Cancel)
    dialog.reject();assert dialog.isVisible()
    monkeypatch.setattr(QMessageBox, 'question', lambda *a, **k:QMessageBox.StandardButton.Save)
    dialog.reject();assert not dialog.isVisible()
    assert len(json.loads(dialog.catalog.get(dialog.revision['uid'])['layout_json'])['fields']) == 1


def test_unapplied_properties_and_escape_do_not_silently_discard(studio, tmp_path, monkeypatch):
    dialog = status_dialog(studio, tmp_path)
    dialog.add_field_from_drag(QRectF(50, 50, 100, 50));dialog.save()
    dialog.show();dialog.name.setText('SYNTHETIC pending text')
    monkeypatch.setattr(QMessageBox, 'question', lambda *a, **k:QMessageBox.StandardButton.Cancel)
    dialog.reject();assert dialog.isVisible()
    monkeypatch.setattr(QMessageBox, 'question', lambda *a, **k:QMessageBox.StandardButton.Discard)
    dialog.reject();assert not dialog.isVisible()
    assert 'SYNTHETIC pending text' not in dialog.catalog.get(dialog.revision['uid'])['layout_json']


def test_two_status_editors_cannot_silently_overwrite(studio, tmp_path, monkeypatch):
    first = status_dialog(studio, tmp_path)
    second = StatusFieldsDialog(first.api, first.revision, first.parentWidget())
    first.add_field_from_drag(QRectF(50, 50, 100, 50));first.save()
    saved = first.catalog.get(first.revision['uid'])['layout_sha']
    second.add_field_from_drag(QRectF(60, 60, 120, 50))
    messages = []
    monkeypatch.setattr(QMessageBox, 'warning', lambda *a:messages.append(a))
    second.save()
    assert messages and second.catalog.get(second.revision['uid'])['layout_sha'] == saved
    assert second.design['fields']  # operator's candidate remains available


def test_graphic_release_keeps_cpp_item_alive_until_event_returns(studio):
    window, session, app = studio
    window.open_editor();assert window.editable()
    item = window.field_items[0]
    before = copy.deepcopy(window.design.state)
    item.setPos(item.x()+5, item.y())
    item.released()
    assert isValid(item), 'Do not delete a C++ item from inside its mouseReleaseEvent'
    assert window.design.state != before and window.design.dirty
    app.processEvents()
    assert not isValid(item)
    assert window.save_work()


def test_close_reentrancy_during_definitive_operation_is_blocked(studio):
    window, session, app = studio
    with window.emission_busy():
        window.close()
        assert window.isVisible()
    assert window.isVisible()


def test_preview_cancel_before_start_never_opens_child(studio, tmp_path, monkeypatch):
    from covex_label_manager.qt_ui.preview_task import PreviewTask
    window, session, app = studio
    path = tmp_path/'proof.pdf'
    task = PreviewTask(window, tmp_path, '0'*32, 1, '0'*64, path, 1)
    task.start = lambda:None
    # QThread ignores requestInterruption before start; exercise the worker's
    # cooperative cancellation predicate deterministically instead.
    monkeypatch.setattr(task, 'isInterruptionRequested', lambda:True)
    payloads = [];task.completed.connect(payloads.append)
    monkeypatch.setattr('covex_label_manager.qt_ui.preview_task.subprocess.run',
        lambda *a, **k:pytest.fail('Cancelled job must not start a process'))
    task.run()
    assert payloads[0]['cancelled'] and not path.exists()


def test_preview_cancel_with_locked_pdf_still_reports_and_cleans_job(studio, tmp_path, monkeypatch):
    from covex_label_manager.qt_ui.preview_task import PreviewTask
    from covex_label_manager.diagnostics import Diagnostics
    from types import SimpleNamespace
    window, session, app = studio
    path = tmp_path/'proof.pdf'
    task = PreviewTask(window, tmp_path, '0'*32, 1, '0'*64, path, 1)
    interrupted = False
    def render(*args, **kwargs):
        nonlocal interrupted
        path.write_bytes(b'SYNTHETIC locked temporary proof')
        interrupted = True
        return SimpleNamespace(returncode=0)
    original = Path.unlink
    def locked(candidate, *args, **kwargs):
        if candidate == path:raise PermissionError('SYNTHETIC Windows sharing violation')
        return original(candidate, *args, **kwargs)
    monkeypatch.setattr(task, 'isInterruptionRequested', lambda:interrupted)
    monkeypatch.setattr('covex_label_manager.qt_ui.preview_task.subprocess.run', render)
    monkeypatch.setattr(Path, 'unlink', locked)
    payloads = [];task.completed.connect(payloads.append)
    diagnostic = Diagnostics(tmp_path/'diagnostic-root', install_hooks=False)
    try:
        task.run()
        assert len(payloads) == 1 and payloads[0]['cancelled']
        assert 'cancelada' in payloads[0]['error'] and path.is_file()
        assert not path.with_suffix('.job.json').exists()
        assert not path.with_suffix('.job.result.json').exists()
        assert 'operation_error' in (diagnostic.directory/'technical.jsonl').read_text(encoding='utf-8')
    finally:diagnostic.close()


def test_shutdown_waits_for_worker_before_session_release(studio, monkeypatch):
    from test_r6b_acceptance_fixes_qt import prepared
    from covex_label_manager.qt_ui.preview_task import PreviewTask
    window, api, app = prepared(studio)
    window.preview_timer.stop()
    real = PreviewTask.run
    def delayed(task):task.msleep(30);real(task)
    monkeypatch.setattr(PreviewTask, 'run', delayed)
    window.automatic_preview()
    task = window.preview_task
    window.shutdown_runtime()
    assert not task.isRunning()
    assert api._repository.db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    app.processEvents()


def test_process_stability_check(tmp_path):
    report = tmp_path/'stability.json'
    run = subprocess.run([sys.executable, 'main_qt.py', '--stability-check', str(report)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        timeout=150, env={**os.environ, 'PYTHONIOENCODING':'utf-8'})
    assert run.returncode == 0, (run.returncode, run.stdout, run.stderr,
        report.read_text(encoding='utf-8') if report.exists() else 'missing report')
    result = json.loads(report.read_text(encoding='utf-8'))
    assert result['ok'] and result['cycles'] >= 8 and result['sqlite_integrity']
    assert result['normal_start_close'] and result['diagnostic_export_private']


def test_qt_method_shadowing_static_regression():
    import ast
    protected = {'layout','geometry','rect','actions','window','done','parent',
        'move','resize','close','update','deleteLater','screen','setVisible'}
    issues = []
    folder = Path(__file__).resolve().parents[1]/'covex_label_manager/qt_ui'
    for path in folder.glob('*.py'):
        for cls in ast.parse(path.read_text(encoding='utf-8')).body:
            if not isinstance(cls, ast.ClassDef):continue
            if cls.name in ('ErrorNotifier','ModalGuard','PreviewTask'):continue  # QObject, not QWidget
            for node in ast.walk(cls):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
                for target in targets:
                    if (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
                            and target.value.id == 'self' and target.attr in protected):
                        issues.append((path.name, cls.name, target.attr, target.lineno))
    assert not issues


def test_settings_export_uses_private_diagnostic_not_gmp_backup(studio, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QFileDialog
    from covex_label_manager.diagnostics import Diagnostics
    window, session, app = studio
    diagnostic = Diagnostics(session.services.location())
    window.diagnostics = diagnostic
    try:
        destination = tmp_path/'SYNTHETIC-report.zip'
        monkeypatch.setattr(QFileDialog, 'getSaveFileName', lambda *a: (str(destination),'ZIP'))
        window.export_diagnostic_report()
        assert destination.is_file()
        import zipfile
        with zipfile.ZipFile(destination) as archive:
            assert all(name.endswith(('.json','.jsonl')) for name in archive.namelist())
            assert not any('sqlite' in name or 'pdf' in name for name in archive.namelist())
    finally:diagnostic.close()


def test_native_qt_critical_is_recorded_without_message(studio, tmp_path):
    from PySide6.QtCore import qCritical
    from covex_label_manager.diagnostics import Diagnostics
    from covex_label_manager.qt_ui.diagnostic_ui import install_qt_diagnostics
    diagnostic = Diagnostics(tmp_path)
    restore = install_qt_diagnostics(diagnostic)
    try:
        qCritical('SYNTHETIC PRIVATE DOCUMENT PATH')
        text = (diagnostic.directory/'technical.jsonl').read_text()
        assert 'qt_critical' in text and 'SYNTHETIC PRIVATE' not in text
    finally:restore();diagnostic.close()


def test_preview_cleanup_failure_does_not_escape_callback(tmp_path, monkeypatch):
    from covex_label_manager.qt_ui.preview_task import discard_temporary
    from covex_label_manager.diagnostics import Diagnostics
    diagnostic = Diagnostics(tmp_path)
    try:
        real = Path.unlink
        path = tmp_path/'SYNTHETIC-locked-proof.pdf'
        def locked(target, *a, **kw):
            if target == path:raise PermissionError('SYNTHETIC PRIVATE PATH')
            return real(target, *a, **kw)
        monkeypatch.setattr(Path, 'unlink', locked)
        discard_temporary(path)
        text = (diagnostic.directory/'technical.jsonl').read_text()
        assert 'operation_error' in text and 'SYNTHETIC PRIVATE' not in text
    finally:diagnostic.close()


def test_database_error_on_autosave_never_accepts_close_or_loses_pending_work(studio, monkeypatch):
    import sqlite3
    from test_r6b_acceptance_fixes_qt import prepared
    window, api, app = prepared(studio)
    window.preview_timer.stop()
    panel = window.emission_panel
    panel.value_inputs['lote'].setText('SYNTHETIC-PENDING-SAVE');panel.changed()
    saved = api.work.save
    def fail(*a, **kw):raise sqlite3.OperationalError('SYNTHETIC database is locked')
    messages = []
    monkeypatch.setattr(api.work, 'save', fail)
    monkeypatch.setattr(QMessageBox, 'warning', lambda *a, **kw:messages.append(a))
    window.close()
    assert window.isVisible() and window.work_dirty_panel is panel and messages
    assert panel.value_inputs['lote'].text() == 'SYNTHETIC-PENDING-SAVE'
    assert 'NO GUARDADO' in panel.note.text()
    assert api.work.get(window.emission_work['uid'])['values']['lote'] == 'SYNTHETIC-AUTO'
    monkeypatch.setattr(api.work, 'save', saved)
    assert window.flush_emission_work()
    assert api.work.get(window.emission_work['uid'])['values']['lote'] == 'SYNTHETIC-PENDING-SAVE'
    window.preview_timer.stop()


def test_exception_inside_close_guard_cannot_authorize_qt_shutdown(studio, monkeypatch):
    window, session, app = studio
    def fail():raise RuntimeError('SYNTHETIC unexpected close guard failure')
    monkeypatch.setattr(window, 'resolve_work', fail)
    window.close()
    assert window.isVisible()
    assert 'cerrar de forma segura' in window.statusBar().currentMessage()


def test_diagnostics_track_actual_module_changes_through_all_mixins(studio, tmp_path):
    from covex_label_manager.diagnostics import Diagnostics
    from covex_label_manager.qt_ui.diagnostic_ui import ErrorNotifier
    window, session, app = studio
    diagnostic = Diagnostics(tmp_path);window.diagnostics=diagnostic
    notifier = ErrorNotifier(window)
    try:
        for module in ('editor','emission','history','settings','status-manager','library'):
            window.navigate(module)
        events = [json.loads(line) for line in (diagnostic.directory/'technical.jsonl').read_text().splitlines()]
        seen = {event.get('module') for event in events if event['event']=='module'}
        assert seen == {'editor','emission','history','settings','status-manager','library'}
    finally:
        window.stack.currentChanged.disconnect(notifier.record_module)
        notifier.deleteLater();diagnostic.close()


def test_startup_failure_is_nonzero_private_and_operator_friendly(studio, tmp_path, monkeypatch):
    import main_qt
    root = tmp_path/'SYNTHETIC-STARTUP'
    messages = []
    monkeypatch.setattr(sys, 'argv', ['main_qt.py','--data-dir',str(root)])
    monkeypatch.setenv('COVEX_LABEL_DATA', str(root))
    def fail(*a):raise RuntimeError('SYNTHETIC PRIVATE STARTUP VALUE')
    monkeypatch.setattr(main_qt, 'run_application', fail)
    monkeypatch.setattr(QMessageBox, 'critical', lambda *a:messages.append(a))
    assert main_qt.main() == 1
    assert messages and 'No se ha podido' in messages[0][2]
    log = (root/'diagnostics/technical.jsonl').read_text()
    assert 'python_error' in log and 'SYNTHETIC PRIVATE STARTUP' not in log
    assert not json.loads(next((root/'diagnostics').glob('session-*.json')).read_text())['normal_end']


def test_invalid_headless_job_never_opens_bootloader_traceback(tmp_path):
    job = tmp_path/'SYNTHETIC-invalid.json';job.write_text('{}')
    process = subprocess.run([sys.executable, 'main_qt.py', '--preview-job', str(job)],
        capture_output=True, cwd=Path(__file__).resolve().parents[1], timeout=20)
    assert process.returncode == 1
    assert b'Traceback' not in process.stderr and str(job).encode() not in process.stderr
