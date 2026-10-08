from __future__ import annotations
import os
import sys
from pathlib import Path


def package_dir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent


def installation_dir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def resource_dir() -> Path:
    return package_dir() / 'resources'


def data_dir() -> Path:
    override = os.environ.get('COVEX_LABEL_DATA')
    path = Path(override).expanduser().resolve() if override else installation_dir() / 'data'
    path.mkdir(parents=True, exist_ok=True)
    for sub in ['sources', 'pdf_masters', 'emissions', 'backups', 'cache']:
        (path / sub).mkdir(exist_ok=True)
    return path
