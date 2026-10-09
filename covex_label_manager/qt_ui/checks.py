"""Real widget/session verification, using only disposable fictional data."""
import json
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QMessageBox
from .functional import FunctionalWindow

def exercise(w,app,captures=None):
    checks=[]
    def check(value,name):
        assert value,name
        checks.append(name)
    def settle():
        for _ in range(3):app.processEvents();QTest.qWait(25)
    def snap(name):
        settle()
        if captures:captures.mkdir(parents=True,exist_ok=True);assert w.grab().save(str(captures/name))
    w.resize(1500,980);settle()
    check(w.table.rowCount()==14,'Library reads existing services')
    check(w.advanced.isHidden(),'Advanced filters closed by default')
    check(not w.prepare_button.isEnabled() and w.test_button.isEnabled(),'Pending: test available, production disabled')
    snap('R3A_Qt_Biblioteca.png')
    w.toggle_advanced();w.remember_filters.setChecked(True);w.save_filter_preference()
    check(w.api.filter_preferences()==(True,True),'Panel preference persisted through existing settings')
    w.filters['family'].setCurrentIndex(1);settle();w.toggle_advanced()
    check('Familia:' in w.active_filter_text.text(),'Active advanced filters visible while closed')
    w.reset_filters();w.select_version(w.session.initial_id)
    w.search.setText('Granulado');settle();check(w.table.rowCount()==2,'Dynamic search supports small result set')
    snap('R3A_Qt_Pocos_Resultados.png')
    check(not w.selection_help.findChildren(__import__('PySide6.QtWidgets',fromlist=['QPushButton']).QPushButton),'Small-result strip does not duplicate inspector actions')
    w.search.setText('ZZ-NOT-FOUND');settle();check(not w.inspector.isEnabled(),'Empty state disables inspector')
    w.reset_filters();w.select_version(w.session.initial_id)
    previous=w.row['favorite'];w.favorite();check(w.row['favorite']!=previous,'Favorite persisted');w.favorite()
    w.sort_table(2);w.select_version(w.session.initial_id);check(w.row['version_id']==w.session.initial_id,'Sorting preserves identity')
    w.open_editor();settle();check(w.current_editor_id==w.session.initial_id,'Editor opens selected revision')
    snap('R3A_Qt_Editor.png')
    w.editor_advanced_button.click();settle();check(w.editor_advanced.isVisible(),'Advanced tools and properties open')
    snap('R3A_Qt_Editor_Ajuste_Avanzado.png')
    w.editor_advanced_button.click()
    original=json.loads(w.api.version(w.current_editor_id)['fields_json'])
    w.spins['x'].setValue(w.spins['x'].value()+1);settle();check(w.dirty,'Changed properties mark active work dirty')
    value=w.fields[0]['x'];w.navigate('library');w.navigate('editor');settle();check(w.fields[0]['x']==value,'Navigation retains unsaved work')
    check(json.loads(w.api.version(w.current_editor_id)['fields_json'])==original,'No autosave')
    check(w.save_work(),'Explicit draft save works')
    check(json.loads(w.api.version(w.current_editor_id)['fields_json'])[0]['x']==value,'Editor save persists through existing service')
    check(not w.dirty,'Saved work no longer dirty')
    w.navigate('library');w.set_mode('recent');check(any(r['version_id']==w.session.initial_id for r in w.rows),'Recent opened revision persisted')
    w.set_mode('all');w.select_version(w.session.initial_id)
    approved=next(v['id'] for v in w.api.versions(w.row['id']) if v['state']=='APPROVED')
    w.revision.setCurrentIndex(w.revision.findData(approved));settle()
    check(w.prepare_button.isEnabled() and w.test_button.isEnabled(),'Approved: production and explicit test separate')
    w.open_editor();settle();check(not w.spins['x'].isEnabled() and not w.key_input.isEnabled(),'Approved editor read-only')
    w.navigate('library');w.preview.fit();settle()
    check(abs(w.preview.transform().m11()-w.preview.transform().m22())<.0001,'Preview proportional')
    check(w.preview.mapToScene(w.preview.viewport().rect()).boundingRect().contains(w.preview.scene().items()[0].sceneBoundingRect()),'Fit includes complete document')
    w.choose_column(6,True);check(not w.table.isColumnHidden(6),'Optional metadata columns accessible');w.reset_columns()
    w.navigate('history');check('versión Tkinter' in w.catalog_text.text(),'Unmigrated section explicitly identified')
    w.quick_search();settle();check(w.search.hasFocus(),'Ctrl+K focuses search')
    QTest.keyClick(w,Qt.Key.Key_K,Qt.KeyboardModifier.ControlModifier);settle();check(w.stack.currentWidget() is w.library,'Ctrl+K actual shortcut')
    w.reset_filters();w.select_version(w.session.initial_id);w.resize(1100,760);settle()
    check(not w.inspector.isVisible(),'Compact inspector folded');snap('R3A_Qt_Compacta.png')
    w.inspector_button.click();settle();check(w.inspector.isVisible(),'Compact inspector can reopen');w.inspector_button.click()
    resolution=[]
    for width,height in ((1920,1080),(1366,768)):
        scale=w.screen().devicePixelRatio();target=(int(width/scale)-16,int(height/scale)-44)
        w.resize(*target);settle();check(w.width()<=target[0] and w.height()<=target[1],f'Library within {width}x{height} bounds')
        check(all(not w.table.isColumnHidden(c) for c in (1,2,4,8)),'Priority columns retained')
        w.open_editor();settle();check(w.width()<=target[0] and w.height()<=target[1],'Editor within compact bounds')
        snap(f'R3A_Qt_{width}x{height}_Editor.png');resolution.append({'target':[width,height],'actual_logical':[w.width(),w.height()],'scale':scale});w.navigate('library')
    return {'ok':True,'fictional':True,'count':len(checks),'checks':checks,'resolution':resolution,'native_windows_monitor_acceptance':False}
