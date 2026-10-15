# Matriz de conservación funcional — R3A integrada / R3B1 en revisión

Base oficial: main `5d27de30ce98ee89f17485225e3a45b92f544484`, R3A integrada por squash de PR #4. PR #2/#3 cerradas como sustituidas, sin integrarlas. Rama actual: `feature/r3b1-qt-advanced-editor`. **87 capacidades, ninguna eliminada.** R3B1 autorizado para desarrollo; integración pendiente de confirmación.

**Qt**: función nativa. R3A aceptada como hito de desarrollo; cambios R3B1 sujetos a revisión final. **Parcial**: parte Qt y parte Tkinter, indicado en cada fila. **Anterior**: función operativa en la versión Tkinter, accesible mediante un botón que abre la aplicación real con los mismos datos. **Motor**: reglas existentes conservadas, sin reescribir ni declararlas interfaz migrada. Word, impresión física y aceptación de DPI nativo siguen pendientes de pruebas reales.

| ID | Capacidad | Acceso actual / referencia | Acceso previsto Qt | Estado prueba |
|---|---|---|---|---|
| B01 | Inicio Biblioteca y navegación horizontal | R3A Application.show/studio_ui | Cabecera | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| B02 | Tabla, selección única, abrir doble clic/Enter | LibraryPanel.tree/open | Tabla → Editor / botón principal | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| B03 | Búsqueda dinámica código/nombre/producto/cliente/metadatos | LibraryService.entries | Buscador principal | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| B04 | Ctrl+K / buscador rápido | _open_library_picker / bind global | Ctrl+K → foco Biblioteca | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| B05 | Filtros categoría/familia/tipo/origen/cliente/país/idioma/versión/estado/incorporación | FILTER_FIELDS / LibraryPanel | Frecuentes + avanzados plegables | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| B06 | Limpiar búsqueda y filtros | LibraryPanel.reset | Limpiar | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| B07 | Favoritas / marcar y desmarcar | LibraryPanel.favorite | Biblioteca → Favoritas / Recientes / inspector | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| B08 | Recientes y última revisión abierta | LibraryService.opened/entries(recent) | Biblioteca → Favoritas / Recientes / inspector | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| B09 | Previsualización documento | LibraryPanel.preview / services.thumbnail | Inspector / ampliar / zoom | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| B10 | Revisiones y estado independiente del nombre | _master_detail / R3A select_revision | Inspector → Revisión | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| B11 | Columnas código/nombre/tipo/versión/origen/cliente/país/estado | R3A LibraryPanel | Tabla adaptable / ficha completa / tooltip | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| B12 | Ocultar/ajustar filtros e inspector | R3A toggle_filters/toggle_inspector | Más filtros / Inspector / Paneles; recordar preferencia opcional | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| B13 | Retener filtros/selección al navegar | R3A vistas retenidas | Controlador de sesión | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| D01 | Ficha: datos, dimensiones, revisiones, referencias | _master_detail | Documentos y acciones → Ficha | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| D02 | Abrir PDF maestro en visor externo | _master_detail.viewfile | Ficha → Abrir fuente | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| D03 | Originales y documentos conservados localmente | Store.add_label/add_version / asset_path | Ficha → Fuentes | Parcial: ficha/abrir original Qt; conservación de archivos por motor existente. |
| D04 | COVEX/cliente, nombre y referencia cliente | Importación / origin/customer/ref_customer | Ficha / filtros / importar | Parcial: filtro/ficha/importación individual Qt; importación carpeta anterior. |
| D05 | Incorporación distinta de origen/estado | acquisition | Ficha → Procedencia | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| D06 | Editar metadatos con fuente obligatoria | _edit_metadata / LibraryService.update_metadata | Documentos y acciones → Metadatos | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| D07 | Nueva revisión, código y motivo | _master_clone / clone_version | Documentos y acciones → Nueva revisión | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| D08 | Variantes actuales por revisión, incluida 00-R1 | _seed_r1_variant / versions | Selector + ficha | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| D09 | Registrar aprobación externa con responsable/evidencia/confirmación | _master_approve / approve | Documentos y acciones → Aprobación | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| D10 | Retirar vigente anterior al aprobar nueva; consulta retirada | Store.approve | Estado / ficha / selector | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| D11 | Vigente no editable; clonar para modificar | replace_pending_fields / AdvancedEditor | Editor solo lectura / Nueva revisión | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| D12 | Integridad antes de clonar/aprobar/emitir | verify_documents / verify_renderable | Guardas de servicios | Motor conservado y comprobado por regresión. |
| D13 | Fuente 00 defectuosa bloqueada, 00-R1 pendiente sin autoaprobación | integrity / render_geometry / storage | Inspector / preflight | Motor conservado y comprobado por regresión. |
| D14 | Comparador básico de imágenes, datos y campos | _master_compare | Documentos y acciones → Comparar | Anterior operativa; no migrada Qt, puente explícito. |
| I01 | Importar PDF/Word individual y datos obligatorios | import_label_dialog / _import_one | Documentos y acciones → Importar | Parcial: diálogo Qt y PDF verificado; conversión Word heredada sin prueba real. |
| I02 | Importar carpeta, progreso, detener, resumen/errores | import_folder_dialog | Importar → Carpeta | Anterior operativa; no migrada Qt, puente explícito. |
| I03 | Conversión Word local y errores por dependencia | docx_to_pdf | Importar → Verificación | Motor conservado y comprobado por regresión. |
| I04 | Recorte automático, geometría, rechazo multipágina | auto_crop / import_label | Importar → Revisar diseño | Motor conservado y comprobado por regresión. |
| I05 | Importar crea pendiente, nunca aprobación | Store.add_label | Documento pendiente | Motor conservado y comprobado por regresión. |
| E01 | Selección de campo por lista/lienzo | AdvancedEditor.select_list/on_select | Elementos / lienzo | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| E02 | Mover campo y bloquear posición | on_drag/on_up / locked | Lienzo / Propiedades | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| E03 | Agregar/quitar campos, clave única | add_field/remove_field | Elementos → Agregar/Quitar | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| E04 | Identificador y nombre visible | apply_props | Propiedades → Identificación | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| E05 | X/Y/ancho/alto en mm y validación | apply_props | Posición y tamaño | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| E06 | Fuente/tamaño, negrita, obligatorio | apply_props | Texto y comportamiento | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| E07 | Recortar por coordenadas/selección visual | edit_crop | Herramientas avanzadas → Recorte | Qt nativo R3B1: recorte visual/mm, rebase de campos/estado/auxiliares; exclusión bloqueada y undo/redo. |
| E08 | Zona de estado y control de proporciones | edit_status_area | Herramientas avanzadas → Zona de estado | Qt nativo R3B1: reserva visual/mm, activación/eliminación y proporción del maestro seleccionado. No aprueba estados. |
| E09 | Anclar a frase Word/PDF de referencia | align_selected_to_word / master_spans | Herramientas avanzadas → Anclar | Qt nativo R3B1: selección explícita de texto PDF/Word convertido, hash/caja/desplazamiento conservados; sin OCR. |
| E10 | Relocalizar desde Word reconocido | autolocate / locate_fields | Herramientas avanzadas → Recalcular | Qt nativo R3B1: anclas explícitas verificadas o plantillas ACETONA/EDROFONIO; fuente no reconocida bloqueada, sin detector universal. |
| E11 | Guardar configuración de borrador sin tocar original | AdvancedEditor.save | Guardar borrador | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| E12 | Reajuste avanzado de posiciones/recorte/zona | Editor + motor | Propiedades / herramientas avanzadas | Qt nativo R3B1: diseño completo en memoria, geometría/recorte/estado/auxiliares, sin editar fondo fijo. |
| E13 | Editor integrado y retención al navegar | R3A Application.editor | Editor central | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| E14 | Confirmar descarte al cambiar diseño | R3A editor | Diálogo trabajo activo | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| E15 | Zoom/ajuste del lienzo | Sin zoom dedicado en editor Tk | Barra lienzo / rueda | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| M01 | Elegir revisión para emitir | select_emission_version / biblioteca | Emisión → Selección | Parcial: selección Qt transferida a emisión anterior. |
| M02 | Preparar emisión exige vigencia/integridad | R3A emission_eligibility | Inspector → Preparar emisión | Qt funcional en R3A integrada; regresión mantenida en R3B1. |
| M03 | Lote y datos variables comunes según diseño | dynamic_fields / _emit_values | Emisión → Datos | Anterior operativa; no migrada Qt, puente explícito. |
| M04 | Recipientes y copias por recipiente | emit_count/emit_copies | Emisión → Serie | Anterior operativa; no migrada Qt, puente explícito. |
| M05 | Numeración n/total y rangos, advertencia sin campo número | numero / parse_ranges / issue_pdf | Emisión → Numeración | Anterior operativa; no migrada Qt, puente explícito. |
| M06 | Lote/PN/PB/conservación por envase | VesselDialog | Emisión → Datos por envase | Anterior operativa; no migrada Qt, puente explícito. |
| M07 | Aplicar/limpiar fila, validar pesos y completar | save_row/clear_row/finish | Tabla por envase | Anterior operativa; no migrada Qt, puente explícito. |
| M08 | Pegar tabla desde Excel | paste_table | Datos por envase → Pegar tabla | Anterior operativa; no migrada Qt, puente explícito. |
| M09 | Ninguna/sin analizar/aprobado/rechazado | _state_change | Emisión → Estado de material | Anterior operativa; no migrada Qt, puente explícito. |
| M10 | Fecha/nombre/condiciones, estado integrado o separado | _state_object / _paint_status | Estado / ubicación | Anterior operativa; no migrada Qt, puente explícito. |
| M11 | Maestros de estado aprobados e íntegros | status_master / _approve_status | Configuración → Maestros de estado | Anterior operativa; no migrada Qt, puente explícito. |
| M12 | Escalado proporcional, ancho/alto, restaurar original | _use_master_size / keep_proportion | Emisión → Formato | Anterior operativa; no migrada Qt, puente explícito. |
| M13 | Seguridad configurable, preflight y límites reales de glifos | emit_safety / check_rendered_bounds | Seguridad / comprobaciones | Anterior operativa; no migrada Qt, puente explícito. |
| M14 | Previsualizar A4, avisos y páginas | preview_issue | Emisión → Vista A4 | Anterior operativa; no migrada Qt, puente explícito. |
| M15 | PDF de prueba de pendientes sin emisión definitiva | _test_mode / issue_pdf | Emisión → PDF de prueba | Parcial: acceso PDF de prueba Qt; preparación/render/test marcado en versión anterior. |
| M16 | Generar PDF definitivo y registrar emisión | issue_pdf / Store.add_issue | Emisión → Generar PDF | Anterior operativa; no migrada Qt, puente explícito. |
| M17 | Abrir último PDF / visor externo | open_last_pdf / open_path | Emisión → Abrir resultado | Anterior operativa; no migrada Qt, puente explícito. |
| M18 | Retener lote/envases/estado/formato al navegar; no heredarlo a otra etiqueta | R3A select_emission_version / vistas retenidas | Controlador de trabajo | Parcial: trabajo de campos Qt conservado; formulario de emisión retenido en puente Tk. |
| P01 | Elegir/guardar perfiles por nombre | _set_profile / add_profile | Emisión → Centro de impresión | Parcial: selección y guardado de perfil Qt en Editor; aplicación a emisión definitiva continúa explícita en Tkinter. |
| P02 | A4 orientación, márgenes, separación, offsets | page_print_center / _profile_dict | Centro impresión → Perfil | Parcial: tamaño, orientación A4, márgenes, separación y seguridad Qt para prueba; offsets/centro completo siguen en Tkinter. |
| P03 | Casilla inicial y marcas de corte | emit_start/emit_cut / plan_sheet | Centro impresión → Distribución | Anterior operativa; no migrada Qt, puente explícito. |
| P04 | Impresora como referencia, no driver | emit_printer | Centro impresión → Referencia impresora | Anterior operativa; no migrada Qt, puente explícito. |
| P05 | Capacidad, casillas omitidas y límites | plan_sheet / paint | Centro impresión → Vista A4 | Anterior operativa; no migrada Qt, puente explícito. |
| P06 | Hoja A4 de calibración y regla | calibration / render_calibration_page | Centro impresión → Calibrar | Anterior operativa; no migrada Qt, puente explícito. |
| P07 | Impresión mediante visor PDF al 100 % | open_path / instrucciones | Abrir PDF → visor del sistema | Anterior operativa; no migrada Qt, puente explícito. |
| H01 | Historial emisión/fecha/producto/revisión/cantidades/operador/reimpresión | page_history / issues | Historial → Tabla | Anterior operativa; no migrada Qt, puente explícito. |
| H02 | Abrir PDF histórico íntegro | _history_open / intact_emission | Historial → Abrir PDF | Anterior operativa; no migrada Qt, puente explícito. |
| H03 | Detalle variables/perfil/estado/envases/números/motivo | _history_detail | Historial → Detalle | Anterior operativa; no migrada Qt, puente explícito. |
| H04 | Reimprimir números originales con motivo/vínculo independiente | _history_reprint | Historial → Reimprimir | Anterior operativa; no migrada Qt, puente explícito. |
| H05 | Bloquear PDF alterado/revisión retirada/números no emitidos | _history_reprint | Validar reimpresión | Anterior operativa; no migrada Qt, puente explícito. |
| C01 | Operador configurable, sin autenticación | page_admin.save_user | Configuración → Preferencias | Anterior operativa; no migrada Qt, puente explícito. |
| C02 | Ubicación y COVEX_LABEL_DATA | location / paths | Configuración → Datos | Anterior operativa; no migrada Qt, puente explícito. |
| C03 | Backup ZIP consistente SQLite WAL y documentos | _backup / LocalServices.backup | Configuración → Copias | Anterior operativa; no migrada Qt, puente explícito. |
| C04 | Actualizar CM Word sin borrar anteriores | _import_cm / import_materials | Configuración → Catálogo CM | Anterior operativa; no migrada Qt, puente explícito. |
| C05 | Materiales/códigos duplicados sin corregir automáticamente | material_duplicates / page_admin | Revisión de catálogo | Anterior operativa; no migrada Qt, puente explícito. |
| C06 | Registrar revisión de maestros de estado | _approve_status | Configuración → Maestros de estado | Anterior operativa; no migrada Qt, puente explícito. |
| C07 | Últimos movimientos de auditoría local | audit_entries / page_admin | Configuración → Actividad | Anterior operativa; no migrada Qt, puente explícito. |
| C08 | UID estable, migración aditiva y copia previa | Store schema/user_version | Persistencia existente | Motor conservado y comprobado por regresión. |
| C09 | Actualizar sin sobrescribir data | paths / build guard / docs | Distribución / actualización | Motor conservado y comprobado por regresión. |
| C10 | Recuentos de etiquetas/vigentes/pendientes/emisiones/materiales y accesos rápidos del Inicio 0.3.1 | page_home / Store.stats | Versión anterior → Inicio (recuentos) / Configuración | Anterior operativa; no migrada Qt, puente explícito. |
## No confundir pendientes con capacidades actuales

R2.5, tarjetas opcionales, composición nativa, entidad de trabajo de emisión independiente, autoguardado/recuperación, nueva sincronización Editor/Emisión, importador Excel automatizado, QR/barcode dinámicos, etiquetas vinculadas, emisión recurrente, integraciones, servidor/multiusuario, driver de impresión, firma electrónica y restaurar ZIP desde UI no están implementados. La restauración actual es manual. No son funciones perdidas por esta prueba.

## Aceptación del 100 %

Cada fila debe contar con acceso Qt claramente localizable, prueba positiva y de bloqueo/cancelación cuando corresponda, conservación de configuraciones e histórico. Un botón informativo no acredita migración. Hasta verificar todas las filas, conservar la aplicación actual. La rama identifica los módulos no migrados y abre las herramientas reales anteriores. No simula ejecución. Aprobación externa no equivale a firma electrónica.


## Límites y criterio para sustituir la distribución

La aplicación distribuida 0.3.1 sigue siendo Tkinter y main permanece intacta. El paquete experimental Qt contiene un ejecutable compañero Tkinter separado para acceder al 100 % del inventario; **eso no significa que el 100 % esté migrado o aceptado**. No se sustituye la distribución mientras queden funciones sin acceso/prueba satisfactoria y sin autorización expresa.

Los nuevos ajustes R3A son filtros secundarios plegables con preferencia opcional y resumen activo, tabla prioritaria/configurable, inspector agrupado, tres acciones separadas (Editor / Preparar emisión / PDF de prueba), y retención con Guardar/Descartar/Cancelar. Un PDF de prueba nunca genera emisión definitiva, incluso al partir de una revisión vigente. 00-R1 permanece pendiente salvo registro explícito de aprobación externa documentada; ni clonación ni despliegue conceden aprobación.

Pruebas de rama: núcleo existente + pruebas Qt/servicio de estados, integridad, metadatos, importación PDF, variantes, guardado, trabajo activo, cancelación y puente. CI añade Qt real y ejecutables Qt/Tk con PDF de prueba marcado, retención y ausencia de registro definitivo. Estados Qt de esta tabla no acreditan todavía aceptación interactiva COVEX, Word ni impresión física.


## Ajustes finales de usabilidad — dirección visual aprobada 09/10/2026

En el hito histórico R3A se conservaron 87 filas con clasificación 33 Qt, 7 parciales, 40 anteriores y 7 motor; la clasificación actual R3B1 figura abajo. B01/B12: Historial y Configuración compactos tienen descripción emergente y nombre accesible, identificando Tkinter. B09/E15: «Vista N%» y descripción del zoom relativo a Ajustar; no es escala física ni modifica el PDF. M02: Preparar emisión pendiente/retirada usa fondo neutro deshabilitado, conservando las guardas existentes. E11: Guardar solo se habilita con cambios, revisión pendiente y compañero cerrado; sin cambios/solo lectura/bloqueo tiene presentación neutra y motivo.

La dirección visual Industrial Moderno de Biblioteca/Editor está aprobada definitivamente por el propietario. Estos ajustes no amplían R3A ni inician R3B/R3C. La aceptación de uso en equipos COVEX/Word/impresión sigue pendiente. Capturas de pendiente, vigente habilitada, retirada, guardado limpio/con cambios y editor solo lectura se generan en los tres factores Qt y se incluyen en el artefacto de la revisión.

## Evidencia y ampliaciones R3B1 — 11/10/2026

Las 87 IDs se conservan. Clasificación en esta rama: 38 Qt, 8 parciales, 34 anteriores y 7 motor. E07–E10/E12 pasan a Qt; P01/P02 pasan a parciales. Ninguna función de Emisión definitiva se declara migrada. E11 guarda campos, recorte y estado juntos; compara el diseño completo y la identidad de fuente dentro de una transacción. Esquema SQLite sin migración.

Ampliaciones nuevas, fuera del recuento histórico de 87 capacidades: selección múltiple, alineación/distribución geométrica, transformación proporcional de campos/auxiliares/estado, historial de deshacer/rehacer, anclas persistentes verificables y prueba PDF desde el diseño en memoria. No incluyen composición libre de textos fijos, tablas o imágenes.

Pruebas: `tests/test_editor_layout.py`, `tests/test_r3b1_qt.py` y `qt_ui/advanced_checks.py`; regresión R3A y núcleo existente. Los resultados ejecutados y CI se presentan en la PR de esta revisión. Word real, impresión física, Windows 10/11/equipos COVEX y GMP siguen pendientes. 00-R1 continúa PENDING; sin R3B2/R3B3, autoguardado ni sincronización bidireccional de variables.


## Evidencias adicionales de R3B2 (sin reemplazar las 87 IDs)

Las 87 filas anteriores permanecen como línea base. R3B2 mantiene sus accesos, añade variantes reales y refuerza los contratos siguientes. No se reclasifica como Qt ninguna pantalla que continúe en Tkinter.

| IDs existentes afectadas | Evidencia R3B2 |
|---|---|
| B01–B13, D01–D07 | Regresión Qt existente, filtros/favoritos/revisiones sin multiplicar filas por variantes. Selector en Inspector y Editor. |
| D08–D13 | `test_variants_v4`: aprobación independiente, congelación, coexistencia, evidencia/hash, derivación sin aprobación y revisión 00-R1 PENDING. No hay conversión ni siembra automática al migrar. |
| `D14` | Comparador básico Tk conservado; comparación documental revisión/variante adicional en Qt. |
| E01–E15 | Suite R3B1 y controles de widgets conservados; edición de layout completo en variante DRAFT. Originales intactos. |
| M01–M18 | `emission_contract`: selección y generación obsoletas bloqueadas, snapshot de toda emisión nueva incluso heredada; smoke Tk fuente/portable con variante, PDF de prueba y emisión sintética definitiva. |
| P01–P07 | Perfiles/escala A4 independientes de diseño nominal; geometría de variante cotejada con posiciones PDF con tolerancia 0.1 mm. Herramientas de impresión existentes conservadas. |
| H01–H05 | Reimpresión con snapshot, enlace/motivo/números originales, rechazo de retirada o PDF alterado. Histórico NULL conserva ruta heredada y advertencia explícita, sin snapshot inferido retrospectivo. |
| C01–C10 | Backup v4 incluye evidencias/barrera/manifiesto y SQLite consistente; restauración íntegra; UID/datos previos preservados; recuentos no incluyen variantes como revisiones. |

La normalización aditiva histórica se ejecuta sobre staging, antes de v3→v4, con backup del esquema original. Se conservan las pruebas de actualización 0.1/0.2: cambian sus rutas de backup a las del protocolo nuevo y se ensaya conservación de campos/perfiles/operador. Fuente nueva sin maestros sigue vacía.

## Evidencias adicionales de R3B3 (se conservan las 87 IDs)

La línea base R3A/R3B1 y las evidencias de R3B2 anteriores describen cada etapa.
R3B3 sustituye la limitación anterior de ausencia de autoguardado de datos variables.
El diseño estructural conserva guardado explícito y las herramientas avanzadas.

| Grupo de capacidad conservada | Evidencia conjunta R3B2+B3 |
|---|---|
| Biblioteca, fuentes, revisiones, variantes | Selección independiente de trabajo/revisión/variante, huella documental, 00-R1 heredada PENDING; `test_variants_v4.py` y checks de variantes. |
| Editor y datos variables | Panel compartido con Emisión, datos de lote y recipiente, autoguardado local; `test_emission_work_qt.py` y capturas `04-editor-variable-panel`. |
| Formato y perfiles | Configuración del trabajo separada del diseño; perfiles reutilizables y offsets conservados en Qt→Tk→Qt. |
| Emisión definitiva e historial | Snapshot SQLite v4 obligatorio con/sin variante, operación de trabajo única, revalidación y reconciliación; `test_emission_work.py`, contrato de emisión y reimpresiones heredadas. |
| Transición Qt/Tk | Tk conserva edición/impresión y usa el mismo repositorio, CAS y guardado antes de navegar/cerrar; `test_emission_work_tk.py`, smoke fuente/portable. |
| Backup, recuperación y compatibilidad | Consentimiento expreso v3→v4, cancelación intacta, barrera frente a EXE previos, archivos de trabajo incluidos en backup, recuperación tras muerte del proceso. |

`--self-check` mantiene los 80 controles de interacción existentes a 100/125/150 %.
`--variant-check` y `--work-check` añaden cobertura real sin sustituir esos controles.
La matriz no afirma validación Word, impresión física, equipos COVEX ni GMP.
