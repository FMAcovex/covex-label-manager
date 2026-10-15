"""Separate-process bridge: Qt and Tk never share an event loop or Python UI state."""
import os
import sys
import subprocess
from pathlib import Path
from .paths import installation_dir

def legacy_command():
    if getattr(sys,'frozen',False):
        return [str(installation_dir()/'legacy'/'COVEXLabelManager_Legacy.exe')]
    return [sys.executable,str(installation_dir()/'legacy_qt_bridge.py')]

def launch_legacy(services,target='maestro',version_id=None,mode='production',smoke_report=None,smoke_issue=False):
    if target=='emitir' and version_id:
        ok,reason=services.eligibility(version_id,production=mode!='test',variant_id=getattr(services,'selected_variant_id',None))
        if not ok:raise ValueError(reason)
    env=os.environ.copy();env['COVEX_LABEL_DATA']=services.location()
    command=legacy_command()+['--target',target,'--mode',mode]
    if version_id is not None:command+=['--version-id',str(version_id)]
    variant_id=getattr(services,'selected_variant_id',None)
    if variant_id is not None:command+=['--variant-id',str(variant_id)]
    command+=['--writer-protocol','4']
    if smoke_report is not None:
        command+=['--smoke-report',str(smoke_report)];env['COVEX_QT_BRIDGE_SMOKE']='1'
        if smoke_issue:command+=['--smoke-issue']
    return subprocess.Popen(command,env=env)

def run_legacy(target,version_id=None,mode='production',smoke_report=None,variant_id=None,writer_protocol=4,smoke_issue=False):
    from .gui import Application
    from .qt_transition import TransitionServices
    import tkinter as tk
    from tkinter import messagebox
    class RetainedApplication(Application):
        """PR #2 idea: retain screens; no changes to the distributed legacy application."""
        def __init__(self,*args):
            self._qt_views={};super().__init__(*args)
        def issue_pdf(self):
            original_question=messagebox.askyesno
            def question(title,message,*args,**kwargs):
                if mode=='test' and title=='Solo PDF de prueba':
                    message='Generar PDF marcado PRUEBA - NO APTO PARA USO GMP. No se registra emisión definitiva. Continuar?'
                return original_question(title,message,*args,**kwargs)
            messagebox.askyesno=question
            try:super().issue_pdf()
            finally:messagebox.askyesno=original_question
        def select_emission_version(self,row):
            if row['version_id']!=self.current_version_id:
                old=self._qt_views.pop('emitir',None)
                if old:old.destroy()
                self.per_container=[];self.formvars={}
            super().select_emission_version(row)
        def show(self,page):
            # Data lists/settings refresh on reentry; active emission form is retained.
            for view in self._qt_views.values():view.pack_forget()
            if page!='emitir' and page in self._qt_views:
                self._qt_views.pop(page).destroy()
            if page not in self._qt_views:
                panel=tk.Frame(self.content.body,bg='#F2F5FA');self._qt_views[page]=panel
                builders={'inicio':self.page_home,'emitir':self.page_emit,'maestro':self.page_master,
                          'centro':self.page_print_center,'historial':self.page_history,'admin':self.page_admin}
                builders[page](panel)
            self._qt_views[page].pack(fill='both',expand=True);self.current_page=page
            self.top_title.configure(text='Versión anterior · '+page)
            for key,b in self.nav_buttons.items():b.configure(bg='#213B59' if key==page else '#162940')
    if writer_protocol!=4:raise ValueError('Acompañante incompatible con almacenamiento v4.')
    api=TransitionServices();api.selected_variant_id=variant_id;app=RetainedApplication(api)
    if version_id is not None:
        version=api.version(version_id)
        if version is None:app._quit();raise ValueError('Revisión inexistente.')
        if target=='emitir':
            ok,reason=api.eligibility(version_id,production=mode!='test',variant_id=variant_id)
            if not ok:messagebox.showerror('Bloqueado',reason,parent=app);app._quit();return
            app.current_version_id=version_id;app.current_label_id=version['label_id']
            if mode=='test':
                # Explicit TEST even for approved revisions: never create definitive issue records.
                app._test_mode=lambda _version:True
        if target=='editor':app.show('maestro');app.editor(version_id)
        else:
            app.show(target)
            if target=='maestro' and str(version_id) in app.library_panel.rows:
                app.library_panel.tree.selection_set(str(version_id));app.library_panel.tree.see(str(version_id))
    else:app.show('maestro' if target=='editor' else target)
    app.title('COVEX Label Manager · Versión anterior durante transición Qt')
    if smoke_report:
        if smoke_issue and api.setting('synthetic_demo')!='1':raise ValueError('Solo datos sintéticos para smoke de emisión definitiva.')
        if os.environ.get('COVEX_QT_BRIDGE_SMOKE')!='1':raise ValueError('Smoke requiere el modo aislado explícito.')
        def smoke():
            import json
            import fitz
            from tkinter import filedialog
            try:
                before=len(api.issues());app.emit_count.set('1');app.emit_copies.set(1)
                for key,var in app.formvars.items():
                    if key not in ('numero','texto_fijo'):var.set({'pn':'0,350','pb':'0,500'}.get(key,'DEMO'))
                entered=app._emit_values();app.show('historial');app.show('emitir')
                assert app._emit_values()==entered,'Emission work was rebuilt'
                output=api.output_path('cache','fictional-bridge-test.pdf')
                filedialog.asksaveasfilename=lambda **kw:str(output)
                messagebox.askyesno=lambda title,*a,**kw:title!='PDF generado'
                errors=[];messagebox.showerror=lambda *a,**kw:errors.append(a)
                app.issue_pdf()
                assert not errors,errors
                if smoke_issue:output=Path(app.last_issue_pdf)
                assert output.is_file(),'No PDF produced'
                with fitz.open(output) as doc:assert ('PRUEBA' in ''.join(p.get_text() for p in doc)) is (not smoke_issue)
                assert len(api.issues())==before+int(smoke_issue),'Unexpected definitive issue count'
                if smoke_issue:
                    issue=api.issues()[0];assert issue['design_snapshot_json'] and issue['design_variant_id']==variant_id
                Path(smoke_report).write_text(json.dumps({'ok':True,'selected_version':app.current_version_id,'selected_variant':variant_id,'writer_protocol':4,'work_retained':True,'test_pdf_watermarked':not smoke_issue,'no_definitive_issue':not smoke_issue,'snapshot_registered':smoke_issue}),encoding='utf-8')
            except Exception:
                import traceback
                Path(smoke_report).write_text(json.dumps({'ok':False,'error':traceback.format_exc()}),encoding='utf-8')
            finally:app._quit()
        app.after(350,smoke)
    app.mainloop()

