# Conservación funcional: las mismas 87 capacidades

Referencia obligatoria: `02f7ba7`, docs/UX_AUDIT_R6B/CONSERVACION_87.md. Implementación desde main `6b4f5076b644fc445bb8a143d116091c9f4c9c64`. No se renumera ni elimina una capacidad. Disponibilidad: **78 rutas Qt, 2 mixtas y 7 de motor/procedimiento**. No equivale a aceptación física/GMP ni cobertura exhaustiva de cada rama de cada control.

Se conservan los controladores de servicios; las consolidaciones reubican entradas o comparten menús. Las pruebas nuevas verifican equivalencia de fuentes, intercambios, selección de revisión/variante, estado de menús, cancelación/pies, navegación con trabajo retenido y precisión del perfil/calibración. Las familias históricas siguen en la suite completa.

| ID | Capacidad | Disponibilidad | Ruta efectiva / equivalencia | Regresión de referencia |
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
| D08 | Revisiones heredadas, incluida 00-R1; variantes independientes desde R3B2 | Ruta Qt | Revisiones y variantes… → RevisionBrowserDialog; selección independiente sin mutación documental. | tests/test_variants_v4.py; tests/test_r3a_qt.py |
| D09 | Registrar aprobación externa con responsable/evidencia/confirmación | Ruta Qt | Inspector → Registrar aprobación de revisión… o Documento → aprobación → RevisionApprovalDialog.commit. | tests/test_r3a_qt.py::test_native_approval_requires_confirmation_and_keeps_state_on_cancel |
| D10 | Retirar vigente anterior al aprobar nueva; consulta retirada | Ruta Qt | Registro de aprobación externa → api.approve; consulta de Retirada | tests/test_r3a_qt.py::test_clone_is_pending_and_approval_retires_previous |
| D11 | Vigente no editable; clonar para modificar | Ruta Qt | Editor solo lectura → Ajustar campos de revisión vigente… crea variante DRAFT | tests/test_r3e_qt.py; tests/test_variants_v4.py |
| D12 | Integridad antes de clonar/aprobar/emitir | Motor/procedimiento | Guardas verify_documents / verify_renderable / review_work; sin botón propio | tests/test_core.py; tests/test_variants_v4.py; tests/test_r3c_emission_qt.py |
| D13 | Fuente 00 defectuosa bloqueada, 00-R1 pendiente sin autoaprobación | Motor/procedimiento | Guardas integrity/render_geometry; no autoaprobación de 00-R1 | tests/test_r1.py; tests/test_migration_v4.py |
| D14 | Comparador básico de imágenes, datos y campos | Ruta Qt | Documento → Comparar revisiones; Variantes → Comparar revisión y variante. | tests/test_r3f_qt.py::test_native_comparison_does_not_mutate_document |
| I01 | Importar PDF/Word individual y datos obligatorios | Mixta | Intercambio → Importar PDF/Word → import_document; Word instalado sigue pendiente de ensayo real. | tests/test_core.py (Word omitido); tests/test_r3a_qt.py::test_import_pdf_remains_pending |
| I02 | Importar carpeta, progreso, detener, resumen/errores | Ruta Qt | Intercambio → Importar carpeta → ControlledImportDialog; FolderImportDialog/Tk conservados como contingencia. | tests/test_r3f_qt.py; tests/test_r5b_migration.py |
| I03 | Conversión Word local y errores por dependencia | Motor/procedimiento | Motor importer.docx_to_pdf, integración local externa | tests/test_core.py (ensayo Word real omitido) |
| I04 | Recorte automático, geometría, rechazo multipágina | Motor/procedimiento | Motor de importación auto_crop y validación de página | tests/test_core.py; tests/test_r1.py |
| I05 | Importar crea pendiente, nunca aprobación | Motor/procedimiento | Motor add_label / catalog_migration_apply: siempre PENDING | tests/test_r5b_migration.py; tests/test_r3a_qt.py::test_import_pdf_remains_pending |
| E01 | Selección de campo por lista/lienzo | Ruta Qt | Editor → Elementos / lienzo; selección múltiple y propiedades retenidas. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py |
| E02 | Mover campo y bloquear posición | Ruta Qt | Editor → elementos / propiedades / ajuste avanzado; AdvancedEditorMixin | tests/test_r3b1_qt.py; tests/test_r3e_qt.py |
| E03 | Agregar/quitar campos, clave única | Ruta Qt | Elementos → Nuevo / Dibujar; Avanzadas o contexto lienzo → Quitar; mismos controladores. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py |
| E04 | Identificador y nombre visible | Ruta Qt | Editor → elementos / propiedades / ajuste avanzado; AdvancedEditorMixin | tests/test_r3b1_qt.py; tests/test_r3e_qt.py |
| E05 | X/Y/ancho/alto en mm y validación | Ruta Qt | Editor → elementos / propiedades / ajuste avanzado; AdvancedEditorMixin | tests/test_r3b1_qt.py; tests/test_r3e_qt.py |
| E06 | Fuente/tamaño, negrita, obligatorio | Ruta Qt | Editor → elementos / propiedades / ajuste avanzado; AdvancedEditorMixin | tests/test_r3b1_qt.py; tests/test_r3e_qt.py |
| E07 | Recortar por coordenadas/selección visual | Ruta Qt | Editor → elementos / propiedades / ajuste avanzado; AdvancedEditorMixin | tests/test_r3b1_qt.py; tests/test_r3e_qt.py |
| E08 | Zona de estado y control de proporciones | Ruta Qt | Editor → elementos / propiedades / ajuste avanzado; AdvancedEditorMixin | tests/test_r3b1_qt.py; tests/test_r3e_qt.py |
| E09 | Anclar a frase Word/PDF de referencia | Ruta Qt | Editor → elementos / propiedades / ajuste avanzado; AdvancedEditorMixin | tests/test_r3b1_qt.py; tests/test_r3e_qt.py |
| E10 | Relocalizar desde Word reconocido | Ruta Qt | Editor → elementos / propiedades / ajuste avanzado; AdvancedEditorMixin | tests/test_r3b1_qt.py; tests/test_r3e_qt.py |
| E11 | Guardar configuración de borrador sin tocar original | Ruta Qt | Barra Editor → Guardar diseño pendiente → save_work; no autoguarda el diseño. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py |
| E12 | Reajuste avanzado de posiciones/recorte/zona | Ruta Qt | Editor → elementos / propiedades / ajuste avanzado; AdvancedEditorMixin | tests/test_r3b1_qt.py; tests/test_r3e_qt.py |
| E13 | Editor integrado y retención al navegar | Ruta Qt | Editor retenido, barra única, Campo y variante / Trabajo de lote; sin dock global. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py |
| E14 | Confirmar descarte al cambiar diseño | Ruta Qt | Editor → elementos / propiedades / ajuste avanzado; AdvancedEditorMixin | tests/test_r3b1_qt.py; tests/test_r3e_qt.py |
| E15 | Zoom/ajuste del lienzo | Ruta Qt | Ajustar / zoom / Ampliar lienzo; visualización independiente del tamaño del PDF. | tests/test_r3b1_qt.py; tests/test_r3e_qt.py |
| M01 | Elegir revisión para emitir | Ruta Qt | Preparar emisión o Centro → Nuevo; selección de revisión/variante desde servicios existentes. | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M02 | Preparar emisión exige vigencia/integridad | Ruta Qt | Emisión → WorkPanel/EmissionCentreMixin; motor de trabajo | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M03 | Lote y datos variables comunes según diseño | Ruta Qt | Emisión → WorkPanel/EmissionCentreMixin; motor de trabajo | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M04 | Recipientes y copias por recipiente | Ruta Qt | Emisión → WorkPanel/EmissionCentreMixin; motor de trabajo | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M05 | Numeración n/total y rangos, advertencia sin campo número | Ruta Qt | Emisión → WorkPanel/EmissionCentreMixin; motor de trabajo | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M06 | Lote/PN/PB/conservación por envase | Ruta Qt | Emisión → WorkPanel/EmissionCentreMixin; motor de trabajo | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M07 | Aplicar/limpiar fila, validar pesos y completar | Ruta Qt | Recipientes → edición celda y menú contextual Limpiar datos; WorkPanel.clear_container_row | tests/test_r3c_emission_qt.py; tests/test_emission_work.py |
| M08 | Pegar tabla desde Excel | Ruta Qt | Centro de emisión → Pegar Excel…; servicio parse_tabular_vessels intacto. | tests/test_r3c_emission_qt.py; tests/test_mass_units.py |
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

`tests/test_r6b_ux_qt.py` añade 33 casos ejecutados (incluida parametrización) para los cambios de interfaz y la corrección de vida útil de pantallas; no sustituye la suite histórica. Se añaden 6 casos de integridad del portable en `tests/test_portable_archive_integrity.py`. D03 conserva fuentes por motor; I01/I03 mantienen el límite de conversión Word externa no ensayada. C09 sigue siendo procedimiento de actualización offline, no restauración automática desde UI.

Ampliaciones posteriores al recuento (variantes v4, trabajos recuperables, hoja libre/casillas usadas, calibración, envío controlado, R5/R6A/R6B) permanecen accesibles por los mismos servicios. La compatibilidad Tkinter sigue en Configuración clásica y Editor Tkinter. No se retiran ejecutables acompañantes ni se alteran migraciones, hashes, snapshots, auditoría o reglas documentales.
