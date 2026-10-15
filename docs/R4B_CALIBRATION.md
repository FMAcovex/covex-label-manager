# R4B — Perfiles y corrección física por impresora

Base `574e869a668118449ca0a8416d74a29566cc0e15` (R4A integrada). Rama `feature/r4b-printer-calibration`.

## Entrega
- Asistente Qt que genera hoja de calibración PDF NO PRODUCTIVA y recibe impresora/modelo, coordenadas esperadas y coordenadas medidas en mm desde borde superior izquierdo de la casilla 1.
- Regla: offset X/Y nuevo = offset X/Y previo + (coordenada esperada − coordenada medida). Correcciones individuales mayores de 10 mm requieren revisar escala, papel y orientación antes de avanzar.
- Se conserva diseño y tamaño de etiqueta, con registro de mediciones y firma geométrica dentro de `printer_calibration` en el perfil del trabajo. Cambiar impresora, papel, orientación, desplazamiento o geometría después de calibrar bloquea el plan de emisión para evitar aplicar ajustes a otro equipo.
- Backward compatibility: perfiles antiguos sin campo de calibración mantienen el mismo algoritmo. SQLite v4, masters y emisiones antiguas intactas; sólo se persiste por guardado explícito del trabajo.
- La identificación de la impresora es **declarativa**: no se busca cola de Windows ni se envía impresión física. El usuario debe abrir PDF, imprimir al 100 %, comprobar la regla de referencia 50 mm y medir. La aceptación física/GMP sigue pendiente.

## R4C pendiente
Envío controlado a impresora y confirmación física verificable; diseño con selección de dispositivo, validación de escala, fallos de spooler y sin afirmar impresión cuando sólo se genera PDF.
