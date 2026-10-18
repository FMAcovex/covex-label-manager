"""R8B source/frozen visual and functional proof, synthetic data ONLY."""
import copy
import hashlib
import json
import math
import os
import sys
from pathlib import Path
import traceback


def present_viewport(widget, size, settle):
    """Show and final sizing are separate. Require the exact client viewport;
    a native desktop clamp must fail, not masquerade as the requested size.
    """
    widget.show();settle()
    widget.resize(size);settle()
    assert widget.size()==size, ('Requested client viewport not available',size,widget.size())


def horizontal_layout_metrics(scroll):
    """Synthetic-check diagnostics: expose the control forcing a minimum width."""
    from PySide6.QtWidgets import QWidget
    content=scroll.widget()
    def measure(widget):
        text=getattr(widget,'text',lambda:'')()
        return dict(type=type(widget).__name__,name=widget.objectName(),text=text[:100],
                    width=widget.width(),minimum=widget.minimumWidth(),
                    hint=widget.minimumSizeHint().width())
    return dict(horizontal_max=scroll.horizontalScrollBar().maximum(),
                viewport_width=scroll.viewport().width(),content=measure(content),
                children=[measure(child) for child in content.findChildren(QWidget)
                          if child.minimumSizeHint().width()>scroll.viewport().width()-30])


def run(report, capture=None, *, baseline=False, svg_dir=None, source_commit=None):
    import fitz
    from PySide6.QtCore import QSize, QPoint, QRectF
    from PySide6.QtGui import QColor, QPalette, QPainter
    from PySide6.QtWidgets import QApplication, QDialog, QAbstractButton
    from PySide6.QtSvg import QSvgGenerator
    from covex_label_manager.qt_ui.demo import DemoSession
    from covex_label_manager.qt_ui.functional import FunctionalWindow
    from covex_label_manager.qt_ui.status_fields_dialog import StatusFieldsDialog
    from covex_label_manager.qt_ui.responsive import install_translation
    from covex_label_manager.status_design import make_layout
    app=QApplication.instance() or QApplication([]);app.setStyle('Fusion');install_translation(app)
    palette=app.palette()
    for role,color in [('Window','#F3F6F7'),('WindowText','#223B40'),('Base','#FFFFFF'),('Text','#223B40'),('Button','#FFFFFF'),('ButtonText','#223B40'),('Highlight','#147D71'),('HighlightedText','#FFFFFF')]:
        palette.setColor(getattr(QPalette.ColorRole,role),QColor(color))
    app.setPalette(palette)
    report=Path(report);out=Path(capture) if capture else report.with_suffix('')
    out.mkdir(parents=True,exist_ok=True)
    session=DemoSession();session.fictional=True;w=FunctionalWindow(session);api=session.services
    w.poll_timer.stop();w.legacy_timer.stop();records=[];dialogs=[]
    result=dict(ok=False,synthetic_only=True,baseline=baseline,source_commit=source_commit,scale=float(os.environ.get('QT_SCALE_FACTOR','1')),captures=records,
                qt_platform=app.platformName(),os=sys.platform)

    def settle():
        for _ in range(4):app.processEvents()

    def snapshot(name,widget):
        settle();path=out/(name+'.png');assert widget.grab().save(str(path))
        records.append(dict(view=name,size=[widget.width(),widget.height()],dpr=widget.devicePixelRatioF(),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        if svg_dir and name in ('1366-editor','1366-status','1920-editor','1920-status'):
            svg=Path(svg_dir)/(name+'.svg');svg.parent.mkdir(parents=True,exist_ok=True)
            gen=QSvgGenerator();gen.setFileName(str(svg));gen.setSize(widget.size());gen.setViewBox(widget.rect());gen.setTitle('SYNTHETIC ONLY · R8B '+('before' if baseline else 'after')+' · '+name)
            painter=QPainter(gen);widget.render(painter,QPoint());painter.end()
            svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
        print('R8B CAPTURE',name,widget.width(),widget.height(),flush=True)

    try:
        initial=session.initial_id
        approved=next(v['id'] for v in api.versions(w.row['id']) if v['state']=='APPROVED')
        original=dict(api.version(approved))
        source=session.root/'SYNTHETIC-status-editor.pdf'
        with fitz.open() as pdf:
            page=pdf.new_page(width=400,height=260)
            page.insert_text((20,35),'SYNTHETIC ONLY - NO DOCUMENTO REAL')
            page.insert_text((20,60),'APROBADO - NOMBRE DE LA ETIQUETA, NO APROBACION')
            pdf.save(source)
        layout=make_layout(source,'aprobado')
        layout['fields']=[dict(key='lote',label='Lote ficticio',rect=[20,90,180,115],font_size=10,bold=False,required=True)]
        uid=api.status_catalog.import_many(source,[dict(kind='aprobado',revision='00',layout=layout)])[0]
        for width,height in ((1366,768),(1920,1080)):
            logical=QSize(math.floor(width/result['scale']),math.floor(height/result['scale'])-40)
            present_viewport(w,logical,settle)
            w.select_version(initial);w.open_editor();settle()
            assert w.size()==logical
            assert w.canvas.width()>=200 and w.canvas.height()>=logical.height()*.45
            w.editor_context.setCurrentIndex(0);w.properties_scroll.verticalScrollBar().setValue(0)
            snapshot(f'{width}-editor',w)
            if not baseline:
                w.editor_advanced_button.setChecked(False);w.toggle_editor_advanced()
                for control in (w.name_input,w.key_input,*w.spins.values(),w.font_size,w.bold,w.required,w.locked,w.draw_mode):
                    assert control.isVisibleTo(w)
                    w.properties_scroll.ensureWidgetVisible(control);settle()
                    assert w.properties_scroll.viewport().rect().contains(control.mapTo(w.properties_scroll.viewport(),control.rect().center()))
                assert not w.properties_scroll.isAncestorOf(w.save_button)
                assert w.save_button.isVisibleTo(w) and w.save_button.mapTo(w,w.save_button.rect().bottomRight()).y()<w.height()
                assert w.properties_scroll.horizontalScrollBar().maximum()==0, horizontal_layout_metrics(w.properties_scroll)
                snapshot(f'{width}-essential-scroll',w)
                w.editor_advanced_button.setChecked(True);w.toggle_editor_advanced()
            w.field_list.item(1).setSelected(True);snapshot(f'{width}-multiple-selection',w)
            w.select_version(approved);w.open_editor();settle()
            assert not w.editable() and not w.save_button.isEnabled()
            assert not w.new_field_button.isEnabled()
            snapshot(f'{width}-protected',w)
            variant=api.create_variant(approved,'R8B-'+str(width),'Variante ficticia','Prueba sintética del Editor','SYNTHETIC OPERATOR')
            w.library_variant_id=variant['id'];w.selected();w.open_editor();settle()
            assert w.editable()
            snapshot(f'{width}-draft-variant',w)
            menu=w.build_variant_menu();menu.popup(w.mapToGlobal(QPoint(100,80)));settle()
            assert menu.isVisible();snapshot(f'{width}-variant-menu',menu);menu.hide();menu.deleteLater()
            if not baseline:
                transform=w.canvas.transform();item=w.field_items[0]
                w.change_name('SYNTHETIC name')
                assert w.field_items[0] is item and w.canvas.transform()==transform
                w.new_field_button.click();assert w.fields[-1]['key'].startswith('campo_')
                assert w.save_work()
                saved=json.loads(api.variant(variant['id'])['design_json'])['layout']
                assert saved==w.design.state
            assert dict(api.version(approved))==original
            dialog=StatusFieldsDialog(api,api.status_catalog.get(uid),w);dialogs.append(dialog)
            dialog_size=QSize(min(1150,logical.width()-24),min(760,logical.height()-24))
            present_viewport(dialog,dialog_size,settle)
            assert dialog.size()==dialog_size
            for footer in dialog.footer_widgets:
                assert footer.mapTo(dialog,footer.rect().bottomRight()).y()<dialog.height()
            snapshot(f'{width}-status',dialog)
            if not baseline:
                for control in (dialog.key,dialog.name,*dialog.spins.values(),dialog.font_size,dialog.bold,dialog.required):
                    dialog.properties_scroll.ensureWidgetVisible(control);settle()
                    assert dialog.properties_scroll.viewport().rect().contains(control.mapTo(dialog.properties_scroll.viewport(),control.rect().center()))
                assert dialog.properties_scroll.horizontalScrollBar().maximum()==0, horizontal_layout_metrics(dialog.properties_scroll)
                dialog.spins['w'].setValue(dialog.spins['w'].value()*.9)
                assert dialog.apply_properties();changed=copy.deepcopy(dialog.design)
                dialog.undo_edit();assert dialog.design!=changed
                dialog.redo_edit();assert dialog.design==changed
                dialog.save();assert dialog.result()==QDialog.DialogCode.Accepted
                assert json.loads(api.status_catalog.get(uid)['layout_json'])==changed
            else:dialog.reject()
        assert not api.issues() and not api.status_catalog.issues()
        assert api._repository.db.execute('PRAGMA user_version').fetchone()[0]==4
        assert api._repository.db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        with api.status_catalog._connect() as db:
            assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
            assert not db.execute('PRAGMA foreign_key_check').fetchall()
        result.update(ok=True,sqlite_v4=True,integrity=True,issues=0,approved_revision_unchanged=True,exact_viewports=True)
    except Exception:
        result['error']=traceback.format_exc()  # synthetic fixture only
        print(result['error'],flush=True)
    finally:
        w.shutdown_runtime()
        for dialog in dialogs:dialog.hide();dialog.deleteLater()
        if w.design:w.design.mark_clean()
        w.hide();w.deleteLater();settle();session.close()
        report.parent.mkdir(parents=True,exist_ok=True)
        report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if result['ok'] else 1
