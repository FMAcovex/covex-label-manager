"""R3A service gates and real Tk navigation, with disposable synthetic data."""
import os
import sys
import json
import pytest
from covex_label_manager.storage import Store
from covex_label_manager.services import LocalServices


def test_preparation_requires_current_document_and_approval(tmp_path):
    api=LocalServices(Store(tmp_path/'data'))
    try:
        row=next(r for r in api.library.entries() if r['version']=='00-R1')
        assert not api.emission_eligibility(row['version_id'])[0]
        api.approve(row['version_id'],'Synthetic reviewer','SYNTHETIC APPROVAL REFERENCE')
        assert api.emission_eligibility(row['version_id'])[0]
        v=api.version(row['version_id'])
        api.asset_path(v['master_pdf']).write_bytes(b'changed synthetic file')
        assert not api.emission_eligibility(row['version_id'])[0]
        assert not api.emission_eligibility(-1)[0]
    finally:api.close()

@pytest.fixture
def app():
    if sys.platform!='win32' and not os.environ.get('DISPLAY'):pytest.skip('Tk GUI requires DISPLAY (or Windows desktop).')
    from covex_label_manager.gui import Application
    value=Application();errors=[]
    value.report_callback_exception=lambda *ex:errors.append(ex)
    value.update()
    yield value
    value._quit()
    assert not errors,errors


def test_library_navigation_retains_filters_and_active_emission(app,monkeypatch):
    assert app.current_page=='maestro'
    panel=app.library_panel
    assert panel.tree['columns']==('favorite','code','name','type','version','origin','customer','country','state')
    panel.query.set('edrofonio');panel.filters['version'].set('00-R1');panel.refresh()
    row=panel.selected();assert row
    assert panel.picture.cget('image') and 'no disponible' not in panel.picture.cget('text')
    assert str(panel.emit_button['state'])=='disabled'
    app.select_emission_version(row);app.update()
    app.formvars['lote'].set('SYNTHETIC-A');app.emit_count.set('2')
    app.per_container={'2':{'lote':'SYNTHETIC-B'}}
    app.status_kind.set('aprobado');app.status_expiry.set('01/2027')
    fields=app.formvars
    for page in ('historial','admin','maestro','emitir'):
        app.show(page);app.update()
    assert app.formvars is fields and app.formvars['lote'].get()=='SYNTHETIC-A'
    assert app.emit_count.get()=='2' and app.per_container['2']['lote']=='SYNTHETIC-B'
    assert app.status_expiry.get()=='01/2027'
    assert panel.query.get()=='edrofonio' and panel.filters['version'].get()=='00-R1'
    app.select_emission_version(row);assert app.formvars is fields
    other=next(r for r in app.services.library.entries() if r['name']=='ACETONA')
    monkeypatch.setattr('covex_label_manager.gui.messagebox.askyesno',lambda *a,**kw:False)
    app.select_emission_version(other);assert app.current_version_id==row['version_id']
    monkeypatch.setattr('covex_label_manager.gui.messagebox.askyesno',lambda *a,**kw:True)
    app.select_emission_version(other);app.update()
    assert not app.per_container and all(not v.get() for v in app.formvars.values())
    assert app.status_kind.get()=='ninguna'


def test_open_editor_and_navigate_without_losing_unsaved_layout(app,monkeypatch):
    row=app.library_panel.selected();app.library_panel.open();app.update()
    assert app.current_page=='editor' and app._editor_view.winfo_exists()
    editor=app._editor_view
    editor.fields[0]['x']+=.001
    for page in ('maestro','historial','editor'):
        app.show(page);app.update()
    assert app._editor_view is editor and editor.fields[0]['x']!=json.loads(editor.version['fields_json'])[0]['x']
    app.editor(row['version_id']);assert app._editor_view is editor
    other=next(r for r in app.services.library.entries() if r['id']!=row['id'])
    monkeypatch.setattr('covex_label_manager.gui.messagebox.askyesno',lambda *a,**kw:False)
    app.editor(other['version_id']);assert app._editor_view is editor
    app.show('maestro');panel=app.library_panel
    panel.toggle_filters();panel.toggle_inspector();app.update()
    panel.toggle_filters();panel.toggle_inspector();app.update()
    assert len(panel.panes.panes())==3
    assert app.bind_all('<Control-k>')
    app._open_library_picker();app.update();assert app._quick_popup.winfo_exists()
    app._quick_popup.destroy()


def test_empty_distribution_library_and_all_pages(tmp_path,monkeypatch):
    if sys.platform!='win32' and not os.environ.get('DISPLAY'):pytest.skip('Tk GUI requires a display.')
    import covex_label_manager.storage as storage
    empty=tmp_path/'empty-resources';empty.mkdir()
    monkeypatch.setattr(storage,'resource_dir',lambda:empty)
    from covex_label_manager.gui import Application
    value=Application();errors=[];value.report_callback_exception=lambda *ex:errors.append(ex)
    try:
        value.update();assert not value.library_panel.rows
        assert str(value.library_panel.open_button['state'])=='disabled'
        for page in ('editor','emitir','centro','historial','admin','maestro'):
            value.show(page);value.update()
        assert not errors,errors
    finally:value._quit()
