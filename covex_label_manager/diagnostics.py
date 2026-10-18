"""Private, bounded technical telemetry. Never serialize exceptions or user data.

This is not the GMP audit trail. Only closed-schema technical events are stored.
Native termination may leave no Python exception: an unfinished marker is NOT
proof of a crash. No raw faulthandler dumps (paths/source text) are exported.
"""
from __future__ import annotations

import hashlib
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import platform
import sys
import threading
import time
import traceback
import uuid
import zipfile

from . import __version__

EVENTS = frozenset(('session_start', 'session_end', 'previous_unfinished',
    'python_error', 'thread_error', 'module', 'editor_open', 'preview_start',
    'preview_finish', 'preview_error', 'preview_stale', 'preview_cancel',
    'shutdown_wait', 'shutdown_blocked', 'legacy_start', 'legacy_finish',
    'operation_error', 'export', 'qt_critical', 'qt_fatal'))
MODULES = frozenset(('library', 'editor', 'emission', 'history', 'settings',
                     'status-manager', 'other'))
_active = None


def event(name, **fields):
    if _active is not None:
        _active.record(name, **fields)


def error(name, exception):
    if _active is not None:
        _active.exception(name, exception)


def technical_exception(exception):
    """Safe across the child-process contract: no message, values or paths."""
    category = next((label for cls, label in (
        (PermissionError, 'permission'), (OSError, 'io'),
        (ValueError, 'validation'), (RuntimeError, 'runtime'),
        (TypeError, 'type')) if isinstance(exception, cls)), 'other')
    frames = []
    package = Path(__file__).parent.resolve()
    allowed = known_sources()
    for frame in traceback.extract_tb(exception.__traceback__)[-12:]:
        try:relative = Path(frame.filename).resolve().relative_to(package).as_posix()
        except ValueError:
            # Frozen co_filename may retain its build-time prefix or be relative.
            filename = '/'+frame.filename.replace('\\','/')
            relative = filename.rpartition('/covex_label_manager/')[2]
            if not relative and filename.rsplit('/',1)[-1] == 'main_qt.py':relative='main_qt.py'
        if relative in allowed:
            frames.append(dict(source=relative, line=frame.lineno))
    return dict(category=category, frames=frames)


def known_sources():
    # PyInstaller stores most Python modules in PYZ, not physical .py files.
    # Already-loaded package identifiers remain available in the portable.
    sources = {'main_qt.py'} | {p.relative_to(Path(__file__).parent).as_posix()
        for p in Path(__file__).parent.rglob('*.py')}
    prefix = 'covex_label_manager.'
    sources.update(name[len(prefix):].replace('.', '/')+'.py'
        for name in tuple(sys.modules) if name.startswith(prefix)
        and all(part.isidentifier() for part in name.split('.')))
    return sources


def process_error(detail):
    if _active is not None:_active.process_error(detail)


def _directory(root):
    # Prefer the configured DATA folder, never the executable's resource tree.
    # If it is protected, a per-data-root opaque key isolates the local fallback.
    root = Path(root).resolve()
    preferred = root / 'diagnostics'
    try:
        preferred.mkdir(parents=True, exist_ok=True)
        probe = preferred / (uuid.uuid4().hex + '.probe')
        with probe.open('x'):
            pass
        probe.unlink()
        return preferred
    except OSError:
        local = Path(os.environ.get('LOCALAPPDATA') or
                     os.environ.get('XDG_STATE_HOME') or Path.home() / '.local/state')
        key = hashlib.sha256(os.fsencode(root)).hexdigest()[:16]
        fallback = local / 'COVEXLabelManager' / 'diagnostics' / key
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


class Diagnostics:
    MAX_BYTES = 256 * 1024
    BACKUPS = 3

    def __init__(self, root, *, install_hooks=True):
        global _active
        self.directory = _directory(root)
        self.session = uuid.uuid4().hex
        self.marker = self.directory / ('session-' + self.session + '.json')
        self.closed = False
        self.failed_io = False
        self.notifier = None
        self.lock = threading.RLock()
        self.logger = logging.Logger('covex-diagnostics-' + self.session)
        self.handler = RotatingFileHandler(self.directory / 'technical.jsonl',
            maxBytes=self.MAX_BYTES, backupCount=self.BACKUPS, encoding='utf-8')
        self.handler.setFormatter(logging.Formatter('%(message)s'))
        self.handler.handleError = self._logging_failure
        self.logger.addHandler(self.handler)
        self.environment = dict(version=__version__, python=platform.python_version(),
            system=platform.system(), architecture=platform.machine(), frozen=bool(getattr(sys, 'frozen', False)))
        self.environment['phase'] = 'R8A'
        # Read only the opaque commit, never paths/packages from the manifest.
        try:
            from .paths import installation_dir
            import re
            commit = json.loads((installation_dir()/'BUILD_MANIFEST.json').read_text(encoding='utf-8')).get('commit')
            if isinstance(commit, str) and re.fullmatch('[a-f0-9]{40}', commit):
                self.environment['build_commit'] = commit
        except (OSError, ValueError, AttributeError):pass
        # Never store host name, user name, environment dump, paths or CLI args.
        markers = sorted(self.directory.glob('session-*.json'), key=lambda p:p.stat().st_mtime)
        self.previous_unfinished = False
        for path in markers:
            try:
                marker = json.loads(path.read_text(encoding='utf-8'))
                if not marker.get('normal_end'):
                    self.previous_unfinished = True
            except (ValueError, OSError):
                self.previous_unfinished = True
        self._marker(False)
        # Bounded marker retention, including interrupted sessions.
        for path in markers[:-15]:
            path.unlink(missing_ok=True)
        self.old_sys_hook = sys.excepthook
        self.old_thread_hook = threading.excepthook
        self.hooks_installed = install_hooks
        self.previous_active = _active
        _active = self
        if install_hooks:
            sys.excepthook = self.sys_hook
            threading.excepthook = self.thread_hook
        self.record('session_start')
        if self.previous_unfinished:
            self.record('previous_unfinished')

    def _marker(self, normal):
        tmp = self.marker.with_suffix('.tmp')
        tmp.write_text(json.dumps(dict(session=self.session, normal_end=normal,
            at=int(time.time()))), encoding='utf-8')
        os.replace(tmp, self.marker)

    def record(self, name, **fields):
        if name not in EVENTS:
            raise ValueError('Unknown technical event')
        record = dict(at=int(time.time()), session=self.session, event=name)
        # No arbitrary string values or exception messages pass this boundary.
        if fields.get('module') in MODULES:record['module'] = fields['module']
        for key in ('returncode', 'elapsed_ms', 'count'):
            value = fields.get(key)
            if type(value) is int:record[key] = max(-2**32, min(value, 2**32))
        for key in ('cancelled', 'normal'):
            if type(fields.get(key)) is bool:record[key] = fields[key]
        with self.lock:
            try:
                self.logger.info(json.dumps(record, ensure_ascii=True))
                self.handler.flush()
            except OSError:
                self.failed_io = True

    def _logging_failure(self, record):
        self.failed_io = True

    def exception(self, name, exception):
        self.record(name)
        self.process_error(technical_exception(exception))

    def process_error(self, detail):
        if not isinstance(detail, dict):return
        category = detail.get('category')
        if category not in ('permission','io','validation','runtime','type','other'):category='other'
        allowed = known_sources()
        raw_frames = detail.get('frames', [])
        if not isinstance(raw_frames, list):raw_frames=[]
        frames = [dict(source=f['source'], line=f['line'])
            for f in raw_frames[:12]
            if isinstance(f, dict) and isinstance(f.get('source'), str)
            and f['source'] in allowed and type(f.get('line')) is int]
        with self.lock:
            try:
                self.logger.info(json.dumps(dict(at=int(time.time()), session=self.session,
                    event='error_detail', category=category, frames=frames)))
                self.handler.flush()
            except OSError:self.failed_io = True

    def sys_hook(self, kind, exception, tb):
        self.exception('python_error', exception.with_traceback(tb))
        if self.notifier is not None:self.notifier()
        # Qt invokes sys.excepthook for failed slots. Do not print raw GMP data
        # or claim success; the UI notifier explicitly reports the failure.

    def thread_hook(self, args):
        self.exception('thread_error', args.exc_value.with_traceback(args.exc_traceback))
        if self.notifier is not None:self.notifier()

    def export(self, destination):
        destination = Path(destination)
        if destination.resolve().is_relative_to(self.directory.resolve()):
            raise ValueError('Guarde el ZIP fuera de la carpeta técnica de diagnósticos.')
        # Construct entirely from known technical files, never recurse into DATA.
        # Reject symlinks to prevent accidental inclusion of a document/database.
        with self.lock:
            self.record('export')
            allowed_sources = known_sources()
            tmp = destination.with_name(destination.name + '.' + uuid.uuid4().hex + '.tmp')
            try:
                with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as archive:
                    archive.writestr('technical-state.json', json.dumps(dict(
                        **self.environment, session=self.session,
                        previous_unfinished=self.previous_unfinished,
                        diagnostic_io_failed=self.failed_io,
                        native_capture='not_guaranteed',
                        note='Una sesion sin cierre normal no demuestra un fallo.'), indent=2))
                    for name in ['technical.jsonl'] + ['technical.jsonl.'+str(n) for n in range(1, self.BACKUPS+1)]:
                        path = self.directory / name
                        if path.is_file() and not path.is_symlink():
                            # Revalidate even our own files: an operator could
                            # have replaced a log with a document or raw dump.
                            lines = []
                            with path.open(encoding='utf-8', errors='replace') as source:
                                for line in source.read(self.MAX_BYTES).splitlines():
                                    if len(line) > 8192:continue
                                    try:raw = json.loads(line)
                                    except ValueError:continue
                                    if not isinstance(raw, dict):continue
                                    import re
                                    sid = raw.get('session')
                                    if not isinstance(sid, str) or not re.fullmatch('[a-f0-9]{32}', sid):continue
                                    name_event = raw.get('event')
                                    if name_event not in EVENTS | {'error_detail'}:continue
                                    clean = dict(session=sid, event=name_event)
                                    for key in ('at', 'returncode', 'elapsed_ms', 'count'):
                                        if type(raw.get(key)) is int:clean[key] = raw[key]
                                    for key in ('normal', 'cancelled'):
                                        if type(raw.get(key)) is bool:clean[key] = raw[key]
                                    if raw.get('module') in MODULES:clean['module'] = raw['module']
                                    if raw.get('category') in ('permission','io','validation','runtime','type','other'):
                                        clean['category'] = raw['category']
                                    clean_frames = []
                                    for frame in raw.get('frames', [])[:12] if isinstance(raw.get('frames'), list) else []:
                                        if (isinstance(frame, dict) and isinstance(frame.get('source'), str) and frame['source'] in allowed_sources
                                                and type(frame.get('line')) is int):
                                            clean_frames.append(dict(source=frame['source'], line=frame['line']))
                                    if clean_frames:clean['frames'] = clean_frames
                                    lines.append(json.dumps(clean))
                                    if len(lines) >= 4096:break
                            archive.writestr(name, '\n'.join(lines))
                os.replace(tmp, destination)
            finally:tmp.unlink(missing_ok=True)
        return destination

    def close(self, normal=True):
        global _active
        if self.closed:return
        self.record('session_end', normal=normal)
        try:self._marker(normal)
        except OSError:self.failed_io = True
        if self.hooks_installed:
            sys.excepthook = self.old_sys_hook
            threading.excepthook = self.old_thread_hook
        self.notifier = None
        self.handler.close()
        self.closed = True
        _active = self.previous_active
