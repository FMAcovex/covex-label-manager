"""Conservative publication guard. Does not replace document/PR review."""
import re
import subprocess
from pathlib import Path

FORBIDDEN={'.pdf','.doc','.docx','.xls','.xlsx','.csv','.sqlite','.db','.zip','.bundle','.pem','.pfx','.key','.png','.jpg','.jpeg'}
PATTERNS=[re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),
          re.compile(r'github_pat_[A-Za-z0-9_]{40,}'),
          re.compile(r'AKIA[A-Z0-9]{16}'),
          re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
          re.compile(r'https://[^\s"\']*covex[^\s"\']*\.sharepoint\.com',re.I)]

def check(root,paths):
    failures=[]
    for relative in paths:
        path=Path(relative)
        if path.suffix.lower() in FORBIDDEN or path.name.startswith('.env') or 'data' in path.parts:
            failures.append(str(path));continue
        try:text=(Path(root)/path).read_text(encoding='utf-8')
        except UnicodeDecodeError:failures.append(str(path));continue
        if any(pattern.search(text) for pattern in PATTERNS):failures.append(str(path))
    if failures:raise ValueError('Publication guard rejected paths: '+', '.join(failures))

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=root,text=True).split('\0')
    check(root,[p for p in paths if p])
    print('Publication guard passed: no document/data/binary assets or matched credential patterns.')
