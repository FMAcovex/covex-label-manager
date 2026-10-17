"""Small synthetic ZIPs, never real executables or document assets."""
import hashlib
import json
import zipfile
import pytest
from scripts.verify_portable_archive import verify_archive


def archive(tmp_path, change=None):
    files = {'COVEXLabelManager_Qt.exe': b'SYNTHETIC QT',
             'legacy/COVEXLabelManager_Legacy.exe': b'SYNTHETIC LEGACY',
             '_internal/covex_label_manager/qt_ui/chevron.svg': b'<svg/>'}
    manifest = {'commit': 'synthetic', 'github_run': 'local', 'files': {
        name.replace('/', '\\'): hashlib.sha256(data).hexdigest()
        for name, data in files.items()}}
    if change:
        change(files, manifest)
    target = tmp_path / 'synthetic.zip'
    with zipfile.ZipFile(target, 'w') as package:
        for name, data in files.items():
            package.writestr('COVEXLabelManager_Qt/' + name, data)
        package.writestr('COVEXLabelManager_Qt/BUILD_MANIFEST.json', json.dumps(manifest))
    return target


def test_complete_archive_crc_inventory_and_hashes(tmp_path):
    target = archive(tmp_path)
    result = verify_archive(target)
    assert result['ok'] and result['crc_ok'] and result['verified_files'] == 3
    assert result['sha256'] == hashlib.sha256(target.read_bytes()).hexdigest()


@pytest.mark.parametrize('change', [
    lambda f, m: f.update({'COVEXLabelManager_Qt.exe': b'CORRUPTED'}),
    lambda f, m: f.pop('legacy/COVEXLabelManager_Legacy.exe'),
    lambda f, m: f.update({'unexpected.txt': b'UNREGISTERED'}),
    lambda f, m: f.update({'../escape.txt': b'UNSAFE'}),
    lambda f, m: m['files'].update({'../escape.txt': 'bad'}),
])
def test_modified_incomplete_or_unsafe_archive_is_rejected(tmp_path, change):
    with pytest.raises(ValueError):
        verify_archive(archive(tmp_path, change))
