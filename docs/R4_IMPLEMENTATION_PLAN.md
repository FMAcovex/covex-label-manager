# R4 — Profesionalización de impresión. Plan y R4A

**Estado:** R4A implementada en rama de desarrollo, sin integración ni pruebas físicas.
**Base:** `main` `e87d3a61177b7b0bc7ece97dca164fcec118719c` (R3F integrada).
**Rama:** `feature/r4a-professional-partial-sheets`.

## R4A — Aprovechar hojas parcialmente utilizadas
- Reutilizar el diseñador nativo de R3E y el motor PDF para marcar mediante una lista gráfica las casillas ocupadas **solo en la primera hoja**.
- Contrato opcional `occupied_slots: [1,3,...]` (índices de casilla 1..capacidad), asociado a `layout_version=1`. Ningún perfil histórico debe recibirlo automáticamente.
- Casilla inicial y marcas de ocupación son conceptos diferentes: la primera omite las anteriores, la ocupación omite cualquier otra casilla indicada. En las hojas siguientes se permiten todas las posiciones.
- Denegar índices fuera de la hoja, duplicados, booleanos, formatos desconocidos y primera hoja sin posiciones disponibles. Vaciar la ocupación si el operador redistribuye automáticamente las casillas.
- El documento PDF deja completamente en blanco las posiciones físicas marcadas como usadas. **El operador debe verificar orientación/carga real de la hoja, impresión sin ajuste de escala, adhesivo y compatibilidad con la impresora.**
- El nuevo campo queda en el perfil del trabajo y su snapshot de emisión. No altera los documentos maestro, números de recipientes, aprobaciones o datos históricos.
- Calibración existente (regla de 50 mm / desplazamientos X/Y) sigue siendo **no productiva** y se debe probar sobre papel sin etiquetas previas; no declarar calibrada una impresora solo por guardar un perfil.
- SQLite v4 sin cambios. Al cargar perfiles nuevos en lectores Tk anteriores se debe bloquear, nunca reinterpretar como A4 normal.

## R4B — Perfiles y calibración por impresora
- Asistente de medición: diseñar PDF no productivo con regla, registrar valores reales medidos y corregir X/Y sin modificar geometría documental ni confundir zoom con milímetros.
- Asociar perfil a nombre/modelo de impresora, tamaño y orientación; selección explícita y revisión de cambios sin autodetectar calidad física.
- Diferenciar impresora informativa (`printer_name`) de cola/dispositivo físico accesible. No enviar silenciosamente contenido a la impresora.

## R4C — Flujo profesional de impresión
- Comprobaciones de selección de impresora/papel, apertura al 100 %, márgenes y hoja parcialmente usada.
- Valorar impresión directa Windows con consentimiento de usuario y manejo de errores. No registrar «impreso físicamente» sin evidencia apropiada.
- Pruebas físicas de hojas, distintas impresoras y Windows 10/11 en COVEX; requisitos/URS y validación GMP aparte.

## Migración de catálogo / exportación masiva — tarea distinta, pendiente
- R3F incluye **importación manual por carpeta local** de PDF/Word con creación de registros PENDING; no migra por sí sola el libro maestro de SharePoint.
- R3F **no incluye una exportación masiva desde la biblioteca de la app**.
- Para importar el libro maestro real: primero inventario solo lectura SharePoint, asociación fichero–producto–revisión/cliente, detección de duplicados y archivos no convertibles, selección/ensayo sintético, importación explícitamente autorizada, conciliación y revisión documental. No marcar revisiones APPROVED automáticamente.
- Para exportar la biblioteca desde la app: especificar alcance (originales Word, PDF maestro, últimas revisiones o todas, variantes y manifiesto con SHA-256), formato ZIP y destino, permisos de salida y pruebas de integridad. No confundir con el ZIP de backup interno.
- Mantener fuera de PR R4A para no mezclar migración de datos reales con posicionamiento físico.

## Aceptación
- Tests geométricos: 1–5 etiquetas, ocupación no contigua, primera hoja vs siguientes, copias 1/2, orientación, formatos A4/A3/libres, borde y fallo de seguridad.
- Tests Qt del selector, deshacer/rehacer, persistencia de perfil y rechazo sin emisión.
- Tests de PDF y snapshots históricos, aviso de reimpresión. Mantener 87 capacidades y CI Windows núcleo, Qt y migración.
- No squash/merge/despliegue; `00-R1` PENDING; Word real, impresión física, hardware Windows de COVEX y validación GMP pendientes.
