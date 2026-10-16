# R4C — Envío controlado de PDF registrado a impresora (Qt)

**Rama:** feature/r4c-controlled-qt-printing. **Base:** main con R4A/R4B integradas.

## Flujo
1. Emisión definitiva registra PDF, snapshot documental e integridad SHA-256.
2. «Imprimir PDF registrado…» desde Emisión o Historial **NO** imprime borradores ni pruebas como documentos definitivos.
3. La verificación comprueba vigencia documental/reimpresión permitida, snapshot, hash, páginas PDF y tamaño físico registrado. Adquiere una copia en memoria para evitar sustituciones durante el envío.
4. Se advierte explícitamente del uso de la primera hoja parcialmente utilizada (R4A) y de la necesidad de hojas nuevas posteriores.
5. Se abre **QPrintDialog** para elegir impresora/cola y revisar papel. Cancelar no registra intento ni envía datos. La cola debe corresponder a la identidad de calibración R4B (si existe).
6. Se rechazan impresión a archivo, elección de formato diferente, rangos parciales, cambio documental antes de enviar, y PDF o datos inconsistentes.
7. Qt QPrinter/QPainter junto con PyMuPDF convierte páginas a resolución del dispositivo y las posiciona en su **tamaño físico** (sin ajuste a márgenes/zoom de pantalla). Fallos de controlador, nuevas páginas o memoria se notifican y registran como incidencias.
8. Eventos de auditoría local SQLite: PRINT_REQUEST, PRINT_DRIVER_HANDOFF y PRINT_DISPATCH_ERROR. **Entregado al controlador no significa impresión física realizada.** No modifica registros de emisión, reimpresiones, revisiones ni SQLite v4.

## Limitaciones y aceptación
- No se confirma físicamente salida, adhesivo, alineación o carga correcta de hojas.
- La impresión directa depende de la cola real de Windows; un controlador virtual o remoto puede aceptar el trabajo sin papel impreso.
- Pruebas CI y empaquetado usan PDFs ficticios y un controlador simulado. Jamás envían documentos a impresoras reales.
- Para aprobación física: Windows 10/11 COVEX, impresoras y drivers reales, resolución correcta, A4/A3/A5/Carta, impresión al 100 %, tarjetas de calibración, inicio/omisión de casillas, impresión parcial y recuperación de errores de cola.
- El contenido se rasteriza con PyMuPDF a 300 dpi (o la resolución de QPrinter); comprobar nitidez de códigos de barras y tamaños de texto como criterio de aceptación. No se acredita reproducción vectorial exacta ni conformidad GMP.
- R4C no implica migración del libro máster SharePoint ni exportación de toda la biblioteca. Mantener ambas tareas separadas para el siguiente bloque.
- No merge hasta CI y revisión. 00-R1 continúa PENDING.
