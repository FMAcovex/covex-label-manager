"""Real Tk app tests run on Windows; no native dialogs are left unanswered."""
import os
import copy
from contextlib import closing
import pytest
pytestmark=pytest.mark.skipif(os.name!='nt' and not os.environ.get('DISPLAY'),reason='Tk requires desktop')


def test_tk_autosave_restart_handoff_cas_and_close_guard(tmp_path,monkeypatch):
    from tkinter import messagebox
    from covex_label_manager.gui import Application
    from covex_label_manager.storage import Store
    from covex_label_manager.services import LocalServices
    from covex_label_manager.emission_work import WorkConflict
    errors=[];monkeypatch.setattr(messagebox,'showerror',lambda *a,**k:errors.append(a))
    monkeypatch.setattr(messagebox,'askyesno',lambda *a,**k:True)
    root=tmp_path/'data';api=LocalServices(Store(root));app=Application(api)
    vid=next(r['version_id'] for r in api.library_records() if r['name']=='ACETONA')
    api.approve(vid,'Synthetic','SYNTHETIC APPROVAL')
    app.current_version_id=vid;app.show('emitir');app.update()
    app.formvars['lote'].set('LOTE-TK');app.emit_count.set('2');app.per_container={'2':{'pn':'0,35','pb':'0,50','lote':'TK-2'}};app._work_changed()
    app.emit_w.set('100');app.emit_h.set('150');app.emit_offx.set('0,5');assert app._work_flush()
    app.work_selection.set('2');assert app._emit_indices(2)==[2] and app._work_flush()
    app.preview_issue()
    import fitz
    with fitz.open(api.output_path('cache','preview_a4.pdf')) as preview:assert '2/2' in ''.join(p.get_text() for p in preview)
    w=copy.deepcopy(app.emission_work);assert w['values']['lote']=='LOTE-TK' and w['profile']['offset_x_mm']=='0,5'
    app.show('historial');app.show('emitir');app.update();assert app.formvars['lote'].get()=='LOTE-TK'
    app._quit()
    api=LocalServices(Store(root));app=Application(api);app.attach_work(w['uid'],w['generation']);app.update()
    assert app.per_container==w['per_container'] and app.formvars['lote'].get()=='LOTE-TK'
    newer=api.work.save(w['uid'],w['generation'],{'values':dict(w['values'],lote='Qt externo')})
    app.formvars['lote'].set('Tk sin guardar');assert not app._work_flush()
    app._quit();assert app.winfo_exists() and errors
    assert app.formvars['lote'].get()=='Tk sin guardar'
    app._work_dirty=False;app.attach_work(w['uid'],newer['generation']);app.update()
    assert app.formvars['lote'].get()=='Qt externo'
    app._quit()
