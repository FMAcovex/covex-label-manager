# Comparativa visual antes / después

Baseline obligatoria: auditoría `02f7ba7`, aplicación `afd0b06`; el main de partida `6b4f507` solo añade su documentación y conserva la misma aplicación. Se utilizan sus seis series sintéticas; no se altera la rama ni la evidencia histórica. La nueva serie contiene 52 estados por combinación (312 PNG) y 126 SVG seleccionados de widgets reales.

Entorno: Qt 6.8.3, Fusion, Linux/Xorg dummy 1920×1080. Tamaño objetivo emulado por ventana y `QT_SCALE_FACTOR`; área cliente = floor(píxeles/factor) menos 40 DIP de alto. No es una prueba física de seis monitores ni aceptación Windows. La CI Qt repite la serie en Windows Server 2022 y conserva los PNG/manifiestos.

| Tamaño / factor | Lienzo antes (alto DIP) | Lienzo después | Dock en Configuración antes → después | Ventanas fuera del área / pies inaccesibles después |
|---|---:|---:|---|---|
| 1366x768_1 | 260 | 528 | True → False | 0 / 0 |
| 1366x768_1.25 | 206 | 384 | True → False | 0 / 0 |
| 1366x768_1.5 | 104 | 282 | True → False | 0 / 0 |
| 1920x1080_1 | 572 | 840 | True → False | 0 / 0 |
| 1920x1080_1.25 | 356 | 624 | True → False | 0 / 0 |
| 1920x1080_1.5 | 212 | 480 | True → False | 0 / 0 |

El lienzo normal supera el 45 % del área cliente en las seis comprobaciones; «Ampliar lienzo» recupera los laterales mediante el mismo botón. La vista PDF compacta conserva zoom, abrir, ampliar y marca/advertencia. La comparación es geométrica y visual revisada, no un certificado de diferencia de píxeles ni de escala física.

## Pares representativos

| Configuración / estado | Antes | Después |
|---|---|---|
| 1366x768_1 / 01-biblioteca-pendiente | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1_01-biblioteca-pendiente.svg) | [SVG](evidencia/1366x768_1_01-biblioteca-pendiente.svg) |
| 1366x768_1 / 07-editor-pendiente | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1_07-editor-pendiente.svg) | [SVG](evidencia/1366x768_1_07-editor-pendiente.svg) |
| 1366x768_1 / 08-editor-herramientas | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1_08-editor-herramientas.svg) | [SVG](evidencia/1366x768_1_08-editor-herramientas.svg) |
| 1366x768_1 / 10-editor-datos-trabajo | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1_10-editor-datos-trabajo.svg) | [SVG](evidencia/1366x768_1_10-editor-datos-trabajo.svg) |
| 1366x768_1 / 14-emision-formato | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1_14-emision-formato.svg) | [SVG](evidencia/1366x768_1_14-emision-formato.svg) |
| 1366x768_1 / 16-emision-preview | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1_16-emision-preview.svg) | [SVG](evidencia/1366x768_1_16-emision-preview.svg) |
| 1366x768_1 / 18-historial-pdf | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1_18-historial-pdf.svg) | [SVG](evidencia/1366x768_1_18-historial-pdf.svg) |
| 1366x768_1 / 20-config-datos | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1_20-config-datos.svg) | [SVG](evidencia/1366x768_1_20-config-datos.svg) |
| 1366x768_1 / 24-aprobacion-revision | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1_24-aprobacion-revision.svg) | [SVG](evidencia/1366x768_1_24-aprobacion-revision.svg) |
| 1366x768_1 / 32b-sesion-uat-casos | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1_32b-sesion-uat-casos.svg) | [SVG](evidencia/1366x768_1_32b-sesion-uat-casos.svg) |
| 1366x768_1 / 33-conciliar-master | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1_33-conciliar-master.svg) | [SVG](evidencia/1366x768_1_33-conciliar-master.svg) |
| 1366x768_1.5 / 01-biblioteca-pendiente | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1.5_01-biblioteca-pendiente.svg) | [SVG](evidencia/1366x768_1.5_01-biblioteca-pendiente.svg) |
| 1366x768_1.5 / 07-editor-pendiente | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1.5_07-editor-pendiente.svg) | [SVG](evidencia/1366x768_1.5_07-editor-pendiente.svg) |
| 1366x768_1.5 / 08-editor-herramientas | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1.5_08-editor-herramientas.svg) | [SVG](evidencia/1366x768_1.5_08-editor-herramientas.svg) |
| 1366x768_1.5 / 10-editor-datos-trabajo | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1.5_10-editor-datos-trabajo.svg) | [SVG](evidencia/1366x768_1.5_10-editor-datos-trabajo.svg) |
| 1366x768_1.5 / 14-emision-formato | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1.5_14-emision-formato.svg) | [SVG](evidencia/1366x768_1.5_14-emision-formato.svg) |
| 1366x768_1.5 / 16-emision-preview | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1.5_16-emision-preview.svg) | [SVG](evidencia/1366x768_1.5_16-emision-preview.svg) |
| 1366x768_1.5 / 18-historial-pdf | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1.5_18-historial-pdf.svg) | [SVG](evidencia/1366x768_1.5_18-historial-pdf.svg) |
| 1366x768_1.5 / 20-config-datos | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1.5_20-config-datos.svg) | [SVG](evidencia/1366x768_1.5_20-config-datos.svg) |
| 1366x768_1.5 / 24-aprobacion-revision | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1.5_24-aprobacion-revision.svg) | [SVG](evidencia/1366x768_1.5_24-aprobacion-revision.svg) |
| 1366x768_1.5 / 32b-sesion-uat-casos | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1.5_32b-sesion-uat-casos.svg) | [SVG](evidencia/1366x768_1.5_32b-sesion-uat-casos.svg) |
| 1366x768_1.5 / 33-conciliar-master | [SVG](../UX_AUDIT_R6B/evidencia/1366x768_1.5_33-conciliar-master.svg) | [SVG](evidencia/1366x768_1.5_33-conciliar-master.svg) |
| 1920x1080_1 / 01-biblioteca-pendiente | [SVG](../UX_AUDIT_R6B/evidencia/1920x1080_1_01-biblioteca-pendiente.svg) | [SVG](evidencia/1920x1080_1_01-biblioteca-pendiente.svg) |
| 1920x1080_1 / 07-editor-pendiente | [SVG](../UX_AUDIT_R6B/evidencia/1920x1080_1_07-editor-pendiente.svg) | [SVG](evidencia/1920x1080_1_07-editor-pendiente.svg) |
| 1920x1080_1 / 08-editor-herramientas | [SVG](../UX_AUDIT_R6B/evidencia/1920x1080_1_08-editor-herramientas.svg) | [SVG](evidencia/1920x1080_1_08-editor-herramientas.svg) |
| 1920x1080_1 / 10-editor-datos-trabajo | [SVG](../UX_AUDIT_R6B/evidencia/1920x1080_1_10-editor-datos-trabajo.svg) | [SVG](evidencia/1920x1080_1_10-editor-datos-trabajo.svg) |
| 1920x1080_1 / 14-emision-formato | [SVG](../UX_AUDIT_R6B/evidencia/1920x1080_1_14-emision-formato.svg) | [SVG](evidencia/1920x1080_1_14-emision-formato.svg) |
| 1920x1080_1 / 16-emision-preview | [SVG](../UX_AUDIT_R6B/evidencia/1920x1080_1_16-emision-preview.svg) | [SVG](evidencia/1920x1080_1_16-emision-preview.svg) |
| 1920x1080_1 / 18-historial-pdf | [SVG](../UX_AUDIT_R6B/evidencia/1920x1080_1_18-historial-pdf.svg) | [SVG](evidencia/1920x1080_1_18-historial-pdf.svg) |
| 1920x1080_1 / 20-config-datos | [SVG](../UX_AUDIT_R6B/evidencia/1920x1080_1_20-config-datos.svg) | [SVG](evidencia/1920x1080_1_20-config-datos.svg) |
| 1920x1080_1 / 24-aprobacion-revision | [SVG](../UX_AUDIT_R6B/evidencia/1920x1080_1_24-aprobacion-revision.svg) | [SVG](evidencia/1920x1080_1_24-aprobacion-revision.svg) |
| 1920x1080_1 / 32b-sesion-uat-casos | [SVG](../UX_AUDIT_R6B/evidencia/1920x1080_1_32b-sesion-uat-casos.svg) | [SVG](evidencia/1920x1080_1_32b-sesion-uat-casos.svg) |
| 1920x1080_1 / 33-conciliar-master | [SVG](../UX_AUDIT_R6B/evidencia/1920x1080_1_33-conciliar-master.svg) | [SVG](evidencia/1920x1080_1_33-conciliar-master.svg) |

## Galería completa seleccionada

| Configuración / estado | Después |
|---|---|
| 1366x768_1 / 01-biblioteca-pendiente / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_01-biblioteca-pendiente.svg) |
| 1366x768_1 / 03-biblioteca-documentos / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_03-biblioteca-documentos.svg) |
| 1366x768_1 / 04-biblioteca-filtros / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_04-biblioteca-filtros.svg) |
| 1366x768_1 / 07-editor-pendiente / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_07-editor-pendiente.svg) |
| 1366x768_1 / 08-editor-herramientas / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_08-editor-herramientas.svg) |
| 1366x768_1 / 10-editor-datos-trabajo / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_10-editor-datos-trabajo.svg) |
| 1366x768_1 / 11b-editor-variante-borrador / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_11b-editor-variante-borrador.svg) |
| 1366x768_1 / 12-emision-datos / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_12-emision-datos.svg) |
| 1366x768_1 / 14-emision-formato / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_14-emision-formato.svg) |
| 1366x768_1 / 16-emision-preview / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_16-emision-preview.svg) |
| 1366x768_1 / dynamic-01 / Confirmar emisión definitiva | [SVG](evidencia/1366x768_1_dynamic-01.svg) |
| 1366x768_1 / dynamic-02 / Metadatos documentados | [SVG](evidencia/1366x768_1_dynamic-02.svg) |
| 1366x768_1 / dynamic-03 / Nueva revisión pendiente | [SVG](evidencia/1366x768_1_dynamic-03.svg) |
| 1366x768_1 / dynamic-04 / Pegar datos por recipiente | [SVG](evidencia/1366x768_1_dynamic-04.svg) |
| 1366x768_1 / dynamic-05 / Recorte del documento | [SVG](evidencia/1366x768_1_dynamic-05.svg) |
| 1366x768_1 / dynamic-06 / Referencia PDF / Word convertido | [SVG](evidencia/1366x768_1_dynamic-06.svg) |
| 1366x768_1 / dynamic-07 / Borrado y continuación del campo | [SVG](evidencia/1366x768_1_dynamic-07.svg) |
| 1366x768_1 / dynamic-08 / Reajuste proporcional de campos | [SVG](evidencia/1366x768_1_dynamic-08.svg) |
| 1366x768_1 / dynamic-09 / Reserva para etiqueta de estado | [SVG](evidencia/1366x768_1_dynamic-09.svg) |
| 1366x768_1 / dynamic-10 / Formato físico y prueba PDF | [SVG](evidencia/1366x768_1_dynamic-10.svg) |
| 1366x768_1 / dynamic-11 / Vista previa · PDF de prueba | [SVG](evidencia/1366x768_1_dynamic-11.svg) |
| 1366x768_1 / dynamic-12 / Nuevo trabajo de emisión | [SVG](evidencia/1366x768_1_dynamic-12.svg) |
| 1366x768_1 / 17-historial-detalle / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_17-historial-detalle.svg) |
| 1366x768_1 / 18-historial-pdf / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_18-historial-pdf.svg) |
| 1366x768_1 / dynamic-13 / Reimpresión controlada · #1 | [SVG](evidencia/1366x768_1_dynamic-13.svg) |
| 1366x768_1 / 19-config-resumen / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_19-config-resumen.svg) |
| 1366x768_1 / 20-config-datos / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_20-config-datos.svg) |
| 1366x768_1 / 24-aprobacion-revision / Registrar aprobación documental · revisión pendiente | [SVG](evidencia/1366x768_1_24-aprobacion-revision.svg) |
| 1366x768_1 / 25-comparar / Comparar revisiones · Solo consulta | [SVG](evidencia/1366x768_1_25-comparar.svg) |
| 1366x768_1 / 26-importar-carpeta / Importar carpeta · Documentos pendientes | [SVG](evidencia/1366x768_1_26-importar-carpeta.svg) |
| 1366x768_1 / 27-importacion-controlada / R5B · Importación y conciliación documental | [SVG](evidencia/1366x768_1_27-importacion-controlada.svg) |
| 1366x768_1 / 28-disenador-hoja / Diseñador de hojas · mm | [SVG](evidencia/1366x768_1_28-disenador-hoja.svg) |
| 1366x768_1 / 29-casillas-utilizadas / Casillas ya utilizadas · primera hoja | [SVG](evidencia/1366x768_1_29-casillas-utilizadas.svg) |
| 1366x768_1 / 30-calibracion / Calibrar impresora · Prueba no productiva | [SVG](evidencia/1366x768_1_30-calibracion.svg) |
| 1366x768_1 / 31-preaceptacion / R6A - Diagnóstico de preaceptación | [SVG](evidencia/1366x768_1_31-preaceptacion.svg) |
| 1366x768_1 / 32-sesion-uat / R6B · Pruebas presenciales y evidencias | [SVG](evidencia/1366x768_1_32-sesion-uat.svg) |
| 1366x768_1 / 32b-sesion-uat-casos / R6B · Pruebas presenciales y evidencias | [SVG](evidencia/1366x768_1_32b-sesion-uat-casos.svg) |
| 1366x768_1 / 33-conciliar-master / R5C · Conciliación con libro máster (solo lectura) | [SVG](evidencia/1366x768_1_33-conciliar-master.svg) |
| 1366x768_1 / 34-config-sin-dock / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_34-config-sin-dock.svg) |
| 1366x768_1 / dynamic-14 / Revisiones documentales y variantes de diseño | [SVG](evidencia/1366x768_1_dynamic-14.svg) |
| 1366x768_1 / 35-seleccion-nativa / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_35-seleccion-nativa.svg) |
| 1366x768_1 / 36-emision-errores / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1_36-emision-errores.svg) |
| 1366x768_1.5 / 01-biblioteca-pendiente / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_01-biblioteca-pendiente.svg) |
| 1366x768_1.5 / 03-biblioteca-documentos / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_03-biblioteca-documentos.svg) |
| 1366x768_1.5 / 04-biblioteca-filtros / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_04-biblioteca-filtros.svg) |
| 1366x768_1.5 / 07-editor-pendiente / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_07-editor-pendiente.svg) |
| 1366x768_1.5 / 08-editor-herramientas / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_08-editor-herramientas.svg) |
| 1366x768_1.5 / 10-editor-datos-trabajo / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_10-editor-datos-trabajo.svg) |
| 1366x768_1.5 / 11b-editor-variante-borrador / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_11b-editor-variante-borrador.svg) |
| 1366x768_1.5 / 12-emision-datos / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_12-emision-datos.svg) |
| 1366x768_1.5 / 14-emision-formato / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_14-emision-formato.svg) |
| 1366x768_1.5 / 16-emision-preview / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_16-emision-preview.svg) |
| 1366x768_1.5 / dynamic-01 / Confirmar emisión definitiva | [SVG](evidencia/1366x768_1.5_dynamic-01.svg) |
| 1366x768_1.5 / dynamic-02 / Metadatos documentados | [SVG](evidencia/1366x768_1.5_dynamic-02.svg) |
| 1366x768_1.5 / dynamic-03 / Nueva revisión pendiente | [SVG](evidencia/1366x768_1.5_dynamic-03.svg) |
| 1366x768_1.5 / dynamic-04 / Pegar datos por recipiente | [SVG](evidencia/1366x768_1.5_dynamic-04.svg) |
| 1366x768_1.5 / dynamic-05 / Recorte del documento | [SVG](evidencia/1366x768_1.5_dynamic-05.svg) |
| 1366x768_1.5 / dynamic-06 / Referencia PDF / Word convertido | [SVG](evidencia/1366x768_1.5_dynamic-06.svg) |
| 1366x768_1.5 / dynamic-07 / Borrado y continuación del campo | [SVG](evidencia/1366x768_1.5_dynamic-07.svg) |
| 1366x768_1.5 / dynamic-08 / Reajuste proporcional de campos | [SVG](evidencia/1366x768_1.5_dynamic-08.svg) |
| 1366x768_1.5 / dynamic-09 / Reserva para etiqueta de estado | [SVG](evidencia/1366x768_1.5_dynamic-09.svg) |
| 1366x768_1.5 / dynamic-10 / Formato físico y prueba PDF | [SVG](evidencia/1366x768_1.5_dynamic-10.svg) |
| 1366x768_1.5 / dynamic-11 / Vista previa · PDF de prueba | [SVG](evidencia/1366x768_1.5_dynamic-11.svg) |
| 1366x768_1.5 / dynamic-12 / Nuevo trabajo de emisión | [SVG](evidencia/1366x768_1.5_dynamic-12.svg) |
| 1366x768_1.5 / 17-historial-detalle / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_17-historial-detalle.svg) |
| 1366x768_1.5 / 18-historial-pdf / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_18-historial-pdf.svg) |
| 1366x768_1.5 / dynamic-13 / Reimpresión controlada · #1 | [SVG](evidencia/1366x768_1.5_dynamic-13.svg) |
| 1366x768_1.5 / 19-config-resumen / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_19-config-resumen.svg) |
| 1366x768_1.5 / 20-config-datos / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_20-config-datos.svg) |
| 1366x768_1.5 / 24-aprobacion-revision / Registrar aprobación documental · revisión pendiente | [SVG](evidencia/1366x768_1.5_24-aprobacion-revision.svg) |
| 1366x768_1.5 / 25-comparar / Comparar revisiones · Solo consulta | [SVG](evidencia/1366x768_1.5_25-comparar.svg) |
| 1366x768_1.5 / 26-importar-carpeta / Importar carpeta · Documentos pendientes | [SVG](evidencia/1366x768_1.5_26-importar-carpeta.svg) |
| 1366x768_1.5 / 27-importacion-controlada / R5B · Importación y conciliación documental | [SVG](evidencia/1366x768_1.5_27-importacion-controlada.svg) |
| 1366x768_1.5 / 28-disenador-hoja / Diseñador de hojas · mm | [SVG](evidencia/1366x768_1.5_28-disenador-hoja.svg) |
| 1366x768_1.5 / 29-casillas-utilizadas / Casillas ya utilizadas · primera hoja | [SVG](evidencia/1366x768_1.5_29-casillas-utilizadas.svg) |
| 1366x768_1.5 / 30-calibracion / Calibrar impresora · Prueba no productiva | [SVG](evidencia/1366x768_1.5_30-calibracion.svg) |
| 1366x768_1.5 / 31-preaceptacion / R6A - Diagnóstico de preaceptación | [SVG](evidencia/1366x768_1.5_31-preaceptacion.svg) |
| 1366x768_1.5 / 32-sesion-uat / R6B · Pruebas presenciales y evidencias | [SVG](evidencia/1366x768_1.5_32-sesion-uat.svg) |
| 1366x768_1.5 / 32b-sesion-uat-casos / R6B · Pruebas presenciales y evidencias | [SVG](evidencia/1366x768_1.5_32b-sesion-uat-casos.svg) |
| 1366x768_1.5 / 33-conciliar-master / R5C · Conciliación con libro máster (solo lectura) | [SVG](evidencia/1366x768_1.5_33-conciliar-master.svg) |
| 1366x768_1.5 / 34-config-sin-dock / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_34-config-sin-dock.svg) |
| 1366x768_1.5 / dynamic-14 / Revisiones documentales y variantes de diseño | [SVG](evidencia/1366x768_1.5_dynamic-14.svg) |
| 1366x768_1.5 / 35-seleccion-nativa / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_35-seleccion-nativa.svg) |
| 1366x768_1.5 / 36-emision-errores / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1366x768_1.5_36-emision-errores.svg) |
| 1920x1080_1 / 01-biblioteca-pendiente / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_01-biblioteca-pendiente.svg) |
| 1920x1080_1 / 03-biblioteca-documentos / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_03-biblioteca-documentos.svg) |
| 1920x1080_1 / 04-biblioteca-filtros / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_04-biblioteca-filtros.svg) |
| 1920x1080_1 / 07-editor-pendiente / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_07-editor-pendiente.svg) |
| 1920x1080_1 / 08-editor-herramientas / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_08-editor-herramientas.svg) |
| 1920x1080_1 / 10-editor-datos-trabajo / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_10-editor-datos-trabajo.svg) |
| 1920x1080_1 / 11b-editor-variante-borrador / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_11b-editor-variante-borrador.svg) |
| 1920x1080_1 / 12-emision-datos / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_12-emision-datos.svg) |
| 1920x1080_1 / 14-emision-formato / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_14-emision-formato.svg) |
| 1920x1080_1 / 16-emision-preview / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_16-emision-preview.svg) |
| 1920x1080_1 / dynamic-01 / Confirmar emisión definitiva | [SVG](evidencia/1920x1080_1_dynamic-01.svg) |
| 1920x1080_1 / dynamic-02 / Metadatos documentados | [SVG](evidencia/1920x1080_1_dynamic-02.svg) |
| 1920x1080_1 / dynamic-03 / Nueva revisión pendiente | [SVG](evidencia/1920x1080_1_dynamic-03.svg) |
| 1920x1080_1 / dynamic-04 / Pegar datos por recipiente | [SVG](evidencia/1920x1080_1_dynamic-04.svg) |
| 1920x1080_1 / dynamic-05 / Recorte del documento | [SVG](evidencia/1920x1080_1_dynamic-05.svg) |
| 1920x1080_1 / dynamic-06 / Referencia PDF / Word convertido | [SVG](evidencia/1920x1080_1_dynamic-06.svg) |
| 1920x1080_1 / dynamic-07 / Borrado y continuación del campo | [SVG](evidencia/1920x1080_1_dynamic-07.svg) |
| 1920x1080_1 / dynamic-08 / Reajuste proporcional de campos | [SVG](evidencia/1920x1080_1_dynamic-08.svg) |
| 1920x1080_1 / dynamic-09 / Reserva para etiqueta de estado | [SVG](evidencia/1920x1080_1_dynamic-09.svg) |
| 1920x1080_1 / dynamic-10 / Formato físico y prueba PDF | [SVG](evidencia/1920x1080_1_dynamic-10.svg) |
| 1920x1080_1 / dynamic-11 / Vista previa · PDF de prueba | [SVG](evidencia/1920x1080_1_dynamic-11.svg) |
| 1920x1080_1 / dynamic-12 / Nuevo trabajo de emisión | [SVG](evidencia/1920x1080_1_dynamic-12.svg) |
| 1920x1080_1 / 17-historial-detalle / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_17-historial-detalle.svg) |
| 1920x1080_1 / 18-historial-pdf / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_18-historial-pdf.svg) |
| 1920x1080_1 / dynamic-13 / Reimpresión controlada · #1 | [SVG](evidencia/1920x1080_1_dynamic-13.svg) |
| 1920x1080_1 / 19-config-resumen / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_19-config-resumen.svg) |
| 1920x1080_1 / 20-config-datos / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_20-config-datos.svg) |
| 1920x1080_1 / 24-aprobacion-revision / Registrar aprobación documental · revisión pendiente | [SVG](evidencia/1920x1080_1_24-aprobacion-revision.svg) |
| 1920x1080_1 / 25-comparar / Comparar revisiones · Solo consulta | [SVG](evidencia/1920x1080_1_25-comparar.svg) |
| 1920x1080_1 / 26-importar-carpeta / Importar carpeta · Documentos pendientes | [SVG](evidencia/1920x1080_1_26-importar-carpeta.svg) |
| 1920x1080_1 / 27-importacion-controlada / R5B · Importación y conciliación documental | [SVG](evidencia/1920x1080_1_27-importacion-controlada.svg) |
| 1920x1080_1 / 28-disenador-hoja / Diseñador de hojas · mm | [SVG](evidencia/1920x1080_1_28-disenador-hoja.svg) |
| 1920x1080_1 / 29-casillas-utilizadas / Casillas ya utilizadas · primera hoja | [SVG](evidencia/1920x1080_1_29-casillas-utilizadas.svg) |
| 1920x1080_1 / 30-calibracion / Calibrar impresora · Prueba no productiva | [SVG](evidencia/1920x1080_1_30-calibracion.svg) |
| 1920x1080_1 / 31-preaceptacion / R6A - Diagnóstico de preaceptación | [SVG](evidencia/1920x1080_1_31-preaceptacion.svg) |
| 1920x1080_1 / 32-sesion-uat / R6B · Pruebas presenciales y evidencias | [SVG](evidencia/1920x1080_1_32-sesion-uat.svg) |
| 1920x1080_1 / 32b-sesion-uat-casos / R6B · Pruebas presenciales y evidencias | [SVG](evidencia/1920x1080_1_32b-sesion-uat-casos.svg) |
| 1920x1080_1 / 33-conciliar-master / R5C · Conciliación con libro máster (solo lectura) | [SVG](evidencia/1920x1080_1_33-conciliar-master.svg) |
| 1920x1080_1 / 34-config-sin-dock / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_34-config-sin-dock.svg) |
| 1920x1080_1 / dynamic-14 / Revisiones documentales y variantes de diseño | [SVG](evidencia/1920x1080_1_dynamic-14.svg) |
| 1920x1080_1 / 35-seleccion-nativa / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_35-seleccion-nativa.svg) |
| 1920x1080_1 / 36-emision-errores / COVEX Label Manager · Datos ficticios | [SVG](evidencia/1920x1080_1_36-emision-errores.svg) |

Los PNG completos y controles expandidos están en `test-results/ux-integrated/<configuración>/manifest.json`, con SHA-256 de cada imagen; el resumen versionado registra los tamaños, DPR, hash del código Qt, pies y archivos. Las capturas de Auditoría local/UAT contienen únicamente referencias temporales ficticias. Ninguna aprobación documental se acepta en el recorrido. Un registro de emisión generado en demo permite consultar Historial; no se envía a una impresora.

Revisión humana: Biblioteca e Inspector abierto, Editor normal/avanzado/trabajo/solo lectura, Emisión/formato/prueba, Historial, Configuración, aprobación, UAT y conciliación; extremos 1366/150 y 1920/100. El gate comprueba todas las geometrías y pies registrados, pero no se afirma inspección humana independiente de cada PNG ni verificación de cada selector del SO.
