"""Synthetic-only R8C source/frozen proof and before/after visual evidence."""
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import traceback


def run(report,capture=None,*,baseline=False,source_commit=None):
    import fitz
    from PySide6.QtCore import QSize,QCoreApplication,QEvent
    from PySide6.QtGui import QColor,QPalette
    from PySide6.QtWidgets import QApplication
    from .demo import DemoSession
    from .functional import FunctionalWindow
    from .status_fields_dialog import StatusFieldsDialog
    from .editor_ux_checks import present_viewport,horizontal_layout_metrics
    from .responsive import install_translation
    from ..status_design import make_layout,render_proof
    app=QApplication.instance() or QApplication([])
    if app.style().objectName().lower()!='fusion':app.setStyle('Fusion')
    install_translation(app)
    palette=app.palette()
    for role,color in [('Window','#F3F6F7'),('WindowText','#223B40'),('Base','#FFFFFF'),('Text','#223B40'),('Button','#FFFFFF'),('ButtonText','#223B40'),('Highlight','#147D71'),('HighlightedText','#FFFFFF')]:
        palette.setColor(getattr(QPalette.ColorRole,role),QColor(color))
    app.setPalette(palette)
    report=Path(report);out=Path(capture) if capture else report.with_suffix('')
    out.mkdir(parents=True,exist_ok=True);session=DemoSession();session.fictional=True
    w=FunctionalWindow(session);api=session.services;dialogs=[];captures=[];pdfs=[]
    result=dict(ok=False,synthetic_only=True,baseline=baseline,source_commit=source_commit,
                os=sys.platform,qt_platform=app.platformName(),scale=float(os.environ.get('QT_SCALE_FACTOR','1')),
                captures=captures,pdfs=pdfs)
    def settle():
        for _ in range(4):app.processEvents()
    def snapshot(name,widget):
        settle();path=out/(name+'.png');assert widget.grab().save(str(path))
        captures.append(dict(view=name,size=[widget.width(),widget.height()],sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        print('R8C CAPTURE',name,widget.width(),widget.height(),flush=True)
    def pdf_record(name,path):
        import shutil
        saved=out/(name+'.pdf');shutil.copyfile(path,saved)
        with fitz.open(saved) as doc:
            assert 'PRUEBA' in doc[0].get_text() or name=='font-specimen'
            raster=doc[0].get_pixmap(matrix=fitz.Matrix(2,2));raster.save(str(out/(name+'-pdf.png')))
            pdfs.append(dict(name=name,sha256=hashlib.sha256(saved.read_bytes()).hexdigest(),pages=len(doc),
                             raster_sha256=hashlib.sha256(raster.samples).hexdigest()))
    try:
        initial=session.initial_id
        approved=next(v['id'] for v in api.versions(w.row['id']) if v['state']=='APPROVED')
        original=dict(api.version(approved))
        if not baseline:
            from ..typography import DEFAULT,font_resource,paint,FONT_SHA256
            from ..status_scaling import DEFAULT as FIT,geometry,critical_losses
            from .emission_appearance import EmissionAppearanceDialog
            fonts=out/'font-specimen.pdf'
            with fitz.open() as doc:
                page=doc.new_page()
                n=0
                for family in ('sans','serif','mono'):
                    for bold,italic in ((False,False),(True,False),(False,True),(True,True)):
                        font,name=font_resource(family,bold,italic)
                        paint(page,f'SYNTHETIC {family} bold={bold} italic={italic} Áéñ',fitz.Rect(25,25+n*45,570,65+n*45),12,bold,dict(DEFAULT,family=family,italic=italic,color='#1234AB'))
                        n+=1
                doc.save(fonts)
            # pdf_record expects a separate source path.
            with fitz.open(fonts) as doc:
                assert len(doc[0].get_fonts())==12
                assert all(len(doc.extract_font(f[0])[3])>1000 for f in doc[0].get_fonts())
            result['embedded_fonts']=12;result['font_hashes']=FONT_SHA256
        uids=[]
        for kind,color in [('sin_analizar',(1,.92,.3)),('aprobado',(.25,.8,.4)),('rechazado',(.9,.3,.3))]:
            path=session.root/('SYNTHETIC-'+kind+'.pdf')
            with fitz.open() as doc:
                page=doc.new_page(width=200,height=100)
                page.draw_rect(page.rect,fill=color,color=None)
                page.insert_text((75,28),'SYNTHETIC',fontsize=8)
                doc.save(path)
            layout=make_layout(path,kind)
            layout['fields']=[dict(key='lote',label='Lote sintético',rect=[75,40,125,60],font_size=8.,bold=False,required=True)]
            if not baseline:
                layout['contract']=2;layout['fields'][0].update(typography=copy.deepcopy(DEFAULT),example='SYN-01')
            uid=api.status_catalog.import_many(path,[dict(kind=kind,revision='SYN-00',layout=layout)])[0];uids.append(uid)
            for mode in (('fit',) if baseline else ('fit','fill')):
                settings={} if baseline else dict(height_mm=70,composition=dict(FIT,mode=mode))
                proof=api.status_catalog.preview(uid,{'lote':'SYN-01'},width_mm=70,**settings)
                pdf_record(kind+'-'+mode,proof)
            if not baseline:
                with fitz.open(path) as src:
                    fit=geometry(layout['crop'],[0,0,200,200],FIT)
                    fill=geometry(layout['crop'],[0,0,200,200],dict(FIT,mode='fill'))
                    assert fit['free_mm'][1]>0 and fill['cropped_mm'][0]>0
                    assert not critical_losses(src[0],layout,fill['source_clip'])
                api.status_catalog.submit(uid)
                api.status_catalog.approve(uid,'SYNTHETIC QA','SYNTHETIC EXTERNAL FIXTURE ONLY',confirmation=True)
                issue,issued=api.status_catalog.emit(uid,{'lote':'SYN-01'},'SYNTHETIC',width_mm=70,height_mm=70,composition=dict(FIT,mode='fill'))
                _,reprint=api.status_catalog.reprint(issue,'SYNTHETIC','SYNTHETIC regression exact copy')
                assert issued.read_bytes()==reprint.read_bytes()
        # Every kind's artwork and fields have been exercised in the real engine.
        result['standalone_kinds']=3
        for width,height in ((1366,768),(1920,1080)):
            logical=QSize(math.floor(width/result['scale']),math.floor(height/result['scale'])-40)
            present_viewport(w,logical,settle);w.select_version(initial);w.open_editor();settle()
            if not baseline:
                index=w.text_appearance.family.findData('sans');w.text_appearance.family.setCurrentIndex(index);w.text_appearance.family.activated.emit(index)
                w.example_input.setText('SYN-01');w.example_input.editingFinished.emit()
                assert w.fields[0]['typography']['family']=='sans'
                for control in (w.text_appearance.family,w.text_appearance.color,w.text_appearance.wrap,w.example_input,*w.spins.values()):
                    w.properties_scroll.ensureWidgetVisible(control);settle()
                    assert w.properties_scroll.viewport().rect().contains(control.mapTo(w.properties_scroll.viewport(),control.rect().center()))
                assert w.properties_scroll.horizontalScrollBar().maximum()==0,horizontal_layout_metrics(w.properties_scroll)
                w.properties_scroll.verticalScrollBar().setValue(0)
            snapshot(f'{width}-editor',w)
            if not baseline:
                item=w.field_items[0];w.editor_pdf_toggle.setChecked(True);w.editor_pdf_timer.stop();w.refresh_editor_pdf()
                assert w.editor_pdf.path;assert w.field_items[0] is item
                snapshot(f'{width}-editor-pdf',w);w.editor_pdf_toggle.setChecked(False)
                w.design.mark_clean()
            dialog=StatusFieldsDialog(api,api.status_catalog.get(uids[0]),w) if baseline else None
            if not baseline:
                # Approved status revisions are not editable; clone through the
                # catalogue's existing documentary lifecycle.
                rec=api.status_catalog.get(uids[0]);clone=api.status_catalog.new_revision(rec['uid'],'SYN-'+str(width),'SYNTHETIC visual draft')
                dialog=StatusFieldsDialog(api,api.status_catalog.get(clone),w)
            dialogs.append(dialog);present_viewport(dialog,QSize(min(1150,logical.width()-24),min(760,logical.height()-24)),settle)
            snapshot(f'{width}-status',dialog)
            if not baseline:
                dialog.pdf_toggle.setChecked(True);dialog.pdf_timer.stop();dialog.refresh_pdf();assert dialog.pdf_preview.path
                snapshot(f'{width}-status-pdf',dialog);dialog.pdf_toggle.setChecked(False)
            dialog.reject();dialog.hide()
            work=api.work.create(approved,name='SYNTHETIC R8C '+str(width))
            work=api.work.save(work['uid'],work['generation'],{'values':{'lote':'SYN-01','cantidad':'1 kg','proveedor':'SYN','direccion':'SYN','telefono':'123','observaciones':'SYN'}})
            w.emission_work=work;w.refresh_work_panels();w.preview_timer.stop();w.preview_pending=False
            legacy=api.output_path('cache','r8c-historical-'+str(width)+'.pdf')
            api.work.proof(work['uid'],work['generation'],legacy)
            pdf_record(f'{width}-historical-unchanged',legacy)
            if not baseline:
                trial=EmissionAppearanceDialog(w);dialogs.append(trial)
                trial.field.setCurrentIndex(trial.field.findData('lote'));trial.font_size.setValue(9);trial.changed();trial.timer.stop();trial.preview()
                present_viewport(trial,QSize(min(1050,logical.width()-24),min(740,logical.height()-24)),settle)
                assert trial.pdf.path;snapshot(f'{width}-trial-appearance',trial);trial.apply()
                work=w.emission_work
                try:api.work.issue(work['uid'],work['generation'],'SYNTHETIC')
                except PermissionError:pass
                else:raise AssertionError('Unapproved trial reached definitive issue')
                assert api.work.get(work['uid'])['phase']=='DRAFT'
            assert w.preview_emission_work()
            w.preview_timer.stop();w.preview_pending=False;w.navigate('emission');w.emission_compact.setCurrentIndex(1);settle()
            snapshot(f'{width}-emission',w)
            if not baseline:pdf_record(f'{width}-trial',w.work_preview['path'])
            assert dict(api.version(approved))==original
        if not baseline:
            # Integrated product+status uses a NEW draft variant, never writes
            # an approved product layout. This is not an approval workaround.
            row=api.create_variant(approved,'R8C-COMB','SYNTHETIC combined','SYNTHETIC only','SYNTHETIC')
            design=json.loads(row['design_json']);design['layout']['area']=[.5,.52,.4,.4]
            row=api.save_variant(row['id'],row['generation'],design,'SYNTHETIC')
            values={'lote':'SYN-01','cantidad':'1 kg','proveedor':'SYN','direccion':'SYN','telefono':'123','observaciones':'SYN'}
            profile=dict(width_mm=140,height_mm=200,margin_mm=8,gap_mm=3,start_slot=1)
            for uid in uids:
                rec=api.status_catalog.get(uid)
                for mode in ('fit','fill'):
                    state=dict(kind=rec['kind'],revision_uid=uid,placement='integrada',fields={'lote':'SYN-01'},composition=dict(FIT,mode=mode))
                    path=api.output_path('cache','r8c-combined-'+rec['kind']+'-'+mode+'.pdf')
                    rendered=api.render(api.resolved_design(approved,row['id']),values,profile,[1],1,1,path,True,status=state)
                    assert rendered['composition'][0]['mode']==mode
                    pdf_record('combined-'+rec['kind']+'-'+mode,path)
            result['combined_cases']=6
            result.update(trial_production_blocked=True,status_exact_reprint=True)
        result.update(ok=True,exact_viewports=True,approved_revision_unchanged=True,
                      sqlite_v4=api._repository.db.execute('PRAGMA user_version').fetchone()[0]==4,
                      integrity=api._repository.db.execute('PRAGMA integrity_check').fetchone()[0]=='ok')
        assert result['sqlite_v4'] and result['integrity'] and not api.issues()
    except Exception:
        result['error']=traceback.format_exc();print(result['error'],flush=True)
    finally:
        w.shutdown_runtime()
        for dialog in dialogs:dialog.hide();dialog.deleteLater()
        w.hide();w.deleteLater();QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete);settle();session.close()
        report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    return 0 if result['ok'] else 1
