"""Packaged core check; does not certify GUI, Word or physical printing."""
import json
import tempfile
import fitz
from pathlib import Path
from . import __version__
from .paths import installation_dir, resource_dir
from .storage import Store
from .services import LocalServices

def run(destination):
    destination=Path(destination)
    with tempfile.TemporaryDirectory(prefix='covex_self_check_',dir=installation_dir()) as temp:
        api=LocalServices(Store(Path(temp)/'data'))
        try:
            # Generated here, never an imported COVEX master or real label.
            synthetic=Path(temp)/'synthetic.pdf'
            with fitz.open() as document:
                page=document.new_page(width=200,height=100)
                page.insert_text((10,30),'SYNTHETIC CORE CHECK',fontsize=10)
                document.save(synthetic)
            vid=api.add_label('DEMO - CORE CHECK','DEMO','Synthetic','','CLIENTE',
                              'Fictional test customer','00',synthetic,None,
                              [0,0,200,100],[],'Temporary software test only')
            version=api.version(vid)
            profile={'width_mm':version['base_w_mm'],'height_mm':version['base_h_mm'],
                     'orientation':'portrait','margin_mm':8,'gap_mm':3,'start_slot':1,
                     'offset_x_mm':0,'offset_y_mm':0,'safety_mm':0}
            pdf=Path(temp)/'test.pdf'
            api.render(version,{},profile,[1],1,1,pdf,True)
            assert pdf.exists() and pdf.stat().st_size>0
            result={'version':__version__,'core_check':'passed','labels':len(api.labels()),
                    'resource_directory':str(resource_dir()),
                    'not_tested':['Windows operator GUI','Word conversion','physical printing']}
        finally:api.close()
    destination.write_text(json.dumps(result,indent=2),encoding='utf-8')
