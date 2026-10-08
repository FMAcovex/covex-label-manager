"""Local document guards, independent of names and revision identifiers."""
from pathlib import Path
import hashlib

KNOWN_OVERFLOW_PDF = 'dcb55be1c82209a9058054fd7100fd35de496bb31404c52278fca4439f5436a5'

def verify_documents(version, root):
    for path_key, hash_key in (('master_pdf', 'pdf_sha256'), ('original_file', 'source_sha256')):
        if not version[path_key]:
            continue
        root_path = Path(root).resolve()
        path = (root_path / version[path_key]).resolve()
        if not path.is_relative_to(root_path) or not path.is_file():
            raise ValueError('Integridad comprometida: documento inexistente o fuera de los datos.')
        if hashlib.sha256(path.read_bytes()).hexdigest() != version[hash_key]:
            raise ValueError('Integridad comprometida: el documento ha cambiado.')

def verify_renderable(version):
    if version['pdf_sha256'] == KNOWN_OVERFLOW_PDF:
        raise ValueError('El PDF original contiene una tabla que desborda el marco. Seleccione 00-R1 y revise su aprobación documental; cambiar el nombre o la revisión no corrige la geometría.')
