"""One non-productive render with a thread-local SQLite/service lifetime."""
from PySide6.QtCore import QThread, Signal


class PreviewTask(QThread):
    completed=Signal(object)

    def __init__(self,parent,root,uid,generation,token,path,serial):
        super().__init__(parent)
        self.request=(root,uid,generation,token,path,serial)

    def run(self):
        from ..storage import Store,sha256
        from ..services import LocalServices
        from ..emission_work import parameters,WorkConflict
        root,uid,generation,token,path,serial=self.request
        payload=dict(uid=uid,generation=generation,stamp=token,path=path,serial=serial)
        api=None
        try:
            # Never use the GUI's SQLite connection from a QThread.
            api=LocalServices(Store(root,seed=False))
            def read_locked(call):
                for attempt in range(5):
                    try:return call()
                    except WorkConflict:
                        if attempt==4:raise
                        self.msleep(50)
            before=read_locked(lambda:api.review_work(uid,generation))
            if not before['proof_allowed'] or before.get('token')!=token:
                raise ValueError('El trabajo o los documentos cambiaron. Revise los datos.')
            # Render an immutable input snapshot, NOT work.proof's long-held
            # exclusive work/catalog lock. Autosave must stay usable while
            # rendering. The token/generation is revalidated before adoption;
            # this path can only produce a visibly watermarked TEST PDF.
            work=read_locked(lambda:api.work.get(uid))
            if work['generation']!=generation:raise WorkConflict('Trabajo obsoleto.')
            api.work.assert_current(work)
            profile,indices,count,copies=parameters(work);binding=work['binding']
            payload['result']=api.render(api.resolved_design(binding['revision_id'],binding['variant_id']),
                work['values'],profile,indices,count,copies,path,True,
                per_container=work['per_container'],status=work['status'])
            if read_locked(lambda:api.review_work(uid,generation)).get('token')!=token:
                raise ValueError('El trabajo o los documentos cambiaron durante el cálculo.')
            payload['sha256']=sha256(path)
        except Exception as ex:payload['error']=str(ex)
        finally:
            if api is not None:api.close()
        self.completed.emit(payload)
