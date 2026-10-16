"""R5C: complete read-only reconciliation using synthetic data only."""
import csv
import hashlib
import json
import zipfile
import pytest
from covex_label_manager.qt_ui.demo import DemoSession
from covex_label_manager.master_reconciliation import (
    read_master,source_sheets,reconcile,export_report,report_csv
)

@pytest.fixture
def demo():
    s=DemoSession()
    yield s
    s.close()


def make_csv(path,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f,delimiter=';');writer.writerow(
            ['Denominación','Código','Rev','Estado','Idioma'])
        writer.writerows(rows)
    return path


def colmap():
    return {'name':'Denominación','version':'Rev','code':'Código','state':'Estado',
            'language':'Idioma'}


def test_coverage_missing_revision_and_app_only(demo,tmp_path):
    api=demo.services
    version=api.version(demo.initial_id)
    path=make_csv(tmp_path/'master.csv',[
        [version['name'],version['code'],version['version'],version['state'],''],
        ['Etiqueta inexistente','X-NONE','00','',''],
        [version['name'],version['code'],'999','','']])
    before=len(api.issues()),[(v['id'],v['state']) for v in api.versions(version['label_id'])]
    report=reconcile(api,path,'CSV/TSV',colmap())
    assert report['summary']['counts']['MATCHED']==1
    assert report['summary']['counts']['MISSING_LABEL']==1
    assert report['summary']['counts']['MISSING_REVISION']==1
    assert report['summary']['coverage_percent']==pytest.approx(33.33)
    assert len(report['only_in_app'])>0
    assert before==(len(api.issues()),[(v['id'],v['state']) for v in api.versions(version['label_id'])])


def test_status_and_metadata_discrepancies(demo,tmp_path):
    api=demo.services
    v=api.version(demo.initial_id)
    swapped='RETIRED' if v['state']!='RETIRED' else 'APPROVED'
    file=make_csv(tmp_path/'master.csv',[
        [v['name'],v['code'],v['version'],swapped,''],
        [v['name'],v['code'],v['version'],'','Idioma no existente']])
    report=reconcile(api,file,None,colmap())
    # Duplicate reference rows are deliberately flagged, not silently matched twice.
    assert report['summary']['counts']['STATE_DIFFERENCE']==1
    assert report['summary']['counts']['DUPLICATE_MASTER_ROW']==1
    other=make_csv(tmp_path/'metadata.csv',[
        [v['name'],v['code'],v['version'],'','Idioma distinto']])
    report=reconcile(api,other,None,colmap())
    assert report['summary']['counts']['METADATA_DIFFERENCE']==1


def test_formula_injection_escaped_and_archive_checks_sha(demo,tmp_path):
    api=demo.services
    source=make_csv(tmp_path/'master.csv',[['=HYPERLINK("x")','@ABC','00','','']])
    report=reconcile(api,source,None,colmap())
    contents=report_csv(report).decode('utf-8-sig')
    assert "'=HYPERLINK" in contents and "'@ABC" in contents
    output=tmp_path/'report.zip';export_report(api,source,report,output)
    with zipfile.ZipFile(output) as z:
        manifest=json.loads(z.read('report-manifest.json'))
        assert manifest['type']=='R5C_REPORT_NOT_BACKUP'
        assert hashlib.sha256(z.read('conciliacion.csv')).hexdigest()==manifest['files']['conciliacion.csv']
    with pytest.raises(FileExistsError):export_report(api,source,report,output)
    source.write_text('modified',encoding='utf-8')
    with pytest.raises(ValueError,match='cambiado'):
        export_report(api,source,report,tmp_path/'second.zip')


def test_duplicate_invalid_and_mapping_guard(demo,tmp_path):
    v=demo.services.version(demo.initial_id)
    path=make_csv(tmp_path/'master.csv',[
        [v['name'],v['code'],v['version'],'',''],
        [v['name'],v['code'],v['version'],'',''],
        ['','','00','','']])
    report=reconcile(demo.services,path,None,colmap())
    assert report['summary']['counts']['DUPLICATE_MASTER_ROW']==1
    assert report['summary']['counts']['INVALID_MASTER_ROW']==1
    with pytest.raises(ValueError,match='Columnas duplicadas o inexistentes'):
        reconcile(demo.services,path,None,{'name':'Denominación','version':'Denominación'})


def test_minimal_xlsx_shared_text_and_numeric_revision_is_blocked(demo,tmp_path):
    p=tmp_path/'minimal.xlsx'
    with zipfile.ZipFile(p,'w') as z:
        z.writestr('xl/workbook.xml',
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Listado" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="test" Target="worksheets/sheet1.xml"/></Relationships>')
        z.writestr('xl/sharedStrings.xml',
            '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<si><t>Nombre</t></si><si><t>Revision</t></si><si><t>Demo</t></si></sst>')
        z.writestr('xl/worksheets/sheet1.xml',
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData><row r="1"><c r="A1" t="s"><v>0</v></c>'
            '<c r="B1" t="s"><v>1</v></c></row>'
            '<row r="2"><c r="A2" t="s"><v>2</v></c>'
            '<c r="B2"><v>1</v></c></row></sheetData></worksheet>')
    assert source_sheets(p)==['Listado']
    table=read_master(p,'Listado')
    assert table['rows'][0]['numeric']==['Revision']
    report=reconcile(demo.services,p,'Listado',{'name':'Nombre','version':'Revision'})
    assert report['summary']['counts']['INVALID_MASTER_ROW']==1


def test_export_blocks_db_location_and_stale_catalog(demo,tmp_path):
    api=demo.services;v=api.version(demo.initial_id)
    source=make_csv(tmp_path/'master.csv',[[v['name'],v['code'],v['version'],'','']])
    report=reconcile(api,source,None,colmap())
    with pytest.raises(PermissionError):export_report(
        api,source,report,api._repository.root/'report.zip')
    api.set_setting('irrelevant','not-a-catalog-update')
    # Catalog changes must invalidate a preview; preferences/settings alone are not labels.
    assert export_report(api,source,report,tmp_path/'valid.zip')['rows']==1
    api.library.update_metadata(v['label_id'],{'language':'Fictional update'},'Synthetic R5C')
    with pytest.raises(ValueError,match='catálogo'):
        export_report(api,source,report,tmp_path/'stale.zip')
