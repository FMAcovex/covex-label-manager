"""Small local Qt transition adapter; existing engine and schema are unchanged."""
from dataclasses import dataclass, field
from .services import LocalServices
from .integrity import verify_documents, verify_renderable

@dataclass
class ActiveWork:
    version_id: int | None = None
    kind: str = 'editor'
    values: dict = field(default_factory=dict)
    dirty: bool = False

class TransitionServices(LocalServices):
    def eligibility(self,version_id,production=True):
        version=self.version(version_id)
        if version is None:return False,'Revisión inexistente.'
        if production and version['state']!='APPROVED':return False,'Preparar emisión requiere una revisión vigente. Puede consultar o preparar un PDF de prueba.'
        if not production and version['state']=='RETIRED':return False,'Revisión retirada: solo consulta; no generar nuevas pruebas.'
        try:
            verify_documents(version,self._repository.root);verify_renderable(version)
        except (ValueError,OSError) as ex:return False,str(ex)
        return True,''
    def open_document(self,version_id,original=False):
        version=self.version(version_id)
        verify_documents(version,self._repository.root)
        key='original_file' if original else 'master_pdf'
        if not version[key]:raise ValueError('No hay documento original asociado.')
        return self.asset_path(version[key])
    def remember_filters(self,remember,expanded):
        self.set_setting('qt_remember_filters','1' if remember else '0')
        self.set_setting('qt_filters_expanded','1' if remember and expanded else '0')
    def filter_preferences(self):
        remember=self.setting('qt_remember_filters','0')=='1'
        return remember,remember and self.setting('qt_filters_expanded','0')=='1'
