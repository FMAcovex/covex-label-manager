"""Tk transition uses the exact same durable work and CAS contract as Qt."""
import copy
import json
import tkinter as tk
from tkinter import ttk,messagebox,simpledialog
from .emission_work import WorkConflict


class WorkTkMixin:
    def _work_init(self):
        self.emission_work=None;self._work_loading=False;self._work_after=None;self._work_dirty=False
        self._work_traces=[];self._work_error=''
    def _work_vars(self):
        return {'width_mm':self.emit_w,'height_mm':self.emit_h,'orientation':self.emit_orient,
            'margin_mm':self.emit_margin,'gap_mm':self.emit_gap,'offset_x_mm':self.emit_offx,
            'offset_y_mm':self.emit_offy,'start_slot':self.emit_start,'crop_marks':self.emit_cut,
            'safety_mm':self.emit_safety,'printer_name':self.emit_printer}
    def _work_capture(self):
        # StringVar/IntVar may contain incomplete text. Save it, validate only on issue.
        return {'values':{**(self.emission_work['values'] if self.emission_work else {}),**{k:str(v.get()) for k,v in self.formvars.items()}},
            'profile':{k:str(int(v.get()) if k=='crop_marks' else v.get()) for k,v in self._work_vars().items()},
            'count':str(self.emit_count.get()),'copies':str(self.emit_copies.get()),
            'selection':self.work_selection.get() if hasattr(self,'work_selection') else '',
            'per_container':copy.deepcopy(self.per_container),'status':self._state_object()}
    def _work_changed(self,*_):
        if self._work_loading:return
        if self.emission_work is None:
            if not self.current_version_id:return
            try:self.emission_work=self.services.work.create(self.current_version_id,getattr(self.services,'selected_variant_id',None),'Trabajo '+__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            except Exception as ex:self._work_error=str(ex);self._work_note('NO GUARDADO · '+str(ex));self._work_dirty=True;return
        self._work_dirty=True
        self._emit_stats()
        if self._work_after:self.after_cancel(self._work_after)
        self._work_after=self.after(400,self._work_autosave)
        self._work_note('Cambios por guardar…')
    def _work_note(self,text):
        if hasattr(self,'work_note') and self.work_note.winfo_exists():self.work_note.configure(text=text)
    def _work_autosave(self):
        self._work_after=None;self._work_flush()
    def _work_flush(self):
        if self._work_loading or not self._work_dirty:return True
        if self.emission_work is None:return False
        if self._work_after:self.after_cancel(self._work_after);self._work_after=None
        try:
            w=self.emission_work
            self.emission_work=self.services.work.save(w['uid'],w['generation'],self._work_capture())
            self._work_dirty=False;self._work_error='';self._work_note('Borrador guardado localmente · '+self.emission_work['name']);return True
        except Exception as ex:
            self._work_error=str(ex);self._work_note('NO GUARDADO · '+str(ex));return False
    def _work_guard(self):
        if self._work_flush():return True
        messagebox.showerror('Borrador no guardado',self._work_error+'\nLos valores siguen en pantalla. Reintente guardar antes de salir.',parent=self);return False
    def _work_apply(self,w):
        from .sheet_layout import require_legacy
        require_legacy(w['profile'])
        previous_loading=self._work_loading;self._work_loading=True
        try:
            self.emission_work=w
            for key,var in self.formvars.items():var.set(w['values'].get(key,''))
            self.per_container=copy.deepcopy(w['per_container'])
            self.emit_count.set(w['count']);self.emit_copies.set(w['copies']);self.work_selection.set(w['selection'])
            for key,var in self._work_vars().items():
                if key in w['profile']:var.set(w['profile'][key])
            state=w['status'];k=state.get('kind','ninguna')
            self.status_kind.set(k)
            if hasattr(self,'status_selector') and self.status_selector.winfo_exists():
                self.status_selector.current(next((i for i,r in enumerate(self._state_options) if r[0]==k),0));self._state_change()
            self.status_placement.set(state.get('placement','integrada'));self.status_fecha.set(state.get('fecha',''))
            self.status_persona.set(state.get('persona',''));self.status_expiry.set(state.get('caducidad_reanalisis',''))
            self._work_dirty=False;self._work_error=''
            self._work_note(w['name']+' · '+w['phase']+' · generación '+str(w['generation']))
            if hasattr(self,'work_choice') and self.work_choice.winfo_exists():
                self._work_rows=self.services.work.list()
                self.work_choice['values']=[r['name']+' · '+r['phase'] for r in self._work_rows]
                index=next((i for i,r in enumerate(self._work_rows) if r['uid']==w['uid']),-1)
                if index>=0:self.work_choice.current(index)
            self._emit_stats()
        finally:self._work_loading=previous_loading
    def _work_attach_traces(self):
        for variable,token in self._work_traces:
            try:variable.trace_remove('write',token)
            except tk.TclError:pass
        variables=list(self.formvars.values())+list(self._work_vars().values())+[self.emit_count,self.emit_copies,
            self.work_selection,self.status_kind,self.status_placement,self.status_fecha,self.status_persona,self.status_expiry]
        self._work_traces=[(v,v.trace_add('write',self._work_changed)) for v in variables]
    def page_emit(self,parent):
        self._work_loading=True
        try:super().page_emit(parent)
        finally:self._work_loading=False
        from .gui import button,text,C
        panel=tk.Frame(parent,bg=C['white'],padx=14,pady=12);panel.pack(fill='x',padx=30,pady=(0,15),before=parent.winfo_children()[1])
        self.work_note=text(panel,'Trabajo local · Guardar borrador no emite',10,True,bg='white');self.work_note.pack(anchor='w')
        line=tk.Frame(panel,bg='white');line.pack(fill='x')
        self.work_choice=ttk.Combobox(line,state='readonly',width=34);self.work_choice.pack(side='left',padx=(0,8))
        rows=self.services.work.list();self._work_rows=rows
        self.work_choice['values']=[r['name']+' · '+r['phase'] for r in rows]
        button(line,'Abrir trabajo',self._work_open_choice,'soft').pack(side='left',padx=3)
        button(line,'Nuevo borrador',self._work_new,'soft').pack(side='left',padx=3)
        button(line,'Guardar borrador',self._work_guard,'soft').pack(side='left',padx=3)
        button(line,'Recargar',self._work_reload,'soft').pack(side='left',padx=3)
        extra=tk.Frame(panel,bg='white');extra.pack(fill='x',pady=(5,0))
        button(extra,'Copiar trabajo',self._work_copy,'soft').pack(side='left',padx=3)
        button(extra,'Recuperar intento / archivo',self._work_recover,'soft').pack(side='left',padx=3)
        button(extra,'Actualizar vínculo documental',self._work_refresh_doc,'soft').pack(side='left',padx=3)
        if not hasattr(self,'work_selection'):self.work_selection=tk.StringVar(value='')
        selection=tk.Frame(panel,bg='white');selection.pack(fill='x',pady=(6,0))
        text(selection,'Recipientes (vacío = todos; separados por comas)',9,bg='white').pack(side='left')
        ttk.Entry(selection,textvariable=self.work_selection,width=24).pack(side='left',padx=8)
        if self.emission_work:self._work_apply(self.emission_work)
        self._work_attach_traces()
    def _work_open_choice(self):
        if not self._work_guard():return
        index=self.work_choice.current()
        if index<0:return
        row=self._work_rows[index]
        try:self.attach_work(row['uid'])
        except Exception as ex:messagebox.showerror('Trabajo no abierto',str(ex),parent=self)
    def attach_work(self,uid,generation=None):
        if not self._work_guard():raise WorkConflict('Hay datos locales sin guardar.')
        w=self.services.work.get(uid)
        if generation is not None and w['generation']!=generation:raise WorkConflict('Handoff obsoleto: vuelva a abrir desde Qt.')
        b=w['binding'];self.current_version_id=b['revision_id'];self.services.selected_variant_id=b['variant_id']
        self.current_label_id=self.services.version(b['revision_id'])['label_id'];self.emission_work=w
        self._work_dirty=False;self.show('emitir')
        self._work_apply(w)
    def _work_new(self):
        if not self._work_guard() or not self.current_version_id:return
        name=simpledialog.askstring('Nuevo trabajo','Denominación del lote o trabajo:',parent=self)
        if not name:return
        try:
            self.emission_work=self.services.work.create(self.current_version_id,getattr(self.services,'selected_variant_id',None),name)
            self._work_apply(self.emission_work)
        except Exception as ex:messagebox.showerror('Trabajo no creado',str(ex),parent=self)
    def _work_copy(self):
        if not self.emission_work or not self._work_guard():return
        try:
            w=self.emission_work;b=w['binding']
            self.emission_work=self.services.work.create(b['revision_id'],b['variant_id'],w['name']+' · copia',w)
            self._work_apply(self.emission_work)
        except Exception as ex:messagebox.showerror('No copiado',str(ex),parent=self)
    def _work_recover(self):
        if not self._work_guard():return
        w=self.emission_work
        index=self.work_choice.current() if hasattr(self,'work_choice') else -1
        uid=w['uid'] if w else (self._work_rows[index]['uid'] if index>=0 else None)
        if not uid:return
        if not messagebox.askyesno('Recuperar trabajo','Reconciliar el intento o recuperar la copia anterior? Se conservarán archivos de diagnóstico.',parent=self,default='no'):return
        try:
            from .emission_work import WorkCorrupt
            try:
                w=self.services.work.get(uid)
                w=self.services.work.recover_attempt(uid,w['generation']) if w['phase']=='EMITTING' else w
            except WorkCorrupt:w=self.services.work.recover_previous(uid)
            self.emission_work=w;self.attach_work(uid)
        except Exception as ex:messagebox.showerror('No recuperado',str(ex),parent=self)
    def _work_refresh_doc(self):
        if not self.emission_work or not self._work_guard():return
        if not messagebox.askyesno('Actualizar vínculo','Conservar datos y actualizar el vínculo documental? Revise campos y formato antes de emitir.',parent=self,default='no'):return
        try:
            w=self.emission_work;self.emission_work=self.services.work.refresh_binding(w['uid'],w['generation'])
            self.attach_work(w['uid'])
        except Exception as ex:messagebox.showerror('Vínculo no actualizado',str(ex),parent=self)
    def _work_reload(self):
        if self.emission_work is None:return
        if self._work_dirty and not messagebox.askyesno('Recargar','Descartar expresamente los valores de pantalla y cargar la versión guardada?',parent=self):return
        try:
            self._work_dirty=False;self.attach_work(self.emission_work['uid'])
        except Exception as ex:messagebox.showerror('No recargado',str(ex),parent=self)
    def _emit_label_change(self,event=None):
        old=self._work_loading;self._work_loading=True
        try:super()._emit_label_change(event)
        finally:self._work_loading=old
        if self.emission_work and self.emission_work['binding']['revision_id']==self.current_version_id:
            if hasattr(self,'work_selection'):self._work_apply(self.emission_work)
    def select_emission_version(self,row):
        if not self._work_guard():return
        self.emission_work=None;self._work_dirty=False
        super().select_emission_version(row)
    def show(self,page):
        if hasattr(self,'services') and not self._work_guard():return
        super().show(page)
    def _edit_vessels(self):
        super()._edit_vessels();self._work_changed()
    def _quit(self):
        if not self._work_guard():return
        if self._work_after:self.after_cancel(self._work_after)
        super()._quit()
