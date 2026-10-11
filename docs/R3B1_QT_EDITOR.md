# R3B1 — Editor avanzado Qt en revisión

Base: main `5d27de30ce98ee89f17485225e3a45b92f544484` (R3A integrada). Rama: `feature/r3b1-qt-advanced-editor`. Propuesta R3B aprobada por el usuario el 11/10/2026; esta PR desarrolla exclusivamente R3B1. Integración pendiente de confirmación.

## Uso y alcance

El Editor conserva el lienzo y la estética Industrial Moderno. Herramientas agrupadas en Documento, Campo, Composición y Estado y límites; las secciones se despliegan según necesidad. Ctrl/Mayús permiten selección múltiple. Las propiedades corresponden al campo seleccionado; las operaciones de composición se aplican a la selección.

| Herramienta | Comportamiento |
|---|---|
| Recorte | Selección sobre página fuente o límites en mm; rebase conserva anclas absolutas, borrados, continuación y estado. Rechaza excluir campos/estado. Fuente sin modificar. |
| Anclaje | Selección explícita de texto extraído del PDF, incluido Word convertido. Guarda hash, página, texto, caja, ocurrencia y desplazamiento; no OCR ni edición Word. |
| Relocalización | Resuelve anclas explícitas verificables sin deriva y rechaza fuente cambiada/referencia ambigua. Sin anclas: solo plantillas ACETONA/EDROFONIO, con confirmación de sustitución y posibilidad de deshacer. |
| Zona de estado | Reserva visual y límites mm; puede quitarse. Aviso de proporción respecto del maestro de estado elegido, no de una proporción universal fija. No aprueba material ni documento. |
| Campos/auxiliares | Geometría mm, tipografía y flags existentes; modos textbox/baseline/continuation/paragraph. Ajustes de borrado y segunda línea preservan atributos JSON anteriores. No recomponen textos fijos, tablas o imágenes. |
| Composición | Alineación a límites/centros y distribución de espacios; reajuste proporcional opcional de fuente y estado. Campos bloqueados impiden transformaciones, eliminación/cambio de clave hasta desbloquear. Recortar conserva su posición absoluta. |
| Deshacer/rehacer | Snapshots completos de campos, recorte y estado; un arrastre es una operación. Ctrl+Z/Ctrl+Mayús+Z y botones. Guardar marca el punto limpio; undo posterior vuelve a estado pendiente. Historial delimitado al cambiar revisión o recargar Tkinter. |
| Formato de salida | Tamaño físico, orientación A4, márgenes, separación y seguridad; selección/guardado de perfiles existentes. El motor conserva proporciones y muestra tamaño efectivo. Seleccionar el perfil explícitamente en Emisión Tkinter; no se transfieren variables ni configuración de trabajo. |
| Prueba PDF | Motor existente sobre el diseño en memoria, datos variables vacíos y numeración de prueba, con marca de prueba. No modifica diseño guardado, no aprueba ni registra emisión histórica. El PDF se guarda en cache local. |

El lienzo de edición muestra fuente y reservas geométricas, no una simulación completa de datos de emisión. La prueba PDF se rasteriza desde el resultado del motor. El zoom de visualización no describe ni cambia el tamaño físico. Los solapamientos con contenido fijo deben revisarse documentalmente; estos controles no reemplazan esa revisión.

## Persistencia y transición

Guardar diseño pendiente es explícito y separado de un futuro trabajo de emisión. Un servicio compara diseño completo e identidad de fuente, verifica integridad/límites y escribe campos/recorte/estado en una transacción con auditoría. Cambio externo, revisión no pendiente o fuente alterada bloquean el guardado. No hay cambio de esquema: `user_version=3`, mismos registros/UID/archivos.

La UI permanece bloqueada durante el acompañante Tkinter y recarga el diseño al cerrarlo. Conserva la misma carpeta de datos y revisión. Esta PR no agrega exclusión entre instancias ni sincronización de variables: ese contrato y los trabajos independientes pertenecen a R3B3. No se promete sincronización bidireccional actual.

Tkinter y su entrada permanecen disponibles. Emisión definitiva, historial, importación por carpeta, comparación básica y otras filas anteriores siguen identificadas como tales. La matriz mantiene 87 IDs: 38 Qt, 8 parciales, 34 anteriores y 7 motor; las ampliaciones nuevas están fuera de ese recuento de referencia.

## Verificación

- Suite completa con fixtures sintéticos, incluidos regresión R3A, núcleo y pruebas nuevas `test_editor_layout.py`/`test_r3b1_qt.py`.
- Pruebas de rebase absoluto, exclusión, borrado/continuación, bloqueo, anclas/ambigüedad, historia completa, guardado transaccional y estados obsoletos.
- Concordancia de origen/línea base y tamaño tipográfico en PDF con geometría calculada; tolerancia 0,02 puntos (aprox. 0,0071 mm) para la prueba sintética, sin extrapolar a impresión física.
- 74 verificaciones de widgets por escala 1/1,25/1,5: 48 anteriores y 26 nuevas; capturas de diseño pendiente, cambios, anclaje, composición, bloqueo, vigente/retirada y compacto.
- Workflow Qt aplica suite, verifica fuentes y ejecutable en tres escalas, empaqueta Qt y compañero Tkinter, verifica puente y publica ZIP/capturas/JSON. Workflow núcleo conserva compilación portable original.

Resultados exactos y enlaces a CI/artefactos se entregan en la PR sobre su commit final. Todas las evidencias públicas del repositorio son sintéticas. Pruebas reales de Word, impresión física, Windows 10/11 y equipos COVEX siguen pendientes; esto no es validación GMP. 00-R1 continúa PENDING. No implementa R3B2/R3B3/R3C ni integraciones Business Central/SharePoint.
