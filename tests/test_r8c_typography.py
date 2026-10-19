"""R8C real PDF geometry and content, exclusively SYNTHETIC fixtures."""
from copy import deepcopy
import json
from pathlib import Path
import fitz
import pytest
from covex_label_manager.typography import DEFAULT,validate,paint,rgb,font_resource,apply_trial,contrast_warning
from covex_label_manager.status_scaling import geometry,paint as paint_status,critical_losses,DEFAULT as FIT
from covex_label_manager.status_design import make_layout,validate_layout,render_proof
from test_emission_work import work
from test_r7b_status_combined import context


@pytest.mark.parametrize('family',['sans','serif','mono'])
@pytest.mark.parametrize('bold,italic',[(False,False),(True,False),(False,True),(True,True)])
def test_real_embedded_fonts_styles_and_pdf_color(family,bold,italic,tmp_path):
    with fitz.open() as doc:
        page=doc.new_page(width=350,height=160)
        style=dict(DEFAULT,family=family,italic=italic,color='#1234AB')
        assert not paint(page,'SYNTHETIC Áéñ 123',fitz.Rect(20,20,330,100),12,bold,style)
        path=tmp_path/'font.pdf';doc.save(path)
    with fitz.open(path) as doc:
        spans=[s for b in doc[0].get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans']]
        assert spans[0]['text']=='SYNTHETIC Áéñ 123'
        assert spans[0]['color']==0x1234AB
        assert abs(spans[0]['size']-12)<.01
        font_id=doc[0].get_fonts()[0][0]
        assert len(doc.extract_font(font_id)[3])>1000 # actual embedded resource
        assert bool(spans[0]['flags']&16)==bold
        assert bool(spans[0]['flags']&2)==italic


@pytest.mark.parametrize('align,fraction',[('left',0),('center',.5),('right',1)])
@pytest.mark.parametrize('valign,fraction_y',[('top',0),('middle',.5),('bottom',1)])
def test_alignment_and_source_box_exact_metrics(align,fraction,valign,fraction_y):
    with fitz.open() as doc:
        page=doc.new_page();box=fitz.Rect(20,30,220,110);size=12
        paint(page,'SYNTHETIC',box,size,False,dict(DEFAULT,align=align,valign=valign))
        span=page.get_text('dict')['blocks'][0]['lines'][0]['spans'][0]
        font,_=font_resource('sans');width=font.text_length('SYNTHETIC',fontsize=size)
        assert span['origin'][0]==pytest.approx(box.x0+(box.width-width)*fraction,abs=.005)
        height=(font.ascender-font.descender)*size
        assert span['bbox'][1]==pytest.approx(box.y0+(box.height-height)*fraction_y,abs=.005)
        assert box.contains(fitz.Rect(span['bbox']))


@pytest.mark.parametrize('patch',[{'family':'ArialInstalled'}, {'color':'red'}, {'color':'#FFFF'}, {'italic':1},{'wrap':'shrink'},{'overflow':'clip'},{'contract':True},{'valign':'baseline'}])
def test_invalid_font_color_and_contract_fail_closed(patch):
    with pytest.raises(ValueError):validate(dict(DEFAULT,**patch))


def test_wrap_overflow_minimum_glyph_and_missing_resource(monkeypatch):
    with fitz.open() as doc:
        page=doc.new_page();box=fitz.Rect(20,20,110,150)
        paint(page,'SYNTHETIC ONE TWO THREE',box,12,False,DEFAULT)
        assert len(page.get_text('dict')['blocks'][0]['lines'])>=2
        for text,rect,size,style in [('VERYVERYLONGWORD',fitz.Rect(0,0,5,30),12,DEFAULT),
                ('A',fitz.Rect(0,0,80,2),12,DEFAULT),('A',box,5,DEFAULT),
                ('A\nB',box,12,dict(DEFAULT,wrap='none')),('未知',box,12,DEFAULT)]:
            if text=='A\nB':continue # explicit newlines are allowed in general text
            with pytest.raises(ValueError):paint(page,text,rect,size,False,style)
        font_resource.cache_clear()
        monkeypatch.setattr(fitz,'Font',lambda **_:(_ for _ in ()).throw(RuntimeError('SYNTHETIC missing resource')))
        with pytest.raises(ValueError,match='no disponible'):paint(page,'A',box,12,False,DEFAULT)
        font_resource.cache_clear()


def source(tmp_path,*,edge=False,color=(.25,.8,.4),styled=True):
    path=tmp_path/'SYNTHETIC-R8C.pdf'
    with fitz.open() as pdf:
        p=pdf.new_page(width=200,height=100)
        p.draw_rect(p.rect,fill=color,color=None)
        p.insert_text((75,28),'SYNTHETIC',fontsize=8)
        if edge:p.insert_text((2,80),'CRITICAL EDGE',fontsize=6)
        pdf.save(path)
    layout=make_layout(path,'aprobado')
    layout['fields']=[dict(key='lote',label='Lote',rect=[75,40,125,60],font_size=8,bold=False,required=True)]
    if styled:
        layout['contract']=2;layout['fields'][0].update(typography=deepcopy(DEFAULT),example='SYN-01')
    return path,layout


@pytest.mark.parametrize('mode',['fit','fill'])
def test_background_and_fields_share_exact_transform_and_uniform_scale(tmp_path,mode):
    path,layout=source(tmp_path)
    with fitz.open(path) as src,fitz.open() as out:
        page=out.new_page(width=250,height=250);target=fitz.Rect(25,25,225,225)
        report=paint_status(page,src,layout,{'lote':'SYN-01'},target,settings=dict(FIT,mode=mode))
        factor=report['scale'];placed=fitz.Rect(report['placed']);clip=fitz.Rect(report['source_clip'])
        spans={s['text']:s for b in page.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans']}
        assert 'SYNTHETIC' in spans and 'SYN-01' in spans
        assert spans['SYNTHETIC']['origin'][0]==pytest.approx(placed.x0+(75-clip.x0)*factor,abs=.01)
        assert spans['SYN-01']['origin'][0]==pytest.approx(placed.x0+(75-clip.x0)*factor,abs=.01)
        assert spans['SYN-01']['size']==pytest.approx(8*factor,abs=.01)
        assert target.contains(fitz.Rect(spans['SYN-01']['bbox']))
        assert not report['critical_losses']
        if mode=='fit':assert report['free_mm'][1]>0
        else:assert report['cropped_mm'][0]>0 and report['free_mm']==[0,0]
        # Actual page raster retains original green background, not a repaint.
        pix=page.get_pixmap();assert pix.pixel(30,130)[1]>150


def test_fill_rejects_fixed_text_fields_symbols_and_borders(tmp_path):
    path,layout=source(tmp_path,edge=True)
    with fitz.open(path) as src,fitz.open() as out:
        page=out.new_page()
        with pytest.raises(ValueError,match='texto fijo'):
            paint_status(page,src,layout,{'lote':'SYN'},fitz.Rect(0,0,100,100),settings=dict(FIT,mode='fill'))
        for field in layout['fields']:field['rect']=[2,40,50,60]
        losses=critical_losses(src[0],layout,[50,0,150,100]);assert any('campo variable' in x['content'] for x in losses)
        src[0].draw_line((0,10),(200,10));assert any('trazo' in x['content'] for x in critical_losses(src[0],layout,[50,0,150,100]))


def test_status_contract2_roundtrip_proof_contrast_and_legacy(tmp_path):
    path,layout=source(tmp_path)
    with fitz.open(path) as src:
        assert validate_layout(layout,src)==layout
        broken=deepcopy(layout);broken['contract']=1
        with pytest.raises(ValueError,match='contrato'):validate_layout(broken,src)
        assert contrast_warning(src[0],layout['fields'][0]['rect'],'#40CC66')
    proof=render_proof(path,layout,{'lote':'SYN-01'},tmp_path/'proof.pdf',width_mm=70,height_mm=70,composition=dict(FIT,mode='fill'))
    with fitz.open(proof) as doc:
        assert 'SYN-01' in doc[0].get_text() and 'PRUEBA' in doc[0].get_text()
    bad=deepcopy(layout);bad['fields'][0]['typography']['color']='#40CC66'
    with fitz.open(path) as src,fitz.open() as out:
        with pytest.raises(ValueError,match='Contraste'):
            paint_status(out.new_page(),src,bad,{'lote':'SYN'},fitz.Rect(0,0,200,100))
    legacy=deepcopy(layout);legacy['contract']=1
    for f in legacy['fields']:f.pop('typography');f.pop('example')
    with fitz.open(path) as doc:assert validate_layout(legacy,doc)==legacy


def test_trial_persists_values_and_blocks_before_intent_and_direct_engine(work,tmp_path):
    api,w=work;version=dict(api.version(w['binding']['revision_id']));before=deepcopy(version)
    trial=dict(contract=1,fields={'lote':{'font_pt':9,'typography':dict(DEFAULT,color='#112233')}})
    profile=dict(w['profile'],trial_appearance=trial)
    w=api.work.save(w['uid'],w['generation'],{'profile':profile})
    assert json.loads(api.work.path(w['uid']).read_text())['contract']==3
    reopened=api.work.get(w['uid']);assert reopened['values']==w['values']
    assert not api.review_work(w['uid'],w['generation'])['production_allowed']
    result=api.work.proof(w['uid'],w['generation'],tmp_path/'trial.pdf')
    with fitz.open(result['path']) as doc:
        assert 'PRUEBA' in doc[0].get_text() and 'SYNTH' in doc[0].get_text()
    with pytest.raises(PermissionError,match='temporales'):api.work.issue(w['uid'],w['generation'],'SYNTHETIC')
    assert api.work.get(w['uid'])['phase']=='DRAFT' and not api.issues()
    from covex_label_manager.engine import render_emission
    with pytest.raises(ValueError,match='temporales'):
        render_emission(version,Path(api.location()),w['values'],profile,[1],1,1,tmp_path/'forbidden.pdf',False)
    assert not (tmp_path/'forbidden.pdf').exists() and dict(api.version(version['id']))==before
    clone=api.work.create(version['id'],name='Reusable SYNTHETIC',template=w)
    assert clone['profile']['trial_appearance']==trial and clone['phase']=='DRAFT'
    profile.pop('trial_appearance');restored=api.work.save(w['uid'],w['generation'],{'profile':profile})
    assert 'trial_appearance' not in api.work.get(restored['uid'])['profile']


def test_trial_rejects_fixed_artwork_identity_and_locked_geometry(work):
    api,w=work;v=dict(api.version(w['binding']['revision_id']))
    for key,patch in [('texto_fijo',{'text':'unsafe'}),('lote',{'erase':[0,0,1,1]}),('lote',{'font_pt':float('nan')}),('lote',{'x':2})]:
        with pytest.raises(ValueError):apply_trial(v,dict(contract=1,fields={key:patch}))
    fields=json.loads(v['fields_json']);next(f for f in fields if f['key']=='lote')['locked']=True
    v['fields_json']=json.dumps(fields)
    with pytest.raises(ValueError,match='Campo bloqueado: lote'):apply_trial(v,dict(contract=1,fields={'lote':{'x':.1}}))


def test_combined_explicit_fit_keeps_documentary_identity_and_records_transform(context,tmp_path):
    store,api,catalog,v,p,values,uids=context
    state=dict(kind='aprobado',revision_uid=uids[1],placement='integrada',fields={'firma':'SYNTHETIC'},composition=FIT)
    result=api.render(v,values,p,[1],1,1,tmp_path/'combined.pdf',True,status=state)
    assert result['composition'] and result['composition'][0]['mode']=='fit'
    with fitz.open(result['path']) as doc:assert 'FICTICIO APROBADO' in doc[0].get_text()
    state['composition']=dict(FIT,mode='fill')
    with pytest.raises(ValueError,match='Relleno bloqueado'):api.render(v,values,p,[1],1,1,tmp_path/'blocked.pdf',True,status=state)
    assert not (tmp_path/'blocked.pdf').exists()


@pytest.mark.parametrize('kind,color',[('sin_analizar',(1,.92,.3)),('aprobado',(.25,.8,.4)),('rechazado',(.9,.3,.3))])
def test_standalone_approved_contract2_fill_and_exact_historical_copy(tmp_path,kind,color):
    from covex_label_manager.status_catalog import StatusCatalogue
    from covex_label_manager.storage import sha256
    path,layout=source(tmp_path,color=color);layout['kind']=kind
    catalog=StatusCatalogue(tmp_path/'isolated');uid=catalog.import_many(path,[dict(kind=kind,revision='00',layout=layout)])[0]
    with pytest.raises(PermissionError):catalog.emit(uid,{'lote':'SYN'},'SYN')
    catalog.submit(uid);catalog.approve(uid,'SYN QA','SYNTHETIC EXTERNAL',confirmation=True)
    issue,pdf=catalog.emit(uid,{'lote':'SYN-01'},'SYN',width_mm=70,height_mm=70,composition=dict(FIT,mode='fill'))
    original=sha256(pdf)
    record,checked=catalog.inspect_issue(issue)
    snapshot=json.loads(record['snapshot_json'])
    assert snapshot['layout']==layout and snapshot['profile']['composition']['mode']=='fill'
    assert checked==pdf
    catalog.retire(uid,'SYNTHETIC retired after issue')
    _,reprinted=catalog.reprint(issue,'SYN','SYNTHETIC damaged original')
    assert sha256(reprinted)==original and reprinted.read_bytes()==pdf.read_bytes()


def test_trial_invalid_patch_and_version_cannot_downgrade_work(work):
    from covex_label_manager.canonical import digest
    from covex_label_manager.emission_work import WorkUnsupported
    api,w=work
    trial=dict(contract=1,fields={'lote':{'typography':deepcopy(DEFAULT)}})
    w=api.work.save(w['uid'],w['generation'],{'profile':dict(w['profile'],trial_appearance=trial)})
    path=api.work.path(w['uid']);envelope=json.loads(path.read_text());envelope['contract']=1
    path.write_text(json.dumps(envelope),encoding='utf-8')
    with pytest.raises(WorkUnsupported):api.work.get(w['uid'])


def test_contrast_does_not_claim_uniform_background_from_only_corners():
    with fitz.open() as doc:
        page=doc.new_page(width=100,height=100);page.draw_rect(page.rect,fill=(1,1,1),color=None)
        # Not at a corner or the centre: a nine-point sample would miss it.
        page.draw_rect(fitz.Rect(18,18,28,28),fill=(0,0,0),color=None)
        assert contrast_warning(page,page.rect,'#FFFFFF') is None


@pytest.mark.parametrize('kind',['sin_analizar','aprobado','rechazado'])
def test_legacy_status_composition_registers_fonts_on_its_own_source_layer(context,tmp_path,kind):
    store,api,catalog,v,p,values,uids=context
    status=dict(kind=kind,placement='integrada',fecha='19/10/2026',persona='SYN',composition=FIT)
    result=api.render(v,values,p,[1],1,1,tmp_path/(kind+'-legacy.pdf'),True,status=status)
    assert result['composition'] and result['composition'][0]['mode']=='fit'
    with fitz.open(result['path']) as doc:
        assert '19/10/2026' in doc[0].get_text() and 'PRUEBA' in doc[0].get_text()


def test_legibility_uses_final_physical_size_not_source_size(tmp_path):
    path,layout=source(tmp_path);layout['fields'][0]['font_size']=5
    with fitz.open(path) as src,fitz.open() as out:
        page=out.new_page()
        result=paint_status(page,src,layout,{'lote':'SYN'},fitz.Rect(0,0,400,200))
        assert not result['warnings'] # 5 source points × 2 = 10 printed points
        with pytest.raises(ValueError,match='demasiado pequeño'):
            paint_status(page,src,layout,{'lote':'SYN'},fitz.Rect(0,250,100,300))


def test_tiny_fixed_source_text_warns_in_proof_and_blocks_definitive(tmp_path):
    path=tmp_path/'SYNTHETIC-TINY-FIXED.pdf'
    with fitz.open() as src:
        page=src.new_page(width=200,height=100);page.insert_text((60,30),'SYNTHETIC TINY',fontsize=3);src.save(path)
    layout=make_layout(path,'aprobado')
    with fitz.open(path) as src,fitz.open() as out:
        page=out.new_page()
        report=paint_status(page,src,layout,{},fitz.Rect(0,0,200,100),strict=False)
        assert any('Texto fijo demasiado pequeño' in warning for warning in report['warnings'])
        with pytest.raises(ValueError,match='Texto fijo demasiado pequeño'):
            paint_status(page,src,layout,{},fitz.Rect(0,120,200,220),strict=True)


def test_trial_move_preserves_anchor_mask_and_continuation_contracts(work):
    api,w=work;v=dict(api.version(w['binding']['revision_id']))
    fields=json.loads(v['fields_json']);field=next(f for f in fields if f['key']=='lote')
    field['locked']=False;field['anchor']={'dx_pt':1.5,'dy_pt':0}
    field['erase']=[field['x'],field['y'],.05,.02]
    field['second_x']=field['x'];field['next_w']=.05
    before=deepcopy(field);v['fields_json']=json.dumps(fields)
    delta=-.005 if field['x']>.005 else .005
    effective=apply_trial(v,dict(contract=1,fields={'lote':{'x':field['x']+delta}}))
    changed=next(f for f in json.loads(effective['fields_json']) if f['key']=='lote')
    width=json.loads(v['crop_json'])[2]-json.loads(v['crop_json'])[0]
    assert changed['erase'][0]==pytest.approx(before['erase'][0]+delta)
    assert changed['second_x']==pytest.approx(before['second_x']+delta)
    assert changed['anchor']['dx_pt']==pytest.approx(before['anchor']['dx_pt']+delta*width)
    assert json.loads(v['fields_json'])==fields # no original layout mutation
