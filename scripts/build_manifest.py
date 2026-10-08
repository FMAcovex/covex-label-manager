"""Record build provenance and every packaged file hash (not bit-exact output)."""
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

root=Path(sys.argv[1])
try:commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
except (OSError,subprocess.CalledProcessError):commit='not available'
manifest={'commit':commit,'python':platform.python_version(),'platform':platform.platform(),
          'github_run':os.environ.get('GITHUB_RUN_ID','local'),
          'packages':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},
          'files':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(root.rglob('*')) if p.is_file() and p.name!='BUILD_MANIFEST.json'}}
(root/'BUILD_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
