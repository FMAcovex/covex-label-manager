"""Capture the real R3A GUI with fictional documents only; needs a display."""
import sys,os,tempfile,time
from pathlib import Path
from PIL import ImageGrab
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from synthetic_fixtures import activate_for_script
fixtures_temp=activate_for_script();fixtures=Path(fixtures_temp.name)
os.environ['COVEX_LABEL_DATA']=tempfile.mkdtemp(prefix='covex_r3a_capture_')
from covex_label_manager.gui import Application
out=Path('test-results/r3a');out.mkdir(parents=True,exist_ok=True)
app=Application();errors=[];app.report_callback_exception=lambda *ex:errors.append(ex)
try:
    app.geometry('1500x920+0+0');app.title('COVEX Label Manager · R3A · Datos ficticios de prueba')
    for n in range(1,7):
        vid=app.services.add_label(f'DEMO — Producto ficticio {n:02}',f'DEMO-{n:03}','Categoría de prueba','','CLIENTE' if n%2 else 'COVEX','Cliente ficticio' if n%2 else '',f'{n:02}',fixtures/'ACETONA_MASTER_00.pdf',None,[0,0,595,842],[],'Documento sintético para comprobar interfaz')
        v=app.services.version(vid)
        app.services.library.update_metadata(v['label_id'],{'type':'Ejemplo sintético','country':'País ficticio','family':'Familia de prueba'},'Fuente sintética de pruebas')
        if n%2:app.services.approve(vid,'Responsable ficticio','SYNTHETIC-REF')
    app.library_panel.refresh_facets();app.library_panel.refresh();app.update()
    app.top_user.configure(text='DATOS FICTICIOS DE PRUEBA')
    def capture(name):
        for _ in range(4):app.update();time.sleep(.08)
        x,y=app.winfo_rootx(),app.winfo_rooty()
        ImageGrab.grab(bbox=(x,y,x+app.winfo_width(),y+app.winfo_height()),xdisplay=os.environ['DISPLAY']).save(out/name)
    panel=app.library_panel
    row=next(r for r in panel.rows.values() if r['name']=='EDROFONIO' and r['version']=='00-R1')
    panel.tree.selection_set(str(row['version_id']));panel.preview()
    capture('R3A_Biblioteca.png')
    panel.query.set('demo');panel.filters['origin'].set('CLIENTE');panel.refresh();capture('R3A_Filtros.png')
    panel.reset();panel.tree.selection_set(str(row['version_id']));panel.preview();panel.open();app.update()
    capture('R3A_Editor_Existente.png')
    app.show('maestro');app.geometry('1100x700+0+0');app.update();capture('R3A_Compacta.png')
    assert not errors,errors
    print('R3A real GUI captures completed with synthetic fixtures only')
finally:app._quit()
