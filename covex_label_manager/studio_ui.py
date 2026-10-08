"""R3A desktop shell. No persistence or rendering code."""
import tkinter as tk

import os
UI_FONT='Segoe UI' if os.name=='nt' else 'DejaVu Sans'
BG='#f3f4f6';INK='#243247';MUTED='#6b7788';BLUE='#2468db'

def build_chrome(app):
    app.main=tk.Frame(app,bg=BG);app.main.pack(fill='both',expand=True)
    app.top=tk.Frame(app.main,bg='white',height=68,highlightthickness=1,highlightbackground='#e3e7ed')
    app.top.pack(fill='x');app.top.pack_propagate(False)
    brand=tk.Frame(app.top,bg='white');brand.pack(side='left',padx=22)
    tk.Label(brand,text='COVEX',bg='white',fg=INK,font=(UI_FONT,14,'bold')).pack(anchor='w')
    tk.Label(brand,text='LABEL MANAGER',bg='white',fg=MUTED,font=(UI_FONT,8)).pack(anchor='w')
    navigation=tk.Frame(app.top,bg='white');navigation.pack(side='left',padx=24,fill='y')
    app.nav_buttons={}
    for key,label in [('maestro','Biblioteca'),('editor','Editor'),('emitir','Emisión'),('historial','Historial'),('admin','Configuración')]:
        b=tk.Button(navigation,text=label,command=lambda k=key:app.show(k),bg='white',fg=MUTED,
                    relief='flat',bd=0,padx=16,pady=10,font=(UI_FONT,10,'bold'),cursor='hand2',highlightthickness=0)
        b.pack(side='left',padx=3,pady=15);app.nav_buttons[key]=b
    identity=tk.Frame(app.top,bg='white');identity.pack(side='right',padx=20)
    tk.Label(identity,text='LOCAL · R3A',bg='white',fg=MUTED,font=(UI_FONT,8)).pack(anchor='e')
    app.top_user=tk.Label(identity,text='',bg='white',fg=INK,font=(UI_FONT,9));app.top_user.pack(anchor='e')
    app.workspace=tk.Frame(app.main,bg=BG);app.workspace.pack(fill='both',expand=True)
    status=tk.Frame(app.main,bg='white',height=25);status.pack(fill='x')
    tk.Label(status,text='Studio  /  R3A para revisión',bg='white',fg=MUTED,font=(UI_FONT,8)).pack(side='left',padx=18,pady=4)
    tk.Label(status,text='Ctrl+K  Buscar etiqueta  ·  Datos locales',bg='white',fg=MUTED,font=(UI_FONT,8)).pack(side='right',padx=18)
