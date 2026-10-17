"""Per-container input and Excel (TSV or semicolon CSV) parsing."""
from __future__ import annotations
import csv
import re
from decimal import Decimal, InvalidOperation
from io import StringIO

_MASS_UNIT = re.compile(r'\s*(kg|mg|g)\s*$',re.IGNORECASE)
MASS_FACTORS={'kg':Decimal('1'),'g':Decimal('0.001'),'mg':Decimal('0.000001')}


def mass_parts(value):
    raw=str(value).strip();match=_MASS_UNIT.search(raw)
    unit=match.group(1).lower() if match else 'kg'
    numeric=raw[:match.start()].strip() if match else raw
    try:amount=Decimal(numeric.replace(' ','').replace(',','.'))
    except InvalidOperation:raise ValueError('Introduzca un peso en kg, g o mg, por ejemplo 350 g. Sin unidad se interpreta kg.')
    if not amount.is_finite() or not 0<=amount*MASS_FACTORS[unit]<Decimal('1e8'):
        raise ValueError('El peso está fuera de rango.')
    return numeric,unit,amount


def mass_numeric_text(value,target_unit='kg'):
    """Convert to an approved documentary suffix, without changing stored input.

    Unsuffixed historical input always means kg. Matching units retain the
    original numeric typography; conversions use exact decimal arithmetic.
    """
    if not str(value).strip():return ''
    target_unit=target_unit.strip().lower()
    if target_unit not in MASS_FACTORS:raise ValueError('Unidad documental de masa no admitida: '+target_unit)
    numeric,unit,amount=mass_parts(value)
    if unit==target_unit:return numeric
    converted=format(amount*MASS_FACTORS[unit]/MASS_FACTORS[target_unit],'f')
    if '.' in converted:converted=converted.rstrip('0').rstrip('.')
    return converted.replace('.',',') if ',' in numeric else converted

COLUMN_KEYS = ('numero','lote','pn','pb','conservacion')


def parse_tabular_vessels(text, count, prior=None):
    """Parse a pasted Excel table; comma decimals are safe (never comma separator)."""
    data = {str(k):dict(v) for k,v in (prior or {}).items()}
    text = text.replace('\r\n','\n').strip('\n \t')
    if not text.strip():
        return data
    if '\t' in text:
        reader=csv.reader(StringIO(text),delimiter='\t')
    elif ';' in text:
        reader=csv.reader(StringIO(text),delimiter=';')
    else:
        raise ValueError('Pegue columnas desde Excel (tabuladas) o CSV separado por punto y coma.')
    rows=[list(map(str.strip,r)) for r in reader if any(c.strip() for c in r)]
    keys={'numero':'numero','n':'numero','nº':'numero','num':'numero',
          'envase':'numero','numero de envase':'numero','número':'numero',
          'lote':'lote','pn':'pn','peso neto':'pn','peso neto kg':'pn',
          'pb':'pb','peso bruto':'pb','peso bruto kg':'pb',
          'condiciones':'conservacion','conservacion':'conservacion',
          'conservación':'conservacion'}
    header_units={}
    for key,title in (('pn','peso neto'),('pb','peso bruto')):
        for unit in MASS_FACTORS:
            for heading in (f'{key} {unit}',f'{key} ({unit})',f'{title} {unit}',f'{title} ({unit})'):
                keys[heading]=key;header_units[heading]=unit
    first=[c.lower().strip() for c in rows[0]]
    units={}
    if first and first[0] in keys:
        col=[keys.get(k,k) for k in first]
        units={keys[k]:header_units[k] for k in first if k in header_units}
        if len(set(col))!=len(col) or col[0]!='numero' or any(k not in COLUMN_KEYS for k in col):
            raise ValueError('Cabecera inválida: Nº | Lote | PN | PB | Conservación.')
        rows=rows[1:]
    else:
        col=list(COLUMN_KEYS[:len(first)])
    seen=set()
    for n,row in enumerate(rows,1):
        if len(row)>len(col):
            raise ValueError(f'Fila {n}: demasiadas columnas.')
        try: index=int(row[0])
        except (ValueError,IndexError):raise ValueError(f'Fila {n}: número de envase inválido.')
        if index<1 or index>count:
            raise ValueError(f'Fila {n}: el envase debe estar entre 1 y {count}.')
        if index in seen:
            raise ValueError(f'Fila {n}: el envase {index} está repetido.')
        seen.add(index)
        d=dict(data.get(str(index),{}))
        for k,v in zip(col[1:],row[1:]):
            if v and k in units and not _MASS_UNIT.search(v):v+=' '+units[k]
            if v:d[k]=v
            else:d.pop(k,None)
        if d:data[str(index)]=d
        else:data.pop(str(index),None)
    return data


def parse_mass(value):
    if value is None or str(value).strip()=='':return None
    _,unit,amount=mass_parts(value)
    return float(amount*MASS_FACTORS[unit])


def validate_vessel_masses(values,number):
    def kilograms(raw):
        if raw is None or not str(raw).strip():return None
        _,unit,amount=mass_parts(raw);return amount*MASS_FACTORS[unit]
    pn=kilograms(values.get('pn'));pb=kilograms(values.get('pb'))
    if pn is not None and pb is not None and pb<pn:
        raise ValueError(f'El peso bruto del envase {number} es menor que su peso neto.')
