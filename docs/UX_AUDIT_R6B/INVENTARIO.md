# Inventario pantalla → control → acción → controlador

## Cómo leer el inventario completo

El [registro estático](inventario-sitios.json) enumera 884 sitios de construcción/registro, incluyendo señales, opciones, filas de formulario, etiquetas informativas, menús, atajos y diálogos. Cada entrada conserva la expresión íntegra y los bucles que generan controles: una fábrica dentro de un bucle representa varios controles reales. [INVENTARIO_SITIOS.md](INVENTARIO_SITIOS.md) permite localizarlos por clase/método y línea del commit base. El [registro runtime](inventario-runtime.json) enumera los controles reales de cada estado observado, sus textos/opciones, visibilidad, habilitación, geometría, tooltip y nombre accesible; incluye los menús extraídos sin ejecutar sus acciones.

Estas capas se complementan: el AST cubre también contingencias, rutas fuera del recorrido y widgets sustituidos por herencia; el runtime prueba presencia en los estados capturados. Los hijos internos de Qt pueden aparecer como controles separados. No sumar ambas cuentas como «número de botones». Un símbolo de test coincidente no acredita cobertura directa: el JSON lo marca `REFERENCE_ONLY_NOT_CLICK_PROOF` o `NO_DIRECT_SYMBOL_MATCH`. El [índice de pruebas](indice-pruebas.json) enumera las funciones localizadas.

Para evitar repetir atributos iguales miles de veces, el JSON runtime guarda `control_definitions` por identificador y `configurations[].captures[].control_states` como `[definition_id, x, y, width, height, visible, enabled]`. `state_fields` documenta el orden. Se conserva la información de cada control/estado; nombres/textos/opciones/tooltips se consultan en su definición. Los manifiestos locales contienen además la forma expandida.

Controlador efectivo: `FunctionalWindow` resuelve, en este orden, `CatalogExchangeMixin → PrintWorkflowMixin → FolderImportMixin → CompareMixin → SettingsMixin → HistoryMixin → EmissionCentreMixin → EmissionWorkMixin → VariantsMixin → AdvancedEditorMixin → BaseFunctionalWindow → StudioWindow`. Por ejemplo, `Preparar emisión` se construye con `open_legacy('emitir')`, pero `EmissionCentreMixin.open_legacy` lo dirige al centro Qt. Leer solo la fábrica da un diagnóstico falso de uso de Tkinter.

## Catálogo de controles efectivos

En las tablas siguientes, «suite» es la referencia de verificación existente; el detalle de controles/estados y variantes generadas está en los registros. Las confirmaciones se capturaron y cancelaron en el recorrido; las pruebas de servicio usan exclusivamente fixtures temporales.

| Pantalla | Control(es) y variantes | Acción / controlador efectivo | Estado / guarda | Suite de referencia |
|---|---|---|---|---|
| Global | Biblioteca, Editor, Emisión, Historial, Configuración | `navigate` de mixins; cambia stack y guarda/consulta trabajo según destino | Editor exige documento; algunas rutas no gestionan igual el dock | test_r3a_qt, test_emission_work_qt, test_r3d_settings_qt |
| Global | Ctrl+K | `StudioWindow.quick_search` → Biblioteca + foco | Atajo de ventana | test_r3a_qt |
| Global | Estado inferior, cierre | feedback; `closeEvent` / `resolve_work` | Guardar/Descartar/Cancelar diseño; cerrar compañero antes de Qt | test_r3a_qt, test_emission_work_qt |
| Biblioteca | Buscar + borrar entrada | `search.textChanged → refresh` | Coincidencia compuesta en servicio | test_r3a_qt |
| Biblioteca | Categoría, Origen, Estado | `make_filter → refresh` | Deshabilitados sin opciones adicionales | test_r3a_qt |
| Biblioteca | Más filtros / Cerrar filtros; Familia, Tipo, Cliente, País, Idioma, Versión, Incorporación | `toggle_advanced`, `filters → refresh` | Plegado automático por tamaño; resumen de filtros activos | test_r3a_qt |
| Biblioteca | Recordar apertura; Limpiar | `remember_filter_choice`, `reset_filters` | Preferencia opcional; limpiar vuelve a Todas | test_r3a_qt |
| Biblioteca | Todas, Favoritas, Recientes; estrella por fila | `set_mode`, `favorite` | Filtros/selección conservados; favorita es de etiqueta | test_r3a_qt |
| Biblioteca | Tabla, cabeceras, selección, doble clic/Enter | `selected`, `sort_table`, `open_editor` | Revisión disponible/integridad; Enter solo tabla | test_r3a_qt |
| Biblioteca | Columnas → Tipo/Origen/Cliente/País/Restablecer | `columns_menu`, `choose_column`, `reset_columns` | Columnas esenciales adaptadas; preferencia local de sesión | test_r3a_qt + capturas |
| Biblioteca | Inspector / Ocultar | `toggle_inspector`, `set_inspector` | Se oculta al entrar en anchura compacta | capturas / test_r3a_qt |
| Inspector | Vista previa, − / + / Ajustar / Ampliar | `Preview.zoom/fit`, `enlarge` | Zoom relativo a Ajustar, no físico | test_r3a_qt |
| Inspector | Revisión; Información/Versiones/Documentos | `revision_changed`, pestañas Qt | Estados Pendiente/Vigente/Retirada | test_r3a_qt |
| Inspector | Variante y Variantes ▾ | `choose_library_variant`, `variant_menu` | Independencia de revisión/variante; ver menú abajo | test_variants_v4 |
| Inspector | Ficha completa y referencias | `document_details` | Consulta de documentos/atributos | test_r3a_qt |
| Inspector | Documentos y aprobación externa | `approve_revision` (reconectado) | Solo revisión PENDING; etiqueta confusa | test_r3a_qt / UX-01 |
| Inspector | Revisiones y variantes | `show_access('document') → catalog` | Ruta residual a transición, no abre selector Qt | captura 35 / UX-02 |
| Inspector | Importaciones PDF / Word | `import_document` | Selector + identidad, nueva revisión pendiente | test_r3a_qt |
| Inspector | Favorita / Abrir en Editor | `favorite`, `open_editor` | Documento íntegro; edición según revisión/variante | test_r3a_qt |
| Inspector | Registrar aprobación de revisión… | `approve_revision → RevisionApprovalDialog` | PENDING, sin compañero; mismo destino que otro botón | test_r3a_qt |
| Inspector | Preparar emisión / PDF de prueba | `EmissionCentreMixin.open_legacy → new_emission_work` | Producción solo elegible; prueba admite pendiente; no arranca Tk | test_r3c_emission_qt |
| Documentos y acciones | Ficha / PDF maestro / Original | `document_details`, `open_document(False/True)` | Archivo y visor externo deben existir | test_r3a_qt; visor SO pendiente |
| Documentos y acciones | Editar metadatos con fuente / Crear nueva revisión / Registrar aprobación | `edit_metadata`, `clone_revision`, `approve_revision` | Fuente/motivo; nunca se aprueba por clonar | test_r3a_qt |
| Documentos y acciones | Importar PDF/Word / Inventariar carpeta / Importar carpeta | `import_document`, `review_catalog_folder`, `import_folder_native` | Lectura, importación controlada R5B por fila; Word externo | test_r3f_qt, test_r5b_migration |
| Documentos y acciones | Exportar catálogo / Conciliar libro máster / Comparar revisiones | `export_entire_library`, `reconcile_master`, `compare_revisions` | Exportación confirmada; comparación solo lectura | test_r5a_catalog, test_r5c_qt, test_r3f_qt |
| Editor | Paneles → Elementos y herramientas / Propiedades | `editor_panels_menu` | Visibilidad de paneles; ocultación automática por anchura | capturas / UX-04 |
| Editor | Biblioteca / Datos del trabajo | `navigate('library')`, `show_editor_work` | Abre dock; trabajo independiente del diseño | test_emission_work_qt |
| Editor | Deshacer / Rehacer / Ctrl+Z / Ctrl+Shift+Z | `undo_edit`, `redo_edit` | Historial de diseño en sesión, no versión documental | test_r3b1_qt |
| Editor | Ajustar, − / +, rueda, porcentaje | `canvas.fit/zoom` | Solo vista; sin escala física | test_r3a_qt, capturas |
| Editor | Ajuste avanzado / Restablecer | `toggle_editor_advanced`, `reset_layout` | Diseño restablecido completo; etiqueta cambia en resize | test_r3b1_qt / UX-10 |
| Editor | Selector Variante / Gestionar variantes | `choose_editor_variant`, `variant_menu` | Diseño heredado o variante elegida | test_variants_v4 |
| Editor | + Nuevo campo / Dibujar campo | `add_field`, `draw_new_field` | Solo editable; key única; formulario y rectángulo | test_r3e_qt |
| Editor | Ajustar campos de revisión vigente… | `editable_variant → create_variant_ui(field_adjustment=True)` | Crea DRAFT con motivo; no modifica vigente | test_r3e_qt |
| Editor | Lista / lienzo / selección múltiple / ocho tiradores / arrastre | `list_selection`, `scene_selection`, `EditorFieldItem`, `ResizableRect` | Bloqueo/guardas/una operación de undo | test_r3b1_qt, test_r3e_qt |
| Editor | Snap 1 mm / cuadrícula 10 mm | `field_snap`, `field_grid → draw_editor` | Ayuda de geometría, no maquetación fija | test_r3e_qt |
| Propiedades | Nombre, identificador, X/Y/Ancho/Alto, tamaño tipográfico, Negrita | `change_name/key/geometry/flags → command` | Solo edición permitida; mm y pt distintos | test_r3b1_qt |
| Avanzadas Documento | Recorte visual/mm / Anclar / Relocalizar | `edit_crop`, `edit_anchor`, `relocate` | Referencia verificable o plantilla reconocida; sin OCR | test_r3b1_qt |
| Avanzadas Campo | Agregar/Quitar / Obligatorio / Bloquear / Caja-Línea base-Continuación-Párrafo / Borrado y continuación | `add/remove_field`, `change_flags/draw_mode`, `edit_auxiliary` | Campos superpuestos, confirmación al quitar | test_r3b1_qt |
| Avanzadas Alineación y escala | Alineación/distribución y Reajuste proporcional | `align_selection`, `edit_scale` | Selección editable; bloqueados no se transforman | test_r3b1_qt |
| Avanzadas Estado y prueba | Zona estado / Vista PDF / Editor Tkinter | `edit_status_area`, `edit_output`, `open_legacy('editor')` | Reserva ≠ aprobación; puente conserva datos y bloquea Qt | test_r3b1_qt, test_emission_work_tk |
| Editor | Guardar diseño pendiente | `save_work` de VariantsMixin / AdvancedEditorMixin | Cambios, fuente/estado/generación válidos; explícito | test_r3b1_qt, test_variants_v4 |
| Variantes ▾ | Crear / Derivar / Tamaño nominal / Enviar a revisión / Devolver a borrador / Aprobar / Retirar / Comparar / Evidencia | `create_variant_ui`, `edit_nominal_size`, `variant_transition`, `approve_variant_ui`, `compare_variant`, `open_variant_evidence` | Menú habilita por selección; servicio verifica cada transición | test_variants_v4; cobertura de widgets parcial |
| Trabajo compartido | Selector / Abrir / Nuevo / Copiar / Recargar | `load/new/copy/reload_emission_work` | Identidad y generación; recargar pide descarte si hay cambios | test_emission_work_qt |
| Datos de lote | Campos generados por key del diseño, multilineales, PN/PB | `WorkPanel.changed → work_changed → timer/flush_emission_work` | Autoguardado 400 ms; PN/PB normalizados por motor | test_emission_work_qt, test_mass_units |
| Recipientes | Nº, Lote, PN, PB, Conservación; contexto Limpiar datos | `WorkPanel.capture/clear_container_row` | Vacío hereda lote común; Nº no editable | test_r3c_emission_qt |
| Formato y emisión | Recipientes, copias, rangos; ancho/alto/margen/gap/offsets/casilla/seguridad/impresora | `profile_inputs/inputs → changed/capture` | Campos de texto validados por review/motor | test_r3c_emission_qt, test_r3e_layout |
| Formato y emisión | Proporción / restaurar tamaño / orientación / marcas / perfil guardado | `scale_size`, `restore_size`, `apply_profile`, `changed` | Perfil de trabajo independiente de diseño nominal | test_r3c_emission_qt |
| Formato y emisión | Diseñar hoja / Calibrar impresora | `design_sheet`, `calibrate_printer` | Diálogo sobre copia; aplicar persiste trabajo | test_r3e_qt, test_r4b_qt |
| Estado de material | Ninguna/Sin analizar/Aprobado/Rechazado; Integrada/Independiente; Fecha/Responsable/Caducidad | `WorkPanel.status_* → capture` | Maestro estado íntegro y aprobado; no aprueba revisión | test_r3c_emission_qt |
| Centro Emisión | Biblioteca / conmutador compacto Datos-Vista PDF | `navigate`, `adapt_emission_layout` | Alterna paneles por altura; mismo trabajo | test_r3c_emission_qt |
| Centro Emisión | Pegar Excel / Guardar perfil / Calibrar hoja | `paste_work_containers`, `save_emission_profile`, `calibrate_emission` | Excel pega, no importa libro; hoja PDF no recoge medidas | test_r3c_emission_qt, test_mass_units |
| Centro Emisión | Actualizar vista previa / Guardar borrador / PDF de prueba | `preview_emission_work`, `flush_emission_work`, `proof_emission_work` | Preflight + token/hash; prueba sin issue | test_r3c_emission_qt |
| Centro Emisión | Opciones → Recuperar / Actualizar vínculo | `recover_emission_work`, `refresh_work_binding` | Reconciliación explícita, no cambia fuente sin control | test_emission_work_qt |
| Centro Emisión | Emitir definitivamente / Imprimir PDF registrado | `issue_emission_work`, `print_emission_pdf` | Preview actual, confirmación, luego PDF registrado verificado | test_r3c_emission_qt, test_r4c_qt |
| Visor PDF compartido | Página / Ajustar / − / + / Ampliar / Abrir PDF | `PdfPane.page_changed`, `Preview`, `expand_pdf/open_pdf` | Validador de hash; controles inferiores ocultos en compacto | test_r3c_emission_qt, capturas |
| Historial | Actualizar / Buscar / selección / 4 pestañas de detalle | `refresh/filter/select_native_issue` | Solo consulta; snapshot/integridad | test_r3c_history_qt |
| Historial | Verificar y ver PDF / Imprimir / Reimpresión controlada | `preview_native_issue`, `print_historical_pdf`, `native_reprint` | Revisión, hash, motivo y números originales | test_r3c_history, test_r3c_history_qt, test_r4c_qt |
| Reimpresión | Números / Motivo / Casilla / aceptación heredada / Prueba / Registrar / Cerrar | cierres `validate/execute` dentro de `native_reprint` | prepare + token + confirmación; no nuevos números | test_r3c_history_qt |
| Configuración Resumen | Actualizar recuentos / Diagnóstico R6A / Sesiones R6B / Biblioteca | `refresh_native_settings`, `open_acceptance_readiness`, `open_uat_session`, `navigate` | Sin aceptación automática | test_r3d_settings_qt, test_r6a_qt, test_r6b_qt |
| Preferencias y datos | Operador / Guardar / ruta readonly / Copiar / Backup | `save_settings_operator`, `copy_settings_path`, `create_settings_backup` | Identificador ≥3; copia consistente confirmada; restore offline | test_r3d_settings_qt |
| Catálogo CM | Importar DOCX / tabla duplicados | `import_settings_cm`, `material_duplicates` | Acumulativo; sin corrección o borrado automático | test_r3d_settings_qt |
| Maestros estado | Selección / Registrar aprobación / responsable / referencia / cotejo | `approve_settings_status` y validación local | Solo maestro PENDING; cotejo obligatorio | test_r3d_settings_qt |
| Auditoría local | Tabla / Actualizar movimientos | `refresh_native_settings → audit_entries` | Solo consulta; registro local no inviolable | test_r3d_settings_qt |
| Configuración | Configuración clásica (compatibilidad) | `open_legacy('admin')` | Guarda y bloquea edición Qt; contingencia | test_emission_work_tk |

## Superficies modales, opciones y contingencias

| Modal / acceso | Controles adicionales / controlador | Verificación / estado |
|---|---|---|
| `ask_form` (metadatos, revisión, variantes, nominal, motivo) | Entradas por lista de campos; OK/Cancel; validación en llamador | Campos exactos en JSON AST; capturas dinámicas; cancelar no muta. |
| `RevisionApprovalDialog` | Responsable, referencia, checkbox, Registrar, Cancel; `update_state/commit` + segundo confirm | test_r3a_qt; no se acepta la aprobación en la captura. |
| `CompareDialog` | Revisiones A/B; paralelo/superposición; opacidad; Cerrar | test_r3f_qt; mismo documento y revisiones diferentes. |
| Comparación de variante | JSON/resumen documental, revisión base y variante | `VariantsMixin.compare_variant`; test_variants_v4, cobertura UI parcial. |
| `RectangleDialog` | Lienzo de selección, X/Y/ancho/alto; ajustar/vista y OK/Cancel; extras para estado | Recorte y reserva: test_r3b1_qt; mínimo no suprime guardas geométricas. |
| Referencia/anclaje | Buscar span, lista y vista, selección/confirmación | `edit_anchor`; sin texto extraíble no hay anclaje automático. |
| Borrado/continuación y escala | Coordenadas auxiliares, modos y factores | `edit_auxiliary/edit_scale`; test_editor_layout + test_r3b1_qt. |
| Vista de salida del diseño | Perfil/valores y PDF de prueba desde memoria | `edit_output`; test_r3c_emission_qt/test_r3b1_qt. |
| `ControlledImportDialog` | Acción por fila Omitir/Nueva etiqueta/Nueva revisión, destino, Editar identidad, Confirmar, Detener, Cerrar | Ruta actual R5B; `selected/start/step/stop`; sin importación durante captura. |
| `FolderImportDialog` | Lista editable, progreso, Comenzar/Detener/Cerrar | R3F conservado en código/pruebas, **no** destino actual de Importar carpeta. |
| Inventario R5A | Informe JSON readonly; Cerrar | `review_catalog_folder`; formato técnico poco legible para operador. |
| `MasterReconciliationDialog` | Hoja; 8 correspondencias; Comparar; filtro resultados; Exportar; tabla; Cerrar | test_r5c_qt; solo consulta, no corrige ni importa automáticamente. |
| `SheetDesigner` | Papel A4/A3/A5/custom, orientación, grid/free, medidas, posiciones, distribuir/auto, casillas usadas, snap/grid, selección XYWH, alineación, eliminar, PDF, perfiles, undo/redo/reset/fit/zoom/aplicar/cancelar | test_r3e_qt/test_r4a_qt; no sobrescribe el trabajo al cancelar. |
| `OccupiedSlotsDialog` | Casillas numeradas; antes del inicio bloqueadas; OK/Cancel | test_r4a_qt; primera hoja, no estado de recipiente. |
| `CalibrationDialog` | Impresora, XY esperadas/medidas, PDF calibración, aplicar/cancelar | test_r4b_qt; medidas físicas no realizadas en auditoría. |
| Impresión nativa | `QPrintDialog`; dispositivo, todas las páginas, cancelar | test_r4c_qt/dispatch simulan driver; no se abre ni envía a dispositivo en captura. |
| `ReadinessDialog` | Ejecutar diagnóstico; tabla; exportar ZIP; cerrar | test_r6a_qt; NO ACEPTADO, pruebas manuales pendientes. |
| `UatSessionDialog` | Nueva/abrir/verificar; 14 casos; resultado, responsable, fecha, observaciones, evidencia, guardar generación, cerrar | test_r6b_qt; captura sesión vacía y cargada sin marcar PASS. |
| Nueva sesión UAT | Selector R6A; equipo, Windows, responsable, commit, SHA portable; destino JSON | `new_session`; no son credenciales ni firma. |
| Consentimiento v3→v4 | Diálogo de explicación/confirmación de migración | `migration_consent.qt_confirmation`; test_migration_consent. No se migra datos reales en auditoría. |
| Selectores SO y mensajes | Abrir/guardar archivo/carpeta; preguntas, aviso/error; cerrar | Sitios y filtros completos en JSON; apariencia Windows/driver no capturada. |

No se detectó un botón visible sin ningún controlador en los estados revisados. Sí hay botones que retornan sin acción por falta de contexto o que solo explican un bloqueo; deben evaluarse como feedback/descubribilidad, sin etiquetarlos automáticamente como funciones vacías. Las conexiones sobrescritas, widgets retirados de layouts y métodos base reemplazados se conservan en el registro estático para evitar atribuir falsos controles activos.
