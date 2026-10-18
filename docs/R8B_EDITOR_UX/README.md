# R8B — Editor visual y simplificación funcional

## Alcance y base

PR dependiente en borrador: `feature/r8b-editor-ux` contra
`feature/r8a-stability-diagnostics`, no contra `main`. Base R8A:
`1885e235aeaf0792834403618531bad392874a3a` (PR #33, sin fusionar).
Incluye la limpieza segura de PDF cancelado y la preparación/cierre del catálogo
corregidos en **R8A**, sin copiarlos a mano ni reconstruir su historial.
Los resultados finales, SHA de entrega, tres ejecuciones CI y enlaces a portable y
evidencias se registran en la PR para no alterar el commit probado al publicarlos.

## Diagnóstico y resultado R8B1–R8B6

Se verificaron las relaciones entre `window`, `advanced_editor`, `workspace`,
`variants`, `functional`, `status_fields_dialog` y `work`. El controlador retenido
combina sus mixins; `workspace` redistribuye widgets **con sus señales originales**.
Los datos del trabajo de lote no son las propiedades estructurales del diseño.

| Bloque | Cambio funcional | Comprobación |
|---|---|---|
| R8B1 | Elementos a la izquierda, PDF fijo central y Propiedades a la derecha. Nombre, identificador, geometría, tamaño, negrita, obligatorio, bloqueo y modo no dependen de Avanzadas. Guardado fuera del scroll y de las pestañas. | Acceso y scroll real en seis tamaños lógicos; pie visible y lienzo utilizable. |
| R8B2 | «Gestionar variantes» sustituye `⋯`. Solo acciones aplicables; ayuda contextual en lugar del submenú de opciones inhabilitadas. Compatibilidad anterior identificada expresamente. | Apertura del menú Qt, ayuda y estados; herramientas existentes accesibles. |
| R8B3 | Añadir crea un campo editable en un clic; Dibujar trabaja directamente sobre el lienzo. Propiedades se actualizan sin destruir escena/zoom/selección/foco. Texto numérico pendiente se interpreta antes de cambiar de campo/guardar/cerrar. | Ratón real, escritura, cursores, identidad de objetos, guardar/reabrir, bloqueo, deshacer/rehacer y descarte. |
| R8B4 | Estados comparte tres zonas, términos, controles de geometría en mm, zoom, alta directa, deshacer/rehacer y guardado explícito. Propiedades pendientes se conservan al seleccionar otro campo; errores no cambian el diseño. | R7A/R7B + regresiones R8B, edición/capturas del EXE extraído. |
| R8B5 | Pie distingue revisión documental de variante y sus estados; instrucciones de solo lectura. «Aprobado» se identifica como **tipo de etiqueta de estado**, no aprobación documental. | Original aprobado sin cambios, mutaciones bloqueadas, variantes en borrador sin heredar aprobación. |
| R8B6 | Seis combinaciones Windows de resolución/escalado; propiedades con scroll vertical y guardado persistente; estilo claro Industrial Moderno. | Capturas antes/después y pruebas source/portable. No equivalen a un monitor físico Windows 10/11. |

No se unifican los repositorios/controladores de producto y estados. Los campos de
producto siguen usando geometría normalizada y los de estado puntos de la fuente;
la interfaz muestra mm desde el recorte sin cambiar sus contratos de guardado.
Los campos de estado no tienen bloqueo o modos tipográficos en su contrato actual:
no se añaden controles aparentes ni se amplía el motor PDF.

## Antes/después reproducible

Solo fixtures `SYNTHETIC`/DEMO temporales. Mismo generador de documentos y estados,
mismos tamaños físicos objetivo y `QT_SCALE_FACTOR=1`, `1.25`, `1.5`. Para comparar
se carga el código de la base exacta R8A mediante `--source-root`, no una imitación
del diseño anterior. Las diferencias de tamaño del cuadro Estado son intencionadas:
ahora el lienzo se adapta al espacio real y las propiedades tienen su propio scroll.

| Vista sintética (100 %) | Antes, base R8A | Después, R8B |
|---|---|---|
| Editor, 1366×768 | [Antes](visual/before/1366-editor.svg) | [Después](visual/after/1366-editor.svg) |
| Estado, 1366×768 | [Antes](visual/before/1366-status.svg) | [Después](visual/after/1366-status.svg) |
| Editor, 1920×1080 | [Antes](visual/before/1920-editor.svg) | [Después](visual/after/1920-editor.svg) |
| Estado, 1920×1080 | [Antes](visual/before/1920-status.svg) | [Después](visual/after/1920-status.svg) |

SVG son capturas Qt de fixtures, no bocetos. PNG nativos, tamaños, DPR, hashes e
informes están en el artefacto técnico de la CI Qt, `r8b-editor/`:
`before-{escala}` (12 vistas), `after-{escala}` y `extracted-{escala}` (14 cada uno).
Se incluyen multiselección, revisión protegida, variante borrador, menú, propiedades
desplazadas y Editor de estados, en ambas resoluciones. El escritorio reserva 40
píxeles lógicos para marco/barra; la resolución física se representa por viewport y
escala de Qt, no se afirma cambio físico de monitor/DPI en mitad de la sesión.
La primera ejecución Windows evidenció que el `show` nativo puede reducir la
ventana al pequeño escritorio alojado del runner. La captura ahora redimensiona
**después** de mostrar y exige igualdad exacta de tamaño, también para Estados;
un recorte residual hace fallar la prueba. No se acepta una captura más pequeña
como prueba de 1920×1080 ni se reduce el mínimo de lienzo. El mismo chequeo se
ejecuta en el EXE extraído y mantiene las verificaciones nativas anteriores.

## Botones: qué cambia y dónde queda cada capacidad

| Antes | Ahora / ubicación | Controlador conservado |
|---|---|---|
| `⋯` | Gestionar variantes, debajo del selector de variante | `variant_menu` / `build_variant_menu` |
| + Nuevo campo (modal común) | Añadir campo, Elementos, sin modal | `quick_add_field` → `command` |
| Dibujar (dos diálogos) | Dibujar campo, arrastre directo y propiedades | `StatusFieldsCanvas` reutilizado → `add_field_from_canvas` → `command` |
| Creación con tipo/numeración/texto fijo | Campo técnico → Añadir campo especial… | **Mismo** `add_field` y formulario completo |
| Quitar campo plegado | Eliminar campo, Elementos | `remove_field`; bloqueado exige desbloquear |
| Obligatorio/bloqueo/modo plegados | Propiedades, desplegadas desde inicio | `change_flags` / `change_draw_mode` |
| Guardar diseño pendiente, arriba | Guardar diseño / Guardar variante, pie persistente | `save_work`; misma exclusión optimista |
| ↶ / ↷ | Deshacer / Rehacer con texto | `undo_edit` / `redo_edit` |
| Herramientas tras dos niveles cerrados | Cabeceras técnicas visibles al iniciar; cuerpos plegables | Documento, Campo, Composición, Estado y límites |
| Editor Tkinter | Editor anterior (compatibilidad)… con explicación | `open_legacy('editor')`, proceso separado y exclusión conservados |
| Otras acciones · requisitos (opciones deshabilitadas duplicadas) | ¿Qué puedo hacer con este diseño? | Ayuda concreta, sin simular acciones prohibidas |
| Aprobar en menú Documento fuera de contexto | Solo aparece cuando la revisión está pendiente | `approve_revision` y validación externa intactos |

Se retiran duplicaciones **de presentación**, no operaciones: identificadores,
anclaje, recorte, borrado/continuación, alineación/distribución, escalado de campos,
formato físico, prueba PDF, restauración, edición anterior y trabajo de lote siguen
accesibles. No hay selector de fuente/color ni controles futuros ficticios.

## Conservación y seguridad

[Matriz completa de las 87 capacidades](CONSERVACION_87.md), con los mismos IDs.
SQLite v4, originales Word/PDF, integridad, historial, trabajos recuperables,
emisión/reimpresión, aprobaciones externas, auditoría y backups no cambian en R8B.
El motor PDF no se modifica. Continúan diagnóstico privado y controles R8A:
hash esperado del borrador de estado; fuente/generación de producto/variante;
redibujado diferido tras gesto nativo; cierre protegido; proceso aislado de preview;
rechazo de resultados obsoletos; exclusión del acompañante Tk.

Los cambios de aprobación que aparezcan en pruebas pertenecen **exclusivamente** a
fixtures sintéticos aislados. No aprueban documentos del usuario, no firman ni
declaran validación GMP. El nombre «Aprobado» no tiene privilegios documentales.

## Pruebas y diagnóstico de regresiones

- `tests/test_r8b_editor_ux_qt.py`: propiedades accesibles, scroll, guardado persistente,
  alta/dibujo reales, foco/cursor/zoom/selección, valores numéricos pendientes,
  bloqueo/solo lectura, herramientas y compatibilidad, menú y ayuda, edición de
  estados, cambio de selección con error, deshacer/rehacer/guardar/reabrir y 87 IDs.
  Un arrastre de estado fuera del recorte o solapado se rechaza restaurando el
  mismo objeto nativo, sin invalidar el borrador ni inutilizar Deshacer.
- `test_r3e_qt.py`: el escenario de creación ahora dibuja con ratón real, sin
  interceptar dos diálogos eliminados; conserva todos sus cotejos de guardado,
  reapertura y deshacer. `test_r6b_ux_qt.py` comprueba los mismos criterios de
  disponibilidad por estado, ahora por presencia en el menú y ayuda en lugar de
  acciones inhabilitadas. No se relajan permisos ni aserciones de integridad.
- `checks.py`: abre explícitamente Herramientas para la misma comprobación visual,
  porque el grupo ya es visible por defecto; mantiene el self-check de 86 casos.
- `main_qt.py --editor-ux-check INFORME --capture CARPETA`: prueba aislada incluida
  también en el EXE; dos resoluciones por proceso, guardado en variante y estado,
  original aprobado intacto, cero emisiones y comprobaciones SQLite.
- Se mantienen suite completa, tres CI, regresiones R8A, 86 self-checks por escala,
  importador, Qt/Tk, compatibilidad histórica, emisión automática antes de manual y
  prueba del ZIP **realmente extraído**, manifiesto/CRC/inventario/SHA por archivo.

## Portable y riesgos residuales

Un único portable Qt para integración técnica; informe/capturas en descarga
separada. El enlace y SHA-256 del ZIP final se entregan en la PR tras tres CI verdes
sobre el mismo commit. No se solicita aceptación manual durante R8B.

La evaluación automática cubre los fixtures y estados descritos, no todas las
combinaciones documentales ni hardware/Word/impresoras reales. A resoluciones
pequeñas hay scroll intencionado para propiedades y herramientas; Ampliar lienzo
es una elección explícita recuperable. La edición múltiple de propiedades sigue
afectando al campo activo; Composición transforma la selección completa. No se
incorpora duplicar campo a un contrato que antes no lo ofrecía.

R8C: familias tipográficas, colores, alineación tipográfica, ajustes en emisión,
escalado avanzado de estados y perfiles aprobados. R8D: siguientes asistencias y
simplificaciones operativas según su alcance futuro; **no se anticipan aquí**.
La aceptación visual humana del conjunto R8 y la validación GMP quedan pendientes.
