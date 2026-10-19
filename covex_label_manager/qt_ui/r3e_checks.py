"""Synthetic native Qt proof, also callable from frozen portable Windows."""
import copy
import json
import math
import os
import sys
from pathlib import Path
from PySide6.QtCore import Qt,QPoint,QPointF,QCoreApplication,QEvent
from PySide6.QtGui import QPalette,QColor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QDialogButtonBox
from .demo import DemoSession
from .functional import FunctionalWindow
from .sheet_designer import SheetDesigner
from .pdf_view import PdfPane
from .window import vbox
from ..sheet_layout import template,slots,paper_size
from ..engine import MM
import fitz

def run(report,captures=None):
    app=QApplication.instance() or QApplication([])
    previous_style=app.style().objectName();previous_palette=app.palette()
    if previous_style.lower()!='fusion':app.setStyle('Fusion')
    palette=app.palette()
    for role,c in [(QPalette.ColorRole.Window,'#F4F7F8'),(QPalette.ColorRole.WindowText,'#203B40'),(QPalette.ColorRole.Base,'white'),(QPalette.ColorRole.Text,'#203B40'),(QPalette.ColorRole.Button,'white'),(QPalette.ColorRole.ButtonText,'#203B40')]:palette.setColor(role,QColor(c))
    app.setPalette(palette);s=DemoSession();s.fictional=True;w=FunctionalWindow(s);api=s.services;extras=[]
    report=Path(report);captures=Path(captures or report.parent/'r3e-captures');captures.mkdir(parents=True,exist_ok=True)
    result={'ok':False,'synthetic_only':True,'platform':sys.platform,'qt_scale_factor':os.environ.get('QT_SCALE_FACTOR','1'),'physical_monitor_acceptance':False,'checks':[],'captures':[]}
    def check(value,title):assert value,title;result['checks'].append(title)
    def capture(widget,name,target=(1920,1080)):
        dpr=widget.devicePixelRatioF();widget.resize(math.floor(target[0]/dpr),math.floor(target[1]/dpr));widget.show();app.processEvents();QTest.qWait(40)
        widget.grab().save(str(captures/(name+'.png')))
        result['captures'].append(dict(name=name,logical_width=widget.width(),logical_height=widget.height(),dpr=dpr,requested_physical_viewport=list(target)))
    try:
        w.show();app.processEvents();w.open_editor();before=copy.deepcopy(w.design.state)
        # R8B draws on the real canvas; the former two modal dialogs no longer
        # participate in common creation. Keep every geometry/PDF assertion.
        w.draw_field_button.click();app.processEvents()
        capture(w,'01-editor-nuevo-campo')
        start=w.canvas.mapFromScene(QPointF(w.image_w*.1,w.image_h*.3))
        end=w.canvas.mapFromScene(QPointF(w.image_w*.4,w.image_h*.4))
        QTest.mousePress(w.canvas.viewport(),Qt.MouseButton.LeftButton,pos=start)
        QTest.mouseMove(w.canvas.viewport(),end,delay=20)
        QTest.mouseRelease(w.canvas.viewport(),Qt.MouseButton.LeftButton,pos=end);app.processEvents()
        capture(w,'02-editor-dibujar-campo')
        check(len(w.fields)==len(before['fields'])+1,'create_drawn_field');w.undo_edit();check(w.design.state==before,'undo_create');w.redo_edit()
        i=w.field_items[-1];i.setSelected(True);w.canvas.fit();app.processEvents();start=w.canvas.mapFromScene(i.handles[4].scenePos())
        old=copy.deepcopy(w.design.state);QTest.mousePress(w.canvas.viewport(),Qt.MouseButton.LeftButton,pos=start);QTest.mouseMove(w.canvas.viewport(),start+QPoint(12,0),delay=20);QTest.mouseRelease(w.canvas.viewport(),Qt.MouseButton.LeftButton,pos=start+QPoint(12,0));app.processEvents()
        check(w.design.state!=old,'actual_field_handle_resize');check(w.save_work(),'save_field');capture(w,'03-editor-campo-redimensionado')
        p=dict(width_mm=80,height_mm=50,margin_mm=8,gap_mm=3,orientation='portrait',start_slot=1,safety_mm=0,offset_x_mm=0,offset_y_mm=0,crop_marks=1,layout_version=1,paper='A4',layout_mode='free');p['slots']=template(p,1)
        d=SheetDesigner(w,p,root=api._repository.root,thumbnail=api.thumbnail(w.editor_version,width_px=450),nominal=(w.editor_version['base_w_mm'],w.editor_version['base_h_mm']));extras.append(d);capture(d,'04-A4-una-posicion');d.count.setValue(5);d.arrange();capture(d,'05-A4-cinco-posiciones');check(len(d.profile['slots'])==5,'exactly_five_positions')
        d.paper.setCurrentText('A3');d.arrange();capture(d,'06-A3-libre')
        # Shrink before moving/alignment to create useful free space.
        for item in d.items:item.setRect(0,0,item.rect().width()*.8,item.rect().height()*.8)
        d.gesture();d.items[0].setSelected(True);d.items[2].setSelected(True);d.align(0);capture(d,'07-alineacion')
        before=copy.deepcopy(d.profile);item=d.items[0];item.setSelected(True);start=d.view.mapFromScene(item.handles[4].scenePos())
        QTest.mousePress(d.view.viewport(),Qt.MouseButton.LeftButton,pos=start);QTest.mouseMove(d.view.viewport(),start-QPoint(10,0),delay=20);QTest.mouseRelease(d.view.viewport(),Qt.MouseButton.LeftButton,pos=start-QPoint(10,0));app.processEvents()
        check(d.profile!=before,'actual_sheet_handle_resize')
        vid=next(v['id'] for v in api.versions(w.row['id']) if v['state']=='APPROVED');work=api.work.create(vid,None,'Synthetic R3E proof');work=api.work.save(work['uid'],work['generation'],{'profile':d.profile,'count':'7','copies':'2','values':{'lote':'SYNTH-R3E','pn':'1','pb':'2'}})
        out=api.output_path('cache','synthetic-r3e.pdf');api.work.proof(work['uid'],work['generation'],out)
        with fitz.open(out) as pdf:
            check(len(pdf)==3,'fourteen_labels_three_pages')
            check(max(abs(x-y) for x,y in zip((pdf[0].rect.width/MM,pdf[0].rect.height/MM),paper_size(d.profile)))<.001,'A3_actual_pdf_dimensions')
            rects=[draw['rect'] for page in pdf for draw in page.get_drawings() if draw.get('color') and draw['color'][0]>.7]
            boxes=slots(d.profile);check(len(rects)==14,'no_fictitious_copies')
            for n,r in enumerate(rects):
                b=boxes[n%5];check(max(abs(x-y) for x,y in zip([v/MM for v in r],(b.x,b.y,b.x+b.width,b.y+b.height)))<.1,'PDF_box_error_under_0.1mm_'+str(n))
        pane=PdfPane(api);extras.append(pane);pane.load(out,'PDF real A3 · prueba marcada');capture(pane,'08-PDF-prueba-real')
        bad=copy.deepcopy(d.profile);bad['slots'][0]['x']=-5;d.push(bad,'Synthetic out of bounds');capture(d,'09-error-fuera-limites');check(not d.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled(),'invalid_acceptance_blocked');d.undo()
        capture(d,'10-compacto-1366x768',target=(1366,768));check(d.width()*d.devicePixelRatioF()<=1366+2,'compact_logical_width')
        api.work.assert_current(work,True);issued,path,summary=api.work.issue(work['uid'],work['generation'],'Synthetic reviewer');check(summary['physical']==14,'definitive_synthetic_fourteen')
        from ..emission_history import HistoryService
        history=HistoryService(api);report_issue=history.inspect(issued['issue_id']);check(report_issue['snapshot']['profile']==d.profile,'snapshot_preserves_slots')
        pk,reprint,summary=history.reproduce(issued['issue_id'],'1,7','Synthetic geometry acceptance','Synthetic reviewer',proof=True)
        with fitz.open(reprint) as pdf:check(abs(pdf[0].rect.width/MM-297)<.001 and abs(pdf[0].rect.height/MM-420)<.001,'reprint_preserves_A3')
        capture(w,'11-editor-compacto-1366x768',target=(1366,768))
        pk,reprint,summary=history.reproduce(issued['issue_id'],'1,7','Synthetic definitive geometry acceptance','Synthetic reviewer',start_slot=3)
        check(pk is not None and api.issue(pk)['source_issue_id']==issued['issue_id'],'definitive_reprint_links_original')
        result['ok']=True
    except Exception:
        import traceback
        result['error']=traceback.format_exc()
    finally:
        report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2),encoding='utf-8')
        w.dirty=False;w.work_dirty_panel=None;w.shutdown_runtime()
        for widget in extras:widget.hide();widget.deleteLater()
        w.hide();w.deleteLater()
        QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
        app.processEvents();s.close()
        if previous_style and app.style().objectName()!=previous_style:app.setStyle(previous_style)
        app.setPalette(previous_palette)
    return 0 if result['ok'] else 1
