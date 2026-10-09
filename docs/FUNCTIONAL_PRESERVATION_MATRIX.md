# Matriz de conservación funcional — Industrial Moderno

Fuentes revisadas: main 0.3.1 bd6e92e y PR #2/R3A e1ac607 (no integrada). La prueba parte de main y no sustituye la aplicación actual. Es el inventario obligatorio para verificar la futura conservación del 100 %, no una afirmación de migración completa.

**Qt demo**: interactivo, datos ficticios. **Visual**: interacción temporal, no persistencia/emisión. **Actual**: permanece en Tkinter, no migrado. **Motor**: regla reutilizable sin cambios. El destino propuesto es un acceso obligatorio, no una función implementada.

| ID | Capacidad | Acceso actual / referencia | Acceso previsto Qt | Estado prueba |
|---|---|---|---|---|
| B01 | Inicio Biblioteca y navegación horizontal | R3A Application.show/studio_ui | Cabecera | Qt demo |
| B02 | Tabla, selección única, abrir doble clic/Enter | LibraryPanel.tree/open | Tabla → Editor / botón principal | Qt demo doble clic/botón; Enter pendiente |
| B03 | Búsqueda dinámica código/nombre/producto/cliente/metadatos | LibraryService.entries | Buscador principal | Qt demo |
| B04 | Ctrl+K / buscador rápido | _open_library_picker / bind global | Ctrl+K → foco Biblioteca | Qt demo; no popup separado |
| B05 | Filtros categoría/familia/tipo/origen/cliente/país/idioma/versión/estado/incorporación | FILTER_FIELDS / LibraryPanel | Frecuentes + avanzados plegables | Qt demo |
| B06 | Limpiar búsqueda y filtros | LibraryPanel.reset | Limpiar | Qt demo |
| B07 | Favoritas / marcar y desmarcar | LibraryPanel.favorite | Panel izquierdo / inspector / estrella | Qt demo, SQLite temporal |
| B08 | Recientes y última revisión abierta | LibraryService.opened/entries(recent) | Panel izquierdo | Qt demo |
| B09 | Previsualización documento | LibraryPanel.preview / services.thumbnail | Inspector / ampliar / zoom | Qt demo, ampliación añadida |
| B10 | Revisiones y estado independiente del nombre | _master_detail / R3A select_revision | Inspector → Revisión | Qt demo |
| B11 | Columnas código/nombre/tipo/versión/origen/cliente/país/estado | R3A LibraryPanel | Tabla adaptable / ficha completa / tooltip | Qt demo, scroll si necesario |
| B12 | Ocultar/ajustar filtros e inspector | R3A toggle_filters/toggle_inspector | Paneles ajustables / avanzados plegables | Qt demo parcial, sin toggle inspector |
| B13 | Retener filtros/selección al navegar | R3A vistas retenidas | Controlador de sesión | Qt demo |
| D01 | Ficha: datos, dimensiones, revisiones, referencias | _master_detail | Documentos y acciones → Ficha | Qt demo de metadatos |
| D02 | Abrir PDF maestro en visor externo | _master_detail.viewfile | Ficha → Abrir fuente | Actual |
| D03 | Originales y documentos conservados localmente | Store.add_label/add_version / asset_path | Ficha → Fuentes | Motor; no originales en prueba |
| D04 | COVEX/cliente, nombre y referencia cliente | Importación / origin/customer/ref_customer | Ficha / filtros / importar | Clasificación Qt demo; importar Actual |
| D05 | Incorporación distinta de origen/estado | acquisition | Ficha → Procedencia | Qt demo |
| D06 | Editar metadatos con fuente obligatoria | _edit_metadata / LibraryService.update_metadata | Documentos y acciones → Metadatos | Actual; generador demo usa servicio |
| D07 | Nueva revisión, código y motivo | _master_clone / clone_version | Documentos y acciones → Nueva revisión | Actual; generador usa servicio |
| D08 | Variantes actuales por revisión, incluida 00-R1 | _seed_r1_variant / versions | Selector + ficha | Actual, sin entidad nueva |
| D09 | Registrar aprobación externa con responsable/evidencia/confirmación | _master_approve / approve | Documentos y acciones → Aprobación | Actual; aprobaciones ficticias solo en demo |
| D10 | Retirar vigente anterior al aprobar nueva; consulta retirada | Store.approve | Estado / ficha / selector | Qt demo sobre revisiones ficticias |
| D11 | Vigente no editable; clonar para modificar | replace_pending_fields / AdvancedEditor | Editor solo lectura / Nueva revisión | Qt demo solo lectura + Motor |
| D12 | Integridad antes de clonar/aprobar/emitir | verify_documents / verify_renderable | Guardas de servicios | Motor sin cambios |
| D13 | Fuente 00 defectuosa bloqueada, 00-R1 pendiente sin autoaprobación | integrity / render_geometry / storage | Inspector / preflight | Motor; sin etiqueta real en prueba |
| D14 | Comparador básico de imágenes, datos y campos | _master_compare | Documentos y acciones → Comparar | Actual; R2.5 pendiente |
| I01 | Importar PDF/Word individual y datos obligatorios | import_label_dialog / _import_one | Documentos y acciones → Importar | Actual |
| I02 | Importar carpeta, progreso, detener, resumen/errores | import_folder_dialog | Importar → Carpeta | Actual |
| I03 | Conversión Word local y errores por dependencia | docx_to_pdf | Importar → Verificación | Motor; Word no validado |
| I04 | Recorte automático, geometría, rechazo multipágina | auto_crop / import_label | Importar → Revisar diseño | Motor sin cambios |
| I05 | Importar crea pendiente, nunca aprobación | Store.add_label | Documento pendiente | Motor sin cambios |
| E01 | Selección de campo por lista/lienzo | AdvancedEditor.select_list/on_select | Elementos / lienzo | Qt demo |
| E02 | Mover campo y bloquear posición | on_drag/on_up / locked | Lienzo / Propiedades | Visual temporal |
| E03 | Agregar/quitar campos, clave única | add_field/remove_field | Elementos → Agregar/Quitar | Actual |
| E04 | Identificador y nombre visible | apply_props | Propiedades → Identificación | Visual nombre; clave Actual |
| E05 | X/Y/ancho/alto en mm y validación | apply_props | Posición y tamaño | Visual acotado al lienzo + Motor |
| E06 | Fuente/tamaño, negrita, obligatorio | apply_props | Texto y comportamiento | Visual valores; render tipográfico pendiente |
| E07 | Recortar por coordenadas/selección visual | edit_crop | Herramientas avanzadas → Recorte | Actual |
| E08 | Zona de estado y control de proporciones | edit_status_area | Herramientas avanzadas → Zona de estado | Actual |
| E09 | Anclar a frase Word/PDF de referencia | align_selected_to_word / master_spans | Herramientas avanzadas → Anclar | Actual |
| E10 | Relocalizar desde Word reconocido | autolocate / locate_fields | Herramientas avanzadas → Recalcular | Actual, solo diseños reconocidos |
| E11 | Guardar configuración de borrador sin tocar original | AdvancedEditor.save | Guardar borrador | Actual; demo no guarda diseños |
| E12 | Reajuste avanzado de posiciones/recorte/zona | Editor + motor | Propiedades / herramientas avanzadas | Actual, no composición nativa |
| E13 | Editor integrado y retención al navegar | R3A Application.editor | Editor central | Qt demo |
| E14 | Confirmar descarte al cambiar diseño | R3A editor | Diálogo trabajo activo | Actual; demo conserva por revisión |
| E15 | Zoom/ajuste del lienzo | Sin zoom dedicado en editor Tk | Barra lienzo / rueda | Qt demo añadido |
| M01 | Elegir revisión para emitir | select_emission_version / biblioteca | Emisión → Selección | Actual |
| M02 | Preparar emisión exige vigencia/integridad | R3A emission_eligibility | Inspector → Preparar emisión | Actual; demo solo muestra acceso |
| M03 | Lote y datos variables comunes según diseño | dynamic_fields / _emit_values | Emisión → Datos | Actual |
| M04 | Recipientes y copias por recipiente | emit_count/emit_copies | Emisión → Serie | Actual |
| M05 | Numeración n/total y rangos, advertencia sin campo número | numero / parse_ranges / issue_pdf | Emisión → Numeración | Actual + Motor |
| M06 | Lote/PN/PB/conservación por envase | VesselDialog | Emisión → Datos por envase | Actual |
| M07 | Aplicar/limpiar fila, validar pesos y completar | save_row/clear_row/finish | Tabla por envase | Actual |
| M08 | Pegar tabla desde Excel | paste_table | Datos por envase → Pegar tabla | Actual; no importador Excel R5 |
| M09 | Ninguna/sin analizar/aprobado/rechazado | _state_change | Emisión → Estado de material | Actual |
| M10 | Fecha/nombre/condiciones, estado integrado o separado | _state_object / _paint_status | Estado / ubicación | Actual + Motor |
| M11 | Maestros de estado aprobados e íntegros | status_master / _approve_status | Configuración → Maestros de estado | Actual + Motor |
| M12 | Escalado proporcional, ancho/alto, restaurar original | _use_master_size / keep_proportion | Emisión → Formato | Actual + Motor |
| M13 | Seguridad configurable, preflight y límites reales de glifos | emit_safety / check_rendered_bounds | Seguridad / comprobaciones | Actual + Motor |
| M14 | Previsualizar A4, avisos y páginas | preview_issue | Emisión → Vista A4 | Actual |
| M15 | PDF de prueba de pendientes sin emisión definitiva | _test_mode / issue_pdf | Emisión → PDF de prueba | Actual + Motor |
| M16 | Generar PDF definitivo y registrar emisión | issue_pdf / Store.add_issue | Emisión → Generar PDF | Actual + Motor |
| M17 | Abrir último PDF / visor externo | open_last_pdf / open_path | Emisión → Abrir resultado | Actual |
| M18 | Retener lote/envases/estado/formato al navegar; no heredarlo a otra etiqueta | R3A select_emission_version / vistas retenidas | Controlador de trabajo | Actual; demo no emite |
| P01 | Elegir/guardar perfiles por nombre | _set_profile / add_profile | Emisión → Centro de impresión | Actual |
| P02 | A4 orientación, márgenes, separación, offsets | page_print_center / _profile_dict | Centro impresión → Perfil | Actual + Motor |
| P03 | Casilla inicial y marcas de corte | emit_start/emit_cut / plan_sheet | Centro impresión → Distribución | Actual + Motor |
| P04 | Impresora como referencia, no driver | emit_printer | Centro impresión → Referencia impresora | Actual |
| P05 | Capacidad, casillas omitidas y límites | plan_sheet / paint | Centro impresión → Vista A4 | Actual + Motor |
| P06 | Hoja A4 de calibración y regla | calibration / render_calibration_page | Centro impresión → Calibrar | Actual + Motor |
| P07 | Impresión mediante visor PDF al 100 % | open_path / instrucciones | Abrir PDF → visor del sistema | Actual; física no validada |
| H01 | Historial emisión/fecha/producto/revisión/cantidades/operador/reimpresión | page_history / issues | Historial → Tabla | Actual |
| H02 | Abrir PDF histórico íntegro | _history_open / intact_emission | Historial → Abrir PDF | Actual + Motor |
| H03 | Detalle variables/perfil/estado/envases/números/motivo | _history_detail | Historial → Detalle | Actual |
| H04 | Reimprimir números originales con motivo/vínculo independiente | _history_reprint | Historial → Reimprimir | Actual + Motor |
| H05 | Bloquear PDF alterado/revisión retirada/números no emitidos | _history_reprint | Validar reimpresión | Actual + Motor |
| C01 | Operador configurable, sin autenticación | page_admin.save_user | Configuración → Preferencias | Actual |
| C02 | Ubicación y COVEX_LABEL_DATA | location / paths | Configuración → Datos | Actual; demo IGNORA variable |
| C03 | Backup ZIP consistente SQLite WAL y documentos | _backup / LocalServices.backup | Configuración → Copias | Actual + Motor |
| C04 | Actualizar CM Word sin borrar anteriores | _import_cm / import_materials | Configuración → Catálogo CM | Actual |
| C05 | Materiales/códigos duplicados sin corregir automáticamente | material_duplicates / page_admin | Revisión de catálogo | Actual |
| C06 | Registrar revisión de maestros de estado | _approve_status | Configuración → Maestros de estado | Actual |
| C07 | Últimos movimientos de auditoría local | audit_entries / page_admin | Configuración → Actividad | Actual; no inviolable |
| C08 | UID estable, migración aditiva y copia previa | Store schema/user_version | Persistencia existente | Motor sin cambios |
| C09 | Actualizar sin sobrescribir data | paths / build guard / docs | Distribución / actualización | Actual; sin nuevo actualizador |
| C10 | Recuentos de etiquetas/vigentes/pendientes/emisiones/materiales y accesos rápidos del Inicio 0.3.1 | page_home / Store.stats | Configuración → Resumen; accesos por cabecera, sin recuperar tarjetas administrativas de inicio | Actual en main; tarjetas retiradas en R3A, resumen a conservar |

## No confundir pendientes con capacidades actuales

R2.5, tarjetas opcionales, composición nativa, entidad separada de variante/plantilla/trabajo, autoguardado/recuperación, nueva sincronización Editor/Emisión, importador Excel automatizado, QR/barcode dinámicos, etiquetas vinculadas, emisión recurrente, integraciones, servidor/multiusuario, driver de impresión, firma electrónica y restaurar ZIP desde UI no están implementados. La restauración actual es manual. No son funciones perdidas por esta prueba.

## Aceptación del 100 %

Cada fila debe contar con acceso Qt claramente localizable, prueba positiva y de bloqueo/cancelación cuando corresponda, conservación de configuraciones e histórico. Un botón informativo no acredita migración. Hasta verificar todas las filas, conservar la aplicación actual. La prueba explica los módulos no migrados y no finge importaciones, emisiones o aprobaciones. Aprobación externa no equivale a firma electrónica.
