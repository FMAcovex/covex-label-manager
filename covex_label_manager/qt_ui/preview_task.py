"""A Qt waiter for one isolated PDF process; no MuPDF runs in this thread."""
import json
from pathlib import Path
import subprocess
import sys
from PySide6.QtCore import QThread, Signal


def discard_temporary(path):
    """Cleanup failure must not mask a result or escape a queued Qt callback."""
    try:Path(path).unlink(missing_ok=True)
    except OSError as ex:
        from ..diagnostics import error
        error('operation_error', ex)


class PreviewTask(QThread):
    completed=Signal(object)

    def __init__(self,parent,root,uid,generation,token,path,serial):
        super().__init__(parent)
        self.request=(root,uid,generation,token,path,serial)

    def run(self):
        from ..migration_v4 import atomic_json
        root,uid,generation,token,path,serial=self.request
        path=Path(path);job_path=path.with_suffix('.job.json')
        result_path=job_path.with_suffix('.result.json')
        payload=dict(uid=uid,generation=generation,stamp=token,path=path,serial=serial)
        try:
            if self.isInterruptionRequested():raise InterruptedError('Vista previa cancelada; el trabajo guardado no se ha modificado.')
            atomic_json(job_path,dict(contract=1,root=str(root),uid=uid,generation=generation,
                token=token,path=str(path),serial=serial))
            command=[sys.executable]
            if not getattr(sys,'frozen',False):command.append(str(Path(__file__).resolve().parents[2]/'main_qt.py'))
            command.extend(['--preview-job',str(job_path)])
            options={'creationflags':0x08000000} if sys.platform=='win32' else {}
            process=subprocess.run(command,capture_output=True,timeout=90,**options)
            payload['returncode']=process.returncode
            if self.isInterruptionRequested():raise InterruptedError('Vista previa cancelada; el trabajo guardado no se ha modificado.')
            if not result_path.is_file():
                raise ValueError(f'El motor de vista previa terminó sin informe (código {process.returncode}). Reintente la vista previa.')
            result=json.loads(result_path.read_text(encoding='utf-8'))
            if any(result.get(k)!=payload[k] for k in ('uid','generation','stamp','serial')) or Path(result['path'])!=path:
                raise ValueError('El resultado de vista previa pertenece a otro cálculo.')
            if process.returncode!=0 and not result.get('error'):raise ValueError('El motor de vista previa no terminó correctamente.')
            payload.update(result);payload['path']=path
            if result.get('error'):
                from ..diagnostics import process_error
                process_error(result.get('technical_error'))
        except InterruptedError as ex:
            payload.update(error=str(ex),cancelled=True)
            path.unlink(missing_ok=True)
        except Exception as ex:
            from ..diagnostics import error
            error('preview_error', ex)
            payload['error']=str(ex)
        finally:
            discard_temporary(job_path);discard_temporary(result_path)
        self.completed.emit(payload)
