"""Executable interaction checks on real Qt widgets and temporary services."""
import json
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

def exercise(w,app,captures=None):
    steps=[]
    def check(condition,name):
        assert condition,name
        steps.append(name)
    def settle():
        for _ in range(3):app.processEvents();QTest.qWait(30)
    def snap(name):
        settle()
        if captures:
            captures.mkdir(parents=True,exist_ok=True)
            assert w.grab().save(str(captures/name))
    w.resize(1500,940);settle()
    check(w.table.rowCount()==14,'14 fictional revisions loaded by existing LibraryService')
    check(w.row['version_id']==w.session.initial_id,'Pending initial revision selected')
    snap('Industrial_Biblioteca.png')
    w.advanced_button.click();settle();check(w.advanced.isVisible(),'Advanced filters expand')
    w.search.setText('granulado');w.filters['origin'].setCurrentIndex(w.filters['origin'].findData('COVEX'));settle()
    check(w.table.rowCount()>0 and all('Granulado' in r['name'] and r['origin']=='COVEX' for r in w.rows),'Search and combined filters')
    snap('Industrial_Filtros.png')
    w.search.setText('NO-SUCH-FICTIONAL-LABEL');settle();check(w.table.rowCount()==0 and not w.inspector.isEnabled(),'Empty results handled')
    w.reset_filters();w.select_version(w.session.initial_id);w.sort_table(2);w.select_version(w.session.initial_id)
    check(w.row['version_id']==w.session.initial_id,'Selection identity remains correct after sort')
    before=w.row['favorite'];w.favorite();check(w.row['favorite']!=before,'Favorites use existing service');w.favorite()
    w.set_mode('favorites');check(w.table.rowCount()>0,'Favorites view');w.set_mode('all');w.select_version(w.session.initial_id)
    original=json.loads(w.api.version(w.session.initial_id)['fields_json'])
    w.open_editor();settle()
    check(w.stack.currentWidget() is w.editor,'Editor opens on selected revision')
    snap('Industrial_Editor.png')
    old=w.fields[0]['x'];w.spins['x'].setValue(w.spins['x'].value()+2);settle()
    check(w.fields[0]['x']>old,'Properties change temporary layout')
    item=w.field_items[0];old=w.fields[0]['y'];item.setPos(item.pos().x(),item.pos().y()+10);settle()
    check(w.fields[0]['y']>old,'Canvas movement updates properties')
    w.locked.setChecked(True);settle()
    check(w.fields[0]['locked'],'Position lock toggles in demo')
    changed=w.fields[0]['x'];w.navigate('library');w.navigate('editor');settle()
    check(w.fields[0]['x']==changed,'Navigation preserves temporary editor state')
    check(json.loads(w.api.version(w.session.initial_id)['fields_json'])==original,'Controlled template never modified')
    w.navigate('library');w.set_mode('recent');check(any(r['version_id']==w.session.initial_id for r in w.rows),'Recents use existing service')
    w.set_mode('all');w.select_version(w.session.initial_id)
    index=w.revision.findData(next(v['id'] for v in w.api.versions(w.row['id']) if v['state']=='APPROVED'))
    w.revision.setCurrentIndex(index);settle();check(w.row['state']=='APPROVED','Revision selector changes document')
    w.open_editor();settle();check(not w.spins['x'].isEnabled(),'Approved revision is read-only')
    w.preview.zoom(1.2);w.preview.fit();check(bool(w.preview.scene().items()),'Real PDF preview and zoom')
    w.navigate('emission');check(w.stack.currentWidget() is w.catalog,'Unmigrated functions explicitly identified')
    w.quick_search();settle();check(w.search.hasFocus(),'Ctrl+K search target')
    QTest.keyClick(w,Qt.Key.Key_K,Qt.KeyboardModifier.ControlModifier);settle()
    check(w.stack.currentWidget() is w.library,'Ctrl+K shortcut works')
    w.reset_filters();w.select_version(w.session.initial_id)
    if w.advanced.isVisible():w.advanced_button.click()
    w.resize(1100,760);settle();check(w.table.isColumnHidden(7),'Responsive secondary columns')
    snap('Industrial_Compacta.png')
    return {'ok':True,'checks':steps,'fictional_only':True,'core_modified':False,'count':len(steps)}
