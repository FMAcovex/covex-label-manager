# R8-RC1 — revisión funcional consolidada

Fuente revisada: `main` **504e542b17bbb8bfe2210fca8c9e19016aa42970**. Árbol **10cf8dd37ed7c10c65e97ebd96ca826ce2144645**, idéntico a R8D **ac4542de2f0195f84474f12de67ee9b349555cc4**. Verificado por Git, no sólo por nombres de ramas. #33, #34, #35 y #36 constan MERGED, en ese orden, el 19/10/2026. Esta fase no realiza fusiones, tags ni releases y no añade funcionalidad.

## Interfaces y comprobaciones de comportamiento

Se revisaron las rutas compartidas, sus guardas y pruebas operativas. La tabla identifica evidencia automatizada, no conformidad manual de 87 tareas. La [matriz de conservación de las 87 capacidades](../R8D_GUIDED_WORKFLOW/CONSERVACION_87.md) sigue siendo la referencia de IDs/nombres y rutas Qt/Legacy; sus pruebas de igualdad no bastan por sí solas para demostrar funcionamiento. Los resultados de ejecución sobre main se consignan en ENTREGA.md.

| Interfaz | Contrato que se conserva / comprobación funcional | Pruebas y ejecutables |
| --- | --- | --- |
| Biblioteca → Editor | Abrir no emite; edición se guarda y recupera; cambio de selección con texto pendiente no descarta silenciosamente | `test_r3a_qt.py`: open_editor_is_not_emission, dirty_work_persists_navigation_and_saves, cancel_revision_change_retains_dirty_work; `test_r8b_editor_ux_qt.py`: dibujo real, undo, selección, guardado |
| Editor → Variantes | Revisión vigente protegida; variante DRAFT independiente; menú contextual y guardas de estado; cambios no aprueban original | `test_variants_v4.py`, `test_r3e_qt.py`, `test_r8b_editor_ux_qt.py`: locked_field_controls_and_read_only_revision_no_bypass, variant_command_opens_actual_menu_and_context_help |
| Biblioteca → Emisión | Identidad revisión/variante explícita; pendiente permite prueba pero no definitiva; retiradas bloqueadas | `test_r3c_emission_qt.py`, `test_r8d_guided_qt.py`: pending_proof_allowed_but_definitive_blocked, ambiguous_results_require_explicit_selection_and_retired_block |
| Guiado ↔ Centro avanzado | Misma identidad, generación y datos persistidos; CAS impide sobrescritura; sin motor/repositorio nuevo | `guided_workflow.py`, `emission_centre.py`; `test_r8d_guided_qt.py`: four_steps_back_values_quantities_and_same_advanced_work, real_cas_conflict_blocks_navigation_and_keeps_unsaved_input |
| Producto → Estado | Revisión de estado explícita; geometría común, fit/fill protegido, contratos históricos preservados | `test_r8c_typography.py`: transformaciones, recortes, reimpresión histórica, contrato 2; `test_r8d_guided_qt.py`: status_revision_and_both_scaling_modes_real_pdf; checks R8C del EXE extraído |
| Prueba → Definitiva | Preview del mismo UID/generación/hash; trial bloquea antes de INTENT/motor; confirmación humana; cancelación sin registro | `test_r8c_typography.py`: trial_persists_values_and_blocks_before_intent_and_direct_engine; `test_r8d_guided_qt.py`: preview_tampering_never_registers_a_definitive_issue, human_cancels_definitive_confirmation_without_issue |
| Emisión → Historial → Reimpresión | PDF registrado verificable, original intacto, vínculo de reimpresión con motivo, no doble emisión del trabajo | `test_r8d_guided_qt.py`: authorized_issue_proof_export_history_duplicate_and_reprint; grupos históricos; check R8D extraído usa acciones/servicios/PDF reales |
| Autoguardado → Cierre → Recuperación | Error al guardar no autoriza cierre; espera al trabajador; borrador recuperable sin copiar valores críticos a nuevo lote | `test_r8a_stability_qt.py`: database_error_on_autosave_never_accepts_close_or_loses_pending_work, exception_inside_close_guard_cannot_authorize_qt_shutdown, shutdown_waits_for_worker_before_session_release; `test_r8d_guided_qt.py`: resume_saved_work_no_critical_defaults_for_new_lot; gate migración abrupta |
| Diseño → Aprobación documental | Trial genera PRUEBA; variante nueva DRAFT exige ciclo externo, no aprobación automática; maestro aprobado inalterado | `test_r8c_typography_qt.py`: trial_can_only_create_documentary_draft_then_requires_external_evidence; `test_r8d_guided_qt.py`: variant_specific_required_fields_and_unapproved_choice; variantes v4 |

Los nombres de pruebas se muestran sin el prefijo `test_`. Se comprueban widgets reales, persistencia y PDFs; las confirmaciones humanas simuladas en tests se limitan a fixtures sintéticos aislados, no son aprobaciones de documentos del usuario ni evidencia de validación GMP.

## Capas conservadas

- **R8A:** ciclo de vida Qt, cierre y cancelaciones, concurrencia/obsolescencia, SQLite v4 y diagnósticos privados.
- **R8B:** Editor de tres zonas, dibujo y selección, propiedades, guardar, undo/redo, herramientas técnicas y variantes accesibles.
- **R8C:** tipografía embebida verificable, geometría/legibilidad, estados con escala proporcional/recorte protegido, ajustes temporales limitados a prueba, histórica/reimpresión sin reinterpretación.
- **R8D:** Inicio y asistente de cuatro pasos, mismo trabajo que Centro avanzado, datos/recipientes/unidades, PDF real, prueba/definitiva, historial, recuperación y errores operativos.
- **Heredadas:** 87 IDs/nombres y rutas Qt/Legacy, versiones/variantes, evidencias/aprobaciones externas, auditoría, emisión/historial y SQLite `user_version=4`. No se desarrolla ni migra esquema en RC1.

## Alcance y límites

Los tests no certifican cada capacidad en cada instalación corporativa. Word real, impresión física, estaciones Windows 10/11, uso prolongado de operarios y aprobación documental quedan pendientes. Los tamaños exactos se comprueban también con el backend Qt offscreen en Windows; no confundir eso con una sesión manual en un monitor físico a cada DPI. Los ensayos nativos del job complementan, no reemplazan, esas pruebas.

La propuesta antigua «no fusionar aún» del plan R8 se conserva como registro de aquella fase: las cuatro fusiones ya las realizó el propietario; este paquete constata su estado y no autoriza otras. Si se reproduce un defecto bloqueante, documentarlo y preparar una PR correctiva independiente contra main, sin fusionarla automáticamente. Los ajustes menores se agrupan después de la aceptación.

## Licencias antes del despliegue

Revisión legal/IT **pendiente**, no subsanada por CI verde ni por empaquetar textos de licencia:

- PyMuPDF/MuPDF: régimen dual AGPL/comercial y obligaciones aplicables a la aplicación/distribución corporativa; confirmar licencia adecuada con el titular/asesoría.
- PySide6/Qt y componentes: verificar módulos realmente redistribuidos, régimen LGPL/GPL/comercial, avisos y obligaciones de distribución/reemplazo que procedan; no asumir exención por ser portable o uso interno.
- Recursos URW: doce fuentes incluidas por MuPDF, licencia SIL OFL 1.1, texto [URW-FONTS-OFL.txt](../R8C_TYPOGRAPHY_SCALING/URW-FONTS-OFL.txt) incluido en ZIP. No se añaden TTF propietarios. Revisar por separado fuentes y maestros históricos del usuario y sus permisos de incorporación/impresión.
- Microsoft Word o conversor instalado y controladores de impresión: licencias y compatibilidad del entorno autorizado; no se redistribuyen Word ni licencias corporativas en CI.
- Completar inventario/avisos y autorización de distribución de dependencias recogidas en BUILD_MANIFEST.json; su inventario técnico no es un informe de cumplimiento legal.

Cierre técnico sólo tras completar satisfactoriamente las tres CI de main, integridad y EXE extraído. Aceptación funcional, aprobación documental, autorización productiva y validación GMP siguen separadas y pendientes de decisión externa.
