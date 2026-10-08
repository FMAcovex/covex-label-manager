from __future__ import annotations
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import fitz


class ImportErrorLabel(RuntimeError):
    pass


def docx_to_pdf(path, output_dir):
    source=Path(path).resolve();destdir=Path(output_dir);destdir.mkdir(parents=True,exist_ok=True)
    if source.suffix.lower() in ('.png','.jpg','.jpeg'):
        img=fitz.open(source)
        try:
            dest=destdir/(source.stem+'.pdf')
            with fitz.open('pdf',img.convert_to_pdf()) as pdfdoc:
                pdfdoc.save(dest)
        finally:
            img.close()
        return dest
    if source.suffix.lower()=='.pdf':
        dest=destdir/source.name
        if source!=dest: shutil.copy2(source,dest)
        return dest
    if source.suffix.lower() not in ('.docx','.doc'):
        raise ImportErrorLabel('Se admite Word DOC/DOCX, PDF e imagen PNG/JPG.')
    expected=destdir/(source.stem+'.pdf')
    if sys.platform=='win32':
        # Use installed Word first to avoid deviations from the source design.
        s=str(source).replace("'","''");out=str(expected).replace("'","''")
        code=("$ErrorActionPreference='Stop';"
              "$w=New-Object -ComObject Word.Application;"
              "$w.Visible=$false; $w.DisplayAlerts=0; $w.AutomationSecurity=3; $doc=$null;"
              "try {$doc=$w.Documents.Open('"+s+"',$false,$true);"
              "$doc.ExportAsFixedFormat('"+out+"',17)}"
              "finally {if($doc){$doc.Close($false)}; $w.Quit()}")
        try:
            subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',code],
                           timeout=150,check=True,capture_output=True,creationflags=0x08000000)
            if expected.exists(): return expected
        except (OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired):
            pass
    libreoffice=shutil.which('soffice') or shutil.which('libreoffice')
    if libreoffice:
        with tempfile.TemporaryDirectory(prefix='covex_word_') as tmp:
            scratch=Path(tmp)
            try:
                subprocess.run([libreoffice,'-env:UserInstallation='+(scratch/'profile').as_uri(),
                    '--headless','--convert-to','pdf','--outdir',str(scratch),str(source)],
                    timeout=150,check=True,capture_output=True)
            except (OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as e:
                raise ImportErrorLabel('No se ha podido convertir el Word a PDF: '+str(e))
            converted=scratch/expected.name
            if converted.exists():
                shutil.copy2(converted,expected)
                return expected
    raise ImportErrorLabel('Para importar Word debe tener Microsoft Word o LibreOffice instalado. Tambien puede importar el PDF directamente.')


def auto_crop(pdf_path):
    d=fitz.open(pdf_path)
    p=d[0]
    page=p.rect
    rects=[]
    for shape in p.get_drawings():
        r=shape['rect']
        if r.width or r.height:
            if r.width==0 or r.height==0: r=fitz.Rect(r.x0-.35,r.y0-.35,r.x1+.35,r.y1+.35)
            rects.append(r)
    for b in p.get_text('blocks'):
        if b[6]==0:
            rects.append(fitz.Rect(*b[:4]))
    for im in p.get_images(full=True):
        for r in p.get_image_rects(im[0]):rects.append(r)
    if not rects:
        box=page
    else:
        box=rects[0]
        for r in rects[1:]:
            box=box|r
        box=fitz.Rect(max(0,box.x0-1.5),max(0,box.y0-1.5),min(page.width,box.x1+1.5),min(page.height,box.y1+1.5))
        if box.width<page.width*.2 or box.height<page.height*.2:
            box=page
    crop=[round(a,1) for a in box]
    info={'page_count':len(d),'page_width':round(page.width,2),'page_height':round(page.height,2)}
    d.close()
    return crop,info


def proposed_identity(path):
    stem=Path(path).stem
    rx=re.search(r'(?i)(?:VERSION\s*|\bv|\s)(\d{2,3})(?:\s*[rR])?$',stem)
    rev=rx.group(1) if rx else '00'
    name=(stem[:rx.start()] if rx else stem).strip(' -_.')
    parent=Path(path).parent.name
    category=parent if not parent.lower().startswith('version') else 'Sin clasificar'
    if 'ANULAD' in str(path).upper():
        category='ANULADA - revisar'
    return {'name':name.title(),'version':rev,'category':category}


def list_importable_files(folder):
    base=Path(folder)
    for p in sorted(base.rglob('*')):
        if p.is_file() and p.suffix.lower() in ('.docx','.doc','.pdf','.png','.jpg','.jpeg') and not p.name.startswith('~$'):
            yield p
