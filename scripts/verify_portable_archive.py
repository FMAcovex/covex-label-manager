"""Verify CRC, complete file inventory and SHA256 of the Qt portable ZIP."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile


def verify_archive(archive):
    archive = Path(archive)
    prefix = 'COVEXLabelManager_Qt/'
    manifest_name = prefix + 'BUILD_MANIFEST.json'
    with zipfile.ZipFile(archive) as package:
        bad = package.testzip()
        if bad:
            raise ValueError('Archive CRC failed: ' + bad)
        files = {}
        seen = set()
        for entry in package.infolist():
            name = entry.filename
            parts = PurePosixPath(name).parts
            if ('\\' in name or ':' in name or name.startswith('/') or
                    '..' in parts or not name.startswith(prefix)):
                raise ValueError('Unsafe archive path: ' + name)
            normalized = name.casefold()
            if normalized in seen:
                raise ValueError('Duplicate archive path: ' + name)
            seen.add(normalized)
            if not entry.is_dir():
                files[name] = entry
        if manifest_name not in files:
            raise ValueError('Build manifest missing')
        manifest = json.loads(package.read(manifest_name))
        expected = {}
        for name, digest in manifest['files'].items():
            normalized = name.replace('\\', '/')
            parts = PurePosixPath(normalized).parts
            if normalized.startswith('/') or '..' in parts or ':' in normalized:
                raise ValueError('Unsafe manifest path: ' + name)
            full = prefix + normalized
            if full in expected:
                raise ValueError('Duplicate manifest path: ' + name)
            expected[full] = digest
        if set(files) != set(expected) | {manifest_name}:
            raise ValueError('Archive and manifest file inventories differ')
        required = {
            prefix + 'COVEXLabelManager_Qt.exe',
            prefix + 'legacy/COVEXLabelManager_Legacy.exe',
            prefix + '_internal/covex_label_manager/qt_ui/chevron.svg',
        }
        if not required <= files.keys():
            raise ValueError('Required Qt/Legacy executable or UI resource missing')
        for name, digest in expected.items():
            actual = hashlib.sha256(package.read(name)).hexdigest()
            if actual != digest:
                raise ValueError('Packaged file SHA256 mismatch: ' + name)
    return {
        'ok': True, 'archive': archive.name,
        'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
        'commit': manifest['commit'], 'github_run': manifest['github_run'],
        'verified_files': len(expected), 'crc_ok': True,
        'qt_legacy_resources_present': True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = verify_archive(args.archive)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
