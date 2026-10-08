"""R2 library panel. All queries and changes go through application services."""
import tkinter as tk
from tkinter import ttk,messagebox
from PIL import ImageTk
from .contracts import FILTER_FIELDS,METADATA_FIELDS

TITLES={'category':'Categoría','family':'Familia','type':'Tipo','origin':'Origen','customer':'Cliente',
        'country':'País','language':'Idioma','version':'Versión','state':'Estado documental','acquisition':'Incorporación',
        'product':'Producto'}
STATES={'APPROVED':'Vigente','PENDING':'Pendiente','RETIRED':'Retirada'}

class LibraryPanel(tk.Frame):
    def __init__(self,parent,services,on_open,on_emit=None):
        super().__init__(parent,bg='#f4f5f7');self.services=services;self.library=services.library
        self.on_open=on_open;self.on_emit=on_emit;self.rows={};self._after=None
        self.query=tk.StringVar();self.view=tk.StringVar(value='all');self.filters={k:tk.StringVar() for k in FILTER_FIELDS}
        toolbar=tk.Frame(self,bg='#252d39',padx=16,pady=12);toolbar.pack(fill='x')
        tk.Label(toolbar,text='LABEL LIBRARY',font=('Arial',12,'bold'),fg='white',bg='#252d39').pack(side='left',padx=(0,20))
        self.search=ttk.Entry(toolbar,textvariable=self.query,width=44);self.search.pack(side='left',fill='x',expand=True)
        self.search.bind('<Return>',lambda _:self.refresh())
        ttk.Button(toolbar,text='Filtros',command=self.toggle_filters).pack(side='left',padx=8)
        ttk.Button(toolbar,text='Limpiar',command=self.reset).pack(side='left')
        modes=tk.Frame(self,bg='#f4f5f7');modes.pack(fill='x',padx=14,pady=9)
        for label,value in [('Todas las revisiones','all'),('★ Favoritos','favorites'),('Recientes','recent')]:
            ttk.Radiobutton(modes,text=label,value=value,variable=self.view,command=self.refresh).pack(side='left',padx=(0,14))
        self.count=tk.Label(modes,bg='#f4f5f7',fg='#616d7d');self.count.pack(side='right')
        self.filterbox=tk.Frame(self,bg='white',padx=14,pady=10)
        facets=self.library.facets()
        for i,key in enumerate(FILTER_FIELDS):
            box=tk.Frame(self.filterbox,bg='white');box.grid(row=i//5,column=i%5,sticky='ew',padx=5,pady=3)
            tk.Label(box,text=TITLES[key],bg='white',fg='#536174',font=('Arial',9)).pack(anchor='w')
            values=['']+facets[key]
            combo=ttk.Combobox(box,textvariable=self.filters[key],values=values,state='readonly',width=17)
            combo.pack(fill='x');combo.bind('<<ComboboxSelected>>',lambda _:self.refresh())
            if len(values)==1:
                combo.configure(state='disabled')
                tk.Label(box,text='Sin datos fuente',bg='white',fg='#9a6570',font=('Arial',8)).pack(anchor='w')
        for i in range(5):self.filterbox.grid_columnconfigure(i,weight=1)
        body=tk.Frame(self,bg='#f4f5f7',height=440);body.pack_propagate(False);body.pack(fill='both',expand=True,padx=14,pady=(0,8))
        listing=tk.Frame(body,bg='white');listing.pack(side='left',fill='both',expand=True)
        cols=('favorite','code','name','version','state','origin')
        self.tree=ttk.Treeview(listing,columns=cols,show='headings',selectmode='browse',height=12)
        for key,title,width in [('favorite','★',35),('code','Código',70),('name','Etiqueta',210),('version','Versión',75),('state','Estado',90),('origin','Origen',85)]:
            self.tree.heading(key,text=title);self.tree.column(key,width=width,stretch=key=='name')
        scroll=ttk.Scrollbar(listing,orient='vertical',command=self.tree.yview);scroll.pack(side='right',fill='y')
        self.tree.configure(yscrollcommand=scroll.set);self.tree.pack(fill='both',expand=True)
        self.tree.bind('<<TreeviewSelect>>',self.preview);self.tree.bind('<Double-1>',lambda _:self.open())
        self.tree.bind('<Return>',lambda _:self.open())
        inspector=tk.Frame(body,bg='white',width=285,padx=12,pady=12);inspector.pack(side='right',fill='y',padx=(12,0));inspector.pack_propagate(False)
        tk.Label(inspector,text='VISTA DE PLANTILLA',bg='white',fg='#697589',font=('Arial',10,'bold')).pack(anchor='w')
        self.picture=tk.Label(inspector,bg='#edf0f3',height=1);self.picture.pack(fill='x',pady=10)
        self.info=tk.Label(inspector,bg='white',justify='left',anchor='w',wraplength=255,fg='#344154',font=('Arial',10));self.info.pack(fill='x')
        ttk.Button(inspector,text='★ Cambiar favorito',command=self.favorite).pack(fill='x',pady=(10,4))
        ttk.Button(inspector,text='Abrir ficha',command=self.open).pack(fill='x',pady=4)
        if on_emit:ttk.Button(inspector,text='Usar para emisión',command=self.emit).pack(fill='x',pady=4)
        self.query.trace_add('write',lambda *_:self.schedule())
        self.refresh()
    def destroy(self):
        if self._after:
            try:self.after_cancel(self._after)
            except tk.TclError:pass
        super().destroy()
    def toggle_filters(self):
        if self.filterbox.winfo_manager():self.filterbox.pack_forget()
        else:self.filterbox.pack(fill='x',before=self.winfo_children()[-1],padx=14,pady=(0,10))
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
        self._after=None
        selected=self.tree.selection();old=selected[0] if selected else None
        self.rows={str(r['version_id']):r for r in self.library.entries(self.query.get(),{k:v.get() for k,v in self.filters.items()},self.view.get())}
        self.tree.delete(*self.tree.get_children())
        for iid,r in self.rows.items():
            self.tree.insert('', 'end',iid=iid,values=('★' if r['favorite'] else '',r['code'],r['name'],r['version'],STATES.get(r['state'],r['state']),r['origin']))
        self.count.configure(text=f'{len(self.rows)} revisiones')
        if self.rows:self.tree.selection_set(old if old in self.rows else next(iter(self.rows)))
        else:self.picture.configure(image='',text='Sin resultados');self.info.configure(text='Cambie la búsqueda o los filtros.')
    def preview(self,event=None):
        r=self.selected()
        if not r:return
        try:
            im=self.services.thumbnail(self.services.version(r['version_id']),width_px=250);im.thumbnail((250,180))
            self.photo=ImageTk.PhotoImage(im);self.picture.configure(image=self.photo,text='',height=0)
            pairs=[('Código',r['code']),('Versión',r['version']),('Estado',STATES.get(r['state'],r['state'])),('Origen',r['origin']),('Incorporación',r['acquisition']),('Cliente',r['customer'])]
            pairs+=[(TITLES[k],r.get(k,'')) for k in ('category','family','type','country','language','product')]
            self.info.configure(text='\n'.join(f'{k}: {v}' for k,v in pairs if v)+f"\n{r['base_w_mm']} × {r['base_h_mm']} mm")
        except Exception as ex:self.picture.configure(image='',text='No se puede previsualizar');self.info.configure(text=str(ex))
    def favorite(self):
        r=self.selected()
        if r:self.library.favorite(r);self.refresh()
    def open(self):
        r=self.selected()
        if r:self.library.opened(r);self.on_open(r)
    def emit(self):
        r=self.selected()
        if r:self.library.opened(r);self.on_emit(r)
