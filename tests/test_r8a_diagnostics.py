"""Closed-schema local diagnostics; all sensitive-looking values are synthetic."""
import json
import sys
import threading
import zipfile

import pytest

from covex_label_manager.diagnostics import Diagnostics


def test_lifecycle_hooks_and_normal_marker(tmp_path):
    old = sys.excepthook
    diag = Diagnostics(tmp_path)
    try:
        assert sys.excepthook == diag.sys_hook
        assert not diag.previous_unfinished
        diag.record('module', module='editor', password='SYNTHETIC_SECRET')
    finally:diag.close()
    assert sys.excepthook == old
    assert json.loads(diag.marker.read_text())['normal_end']
    again = Diagnostics(tmp_path)
    try:assert not again.previous_unfinished
    finally:again.close()


def test_unfinished_session_is_not_declared_crash(tmp_path):
    diag = Diagnostics(tmp_path)
    diag.close(normal=False)
    again = Diagnostics(tmp_path)
    try:
        assert again.previous_unfinished
        report = again.export(tmp_path/'report.zip')
        with zipfile.ZipFile(report) as archive:
            state = json.loads(archive.read('technical-state.json'))
            assert state['previous_unfinished']
            assert 'no demuestra un fallo' in state['note']
    finally:again.close()


def test_python_thread_errors_and_export_never_include_sensitive_content(tmp_path):
    secret = 'SYNTHETIC_CLIENT_LOT_PASSWORD_CORPORATE_PATH'
    diag = Diagnostics(tmp_path)
    notices = []
    diag.notifier = lambda:notices.append(True)
    try:
        try:raise RuntimeError(secret)
        except RuntimeError as ex:diag.sys_hook(type(ex), ex, ex.__traceback__)
        def fail():raise ValueError(secret)
        thread = threading.Thread(target=fail)
        thread.start();thread.join(5)
        assert not thread.is_alive() and len(notices) == 2
        diag.record('module', module=secret, count=2, detail=secret)
        report = diag.export(tmp_path/'safe.zip')
        with zipfile.ZipFile(report) as archive:
            assert set(archive.namelist()) == {'technical-state.json','technical.jsonl'}
            text = ''.join(archive.read(name).decode() for name in archive.namelist())
            assert secret not in text and str(tmp_path) not in text
            assert 'python_error' in text and 'thread_error' in text
        assert secret not in (diag.directory/'technical.jsonl').read_text()
    finally:diag.close()


def test_rotation_retention_and_revalidated_export(tmp_path):
    diag = Diagnostics(tmp_path)
    try:
        for _ in range(4000):diag.record('module', module='library')
        logs = list(diag.directory.glob('technical.jsonl*'))
        assert 1 < len(logs) <= diag.BACKUPS+1
        assert all(path.stat().st_size <= diag.MAX_BYTES for path in logs)
        # A replaced/tampered file is not blindly included as a confidential dump.
        (diag.directory/'technical.jsonl.3').write_text(json.dumps(dict(
            event='module', session=diag.session, module='library',
            document='SYNTHETIC_CONFIDENTIAL'))+'\n')
        report = diag.export(tmp_path/'safe.zip')
        with zipfile.ZipFile(report) as archive:
            assert all(b'SYNTHETIC_CONFIDENTIAL' not in archive.read(n) for n in archive.namelist())
        with pytest.raises(ValueError):diag.export(diag.directory/'recursive.zip')
        with pytest.raises(ValueError):diag.record('arbitrary sensitive text')
    finally:diag.close()


def test_export_ignores_symlink_documents(tmp_path):
    diag = Diagnostics(tmp_path)
    try:
        source = tmp_path/'SYNTHETIC.txt';source.write_text('SYNTHETIC_PRIVATE')
        link = diag.directory/'technical.jsonl.1'
        try:link.symlink_to(source)
        except OSError:pytest.skip('Symlink creation unavailable on this Windows account')
        report = diag.export(tmp_path/'safe.zip')
        with zipfile.ZipFile(report) as archive:assert link.name not in archive.namelist()
    finally:diag.close()


def test_protected_data_uses_writable_local_fallback(tmp_path, monkeypatch):
    from pathlib import Path
    original = Path.mkdir
    protected = tmp_path/'protected'
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path/'local'))
    def mkdir(path, *a, **k):
        if path == protected/'diagnostics':raise PermissionError('synthetic protected installation')
        return original(path, *a, **k)
    monkeypatch.setattr(Path, 'mkdir', mkdir)
    diag = Diagnostics(protected)
    try:
        assert diag.directory.is_relative_to(tmp_path/'local')
        assert protected.name not in diag.directory.parts
    finally:diag.close()


def test_frozen_pyz_frames_survive_export_without_source_files(tmp_path, monkeypatch):
    from pathlib import Path
    from covex_label_manager.vessels import parse_mass
    diag = Diagnostics(tmp_path)
    try:
        try:parse_mass('SYNTHETIC PRIVATE VALUE')
        except ValueError as ex:diag.exception('operation_error', ex)
        monkeypatch.setattr(Path, 'rglob', lambda *a:iter(()))
        report = diag.export(tmp_path/'frozen.zip')
        with zipfile.ZipFile(report) as archive:
            text = archive.read('technical.jsonl').decode()
            assert 'vessels.py' in text and 'SYNTHETIC PRIVATE' not in text
    finally:diag.close()


def test_secondary_process_error_has_safe_source_without_message_or_root(tmp_path):
    from covex_label_manager.preview_render import run_job
    from covex_label_manager.diagnostics import process_error
    root = tmp_path/'SYNTHETIC-CORPORATE-ROOT'
    cache = root/'cache';cache.mkdir(parents=True)
    output = cache/('qt-auto-proof-'+'a'*32+'.pdf')
    job = output.with_suffix('.job.json')
    job.write_text(json.dumps(dict(contract=1, root=str(root), uid='a'*32,
        generation=1, token='b'*64, path=str(output), serial=1)))
    assert run_job(job) == 1
    payload = json.loads(job.with_suffix('.result.json').read_text())
    assert payload['technical_error']['frames']
    diag = Diagnostics(root)
    try:
        process_error(payload['technical_error'])
        report = diag.export(tmp_path/'secondary.zip')
        with zipfile.ZipFile(report) as archive:
            text = archive.read('technical.jsonl').decode()
            assert 'preview_render.py' in text and str(root) not in text
            assert payload['error'] not in text
    finally:diag.close()


def test_late_callback_cannot_reopen_closed_log(tmp_path):
    diag = Diagnostics(tmp_path)
    diag.close()
    log = diag.directory/'technical.jsonl'
    log.unlink()
    diag.record('module', module='library')
    diag.process_error({'category':'runtime','frames':[]})
    assert not log.exists()


def test_legacy_process_and_tk_callback_errors_are_exported_without_sensitive_values(tmp_path, monkeypatch):
    import os
    from pathlib import Path
    import subprocess
    from covex_label_manager.qt_legacy import report_callback_error
    root = tmp_path/'SYNTHETIC-ROOT'
    code = """
import legacy_qt_bridge
def fail(*args):raise RuntimeError('SYNTHETIC PRIVATE LEGACY VALUE')
legacy_qt_bridge.run_legacy=fail
legacy_qt_bridge.main([])
"""
    process = subprocess.run([sys.executable,'-c',code], capture_output=True,
        env={**os.environ,'COVEX_LABEL_DATA':str(root)},
        cwd=Path(__file__).resolve().parents[1],timeout=20)
    assert process.returncode != 0
    assert (root/'diagnostics/technical-legacy.jsonl').is_file()
    diagnostic = Diagnostics(root)
    try:
        from types import SimpleNamespace
        messages = []
        app = SimpleNamespace(top_title=SimpleNamespace(configure=lambda **kw:messages.append(kw)))
        try:raise ValueError('SYNTHETIC PRIVATE CALLBACK VALUE')
        except ValueError as ex:report_callback_error(app,type(ex),ex,ex.__traceback__)
        assert messages and 'Operación no completada' in messages[0]['text']
        report = diagnostic.export(tmp_path/'legacy.zip')
        with zipfile.ZipFile(report) as archive:
            assert 'technical-legacy.jsonl' in archive.namelist()
            text = ''.join(archive.read(n).decode() for n in archive.namelist())
            assert 'python_error' in text
            assert 'SYNTHETIC PRIVATE' not in text and str(root) not in text
    finally:diagnostic.close()
