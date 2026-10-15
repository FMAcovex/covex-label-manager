"""Portable canonical JSON v1: NFC strings, exact decimal spelling, no floats in hashes.

Floats use their shortest Python decimal roundtrip (str); decimal and float values
with that same decimal value hash alike. Exponents and negative zero disappear.
No locale, platform JSON float formatting or Unicode escape choices enter hashes.
"""
import hashlib
import json
import math
import unicodedata
from decimal import Decimal


def canonical(value):
    if value is None:return 'null'
    if value is True:return 'true'
    if value is False:return 'false'
    if isinstance(value, (int, float, Decimal)):
        if isinstance(value,float) and not math.isfinite(value):raise ValueError('Número no finito.')
        number=Decimal(str(value))
        if not number.is_finite():raise ValueError('Número no finito.')
        if not number:return '0'
        text=format(number,'f')
        return text.rstrip('0').rstrip('.') if '.' in text else text
    if isinstance(value,str):
        text=unicodedata.normalize('NFC',value)
        text.encode('utf-8',errors='strict')
        return json.dumps(text,ensure_ascii=False,separators=(',',':'))
    if isinstance(value,(list,tuple)):
        return '['+','.join(canonical(v) for v in value)+']'
    if isinstance(value,dict):
        if any(not isinstance(k,str) for k in value):raise ValueError('Claves de texto obligatorias.')
        normalized={unicodedata.normalize('NFC',k):v for k,v in value.items()}
        if len(normalized)!=len(value):raise ValueError('Claves Unicode duplicadas.')
        return '{'+','.join(canonical(k)+':'+canonical(normalized[k]) for k in sorted(normalized))+'}'
    raise ValueError('Tipo no admitido en JSON canónico: '+type(value).__name__)


def digest(value):return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def parse(text):
    def invalid(value):raise ValueError('Número no finito: '+value)
    def pairs(items):
        out={}
        for k,v in items:
            k=unicodedata.normalize('NFC',k)
            if k in out:raise ValueError('Clave JSON duplicada.')
            out[k]=v
        return out
    return json.loads(text,parse_float=Decimal,parse_constant=invalid,object_pairs_hook=pairs)


def json_digest(text):return digest(parse(text))
