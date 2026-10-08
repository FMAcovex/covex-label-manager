"""Graphical verification on disposable local data. Requires DISPLAY."""
import os,tempfile,sys
from pathlib import Path
from PIL import ImageGrab
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from synthetic_fixtures import activate_for_script
_synthetic=activate_for_script()
os.environ['COVEX_LABEL_DATA']=tempfile.mkdtemp(prefix='covex_r1_r2_gui_')
from covex_label_manager.gui import Application,AdvancedEditor,VesselDialog
Path('test-results').mkdir(exist_ok=True)
app=Application()
errors=[]
app.report_callback_exception=lambda *ex:errors.append(ex)
try:
    app.update()
    row=next(r for r in app.services.library.entries() if r['version']=='00-R1')
    app.select_emission_version(row);app.update()
    app.emit_count.set('2');app._use_master_size()
    for k,v in {'lote':'CV/EDR/TEST-001','pn':'0,1000','pb':'0,2000','conservacion':'Envasar en atmosfera de nitrogeno'}.items():app.formvars[k].set(v)
    app.preview_issue();app.update()
    assert app.preview_warning.cget('text').startswith('Previsualizacion'),app.preview_warning.cget('text')
    app.show('maestro');app.update()
    panel=app.library_panel
    panel.tree.selection_set(str(row['version_id']));panel.preview();app.update()
    app.update()
    x,y=app.winfo_rootx(),app.winfo_rooty()
    ImageGrab.grab(bbox=(x,y,x+app.winfo_width(),y+app.winfo_height()),xdisplay=os.environ.get('DISPLAY')).save('test-results/Captura_Maestro_R2.png')
    panel.toggle_filters();app.update()
    ImageGrab.grab(bbox=(x,y,x+app.winfo_width(),y+app.winfo_height()),xdisplay=os.environ.get('DISPLAY')).save('test-results/Captura_Filtros_R2.png')
    panel.query.set('edrofonio');panel.refresh();assert len(panel.rows)==2
    panel.filters['version'].set('00-R1');panel.refresh();assert len(panel.rows)==1
    panel.favorite();panel.view.set('favorites');panel.refresh();assert len(panel.rows)==1
    panel.reset();panel.tree.selection_set(str(row['version_id']));app._master_compare();app.update()
    for w in app.winfo_children():
        if w.winfo_class()=='Toplevel':w.destroy()
    panel.open();app.update()
    for w in app.winfo_children():
        if w.winfo_class()=='Toplevel':w.destroy()
    assert app.bind_all('<Control-k>')
    app._open_library_picker();app.update();assert app._quick_popup.winfo_exists()
    app._quick_popup.destroy()
    editor=AdvancedEditor(app,row['version_id']);editor.update();editor.selected=0;editor.select_list();editor.draw();editor.update()
    spans=app.services.master_spans(editor.version);assert spans
    image,rect,zoom=app.services.master_preview(editor.version);assert rect.width>0 and image.height>0
    fields,area=app.services.locate_fields(editor.version,editor.crop);assert fields==editor.fields
    editor.destroy()
    dlg=VesselDialog(app,2,{});dlg.update();dlg.destroy()
    for name in ('centro','historial','admin','inicio'):
        app.show(name);app.update()
    assert not errors,errors
    print('Graphical R1/R2 smoke passed')
finally:app._quit()
