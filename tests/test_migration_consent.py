"""Explicit interactive consent, cancellation without writes, and restart recovery."""
import os
from contextlib import closing
from pathlib import Path
import pytest
from v3_fixture import create
from covex_label_manager.storage import Store
from covex_label_manager.migration_v4 import (MigrationConsentRequired,MigrationCancelled,
    migrate,recover,PHASES,sha,active_path)


def inventory(root):
    return sorted((p.relative_to(root).as_posix(),sha(p) if p.is_file() else None)
                  for p in root.rglob('*'))


def test_no_implicit_migration_and_cancel_is_read_only(tmp_path):
    root=tmp_path/'data'
    with closing(create(root)):pass
    before=inventory(root)
    with pytest.raises(MigrationConsentRequired):Store(root)
    with pytest.raises(MigrationConsentRequired):migrate(root)
    assert inventory(root)==before
    paths=[]
    with pytest.raises(MigrationCancelled):Store(root,migration_confirmation=lambda p:paths.append(p))
    assert paths==[root.resolve()]
    assert inventory(root)==before
    with closing(Store(root,migration_confirmation=lambda _:True)) as s:
        assert s.db.execute('PRAGMA user_version').fetchone()[0]==4
    # Existing v4 and fresh installation never ask for migration consent.
    def forbidden(_):raise AssertionError('unexpected prompt')
    with closing(Store(root,migration_confirmation=forbidden)):pass
    with closing(Store(tmp_path/'fresh',seed=False,migration_confirmation=forbidden)):pass


@pytest.mark.parametrize('phase',PHASES)
def test_recovery_does_not_silently_reauthorize_legacy(tmp_path,phase):
    root=tmp_path/'data'
    with closing(create(root)):pass
    def crash(name,_):
        if name==phase:raise RuntimeError('synthetic power loss')
    with pytest.raises(RuntimeError):migrate(root,crash,confirmed=True)
    result=recover(root)
    if result=='v3':
        before=inventory(root)
        with pytest.raises(MigrationCancelled):Store(root,migration_confirmation=lambda _:False)
        assert inventory(root)==before
        with closing(Store(root,migration_confirmation=lambda _:True)):pass
    else:
        with closing(Store(root)):pass
    assert active_path(root).parent.name=='storage_v4'


def test_qt_startup_uses_cancel_default_and_accepts_only_yes(tmp_path,monkeypatch):
    pytest.importorskip('PySide6')
    from PySide6.QtWidgets import QApplication,QMessageBox
    from main_qt import LocalSession
    app=QApplication.instance() or QApplication([])
    root=tmp_path/'data'
    with closing(create(root)):pass
    monkeypatch.setenv('COVEX_LABEL_DATA',str(root))
    before=inventory(root);calls=[]
    def cancel(parent,title,text,buttons,default):
        calls.append((text,default));return QMessageBox.StandardButton.Cancel
    monkeypatch.setattr(QMessageBox,'question',cancel)
    with pytest.raises(MigrationCancelled):LocalSession()
    assert inventory(root)==before
    assert calls[0][1]==QMessageBox.StandardButton.Cancel and str(root) in calls[0][0]
    monkeypatch.setattr(QMessageBox,'question',lambda *args:QMessageBox.StandardButton.Yes)
    session=LocalSession();session.close()
    session=LocalSession();session.close()


@pytest.mark.skipif(os.name!='nt' and not os.environ.get('DISPLAY'),reason='Tk requires desktop')
def test_tk_startup_cancel_then_accept_and_reopen(tmp_path,monkeypatch):
    from tkinter import messagebox
    from covex_label_manager.gui import Application
    root=tmp_path/'data'
    with closing(create(root)):pass
    monkeypatch.setenv('COVEX_LABEL_DATA',str(root))
    before=inventory(root);calls=[]
    def cancel(*args,**kw):calls.append(kw);return False
    monkeypatch.setattr(messagebox,'askokcancel',cancel)
    with pytest.raises(MigrationCancelled):Application()
    assert inventory(root)==before and calls[0]['default']=='cancel'
    monkeypatch.setattr(messagebox,'askokcancel',lambda *a,**kw:True)
    app=Application();app.update();app.store.close();app.destroy()
    monkeypatch.setattr(messagebox,'askokcancel',lambda *a,**kw:pytest.fail('v4 must not ask'))
    app=Application();app.update();app.store.close();app.destroy()
