# Correcciones de aceptación Windows — PR #29

La entrega anterior (`46d3eab`) fue **NO CONFORME** en aceptación presencial. Sus CI verdes no invalidan los defectos comunicados en [el comentario obligatorio](https://github.com/FMAcovex/covex-label-manager/pull/29#issuecomment-6240765573). Esta ampliación mantiene UX-1/2/3 y las 87 capacidades. La PR continúa en borrador; cualquier nuevo portable necesita aceptación humana, no implica validación GMP.

## Diagnóstico y correcciones

| Incidencia | Causa demostrada / cambio | Regresión |
|---|---|---|
| P1: cerrar el importador termina la aplicación | Ambos importadores asignaban un entero a `self.done`, ocultando el método virtual `QDialog.done(int)`. Un cierre modal real reproduce `Error calling Python override of QDialog::done(): TypeError: 'int' object is not callable`. El contador pasa a `processed`; Qt conserva su método. Cerrar/Escape/X durante un lote solicita detener y cierra al terminar el archivo actual, sin revertir incorporaciones. No es la antigua hipótesis QScreen: su protección se conserva. | `main_qt.py --import-check`: 18 escenarios con `QApplication.exec` y `QDialog.exec` reales; dos importadores × antes/durante/después × botón/Escape/X. Tras cada cierre navega y comprueba el lote guardado. CI repite fuente y EXE a tres escalas. |
| P1: importación confusa y controles superpuestos | Asistente de tres pasos: carpeta visible/cambiable; revisión de sugerencias/identidad; resultados por archivo con acceso al Editor. Nombre/código/revisión/categoría editables, identidad completa y edición masiva de campos marcados/acción de filas seleccionadas. Combos con altura calculada, tabla desplazable y tooltips. Diagnósticos legibles; todo se omite por defecto. | `tests/test_r6b_acceptance_fixes_qt.py`: seis tamaños, edición individual/masiva, destino de nueva revisión, confirmación reiniciada al editar, hash modificado rechazado, incorporación PENDIENTE y apertura del Editor. R5B conserva servicio y bloqueos. |
| P1: solo se aceptaba kg | Entrada kg/g/mg, comparación canónica en kg mediante Decimal. Texto de entrada conservado en trabajo/snapshot. El sufijo documental del campo fija la unidad de salida; se convierte la cantidad antes de añadirlo una sola vez. | `tests/test_mass_units.py`: coma/punto, conversiones, unidades mezcladas, PN≤PB, Excel, compatibilidad sin sufijo, texto PDF y metadatos sin mutación. |
| P1: actualización manual constante | Espera de 450 ms; un solo render de PRUEBA en proceso separado, con servicio/conexión SQLite propios. QThread solo espera el proceso: no ejecuta MuPDF junto al visor de la interfaz. Datos editables durante el cálculo. Vista desactualizada/actualizando/errores explícitos; generaciones/tokens obsoletos se descartan y la última edición vuelve a programarse. | Pruebas de ráfaga de ediciones, número/formato, unidad inválida y recuperación; resultado obsoleto descartado y sin emisiones. Se comprueba PID distinto y reintento acotado de lecturas ocupadas sin ignorar fallos. Las regresiones existentes conservan confirmación, hash, token y cambios concurrentes. |
| P2: menú de variantes opaco | Encabezados separan revisión documental y variante e indican estado. Solo las acciones aplicables están en primer nivel; las demás se conservan en «Otras acciones · requisitos», con motivo visible, sin depender exclusivamente del tooltip. | `test_variant_menu_explains_available_transitions` mantiene las mismas expectativas de habilitación. Los repositorios siguen validando estados y aprobación externa. |

### Flujo de importación

1. Biblioteca → Documento → Importar carpeta. Elegir/cambiar carpeta dentro del asistente; revisar ruta y número de documentos.
2. Revisar nombres/revisiones y categoría sugerida por carpeta. La sugerencia no acredita clasificación. Elegir explícitamente Nueva etiqueta, Nueva revisión u Omitir; los bloqueados/duplicados no se desbloquean. La edición masiva afecta solo a campos marcados y filas seleccionadas.
3. Nueva revisión exige destino existente y conserva la identidad de ese expediente; no renombra ni reclasifica su maestro. Revisar el documento mediante Vista previa (Word necesita Word/LibreOffice o PDF asociado). Confirmar las identidades y después la importación.
4. Consultar cada resultado, detener si procede y abrir una revisión importada en Editor para configurar campos/recorte. **PENDIENTE no significa aprobado ni listo para emisión productiva**.

El acceso al Editor comprueba que se ha seleccionado exactamente la revisión importada. Si la búsqueda/categoría/favoritas la excluye, limpia los filtros e informa en la barra de estado; nunca abre la etiqueta anterior por defecto. Cerrar el asistente sin pedir Editor conserva filtros y selección. Hay regresión para ambos casos.

La selección de una denominación muy larga en el resumen tampoco puede imponer su ancho al diálogo: se limita el tamaño preferido del desplegable, conservando el nombre íntegro en su modelo y tooltip. La regresión reproduce el crecimiento previo a 3632 px y exige mantener 886×424 con el mismo texto, sin truncar datos.

La conversión Word sigue siendo secuencial y puede ocupar la interfaz durante el archivo actual, con los límites existentes del convertidor. No se mata Word ni se interrumpe una transacción: Detener se aplica entre archivos. Esta limitación residual (UX-15) no se disfraza de concurrencia Word resuelta. Los originales y hashes siguen protegidos por R5B.

### Contrato de unidades

- Únicamente **kg, g y mg**, sin distinguir mayúsculas; no se aceptan lb, t, concentraciones ni unidades desconocidas. Sin unidad = **kg**, por compatibilidad histórica; la interfaz lo explica.
- `350 g`, `0,35 kg` y `350000 mg` tienen igual masa. PN/PB comunes y por recipiente se comparan después de convertir, no como cifras sin unidad.
- Campo con sufijo aprobado ` KG`: `350g` → `0.35 KG`. Campo con sufijo ` g`: `0,35 kg` → `350 g`. No se cambia el PDF maestro, su tipografía ni el diseño aprobado; nunca se convierte `350g` en `350KG`.
- Sin sufijo documental configurado se mantiene el texto/unidad introducidos. No se intenta inferir semántica mediante OCR ni se modifica automáticamente un diseño aprobado. Las unidades fijas deben estar representadas correctamente en los campos documentales; comprobarlo en aceptación del diseño.
- Excel admite unidad explícita en cada celda y cabeceras `PN g`, `PN (g)`, `Peso neto g` / `PB mg`, etc. Una unidad explícita en una celda prevalece sobre la cabecera; vacío sigue heredando el valor común.

### Seguridad de la vista previa

El render automático es exclusivamente no productivo y lleva marca PRUEBA. Usa una instantánea de entrada sin mantener el bloqueo exclusivo de trabajo durante el cálculo, para no impedir autoguardado. Verifica generación y token antes/después; la UI vuelve a contrastarlos antes de adoptar el PDF. El proceso hijo abre/cierra su propia conexión SQLite y aísla también el estado nativo de MuPDF del visor Qt; no se comparten conexiones ni se renderiza PDF desde un hilo secundario del proceso de interfaz. QThread solo espera la terminación y entrega el informe. Nunca se ejecutan dos procesos de vista previa a la vez; la emisión queda bloqueada durante el cálculo y con datos inválidos/desactualizados. Una caída del hijo o ausencia de informe deja la emisión bloqueada, no termina la aplicación. El cálculo automático tiene un límite de 90 s, sin registrar emisión; la acción manual existente se conserva. Cerrar la ventana principal mientras calcula pide esperar, no destruye un QThread activo.

Emitir sigue exigiendo revisión/variante elegibles, preflight vigente, ausencia de avisos del render, confirmación explícita, nuevo token, SHA256 de la prueba y las validaciones del servicio/SQLite. «Actualizar vista previa» se conserva como reintento manual, no como paso obligatorio de cada edición. No se aprueban documentos ni se registra una emisión al actualizar.

## Conservación de las 87 capacidades

La [matriz íntegra](CONSERVACION_87.md) conserva los mismos 87 IDs, 78 rutas Qt, 2 mixtas y 7 de motor/procedimiento. No se modifica SQLite v4 ni su migración. Correspondencias afectadas:

| IDs existentes | Acceso/controladores actuales |
|---|---|
| D03, D04, D07, I01–I04 | `FolderImportMixin.import_folder_native` → `ControlledImportDialog` → `catalog_migration_preview/apply`; originales, inventario, conciliación y aprobación documental siguen separados. |
| D08, D11 | Selector nativo + `VariantsMixin.build_variant_menu`; la aprobación de revisión no se convierte en aprobación de variante. |
| M03, M06–M08 | WorkPanel, parse_tabular_vessels, validación canónica y conversión en `_overlay_field`; mismos trabajos y datos por envase. |
| M13–M16, M18 | EmissionCentreMixin, PreviewTask y servicios existentes; autoguardado, prueba, preflight y emisión definitiva separados. |
| H01–H05, C03 | Historial, snapshots, reimpresión y backup siguen en los servicios/regresiones existentes; no se alteran los PDF históricos. |

## Evidencias visuales sintéticas

`scripts/ux_acceptance_visual.py` reproduce **5 vistas anteriores + 12 posteriores**, a 1366×768 y 1920×1080, factores Qt 1/1.25/1.5: 102 PNG con manifiestos y SHA256. El antes usa código inmutable `46d3eab93381a81bae47f04ffe367334c8f16709`, no una reconstrucción estética. Los datos se generan en DemoSession temporal, sin abrir bases propias. Ninguna captura aprueba documentos ni emite; solo se confirma una importación sintética PENDIENTE.

Los PNG completos y JSON se conservan en el artefacto de CI (`test-results/acceptance-visual`). Se versionan SVG sintéticos seleccionados (tres configuraciones); no se publican documentos reales. Ejemplos:

| Antes | Después |
|---|---|
| [Importador anterior](aceptacion-visual/before/1366x768_1/01-importador.svg) | [Identidades editables](aceptacion-visual/after/1366x768_1/02-identidades.svg) |
| [Masas rechazadas](aceptacion-visual/before/1366x768_1/06-emision-masas.svg) | [Vista actualizada](aceptacion-visual/after/1366x768_1/07-emision-actualizada.svg) |
| [Menú anterior](aceptacion-visual/before/1366x768_1/10-menu-pending.svg) | [Menú por estado](aceptacion-visual/after/1366x768_1/10-menu-pending.svg) |

La evidencia local usa Linux/Xorg dummy/Qt 6.8.3 y tamaños lógicos derivados; no equivale a cambiar físicamente el DPI de Windows. CI repite estas vistas en Windows, además del gate integrado anterior. La validación física, Word/Office real, lector de pantalla, impresión y aprobación GMP siguen pendientes.

La primera regresión Windows (`891b52e`, ejecución `39072306034`) detectó un mínimo nativo de 453 px frente al límite de 424 px. Se corrige con scroll **solo del cuerpo de cada paso**, dejando encabezado, confirmación y acciones fuera; se conserva el límite de aceptación y se añade una prueba con tipografía ampliada. Dos aserciones de lote detectaron además U+00AD en la extracción de Arial: se normaliza a guion, igual que las pruebas R3C existentes, sin cambiar datos, fuentes ni PDF aprobados. Se exige el lote más reciente y la ausencia de los anteriores; no se eliminan comprobaciones.

En `d9afc92` las 27 regresiones de aceptación, las 295 restantes, los cierres a tres escalas y las 420 capturas Windows pasaron. El check R3C al 125 % detectó `no_unexpected_dialogs`; el informe anterior no incluía el título y no permite identificar con certeza aquel modal. Se reproduce un defecto de su vigía: consideraba inesperado incluso el diálogo de reimpresión que el propio check estaba operando, según coincidiera el tick de 10 s con la ejecución. El diagnóstico registra ahora cada modal desde Show y permite **solo la identidad exacta del diálogo esperado**, durante esa acción; cualquier otro modal, incluidos hijos de ese diálogo, sigue fallando. Hay regresión con tick forzado sobre el diálogo esperado y otro modal desconocido; se conserva la aserción original y se añade la del diálogo esperado único. El workflow imprime el JSON/traceback completo al fallar, sin depender de la descarga del artefacto, y adelanta ese check para confirmar el resultado en Windows y revelar cualquier otra incidencia.

El check nativo exige además una prueba automática vigente **antes** de ejercitar el botón manual, tanto desde fuente como desde el EXE. Una regresión fuerza el fallo del trabajador y verifica que el check falla sin recurrir al refresco manual. Así un empaquetado defectuoso del proceso hijo no puede quedar enmascarado por una prueba manual satisfactoria.

## Comprobación y aceptación del nuevo portable

Consultar [la guía](PRUEBAS_Y_PORTABLE.md) y el resultado CI del commit entregado. Tras descargar y extraer completamente el nuevo ZIP:

1. Ejecutar `PROBAR_DEMO_QT.bat`; no reutilizar la instalación productiva ni los datos reales. Importar exclusivamente fuentes sintéticas del entorno de prueba.
2. Probar Cerrar/Escape/X antes, durante y después del lote; navegar y comprobar que permanecen el trabajo y las incorporaciones anteriores.
3. Cambiar carpeta, editar y aplicar datos comunes, revisar duplicados/destino, previsualizar, importar y abrir Editor. Confirmar legibilidad y pies a 1366×768/150 %.
4. Probar kg/g/mg y el sufijo documental conocido de una etiqueta sintética; comprobar en PDF las cantidades y la coherencia PN/PB, también con Excel.
5. Editar rápidamente lote, recipientes, formato y unidades; comprobar actualización sin pulsar Actualizar, bloqueo ante errores y preflight/confirmación antes de una emisión de ensayo.
6. Revisar menús con revisión pendiente/vigente/retirada y variante borrador/pendiente/aprobada/retirada; verificar requisitos y separación documental.

Registrar CONFORME/NO CONFORME, SHA del portable, versión Windows y escala real. Mantener la PR en borrador hasta decisión humana; no squash ni merge.
