from __future__ import annotations
import json
import os
import shutil
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageTk, ImageChops, ImageEnhance

from .storage import Store, now
from .services import LocalServices
from .library_ui import LibraryPanel
from .contracts import METADATA_FIELDS
from .engine import LayoutError
from .importer import proposed_identity
from .geometry import STATUS_NAMES, acetona_template, edrofonio_template, rebase_layout
from .vessels import parse_tabular_vessels, validate_vessel_masses

UI_FONT='Segoe UI' if os.name=='nt' else 'DejaVu Sans'

C={
 'nav':'#162940','nav_alt':'#213B59','blue':'#2365A8','blue_dark':'#1A4F85',
 'bg':'#F2F5FA','white':'#FFFFFF','ink':'#1B2D45','muted':'#64748B',
 'line':'#DCE5EF','green':'#1C875E','red':'#B93D48','orange':'#A56D14',
 'cyan':'#E9F2FC','soft':'#F8FAFD',
}


def text(parent, value, size=11, bold=False, color=None, bg=None, **kwargs):
    f=(UI_FONT,size,'bold' if bold else 'normal')
    return tk.Label(parent,text=value,fg=color or C['ink'],bg=bg or parent.cget('bg'),font=f,
                    justify='left',anchor='w',**kwargs)


def button(parent,label,cmd,kind='primary',**kwargs):
    styles={'primary':(C['blue'],'white'),'ghost':(C['white'],C['blue']),
            'soft':(C['cyan'],C['blue_dark']),'danger':('#FDE9EA',C['red']),
            'dark':(C['nav_alt'],'white')}
    bg,fg=styles.get(kind,styles['primary'])
    return tk.Button(parent,text=label,command=cmd,fg=fg,bg=bg,
        activebackground=(C['blue_dark'] if kind=='primary' else '#E3EDF9'),
        activeforeground=('white' if kind=='primary' else C['blue_dark']),
        font=(UI_FONT,10,'bold'),relief='flat',bd=0,cursor='hand2',
        padx=13,pady=9,highlightthickness=0,**kwargs)


def entry(parent,var=None,width=23):
    return ttk.Entry(parent,textvariable=var,width=width,style='Covex.TEntry')


def card(parent,pad=18):
    box=tk.Frame(parent,bg=C['white'],highlightbackground=C['line'],highlightthickness=1)
    body=tk.Frame(box,bg=C['white'],padx=pad,pady=pad)
    body.pack(fill='both',expand=True)
    return box,body


def slug(v):
    return ''.join(c if c.isalnum() or c in ('-','_') else '_' for c in str(v))[:45]


def open_path(path):
    if os.name=='nt':
        os.startfile(str(path))
    elif shutil.which('xdg-open'):
        import subprocess
        subprocess.Popen(['xdg-open',str(path)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    else:
        raise OSError('No hay visor de PDF disponible')


def parse_ranges(s,count):
    values=[]
    for part in s.replace(' ','').split(','):
        if not part:continue
        if '-' in part:
            bits=part.split('-')
            if len(bits)!=2:raise ValueError('Rango invalido')
            start,end=map(int,bits)
            if end<start or end-start>10000: raise ValueError('Rango invalido')
            values.extend(range(start,end+1))
        else:
            values.append(int(part))
    values=list(dict.fromkeys(values))
    if not values or any(i<1 or i>count for i in values):
        raise ValueError('Introduzca numeros validos dentro de la emisión original')
    return values


class ScrolledFrame(tk.Frame):
    def __init__(self,parent,**kw):
        super().__init__(parent,bg=C['bg'],**kw)
        self.canvas=tk.Canvas(self,bg=C['bg'],highlightthickness=0,bd=0)
        bar=ttk.Scrollbar(self,orient='vertical',command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=bar.set)
        self.canvas.pack(side='left',fill='both',expand=True)
        bar.pack(side='right',fill='y')
        self.body=tk.Frame(self.canvas,bg=C['bg'])
        win=self.canvas.create_window((0,0),window=self.body,anchor='nw')
        self.body.bind('<Configure>',lambda _: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>',lambda e:self.canvas.itemconfigure(win,width=e.width))
        self.canvas.bind('<Enter>',lambda _:self.canvas.bind_all('<MouseWheel>',self._wheel))
        self.canvas.bind('<Leave>',lambda _:self.canvas.unbind_all('<MouseWheel>'))
    def _wheel(self,e):
        self.canvas.yview_scroll(-int(e.delta/120),'units')


from .work_tk import WorkTkMixin

class BaseApplication(tk.Tk):
    def __init__(self,store=None):
        self._work_init()
        super().__init__()
        from .migration_consent import tk_confirmation
        try:
            self.store=store if isinstance(store,LocalServices) else LocalServices(store,
                migration_confirmation=lambda root:tk_confirmation(root,self))
        except Exception:
            self.destroy()
            raise
        self.services=self.store
        self.current_version_id=None
        self.bind_all('<Control-k>',lambda _:self._open_library_picker())
        self.bind_all('<Control-K>',lambda _:self._open_library_picker())
        self.title('COVEX Label Manager  |  Desktop 0.3.1 R1-R2')
        self.geometry('1390x850')
        self.minsize(1100,700)
        self.configure(bg=C['bg'])
        try:self.tk.call('tk','scaling',1.12)
        except tk.TclError:pass
        self._style()
        self.current_page='inicio'
        self.current_label_id=None
        self._preview_image=None
        self._preview_after=None
        self.formvars={}
        self.emit_count=tk.StringVar(value='10')
        self.emit_copies=tk.StringVar(value='1')
        self.emit_w=tk.StringVar(value='160')
        self.emit_h=tk.StringVar(value='235')
        self.emit_margin=tk.StringVar(value='8')
        self.emit_gap=tk.StringVar(value='3')
        self.emit_offx=tk.StringVar(value='0')
        self.emit_offy=tk.StringVar(value='0')
        self.emit_start=tk.StringVar(value='1')
        self.emit_safety=tk.StringVar(value='0')
        self.emit_orient=tk.StringVar(value='portrait')
        self.emit_cut=tk.BooleanVar(value=False)
        self.emit_printer=tk.StringVar(value='')
        self.emit_profile=tk.StringVar(value='')
        self.last_issue_pdf=None
        self.per_container={}
        self.status_kind=tk.StringVar(value='ninguna')
        self.status_placement=tk.StringVar(value='integrada')
        self.status_fecha=tk.StringVar(value='')
        self.status_persona=tk.StringVar(value='')
        self.status_expiry=tk.StringVar(value='')
        self._chrome()
        self.show('inicio')
        self.protocol('WM_DELETE_WINDOW',self._quit)

    def _style(self):
        style=ttk.Style(self)
        if 'clam' in style.theme_names():style.theme_use('clam')
        style.configure('.',font=(UI_FONT,10))
        style.configure('Covex.TEntry',padding=8,fieldbackground='#FFFFFF',foreground=C['ink'],bordercolor=C['line'],lightcolor=C['line'],darkcolor=C['line'])
        style.configure('Covex.TCombobox',padding=7,fieldbackground='#FFFFFF',foreground=C['ink'],bordercolor=C['line'])
        style.configure('Covex.Treeview',font=(UI_FONT,10),rowheight=36,background='#FFFFFF',foreground=C['ink'],fieldbackground='#FFFFFF',borderwidth=0)
        style.configure('Covex.Treeview.Heading',font=(UI_FONT,10,'bold'),background='#EEF3F8',foreground=C['ink'],relief='flat',padding=9)
        style.map('Covex.Treeview',background=[('selected','#DDECFB')],foreground=[('selected',C['ink'])])
        style.configure('Covex.TNotebook',background=C['bg'],borderwidth=0)
        style.configure('Covex.TNotebook.Tab',padding=(12,9),font=(UI_FONT,10))
        style.configure('Covex.Horizontal.TProgressbar',troughcolor='#E3E9F1',background=C['blue'])

    def _chrome(self):
        self.sidebar=tk.Frame(self,width=232,bg=C['nav']);self.sidebar.pack(side='left',fill='y');self.sidebar.pack_propagate(False)
        brand=tk.Frame(self.sidebar,bg=C['nav'],pady=25,padx=19);brand.pack(fill='x')
        logo=tk.Canvas(brand,width=41,height=41,bg=C['nav'],highlightthickness=0)
        logo.pack(side='left')
        logo.create_oval(3,3,38,38,fill=C['blue'],outline='')
        logo.create_text(20,20,text='C',font=(UI_FONT,22,'bold'),fill='white')
        title=tk.Frame(brand,bg=C['nav']);title.pack(side='left',padx=10)
        text(title,'COVEX',16,True,'white',C['nav']).pack(anchor='w')
        text(title,'LABEL MANAGER',8,True,'#A8C5E3',C['nav']).pack(anchor='w')
        tk.Frame(self.sidebar,height=1,bg='#35506F').pack(fill='x',padx=18,pady=(0,18))
        self.nav_buttons={}
        nav=[('inicio','Inicio'),('emitir','Emitir etiquetas'),('maestro','Maestro de etiquetas'),
             ('centro','Centro de impresión'),('historial','Historial de emisiones'),('admin','Administración')]
        for page,label in nav:
            b=tk.Button(self.sidebar,text='  '+label,anchor='w',command=lambda x=page:self.show(x),
               relief='flat',bd=0,font=(UI_FONT,10,'bold'),fg='#C8D7E8',bg=C['nav'],
               activebackground=C['nav_alt'],activeforeground='white',cursor='hand2',padx=17,pady=14,highlightthickness=0)
            b.pack(fill='x',padx=10,pady=2);self.nav_buttons[page]=b
        tk.Frame(self.sidebar,bg=C['nav']).pack(fill='both',expand=True)
        text(self.sidebar,'DESKTOP  |  v0.3.1 · R1/R2',9,True,'#7593B2',C['nav']).pack(anchor='w',padx=24,pady=(0,6))
        text(self.sidebar,'Datos guardados localmente',9,False,'#7D9CB9',C['nav']).pack(anchor='w',padx=24,pady=(0,26))
        self.main=tk.Frame(self,bg=C['bg']);self.main.pack(side='left',fill='both',expand=True)
        self.top=tk.Frame(self.main,height=77,bg=C['white'],highlightbackground=C['line'],highlightthickness=1)
        self.top.pack(fill='x');self.top.pack_propagate(False)
        self.top_title=tk.Label(self.top,bg='white',fg=C['ink'],font=(UI_FONT,17,'bold'))
        self.top_title.pack(side='left',padx=32,pady=18)
        operator=tk.Frame(self.top,bg='white');operator.pack(side='right',padx=28)
        text(operator,'ENTORNO LOCAL',8,True,C['green'],'white').pack(anchor='e')
        self.top_user=text(operator,self.store.setting('operator'),10,True,C['ink'],'white');self.top_user.pack(anchor='e')
        self.content=ScrolledFrame(self.main)
        self.content.pack(fill='both',expand=True)

    def show(self,page):
        self.current_page=page
        self.top_title.configure(text={
           'inicio':'Panel de inicio','emitir':'Emitir etiquetas','maestro':'Maestro de etiquetas',
           'centro':'Centro de impresión','historial':'Historial de emisiones','admin':'Administración'}[page])
        for name,b in self.nav_buttons.items():
            b.configure(bg=C['nav_alt'] if page==name else C['nav'],fg='white' if page==name else '#C8D7E8')
        for w in self.content.body.winfo_children():w.destroy()
        panel=self.content.body
        if page=='inicio':self.page_home(panel)
        if page=='emitir':self.page_emit(panel)
        if page=='maestro':self.page_master(panel)
        if page=='centro':self.page_print_center(panel)
        if page=='historial':self.page_history(panel)
        if page=='admin':self.page_admin(panel)

    def header(self,parent,title,subtitle,action_label=None,action=None):
        h=tk.Frame(parent,bg=C['bg']);h.pack(fill='x',padx=30,pady=(28,19))
        lf=tk.Frame(h,bg=C['bg']);lf.pack(side='left')
        text(lf,title,20,True).pack(anchor='w')
        text(lf,subtitle,10,color=C['muted']).pack(anchor='w',pady=(5,0))
        if action_label:button(h,action_label,action).pack(side='right',pady=3)
        return h

    def page_home(self,parent):
        self.header(parent,'Todo el etiquetado en un unico lugar',
            'Plantillas controladas, formatos A4 y trazabilidad de cada emisión.',
            '+ Nueva emisión',lambda:self.show('emitir'))
        stats=self.store.stats()
        strip=tk.Frame(parent,bg=C['bg']);strip.pack(fill='x',padx=30)
        for title,n,subtitle,col in [
            ('Etiquetas',stats['labels'],'En el maestro',C['blue']),
            ('Vigentes',stats['approved'],'Autorizadas',C['green']),
            ('Por revisar',stats['pending'],'No emitir en produccion',C['orange']),
            ('Emisiones',stats['issues'],'PDF con trazabilidad',C['blue_dark'])]:
            b,inner=card(strip,17);b.pack(side='left',fill='both',expand=True,padx=(0,10))
            text(inner,title,10,color=C['muted'],bg='white').pack(anchor='w')
            text(inner,str(n),28,True,col,'white').pack(anchor='w',pady=(9,5))
            text(inner,subtitle,9,color=C['muted'],bg='white').pack(anchor='w')
        rows=tk.Frame(parent,bg=C['bg']);rows.pack(fill='x',padx=30,pady=21)
        for heading,body,cmd,label in [
           ('Emisión asistida','Complete los campos de su etiqueta, configure el tamaño y genere el PDF A4.',
            lambda:self.show('emitir'),'Preparar etiquetas'),
           ('Maestro y versiones','Consulte los archivos de origen, cree revisiones y controle su vigencia.',
            lambda:self.show('maestro'),'Abrir maestro'),
           ('Reimpresión trazable','Recupere una emisión anterior y seleccione un rango concreto de numeros.',
            lambda:self.show('historial'),'Ver historial')]:
            b,inner=card(rows,19);b.pack(side='left',fill='both',expand=True,padx=(0,10))
            text(inner,heading,13,True,bg='white').pack(anchor='w')
            text(inner,body,10,color=C['muted'],bg='white',wraplength=245).pack(anchor='w',pady=(11,18))
            button(inner,label,cmd,'soft').pack(anchor='w')
        b,inner=card(parent,20);b.pack(fill='x',padx=30,pady=(0,15))
        text(inner,'Control documental',13,True,bg='white').pack(anchor='w')
        text(inner,'Los originales importados se conservan inalterados. Las nuevas plantillas permanecen pendientes hasta registrar la referencia de su aprobacion documental.',10,color=C['muted'],bg='white',wraplength=900).pack(anchor='w',pady=(8,5))
        text(inner,'Catálogo CM: '+str(stats['materials'])+' materiales  |  códigos repetidos: '+str(len(self.store.material_duplicates())),10,color=C['blue_dark'],bg='white').pack(anchor='w')

    def _profile_dict(self):
        from .emission_work import profile_numbers
        return profile_numbers({k:str(int(v.get()) if k=='crop_marks' else v.get()) for k,v in self._work_vars().items()})

    def _set_profile(self,event=None):
        name=self.emit_profile.get()
        p=next((x for x in self.store.profile_list() if x['name']==name),None)
        if not p:return
        m={'width_mm':self.emit_w,'height_mm':self.emit_h,'margin_mm':self.emit_margin,
           'gap_mm':self.emit_gap,'offset_x_mm':self.emit_offx,'offset_y_mm':self.emit_offy,
           'start_slot':self.emit_start,'orientation':self.emit_orient,'crop_marks':self.emit_cut,
           'printer_name':self.emit_printer,'safety_mm':self.emit_safety}
        for k,v in m.items():v.set(p[k])
        self._emit_stats()

    def _get_selected_version(self):
        return self.services.emission_version(self.current_version_id) if self.current_version_id else None

    def select_emission_version(self,row):
        self.current_version_id=row['version_id'];self.current_label_id=row['id']
        self.services.library.opened(row)
        self.show('emitir')

    def _open_library_picker(self):
        if hasattr(self,'_quick_popup') and self._quick_popup.winfo_exists():
            self._quick_popup.lift();return 'break'
        popup=tk.Toplevel(self);self._quick_popup=popup
        popup.title('Biblioteca | Buscar y seleccionar etiqueta');popup.geometry('1100x740');popup.minsize(950,640)
        def chosen(row):
            popup.destroy();self.select_emission_version(row)
        panel=LibraryPanel(popup,self.services,chosen,chosen);panel.pack(fill='both',expand=True)
        panel.search.focus_set();popup.bind('<Escape>',lambda _:popup.destroy())
        return 'break'

    def page_emit(self,parent):
        self.header(parent,'Nueva emisión','Datos por envase, estado del material y ajuste automático en A4.',
                    'Configurar impresora',lambda:self.show('centro'))
        shell=tk.Frame(parent,bg=C['bg']);shell.pack(fill='both',expand=True,padx=30,pady=(0,25))
        shell.grid_columnconfigure(0,weight=0,minsize=385)
        shell.grid_columnconfigure(1,weight=1)
        left,body=card(shell,20);left.grid(row=0,column=0,sticky='nsew',padx=(0,15))
        text(body,'01  Seleccion de etiqueta',12,True,bg='white').pack(anchor='w')
        text(body,'Elija una revisión en la biblioteca. Ctrl+K abre la búsqueda rápida.',9,color=C['muted'],bg='white',wraplength=330).pack(anchor='w',pady=(8,4))
        self.emit_label_title=text(body,'Sin etiqueta seleccionada',11,True,bg='white',wraplength=335)
        self.emit_label_title.pack(anchor='w',pady=5)
        button(body,'Elegir en biblioteca  ·  Ctrl+K',self._open_library_picker,'soft').pack(fill='x',pady=(4,8))
        self.label_version_note=text(body,'Seleccione una plantilla',9,color=C['orange'],bg='white',wraplength=335)
        self.label_version_note.pack(anchor='w')
        tk.Frame(body,height=1,bg=C['line']).pack(fill='x',pady=18)
        text(body,'02  Datos de la etiqueta',12,True,bg='white').pack(anchor='w')
        self.dynamic_fields=tk.Frame(body,bg='white');self.dynamic_fields.pack(fill='x',pady=(7,10))
        tk.Frame(body,height=1,bg=C['line']).pack(fill='x',pady=13)
        text(body,'03  Etiqueta de estado',12,True,bg='white').pack(anchor='w')
        text(body,'Superponer en el recuadro previsto o imprimir por separado.',9,color=C['muted'],bg='white',wraplength=330).pack(anchor='w',pady=(4,8))
        options=[('ninguna','Sin etiqueta de estado'),('sin_analizar','Sin analizar  /  Amarilla'),
                 ('aprobado','Aprobado  /  Verde'),('rechazado','Rechazado  /  Roja')]
        self._state_options=options
        self.status_selector=ttk.Combobox(body,state='readonly',width=39,
                                    values=[label for _,label in options],style='Covex.TCombobox')
        self.status_selector.pack(fill='x',pady=(0,7));self.status_selector.current(0)
        self.status_selector.bind('<<ComboboxSelected>>',self._state_change)
        self.status_inputs=tk.Frame(body,bg='white');self.status_inputs.pack(fill='x')
        self.status_note=text(body,'',9,color=C['muted'],bg='white',wraplength=320)
        self.status_note.pack(anchor='w',pady=(3,5))
        tk.Frame(body,height=1,bg=C['line']).pack(fill='x',pady=13)
        text(body,'04  Serie y formato',12,True,bg='white').pack(anchor='w')
        seq=tk.Frame(body,bg='white');seq.pack(fill='x',pady=(9,10))
        self._labeled_input(seq,'N. de recipientes',self.emit_count,0,0)
        button(body,'Datos individuales por envase (PN / PB / lote)',self._edit_vessels,'soft').pack(anchor='w',pady=(1,8))
        self.vessel_note=text(body,'Sin datos individuales: se usan valores comunes.',9,color=C['muted'],bg='white',wraplength=325)
        self.vessel_note.pack(anchor='w',pady=(0,9))
        text(seq,'Etiquetas por recipiente',9,color=C['muted'],bg='white').grid(row=0,column=1,sticky='w',padx=(15,0))
        opts=ttk.Combobox(seq,values=['1','2'],state='readonly',width=8)
        opts.set(str(self.emit_copies.get()));opts.grid(row=1,column=1,sticky='w',padx=(15,0))
        opts.bind('<<ComboboxSelected>>',lambda _: (self.emit_copies.set(int(opts.get())),self._emit_stats()))
        prof=tk.Frame(body,bg='white');prof.pack(fill='x',pady=(1,8))
        text(prof,'Perfil de impresión',9,color=C['muted'],bg='white').pack(anchor='w')
        self.profile_select=ttk.Combobox(prof,state='readonly',textvariable=self.emit_profile,
            values=[r['name'] for r in self.store.profile_list()],style='Covex.TCombobox')
        self.profile_select.pack(fill='x',pady=(5,0));self.profile_select.bind('<<ComboboxSelected>>',self._set_profile)
        dimension=tk.Frame(body,bg='white');dimension.pack(fill='x',pady=(4,8))
        self._labeled_input(dimension,'Ancho (mm)',self.emit_w,0,0)
        self._labeled_input(dimension,'Alto (mm)',self.emit_h,0,1)
        self._labeled_input(dimension,'Seguridad (mm)',self.emit_safety,1,0)
        button(body,'Restablecer tamaño original del máster',self._use_master_size,'ghost').pack(anchor='w',pady=(2,8))
        self.emit_summary=text(body,'',9,True,C['blue_dark'],'white')
        self.emit_summary.pack(anchor='w',pady=(3,10))
        actions=tk.Frame(body,bg='white');actions.pack(fill='x',pady=(8,0))
        button(actions,'Previsualizar A4',self.preview_issue,'soft').pack(side='left',padx=(0,8))
        button(actions,'Generar PDF',self.issue_pdf).pack(side='left')
        button(body,'Abrir ultimo PDF',self.open_last_pdf,'ghost').pack(anchor='w',pady=(9,0))
        for v in [self.emit_count,self.emit_w,self.emit_h]:
            v.trace_add('write',lambda *_:self._emit_stats())
        right,rb=card(shell,20);right.grid(row=0,column=1,sticky='new')
        prh=tk.Frame(rb,bg='white');prh.pack(fill='x',pady=(0,11))
        text(prh,'Vista previa de la hoja A4',13,True,bg='white').pack(side='left')
        self.preview_pages=text(prh,'',9,color=C['muted'],bg='white');self.preview_pages.pack(side='right')
        preview_holder=tk.Frame(rb,bg='#E7EDF5',padx=14,pady=14)
        preview_holder.pack(fill='x')
        self.preview_label=tk.Label(preview_holder,bg='#E7EDF5',text='Seleccione una etiqueta y pulse Previsualizar A4',
                              fg=C['muted'],font=(UI_FONT,11))
        self.preview_label.pack(fill='x',anchor='n')
        self.preview_warning=text(rb,'',9,color=C['orange'],bg='white',wraplength=680)
        self.preview_warning.pack(anchor='w',pady=(12,0))
        if not self.current_version_id:
            rows=self.store.labels()
            if rows:self.current_version_id=rows[0]['version_id']
        self._emit_label_change()
        if not self.emit_profile.get() and self.store.profile_list():
            self.emit_profile.set(self.store.profile_list()[0]['name'])
            self._set_profile()
        selected_design=self._get_selected_version()
        if selected_design and selected_design.get('_variant_id'):
            self.emit_w.set(str(selected_design['base_w_mm']));self.emit_h.set(str(selected_design['base_h_mm']))
        self._emit_stats()
        self._state_change()
        self.after(150,self.preview_issue)

    def _labeled_input(self,parent,label,var,r,c):
        f=tk.Frame(parent,bg='white')
        f.grid(row=r,column=c,sticky='w',padx=(0 if c==0 else 14,0),pady=3)
        text(f,label,9,color=C['muted'],bg='white').pack(anchor='w')
        e=entry(f,var,10);e.pack(anchor='w',pady=(4,0))
        return e

    def _emit_label_change(self,event=None):
        v=self._get_selected_version()
        for w in self.dynamic_fields.winfo_children():w.destroy()
        self.formvars={}
        self.per_container={}
        self.status_kind.set('ninguna')
        self.status_placement.set('integrada')
        self.status_fecha.set('')
        self.status_persona.set('')
        self.status_expiry.set('')
        if hasattr(self,'status_selector') and self.status_selector.winfo_exists():self.status_selector.current(0)
        if not v:return
        self.current_label_id=v['label_id']
        self.emit_label_title.configure(text=v['name']+'  ·  '+v['code']+'  ·  v'+v['version']+('  ·  Variante '+v['_variant_code']+' / '+v['_variant_state'] if v.get('_variant_id') else ''))
        self.label_version_note.configure(text=f"{v['annex']}  |  Revisión {v['version']}  |  "+('VIGENTE' if v['state']=='APPROVED' else 'PENDIENTE - solo PDF de prueba'),
                                   fg=C['green'] if v['state']=='APPROVED' else C['orange'])
        fields=json.loads(v['fields_json'])
        for f in fields:
            if f['key'] in ('numero','texto_fijo'):continue
            line=tk.Frame(self.dynamic_fields,bg='white');line.pack(fill='x',pady=(6,3))
            text(line,f['label']+(' *' if f.get('required') else ''),9,color=C['muted'],bg='white').pack(anchor='w')
            var=tk.StringVar()
            entry(line,var,35).pack(fill='x',pady=(4,0))
            self.formvars[f['key']]=var
        if not self.formvars:
            text(self.dynamic_fields,'Sin campos definidos. Configure la plantilla en el editor avanzado.',10,color=C['orange'],bg='white',wraplength=320).pack(anchor='w',pady=9)
        self._emit_stats()
        self._state_change()

    def _use_master_size(self):
        v=self._get_selected_version()
        if not v:return
        if self.status_kind.get()!='ninguna' and self.status_placement.get()=='independiente':
            asset=self._state_master()
            if asset:
                crop=json.loads(asset['crop_json'])
                self.emit_w.set(str(round((crop[2]-crop[0])*25.4/72,2)))
                self.emit_h.set(str(round((crop[3]-crop[1])*25.4/72,2)))
        else:
            self.emit_w.set(str(v['base_w_mm']))
            self.emit_h.set(str(v['base_h_mm']))
        self._emit_stats()

    def _state_change(self,event=None):
        if not hasattr(self,'status_selector') or not self.status_selector.winfo_exists():return
        ix=self.status_selector.current()
        if ix<0:ix=0
        kind=self._state_options[ix][0]
        self.status_kind.set(kind)
        for w in self.status_inputs.winfo_children():w.destroy()
        if kind=='ninguna':
            self.status_note.configure(text='La etiqueta principal se imprimirá sin estado.',fg=C['muted'])
            return
        asset=self.store.status_master(kind)
        v=self._get_selected_version()
        area=json.loads(v['status_area_json'] or '[]') if v else []
        note='Revisión 00  |  '+('DISEÑO VIGENTE' if asset and asset['state']=='APPROVED' else 'PENDIENTE: solo PDF de prueba')
        if not area:note+='  |  Falta definir zona en el editor'
        self.status_note.configure(text=note,fg=C['green'] if asset and asset['state']=='APPROVED' else C['orange'])
        for value,title in [('integrada','Integrada en etiqueta principal'),('independiente','Etiqueta de estado por separado')]:
            tk.Radiobutton(self.status_inputs,text=title,variable=self.status_placement,value=value,
                           bg='white',fg=C['ink'],font=(UI_FONT,9)).pack(anchor='w')
        for title,var in [('Fecha (DD/MM/AAAA)',self.status_fecha),
                          ('Responsable (si figura)',self.status_persona),
                          ('Caducidad / reanálisis',self.status_expiry)]:
            if kind!='aprobado' and var==self.status_expiry:continue
            if kind=='sin_analizar' and var==self.status_persona:continue
            block=tk.Frame(self.status_inputs,bg='white');block.pack(fill='x',pady=3)
            text(block,title,9,color=C['muted'],bg='white').pack(anchor='w')
            entry(block,var,34).pack(fill='x')

    def _state_object(self):
        out={'kind':self.status_kind.get()}
        if out['kind']!='ninguna':
            out.update(placement=self.status_placement.get(),fecha=self.status_fecha.get().strip(),
                       persona=self.status_persona.get().strip(),
                       caducidad_reanalisis=self.status_expiry.get().strip())
        return out

    def _state_master(self):
        kind=self.status_kind.get()
        return self.store.status_master(kind) if kind!='ninguna' else None

    def _test_mode(self,v):
        asset=self._state_master()
        return v['state']!='APPROVED' or v.get('_variant_state','APPROVED')!='APPROVED' or (asset is not None and asset['state']!='APPROVED')

    def _edit_vessels(self):
        try:
            count=int(self.emit_count.get())
            if not 1<=count<=10000:raise ValueError('Indique de 1 a 10000 recipientes.')
            dlg=VesselDialog(self,count,self.per_container)
            self.wait_window(dlg)
            if dlg.result is not None:
                self.per_container=dlg.result
                self.vessel_note.configure(text=f'{len(self.per_container)} envases con datos propios. El resto usa los campos comunes.',fg=C['blue_dark'])
                self.preview_issue()
        except ValueError as ex:messagebox.showerror('Serie',str(ex),parent=self)

    def _emit_stats(self):
        label=getattr(self,'emit_summary',None)
        if not label or not label.winfo_exists():return
        try:
            count=int(self.emit_count.get());p=self._profile_dict()
            plan=self.services.sheet_plan(p,count*int(self.emit_copies.get()))
            label.configure(text=f'{plan.capacity} etiquetas/hoja  |  {plan.pages} hojas A4  |  {plan.count_physical} impresiones')
        except (LayoutError,ValueError):
            label.configure(text='Compruebe las medidas y la cantidad de etiquetas')

    def _emit_values(self):
        return {k:var.get() for k,var in self.formvars.items()}

    def preview_issue(self):
        if self.current_page!='emitir':return
        try:
            v=self._get_selected_version()
            if not v:return
            p=self._profile_dict();count=int(self.emit_count.get());copy=int(self.emit_copies.get())
            plan=self.services.sheet_plan(p,count*copy)
            sample=max(1,min(count,plan.capacity))
            cache=self.services.output_path('cache','preview_a4.pdf')
            vals=self._emit_values()
            result=self.services.render(v,vals,p,list(range(1,sample+1)),count,copy,cache,True,
                                   per_container=self.per_container,status=self._state_object(),status_master=self._state_master())
            img,_=self.services.preview_pdf(cache,maxwidth=480)
            img.thumbnail((580,640))
            self._preview_image=ImageTk.PhotoImage(img)
            self.preview_label.configure(image=self._preview_image,text='')
            self.preview_pages.configure(text=f'Vista: página 1 de {plan.pages}')
            alerts=result['warnings']
            self.preview_warning.configure(text=(' | '.join(alerts[:3]) if alerts else 'Previsualizacion de prueba. El PDF final se generara sin esta marca si la plantilla esta vigente.'),
                                           fg=C['orange'] if alerts else C['muted'])
        except Exception as ex:
            self.preview_warning.configure(text=str(ex),fg=C['red'])

    def issue_pdf(self):
        try:
            v=self._get_selected_version()
            if not v:return
            p=self._profile_dict()
            count=int(self.emit_count.get());copies=int(self.emit_copies.get())
            inds=list(range(1,count+1))
            if count>10000:raise ValueError('Numero excesivo de etiquetas.')
            test_mode=self._test_mode(v)
            if not any(f['key']=='numero' for f in json.loads(v['fields_json'])) and count>1:
                if not messagebox.askyesno('Sin numeración',
                    'La plantilla no tiene un campo de numeración. Las copias resultantes seran identicas, sin 1/N en su interior. Continuar?',parent=self):return
            if test_mode:
                if not messagebox.askyesno('Solo PDF de prueba',
                       'Esta plantilla NO esta vigente. Se generara un PDF marcado PRUEBA - NO APTO PARA USO GMP. Continuar?',parent=self):return
                path=filedialog.asksaveasfilename(parent=self,defaultextension='.pdf',filetypes=[('PDF','*.pdf')],
                       initialfile='PRUEBA_'+slug(v['name'])+'.pdf')
                if not path:return
            if self.emission_work is None:self._work_changed()
            if not self._work_guard():return
            if self.emission_work is None:raise PermissionError('Guarde el trabajo antes de generar un PDF.')
            if not test_mode:
                if not messagebox.askyesno('Emitir definitivamente','Registrar la emisión definitiva del trabajo guardado? No equivale a guardar un borrador ni a confirmar impresión física.',parent=self,default='no'):return
                w,path,data=self.services.work.issue(self.emission_work['uid'],self.emission_work['generation'],self.store.setting('operator'))
                self.emission_work=w;self._work_note(w['name']+' · ISSUED · emisión #'+str(w['issue_id']))
                msg=f'Emisión #{w["issue_id"]} registrada con snapshot.\n\n{data["physical"]} etiquetas en {data["pages"]} hojas A4.\n\nPDF:\n{path}\n\nLa aplicación registra la generación del PDF, no confirma la impresión física.'
            else:
                w=self.emission_work;data=self.services.work.proof(w['uid'],w['generation'],path)
                msg=f'PDF de prueba creado.\n\n{data["physical"]} etiquetas en {data["pages"]} hojas A4.\n\nNo apto para uso productivo.\n\n{path}'
            self.last_issue_pdf=path
            if data['warnings']:
                msg+='\n\nAdvertencias:\n'+'\n'.join(data['warnings'][:4])
            if messagebox.askyesno('PDF generado',msg+'\n\nDesea abrir el archivo ahora?',parent=self):
                try:open_path(path)
                except Exception as ex:messagebox.showwarning('Visor PDF',str(ex))
        except (ValueError,PermissionError,LayoutError,OSError) as ex:
            if self.emission_work and not self._work_dirty:
                try:self.emission_work=self.services.work.get(self.emission_work['uid']);self._work_note(self.emission_work['phase']+' · '+str(ex))
                except (ValueError,OSError):pass
            messagebox.showerror('No se ha podido emitir',str(ex),parent=self)

    def open_last_pdf(self):
        if not self.last_issue_pdf or not self.services.file_exists(self.last_issue_pdf):
            messagebox.showinfo('Sin archivo','Todavia no se ha generado ningun PDF en esta sesion.')
            return
        try:open_path(self.last_issue_pdf)
        except Exception as ex:messagebox.showerror('Error',str(ex))

    def page_print_center(self,parent):
        self.header(parent,'Formatos, A4 y calibración',
           'Guarde ajustes por impresora y reutilice las medidas en las emisiones.')
        layout=tk.Frame(parent,bg=C['bg']);layout.pack(fill='both',expand=True,padx=30,pady=(0,20))
        left,body=card(layout,22);left.pack(side='left',fill='both',expand=True,padx=(0,16))
        text(body,'Perfil de impresión',13,True,bg='white').pack(anchor='w')
        form=tk.Frame(body,bg='white');form.pack(anchor='w',pady=15)
        self.profile_name_var=tk.StringVar(value=self.emit_profile.get() or 'Nuevo perfil')
        def field(row,label,var,w=12):
            text(form,label,10,color=C['muted'],bg='white').grid(row=row,column=0,sticky='w',padx=(0,15),pady=8)
            return entry(form,var,w).grid(row=row,column=1,sticky='w',pady=7)
        field(0,'Nombre del perfil',self.profile_name_var,34)
        for j,(name,var) in enumerate([
           ('Ancho de etiqueta (mm)',self.emit_w),('Alto de etiqueta (mm)',self.emit_h),
           ('Margen A4 (mm)',self.emit_margin),('Separacion entre etiquetas (mm)',self.emit_gap),
           ('Correccion horizontal (mm)',self.emit_offx),('Correccion vertical (mm)',self.emit_offy),
           ('Casilla inicial en primera hoja',self.emit_start),('Nombre de impresora (referencia)',self.emit_printer)]):
            field(j+1,name,var,32 if j==7 else 13)
        orient=tk.Frame(body,bg='white');orient.pack(anchor='w',pady=(3,10))
        text(orient,'Orientacion A4',10,color=C['muted'],bg='white').pack(side='left',padx=(0,18))
        for label,val in [('Vertical','portrait'),('Horizontal','landscape')]:
            tk.Radiobutton(orient,text=label,variable=self.emit_orient,value=val,bg='white',
                           fg=C['ink'],font=(UI_FONT,10)).pack(side='left',padx=7)
        tk.Checkbutton(body,text='Incluir marcas de corte',variable=self.emit_cut,bg='white',
              fg=C['ink'],font=(UI_FONT,10)).pack(anchor='w',pady=5)
        def save():
            try:
                p=self._profile_dict();p['name']=self.profile_name_var.get().strip()
                if not p['name']:raise ValueError('Indique un nombre para el perfil.')
                self.services.sheet_plan(p,1)
                self.store.add_profile(p)
                self.emit_profile.set(p['name'])
                messagebox.showinfo('Perfil guardado','El perfil ya se puede usar en cualquier emisión.',parent=self)
                self.show('centro')
            except (ValueError,LayoutError) as ex:messagebox.showerror('Error',str(ex),parent=self)
        commands=tk.Frame(body,bg='white');commands.pack(anchor='w',pady=12)
        button(commands,'Guardar perfil',save).pack(side='left',padx=(0,8))
        def calibrate():
            try:
                path=self.services.calibration(self._profile_dict(),self.services.output_path('cache','HOJA_CALIBRACION_A4.pdf'))
                if messagebox.askyesno('Hoja de prueba','Hoja de calibracion creada. Imprimala a escala 100%, sin ajustar a pagina.\n\nDesea abrirla?',parent=self):
                    open_path(path)
            except Exception as ex:messagebox.showerror('Calibracion',str(ex),parent=self)
        button(commands,'Hoja de prueba A4',calibrate,'soft').pack(side='left')
        right,inner=card(layout,22);right.pack(side='left',fill='both',expand=True)
        text(inner,'Distribucion calculada',13,True,bg='white').pack(anchor='w')
        summary=text(inner,'',11,True,C['blue_dark'],'white');summary.pack(anchor='w',pady=12)
        holder=tk.Frame(inner,bg='#E9EFF6',height=390);holder.pack(fill='x',pady=10)
        cv=tk.Canvas(holder,width=310,height=370,bg='#E9EFF6',bd=0,highlightthickness=0)
        cv.pack(pady=10)
        def paint(*_):
            if not cv.winfo_exists():return
            cv.delete('all')
            try:
                p=self._profile_dict();plan=self.services.sheet_plan(p,1)
                summary.configure(text=f'{plan.capacity} etiquetas por hoja A4  |  {plan.cols} columnas x {plan.rows} filas')
                scale=min(270/plan.paper_w_mm,340/plan.paper_h_mm)
                dw=plan.paper_w_mm*scale;dh=plan.paper_h_mm*scale
                l=155-dw/2;t=185-dh/2
                cv.create_rectangle(l,t,l+dw,t+dh,fill='white',outline='#C7D4E2')
                for i in range(plan.capacity):
                    x=l+(p['margin_mm']+(i%plan.cols)*(p['width_mm']+p['gap_mm'])+p['offset_x_mm'])*scale
                    y=t+(p['margin_mm']+(i//plan.cols)*(p['height_mm']+p['gap_mm'])+p['offset_y_mm'])*scale
                    cv.create_rectangle(x,y,x+p['width_mm']*scale,y+p['height_mm']*scale,
                                        fill='#EAF2FB' if i+1>=p['start_slot'] else '#E5E7EB',outline='#7196BE')
                    cv.create_text(x+7,y+7,text=str(i+1),anchor='nw',font=(UI_FONT,9,'bold'),fill=C['blue_dark'])
            except (ValueError,LayoutError) as ex:
                summary.configure(text='No cabe en A4: '+str(ex)[:70])
        for v in [self.emit_w,self.emit_h,self.emit_margin,self.emit_gap,self.emit_offx,self.emit_offy,self.emit_start,self.emit_orient]:
            v.trace_add('write',paint)
        paint()
        text(inner,'Las casillas grises representan posiciones de la primera hoja que no se utilizaran.',9,
             color=C['muted'],bg='white',wraplength=380).pack(anchor='w')

    def _master_rows(self):
        if hasattr(self,'library_panel'):self.library_panel.refresh()

    def page_master(self,parent):
        self.header(parent,'Biblioteca de etiquetas',
            'Explore diseños, revisiones y fuentes. Doble clic abre la ficha · Ctrl+K selecciona para emitir.',
            '+ Importar etiqueta',self.import_label_dialog)
        self.library_panel=LibraryPanel(parent,self.services,lambda row:self._master_detail(),self.select_emission_version)
        self.library_panel.pack(fill='both',expand=True,padx=30,pady=(0,10))
        self.master_tree=self.library_panel.tree
        actions=tk.Frame(parent,bg=C['bg']);actions.pack(fill='x',padx=30,pady=(0,16))
        for i,(label,cmd) in enumerate([
          ('Editar campos',self._master_edit),('Nueva versión',self._master_clone),('Activar revisión',self._master_approve),
          ('Metadatos y fuente',self._edit_metadata),('Importar carpeta',self.import_folder_dialog),('Comparación básica',self._master_compare)]):
            button(actions,label,cmd,'soft').grid(row=i//3,column=i%3,sticky='w',padx=(0,9),pady=3)

    def _selected_master(self):
        row=self.library_panel.selected() if hasattr(self,'library_panel') else None
        if not row:messagebox.showinfo('Seleccione','Seleccione una revisión del listado.',parent=self)
        return row

    def _edit_metadata(self):
        row=self._selected_master()
        if not row:return
        pop=tk.Toplevel(self);pop.title('Metadatos documentados');pop.geometry('520x490');pop.configure(bg='white')
        box=tk.Frame(pop,bg='white',padx=22,pady=18);box.pack(fill='both',expand=True)
        text(box,'Completar solo con información de la fuente',12,True,bg='white').pack(anchor='w',pady=(0,10))
        fields={}
        labels={'product':'Producto','family':'Familia','type':'Tipo','country':'País','language':'Idioma'}
        for k in METADATA_FIELDS:
            text(box,labels[k],9,bg='white').pack(anchor='w')
            fields[k]=tk.StringVar(value=row.get(k,''));entry(box,fields[k],45).pack(fill='x',pady=(2,6))
        text(box,'Referencia de la fuente (obligatoria)',9,bg='white').pack(anchor='w')
        source=tk.StringVar();entry(box,source,45).pack(fill='x',pady=5)
        def save():
            try:
                self.services.library.update_metadata(row['id'],{k:v.get() for k,v in fields.items()},source.get())
                pop.destroy();self.show('maestro')
            except Exception as ex:messagebox.showerror('No guardado',str(ex),parent=pop)
        button(box,'Guardar metadatos',save).pack(anchor='e',pady=10)

    def _master_detail(self):
        r=self._selected_master()
        if not r:return
        versions=self.store.versions(r['id'])
        w=tk.Toplevel(self);w.title('Ficha de etiqueta  |  '+r['name']);w.configure(bg=C['white']);w.geometry('640x560')
        base=tk.Frame(w,bg='white',padx=24,pady=24);base.pack(fill='both',expand=True)
        text(base,r['name'],19,True,bg='white').pack(anchor='w')
        info=f"Código: {r['code']}  |  {r['origin']}  |  {r['category']}  |  {r['annex']}"
        text(base,info,10,color=C['muted'],bg='white',wraplength=580).pack(anchor='w',pady=8)
        text(base,'Versiones y documentos fuente',12,True,bg='white').pack(anchor='w',pady=(18,9))
        cols=('rev','state','date','evidence')
        tree=ttk.Treeview(base,columns=cols,show='headings',height=9,style='Covex.Treeview')
        for key,label,sz in [('rev','Revisión',70),('state','Estado',115),('date','Fecha',170),('evidence','Referencia aprobacion',215)]:
            tree.heading(key,text=label);tree.column(key,width=sz)
        tree.pack(fill='both',expand=True)
        for v in versions:tree.insert('', 'end',iid=str(v['id']),values=(v['version'],v['state'],v['created_at'][:19],v['approval_ref'] or '-'))
        tree.selection_set(str(r['version_id']))
        def viewfile():
            sel=tree.selection();vid=int(sel[0]) if sel else versions[0]['id']
            v=self.store.version(vid)
            try:open_path(self.services.asset_path(v['master_pdf']))
            except Exception as ex:messagebox.showerror('Error',str(ex),parent=w)
        def edit():
            sel=tree.selection();vid=int(sel[0]) if sel else versions[0]['id']
            w.destroy();self.editor(vid)
        acts=tk.Frame(base,bg='white');acts.pack(fill='x',pady=(15,0))
        button(acts,'Ver PDF maestro',viewfile,'soft').pack(side='left',padx=(0,9))
        button(acts,'Editor avanzado',edit).pack(side='left')

    def _master_edit(self):
        r=self._selected_master()
        if r:self.editor(r['version_id'])

    def _master_clone(self):
        r=self._selected_master()
        if not r:return
        old=self.store.version(r['version_id'])
        ver=simpledialog.askstring('Nueva version','Código de revisión de la nueva version (p.ej. 01):',parent=self)
        if not ver:return
        reason=simpledialog.askstring('Motivo','Motivo obligatorio de la revisión:',parent=self)
        if not reason or len(reason.strip())<5:
            messagebox.showwarning('Revisión','Indique un motivo de al menos 5 caracteres.',parent=self);return
        try:
            v=self.store.clone_version(old['id'],ver.strip(),reason.strip())
            self.show('maestro')
            self.editor(v)
        except Exception as ex:messagebox.showerror('No se ha creado la version',str(ex),parent=self)

    def _master_compare(self):
        r=self._selected_master()
        if not r:return
        versions=self.store.versions(r['id'])
        if len(versions)<2:
            messagebox.showinfo('Comparacion','Se necesitan al menos dos versiones de la misma etiqueta.',parent=self);return
        a,b=versions[0],versions[1]
        popup=tk.Toplevel(self);popup.geometry('990x735');popup.configure(bg=C['bg']);popup.title('Comparar versiones')
        text(popup,f"{r['name']}  |  {a['version']} frente a {b['version']}",16,True,bg=C['bg']).pack(anchor='w',padx=20,pady=18)
        row=tk.Frame(popup,bg=C['bg']);row.pack(fill='both',expand=True,padx=20,pady=(0,15))
        self._compare_imgs=[]
        try:
            imgs=[self.services.thumbnail(self.store.version(v['id']),width_px=365) for v in (a,b)]
            for v,im in zip((a,b),imgs):
                f,inner=card(row,12);f.pack(side='left',fill='both',expand=True,padx=(0,12))
                text(inner,f'Revisión {v["version"]}  |  {v["state"]}',11,True,bg='white').pack(anchor='w',pady=(0,10))
                im.thumbnail((400,550));p=ImageTk.PhotoImage(im);self._compare_imgs.append(p)
                tk.Label(inner,image=p,bg='white').pack(anchor='n')
            def change():
                differences=[]
                if a['pdf_sha256']!=b['pdf_sha256']:differences.append('El PDF de fondo ha cambiado.')
                if a['fields_json']!=b['fields_json']:differences.append('La configuracion de campos variables ha cambiado.')
                if a['crop_json']!=b['crop_json']:differences.append('El recorte de origen ha cambiado.')
                messagebox.showinfo('Diferencias detectadas','\n'.join(differences) if differences else 'No se detectan diferencias de contenido o configuracion.',parent=popup)
            button(popup,'Comprobar cambios documentales',change).pack(anchor='w',padx=20,pady=15)
        except Exception as ex:messagebox.showerror('Error',str(ex),parent=popup)

    def _master_approve(self):
        r=self._selected_master()
        if not r:return
        v=self.store.version(r['version_id'])
        if v['state']!='PENDING':
            messagebox.showinfo('Estado','Seleccione una version pendiente. Para modificar una vigente, cree una revisión.',parent=self);return
        reviewer=simpledialog.askstring('Responsable','Nombre del responsable de verificacion:',parent=self)
        if not reviewer:return
        evidence=simpledialog.askstring('Referencia documental',
           'Indique la aprobacion/EGP/anexo que autoriza este diseño y los campos configurados:',parent=self)
        if not evidence:return
        if not messagebox.askyesno('Activar version',
            'Confirma que ha revisado visualmente el diseño, sus requisitos regulatorios y las posiciones de todos los campos?\n\nRegistrar la referencia no equivale a una firma electronica GMP.',parent=self):return
        try:
            self.store.approve(v['id'],reviewer,evidence)
            self.show('maestro')
        except Exception as ex:messagebox.showerror('Activacion no realizada',str(ex),parent=self)

    def import_label_dialog(self):
        path=filedialog.askopenfilename(parent=self,title='Seleccionar etiqueta PDF o Word',
              filetypes=[('Etiquetas PDF, Word e imagen','*.pdf *.doc *.docx *.png *.jpg *.jpeg'),('Todos los archivos','*.*')])
        if path:self._import_one(path,interactive=True)

    def _import_one(self,path,interactive=False):
        meta=proposed_identity(path)
        data={'name':meta['name'],'version':meta['version'],'code':'','category':meta['category'],
              'annex':'','origin':'COVEX','customer':'','ref_customer':''}
        if interactive:
            popup=tk.Toplevel(self);popup.title('Importar etiqueta');popup.configure(bg=C['white']);popup.geometry('595x620')
            popup.transient(self);popup.grab_set()
            base=tk.Frame(popup,bg='white',padx=26,pady=23);base.pack(fill='both',expand=True)
            text(base,'Nueva etiqueta maestra',18,True,bg='white').pack(anchor='w')
            text(base,Path(path).name,9,color=C['muted'],bg='white',wraplength=520).pack(anchor='w',pady=10)
            v={k:tk.StringVar(value=str(val)) for k,val in data.items()}
            form=tk.Frame(base,bg='white');form.pack(fill='x',pady=(10,0))
            names=[('name','Nombre'),('code','Código de material'),('category','Categoria'),
                   ('annex','Anexo EGP'),('version','Revisión del diseño'),('origin','Origen COVEX / CLIENTE'),
                   ('customer','Cliente (si procede)'),('ref_customer','Referencia cliente')]
            for i,(k,label) in enumerate(names):
                text(form,label,9,color=C['muted'],bg='white').grid(row=i,column=0,sticky='w',pady=8,padx=(0,18))
                if k=='origin':
                    cb=ttk.Combobox(form,textvariable=v[k],values=['COVEX','CLIENTE'],state='readonly',width=32)
                    cb.grid(row=i,column=1,sticky='we',pady=5)
                else:entry(form,v[k],37).grid(row=i,column=1,sticky='we',pady=4)
            def accept():
                for k in data:data[k]=v[k].get().strip()
                if not data['name'] or not data['version']:
                    messagebox.showwarning('Obligatorio','Introduzca nombre y revisión.',parent=popup);return
                if data['origin']=='CLIENTE' and not data['customer']:
                    messagebox.showwarning('Cliente','Introduzca el nombre del cliente.',parent=popup);return
                popup.destroy()
                self._import_processed(path,data)
            button(base,'Importar y revisar en editor',accept).pack(anchor='e',pady=15)
        else:
            self._import_processed(path,data,refresh=False)

    def _import_processed(self,path,data,refresh=True):
        try:
            vid=self.services.import_label(path,data)
            if refresh:
                messagebox.showinfo('Etiqueta importada',
                    'Se ha incorporado como PENDIENTE. Configure campos y revise el PDF antes de activarla.',parent=self)
                self.show('maestro');self.editor(vid)
            return vid
        except Exception as ex:
            if refresh:messagebox.showerror('Importacion fallida',str(ex),parent=self)
            else:raise

    def import_folder_dialog(self):
        folder=filedialog.askdirectory(parent=self,title='Seleccionar carpeta de etiquetas')
        if not folder:return
        paths=list(self.services.importable_files(folder))
        if not paths:
            messagebox.showinfo('Sin archivos','No se han encontrado Word o PDF validos.',parent=self);return
        if not messagebox.askyesno('Importar carpeta',
             f'Se han encontrado {len(paths)} archivos. Se importaran como PENDIENTES y sera necesario revisar los campos individualmente.\n\nContinuar?',parent=self):return
        popup=tk.Toplevel(self);popup.title('Importando etiquetas');popup.geometry('520x195');popup.configure(bg='white')
        base=tk.Frame(popup,bg='white',padx=20,pady=20);base.pack(fill='both',expand=True)
        title=text(base,'Preparando importacion...',12,True,bg='white');title.pack(anchor='w',pady=7)
        progress=ttk.Progressbar(base,maximum=len(paths),mode='determinate',style='Covex.Horizontal.TProgressbar')
        progress.pack(fill='x',pady=15)
        state={'index':0,'ok':0,'bad':[],'cancel':False}
        def step():
            if state['cancel']:popup.destroy();return
            ix=state['index']
            if ix>=len(paths):
                popup.destroy()
                msg=f'Importadas: {state["ok"]} de {len(paths)}.\nCon incidencias: {len(state["bad"])}.'
                if state['bad']:msg+='\n\nPrimeras incidencias:\n'+'\n'.join(state['bad'][:5])
                messagebox.showinfo('Importacion terminada',msg,parent=self)
                self.show('maestro');return
            f=paths[ix];title.configure(text=f'{ix+1}/{len(paths)}  {f.name[:51]}')
            try:
                self._import_one(str(f),False)
                state['ok']+=1
            except Exception as ex:
                state['bad'].append(f'{f.name}: {str(ex)[:75]}')
            state['index']+=1;progress['value']=state['index']
            popup.after(25,step)
        button(base,'Detener',lambda:state.__setitem__('cancel',True),'ghost').pack(anchor='e')
        popup.after(30,step)

    def page_history(self,parent):
        self.header(parent,'Historial y reimpresiones','Recupere los datos y documentos de cada emisión controlada.')
        b,inner=card(parent,18);b.pack(fill='both',expand=True,padx=30,pady=(0,22))
        cols=('id','date','label','version','quant','copies','user','parent')
        self.history_tree=ttk.Treeview(inner,columns=cols,show='headings',style='Covex.Treeview',height=15)
        for k,label,w in [('id','N.',60),('date','Fecha y hora',175),('label','Producto',205),('version','Rev.',60),
             ('quant','Recipientes',115),('copies','Copias',80),('user','Emitido por',170),('parent','Reimpresión de',120)]:
            self.history_tree.heading(k,text=label);self.history_tree.column(k,width=w)
        self.history_tree.pack(fill='both',expand=True)
        for i in self.store.issues():
            self.history_tree.insert('','end',iid=str(i['id']),values=(i['id'],i['created_at'][:19],i['name'],
                   i['version'],i['count_containers'],i['copies_per_container'],i['operator'],i['source_issue_id'] or '-'))
        actions=tk.Frame(inner,bg='white');actions.pack(fill='x',pady=(17,0))
        button(actions,'Abrir PDF',self._history_open).pack(side='left',padx=(0,9))
        button(actions,'Reimprimir numeros',self._history_reprint,'soft').pack(side='left',padx=(0,9))
        button(actions,'Ver detalles',self._history_detail,'soft').pack(side='left')
        text(inner,'Una reimpresión mantiene el numero original (por ejemplo, 12/50), exige motivo y genera un registro independiente.',9,
             color=C['muted'],bg='white').pack(anchor='w',pady=12)

    def _selected_issue(self):
        sel=self.history_tree.selection() if hasattr(self,'history_tree') else ()
        if not sel:messagebox.showinfo('Seleccione','Seleccione una emisión.',parent=self);return None
        return self.store.issue(int(sel[0]))

    def _history_open(self):
        i=self._selected_issue()
        if i:
            try:
                file=self.services.asset_path(i['pdf_path'])
                if not self.services.intact_emission(i):
                    raise OSError('El PDF ha cambiado desde que se emitio. Se bloquea su apertura.')
                open_path(file)
            except Exception as ex:messagebox.showerror('Error',str(ex),parent=self)

    def _history_detail(self):
        i=self._selected_issue()
        if not i:return
        v=self.store.version(i['version_id'])
        val=json.loads(i['variables_json']);p=json.loads(i['profile_json'])
        details=(f'Emisión: #{i["id"]}\nFecha: {i["created_at"]}\nProducto: {v["name"]}\n'
           f'Versión: {v["version"]}\nOperador: {i["operator"]}\n'
           f'Recipientes del expediente: {i["count_containers"]}\nCopias por recipiente: {i["copies_per_container"]}\n'
           f'Numeros seleccionados: {i["selected_indices"]}\n'
           f'Referencia reimpresión: {i["source_issue_id"] or "-"}\nMotivo: {i["reason"] or "-"}\n'
           f'Tamaño: {p["width_mm"]} x {p["height_mm"]} mm\n\nCampos:\n')
        details+='\n'.join(f'  {k}: {value}' for k,value in val.items())
        if i['status_json'] and i['status_json']!='{}':
            details+='\n\nEstado integrado/independiente:\n'+json.dumps(json.loads(i['status_json']),ensure_ascii=False,indent=2)
        if i['per_container_json'] and i['per_container_json']!='{}':
            details+='\n\nDatos por envase:\n'+json.dumps(json.loads(i['per_container_json']),ensure_ascii=False,indent=2)
        details+='\n\nEstado: PDF generado. Impresión fisica no confirmada.'
        w=tk.Toplevel(self);w.title('Detalle de emisión');w.geometry('650x560');w.configure(bg='white')
        t=tk.Text(w,font=('Consolas',10),wrap='word',padx=23,pady=18,relief='flat',bg='white',fg=C['ink'])
        t.pack(fill='both',expand=True);t.insert('1.0',details);t.configure(state='disabled')

    def _history_reprint(self):
        i=self._selected_issue()
        if not i:return
        v=self.store.version(i['version_id'])
        variant_id=i['design_variant_id']
        try:v=self.services.resolved_design(i['version_id'],variant_id,True)
        except (ValueError,PermissionError,OSError) as ex:
            messagebox.showerror('Reimpresión bloqueada',str(ex),parent=self);return
        historical=json.loads(i['design_snapshot_json']) if i['design_snapshot_json'] else None
        if not historical and not messagebox.askyesno('Histórico sin snapshot','Este registro heredado no conserva snapshot de diseño. Se usará la revisión documentada actual, sin atribuirle reproducción exacta. Continuar?',parent=self):return
        if not self.services.intact_emission(i):
            messagebox.showerror('Integridad','El PDF de emisión original ha sido modificado.',parent=self);return
        if v['state']!='APPROVED':
            messagebox.showerror('Reimpresión bloqueada',
              'La version de la emisión ya no esta vigente. Debe evaluarse documentalmente antes de reimprimir.',parent=self);return
        choices=simpledialog.askstring('Reimpresión',
            f'Indique los numeros a reimprimir (1-{i["count_containers"]}).\nEjemplo: 12-14,18\n\nSe conservara su numeración original:',parent=self)
        if not choices:return
        reason=simpledialog.askstring('Motivo de reimpresión','Motivo obligatorio de la reimpresión:',parent=self)
        if not reason or len(reason.strip())<5:
            messagebox.showerror('Motivo','Indique un motivo de al menos 5 caracteres.',parent=self);return
        try:
            numbers=parse_ranges(choices,i['count_containers'])
            if not set(numbers).issubset(json.loads(i['selected_indices'])):
                raise ValueError('Seleccione solo números incluidos en esta emisión. Para otros números, abra la emisión original.')
            profile=json.loads(i['profile_json']);profile['start_slot']=1
            values=json.loads(i['variables_json'])
            out=self.services.output_path('emissions',f'REIMP_{i["id"]}_{datetime.now():%Y%m%d_%H%M%S_%f}.pdf')
            status=json.loads(i['status_json'] or '{}')
            per_container=json.loads(i['per_container_json'] or '{}')
            asset=self.store.status_master(status.get('kind','ninguna')) if status.get('kind','ninguna')!='ninguna' else None
            self.services.render(v,values,profile,numbers,i['count_containers'],i['copies_per_container'],out,False,
                            per_container=per_container,status=status,status_master=asset,history_snapshot=historical)
            pk=self.store.add_issue(v['id'],self.store.setting('operator'),i['count_containers'],
                    i['copies_per_container'],numbers,values,profile,out,source_issue_id=i['id'],reason=reason.strip(),
                    per_container=per_container,status=status)
            messagebox.showinfo('Reimpresión registrada',f'Reimpresión #{pk} generada. {len(numbers)} numeros.\n\n{out}',parent=self)
            self.show('historial')
        except Exception as ex:messagebox.showerror('Reimpresión cancelada',str(ex),parent=self)

    def page_admin(self,parent):
        self.header(parent,'Administración y datos','Ajustes locales, catálogo CM, copias de seguridad y auditoria.')
        shell=tk.Frame(parent,bg=C['bg']);shell.pack(fill='x',padx=30)
        left,inside=card(shell,19);left.pack(side='left',fill='both',expand=True,padx=(0,15))
        text(inside,'Preferencias',13,True,bg='white').pack(anchor='w')
        text(inside,'Usuario que constara en las emisiones',9,color=C['muted'],bg='white').pack(anchor='w',pady=(12,5))
        name=tk.StringVar(value=self.store.setting('operator'))
        entry(inside,name,35).pack(anchor='w')
        def save_user():
            if len(name.get().strip())<3:
                messagebox.showwarning('Obligatorio','Indique el nombre o identificador del operador.',parent=self);return
            self.store.set_setting('operator',name.get().strip())
            self.top_user.configure(text=name.get().strip())
            messagebox.showinfo('Guardado','Usuario actualizado.',parent=self)
        button(inside,'Guardar usuario',save_user,'soft').pack(anchor='w',pady=10)
        text(inside,'Directorio de datos',10,True,bg='white').pack(anchor='w',pady=(15,0))
        text(inside,self.services.location(),9,color=C['muted'],bg='white',wraplength=450).pack(anchor='w',pady=7)
        button(inside,'Crear copia de seguridad ZIP',self._backup).pack(anchor='w',pady=12)
        right,ri=card(shell,19);right.pack(side='left',fill='both',expand=True)
        text(ri,'Clasificación de materiales (CM)',13,True,bg='white').pack(anchor='w')
        stats=self.store.stats()
        text(ri,f'{stats["materials"]} materiales cargados  |  {len(self.store.material_duplicates())} códigos duplicados',11,True,
             C['blue_dark'],'white').pack(anchor='w',pady=12)
        button(ri,'Importar un CM actualizado (Word)',self._import_cm,'soft').pack(anchor='w',pady=(0,13))
        text(ri,'Duplicidades a revisar (sin modificacion automatica)',10,True,bg='white').pack(anchor='w',pady=3)
        listbox=tk.Listbox(ri,relief='flat',bg='#F6F9FD',fg=C['ink'],font=(UI_FONT,10),height=10)
        listbox.pack(fill='both',expand=True)
        for d in self.store.material_duplicates():
            listbox.insert('end',f"{d['code']}  ({d['total']})  -  {d['names'][:85]}")
        b,inner=card(parent,17);b.pack(fill='x',padx=30,pady=18)
        text(inner,'Maestros de etiquetas de estado (procedentes del Word)',12,True,bg='white').pack(anchor='w')
        text(inner,'El registro no sustituye la aprobación documental externa. Compruebe cada estado frente a su Word autorizado.',9,
             color=C['muted'],bg='white',wraplength=800).pack(anchor='w',pady=(6,10))
        for asset in self.store.status_masters():
            row=tk.Frame(inner,bg='white');row.pack(fill='x',pady=3)
            text(row,asset['name']+'  ·  '+asset['version']+'  ·  '+asset['state'],10,color=C['ink'],bg='white').pack(side='left')
            if asset['state']=='PENDING':
                button(row,'Registrar revisión',lambda kind=asset['kind']:self._approve_status(kind),'soft').pack(side='right')
        b,inner=card(parent,17);b.pack(fill='x',padx=30,pady=18)
        text(inner,'Ultimos movimientos',12,True,bg='white').pack(anchor='w',pady=(0,10))
        for a in self.store.audit_entries():
            text(inner,f"{a['at'][:19]}  |  {a['event']:<13}  |  {a['detail'][:85]}",9,color=C['muted'],bg='white').pack(anchor='w',pady=3)

    def _approve_status(self,kind):
        asset=self.store.status_master(kind)
        reviewer=simpledialog.askstring('Responsable','Responsable de la revisión del diseño '+asset['name']+':',parent=self)
        if not reviewer:return
        evidence=simpledialog.askstring('Referencia documental','Referencia de la aprobación vigente del diseño de estado:',parent=self)
        if not evidence:return
        if not messagebox.askyesno('Verificación','¿Ha cotejado físicamente la etiqueta de estado con su Word autorizado y comprobado sus requisitos?',parent=self):return
        try:
            self.store.approve_status_master(kind,reviewer,evidence)
            self.show('admin')
        except Exception as ex:messagebox.showerror('No activado',str(ex),parent=self)

    def _backup(self):
        try:
            out=self.services.backup()
            messagebox.showinfo('Copia creada',f'Archivo:\n{out}\n\nConserve esta copia en un lugar protegido.',parent=self)
        except Exception as ex:messagebox.showerror('Error en backup',str(ex),parent=self)

    def _import_cm(self):
        path=filedialog.askopenfilename(parent=self,title='CM vigente',filetypes=[('Word DOCX','*.docx')])
        if not path:return
        try:
            rows=self.services.read_cm(path)
            if not rows:raise ValueError('No hay materiales reconocibles en el documento.')
            if not messagebox.askyesno('Actualizar CM',
                  f'Se han identificado {len(rows)} filas. Se anadiran sin borrar registros anteriores.\n\nContinuar?',parent=self):return
            self.store.import_materials(rows)
            self.show('admin')
        except Exception as ex:messagebox.showerror('CM no importado',str(ex),parent=self)

    def editor(self,version_id):
        AdvancedEditor(self,version_id)

    def _quit(self):
        self.store.close();self.destroy()


class Application(WorkTkMixin,BaseApplication):
    """Work persistence wraps every legacy navigation and emission form."""


class VesselDialog(tk.Toplevel):
    """Per-container lot/PN/PB overrides, Excel paste, and editable rows."""
    def __init__(self,app,count,current):
        super().__init__(app)
        self.app=app;self.count=count
        self.result=None
        self.data={str(k):dict(v) for k,v in current.items()}
        self.title('Datos individuales por envase  |  COVEX Label Manager')
        self.geometry('1050x710');self.minsize(880,610)
        self.configure(bg=C['bg'])
        self.transient(app);self.grab_set()
        heading=tk.Frame(self,bg='white',padx=25,pady=16);heading.pack(fill='x')
        text(heading,'Datos variables por recipiente',16,True,bg='white').pack(anchor='w')
        text(heading,f'Serie de {count} recipientes. Las celdas vacías heredan el valor común de la emisión.',10,
             color=C['muted'],bg='white').pack(anchor='w',pady=4)
        body=tk.Frame(self,bg=C['bg'],padx=23,pady=18);body.pack(fill='both',expand=True)
        left,inside=card(body,15);left.pack(fill='both',expand=True)
        cols=('numero','lote','pn','pb','conservacion')
        self.tree=ttk.Treeview(inside,columns=cols,show='headings',style='Covex.Treeview',height=10)
        for col,name,width in [('numero','Nº',65),('lote','Lote',175),('pn','PN (kg)',105),('pb','PB (kg)',105),('conservacion','Condiciones específicas',360)]:
            self.tree.heading(col,text=name);self.tree.column(col,width=width,stretch=(col=='conservacion'))
        self.tree.pack(fill='both',expand=True)
        self.tree.bind('<<TreeviewSelect>>',self.choose)
        self.tree.bind('<Double-1>',self.choose)
        text(inside,'Se muestran hasta 500 envases en la tabla. Puede pegar filas de Excel para importar el resto.',9,
             color=C['muted'],bg='white').pack(anchor='w',pady=(9,0))
        edit=tk.Frame(inside,bg='white');edit.pack(fill='x',pady=(16,7))
        self.current=tk.IntVar(value=1)
        self.vars={k:tk.StringVar() for k in ('lote','pn','pb','conservacion')}
        for i,(key,name,w) in enumerate([('lote','Lote',21),('pn','PN (kg)',11),('pb','PB (kg)',11),('conservacion','Conservación',35)]):
            box=tk.Frame(edit,bg='white');box.pack(side='left',padx=(0,12))
            text(box,name,9,color=C['muted'],bg='white').pack(anchor='w')
            entry(box,self.vars[key],w).pack(anchor='w',pady=(4,0))
        actions=tk.Frame(inside,bg='white');actions.pack(fill='x',pady=(7,0))
        button(actions,'Aplicar a este envase',self.save_row,'soft').pack(side='left',padx=(0,8))
        button(actions,'Pegar tabla desde Excel',self.paste_table,'soft').pack(side='left',padx=(0,8))
        button(actions,'Borrar datos de la fila',self.clear_row,'ghost').pack(side='left')
        footer=tk.Frame(self,bg='white',padx=24,pady=13);footer.pack(fill='x')
        text(footer,'No modifica los Word maestros ni las firmas. Se conservará en el historial de la emisión.',9,
             color=C['muted'],bg='white').pack(side='left')
        button(footer,'Guardar datos',self.finish).pack(side='right',padx=(8,0))
        button(footer,'Cancelar',self.destroy,'ghost').pack(side='right')
        self.refresh()
        self.tree.selection_set('1');self.choose()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for number in range(1,min(self.count,500)+1):
            d=self.data.get(str(number),{})
            self.tree.insert('','end',iid=str(number),values=(number,d.get('lote',''),d.get('pn',''),d.get('pb',''),d.get('conservacion','')))

    def choose(self,event=None):
        choices=self.tree.selection()
        if not choices:return
        num=int(choices[0]);self.current.set(num)
        d=self.data.get(str(num),{})
        for key,var in self.vars.items():var.set(d.get(key,''))

    def save_row(self):
        num=self.current.get();item={key:var.get().strip() for key,var in self.vars.items()}
        item={k:v for k,v in item.items() if v}
        try:
            validate_vessel_masses(item,num)
        except ValueError as ex:messagebox.showerror('Pesos',str(ex),parent=self);return False
        if item:self.data[str(num)]=item
        else:self.data.pop(str(num),None)
        self.refresh();self.tree.selection_set(str(num))
        return True

    def clear_row(self):
        number=self.current.get()
        self.data.pop(str(number),None)
        self.refresh();self.tree.selection_set(str(number));self.choose()

    def paste_table(self):
        w=tk.Toplevel(self);w.title('Importar datos desde Excel');w.geometry('780x500');w.configure(bg='white')
        text(w,'Pegar una selección de Excel',15,True,bg='white').pack(anchor='w',padx=22,pady=(20,5))
        text(w,'Columnas: Número de envase | Lote | PN | PB | Conservación. Puede incluir cabecera.',10,
             color=C['muted'],bg='white').pack(anchor='w',padx=22,pady=(0,15))
        t=tk.Text(w,font=('Consolas',11),wrap='none',bg=C['soft'],fg=C['ink'],height=13)
        t.pack(fill='both',expand=True,padx=22)
        t.insert('1.0','Nº\tLote\tPN\tPB\tConservación\n1\tCV/EDR/2505-01\t0,3558\t0,7584\tEnvasar en atmosfera de nitrogeno')
        t.focus_set();t.tag_add('sel','1.0','end')
        def parse():
            try:
                data=parse_tabular_vessels(t.get('1.0','end'),self.count,self.data)
                for k,item in data.items():validate_vessel_masses(item,k)
                self.data=data;self.refresh();w.destroy()
                messagebox.showinfo('Importación','Filas incorporadas. Pulse Guardar datos para confirmar.',parent=self)
            except Exception as ex:messagebox.showerror('Tabla no válida',str(ex),parent=w)
        button(w,'Importar filas',parse).pack(anchor='e',padx=22,pady=15)
        w.transient(self)

    def finish(self):
        try:
            if not self.save_row():return
            for n,record in self.data.items():
                if int(n)>self.count:raise ValueError('Hay filas fuera de la serie actual. Revise la cantidad de recipientes.')
                validate_vessel_masses(record,n)
            self.result=self.data
            self.destroy()
        except ValueError as ex:messagebox.showerror('Datos individuales',str(ex),parent=self)


class AdvancedEditor(tk.Toplevel):
    def __init__(self,app,version_id):
        super().__init__(app)
        self.app=app;self.store=app.store;self.version_id=version_id
        self.variant_id=getattr(self.store,'selected_variant_id',None)
        self.version=self.store.resolved_design(version_id,self.variant_id) if self.variant_id else self.store.version(version_id)
        self.variant=self.store.variant(self.variant_id) if self.variant_id else None
        self.editable=self.variant['state']=='DRAFT' if self.variant else self.version['state']=='PENDING'
        self.fields=json.loads(self.version['fields_json'])
        self.crop=json.loads(self.version['crop_json'])
        self.status_area=json.loads(self.version['status_area_json'] or '[]')
        self.selected=None
        self.image=None
        self._drag=None
        self.title('Editor avanzado  |  '+self.version['name'])
        self.configure(bg=C['bg']);self.geometry('1210x850');self.minsize(960,690)
        top=tk.Frame(self,bg='white',padx=23,pady=18);top.pack(fill='x')
        text(top,'Editor visual de campos  |  '+self.version['name'],16,True,bg='white').pack(side='left')
        text(top,'EDICION DE BORRADOR' if self.editable else 'VERSION APROBADA - SOLO LECTURA',10,True,
             C['green'] if self.editable else C['orange'],'white').pack(side='right')
        area=tk.Frame(self,bg=C['bg']);area.pack(fill='both',expand=True,padx=22,pady=18)
        left,inside=card(area,12);left.pack(side='left',fill='both',expand=True,padx=(0,16))
        self.canvas=tk.Canvas(inside,background='#EFF4F9',bd=0,highlightthickness=0,cursor='crosshair')
        self.canvas.pack(fill='both',expand=True)
        self.canvas.bind('<Button-1>',self.on_select)
        self.canvas.bind('<B1-Motion>',self.on_drag)
        self.canvas.bind('<ButtonRelease-1>',self.on_up)
        self.canvas.bind('<Configure>',lambda _:self.after_idle(self.draw))
        right=tk.Frame(area,bg='white',width=335,highlightbackground=C['line'],highlightthickness=1)
        right.pack(side='left',fill='y');right.pack_propagate(False)
        prop_scroll=ScrolledFrame(right);prop_scroll.pack(fill='both',expand=True)
        props=tk.Frame(prop_scroll.body,bg='white',padx=16,pady=19);props.pack(fill='x')
        text(props,'Campos variables',13,True,bg='white').pack(anchor='w')
        self.lst=tk.Listbox(props,relief='flat',bg=C['soft'],font=(UI_FONT,10),height=6,exportselection=False,
                            selectbackground=C['cyan'],selectforeground=C['blue_dark'])
        self.lst.pack(fill='x',pady=(10,7));self.lst.bind('<<ListboxSelect>>',self.select_list)
        row=tk.Frame(props,bg='white');row.pack(fill='x',pady=(0,18))
        button(row,'+ Agregar',self.add_field,'soft').pack(side='left',padx=(0,7))
        button(row,'Quitar',self.remove_field,'danger').pack(side='left')
        text(props,'Propiedades del campo',12,True,bg='white').pack(anchor='w',pady=(0,8))
        button(props,'Recortar área de etiqueta',self.edit_crop,'ghost').pack(anchor='w',pady=(0,6))
        button(props,'Definir espacio de estado',self.edit_status_area,'soft').pack(anchor='w',pady=(0,6))
        button(props,'Anclar campo a texto Word',self.align_selected_to_word,'soft').pack(anchor='w',pady=(0,6))
        if self.version['name'].upper() in ('ACETONA','EDROFONIO'):
            button(props,'Alinear de nuevo desde Word',self.autolocate,'soft').pack(anchor='w',pady=(0,8))
        self.props={}
        items=[('key','Identificador'),('label','Nombre visible'),('x','X (mm)'),('y','Y (mm)'),
               ('w','Ancho (mm)'),('h','Alto (mm)'),('font_pt','Texto (pt origen)')]
        for k,label in items:
            r=tk.Frame(props,bg='white');r.pack(fill='x',pady=3)
            text(r,label,9,color=C['muted'],bg='white',width=19).pack(side='left')
            var=tk.StringVar();self.props[k]=var
            entry(r,var,13).pack(side='right',fill='x',expand=True)
        self.bol=tk.BooleanVar(value=False);self.req=tk.BooleanVar(value=False);self.lock=tk.BooleanVar(value=False)
        tk.Checkbutton(props,text='Negrita',variable=self.bol,bg='white',font=(UI_FONT,9)).pack(anchor='w',pady=(10,0))
        tk.Checkbutton(props,text='Obligatorio',variable=self.req,bg='white',font=(UI_FONT,9)).pack(anchor='w')
        tk.Checkbutton(props,text='Posicion bloqueada',variable=self.lock,bg='white',font=(UI_FONT,9)).pack(anchor='w')
        button(props,'Aplicar propiedades',self.apply_props,'soft').pack(fill='x',pady=(12,4))
        if self.editable:button(props,'Guardar borrador',self.save).pack(fill='x',pady=5)
        text(props,'Coordenadas en milímetros sobre el recorte; campos calculados desde las posiciones visibles del Word. El original permanece inalterado.',
             9,color=C['muted'],bg='white',wraplength=265).pack(anchor='w',pady=(10,0))
        self._refresh_list();self.draw()

    def _refresh_list(self):
        self.lst.delete(0,'end')
        for f in self.fields:
            self.lst.insert('end',f.get('label',f.get('key','?')))
        if self.selected is not None and self.selected<len(self.fields):
            self.lst.selection_set(self.selected)

    def draw(self):
        if not self.canvas.winfo_exists():return
        self.canvas.delete('all')
        cw=max(300,self.canvas.winfo_width());ch=max(400,self.canvas.winfo_height())
        try:
            v=dict(self.version);v['crop_json']=json.dumps(self.crop)
            img=self.app.services.thumbnail(v,width_px=int(cw-90))
            img.thumbnail((cw-70,ch-70))
            self.image=ImageTk.PhotoImage(img)
            x0=(cw-img.width)//2;y0=(ch-img.height)//2
            self._rect=(x0,y0,img.width,img.height)
            self.canvas.create_rectangle(x0-1,y0-1,x0+img.width+1,y0+img.height+1,fill='white',outline=C['line'])
            self.canvas.create_image(x0,y0,anchor='nw',image=self.image)
            if len(self.status_area)==4:
                ax,ay,aw,ah=self.status_area
                sx=x0+ax*img.width;sy=y0+ay*img.height
                self.canvas.create_rectangle(sx,sy,sx+aw*img.width,sy+ah*img.height,
                        outline='#AE5BC0',width=2,dash=(6,4),tags='status_region')
                self.canvas.create_text(sx+4,sy+4,anchor='nw',text='RESERVA ETIQUETA DE ESTADO',
                        fill='#85369A',font=(UI_FONT,9,'bold'))
            for idx,f in enumerate(self.fields):
                x=x0+f['x']*img.width;y=y0+f['y']*img.height
                w=f['w']*img.width;h=f['h']*img.height
                if f.get('draw') in ('baseline','continuation'):
                    font_px=float(f.get('font_pt',12))*img.width/(self.crop[2]-self.crop[0])
                    y-=font_px*1.06
                    h=max(13,font_px*1.4)
                outline=C['orange'] if idx==self.selected else C['blue']
                self.canvas.create_rectangle(x,y,x+w,y+h,outline=outline,width=2 if idx==self.selected else 1,dash=() if idx==self.selected else (4,3),tags=(f'field_{idx}','overlay'))
                self.canvas.create_text(x+3,y+3,text=f.get('key','?'),anchor='nw',fill=outline,
                                        font=(UI_FONT,9,'bold'),tags=(f'field_{idx}','overlay'))
        except Exception as ex:
            self.canvas.create_text(20,20,text=str(ex),anchor='nw',fill=C['red'])

    def select_list(self,event=None):
        if self.lst.curselection():
            self.selected=int(self.lst.curselection()[0]);f=self.fields[self.selected]
            mw=(self.crop[2]-self.crop[0])*25.4/72
            mh=(self.crop[3]-self.crop[1])*25.4/72
            for k,var in self.props.items():
                val=f.get(k,'')
                if k in ('x','w'):val=round(float(val)*mw,2)
                elif k in ('y','h'):val=round(float(val)*mh,2)
                var.set(str(val))
            self.bol.set(bool(f.get('bold')));self.req.set(bool(f.get('required')));self.lock.set(bool(f.get('locked')))
            self.draw()

    def on_select(self,event):
        items=self.canvas.find_overlapping(event.x-3,event.y-3,event.x+3,event.y+3)
        idx=None
        for item in reversed(items):
            for tag in self.canvas.gettags(item):
                if tag.startswith('field_'):idx=int(tag[6:]);break
            if idx is not None:break
        if idx is None:return
        self.selected=idx
        self.lst.selection_clear(0,'end');self.lst.selection_set(idx)
        self.select_list()
        self._drag=(event.x,event.y)

    def on_drag(self,event):
        if not self.editable or self._drag is None or self.selected is None or self.fields[self.selected].get('locked'):return
        _,_,dw,dh=self._rect
        delta_x=(event.x-self._drag[0])/dw;delta_y=(event.y-self._drag[1])/dh
        f=self.fields[self.selected]
        f['x']=round(min(max(0,f['x']+delta_x),1-f['w']),4)
        f['y']=round(min(max(0,f['y']+delta_y),1-f['h']),4)
        self._drag=(event.x,event.y)
        mw=(self.crop[2]-self.crop[0])*25.4/72
        mh=(self.crop[3]-self.crop[1])*25.4/72
        self.props['x'].set(str(round(f['x']*mw,2)))
        self.props['y'].set(str(round(f['y']*mh,2)))
        self.draw()

    def on_up(self,event):
        self._drag=None

    def edit_crop(self):
        if not self.editable:
            messagebox.showinfo('Versión aprobada','El recorte solo puede modificarse en una nueva version pendiente.',parent=self)
            return
        pop=tk.Toplevel(self);pop.title('Seleccionar zona de etiqueta');pop.configure(bg='white');pop.geometry('870x750')
        root=tk.Frame(pop,bg='white',padx=20,pady=16);root.pack(fill='both',expand=True)
        text(root,'Definir recorte sobre el PDF original',15,True,bg='white').pack(anchor='w')
        text(root,'Arrastre sobre la hoja la zona de la etiqueta que desea conservar.',10,color=C['muted'],bg='white').pack(anchor='w',pady=5)
        body=tk.Frame(root,bg='white');body.pack(fill='both',expand=True,pady=10)
        cvs=tk.Canvas(body,width=510,height=590,bg=C['soft'],highlightbackground=C['line'],highlightthickness=1)
        cvs.pack(side='left',padx=(0,20))
        right=tk.Frame(body,bg='white');right.pack(side='left',fill='y')
        img,page_rect,zoom=self.app.services.master_preview(self.version)
        photo=ImageTk.PhotoImage(img)
        origin=(int((510-img.width)/2),int((590-img.height)/2))
        current=list(self.crop)
        v={k:tk.StringVar() for k in ('x0','y0','x1','y1')}
        def set_form():
            for k,z in zip(('x0','y0','x1','y1'),current):v[k].set(str(round(z*25.4/72,1)))
        def paint():
            cvs.delete('all')
            cvs.create_image(origin[0],origin[1],anchor='nw',image=photo)
            coords=[origin[0]+current[0]*zoom,origin[1]+current[1]*zoom,
                    origin[0]+current[2]*zoom,origin[1]+current[3]*zoom]
            cvs.create_rectangle(*coords,outline=C['blue'],width=3,dash=(5,3))
        set_form()
        text(right,'Limites en mm desde la hoja',11,True,bg='white').pack(anchor='w',pady=(6,15))
        for key,label in [('x0','Izquierda'),('y0','Superior'),('x1','Derecha'),('y1','Inferior')]:
            text(right,label,9,color=C['muted'],bg='white').pack(anchor='w',pady=(7,3))
            entry(right,v[key],18).pack(anchor='w')
        def apply_entries():
            try:
                values=[float(v[k].get())*72/25.4 for k in ('x0','y0','x1','y1')]
                if not (0<=values[0]<values[2]<=page_rect.width and 0<=values[1]<values[3]<=page_rect.height):
                    raise ValueError('Los limites no son validos.')
                if (values[2]-values[0])<20 or (values[3]-values[1])<20:
                    raise ValueError('El recorte debe tener al menos 7 mm por lado.')
                current[:]=values;paint()
                return True
            except ValueError as ex:
                messagebox.showerror('Recorte',str(ex),parent=pop)
                return False
        button(right,'Aplicar coordenadas',apply_entries,'soft').pack(anchor='w',pady=15)
        def save():
            try:
                if not apply_entries():return
                self.fields,self.status_area=rebase_layout(self.fields,self.status_area,self.crop,current)
                self.crop[:]=current
                self.draw();pop.destroy()
            except Exception as ex:messagebox.showerror('Recorte',str(ex),parent=pop)
        button(right,'Aceptar recorte',save).pack(anchor='w',pady=5)
        start=[None]
        def down(e):start[0]=(e.x,e.y)
        def up(e):
            if start[0] is None:return
            a,b=start[0];start[0]=None
            coords=[(t-origin[i%2])/zoom for i,t in enumerate((a,b,e.x,e.y))]
            x0,x1=sorted((coords[0],coords[2]));y0,y1=sorted((coords[1],coords[3]))
            current[:]=[max(0,x0),max(0,y0),min(page_rect.width,x1),min(page_rect.height,y1)]
            if current[2]-current[0]<20 or current[3]-current[1]<20:return
            set_form();paint()
        cvs.bind('<Button-1>',down);cvs.bind('<ButtonRelease-1>',up)
        paint()
        pop._img_keep=photo

    def add_field(self):
        if not self.editable:return
        k=simpledialog.askstring('Nuevo campo','Clave del campo (p.ej. lote, observaciones, fecha):',parent=self)
        if not k:return
        k=k.strip().lower().replace(' ','_')
        if any(f['key']==k for f in self.fields):
            messagebox.showerror('Duplicado','Ya existe un campo con esa clave.',parent=self);return
        self.fields.append({'key':k,'label':k.replace('_',' ').title(),'x':.10,'y':.12,'w':.5,'h':.055,'font_pt':12,'required':False,'bold':False})
        self.selected=len(self.fields)-1;self._refresh_list();self.select_list();self.draw()

    def remove_field(self):
        if not self.editable or self.selected is None:return
        if messagebox.askyesno('Eliminar campo','Desea quitar este campo del borrador?',parent=self):
            self.fields.pop(self.selected);self.selected=None;self._refresh_list();self.draw()

    def apply_props(self):
        if not self.editable or self.selected is None:return
        try:
            f=self.fields[self.selected]
            vals={k:v.get().strip() for k,v in self.props.items()}
            for k in ('x','y','w','h','font_pt'):vals[k]=float(vals[k].replace(',','.'))
            mw=(self.crop[2]-self.crop[0])*25.4/72
            mh=(self.crop[3]-self.crop[1])*25.4/72
            for k in ('x','w'):vals[k]/=mw
            for k in ('y','h'):vals[k]/=mh
            if not vals['key'] or not vals['label']:raise ValueError('Identificador y nombre obligatorios')
            if vals['key']!=f['key'] and any(other['key']==vals['key'] for j,other in enumerate(self.fields) if j!=self.selected):
                raise ValueError('Clave duplicada')
            if not (0<=vals['x']<1 and 0<=vals['y']<1 and 0<vals['w']<=1 and 0<vals['h']<=1 and vals['x']+vals['w']<=1.001 and vals['y']+vals['h']<=1.001 and 3<=vals['font_pt']<=60):
                raise ValueError('Posicion, tamaños o fuente fuera del intervalo valido')
            f.update(vals);f['bold']=bool(self.bol.get());f['required']=bool(self.req.get());f['locked']=bool(self.lock.get())
            self._refresh_list();self.draw()
        except ValueError as ex:messagebox.showerror('Propiedades',str(ex),parent=self)

    def align_selected_to_word(self):
        """Anchor a field to a span extracted from the Word-converted master PDF."""
        if not self.editable:
            messagebox.showinfo('Sólo lectura','Cree una nueva revisión pendiente.',parent=self)
            return
        if self.selected is None:
            messagebox.showinfo('Campo','Seleccione primero un campo variable en el listado.',parent=self)
            return
        try:
            spans=self.app.services.master_spans(self.version)
            if not spans:raise ValueError('El PDF no contiene texto extraíble. Debe ubicarlo manualmente.')
            dlg=tk.Toplevel(self);dlg.title('Anclas del Word original');dlg.geometry('760x500');dlg.configure(bg='white')
            frame=tk.Frame(dlg,bg='white',padx=23,pady=18);frame.pack(fill='both',expand=True)
            text(frame,'Elegir el texto fijo inmediatamente anterior al campo',14,True,bg='white').pack(anchor='w')
            text(frame,'La posición se tomará del PDF convertido desde el Word, en milímetros.',9,
                 color=C['muted'],bg='white').pack(anchor='w',pady=(6,11))
            ls=tk.Listbox(frame,selectmode='browse',font=(UI_FONT,10),bg=C['soft'])
            ls.pack(fill='both',expand=True)
            for sp in spans:
                label=sp['text'].strip().replace('\n',' ')[:90]
                ls.insert('end',f"{sp['bbox'][0]*25.4/72:5.1f} mm  |  {label}")
            def apply():
                if not ls.curselection():
                    messagebox.showwarning('Elegir','Seleccione la frase de referencia.',parent=dlg);return
                sp=spans[ls.curselection()[0]]
                f=self.fields[self.selected]
                crop_w=self.crop[2]-self.crop[0];crop_h=self.crop[3]-self.crop[1]
                x=sp['bbox'][2]+1.5
                if x>=self.crop[2]:
                    messagebox.showwarning('No cabe','No queda espacio después de esa frase.',parent=dlg);return
                f['x']=round((x-self.crop[0])/crop_w,7)
                f['y']=round((sp['origin'][1]-self.crop[1])/crop_h,7)
                f['w']=round((self.crop[2]-x-4)/crop_w,7)
                f['h']=round(1.5/crop_h,7)
                f['font_pt']=sp['size']
                f['draw']='baseline'
                f['bold']='Bold' in sp['font']
                self.select_list();self.draw();dlg.destroy()
            button(frame,'Usar esta referencia',apply).pack(anchor='e',pady=12)
        except Exception as ex:
            messagebox.showerror('Anclaje Word',str(ex),parent=self)

    def autolocate(self):
        if not self.editable:
            messagebox.showinfo('Sólo lectura','Cree una nueva revisión antes de cambiar coordenadas.',parent=self)
            return
        if not messagebox.askyesno('Recalcular desde Word',
                '¿Restablecer la posición de los campos usando el Word de origen?\n\n'
                'Se perderán las posiciones modificadas en este borrador que todavía no haya guardado.',parent=self):return
        try:
            self.fields,self.status_area=self.app.services.locate_fields(self.version,self.crop)
            self.selected=None;self._refresh_list();self.draw()
        except Exception as ex:messagebox.showerror('Geometría Word',str(ex),parent=self)

    def edit_status_area(self):
        if not self.editable:
            messagebox.showinfo('Solo lectura','Modifique primero una nueva revisión pendiente.',parent=self);return
        pop=tk.Toplevel(self);pop.title('Zona para etiqueta de estado');pop.geometry('470x470');pop.configure(bg='white')
        root=tk.Frame(pop,bg='white',padx=23,pady=21);root.pack(fill='both',expand=True)
        text(root,'Espacio reservado a etiquetas de estado',14,True,bg='white').pack(anchor='w')
        text(root,'Posiciones en milímetros desde la esquina superior izquierda de la etiqueta recortada.',9,
             color=C['muted'],bg='white',wraplength=400).pack(anchor='w',pady=(8,13))
        cw=(self.crop[2]-self.crop[0])*25.4/72
        ch=(self.crop[3]-self.crop[1])*25.4/72
        orig=self.status_area if len(self.status_area)==4 else [.08,.77,.84,.15]
        values=[orig[0]*cw,orig[1]*ch,orig[2]*cw,orig[3]*ch]
        vars=[tk.StringVar(value=f'{x:.2f}') for x in values]
        for var,lab in zip(vars,('X (mm)','Y (mm)','Ancho (mm)','Alto (mm)')):
            line=tk.Frame(root,bg='white');line.pack(fill='x',pady=7)
            text(line,lab,10,color=C['muted'],bg='white').pack(side='left')
            entry(line,var,14).pack(side='right')
        def save():
            try:
                a,b,c,d=[float(v.get().replace(',','.')) for v in vars]
                if not (0<=a<cw and 0<=b<ch and c>0 and d>0 and a+c<=cw+.01 and b+d<=ch+.01):
                    raise ValueError('El espacio debe estar totalmente dentro de la etiqueta.')
                ratio=c/d
                if abs(ratio-(432.2/83.3))>.2:
                    if not messagebox.askyesno('Proporciones distintas',
                         'La zona no tiene la misma proporción que las etiquetas de estado originales. '
                         'Podría dejar bordes en blanco. ¿Guardar como borrador?',parent=pop):return
                self.status_area=[a/cw,b/ch,c/cw,d/ch]
                self.draw();pop.destroy()
            except ValueError as ex:messagebox.showerror('Medidas',str(ex),parent=pop)
        button(root,'Guardar zona',save).pack(anchor='e',pady=18)

    def save(self):
        try:
            if self.variant:
                from .variants import update_design_layout
                design=update_design_layout(json.loads(self.variant['design_json']),{'fields':self.fields,'crop':self.crop,'area':self.status_area})
                self.variant=self.store.save_variant(self.variant_id,self.variant['generation'],design,self.store.setting('operator'))
            else:self.store.replace_pending_fields(self.version_id,self.fields,self.crop,self.status_area)
            messagebox.showinfo('Guardado','Cambios guardados en la version pendiente.\nReviselos antes de activar la plantilla.',parent=self)
            self.app.show('maestro')
        except Exception as ex:messagebox.showerror('Error al guardar',str(ex),parent=self)


def start():
    from .migration_v4 import MigrationCancelled
    try:app=Application()
    except MigrationCancelled:return
    app.mainloop()

