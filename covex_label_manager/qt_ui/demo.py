"""Private disposable data. Never loads configured COVEX_LABEL_DATA or resources."""
import tempfile
from pathlib import Path
import fitz
from covex_label_manager.storage import Store
from covex_label_manager.qt_transition import TransitionServices

FIELDS=[dict(key=key,label=label,x=x,y=y,w=w,h=.07,font_pt=12,bold=False,required=False,locked=False)
        for key,label,x,y,w in [('lote','Lote',.12,.46,.72),('pn','Peso neto',.12,.62,.31),
                               ('pb','Peso bruto',.55,.62,.31),('numero','Envase / total',.12,.79,.5)]]

class DemoSession:
    def __init__(self):
        self.temp=tempfile.TemporaryDirectory(prefix='covex_qt_fictional_')
        self.root=Path(self.temp.name)
        self.services=TransitionServices(Store(self.root/'demo-data',seed=False))
        self.initial_id=None
        names=['Solución Alfa','Granulado Beta','Reactivo Gamma','Producto Delta','Mezcla Sigma',
               'Extracto Omega','Solución Épsilon','Granulado Zeta','Reactivo Eta','Producto Theta',
               'Mezcla Iota','Extracto Kappa']
        for n,name in enumerate(names,1):
            source=self.root/f'fictional-{n}.pdf'
            with fitz.open() as pdf:
                page=pdf.new_page(width=432,height=300)
                page.draw_rect(fitz.Rect(12,12,420,288),color=(.13,.19,.2),width=.8)
                page.draw_rect(fitz.Rect(12,12,420,86),fill=(.09,.22,.25),color=None)
                page.insert_text((30,38),'DEMO / DATOS FICTICIOS',fontsize=9,color=(.7,.85,.84))
                page.insert_text((30,66),name.upper(),fontsize=19,fontname='hebo',color=(1,1,1))
                page.insert_text((30,111),'DEM-'+str(n).zfill(3)+'  /  Ejemplo visual sin uso productivo',fontsize=10)
                for title,x,y in [('LOTE',30,132),('PESO NETO',30,181),('PESO BRUTO',236,181),('ENVASE / TOTAL',30,233)]:
                    page.insert_text((x,y),title,fontsize=8,color=(.38,.47,.48))
                page.insert_text((30,279),'FUENTE SINTETICA / NO ES UN DOCUMENTO COVEX',fontsize=7,color=(.44,.52,.53))
                pdf.save(source)
            vid=self.services.add_label(name+' · Demo',f'DEM-{n:03}',
                'Materias de ejemplo' if n%2 else 'Productos de ejemplo','',
                'CLIENTE' if n%3==0 else 'COVEX','Cliente ficticio Norte' if n%3==0 else '',
                '00',source,None,[0,0,432,300],FIELDS,'Fuente completamente ficticia para evaluación visual.')
            version=self.services.version(vid)
            self.services.library.update_metadata(version['label_id'],{'family':'Familia sintética A' if n%2 else 'Familia sintética B',
                'type':'Etiqueta de recipiente','country':'País de ejemplo','language':'Español (demo)',
                'product':name+' ficticio'},'Generador sintético de la prueba visual')
            if n%4!=0:self.services.approve(vid,'Revisor ficticio','APROBACION FICTICIA DEMO')
            if n in (1,3):
                vid=self.services.clone_version(vid,'01','Revisión ficticia para probar selector documental')
                if n==3:self.services.approve(vid,'Revisor ficticio','SEGUNDA APROBACION FICTICIA DEMO')
            if n==1:self.initial_id=vid
        row=next(r for r in self.services.library.entries() if r['version_id']==self.initial_id)
        self.services.library.favorite(row)
    def close(self):
        self.services.close()
        self.temp.cleanup()
