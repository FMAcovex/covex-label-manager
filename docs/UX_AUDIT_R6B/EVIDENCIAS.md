# Evidencias visuales sintéticas

Capturas del widget real mediante `QWidget.grab()` (PNG local) y `QWidget.render(QSvgGenerator)` (SVG versionado, texto/vector con imágenes sintéticas integradas). Los SVG no son propuestas ni reconstrucciones manuales; muestran los widgets existentes, sin decoración de ventana del SO.

Solo fixtures `DemoSession` y archivos creados en directorios temporales. Los PNG completos están en `test-results/ux-audit/<configuración>/`; sus SHA-256 figuran en [inventario-runtime.json](inventario-runtime.json). Los SVG seleccionados se pueden revisar en esta PR. No se usa una aplicación productiva ni se aprueba documento real.

| Configuración | Capturas | Errores del harness | Ventanas mayores que el área solicitada |
|---|---:|---:|---:|
| 1366x768_1 | 51 | 0 | 0 |
| 1366x768_1.25 | 51 | 0 | 2 |
| 1366x768_1.5 | 51 | 0 | 4 |
| 1920x1080_1 | 51 | 0 | 0 |
| 1920x1080_1.25 | 51 | 0 | 0 |
| 1920x1080_1.5 | 51 | 0 | 0 |

El área cliente pedida es `floor(ancho/factor) × (floor(alto/factor) − 40)` DIP; se reservan 40 DIP para marco/barra. Xorg tiene 1920×1080; se emulan los dos tamaños mediante el área de ventana y los factores Qt, no mediante Windows ni seis monitores físicos. Las mínimas de Qt pueden impedir el tamaño pedido; se registra el real, sin recortar o falsear el resultado. No hay comparación automática con una golden baseline anterior.

En `1366×768 / 150 %`, un diálogo de 676 DIP exige 1014 px, mayor que el alto físico objetivo: fallo de adaptación demostrable respecto a ese objetivo, pendiente de repetir en Windows. El diseñador de hoja consulta el QScreen Xorg real; su tamaño automático no prueba un monitor Windows 1366×768. Los modales se intentan ajustar al área objetivo, conservando todas las restricciones mínimas de la aplicación.

## Galería

| Configuración / estado | Captura SVG |
|---|---|
| 1366x768_1 · 01-biblioteca-pendiente · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_01-biblioteca-pendiente.svg) |
| 1366x768_1 · 03-biblioteca-documentos · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_03-biblioteca-documentos.svg) |
| 1366x768_1 · 04-biblioteca-filtros · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_04-biblioteca-filtros.svg) |
| 1366x768_1 · 07-editor-pendiente · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_07-editor-pendiente.svg) |
| 1366x768_1 · 08-editor-herramientas · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_08-editor-herramientas.svg) |
| 1366x768_1 · 10-editor-datos-trabajo · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_10-editor-datos-trabajo.svg) |
| 1366x768_1 · 11b-editor-variante-borrador · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_11b-editor-variante-borrador.svg) |
| 1366x768_1 · 12-emision-datos · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_12-emision-datos.svg) |
| 1366x768_1 · 14-emision-formato · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_14-emision-formato.svg) |
| 1366x768_1 · 16-emision-preview · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_16-emision-preview.svg) |
| 1366x768_1 · dynamic-01 · Confirmar emisión definitiva | [SVG](evidencia/1366x768_1_dynamic-01.svg) |
| 1366x768_1 · dynamic-02 · Metadatos documentados | [SVG](evidencia/1366x768_1_dynamic-02.svg) |
| 1366x768_1 · dynamic-03 · Nueva revisión pendiente | [SVG](evidencia/1366x768_1_dynamic-03.svg) |
| 1366x768_1 · dynamic-04 · Pegar datos por recipiente | [SVG](evidencia/1366x768_1_dynamic-04.svg) |
| 1366x768_1 · dynamic-05 · Recorte del documento | [SVG](evidencia/1366x768_1_dynamic-05.svg) |
| 1366x768_1 · dynamic-06 · Referencia PDF / Word convertido | [SVG](evidencia/1366x768_1_dynamic-06.svg) |
| 1366x768_1 · dynamic-07 · Borrado y continuación del campo | [SVG](evidencia/1366x768_1_dynamic-07.svg) |
| 1366x768_1 · dynamic-08 · Reajuste proporcional de campos | [SVG](evidencia/1366x768_1_dynamic-08.svg) |
| 1366x768_1 · dynamic-09 · Reserva para etiqueta de estado | [SVG](evidencia/1366x768_1_dynamic-09.svg) |
| 1366x768_1 · dynamic-10 · Formato físico y prueba PDF | [SVG](evidencia/1366x768_1_dynamic-10.svg) |
| 1366x768_1 · dynamic-11 · Vista previa · PDF de prueba | [SVG](evidencia/1366x768_1_dynamic-11.svg) |
| 1366x768_1 · dynamic-12 · Nuevo trabajo de emisión | [SVG](evidencia/1366x768_1_dynamic-12.svg) |
| 1366x768_1 · 17-historial-detalle · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_17-historial-detalle.svg) |
| 1366x768_1 · 18-historial-pdf · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_18-historial-pdf.svg) |
| 1366x768_1 · dynamic-13 · Reimpresión controlada · #1 | [SVG](evidencia/1366x768_1_dynamic-13.svg) |
| 1366x768_1 · 19-config-resumen · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_19-config-resumen.svg) |
| 1366x768_1 · 20-config-datos · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_20-config-datos.svg) |
| 1366x768_1 · 24-aprobacion-revision · Registrar aprobación documental · revisión pendiente | [SVG](evidencia/1366x768_1_24-aprobacion-revision.svg) |
| 1366x768_1 · 25-comparar · Comparar revisiones · Solo consulta | [SVG](evidencia/1366x768_1_25-comparar.svg) |
| 1366x768_1 · 26-importar-carpeta · Importar carpeta · Documentos pendientes | [SVG](evidencia/1366x768_1_26-importar-carpeta.svg) |
| 1366x768_1 · 27-importacion-controlada · R5B · Importación y conciliación documental | [SVG](evidencia/1366x768_1_27-importacion-controlada.svg) |
| 1366x768_1 · 28-disenador-hoja · Diseñador de hojas · mm | [SVG](evidencia/1366x768_1_28-disenador-hoja.svg) |
| 1366x768_1 · 29-casillas-utilizadas · Casillas ya utilizadas · primera hoja | [SVG](evidencia/1366x768_1_29-casillas-utilizadas.svg) |
| 1366x768_1 · 30-calibracion · Calibrar impresora · Prueba no productiva | [SVG](evidencia/1366x768_1_30-calibracion.svg) |
| 1366x768_1 · 31-preaceptacion · R6A - Diagnóstico de preaceptación | [SVG](evidencia/1366x768_1_31-preaceptacion.svg) |
| 1366x768_1 · 32-sesion-uat · R6B · Pruebas presenciales y evidencias | [SVG](evidencia/1366x768_1_32-sesion-uat.svg) |
| 1366x768_1 · 32b-sesion-uat-casos · R6B · Pruebas presenciales y evidencias | [SVG](evidencia/1366x768_1_32b-sesion-uat-casos.svg) |
| 1366x768_1 · 33-conciliar-master · R5C · Conciliación con libro máster (solo lectura) | [SVG](evidencia/1366x768_1_33-conciliar-master.svg) |
| 1366x768_1 · 34-config-dock-residual · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_34-config-dock-residual.svg) |
| 1366x768_1 · 35-acceso-heredado-residual · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_35-acceso-heredado-residual.svg) |
| 1366x768_1 · 36-emision-errores · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1_36-emision-errores.svg) |
| 1366x768_1.5 · 01-biblioteca-pendiente · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_01-biblioteca-pendiente.svg) |
| 1366x768_1.5 · 03-biblioteca-documentos · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_03-biblioteca-documentos.svg) |
| 1366x768_1.5 · 04-biblioteca-filtros · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_04-biblioteca-filtros.svg) |
| 1366x768_1.5 · 07-editor-pendiente · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_07-editor-pendiente.svg) |
| 1366x768_1.5 · 08-editor-herramientas · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_08-editor-herramientas.svg) |
| 1366x768_1.5 · 10-editor-datos-trabajo · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_10-editor-datos-trabajo.svg) |
| 1366x768_1.5 · 11b-editor-variante-borrador · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_11b-editor-variante-borrador.svg) |
| 1366x768_1.5 · 12-emision-datos · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_12-emision-datos.svg) |
| 1366x768_1.5 · 14-emision-formato · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_14-emision-formato.svg) |
| 1366x768_1.5 · 16-emision-preview · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_16-emision-preview.svg) |
| 1366x768_1.5 · dynamic-01 · Confirmar emisión definitiva | [SVG](evidencia/1366x768_1.5_dynamic-01.svg) |
| 1366x768_1.5 · dynamic-02 · Metadatos documentados | [SVG](evidencia/1366x768_1.5_dynamic-02.svg) |
| 1366x768_1.5 · dynamic-03 · Nueva revisión pendiente | [SVG](evidencia/1366x768_1.5_dynamic-03.svg) |
| 1366x768_1.5 · dynamic-04 · Pegar datos por recipiente | [SVG](evidencia/1366x768_1.5_dynamic-04.svg) |
| 1366x768_1.5 · dynamic-05 · Recorte del documento | [SVG](evidencia/1366x768_1.5_dynamic-05.svg) |
| 1366x768_1.5 · dynamic-06 · Referencia PDF / Word convertido | [SVG](evidencia/1366x768_1.5_dynamic-06.svg) |
| 1366x768_1.5 · dynamic-07 · Borrado y continuación del campo | [SVG](evidencia/1366x768_1.5_dynamic-07.svg) |
| 1366x768_1.5 · dynamic-08 · Reajuste proporcional de campos | [SVG](evidencia/1366x768_1.5_dynamic-08.svg) |
| 1366x768_1.5 · dynamic-09 · Reserva para etiqueta de estado | [SVG](evidencia/1366x768_1.5_dynamic-09.svg) |
| 1366x768_1.5 · dynamic-10 · Formato físico y prueba PDF | [SVG](evidencia/1366x768_1.5_dynamic-10.svg) |
| 1366x768_1.5 · dynamic-11 · Vista previa · PDF de prueba | [SVG](evidencia/1366x768_1.5_dynamic-11.svg) |
| 1366x768_1.5 · dynamic-12 · Nuevo trabajo de emisión | [SVG](evidencia/1366x768_1.5_dynamic-12.svg) |
| 1366x768_1.5 · 17-historial-detalle · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_17-historial-detalle.svg) |
| 1366x768_1.5 · 18-historial-pdf · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_18-historial-pdf.svg) |
| 1366x768_1.5 · dynamic-13 · Reimpresión controlada · #1 | [SVG](evidencia/1366x768_1.5_dynamic-13.svg) |
| 1366x768_1.5 · 19-config-resumen · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_19-config-resumen.svg) |
| 1366x768_1.5 · 20-config-datos · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_20-config-datos.svg) |
| 1366x768_1.5 · 24-aprobacion-revision · Registrar aprobación documental · revisión pendiente | [SVG](evidencia/1366x768_1.5_24-aprobacion-revision.svg) |
| 1366x768_1.5 · 25-comparar · Comparar revisiones · Solo consulta | [SVG](evidencia/1366x768_1.5_25-comparar.svg) |
| 1366x768_1.5 · 26-importar-carpeta · Importar carpeta · Documentos pendientes | [SVG](evidencia/1366x768_1.5_26-importar-carpeta.svg) |
| 1366x768_1.5 · 27-importacion-controlada · R5B · Importación y conciliación documental | [SVG](evidencia/1366x768_1.5_27-importacion-controlada.svg) |
| 1366x768_1.5 · 28-disenador-hoja · Diseñador de hojas · mm | [SVG](evidencia/1366x768_1.5_28-disenador-hoja.svg) |
| 1366x768_1.5 · 29-casillas-utilizadas · Casillas ya utilizadas · primera hoja | [SVG](evidencia/1366x768_1.5_29-casillas-utilizadas.svg) |
| 1366x768_1.5 · 30-calibracion · Calibrar impresora · Prueba no productiva | [SVG](evidencia/1366x768_1.5_30-calibracion.svg) |
| 1366x768_1.5 · 31-preaceptacion · R6A - Diagnóstico de preaceptación | [SVG](evidencia/1366x768_1.5_31-preaceptacion.svg) |
| 1366x768_1.5 · 32-sesion-uat · R6B · Pruebas presenciales y evidencias | [SVG](evidencia/1366x768_1.5_32-sesion-uat.svg) |
| 1366x768_1.5 · 32b-sesion-uat-casos · R6B · Pruebas presenciales y evidencias | [SVG](evidencia/1366x768_1.5_32b-sesion-uat-casos.svg) |
| 1366x768_1.5 · 33-conciliar-master · R5C · Conciliación con libro máster (solo lectura) | [SVG](evidencia/1366x768_1.5_33-conciliar-master.svg) |
| 1366x768_1.5 · 34-config-dock-residual · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_34-config-dock-residual.svg) |
| 1366x768_1.5 · 35-acceso-heredado-residual · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_35-acceso-heredado-residual.svg) |
| 1366x768_1.5 · 36-emision-errores · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1366x768_1.5_36-emision-errores.svg) |
| 1920x1080_1 · 01-biblioteca-pendiente · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_01-biblioteca-pendiente.svg) |
| 1920x1080_1 · 03-biblioteca-documentos · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_03-biblioteca-documentos.svg) |
| 1920x1080_1 · 04-biblioteca-filtros · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_04-biblioteca-filtros.svg) |
| 1920x1080_1 · 07-editor-pendiente · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_07-editor-pendiente.svg) |
| 1920x1080_1 · 08-editor-herramientas · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_08-editor-herramientas.svg) |
| 1920x1080_1 · 10-editor-datos-trabajo · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_10-editor-datos-trabajo.svg) |
| 1920x1080_1 · 11b-editor-variante-borrador · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_11b-editor-variante-borrador.svg) |
| 1920x1080_1 · 12-emision-datos · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_12-emision-datos.svg) |
| 1920x1080_1 · 14-emision-formato · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_14-emision-formato.svg) |
| 1920x1080_1 · 16-emision-preview · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_16-emision-preview.svg) |
| 1920x1080_1 · dynamic-01 · Confirmar emisión definitiva | [SVG](evidencia/1920x1080_1_dynamic-01.svg) |
| 1920x1080_1 · dynamic-02 · Metadatos documentados | [SVG](evidencia/1920x1080_1_dynamic-02.svg) |
| 1920x1080_1 · dynamic-03 · Nueva revisión pendiente | [SVG](evidencia/1920x1080_1_dynamic-03.svg) |
| 1920x1080_1 · dynamic-04 · Pegar datos por recipiente | [SVG](evidencia/1920x1080_1_dynamic-04.svg) |
| 1920x1080_1 · dynamic-05 · Recorte del documento | [SVG](evidencia/1920x1080_1_dynamic-05.svg) |
| 1920x1080_1 · dynamic-06 · Referencia PDF / Word convertido | [SVG](evidencia/1920x1080_1_dynamic-06.svg) |
| 1920x1080_1 · dynamic-07 · Borrado y continuación del campo | [SVG](evidencia/1920x1080_1_dynamic-07.svg) |
| 1920x1080_1 · dynamic-08 · Reajuste proporcional de campos | [SVG](evidencia/1920x1080_1_dynamic-08.svg) |
| 1920x1080_1 · dynamic-09 · Reserva para etiqueta de estado | [SVG](evidencia/1920x1080_1_dynamic-09.svg) |
| 1920x1080_1 · dynamic-10 · Formato físico y prueba PDF | [SVG](evidencia/1920x1080_1_dynamic-10.svg) |
| 1920x1080_1 · dynamic-11 · Vista previa · PDF de prueba | [SVG](evidencia/1920x1080_1_dynamic-11.svg) |
| 1920x1080_1 · dynamic-12 · Nuevo trabajo de emisión | [SVG](evidencia/1920x1080_1_dynamic-12.svg) |
| 1920x1080_1 · 17-historial-detalle · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_17-historial-detalle.svg) |
| 1920x1080_1 · 18-historial-pdf · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_18-historial-pdf.svg) |
| 1920x1080_1 · dynamic-13 · Reimpresión controlada · #1 | [SVG](evidencia/1920x1080_1_dynamic-13.svg) |
| 1920x1080_1 · 19-config-resumen · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_19-config-resumen.svg) |
| 1920x1080_1 · 20-config-datos · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_20-config-datos.svg) |
| 1920x1080_1 · 24-aprobacion-revision · Registrar aprobación documental · revisión pendiente | [SVG](evidencia/1920x1080_1_24-aprobacion-revision.svg) |
| 1920x1080_1 · 25-comparar · Comparar revisiones · Solo consulta | [SVG](evidencia/1920x1080_1_25-comparar.svg) |
| 1920x1080_1 · 26-importar-carpeta · Importar carpeta · Documentos pendientes | [SVG](evidencia/1920x1080_1_26-importar-carpeta.svg) |
| 1920x1080_1 · 27-importacion-controlada · R5B · Importación y conciliación documental | [SVG](evidencia/1920x1080_1_27-importacion-controlada.svg) |
| 1920x1080_1 · 28-disenador-hoja · Diseñador de hojas · mm | [SVG](evidencia/1920x1080_1_28-disenador-hoja.svg) |
| 1920x1080_1 · 29-casillas-utilizadas · Casillas ya utilizadas · primera hoja | [SVG](evidencia/1920x1080_1_29-casillas-utilizadas.svg) |
| 1920x1080_1 · 30-calibracion · Calibrar impresora · Prueba no productiva | [SVG](evidencia/1920x1080_1_30-calibracion.svg) |
| 1920x1080_1 · 31-preaceptacion · R6A - Diagnóstico de preaceptación | [SVG](evidencia/1920x1080_1_31-preaceptacion.svg) |
| 1920x1080_1 · 32-sesion-uat · R6B · Pruebas presenciales y evidencias | [SVG](evidencia/1920x1080_1_32-sesion-uat.svg) |
| 1920x1080_1 · 32b-sesion-uat-casos · R6B · Pruebas presenciales y evidencias | [SVG](evidencia/1920x1080_1_32b-sesion-uat-casos.svg) |
| 1920x1080_1 · 33-conciliar-master · R5C · Conciliación con libro máster (solo lectura) | [SVG](evidencia/1920x1080_1_33-conciliar-master.svg) |
| 1920x1080_1 · 34-config-dock-residual · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_34-config-dock-residual.svg) |
| 1920x1080_1 · 35-acceso-heredado-residual · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_35-acceso-heredado-residual.svg) |
| 1920x1080_1 · 36-emision-errores · COVEX Label Manager · Centro de emisión | [SVG](evidencia/1920x1080_1_36-emision-errores.svg) |

## Revisión humana de las capturas

Se revisaron Biblioteca pendiente y filtros; Editor normal, avanzado, solo lectura y con dock; Emisión datos/formato/preview; Historial PDF; Configuración; aprobación documental; UAT y conciliación, con especial atención al caso 1366×768/150 % y comparación con 1920×1080/100 %. Las demás imágenes están capturadas y disponibles para revisión: no se afirma revisión humana individual de cada una. Los errores del harness inicial se corrigieron antes de la serie final y no se contabilizan como defectos de producto.
