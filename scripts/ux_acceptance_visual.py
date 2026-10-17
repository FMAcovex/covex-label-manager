"""Synthetic before/after acceptance views; never opens the user's data root."""
import argparse,os,sys,math,json,hashlib,subprocess
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root',type=Path,default=Path(__file__).resolve().parents[1])
parser.add_argument('--baseline',action='store_true')
parser.add_argument('--width',type=int,default=1366);parser.add_argument('--height',type=int,default=768)
parser.add_argument('--output-dir',type=Path,default=Path('test-results/acceptance-visual'))
parser.add_argument('--svg-dir',type=Path)
a=parser.parse_args();sys.path.insert(0,str(a.source_root.resolve()))
revision=subprocess.run(['git','-C',str(a.source_root),'rev-parse','HEAD'],capture_output=True,text=True)
source_revision=revision.stdout.strip() if revision.returncode==0 else ('46d3eab93381a81bae47f04ffe367334c8f16709' if a.baseline else 'unversioned')
source_hash=hashlib.sha256(b''.join(p.read_bytes() for p in sorted((a.source_root/'covex_label_manager').rglob('*.py')))).hexdigest()
from PySide6.QtCore import QSize,QPoint,Qt
from PySide6.QtWidgets import QApplication,QMessageBox,QDialog,QAbstractButton
from PySide6.QtGui import QPalette,QColor,QPainter
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtTest import QTest
from covex_label_manager.qt_ui.demo import DemoSession
from covex_label_manager.qt_ui.functional import FunctionalWindow
from covex_label_manager.qt_ui.controlled_import import ControlledImportDialog
from covex_label_manager.qt_ui.responsive import install_translation
import fitz
scale=float(os.environ.get('QT_SCALE_FACTOR','1'));key=f'{a.width}x{a.height}_{scale:g}'
out=a.output_dir/('before' if a.baseline else 'after')/key;out.mkdir(parents=True,exist_ok=True)
app=QApplication([]);app.setStyle('Fusion');install_translation(app)
palette=app.palette()
for role,color in [('Window','#F3F6F7'),('WindowText','#223B40'),('Base','#FFFFFF'),('Text','#223B40'),('Button','#FFFFFF'),('ButtonText','#223B40'),('Highlight','#147D71'),('HighlightedText','#FFFFFF')]:
    palette.setColor(getattr(QPalette.ColorRole,role),QColor(color))
app.setPalette(palette)
session=DemoSession();session.fictional=True;api=session.services
w=FunctionalWindow(session);w.poll_timer.stop();w.legacy_timer.stop()
logical=(math.floor(a.width/scale),math.floor(a.height/scale)-40)
w.resize(*logical);w.show();app.processEvents();records=[];dialogs=[]

def capture(name,widget):
    app.processEvents()
    if hasattr(widget,'fit_available'):widget.fit_available(QSize(logical[0]-24,logical[1]-24));app.processEvents()
    for _ in range(3):app.processEvents()
    footer_controls=[]
    if hasattr(widget,'wizard_footer'):
        for control in widget.wizard_footer.findChildren(QAbstractButton):
            if not control.isVisibleTo(widget):continue
            position=control.mapTo(widget,QPoint())
            assert 0<=position.y() and position.y()+control.height()<=widget.height(),(name,control.text(),position.y(),control.height(),widget.height())
            footer_controls.append(dict(text=control.text(),y=position.y(),height=control.height()))
    image=widget.grab();path=out/(name+'.png');assert image.save(str(path))
    visible=[f for f in getattr(widget,'footer_widgets',[]) if f.isVisibleTo(widget)]
    assert widget.width()<=logical[0] and widget.height()<=logical[1],name
    assert all(f.mapTo(widget,f.rect().bottomRight()).y()<widget.height() for f in visible),name
    if a.svg_dir and key in ('1366x768_1','1366x768_1.5','1920x1080_1'):
        svg=a.svg_dir/('before' if a.baseline else 'after')/key/(name+'.svg');svg.parent.mkdir(parents=True,exist_ok=True)
        gen=QSvgGenerator();gen.setFileName(str(svg));gen.setSize(widget.size());gen.setViewBox(widget.rect());gen.setTitle('SYNTHETIC ONLY · '+name)
        painter=QPainter(gen);widget.render(painter,QPoint());painter.end()
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
    records.append(dict(view=name,size=[widget.width(),widget.height()],dpr=widget.devicePixelRatioF(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),footer_reachable=True,footer_controls=footer_controls))
    print(key,name,flush=True)

def wait_preview():
    for _ in range(800):
        QTest.qWait(25)
        if w.work_preview and w.preview_task is None and not w.preview_timer.isActive():return
    raise AssertionError(w.emission_pdf.note.text())

try:
    folder=session.root/'SYNTHETIC Categoria sugerida';folder.mkdir()
    for n in range(3):
        with fitz.open() as pdf:
            pdf.new_page(width=400,height=300).insert_text((40,70),f'SYNTHETIC LABEL {n} - NO DOCUMENTOS REALES')
            pdf.save(folder/f'SYNTHETIC Etiqueta {n} 00.pdf')
    d=ControlledImportDialog(w,api,folder);dialogs.append(d);d.show()
    if a.baseline:capture('01-importador',d)
    else:
        capture('01-carpeta',d);d.next_page();capture('02-identidades',d)
        d.actions[0].setCurrentIndex(1);d.table.item(0,5).setText('SYNTHETIC-CODE');d.confirm_identity.setChecked(True)
        d.table.selectRow(0)
        real_exec=QDialog.exec
        def preview_dialog(dialog):
            dialog.show();capture('03-origen-previo',dialog);dialog.reject();return QDialog.DialogCode.Rejected
        QDialog.exec=preview_dialog
        try:d.preview_selected()
        finally:QDialog.exec=real_exec
        real_question=QMessageBox.question
        try:
            QMessageBox.question=lambda *args,**kwargs:QMessageBox.StandardButton.Yes
            d.start();d.timer.stop();d.step();d.timer.stop();d.finish()
        finally:QMessageBox.question=real_question
        assert d.ok==1 and api.version(d.imported[0]['version_id'])['state']=='PENDING'
        capture('04-resumen-pendiente',d)
        w.refresh();w.select_version(d.imported[0]['version_id']);w.open_editor();capture('05-editor-importado',w)
    d.hide()
    approved=next(r['version_id'] for r in api.library.entries() if r['state']=='APPROVED')
    work=api.work.create(approved,name='SYNTHETIC mass and preview')
    work=api.work.save(work['uid'],work['generation'],{'values':{'lote':'SYNTHETIC-MASS','pn':'350 g','pb':'500000 mg'}})
    w.load_emission_work(work['uid']);w.navigate('emission')
    if a.baseline:
        w.refresh_emission_review();capture('06-emision-masas',w)
    else:
        capture('06-emision-actualizando',w);wait_preview();capture('07-emision-actualizada',w)
        w.emission_panel.value_inputs['pn'].setText('SYNTHETIC invalid');w.emission_panel.changed();QTest.qWait(800)
        assert not w.native_issue.isEnabled() and w.work_preview is None
        capture('08-emision-errores',w)
        w.emission_panel.value_inputs['pn'].setText('350 g');w.emission_panel.changed();wait_preview()
        w.emission_panel.tabs.setCurrentIndex(1);capture('09-recipientes-unidades',w)
    w.navigate('library');w.select_version(approved)
    variant=api.create_variant(approved,'SYNTHETIC-VARIANT','SYNTHETIC design','Synthetic acceptance evidence','SYNTHETIC OPERATOR')
    for state in ('DRAFT','PENDING','RETIRED'):
        if state!='DRAFT':variant=api.transition_variant(variant['id'],variant['generation'],state,'SYNTHETIC OPERATOR','Synthetic reason')
        w.library_variant_id=variant['id'];w.selected()
        menu=w.build_variant_menu();menu.popup(w.mapToGlobal(QPoint(220,90)));app.processEvents()
        capture('10-menu-'+state.lower(),menu)
        menu.hide();menu.deleteLater()
    assert not api.issues()
    assert api._repository.db.execute('PRAGMA user_version').fetchone()[0]==4
finally:
    if hasattr(w,'preview_timer'):
        w.preview_timer.stop();w.preview_pending=False
        if w.preview_task:w.preview_task.wait(30000);app.processEvents()
    w.work_timer.stop();w.work_dirty_panel=None;w.dirty=False
    for dialog in dialogs:dialog.hide();dialog.deleteLater()
    w.hide();w.deleteLater();app.processEvents();session.close()
(out/'manifest.json').write_text(json.dumps(dict(baseline=a.baseline,source_revision=source_revision,source_code_sha256=source_hash,key=key,synthetic_only=True,sql_version=4,issues=0,captures=records),ensure_ascii=False,indent=2),encoding='utf-8')
print('OK',key,len(records),flush=True)
