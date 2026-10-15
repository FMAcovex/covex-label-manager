"""R3D: native configuration parity with legacy admin and clear modal palette."""
import json
import zipfile
import pytest
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QMessageBox,QFileDialog,QDialog,QLineEdit,QCheckBox,QDialogButtonBox
from PySide6.QtCore import Qt
from test_emission_work_qt import studio


def test_settings_is_native_without_launching_tk(studio,monkeypatch):
    w,api,app=studio
    def forbidden(*a,**k):pytest.fail('Configuración launched legacy Tk')
    monkeypatch.setattr(w,'open_legacy',forbidden)
    w.navigate('settings');app.processEvents()
    assert w.stack.currentWidget() is w.settings_page
    assert w.settings_page.isEnabled()
    assert w.settings_tabs.count()==5
    assert w.settings_counts['labels'].text()==str(api.stats()['labels'])
    assert w.settings_data_path.isReadOnly()
    assert w.settings_data_path.text()==api.location()
    assert w.nav['settings'].isChecked()


def test_operator_validation_and_backup_are_native(studio,monkeypatch):
    w,api,app=studio;w.navigate('settings')
    original=api.setting('operator')
    w.settings_operator.setText('x')
    assert not w.save_settings_operator() and api.setting('operator')==original
    w.settings_operator.setText('Operador sintético de prueba')
    assert w.save_settings_operator()
    assert api.setting('operator')=='Operador sintético de prueba'
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Cancel)
    assert not w.create_settings_backup()
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
    monkeypatch.setattr(QMessageBox,'information',lambda *a,**k:QMessageBox.StandardButton.Ok)
    assert w.create_settings_backup()
    backups=list((api._repository.root/'backups').glob('covex_labels_backup_*.zip'))
    assert len(backups)==1
    with zipfile.ZipFile(backups[0]) as archive:
        assert 'backup-manifest.json' in archive.namelist()
        data=json.loads(archive.read('backup-manifest.json'))
        assert data['files']


def test_cm_import_no_delete_and_duplicates(studio,monkeypatch,tmp_path):
    w,api,app=studio;w.navigate('settings')
    source=tmp_path/'CM-sintetico.docx';source.write_bytes(b'dummy')
    rows=[{'name':'MATERIAL SINTETICO','code':'SYN-R3D','category':'Demo','source_ref':'SYN-R3D'}]
    monkeypatch.setattr(QFileDialog,'getOpenFileName',lambda *a,**k:(str(source),''))
    monkeypatch.setattr(api,'read_cm',lambda path:rows)
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Cancel)
    before=api.stats()['materials']
    assert not w.import_settings_cm() and api.stats()['materials']==before
    monkeypatch.setattr(QMessageBox,'question',lambda *a,**k:QMessageBox.StandardButton.Yes)
    assert w.import_settings_cm()
    assert api.stats()['materials']==before+1
    # No duplicate entries on re-import: same service's INSERT OR IGNORE contract.
    assert w.import_settings_cm()
    assert api.stats()['materials']==before+1


def test_pending_status_never_autoapproves(studio,monkeypatch):
    w,api,app=studio;w.navigate('settings')
    assert w.settings_status.rowCount()==len(api.status_masters())
    monkeypatch.setattr(QMessageBox,'information',lambda *a,**k:QMessageBox.StandardButton.Ok)
    assert not w.approve_settings_status()  # no selection
    # The genuine service is the only approval boundary; cancelled modals never call it.
    pending={'kind':'synthetic','name':'Estado ficticio','version':'00','state':'PENDING','approval_ref':None}
    monkeypatch.setattr(api,'status_masters',lambda:[pending])
    monkeypatch.setattr(api,'status_master',lambda kind:pending)
    approvals=[]
    monkeypatch.setattr(api,'approve_status_master',lambda *args:approvals.append(args))
    w.refresh_native_settings()
    w.settings_status.selectRow(0)
    monkeypatch.setattr(QDialog,'exec',lambda *args:QDialog.DialogCode.Rejected)
    assert not w.approve_settings_status()
    assert not approvals


def test_dark_os_modal_styles_have_light_explicit_background(studio):
    w,api,app=studio
    styles=w.styleSheet()
    assert 'QDialog, QMessageBox, QInputDialog' in styles
    assert '#F3F6F7' in styles
    assert 'QToolTip' in styles


def test_legacy_transition_keeps_all_87_feature_ids(studio):
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    matrix=(root/'docs'/'FUNCTIONAL_PRESERVATION_MATRIX.md').read_text(encoding='utf-8')
    ids=[line.split('|')[1].strip() for line in matrix.splitlines()
         if line.startswith('| ') and len(line.split('|')[1].strip())==3
         and line.split('|')[1].strip()[0].isalpha()
         and line.split('|')[1].strip()[1:].isdigit()]
    assert len(ids)==87 and len(set(ids))==87
