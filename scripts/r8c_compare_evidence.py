"""Require true before/after coverage AND unchanged legacy PDF rasters."""
import argparse
import json
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True)
p.add_argument('--report',type=Path,required=True);a=p.parse_args()
before=json.loads(a.before.read_text(encoding='utf-8'));after=json.loads(a.after.read_text(encoding='utf-8'))
assert before['ok'] and after['ok'] and before['synthetic_only'] and after['synthetic_only']
assert before['baseline'] and not after['baseline'] and before['scale']==after['scale']
assert before['source_commit'] in (None,'56399394424896a1adbd56a91882a7eb49282632')
assert len(before['captures'])==6 and len(after['captures'])==12
assert after['combined_cases']==6 and after['embedded_fonts']==12 and after['trial_production_blocked']
assert after['legacy_compositions']==3 and after['critical_crop_blocked']
comparisons=[]
for width in (1366,1920):
    name=f'{width}-historical-unchanged'
    old=next(p for p in before['pdfs'] if p['name']==name)
    new=next(p for p in after['pdfs'] if p['name']==name)
    assert old['raster_sha256']==new['raster_sha256'],(name,old,new)
    comparisons.append(dict(name=name,raster_sha256=new['raster_sha256'],unchanged=True))
result=dict(ok=True,synthetic_only=True,legacy_pdf_rasters=comparisons,
            before=before['source_commit'],after=after['source_commit'],scale=after['scale'])
a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
