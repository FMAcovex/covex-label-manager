"""R3A library view, reusing the R2 service; no file/SQL access."""
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
from .contracts import FILTER_FIELDS,METADATA_FIELDS

TITLES={'category':'Categoría','family':'Familia','type':'Tipo','origin':'Origen','customer':'Cliente',
        'country':'País','language':'Idioma','version':'Versión','state':'Estado documental','acquisition':'Incorporación','product':'Producto'}
STATES={'APPROVED':'Vigente','PENDING':'Pendiente','RETIRED':'Retirada'}
import os
UI_FONT='Segoe UI' if os.name=='nt' else 'DejaVu Sans'
BG='#f3f4f6';INK='#243247';MUTED='#6b7788';BLUE='#2468db';LINE='#e3e7ed'

class LibraryPanel(tk.Frame):
    def __init__(self,parent,services,on_open,on_emit=None):
        super().__init__(parent,bg=BG)
        self.services=services;self.library=services.library;self.on_open=on_open;self.on_emit=on_emit
        self.rows={};self._after=None;self._preview_after=None;self._selected_id=None
        self.query=tk.StringVar();self.view=tk.StringVar(value='all');self.filters={k:tk.StringVar() for k in FILTER_FIELDS}
        toolbar=tk.Frame(self,bg=BG);toolbar.pack(fill='x',pady=(0,14))
        title=tk.Frame(toolbar,bg=BG);title.pack(side='left',padx=(2,24))
        tk.Label(title,text='Biblioteca de etiquetas',font=(UI_FONT,19,'bold'),bg=BG,fg=INK).pack(anchor='w')
        tk.Label(title,text='Diseños, revisiones y documentos locales',font=(UI_FONT,9),bg=BG,fg=MUTED).pack(anchor='w')
        searchbox=tk.Frame(toolbar,bg='white',highlightbackground=LINE,highlightthickness=1,padx=10,pady=4)
        searchbox.pack(side='left',fill='x',expand=True)
        tk.Label(searchbox,text='Buscar',bg='white',fg=MUTED,font=(UI_FONT,9)).pack(side='left',padx=(0,8))
        self.search=ttk.Entry(searchbox,textvariable=self.query,width=30,style='Covex.TEntry');self.search.pack(side='left',fill='x',expand=True)
        self.search.bind('<Return>',lambda _:self.refresh())
        tk.Label(searchbox,text='Ctrl+K',bg='white',fg=MUTED,font=(UI_FONT,8)).pack(side='right',padx=6)
        self.actions_button=ttk.Menubutton(toolbar,text='Acciones  ▾');self.actions_button.pack(side='right',padx=(12,0))
        self.action_menu=tk.Menu(self.actions_button,tearoff=False);self.actions_button.configure(menu=self.action_menu)
        controls=tk.Frame(self,bg=BG);controls.pack(fill='x',pady=(0,10))
        for label,value in [('Todas','all'),('★ Favoritas','favorites'),('Recientes','recent')]:
            ttk.Radiobutton(controls,text=label,value=value,variable=self.view,command=self.refresh).pack(side='left',padx=(0,16))
        self.count=tk.Label(controls,bg=BG,fg=MUTED,font=(UI_FONT,9));self.count.pack(side='right')
        ttk.Button(controls,text='Inspector',command=self.toggle_inspector).pack(side='right',padx=6)
        ttk.Button(controls,text='Filtros',command=self.toggle_filters).pack(side='right',padx=6)
        self.panes=tk.PanedWindow(self,orient='horizontal',bg=LINE,sashwidth=5,bd=0,showhandle=False,opaqueresize=True)
        self.panes.pack(fill='both',expand=True)
        self.filterbox=tk.Frame(self.panes,bg='white',width=218)
        self.panes.add(self.filterbox,minsize=175,width=218,stretch='never')
        tk.Label(self.filterbox,text='CATEGORÍAS Y FILTROS',font=(UI_FONT,9,'bold'),fg=MUTED,bg='white').pack(anchor='w',padx=14,pady=(16,10))
        # Scrollable filters remain usable at smaller window heights.
        fc=tk.Canvas(self.filterbox,bg='white',highlightthickness=0,width=210)
        fs=ttk.Scrollbar(self.filterbox,orient='vertical',command=fc.yview);fs.pack(side='right',fill='y')
        fc.configure(yscrollcommand=fs.set);fc.pack(fill='both',expand=True)
        self.filter_body=tk.Frame(fc,bg='white');fw=fc.create_window((0,0),window=self.filter_body,anchor='nw')
        self.filter_body.bind('<Configure>',lambda _:fc.configure(scrollregion=fc.bbox('all')))
        fc.bind('<Configure>',lambda e:fc.itemconfigure(fw,width=e.width))
        self.combos={}
        for key in FILTER_FIELDS:
            box=tk.Frame(self.filter_body,bg='white');box.pack(fill='x',padx=14,pady=5)
            tk.Label(box,text=TITLES[key],bg='white',fg=MUTED,font=(UI_FONT,9)).pack(anchor='w',pady=(0,3))
            combo=ttk.Combobox(box,textvariable=self.filters[key],state='readonly',width=18,style='Covex.TCombobox')
            combo.pack(fill='x');combo.bind('<<ComboboxSelected>>',lambda _:self.refresh());self.combos[key]=combo
        ttk.Button(self.filterbox,text='Limpiar búsqueda y filtros',command=self.reset).pack(fill='x',padx=14,pady=12)
        listing=tk.Frame(self.panes,bg='white');self.listing=listing
        self.panes.add(listing,minsize=330,stretch='always')
        columns=('favorite','code','name','type','version','origin','customer','country','state')
        self.tree=ttk.Treeview(listing,columns=columns,show='headings',selectmode='browse',height=15,style='Covex.Treeview')
        for key,label,width in [('favorite','★',34),('code','Código',75),('name','Denominación',190),('type','Tipo',90),('version','Versión',75),('origin','Origen',85),('customer','Cliente',110),('country','País',75),('state','Estado',100)]:
            self.tree.heading(key,text=label);self.tree.column(key,width=width,minwidth=width,stretch=key=='name')
        vs=ttk.Scrollbar(listing,orient='vertical',command=self.tree.yview);vs.pack(side='right',fill='y')
        hs=ttk.Scrollbar(listing,orient='horizontal',command=self.tree.xview);hs.pack(side='bottom',fill='x')
        self.tree.configure(yscrollcommand=vs.set,xscrollcommand=hs.set);self.tree.pack(fill='both',expand=True)
        self.tree.tag_configure('RETIRED',foreground='#6b7788')
        self.tree.bind('<<TreeviewSelect>>',self.preview);self.tree.bind('<Double-1>',lambda _:self.open());self.tree.bind('<Return>',lambda _:self.open())
        self.inspector=tk.Frame(self.panes,bg='white',width=290,padx=16,pady=16)
        self.panes.add(self.inspector,minsize=255,width=290,stretch='never')
        footer=tk.Frame(self.inspector,bg='white');footer.pack(side='bottom',fill='x')
        dc=tk.Canvas(self.inspector,bg='white',highlightthickness=0,width=260)
        ds=ttk.Scrollbar(self.inspector,orient='vertical',command=dc.yview);ds.pack(side='right',fill='y')
        dc.configure(yscrollcommand=ds.set);dc.pack(fill='both',expand=True)
        details=tk.Frame(dc,bg='white');dw=dc.create_window((0,0),window=details,anchor='nw')
        details.bind('<Configure>',lambda _:dc.configure(scrollregion=dc.bbox('all')))
        def resize_details(event):
            dc.itemconfigure(dw,width=event.width)
            for label in (self.document_title,self.info,self.revision_note):
                label.configure(wraplength=max(100,event.width-4))
        dc.bind('<Configure>',resize_details)
        tk.Label(details,text='VISTA DE ETIQUETA',bg='white',fg=MUTED,font=(UI_FONT,9,'bold')).pack(anchor='w')
        self.document_title=tk.Label(details,text='Seleccione una revisión',bg='white',fg=INK,font=(UI_FONT,13,'bold'),wraplength=260,justify='left');self.document_title.pack(anchor='w',pady=(12,6))
        self.state_badge=tk.Label(details,bg='#fff4dc',fg='#956514',font=(UI_FONT,9,'bold'),padx=8,pady=5);self.state_badge.pack(anchor='w')
        self.picture=tk.Label(details,bg=BG,text='Sin selección');self.picture.pack(fill='x',pady=12)
        self.info=tk.Label(details,bg='white',justify='left',anchor='w',wraplength=255,fg=MUTED,font=(UI_FONT,9));self.info.pack(fill='x')
        tk.Label(details,text='REVISIONES Y REFERENCIAS',bg='white',fg=MUTED,font=(UI_FONT,9,'bold')).pack(anchor='w',pady=(14,5))
        self.revisions=ttk.Combobox(details,state='readonly');self.revisions.pack(fill='x');self.revisions.bind('<<ComboboxSelected>>',self.select_revision)
        self.revision_note=tk.Label(details,bg='white',fg=MUTED,wraplength=255,justify='left',font=(UI_FONT,8));self.revision_note.pack(fill='x',pady=5)
        ttk.Button(footer,text='★ Cambiar favorita',command=self.favorite).pack(fill='x',pady=(6,4))
        self.open_button=ttk.Button(footer,text='Abrir etiqueta → Editor',command=self.open);self.open_button.pack(fill='x',pady=4)
        self.emit_button=ttk.Button(footer,text='Preparar emisión',command=self.emit)
        if on_emit:self.emit_button.pack(fill='x',pady=4)
        self.eligibility=tk.Label(footer,bg='white',fg='#956514',wraplength=255,justify='left',font=(UI_FONT,8));self.eligibility.pack(fill='x',pady=6)
        footer.bind('<Configure>',lambda e:self.eligibility.configure(wraplength=max(100,e.width-4)))
        self.query.trace_add('write',lambda *_:self.schedule());self.refresh_facets();self.refresh()
    def set_actions(self,actions):
        self.action_menu.delete(0,'end')
        for label,command in actions:self.action_menu.add_command(label=label,command=command)
    def destroy(self):
        for job in (self._after,self._preview_after):
            if job:
                try:self.after_cancel(job)
                except tk.TclError:pass
        super().destroy()
    def toggle_filters(self):
        if str(self.filterbox) in self.panes.panes():self.panes.forget(self.filterbox)
        else:self.panes.add(self.filterbox,before=self.listing,minsize=175,width=218,stretch='never')
    def toggle_inspector(self):
        if str(self.inspector) in self.panes.panes():self.panes.forget(self.inspector)
        else:self.panes.add(self.inspector,minsize=255,width=290,stretch='never')
    def refresh_facets(self):
        facets=self.library.facets()
        for key,combo in self.combos.items():combo.configure(values=['']+facets[key],state='readonly' if facets[key] else 'disabled')
    def schedule(self):
        if self._after:self.after_cancel(self._after)
        self._after=self.after(160,self.refresh)
    def reset(self):
        self.query.set('');self.view.set('all')
        for v in self.filters.values():v.set('')
        self.refresh()
    def selected(self):
        sel=self.tree.selection();return self.rows.get(sel[0]) if sel else None
    def refresh(self):
        if self._after:self.after_cancel(self._after)
        self._after=None
        selection=self.tree.selection();old=selection[0] if selection else self._selected_id
        self.rows={str(r['version_id']):r for r in self.library.entries(self.query.get(),{k:v.get() for k,v in self.filters.items()},self.view.get())}
        self.tree.delete(*self.tree.get_children())
        for iid,r in self.rows.items():
            self.tree.insert('','end',iid=iid,values=('★' if r['favorite'] else '',r['code'],r['name'],r.get('type',''),r['version'],r['origin'],r['customer'],r.get('country',''),STATES.get(r['state'],r['state'])),tags=(r['state'],))
        self.count.configure(text=f'{len(self.rows)} revisiones · documentos locales')
        if self.rows:
            self.tree.selection_set(old if old in self.rows else next(iter(self.rows)));self.preview()
        else:
            self._selected_id=None;self.picture.configure(image='',text='Sin resultados');self.document_title.configure(text='Sin selección');self.info.configure(text='Cambie la búsqueda o los filtros.')
            self.state_badge.configure(text='');self.revisions.configure(values=[]);self.revisions.set('');self.revision_note.configure(text='');self.eligibility.configure(text='')
            self.open_button.configure(state='disabled');self.emit_button.configure(state='disabled')
    def preview(self,event=None):
        r=self.selected()
        if not r:return
        self._selected_id=str(r['version_id']);self.document_title.configure(text=r['name']);self.open_button.configure(state='normal')
        colors={'APPROVED':('#e8f6ef','#177a56'),'PENDING':('#fff4dc','#956514'),'RETIRED':('#fbecee','#9b4250')}
        bg,fg=colors.get(r['state'],('#f3f4f6',MUTED));self.state_badge.configure(text=STATES.get(r['state'],r['state']),bg=bg,fg=fg)
        try:
            v=dict(self.services.version(r['version_id']))
            im=self.services.thumbnail(v,width_px=260);im.thumbnail((260,195))
            self.photo=ImageTk.PhotoImage(im);self.picture.configure(image=self.photo,text='')
            pairs=[('Código',r['code']),('Origen',r['origin']),('Incorporación',r['acquisition']),('Cliente',r['customer'])]+[(TITLES[k],r.get(k,'')) for k in ('category','family','type','country','language','product')]
            self.info.configure(text='\n'.join(f'{k}: {value}' for k,value in pairs if value)+f"\n{r['base_w_mm']:.1f} × {r['base_h_mm']:.1f} mm")
            self._revision_rows=self.services.versions(r['id'])
            self.revisions.configure(values=[f"{x['version']} · {STATES.get(x['state'],x['state'])}" for x in self._revision_rows])
            self.revisions.current(next(i for i,x in enumerate(self._revision_rows) if x['id']==r['version_id']))
            self.revision_note.configure(text='\n'.join(value for value in [v.get('approval_ref',''),v.get('approved_by',''),v.get('approved_at','')] if value) or 'Sin aprobación documental registrada.\nLas variantes actuales se identifican por su revisión; no existe aún una entidad separada.')
            allowed,reason=self.services.emission_eligibility(r['version_id'])
            self.emit_button.configure(state='normal' if allowed else 'disabled');self.eligibility.configure(text=reason,fg='#177a56' if allowed else '#956514')
        except Exception as ex:
            self.picture.configure(image='',text='Previsualización no disponible');self.info.configure(text=str(ex));self.emit_button.configure(state='disabled');self.eligibility.configure(text='Revise el documento fuente.')
    def select_revision(self,event=None):
        n=self.revisions.current()
        if n<0:return
        vid=str(self._revision_rows[n]['id'])
        # A revision hidden by current filters must not silently clear those filters.
        if vid in self.rows:self.tree.selection_set(vid);self.tree.see(vid);self.preview()
        else:
            selected=self.selected()
            if selected:self.revisions.current(next(i for i,r in enumerate(self._revision_rows) if r['id']==selected['version_id']))
            self.revision_note.configure(text='Esta revisión no está en el resultado filtrado. Ajuste los filtros para seleccionarla.')
    def favorite(self):
        r=self.selected()
        if r:self.library.favorite(r);self.refresh()
    def open(self):
        r=self.selected()
        if r:self.library.opened(r);self.on_open(r)
    def emit(self):
        r=self.selected()
        if r:
            allowed,reason=self.services.emission_eligibility(r['version_id'])
            if allowed:self.on_emit(r)
            else:self.emit_button.configure(state='disabled');self.eligibility.configure(text=reason)
