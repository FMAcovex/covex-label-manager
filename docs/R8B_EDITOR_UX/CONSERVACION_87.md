# Conservación de las 87 capacidades en R8B

Mismos 87 IDs, nombres y categorías que [R6B integrada](../R6B_UX_INTEGRATED/CONSERVACION_87.md). No se elimina ni renumera ninguna capacidad. R7A/R7B y diagnóstico R8A son ampliaciones conservadas, no sustitutos de esta matriz.

Las rutas E01–E15 y D08/D09/D11 se actualizan para R8B. Las restantes conservan su ruta y regresión histórica. La suite completa se mantiene; esta correspondencia no certifica cada combinación de datos, dispositivo o procedimiento GMP. Ninguna prueba sintética aprueba documentos del usuario ni valida Word/impresión/equipos reales.

| ID | Capacidad | Disponibilidad conservada | Ruta efectiva R8B / equivalencia | Regresión |
|---|---|---|---|---|
| B01 | Inicio Biblioteca y navegación horizontal | Ruta Qt | Biblioteca; StudioWindow/BaseFunctionalWindow | tests/test_r3a_qt.py |
| B02 | Tabla, selección única, abrir doble clic/Enter | Ruta Qt | Tabla → selección, doble clic/Enter; StudioWindow.selected / BaseFunctionalWindow.open_editor | tests/test_r3a_qt.py::test_enter_opens_only_from_table_not_search |
| B03 | Búsqueda dinámica código/nombre/producto/cliente/metadatos | Ruta Qt | Biblioteca; StudioWindow/BaseFunctionalWindow | tests/test_r3a_qt.py |
| B04 | Ctrl+K / buscador rápido | Ruta Qt | Ctrl+K → StudioWindow.quick_search | tests/test_r3a_qt.py |
| B05 | Filtros categoría/familia/tipo/origen/cliente/país/idioma/versión/estado/incorporación | Ruta Qt | Biblioteca; StudioWindow/BaseFunctionalWindow | tests/test_r3a_qt.py |
| B06 | Limpiar búsqueda y filtros | Ruta Qt | Biblioteca; StudioWindow/BaseFunctionalWindow | tests/test_r3a_qt.py |
| B07 | Favoritas / marcar y desmarcar | Ruta Qt | Biblioteca; StudioWindow/BaseFunctionalWindow | tests/test_r3a_qt.py |
| B08 | Recientes y última revisión abierta | Ruta Qt | Biblioteca; StudioWindow/BaseFunctionalWindow | tests/test_r3a_qt.py |
| B09 | Previsualización documento | Ruta Qt | Inspector → Preview / Ampliar; StudioWindow.enlarge | tests/test_r3a_qt.py |
| B10 | Revisiones y estado independiente del nombre | Ruta Qt | Biblioteca; StudioWindow/BaseFunctionalWindow | tests/test_r3a_qt.py |
| B11 | Columnas código/nombre/tipo/versión/origen/cliente/país/estado | Ruta Qt | Biblioteca; StudioWindow/BaseFunctionalWindow | tests/test_r3a_qt.py |
| B12 | Ocultar/ajustar filtros e inspector | Ruta Qt | Más filtros / Inspector / Paneles / Ampliar lienzo: visibilidad explícita, no ocultación automática de Elementos. | tests/test_r3a_qt.py::test_compact_auto_fold_does_not_forget_manual_preference |
| B13 | Retener filtros/selección al navegar | Ruta Qt | Biblioteca; StudioWindow/BaseFunctionalWindow | tests/test_r3a_qt.py |
| D01 | Ficha: datos, dimensiones, revisiones, referencias | Ruta Qt | Documento → Ficha completa; Inspector → Ficha completa y referencias. | tests/test_r3a_qt.py; tests/test_variants_v4.py |
| D02 | Abrir PDF maestro en visor externo | Ruta Qt | Documento o Inspector → Abrir PDF maestro → open_document(False). | tests/test_r3a_qt.py; tests/test_variants_v4.py |
| D03 | Originales y documentos conservados localmente | Mixta | Documento o Inspector → Abrir original → open_document(True); motor de conservación intacto. | tests/test_r5a_catalog.py; tests/test_core.py |
| D04 | COVEX/cliente, nombre y referencia cliente | Ruta Qt | Importar PDF/Word y carpeta controlada; import_document / ControlledImportDialog | tests/test_r3f_qt.py; tests/test_r5b_migration.py |
| D05 | Incorporación distinta de origen/estado | Ruta Qt | Biblioteca → Documento / Intercambio; BaseFunctionalWindow | tests/test_r3a_qt.py; tests/test_variants_v4.py |
| D06 | Editar metadatos con fuente obligatoria | Ruta Qt | Documento → Editar metadatos con fuente → edit_metadata. | tests/test_r3a_qt.py; tests/test_variants_v4.py |
| D07 | Nueva revisión, código y motivo | Ruta Qt | Documento → Crear nueva revisión → clone_revision, sin aprobación. | tests/test_r3a_qt.py::test_clone_is_pending_and_approval_retires_previous |
| D08 | Revisiones heredadas, incluida 00-R1; variantes independientes desde R3B2 | Ruta Qt | Biblioteca → Revisiones y variantes; Editor → Gestionar variantes. Mismos controladores y selección de revisión/variante. | tests/test_variants_v4.py; tests/test_r3a_qt.py; tests/test_r8b_editor_ux_qt.py |
| D09 | Registrar aprobación externa con responsable/evidencia/confirmación | Ruta Qt | Inspector o Documento → Registrar aprobación externa solo en estado aplicable; mismas evidencias/confirmación/servicios. | tests/test_r3a_qt.py::test_native_approval_requires_confirmation_and_keeps_state_on_cancel; tests/test_r8b_editor_ux_qt.py |
| D10 | Retirar vigente anterior al aprobar nueva; consulta retirada | Ruta Qt | Registro de aprobación externa → api.approve; consulta de Retirada | tests/test_r3a_qt.py::test_clone_is_pending_and_approval_retires_previous |
| D11 | Vigente no editable; clonar para modificar | Ruta Qt | Diseño protegido y mensaje visible → Crear variante editable… desde revisión vigente. Restricciones se revalidan en servicios. | tests/test_r3e_qt.py; tests/test_variants_v4.py; tests/test_r8b_editor_ux_qt.py |
| D12 | Integridad antes de clonar/aprobar/emitir | Motor/procedimiento | Guardas verify_documents / verify_renderable / review_work; sin botón propio | tests/test_core.py; tests/test_variants_v4.py; tests/test_r3c_emission_qt.py |
| D13 | Fuente 00 defectuosa bloqueada, 00-R1 pendiente sin autoaprobación | Motor/procedimiento | Guardas integrity/render_geometry; no autoaprobación de 00-R1 | tests/test_r1.py; tests/test_migration_v4.py |
| D14 | Comparador básico de imágenes, datos y campos | Ruta Qt | Documento → Comparar revisiones; Variantes → Comparar revisión y variante. | tests/test_r3f_qt.py::test_native_comparison_does_not_mutate_document |
| I01 | Importar PDF/Word individual y datos obligatorios | Mixta | Intercambio → Importar PDF/Word → import_document; Word instalado sigue pendiente de ensayo real. | tests/test_core.py (Word omitido); tests/test_r3a_qt.py::test_import_pdf_remains_pending |
| I02 | Importar carpeta, progreso, detener, resumen/errores | Ruta Qt | Intercambio → Importar carpeta → ControlledImportDialog; FolderImportDialog/Tk conservados como contingencia. | tests/test_r3f_qt.py; tests/test_r5b_migration.py |
| I03 | Conversión Word local y errores por dependencia | Motor/procedimiento | Motor importer.docx_to_pdf, integración local externa | tests/test_core.py (ensayo Word real omitido) |
| I04 | Recorte automático, geometría, rechazo multipágina | Motor/procedimiento | Motor de importación auto_crop y validación de página | tests/test_core.py; tests/test_r1.py |
| I05 | Importar crea pendiente, nunca aprobación | Motor/procedimiento | Motor add_label / catalog_migration_apply: siempre PENDING | tests/test_r5b_migration.py; tests/test_r3a_qt.py::test_import_pdf_remains_pending |
| E01 | Selección de campo por lista/lienzo | Ruta Qt | Elementos / clic en lienzo → select_field, list_selection, scene_selection. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py; tests/test_r8b_editor_ux_qt.py |
| E02 | Mover campo y bloquear posición | Ruta Qt | Propiedades → Bloquear posición; arrastre → finish_graphic_gesture (protección R8A). | tests/test_r3b1_qt.py; tests/test_r3e_qt.py; tests/test_r8b_editor_ux_qt.py |
| E03 | Agregar/quitar campos, clave única | Ruta Qt | Elementos → Añadir campo / Dibujar campo / Eliminar campo. Campo técnico → Añadir campo especial… conserva numeración/texto fijo. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py; tests/test_r8b_editor_ux_qt.py |
| E04 | Identificador y nombre visible | Ruta Qt | Propiedades siempre desplegadas → Nombre visible / Identificador; actualización sin reconstruir la escena. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py; tests/test_r8b_editor_ux_qt.py |
| E05 | X/Y/ancho/alto en mm y validación | Ruta Qt | Propiedades → Posición X/Y, Anchura/Altura; commit_pending_properties antes de selección, cierre o guardado. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py; tests/test_r8b_editor_ux_qt.py |
| E06 | Fuente/tamaño, negrita, obligatorio | Ruta Qt | Propiedades → Tamaño de texto / Negrita / Campo obligatorio. No se añaden familias tipográficas (R8C). | tests/test_r3b1_qt.py; tests/test_r3e_qt.py; tests/test_r8b_editor_ux_qt.py |
| E07 | Recortar por coordenadas/selección visual | Ruta Qt | Herramientas → Documento → Recorte visual / mm. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py; tests/test_r8b_editor_ux_qt.py |
| E08 | Zona de estado y control de proporciones | Ruta Qt | Herramientas → Estado y límites → Zona de estado visual / mm. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py; tests/test_r8b_editor_ux_qt.py |
| E09 | Anclar a frase Word/PDF de referencia | Ruta Qt | Herramientas → Documento → Anclar a referencia. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py; tests/test_r8b_editor_ux_qt.py |
| E10 | Relocalizar desde Word reconocido | Ruta Qt | Herramientas → Documento → Relocalizar referencias; mismas fuentes reconocidas. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py; tests/test_r8b_editor_ux_qt.py |
| E11 | Guardar configuración de borrador sin tocar original | Ruta Qt | Pie persistente → Guardar diseño / Guardar variante → save_work; mismos cotejos de fuente/generación/hash. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py; tests/test_r8b_editor_ux_qt.py |
| E12 | Reajuste avanzado de posiciones/recorte/zona | Ruta Qt | Herramientas → Documento, Campo y Composición; alineación, distribución, reajuste, borrado/continuación, formato/prueba y restablecer conservados. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py; tests/test_r8b_editor_ux_qt.py |
| E13 | Editor integrado y retención al navegar | Ruta Qt | Tres zonas retenidas; pestañas Propiedades / Trabajo de lote; datos de emisión siguen separados del diseño. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py; tests/test_r8b_editor_ux_qt.py |
| E14 | Confirmar descarte al cambiar diseño | Ruta Qt | resolve_work con Save/Discard/Cancel; campos numéricos pendientes se interpretan antes del aviso. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py; tests/test_r8b_editor_ux_qt.py |
| E15 | Zoom/ajuste del lienzo | Ruta Qt | Barra → Ajustar / − / + / Ampliar lienzo; zoom manual se conserva al editar propiedades. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py; tests/test_r8b_editor_ux_qt.py |
| M01 | Elegir revisión para emitir | Ruta Qt | Preparar emisión o Centro → Nuevo; selección de revisión/variante desde servicios existentes. | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M02 | Preparar emisión exige vigencia/integridad | Ruta Qt | Emisión → WorkPanel/EmissionCentreMixin; motor de trabajo | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M03 | Lote y datos variables comunes según diseño | Ruta Qt | Emisión → WorkPanel/EmissionCentreMixin; motor de trabajo | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M04 | Recipientes y copias por recipiente | Ruta Qt | Emisión → WorkPanel/EmissionCentreMixin; motor de trabajo | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M05 | Numeración n/total y rangos, advertencia sin campo número | Ruta Qt | Emisión → WorkPanel/EmissionCentreMixin; motor de trabajo | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M06 | Lote/PN/PB/conservación por envase | Ruta Qt | Emisión → WorkPanel/EmissionCentreMixin; motor de trabajo | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M07 | Aplicar/limpiar fila, validar pesos y completar | Ruta Qt | Recipientes → edición celda y menú contextual Limpiar datos; WorkPanel.clear_container_row | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M08 | Pegar tabla desde Excel | Ruta Qt | Centro de emisión → Pegar Excel…; parse_tabular_vessels conserva TSV/CSV y admite kg/g/mg por celda o cabecera. | tests/test_r3c_emission_qt.py; tests/test_mass_units.py |
| M09 | Ninguna/sin analizar/aprobado/rechazado | Ruta Qt | Emisión → WorkPanel/EmissionCentreMixin; motor de trabajo | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M10 | Fecha/nombre/condiciones, estado integrado o separado | Ruta Qt | Emisión → WorkPanel/EmissionCentreMixin; motor de trabajo | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M11 | Maestros de estado aprobados e íntegros | Ruta Qt | Configuración → Maestros de estado → Registrar aprobación documental con cotejo. | tests/test_r3d_settings_qt.py::test_pending_status_never_autoapproves |
| M12 | Escalado proporcional, ancho/alto, restaurar original | Ruta Qt | Emisión → WorkPanel/EmissionCentreMixin; motor de trabajo | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M13 | Seguridad configurable, preflight y límites reales de glifos | Ruta Qt | Formato y emisión → Seguridad + preflight; refresh_emission_review | tests/test_r3c_emission_qt.py::test_inline_checks_pending_invalid_format_and_long_fields |
| M14 | Previsualizar A4, avisos y páginas | Ruta Qt | Emisión → WorkPanel/EmissionCentreMixin; motor de trabajo | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M15 | PDF de prueba de pendientes sin emisión definitiva | Ruta Qt | Centro → PDF de prueba (exportación) / Actualizar vista previa; sin emisión definitiva. | tests/test_r3c_emission_qt.py::test_native_preview_export_cancel_issue_and_recovery |
| M16 | Generar PDF definitivo y registrar emisión | Ruta Qt | Centro → Emitir definitivamente → misma confirmación/token/hash/snapshot. | tests/test_r3c_emission_qt.py::test_native_preview_export_cancel_issue_and_recovery |
| M17 | Abrir último PDF / visor externo | Ruta Qt | Visor → Abrir PDF / Ampliar PDF, también visibles en compacto. | tests/test_r3c_emission_qt.py; visor externo pendiente por plataforma |
| M18 | Retener lote/envases/estado/formato al navegar; no heredarlo a otra etiqueta | Ruta Qt | Trabajo de lote en Editor ↔ Centro de emisión; mismos WorkPanel/CAS/autoguardado. | tests/test_emission_work_qt.py; tests/test_emission_work_tk.py |
| P01 | Elegir/guardar perfiles por nombre | Ruta Qt | Emisión → Formato y emisión / Diseñar hoja; WorkPanel/SheetDesigner | tests/test_r3e_qt.py; tests/test_r4a_qt.py; tests/test_r4b_qt.py |
| P02 | A4 orientación, márgenes, separación, offsets | Ruta Qt | Emisión → Formato y emisión / Diseñar hoja; WorkPanel/SheetDesigner | tests/test_r3e_qt.py; tests/test_r4a_qt.py; tests/test_r4b_qt.py |
| P03 | Casilla inicial y marcas de corte | Ruta Qt | Emisión → Formato y emisión / Diseñar hoja; WorkPanel/SheetDesigner | tests/test_r3e_qt.py; tests/test_r4a_qt.py; tests/test_r4b_qt.py |
| P04 | Impresora como referencia, no driver | Ruta Qt | Emisión → Formato y emisión / Diseñar hoja; WorkPanel/SheetDesigner | tests/test_r3e_qt.py; tests/test_r4a_qt.py; tests/test_r4b_qt.py |
| P05 | Capacidad, casillas omitidas y límites | Ruta Qt | Emisión → Formato y emisión / Diseñar hoja; WorkPanel/SheetDesigner | tests/test_r3e_qt.py; tests/test_r4a_qt.py; tests/test_r4b_qt.py |
| P06 | Hoja A4 de calibración y regla | Ruta Qt | Hoja patrón… genera regla PDF; Aplicar medidas de impresora… abre CalibrationDialog; medición física pendiente. | tests/test_r4b_calibration.py; tests/test_r4b_qt.py |
| P07 | Impresión mediante visor PDF al 100 % | Ruta Qt | Abrir PDF o Imprimir PDF registrado…; PrintWorkflowMixin original, sin confirmación de papel. | tests/test_r4c_dispatch.py; tests/test_r4c_qt.py; dispositivo físico pendiente |
| H01 | Historial emisión/fecha/producto/revisión/cantidades/operador/reimpresión | Ruta Qt | Historial; HistoryMixin → api.history | tests/test_r3c_history.py; tests/test_r3c_history_qt.py |
| H02 | Abrir PDF histórico íntegro | Ruta Qt | Historial; HistoryMixin → api.history | tests/test_r3c_history.py; tests/test_r3c_history_qt.py |
| H03 | Detalle variables/perfil/estado/envases/números/motivo | Ruta Qt | Historial; HistoryMixin → api.history | tests/test_r3c_history.py; tests/test_r3c_history_qt.py |
| H04 | Reimprimir números originales con motivo/vínculo independiente | Ruta Qt | Historial; HistoryMixin → api.history | tests/test_r3c_history.py; tests/test_r3c_history_qt.py |
| H05 | Bloquear PDF alterado/revisión retirada/números no emitidos | Ruta Qt | Historial; HistoryMixin → api.history | tests/test_r3c_history.py; tests/test_r3c_history_qt.py |
| C01 | Operador configurable, sin autenticación | Ruta Qt | Preferencias y datos → Guardar operador → save_settings_operator | tests/test_r3d_settings_qt.py::test_operator_validation_and_backup_are_native |
| C02 | Ubicación y COVEX_LABEL_DATA | Ruta Qt | Preferencias y datos → ruta de solo lectura / Copiar ruta → copy_settings_path | tests/test_r3d_settings_qt.py |
| C03 | Backup ZIP consistente SQLite WAL y documentos | Ruta Qt | Preferencias y datos → Crear copia verificada → create_settings_backup | tests/test_r3d_settings_qt.py::test_operator_validation_and_backup_are_native |
| C04 | Actualizar CM Word sin borrar anteriores | Ruta Qt | Catálogo CM → Importar clasificación CM → import_settings_cm | tests/test_r3d_settings_qt.py::test_cm_import_no_delete_and_duplicates |
| C05 | Materiales/códigos duplicados sin corregir automáticamente | Ruta Qt | Catálogo CM → tabla de duplicidades; consulta sin corrección automática | tests/test_r3d_settings_qt.py::test_cm_import_no_delete_and_duplicates |
| C06 | Registrar revisión de maestros de estado | Ruta Qt | Maestros de estado → Registrar aprobación → approve_settings_status | tests/test_r3d_settings_qt.py::test_pending_status_never_autoapproves |
| C07 | Últimos movimientos de auditoría local | Ruta Qt | Auditoría local → Actualizar movimientos → refresh_native_settings | tests/test_r3d_settings_qt.py |
| C08 | UID estable, migración aditiva y copia previa | Motor/procedimiento | Store/migration_v4/consentimiento expreso; SQLite v4 | tests/test_migration_v4.py; tests/test_migration_consent.py |
| C09 | Actualizar sin sobrescribir data | Motor/procedimiento | Procedimiento offline / guardas de build; no actualizador automático | tests/test_publication.py; docs/INSTALACION_Y_ACTUALIZACION.md |
| C10 | Recuentos de etiquetas/vigentes/pendientes/emisiones/materiales y accesos rápidos del Inicio 0.3.1 | Ruta Qt | Configuración → Resumen: recuentos / preaceptación / pruebas presenciales / Biblioteca. | tests/test_r3d_settings_qt.py::test_settings_is_native_without_launching_tk |

Editor de estados independiente: `test_r7a_status_qt.py`, `test_r7b_status_qt.py` y nuevas regresiones R8B de geometría, selección con valores pendientes, deshacer/rehacer y guardado. Su contrato no incorpora bloqueo ni modo tipográfico avanzado; no se muestran controles inexistentes. Diagnóstico, concurrencia y limpieza segura siguen cubiertos por las pruebas R8A.

