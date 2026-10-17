# Auxiliares exactos de reproducción

Código de auditoría en bloques documentales; no forma parte del producto. Guardar cada bloque en la ruta externa indicada antes de ejecutar los comandos de METODO.md. La variante `ux_capture.py` captura y cancela modales, y solo usa datos temporales ficticios.

## /workspace/cloud-setup/ux_capture.py

```python
"""Read-only UI audit harness; all database operations use DemoSession temp data."""
import os, sys, json, math, copy, hashlib, traceback
import faulthandler
faulthandler.dump_traceback_later(40,repeat=False)
from pathlib import Path
sys.path.insert(0, '/workspace/covex-label-manager')
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

width,height=map(int,sys.argv[1:3]);scale=float(os.environ['QT_SCALE_FACTOR'])
key=f'{width}x{height}_{scale:g}'
repo=Path('/workspace/covex-label-manager')
out=repo/'test-results'/'ux-audit'/key;out.mkdir(parents=True,exist_ok=True)
docs=repo/'docs'/'UX_AUDIT_R6B'/'evidencia';docs.mkdir(parents=True,exist_ok=True)
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
    rec={'id':name,'title':widget.windowTitle(),'viewport_physical':[width,height],'requested_logical':logical,
        'actual_logical':[widget.width(),widget.height()],'dpr':widget.devicePixelRatioF(),
        'png':str(png.relative_to(repo)),'sha256':hashlib.sha256(png.read_bytes()).hexdigest(),
        'svg':str(svg.relative_to(repo/'docs'/'UX_AUDIT_R6B')) if svg else None,
        'controls':controls}
    records.append(rec);print('CAPTURE',key,name,rec['actual_logical'],flush=True)

def dialog_capture(d):
    global dialog_index
    dialog_index+=1
    d.resize(min(d.width(),logical[0]-24),min(d.height(),logical[1]-24))
    d.show();snapshot(f'dynamic-{dialog_index:02d}',d,True)
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
    d.resize(min(d.width(),logical[0]-24),min(d.height(),logical[1]-24));d.show()
    snapshot(name,d,vector);d.hide();d.deleteLater();app.processEvents()

try:
    pending=session.initial_id
    approved=next(r['version_id'] for r in api.library.entries() if r['state']=='APPROVED')
    retired=next(r['version_id'] for r in api.library.entries() if r['state']=='RETIRED')
    w.select_version(pending);snapshot('01-biblioteca-pendiente',vector=True)
    w.inspector_tabs.setCurrentIndex(1);snapshot('02-biblioteca-versiones')
    w.inspector_tabs.setCurrentIndex(2);snapshot('03-biblioteca-documentos',vector=True)
    # Reproduce the two differently labelled buttons that both open approval.
    observations['approval_accesses']=[b.text() for b in w.inspector.findChildren(QAbstractButton)
        if 'aprobaci' in b.text().lower()]
    w.advanced_button.click();snapshot('04-biblioteca-filtros',vector=True)
    w.advanced_button.click();w.select_version(approved);snapshot('05-biblioteca-vigente')
    w.select_version(retired);snapshot('06-biblioteca-retirada')
    w.select_version(pending);w.open_editor();snapshot('07-editor-pendiente',vector=True)
    w.editor_advanced_button.click()
    for toggle,content in w.tool_sections.values():toggle.setChecked(True)
    snapshot('08-editor-herramientas',vector=True)
    w.spins['x'].setValue(w.spins['x'].value()+.2);snapshot('09-editor-cambios');w.undo_edit()
    w.show_editor_work();snapshot('10-editor-datos-trabajo',vector=True);w.work_dock.hide()
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
        'tester':'AUDITOR SINTETICO','commit':'afd0b06454c54e1e722596c37a6f6557883f2c16','portable_sha256':'0'*64})
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
    for name,fn in [('document-menu',w.actions_menu),('columns-menu',w.columns_menu),('panels-menu',w.editor_panels_menu),('variant-menu',w.variant_menu),('work-options',w.work_options)]:action(name,fn)
    QMenu.exec=original_menu
    # Demonstrate current context visibility, without changing document state.
    w.select_version(pending);w.open_editor();w.show_editor_work();w.navigate('settings')
    observations['dock_visible_in_settings']=w.work_dock.isVisible()
    snapshot('34-config-dock-residual',vector=True)
    w.work_dock.hide();w.navigate('library');w.inspector_tabs.setCurrentIndex(1)
    legacy_link=next(b for b in w.inspector.findChildren(QAbstractButton) if b.text()=='Revisiones y variantes')
    legacy_link.click();observations['revisions_variants_opens_legacy_catalog']=w.stack.currentWidget()==w.catalog
    snapshot('35-acceso-heredado-residual',vector=True)
    invalid=api.work.create(pending,name='AUDITORIA SINTETICA - errores')
    w.load_emission_work(invalid['uid']);w.navigate('emission')
    w.emission_panel.inputs['count'].setText('0');w.emission_panel.changed();w.flush_emission_work()
    snapshot('36-emision-errores',vector=True)
    observations['sql_version']=api._repository.conn.execute('PRAGMA user_version').fetchone()[0] if hasattr(api._repository,'conn') else 'see migration_v4 tests'
finally:
    QDialog.exec=original_exec
    (out/'manifest.json').write_text(json.dumps({'key':key,'base':'afd0b06454c54e1e722596c37a6f6557883f2c16','logical_request':logical,'observations':observations,'errors':errors,'captures':records},ensure_ascii=False,indent=2),encoding='utf-8')
    w.dirty=False;w.work_dirty_panel=None;w.hide();session.close()
print('DONE',key,'captures',len(records),'errors',errors,flush=True)
```

## /workspace/cloud-setup/ux_inventory.py

```python
import ast,json,re
from pathlib import Path
repo=Path('/workspace/covex-label-manager');out=repo/'docs/UX_AUDIT_R6B';out.mkdir(parents=True,exist_ok=True)
tests={}
for path in sorted((repo/'tests').glob('test_*.py')):
    src=path.read_text();tree=ast.parse(src)
    for n in ast.walk(tree):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test_'):
            names={x.attr for x in ast.walk(n) if isinstance(x,ast.Attribute)}
            tests[f'{path.relative_to(repo)}::{n.name}']={'names':names,'source':ast.get_source_segment(src,n)}
rows=[];controls={'button','action','QPushButton','QToolButton','QCheckBox','QLineEdit','QPlainTextEdit','QTextEdit',
    'QComboBox','QDoubleSpinBox','QSpinBox','QSlider','QListWidget','QTableWidget','QTabWidget',
    'QDialogButtonBox','QShortcut','QAction','QDialog','QFileDialog','QInputDialog','QPrintDialog',
    'Preview','PdfPane','RectangleView','QDockWidget','label','QLabel','QProgressBar',
    'QGraphicsView','QGraphicsScene','QScrollArea','QSplitter','QStackedWidget'}
class Visitor(ast.NodeVisitor):
    def __init__(self,path,src):self.path=path;self.src=src;self.context=[];self.loops=[]
    def visit_ClassDef(self,n):
        self.context.append(n.name);self.generic_visit(n);self.context.pop()
    def visit_FunctionDef(self,n):
        self.context.append(n.name);self.generic_visit(n);self.context.pop()
    def visit_For(self,n):
        self.loops.append(ast.unparse(n.target)+' in '+ast.unparse(n.iter));self.generic_visit(n);self.loops.pop()
    def visit_Call(self,n):
        name=n.func.id if isinstance(n.func,ast.Name) else n.func.attr if isinstance(n.func,ast.Attribute) else ''
        if name in controls or name in ('connect','addAction','addTab','addItem','addItems','addRow','getText','getMultiLineText','getOpenFileName','getSaveFileName','getExistingDirectory','question','warning','information'):
            code=ast.get_source_segment(self.src,n) or ast.unparse(n)
            targets=[]
            if name in ('button','action') and len(n.args)>1:targets=[ast.unparse(n.args[2] if name=='action' and len(n.args)>2 else n.args[1])]
            elif name=='connect':targets=[ast.unparse(x) for x in n.args]
            elif name=='addAction' and len(n.args)>1:targets=[ast.unparse(n.args[1])]
            symbols={x.attr for a in n.args for x in ast.walk(a) if isinstance(x,ast.Attribute)}
            related=[t for t,d in tests.items() if symbols & d['names']]
            rows.append({'id':f'S{len(rows)+1:04d}','source':str(self.path.relative_to(repo)),
                'line':n.lineno,'context':'.'.join(self.context),'kind':name,'expression':code,
                'loop_expansion':self.loops.copy(),'controller_expression':targets,
                'related_tests_by_symbol':related,'coverage_status':'REFERENCE_ONLY_NOT_CLICK_PROOF' if related else 'NO_DIRECT_SYMBOL_MATCH',
                'state':'SOURCE_SITE_VERIFY_RUNTIME; inherited constructors may be replaced or detached'})
        self.generic_visit(n)
for path in sorted((repo/'covex_label_manager/qt_ui').glob('*.py')):
    if path.name.endswith('_checks.py') or path.name in ('checks.py','demo.py','style.py'):continue
    src=path.read_text();Visitor(path,src).visit(ast.parse(src))
for file in ['main_qt.py','covex_label_manager/migration_consent.py']:
    path=repo/file;src=path.read_text();Visitor(path,src).visit(ast.parse(src))
(out/'inventario-sitios.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
lines=['# Inventario estático de sitios de interfaz','',
    'Registro generado por AST de todo `qt_ui`, `main_qt.py` y el consentimiento de migración. Cada sitio contiene contexto, línea, expresión completa, expansión de bucles, controlador explícito y referencias de tests en [inventario-sitios.json](inventario-sitios.json).',
    '', 'Un sitio de construcción no equivale a un control visible: la herencia elimina, mueve o reconecta controles. Los tests asociados se buscan por símbolo y son referencias para revisar; **no prueban por sí solos clic ni cobertura del sitio**. Véase INVENTARIO.md para resolución del controlador efectivo y alcance.', '',
    '| ID | Pantalla/clase y método | Tipo | Fuente | Controlador explícito | Test por símbolo |',
    '|---|---|---|---|---|---|']
for r in rows:
    clean=lambda s:s.replace('|','/').replace('\n',' ')[:150]
    lines.append(f"| {r['id']} | {clean(r['context'])} | {r['kind']} | [{r['source']}:{r['line']}](../../{r['source']}#L{r['line']}) | {clean('; '.join(r['controller_expression'])) or 'Señales/registro JSON'} | {len(r['related_tests_by_symbol']) if r['related_tests_by_symbol'] else 'Sin vínculo directo'} |")
(out/'INVENTARIO_SITIOS.md').write_text('\n'.join(lines)+'\n')
test_index=[{'test':t,'line':next(n.lineno for n in ast.walk(ast.parse((repo/t.split('::')[0]).read_text())) if isinstance(n,ast.FunctionDef) and n.name==t.split('::')[1])} for t in tests]
(out/'indice-pruebas.json').write_text(json.dumps(test_index,ensure_ascii=False,indent=2)+'\n')
print('Static sites',len(rows),'test functions',len(tests))
```

## /workspace/cloud-setup/ux_summarize.py

```python
import json,re,hashlib,collections,xml.etree.ElementTree as ET
from pathlib import Path
repo=Path('/workspace/covex-label-manager');out=repo/'docs/UX_AUDIT_R6B'
# QSvgGenerator emits trailing spaces in attribute lines; normalize formatting only.
for svg in (out/'evidencia').glob('*.svg'):
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
manifests=[];stats=[]
for f in sorted((repo/'test-results/ux-audit').glob('*/manifest.json')):
    m=json.loads(f.read_text());assert not m['errors'],m['errors'];manifests.append(m)
    overflow=[{'id':r['id'],'title':r['title'],'actual_logical':r['actual_logical'],'limit':r['requested_logical']} for r in m['captures'] if r['actual_logical'][0]>r['requested_logical'][0] or r['actual_logical'][1]>r['requested_logical'][1]]
    stats.append({'configuration':m['key'],'captures':len(m['captures']),'errors':m['errors'],
        'observations':m['observations'],'oversized_windows':overflow})
definitions={};compact=[]
for manifest in manifests:
    config={k:v for k,v in manifest.items() if k!='captures'};config['captures']=[]
    for capture in manifest['captures']:
        record={k:v for k,v in capture.items() if k!='controls'};record['control_states']=[]
        for control in capture['controls']:
            definition={k:v for k,v in control.items() if k not in ('rect','visible','enabled')}
            signature=hashlib.sha256(json.dumps(definition,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
            assert signature not in definitions or definitions[signature]==definition
            definitions[signature]=definition
            record['control_states'].append([signature,*control['rect'],control['visible'],control['enabled']])
        config['captures'].append(record)
    compact.append(config)
runtime={'schema':1,'state_fields':['definition_id','x','y','width','height','visible','enabled'],
    'control_definitions':definitions,'configurations':compact}
(out/'inventario-runtime.json').write_text(json.dumps(runtime,ensure_ascii=False,separators=(',',':'))+'\n')
(out/'resultados-visuales.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
lines=['# Evidencias visuales sintéticas','',
    'Capturas del widget real mediante `QWidget.grab()` (PNG local) y `QWidget.render(QSvgGenerator)` (SVG versionado, texto/vector con imágenes sintéticas integradas). Los SVG no son propuestas ni reconstrucciones manuales; muestran los widgets existentes, sin decoración de ventana del SO.',
    '', 'Solo fixtures `DemoSession` y archivos creados en directorios temporales. Los PNG completos están en `test-results/ux-audit/<configuración>/`; sus SHA-256 figuran en [inventario-runtime.json](inventario-runtime.json). Los SVG seleccionados se pueden revisar en esta PR. No se usa una aplicación productiva ni se aprueba documento real.',
    '', '| Configuración | Capturas | Errores del harness | Ventanas mayores que el área solicitada |', '|---|---:|---:|---:|']
for s in stats:lines.append(f"| {s['configuration']} | {s['captures']} | {len(s['errors'])} | {len(s['oversized_windows'])} |")
lines+=['','El área cliente pedida es `floor(ancho/factor) × (floor(alto/factor) − 40)` DIP; se reservan 40 DIP para marco/barra. Xorg tiene 1920×1080; se emulan los dos tamaños mediante el área de ventana y los factores Qt, no mediante Windows ni seis monitores físicos. Las mínimas de Qt pueden impedir el tamaño pedido; se registra el real, sin recortar o falsear el resultado. No hay comparación automática con una golden baseline anterior.','',
    'En `1366×768 / 150 %`, un diálogo de 676 DIP exige 1014 px, mayor que el alto físico objetivo: fallo de adaptación demostrable respecto a ese objetivo, pendiente de repetir en Windows. El diseñador de hoja consulta el QScreen Xorg real; su tamaño automático no prueba un monitor Windows 1366×768. Los modales se intentan ajustar al área objetivo, conservando todas las restricciones mínimas de la aplicación.','',
    '## Galería','', '| Configuración / estado | Captura SVG |','|---|---|']
for m in manifests:
    for r in m['captures']:
        if r['svg']:lines.append(f"| {m['key']} · {r['id']} · {r['title'].replace('|','/')} | [SVG]({r['svg']}) |")
lines+=['','## Revisión humana de las capturas','',
    'Se revisaron Biblioteca pendiente y filtros; Editor normal, avanzado, solo lectura y con dock; Emisión datos/formato/preview; Historial PDF; Configuración; aprobación documental; UAT y conciliación, con especial atención al caso 1366×768/150 % y comparación con 1920×1080/100 %. Las demás imágenes están capturadas y disponibles para revisión: no se afirma revisión humana individual de cada una. Los errores del harness inicial se corrigieron antes de la serie final y no se contabilizan como defectos de producto.']
(out/'EVIDENCIAS.md').write_text('\n'.join(lines)+'\n')
matrix=[]
for line in (repo/'docs/FUNCTIONAL_PRESERVATION_MATRIX.md').read_text().splitlines():
    m=re.match(r'\| ([BDEIMPHC]\d\d) \| (.*?) \|',line)
    if m:matrix.append(m.groups())
assert len(matrix)==87 and len(dict(matrix))==87
paths={
 'B':('Biblioteca; StudioWindow/BaseFunctionalWindow','tests/test_r3a_qt.py'),
 'D':('Biblioteca → Documentos y acciones; BaseFunctionalWindow','tests/test_r3a_qt.py; tests/test_variants_v4.py'),
 'E':('Editor → elementos / propiedades / ajuste avanzado; AdvancedEditorMixin','tests/test_r3b1_qt.py; tests/test_r3e_qt.py'),
 'I':('Biblioteca → Documentos y acciones → Importar; BaseFunctionalWindow/FolderImportMixin','tests/test_core.py; tests/test_r3f_qt.py; tests/test_r5b_migration.py'),
 'M':('Emisión → WorkPanel/EmissionCentreMixin; motor de trabajo','tests/test_r3c_emission_qt.py; tests/test_emission_work.py'),
 'P':('Emisión → Formato y emisión / Diseñar hoja; WorkPanel/SheetDesigner','tests/test_r3e_qt.py; tests/test_r4a_qt.py; tests/test_r4b_qt.py'),
 'H':('Historial; HistoryMixin → api.history','tests/test_r3c_history.py; tests/test_r3c_history_qt.py'),
 'C':('Configuración; SettingsMixin','tests/test_r3d_settings_qt.py')}
specific={
 'B02':('Tabla → selección, doble clic/Enter; StudioWindow.selected / BaseFunctionalWindow.open_editor','tests/test_r3a_qt.py::test_enter_opens_only_from_table_not_search'),
 'B04':('Ctrl+K → StudioWindow.quick_search','tests/test_r3a_qt.py'),
 'B09':('Inspector → Preview / Ampliar; StudioWindow.enlarge','tests/test_r3a_qt.py'),
 'B12':('Más filtros / Inspector / Paneles; resizeEvent / set_inspector','tests/test_r3a_qt.py::test_compact_auto_fold_does_not_forget_manual_preference'),
 'D03':('Ficha / Abrir documento original → BaseFunctionalWindow.open_document(True) → motor de conservación','tests/test_r5a_catalog.py; tests/test_core.py'),
 'D04':('Importar PDF/Word y carpeta controlada; import_document / ControlledImportDialog','tests/test_r3f_qt.py; tests/test_r5b_migration.py'),
 'D07':('Documentos y acciones → Crear nueva revisión → clone_revision','tests/test_r3a_qt.py::test_clone_is_pending_and_approval_retires_previous'),
 'D08':('Selector de revisión + selector de variante; revision_changed / choose_library_variant','tests/test_variants_v4.py; tests/test_r3a_qt.py'),
 'D09':('Registrar aprobación de revisión… → approve_revision → RevisionApprovalDialog.commit','tests/test_r3a_qt.py::test_native_approval_requires_confirmation_and_keeps_state_on_cancel'),
 'D10':('Registro de aprobación externa → api.approve; consulta de Retirada','tests/test_r3a_qt.py::test_clone_is_pending_and_approval_retires_previous'),
 'D11':('Editor solo lectura → Ajustar campos de revisión vigente… crea variante DRAFT','tests/test_r3e_qt.py; tests/test_variants_v4.py'),
 'D12':('Guardas verify_documents / verify_renderable / review_work; sin botón propio','tests/test_core.py; tests/test_variants_v4.py; tests/test_r3c_emission_qt.py'),
 'D13':('Guardas integrity/render_geometry; no autoaprobación de 00-R1','tests/test_r1.py; tests/test_migration_v4.py'),
 'D14':('Documentos y acciones → Comparar revisiones → CompareDialog (Qt); comparador de variante independiente','tests/test_r3f_qt.py::test_native_comparison_does_not_mutate_document'),
 'I01':('Importar PDF/Word → import_document; conversión requiere Word/LibreOffice instalado','tests/test_core.py (Word omitido); tests/test_r3a_qt.py::test_import_pdf_remains_pending'),
 'I02':('Importar carpeta… → FolderImportMixin.import_folder_native → ControlledImportDialog R5B; FolderImportDialog R3F existe pero no es la ruta de este menú','tests/test_r3f_qt.py; tests/test_r5b_migration.py'),
 'I03':('Motor importer.docx_to_pdf, integración local externa','tests/test_core.py (ensayo Word real omitido)'),
 'I04':('Motor de importación auto_crop y validación de página','tests/test_core.py; tests/test_r1.py'),
 'I05':('Motor add_label / catalog_migration_apply: siempre PENDING','tests/test_r5b_migration.py; tests/test_r3a_qt.py::test_import_pdf_remains_pending'),
 'M07':('Recipientes → edición celda y menú contextual Limpiar datos; WorkPanel.clear_container_row','tests/test_r3c_emission_qt.py; tests/test_emission_work.py'),
 'M08':('Pegar Excel… → EmissionCentreMixin.paste_work_containers','tests/test_r3c_emission_qt.py; tests/test_mass_units.py'),
 'M11':('Configuración → Maestros de estado → approve_settings_status; nativo Qt desde R3D','tests/test_r3d_settings_qt.py::test_pending_status_never_autoapproves'),
 'M13':('Formato y emisión → Seguridad + preflight; refresh_emission_review','tests/test_r3c_emission_qt.py::test_inline_checks_pending_invalid_format_and_long_fields'),
 'M15':('PDF de prueba → proof_emission_work; no registro definitivo','tests/test_r3c_emission_qt.py::test_native_preview_export_cancel_issue_and_recovery'),
 'M16':('Vista previa → Emitir definitivamente → confirmación → issue_emission_work','tests/test_r3c_emission_qt.py::test_native_preview_export_cancel_issue_and_recovery'),
 'M17':('PdfPane → Abrir PDF / Ampliar PDF → QDesktopServices / expand_pdf','tests/test_r3c_emission_qt.py; visor externo pendiente por plataforma'),
 'M18':('WorkPanel compartido / work_timer 400 ms / flush_emission_work','tests/test_emission_work_qt.py; tests/test_emission_work_tk.py'),
 'P06':('Calibrar hoja genera PDF de regla; Calibrar impresora… recoge medidas; funciones diferentes','tests/test_r4b_calibration.py; tests/test_r4b_qt.py'),
 'P07':('PdfPane.open_pdf → visor externo; adicional R4C Imprimir PDF registrado… → PrintWorkflowMixin/QPrintDialog','tests/test_r4c_dispatch.py; tests/test_r4c_qt.py; dispositivo físico pendiente'),
 'C01':('Preferencias y datos → Guardar operador → save_settings_operator','tests/test_r3d_settings_qt.py::test_operator_validation_and_backup_are_native'),
 'C02':('Preferencias y datos → ruta de solo lectura / Copiar ruta → copy_settings_path','tests/test_r3d_settings_qt.py'),
 'C03':('Preferencias y datos → Crear copia verificada → create_settings_backup','tests/test_r3d_settings_qt.py::test_operator_validation_and_backup_are_native'),
 'C04':('Catálogo CM → Importar clasificación CM → import_settings_cm','tests/test_r3d_settings_qt.py::test_cm_import_no_delete_and_duplicates'),
 'C05':('Catálogo CM → tabla de duplicidades; consulta sin corrección automática','tests/test_r3d_settings_qt.py::test_cm_import_no_delete_and_duplicates'),
 'C06':('Maestros de estado → Registrar aprobación → approve_settings_status','tests/test_r3d_settings_qt.py::test_pending_status_never_autoapproves'),
 'C07':('Auditoría local → Actualizar movimientos → refresh_native_settings','tests/test_r3d_settings_qt.py'),
 'C08':('Store/migration_v4/consentimiento expreso; SQLite v4','tests/test_migration_v4.py; tests/test_migration_consent.py'),
 'C09':('Procedimiento offline / guardas de build; no actualizador automático','tests/test_publication.py; docs/INSTALACION_Y_ACTUALIZACION.md'),
 'C10':('Resumen → recuentos y Biblioteca → refresh_native_settings','tests/test_r3d_settings_qt.py::test_settings_is_native_without_launching_tk')}
motor={'D12','D13','I03','I04','I05','C08','C09'};partial={'D03','I01'}
notes={'B12':'Accesos compactos menos visibles; UX-03/04.', 'D09':'Duplicación de entrada; UX-01.', 'D14':'El acceso alternativo Revisiones y variantes sigue en catálogo heredado; UX-02.',
    'I02':'Ruta actual controlada R5B; no confundir con diálogo R3F capturado como contingencia.',
    'M18':'Autoguardado solo de datos; diseño explícito. Dock residual UX-06.', 'P06':'Dos funciones distintas: no consolidar eliminando medidas.', 'P07':'No acredita entrega física ni disponibilidad de driver Windows.'}
lines=['# Matriz actual de conservación funcional: 87 IDs','',
    'Base `afd0b06454c54e1e722596c37a6f6557883f2c16`. Conserva sin renumerar las 87 filas de la matriz histórica. Esta actualización vive en la carpeta de auditoría y no altera la documentación histórica ni código.',
    '', '**78 rutas Qt, 2 mixtas y 7 motor/procedimiento; 0 capacidades clasificadas como exclusivamente Tk.** Es un recuento de disponibilidad de rutas, no 87 aceptaciones demostradas ni certificación de paridad visual. Las mixtas son D03 (fuentes originales + conservación de motor) e I01 (Word externo sin ensayo real); I03 conserva la limitación en el motor. D04 pasa a Qt tras la importación de carpeta; D14 e I02 tienen rutas nativas. La clasificación histórica 66/4/10/7 quedó obsoleta tras R3D/R3F/R5B.',
    '', 'No se ha demostrado una capacidad histórica eliminada. Sí hay degradaciones de descubribilidad y espacio, documentadas por incidencia; la ausencia de pérdida observada no demuestra ausencia de toda regresión. Las suites listadas son evidencia de familia funcional, no cobertura individual inferida. La serie ejecutada completa es 373 pass / 2 skip; Word real y bloqueo Windows siguen pendientes.',
    '', '| ID | Capacidad original | Disponibilidad | Acceso / controlador efectivo | Referencias de comprobación | Diagnóstico |','|---|---|---|---|---|---|']
for id,cap in matrix:
    route,tests= specific.get(id,paths[id[0]])
    state='Motor/procedimiento' if id in motor else 'Mixta' if id in partial else 'Ruta Qt'
    note=notes.get(id,'Ruta revisada; aceptación operativa/visual final pendiente.')
    lines.append(f'| {id} | {cap} | {state} | {route} | {tests} | {note} |')
lines+=['','## Capacidades posteriores: no inflar la cuenta histórica','',
    '| Ampliación | Ruta efectiva | Evidencia / límite |','|---|---|---|',
    '| Variantes SQLite v4: DRAFT/PENDING/APPROVED/RETIRED, nominal, evidencia/hash | Variantes ▾ / Gestionar variantes | test_variants_v4; la revisión y la variante tienen estados independientes. |',
    '| Editor avanzado: ocho tiradores, selección múltiple, snap, deshacer/rehacer | Editor / Ajuste avanzado | test_r3b1_qt, test_r3e_qt; no composición del maestro fijo. |',
    '| Trabajos recuperables, autoguardado, CAS y conciliación de emisión | Emisión / Datos del trabajo | test_emission_work, test_emission_work_qt/tk. |',
    '| Diseñador libre de hoja, A3/A5/custom, casillas usadas | Formato y emisión → Diseñar hoja | test_r3e_layout, test_r4a_layout/qt; soporte físico pendiente. |',
    '| Calibración por medidas + envío controlado de PDF registrado | Calibrar impresora / Imprimir PDF registrado | test_r4b_* y test_r4c_*; handoff no confirma papel. |',
    '| Inventario/exportación íntegra, importación por fila, conciliación libro máster | Documentos y acciones → R5A/R5B/R5C | test_r5a/b/c; sin datos internos en GitHub. |',
    '| Diagnóstico técnico y sesiones UAT versionadas | Configuración → Resumen → R6A/R6B | test_r6a_*, test_r6b_*; NO ACEPTADO, no ejecución física automática. |']
(out/'CONSERVACION_87.md').write_text('\n'.join(lines)+'\n')
sources=['# Auxiliares exactos de reproducción','',
    'Código de auditoría en bloques documentales; no forma parte del producto. Guardar cada bloque en la ruta externa indicada antes de ejecutar los comandos de METODO.md. La variante `ux_capture.py` captura y cancela modales, y solo usa datos temporales ficticios.','']
for name in ['ux_capture.py','ux_inventory.py','ux_summarize.py','ux_validate_docs.py']:
    sources.extend([f'## /workspace/cloud-setup/{name}','','```python',Path('/workspace/cloud-setup',name).read_text().rstrip(),'```',''])
(out/'REPRODUCCION.md').write_text('\n'.join(sources))
print(json.dumps(stats,ensure_ascii=False,indent=2))
```

## /workspace/cloud-setup/ux_validate_docs.py

```python
import re,json,hashlib,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
repo=Path('/workspace/covex-label-manager');docs=repo/'docs/UX_AUDIT_R6B';fail=[]
for path in docs.rglob('*.md'):
    text=path.read_text()
    # Fenced reproduction code is documentary source, not rendered local links.
    text=re.sub(r'```.*?```','',text,flags=re.S)
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if target.startswith(('http:','https:','#','mailto:')):continue
        target=target.split('#')[0]
        if not (path.parent/target).exists():fail.append(f'Broken link {path}: {target}')
sites=json.loads((docs/'inventario-sitios.json').read_text());assert len(sites)==884
for row in sites:
    assert (repo/row['source']).is_file()
    assert 1<=row['line']<=len((repo/row['source']).read_text().splitlines())
    for test in row['related_tests_by_symbol']:assert (repo/test.split('::')[0]).is_file()
matrix=(docs/'CONSERVACION_87.md').read_text()
ids=re.findall(r'^\| ([BDEIMPHC]\d\d) \|',matrix,re.M)
assert len(ids)==87 and len(set(ids))==87
runtime=json.loads((docs/'inventario-runtime.json').read_text());assert len(runtime['configurations'])==6
count=0;svg_paths=set();oversize={}
for config in runtime['configurations']:
    assert not config['errors'];assert len(config['captures'])==51
    assert config['observations']['preview_ok']
    for capture in config['captures']:
        count+=1;png=repo/capture['png'];assert hashlib.sha256(png.read_bytes()).hexdigest()==capture['sha256']
        for state in capture['control_states']:assert state[0] in runtime['control_definitions']
        if capture['svg']:svg_paths.add(docs/capture['svg'])
assert count==306
assert len(svg_paths)==123
assert svg_paths==set((docs/'evidencia').glob('*.svg'))
for svg in svg_paths:
    root=ET.parse(svg).getroot()
    for node in root.iter():
        assert node.tag.split('}')[-1] not in ('script','foreignObject')
        for k,v in node.attrib.items():
            assert not k.lower().startswith('on')
            if k.endswith('href'):assert v.startswith(('data:image/png;base64,','#')),v[:100]
# WCAG token calculation, normal enabled text (not disabled widgets).
def lum(color):
    rgb=[int(color[i:i+2],16)/255 for i in (0,2,4)]
    c=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in rgb]
    return sum(a*b for a,b in zip(c,[.2126,.7152,.0722]))
ratios={bg:(lum(bg)+.05)/(lum('72868C')+.05) for bg in ('FFFFFF','F3F6F7')}
print('Contrast subtle:',ratios)
print('Controls/source sites:',len(sites),'matrix IDs:',len(ids),'captures:',count,'SVG:',len(svg_paths))
assert not fail,'\n'.join(fail)
print('Documentation checks passed: links, source references, IDs, JSON, PNG hashes, self-contained SVG safety.')
```
