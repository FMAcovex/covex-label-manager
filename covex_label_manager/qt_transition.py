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
    @property
    def status_catalog(self):
        from .status_catalog import StatusCatalogue
        if not hasattr(self, '_status_catalogue'):
            self._status_catalogue = StatusCatalogue(self._repository.root)
        return self._status_catalogue

    def save_editor_layout(self, version_id, layout, expected, expected_source):
        return self._repository.save_pending_layout(version_id, layout, expected, expected_source)

    def editor_page_rect(self, version_id):
        import fitz
        version = self.version(version_id)
        verify_documents(version, self._repository.root)
        with fitz.open(self.asset_path(version['master_pdf'])) as document:
            return list(document[0].rect)

    def editor_spans(self, version_id):
        version = self.version(version_id)
        verify_documents(version, self._repository.root)
        return self.master_spans(version)

    def editor_template_layout(self, version_id, crop):
        version = self.version(version_id)
        verify_documents(version, self._repository.root)
        if version['name'].upper() not in ('ACETONA', 'EDROFONIO'):
            raise ValueError('Sin plantilla reconocida. Use anclas explícitas o ajuste manual.')
        from .editor_layout import validate_layout
        fields, area = self.locate_fields(version, crop)
        layout = dict(fields=fields, area=area, crop=list(crop))
        validate_layout(layout, self.editor_page_rect(version_id))
        return layout

    def preview_editor_layout(self, version_id, layout, profile):
        """Proof only: never approve, save design, or add a definitive issue."""
        import uuid
        from .editor_layout import validate_layout, version_with_layout
        from .engine import render_emission
        ok, reason = self.eligibility(version_id, False)
        if not ok: raise ValueError(reason)
        validate_layout(layout, self.editor_page_rect(version_id))
        version = version_with_layout(self.version(version_id), layout)
        path = self.output_path('cache', 'qt-layout-proof-'+uuid.uuid4().hex+'.pdf')
        warnings = render_emission(version, self._repository.root, {}, profile,
                                   [1], 1, 1, path, test_mode=True)
        return path, warnings

    def eligibility(self,version_id,production=True,variant_id=None):
        version=self.version(version_id)
        if version is None:return False,'Revisión inexistente.'
        if production and version['state']!='APPROVED':return False,'Preparar emisión requiere una revisión vigente. Puede consultar o preparar un PDF de prueba.'
        if not production and version['state']=='RETIRED':return False,'Revisión retirada: solo consulta; no generar nuevas pruebas.'
        try:
            verify_documents(version,self._repository.root);verify_renderable(version)
        except (ValueError,OSError) as ex:return False,str(ex)
        try:self._repository.variants.resolve(version_id,variant_id,production)
        except (ValueError,OSError,PermissionError) as ex:return False,str(ex)
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

