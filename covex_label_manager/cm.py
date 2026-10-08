from __future__ import annotations
import re
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn


def parse_cm(path):
    doc=Document(path)
    category='Sin clasificar'
    results=[]
    tbl_map={id(t._element):t for t in doc.tables}
    current_section=''
    for el in doc.element.body.iterchildren():
        if el.tag==qn('w:p'):
            txt=''.join(node.text or '' for node in el.iter(qn('w:t'))).strip()
            if re.match(r'^\d+(?:\.\d+)*(?:\s*[-.]|\s+)',txt) and len(txt)<110:
                if re.match(r'^\d+(?:\.\d+)*\s*[-.]?\s*[A-Z]',txt):
                    current_section=txt
        if el.tag==qn('w:tbl') and id(el) in tbl_map:
            table=tbl_map[id(el)]
            if not any(row.cells and 'Material' in row.cells[0].text for row in list(table.rows)[:1]) and not results:
                continue
            for row in table.rows:
                if len(row.cells)<2:
                    continue
                name=row.cells[0].text.strip().replace('\n',' ')
                rawcode=row.cells[1].text.strip().replace('\n',' ')
                if not name or not rawcode or name.lower() in ['material','nombre','producto']:
                    continue
                if len(rawcode)>160 or 'FIRMA' in rawcode.upper():
                    continue
                code=re.sub(r'\s*\(.*$', '', rawcode).strip()
                results.append({'name':name,'code':code,'category':current_section or 'CM - pendiente de categoria',
                                'source_ref':'CM/V03/03-2026'})
    unique={ (x['name'].lower(),x['code'].lower(),x['category'].lower()): x for x in results }
    return list(unique.values())
