"""Synthetic visual gate: never reads user data, approves documents or dispatches print."""
import os, sys, json, math, copy, hashlib, traceback, argparse, subprocess
import faulthandler
faulthandler.dump_traceback_later(40,repeat=False)
from pathlib import Path
repo=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(repo))
from PySide6.QtCore import Qt, QPoint, QSize, QCoreApplication, QEvent
from PySide6.QtGui import QPainter, QPalette, QColor
from PySide6.QtWidgets import (QApplication,QWidget,QDialog,QMessageBox,QFileDialog,
    QAbstractButton,QComboBox,QLineEdit,QPlainTextEdit,QAbstractSpinBox,QTableWidget,
    QTabWidget,QMenu,QInputDialog,QScrollArea,QAbstractItemView,QLabel,QProgressBar,QGraphicsView,QDockWidget)
from PySide6.QtSvg import QSvgGenerator
from covex_label_manager.qt_ui.demo import DemoSession
from covex_label_manager.qt_ui.functional import FunctionalWindow
from covex_label_manager.qt_ui.revision_approval import RevisionApprovalDialog
from covex_label_manager.qt_ui.compare import CompareDialog
from covex_label_manager.qt_ui.folder_import import FolderImportDialog
from covex_label_manager.qt_ui.controlled_import import ControlledImportDialog
from covex_label_manager.qt_ui.sheet_designer import SheetDesigner,OccupiedSlotsDialog
from covex_label_manager.qt_ui.printer_calibration_ui import CalibrationDialog
from covex_label_manager.qt_ui.acceptance_dialog import ReadinessDialog
from covex_label_manager.qt_ui.uat_session_dialog import UatSessionDialog
from covex_label_manager.qt_ui.master_reconcile_ui import MasterReconciliationDialog

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--width',type=int,default=1366)
parser.add_argument('--height',type=int,default=768)
parser.add_argument('--output-dir',type=Path,default=repo/'test-results'/'ux-integrated')
parser.add_argument('--svg-dir',type=Path)
args=parser.parse_args()
width,height=args.width,args.height;scale=float(os.environ.get('QT_SCALE_FACTOR','1'))
key=f'{width}x{height}_{scale:g}'
out=(args.output_dir/key).resolve();out.mkdir(parents=True,exist_ok=True)
docs=(args.svg_dir or out/'svg').resolve();docs.mkdir(parents=True,exist_ok=True)
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
code_hash=hashlib.sha256(b''.join(p.read_bytes() for p in sorted((repo/'covex_label_manager/qt_ui').glob('*.py')))).hexdigest()
app=QApplication([]);app.setStyle('Fusion')
pal=app.palette()
for role,color in [('Window','#F3F6F7'),('WindowText','#223B40'),('Base','#FFFFFF'),
    ('Text','#223B40'),('Button','#FFFFFF'),('ButtonText','#223B40'),
    ('Highlight','#147D71'),('HighlightedText','#FFFFFF'),('AlternateBase','#F8FAFA'),
    ('ToolTipBase','#FFFFFF'),('ToolTipText','#223B40')]:
    pal.setColor(getattr(QPalette.ColorRole,role),QColor(color))
app.setPalette(pal)
session=DemoSession();session.fictional=True
w=FunctionalWindow(session);api=session.services
# Stop polling to keep observations reproducible. Application actions are unchanged.
w.poll_timer.stop();w.legacy_timer.stop()
logical=(math.floor(width/scale),math.floor(height/scale)-40)
w.resize(*logical);w.show();app.processEvents()
records=[];errors=[];observations={}
original_exec=QDialog.exec
dialog_index=0

def textof(obj):
    if isinstance(obj,QLabel):return obj.text()
    if isinstance(obj,QAbstractButton):return obj.text()
    if isinstance(obj,QComboBox):return obj.currentText()
    if isinstance(obj,QLineEdit):return obj.text() or obj.placeholderText()
    if isinstance(obj,QPlainTextEdit):return obj.toPlainText()[:200]
    return ''

def snapshot(name,widget=None,vector=False):
    widget=widget or w
    app.processEvents()
    # settle Qt focus and queued layouts without any data mutation
    for _ in range(3):app.processEvents()
    QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
    app.processEvents()
    image=widget.grab();png=out/(name+'.png');assert image.save(str(png))
    controls=[]
    for obj in widget.findChildren(QWidget):
        if not isinstance(obj,(QAbstractButton,QComboBox,QLineEdit,QPlainTextEdit,QAbstractSpinBox,QTableWidget,QTabWidget,QAbstractItemView,QLabel,QProgressBar,QGraphicsView,QScrollArea,QDockWidget)):continue
        pos=obj.mapTo(widget,QPoint(0,0));r=obj.rect()
        controls.append({'class':type(obj).__name__,'object':obj.objectName(),'text':textof(obj),
            'visible':obj.isVisibleTo(widget),'enabled':obj.isEnabled(),
            'accessible_name':obj.accessibleName(),'tooltip':obj.toolTip(),
            'focus_policy':str(obj.focusPolicy()),
            'read_only':obj.isReadOnly() if hasattr(obj,'isReadOnly') else None,
            'rect':[pos.x(),pos.y(),r.width(),r.height()],
            'tabs':[obj.tabText(i) for i in range(obj.count())] if isinstance(obj,QTabWidget) else [],
            'choices':[obj.itemText(i) for i in range(obj.count())] if isinstance(obj,QComboBox) else []})
    svg=None
    if vector and key in ('1366x768_1','1366x768_1.5','1920x1080_1'):
        svg=docs/f'{key}_{name}.svg'
        gen=QSvgGenerator();gen.setFileName(str(svg));gen.setSize(widget.size());gen.setViewBox(QWidget.rect(widget))
        gen.setTitle(f'COVEX UX audit {key} / {name} / SYNTHETIC ONLY')
        painter=QPainter(gen);widget.render(painter,QPoint(0,0));painter.end()
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
    rec={'id':name,'title':widget.windowTitle(),'viewport_physical':[width,height],'requested_logical':logical,
        'actual_logical':[widget.width(),widget.height()],'dpr':widget.devicePixelRatioF(),
        'png':str(png.relative_to(repo)),'sha256':hashlib.sha256(png.read_bytes()).hexdigest(),
        'svg':str(svg.relative_to(repo)) if svg else None,
        'canvas_height':w.canvas.height() if widget is w and w.stack.currentWidget() is w.editor else None,
        'footer_reachable':all(0<=f.mapTo(widget,f.rect().bottomRight()).y()<widget.height()
            for f in getattr(widget,'footer_widgets',[])),
        'controls':controls}
    records.append(rec);print('CAPTURE',key,name,rec['actual_logical'],flush=True)

def dialog_capture(d):
    global dialog_index
    dialog_index+=1
    if hasattr(d,'prepare_layout'):d.prepare_layout()
    d.resize(min(d.width(),logical[0]-24),min(d.height(),logical[1]-24))
    d.show()
    if hasattr(d,'fit_available'):d.fit_available(QSize(logical[0]-24,logical[1]-24))
    snapshot(f'dynamic-{dialog_index:02d}',d,True)
    d.reject()
    return QDialog.DialogCode.Rejected

def question_capture(parent,title,text,*args,**kwargs):
    d=QMessageBox(parent);d.setWindowTitle(title);d.setText(text)
    d.setStandardButtons(QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel)
    dialog_capture(d);return QMessageBox.StandardButton.Cancel

def info_capture(parent,title,text,*args,**kwargs):
    d=QMessageBox(parent);d.setWindowTitle(title);d.setText(text)
    d.setStandardButtons(QMessageBox.StandardButton.Ok)
    dialog_capture(d);return QMessageBox.StandardButton.Ok

def input_capture(parent,title,text,*args,**kwargs):
    d=QInputDialog(parent);d.setWindowTitle(title);d.setLabelText(text)
    if 'recipiente' in title:d.setOption(QInputDialog.InputDialogOption.UsePlainTextEditForTextInput,True)
    dialog_capture(d);return '',False

def action(name,fn):
    try:fn()
    except Exception as ex:errors.append({'action':name,'error':str(ex),'trace':traceback.format_exc()})

def show_dialog(name,d,vector=True):
    if hasattr(d,'prepare_layout'):d.prepare_layout()
    d.resize(min(d.width(),logical[0]-24),min(d.height(),logical[1]-24));d.show()
    if hasattr(d,'fit_available'):d.fit_available(QSize(logical[0]-24,logical[1]-24))
    snapshot(name,d,vector);d.hide();d.deleteLater();app.processEvents()

try:
    pending=session.initial_id
    approved=next(r['version_id'] for r in api.library.entries() if r['state']=='APPROVED')
    retired=next(r['version_id'] for r in api.library.entries() if r['state']=='RETIRED')
    w.select_version(pending);snapshot('01-biblioteca-pendiente',vector=True)
    w.inspector_tabs.setCurrentIndex(1);snapshot('02-biblioteca-versiones')
    w.set_inspector(True);w.inspector_tabs.setCurrentIndex(2);snapshot('03-biblioteca-documentos',vector=True)
    assert w.native_approval_button.isVisibleTo(w)
    assert w.native_approval_button.mapTo(w,w.native_approval_button.rect().bottomRight()).y()<w.height()
    # Reproduce the two differently labelled buttons that both open approval.
    observations['approval_accesses']=[b.text() for b in w.inspector_panel.findChildren(QAbstractButton)
        if 'aprobaci' in b.text().lower()]
    w.advanced_button.click();snapshot('04-biblioteca-filtros',vector=True)
    w.advanced_button.click();w.select_version(approved);snapshot('05-biblioteca-vigente')
    w.select_version(retired);snapshot('06-biblioteca-retirada')
    w.select_version(pending);w.open_editor();snapshot('07-editor-pendiente',vector=True)
    w.editor_advanced_button.click()
    for toggle,content in w.tool_sections.values():toggle.setChecked(True)
    snapshot('08-editor-herramientas',vector=True)
    w.spins['x'].setValue(w.spins['x'].value()+.2);snapshot('09-editor-cambios');w.undo_edit()
    w.show_editor_work();snapshot('10-editor-datos-trabajo',vector=True);w.editor_context.setCurrentIndex(0)
    w.select_version(approved);w.open_editor();snapshot('11-editor-solo-lectura')
    variant=api.create_variant(approved,'UX-DRAFT','Variante sintética de auditoría','Ensayo visual ficticio','AUDITOR SINTETICO')
    w.library_variant_id=variant['id'];w.selected();w.open_editor();snapshot('11b-editor-variante-borrador',vector=True)
    # One synthetic work, bound to an already fictional approved demo revision.
    work=api.work.create(approved,name='AUDITORIA SINTETICA - lote')
    work=api.work.save(work['uid'],work['generation'],{'values':{'lote':'UX-SYN-001','pn':'0,3558','pb':'0,5000'},'count':'3','selection':'1-3'})
    w.load_emission_work(work['uid']);w.navigate('emission');snapshot('12-emision-datos',vector=True)
    for i,name in [(1,'13-emision-recipientes'),(2,'14-emision-formato'),(3,'15-emision-estado')]:
        w.emission_panel.tabs.setCurrentIndex(i);snapshot(name,vector=(i==2))
    w.emission_panel.tabs.setCurrentIndex(0)
    observations['preview_ok']=bool(w.preview_emission_work());snapshot('16-emision-preview',vector=True)
    observations['issue_enabled_after_preview']=w.native_issue.isEnabled()
    # No confirmation is accepted: capture modal + cancel every operation.
    QDialog.exec=dialog_capture
    QMessageBox.question=question_capture
    QMessageBox.warning=info_capture
    QMessageBox.information=info_capture
    QInputDialog.getText=input_capture
    QInputDialog.getMultiLineText=input_capture
    action('issue-confirmation',w.issue_emission_work)
    action('revision-approval',lambda:w.ask_form('Metadatos documentados',[('product','Producto','SYNTHETIC'),('source','Fuente obligatoria','')]))
    action('new-revision',w.clone_revision)
    action('paste-excel',w.paste_work_containers)
    w.select_version(pending);w.open_editor()
    action('editor-crop',w.edit_crop)
    action('editor-anchor',w.edit_anchor)
    action('editor-auxiliary',w.edit_auxiliary)
    action('editor-scale',w.edit_scale)
    action('editor-status',w.edit_status_area)
    action('editor-output',w.edit_output)
    action('pdf-expanded',w.emission_pdf.expand_pdf)
    action('new-work',w.new_emission_work)
    # No document approval or printer dispatch is called. Historical state is
    # generated only in disposable demo data, through the normal work service.
    w.emission_work=api.work.get(work['uid']);w.refresh_work_panels()
    issued,path,result=api.work.issue(work['uid'],w.emission_work['generation'],'AUDITOR SINTETICO')
    w.emission_work=issued;w.refresh_work_panels();w.navigate('history');w.history_table.selectRow(0)
    snapshot('17-historial-detalle',vector=True)
    w.preview_native_issue();snapshot('18-historial-pdf',vector=True)
    action('reprint-dialog',w.native_reprint)
    for i,name in enumerate(['19-config-resumen','20-config-datos','21-config-cm','22-config-estados','23-config-auditoria']):
        w.navigate('settings');w.settings_tabs.setCurrentIndex(i);snapshot(name,vector=i in (0,1))
    w.work_dock.hide()
    show_dialog('24-aprobacion-revision',RevisionApprovalDialog(w,api,api.version(pending)))
    show_dialog('25-comparar',CompareDialog(w,api,api.version(pending)['label_id'],pending))
    show_dialog('26-importar-carpeta',FolderImportDialog(w,api,session.root,paths=[session.root/'fictional-1.pdf']))
    show_dialog('27-importacion-controlada',ControlledImportDialog(w,api,session.root))
    profile=copy.deepcopy(issued['profile'])
    show_dialog('28-disenador-hoja',SheetDesigner(w,profile,root=api._repository.root))
    show_dialog('29-casillas-utilizadas',OccupiedSlotsDialog(w,12,3,[5,7]))
    show_dialog('30-calibracion',CalibrationDialog(w,api,profile))
    read=ReadinessDialog(w,api);read.run();show_dialog('31-preaceptacion',read)
    uat=UatSessionDialog(w,api);show_dialog('32-sesion-uat',uat)
    pack=session.root/'synthetic-r6a.zip';api.acceptance_export(api.acceptance_preflight(),pack)
    uat_path=session.root/'synthetic-uat.json'
    api.uat_create(pack,uat_path,{'machine':'SYNTHETIC-PC','windows':'SIMULATION ONLY',
        'tester':'AUDITOR SINTETICO','commit':commit,'portable_sha256':'0'*64})
    uat2=UatSessionDialog(w,api);uat2.load(uat_path);show_dialog('32b-sesion-uat-casos',uat2)
    master=session.root/'synthetic-master.csv'
    master.write_text('Nombre,Revisión,Código\nDEMO,00,SYN-001\n',encoding='utf-8')
    show_dialog('33-conciliar-master',MasterReconciliationDialog(w,api,master))
    # Exercise menu builders without invoking a menu action.
    original_menu=QMenu.exec
    def menu_capture(menu,*a,**kw):
        observations.setdefault('menus',[]).append([{'text':a.text(),'enabled':a.isEnabled(),'checkable':a.isCheckable()} for a in menu.actions()])
        return None
    class AuditMenu(QMenu):
        def exec(self,*args,**kwargs):return menu_capture(self,*args,**kwargs)
    for module in list(sys.modules.values()):
        if module and getattr(module,'__name__','').startswith('covex_label_manager.qt_ui') and getattr(module,'QMenu',None) is QMenu:
            module.QMenu=AuditMenu
    for name,fn in [('document-menu',w.actions_menu),('exchange-menu',w.exchange_menu),('columns-menu',w.columns_menu),('panels-menu',w.editor_panels_menu),('variant-menu',w.variant_menu),('work-options',w.work_options)]:action(name,fn)
    QMenu.exec=original_menu
    # Demonstrate current context visibility, without changing document state.
    w.select_version(pending);w.open_editor();w.show_editor_work();w.navigate('settings')
    observations['dock_visible_in_settings']=w.work_dock.isVisible()
    snapshot('34-config-sin-dock',vector=True)
    w.work_dock.hide();w.navigate('library');w.inspector_tabs.setCurrentIndex(1)
    legacy_link=next(b for b in w.inspector.findChildren(QAbstractButton) if b.text()=='Revisiones y variantes')
    legacy_link.click();observations['revisions_variants_opens_legacy_catalog']=w.stack.currentWidget()==w.catalog
    snapshot('35-seleccion-nativa',vector=True)
    invalid=api.work.create(pending,name='AUDITORIA SINTETICA - errores')
    w.load_emission_work(invalid['uid']);w.navigate('emission')
    w.emission_panel.inputs['count'].setText('0');w.emission_panel.changed();w.flush_emission_work()
    snapshot('36-emision-errores',vector=True)
    observations['sql_version']=api._repository.db.execute('PRAGMA user_version').fetchone()[0]
    assert observations['preview_ok'] and observations['issue_enabled_after_preview']
    assert not observations['dock_visible_in_settings']
    assert not observations['revisions_variants_opens_legacy_catalog']
    assert observations['sql_version']==4
    assert not errors,errors
    for record in records:
        assert record['footer_reachable'],record['id']
        assert record['actual_logical'][0]<=logical[0] and record['actual_logical'][1]<=logical[1],record['id']
finally:
    QDialog.exec=original_exec
    (out/'manifest.json').write_text(json.dumps({'key':key,'commit':commit,'qt_ui_sha256':code_hash,'logical_request':logical,'observations':observations,'errors':errors,'captures':records},ensure_ascii=False,indent=2),encoding='utf-8')
    w.work_timer.stop();w.dirty=False;w.work_dirty_panel=None;w.hide()
    w.deleteLater();QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
    session.close()
print('DONE',key,'captures',len(records),'errors',errors,flush=True)
