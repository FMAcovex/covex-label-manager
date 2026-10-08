"""Refuse any packaging rebuild that could remove an existing user instance."""
import os
import sys
from pathlib import Path

def ensure_safe(destination,configured_data=None):
    destination=Path(destination).resolve()
    if (destination/'data').exists() or any(destination.rglob('*.sqlite')):
        raise ValueError('Destino con datos de usuario: construya en otra carpeta limpia.')
    if configured_data:
        data=Path(configured_data).expanduser().resolve()
        if data==destination or data.is_relative_to(destination):
            raise ValueError('COVEX_LABEL_DATA está dentro del destino: construya en otra carpeta.')

if __name__=='__main__':
    ensure_safe(sys.argv[1],os.environ.get('COVEX_LABEL_DATA'))
