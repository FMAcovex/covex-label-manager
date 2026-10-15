"""Per-container input and Excel (TSV or semicolon CSV) parsing."""
from __future__ import annotations
import csv
import re
from io import StringIO

_MASS_UNIT = re.compile(r'\s*kg\s*$',re.IGNORECASE)


def mass_numeric_text(value):
    """Return the numeric display portion of an optional kilograms entry.

    Preserve the user's original text separately in the work/snapshot; this
    function is only used for numeric validation and masters with a KG suffix.
    """
    return _MASS_UNIT.sub('',str(value).strip()).strip()

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
    first=[c.lower().strip() for c in rows[0]]
    if first and first[0] in keys:
        col=[keys.get(k,k) for k in first]
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
            if v:d[k]=v
            else:d.pop(k,None)
        if d:data[str(index)]=d
        else:data.pop(str(index),None)
    return data


def parse_mass(value):
    if value is None or str(value).strip()=='':return None
    # EU comma/dot decimal. Accept an explicit kg suffix; never accept g or
    # silently convert a different unit. The numeric comparison remains in kg.
    value=mass_numeric_text(value).replace(' ','').replace(',','.')
    try:out=float(value)
    except ValueError:raise ValueError('Introduzca un peso en kg, por ejemplo 0,3558 o 0,3558 kg.')
    if not (0<=out<1e8):raise ValueError('El peso está fuera de rango.')
    return out


def validate_vessel_masses(values,number):
    pn=parse_mass(values.get('pn'))
    pb=parse_mass(values.get('pb'))
    if pn is not None and pb is not None and pb+1e-10<pn:
        raise ValueError(f'El peso bruto del envase {number} es menor que su peso neto.')
