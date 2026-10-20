"""Real widget/session verification, using only disposable fictional data."""
import json
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QMessageBox
from .functional import FunctionalWindow

def exercise(w,app,captures=None):
    checks=[]
    def check(value,name):
        print(('PASS' if value else 'FAIL')+': '+name,flush=True)
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
    check(w.prepare_button.grab().toImage().pixelColor(w.prepare_button.width()//2,5).name()=='#e7ecee','Pending primary uses disabled neutral background')
    snap('R3A_Qt_Biblioteca.png')
    snap('R3A_Qt_Emision_Pendiente_Bloqueada.png')
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
    check(not w.save_button.isEnabled(),'Clean pending draft cannot save')
    check(w.save_button.grab().toImage().pixelColor(w.save_button.width()//2,5).name()=='#e7ecee','Clean draft save uses disabled neutral background')
    check('Sin cambios' in w.save_button.toolTip(),'Clean save explains unavailable state')
    check('Vista' in w.canvas_zoom_label.text() and 'No indica tamaño físico' in w.canvas_zoom_label.toolTip(),'Editor zoom explicitly visual, not print scale')
    snap('R3A_Qt_Editor.png')
    snap('R3A_Qt_Guardado_Sin_Cambios.png')
    w.editor_advanced_button.setChecked(True);w.toggle_editor_advanced();settle();check(w.editor_advanced.isVisible(),'Advanced tools and properties open')
    snap('R3A_Qt_Editor_Ajuste_Avanzado.png')
    w.editor_advanced_button.click()
    original=json.loads(w.api.version(w.current_editor_id)['fields_json'])
    w.spins['x'].setValue(w.spins['x'].value()+1);settle();check(w.dirty,'Changed properties mark active work dirty')
    check(w.save_button.isEnabled(),'Dirty pending draft can save')
    check(w.save_button.grab().toImage().pixelColor(w.save_button.width()//2,5).name()=='#147d71','Enabled save retains approved primary appearance')
    snap('R3A_Qt_Guardado_Cambios_Pendientes.png')
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
    snap('R3A_Qt_Emision_Vigente_Habilitada.png')
    check(w.prepare_button.grab().toImage().pixelColor(w.prepare_button.width()//2,5).name()=='#147d71','Enabled production retains primary appearance')
    w.open_editor();settle();check(not w.save_button.isEnabled(),'Approved save disabled')
    snap('R3A_Qt_Editor_Vigente_Solo_Lectura.png')
    check(not w.spins['x'].isEnabled() and not w.key_input.isEnabled(),'Approved editor read-only')
    w.navigate('library');w.preview.fit();settle()
    check(abs(w.preview.transform().m11()-w.preview.transform().m22())<.0001,'Preview proportional')
    check(w.preview.mapToScene(w.preview.viewport().rect()).boundingRect().contains(w.preview.scene().items()[0].sceneBoundingRect()),'Fit includes complete document')
    check('Vista' in w.preview.zoom_label.text() and 'No indica tamaño físico' in w.preview.zoom_label.toolTip(),'Library zoom explicitly visual, not print scale')
    retired=next(r['version_id'] for r in w.rows if r['state']=='RETIRED')
    w.select_version(retired);settle()
    check(not w.prepare_button.isEnabled() and not w.test_button.isEnabled(),'Retired revision blocks production and test')
    snap('R3A_Qt_Emision_Retirada_Bloqueada.png')
    w.open_editor();settle();check(not w.save_button.isEnabled(),'Retired save disabled')
    snap('R3A_Qt_Editor_Retirada_Solo_Lectura.png')
    w.navigate('library');w.select_version(approved)
    w.choose_column(6,True);check(not w.table.isColumnHidden(6),'Optional metadata columns accessible');w.reset_columns()
    w.navigate('history');check(w.stack.currentWidget() is w.history_page,'Native history replaces the previous companion-only section')
    w.navigate('settings');settle()
    check(w.stack.currentWidget() is w.settings_page and w.settings_tabs.count()==3
          and w.settings_general_tabs.count()==2
          and w.settings_documents_tabs.count()==3
          and w.settings_admin_tabs.count()==2,
          'Native settings groups the preserved functions into three clear areas, not Tkinter')
    check(w.settings_data_path.isReadOnly() and w.settings_data_path.text()==w.api.location(),
          'Settings exposes only a read-only data location')
    check(w.settings_counts['labels'].text()==str(w.api.stats()['labels']),
          'Settings counters are read from the existing service')
    snap('R3D_Qt_Configuracion_Resumen.png')
    w.open_settings_section(0,1);settle();snap('R3D_Qt_Configuracion_Datos.png')
    w.open_settings_section(1,1);settle();snap('R3D_Qt_Configuracion_CM.png')
    w.open_settings_section(1,2);settle();snap('R3D_Qt_Configuracion_Estados.png')
    w.open_settings_section(2,0);settle();snap('R3D_Qt_Configuracion_Auditoria.png')
    dialog=QMessageBox(QMessageBox.Icon.Information,'Confirmación de prueba',
        'Vista de ejemplo del cuadro emergente. Solo contiene datos ficticios.',
        QMessageBox.StandardButton.Ok,w)
    dialog.show();settle()
    from PySide6.QtGui import QPalette
    check(dialog.palette().color(QPalette.ColorRole.Window).lightness()>150,
          'Dialog uses a light background even under a dark OS theme')
    if captures:assert dialog.grab().save(str(captures/'R3D_Qt_Cuadro_Emergente_Claro.png'))
    dialog.close();dialog.deleteLater()
    w.navigate('library')
    w.quick_search();settle();check(w.search.hasFocus(),'Ctrl+K focuses search')
    QTest.keyClick(w,Qt.Key.Key_K,Qt.KeyboardModifier.ControlModifier);settle();check(w.stack.currentWidget() is w.library,'Ctrl+K actual shortcut')
    w.reset_filters();w.select_version(w.session.initial_id);w.resize(1100,760);settle()
    check(all(w.nav[k].text()==title and title in w.nav[k].toolTip() and ('nativas Qt' if k=='history' else 'Función nativa Qt') in w.nav[k].toolTip() and w.nav[k].accessibleName()==title for k,title in [('history','Historial'),('settings','Configuración')]),'Compact navigation retains labels, tooltips and accessible names')
    check(not w.inspector.isVisible(),'Compact inspector folded');snap('R3A_Qt_Compacta.png')
    w.inspector_button.click();settle();check(w.inspector.isVisible(),'Compact inspector can reopen');w.inspector_button.click()
    resolution=[]
    for width,height in ((1920,1080),(1366,768)):
        scale=w.screen().devicePixelRatio();target=(int(width/scale)-16,int(height/scale)-44)
        w.resize(*target);settle();check(w.width()<=target[0] and w.height()<=target[1],f'Library within {width}x{height} bounds')
        check(all(not w.table.isColumnHidden(c) for c in (1,2,4,8)),'Priority columns retained')
        w.open_editor();settle();check(w.width()<=target[0] and w.height()<=target[1],'Editor within compact bounds')
        snap(f'R3A_Qt_{width}x{height}_Editor.png');resolution.append({'target':[width,height],'actual_logical':[w.width(),w.height()],'scale':scale});w.navigate('library')
        w.navigate('settings');settle()
        check(w.settings_tabs.isVisible() and w.settings_page.isEnabled(),
              'Settings controls remain available at '+str(width)+'x'+str(height))
        snap(f'R3D_Qt_Configuracion_{width}x{height}.png')
        w.navigate('library')
    from .advanced_checks import exercise_advanced
    checks.extend(exercise_advanced(w,app,captures))
    return {'ok':True,'fictional':True,'count':len(checks),'checks':checks,'resolution':resolution,'native_windows_monitor_acceptance':False}

