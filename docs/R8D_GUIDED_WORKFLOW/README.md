# R8D — experiencia guiada de emisión

Base R8C `8859f21ab77878b3e5c874bfac0023d0c8ad2ca3`. Rama `feature/r8d-guided-workflow-ux`, una PR borrador contra R8C. Cadena R8A #33 → R8B #34 → R8C #35 → R8D sin fusionar ni squash. Evidencia exclusivamente sintética. No declara aceptación funcional ni validación GMP.

## Recorrido de cuatro pasos

1. **Seleccionar etiqueta**. Buscar nombre, código, producto, país/mercado o tipo realmente registrado. Cada fila identifica revisión, variante y uso documental, con PDF de la fuente fija. Los datos variables se revisan después. Ante alternativas exige elección; sólo un resultado inequívoco autorizado se preselecciona, nunca borrador/retirada/variante no autorizada.
2. **Introducir datos**. Formulario del contrato real, obligatorios con *, recipientes y copias visibles (límites anteriores: 1–10000 recipientes, 1–2 copias). No inventa lote/peso/fecha. kg/g/mg conservados y convertidos según sufijo documental. Pestañas «Datos por recipiente», «Formato y opciones adicionales» y «Añadir etiqueta de estado». Los valores de campos eliminados de un contrato se conservan para revisión, no se borran silenciosamente.
3. **Revisar etiqueta**. PDF real del mismo trabajador aislado del Centro, token/generación/SHA; datos, revisión/variante, papel, dimensiones, cantidad, composición y avisos. Zoom/ampliación, regreso a datos/estado o ajuste temporal R8C. No continúa con vista previa obsoleta.
4. **Emitir o generar prueba**. Resumen, prueba separada de definitiva y confirmación documental del controlador existente. Éxito sólo después de persistir. Abrir PDF, imprimir mediante función existente, historial y preparar otra emisión. Generar PDF o enviar al controlador **no confirma impresión física**.

Volver a Inicio conserva el borrador. Continuar abre UID/generación existentes. Retroceder a selección y continuar con el mismo diseño conserva trabajo/valores; elegir otro crea un trabajo nuevo y deja el anterior recuperable. Nueva emisión no copia datos críticos. Copiar explícitamente sigue disponible en el Centro avanzado.

## Arquitectura, conservación y GMP

`GuidedWorkflow` es presentación: no persiste ni compone PDFs. Su `WorkPanel` está en `work_panels`, con el mismo `api.work`, CAS/autoguardado, revisión, PDF, emisión e historial. «Centro avanzado»/«Asistente» conservan identidad y generación; si no se guarda, no hay traspaso. En conflicto externo conserva pantalla y no sobrescribe disco. Ambas presentaciones se desactivan durante operación crítica; Tkinter mantiene exclusión. El temporizador de presentación se detiene al cerrar; protecciones R8A originales intactas.

SQLite v4 **sin cambio de esquema**, contratos R8C intactos, sin catálogo ni motor paralelo. Editor de tres zonas, tipografía/escalado, variantes, revisiones, aprobación externa, diagnóstico, auditoría, historial y reimpresiones conservados. Un trial R8C sigue PRUEBA / NO GMP y bloquea definitiva antes de INTENT. El nombre del tipo verde «Aprobado» no concede aprobación documental. Revisión de estado explícita, sin sustituir silenciosamente el maestro histórico.

Mensajes operativos evitan excepciones/rutas/UUID técnicos, dan siguiente acción y conservación de datos; detalles en diagnóstico privado R8A. Cambiar el mensaje no elimina errores de autorización o integridad. La confirmación definitiva ahora muestra lote e identidad completa, sin depender del encabezado elidido.

La identidad distingue estado documental de revisión/variante y «Trabajo: Borrador». Guardar un trabajo pendiente de emisión no rebaja una revisión aprobada ni otorga aprobación a un diseño pendiente.

## Navegación y cambios visuales

| R8C | R8D | Conservación |
| --- | --- | --- |
| Apertura en Biblioteca | Inicio: Nueva emisión, Continuar, Buscar, Historial | Cabecera conocida y COVEX · Inicio persistente |
| Nuevo técnico y Centro concentrado | Asistente recomendado de cuatro pasos | Centro avanzado completo con Nuevo/Copiar/Recargar |
| Cantidad/copias dentro de Formato | Visibles en datos, opciones adicionales separadas | Mismos widgets y validadores |
| Estado entre parámetros técnicos | «Añadir etiqueta de estado» y explicación documental | Catálogo, editor y emisión individual anteriores |
| Guardar/prueba/definitiva/impresión próximos | Separación datos/revisión/operación/resultado | Mismos servicios, confirmación e impresión real |
| Ajuste de apariencia en Centro | También desde revisión guiada | Diálogo y guardas R8C |
| Ayuda dispersa | Inicio rápido y explicaciones breves | No sustituye procedimientos GMP |

Tema claro Industrial Moderno, controles conocidos y scroll en paneles extensos. Anterior/Continuar/Inicio fuera del scroll. Tab/Shift+Tab, Alt+Derecha/Alt+Izquierda en asistente. Ayuda explica variante, retirada, copias, prueba/definitiva y ajustar/rellenar. Separación visual no crea permisos GMP.

## Medición reproducible de cinco tareas

`r8d_visual.py` ejecuta el mismo módulo contra R8C exacta y R8D. Cuenta cada edición, selección o activación como una acción, no caracteres. Formularios/confirmaciones se cuentan como diálogos; esperas, setups de fixture y capturas fuera del recorrido no son clicks. No mide tiempos ni carga cognitiva humana.

Resultados locales al 100 %, iguales en ambas resoluciones, con controles/PDF/servicios reales:

| Tarea y punto de partida idéntico | Acciones antes → después | Pantalla/pestaña antes → después | Diálogos antes → después |
| --- | --- | --- | --- |
| Producto: trabajo nuevo ya vinculado, sólo falta lote; terminar en registro | 4 → 5 | 0 → 2 | 1 → 1 |
| Recipientes: valores comunes preparados, cambiar cantidad/lote recipiente 2; revisar PDF | 4 → 4 | 1 → 2 | 0 → 0 |
| Estado: lote preparado, elegir tipo/revisión/ubicación/composición; revisar PDF | 6 → 6 | 1 → 2 | 0 → 0 |
| Recuperar: selector visible, abrir borrador de disco | 2 → 2 | 0 → 1 | 0 → 0 |
| Historial visible: elegir original, verificar PDF, motivo y reimpresión registrada | 6 → 6 | 0 → 0 | 2 → 2 |

**No se afirma ahorro de clicks.** Se añade una activación para separar revisión y registro, estructurando pantallas enfocadas. Centro avanzado sigue más directo para expertos. Búsqueda/vinculación se prueba y captura aparte; la tabla no incluye importación/aprobación y empieza con trabajo vinculado. Tres decisiones técnicas explícitas del caso de estado (revisión, ubicación, composición) permanecen en ambos; las demás tareas usan formato válido sin decisiones de formato. No equivale a medir carga cognitiva con operarios. JSON guarda todas las secuencias y límites del benchmark.

## Evidencia y regresiones

`test_r8d_guided_qt.py`: cuatro pasos, navegación real/teclado/seis tamaños, vuelta atrás, recuperación, identidad compartida, prueba/definitiva, duplicados, historial, unidades/recipientes, estados/fit/fill, trial R8C, CAS, integridad y PDF alterado. Sólo se automatizan respuestas humanas de confirmación/destino; ningún mock sustituye emisión, autorización, PDF o guardado.

`guided_checks.py`: fuente/EXE, arranque/cierre, edición por teclado, PDF automático, emisión y reimpresión por diálogo real/motivo, original/hash/raster intactos, SQLite, traspaso y medidas exactas. Cinco tareas por dos resoluciones. CI conserva bloques previos y añade R8D nativo, antes/después R8C, y **el mismo ZIP final extraído** al 100/125/150 %. No se relajan aserciones ni timeouts. Interacciones Windows nativas; capturas grandes Qt offscreen sobre Windows, como R8B/C, no aceptación física.

Artefacto técnico: `r8d-visual/before-1/` Biblioteca/Centro/Historial; `source-1/` y `extracted-1/` Inicio/Selección/Datos/Revisión/Emitir/Centro/Historial. También `1.25`/`1.5`. PDFs sintéticos registrados, hashes, JSON/trazas/JUnit separados del portable y de Git. Guía/plan integral se incluyen antes de manifiesto SHA/CRC; portable mantiene Qt/Legacy/licencias. Artefactos retención 14 días.

Resultados finales, commit, tres CI y enlaces se registrarán en la PR al terminar, no se presuponen. [Auditoría previa](AUDITORIA_PREVIA.md), [87 capacidades y ampliaciones](CONSERVACION_87.md), [plan integral](../R8_INTEGRAL_ACCEPTANCE_PLAN.md).

## Incidencias resueltas y límites

Primera CI Qt (`39266168063`): los bloques históricos R8A/B y 70 R8C pasaron; la nueva aserción literal `SYN-R8D` encontró `SYN\u00adR8D` con Arial histórica Windows. Se conserva íntegra esa ruta y sus métricas. Las aserciones nuevas ahora usan una variante sintética con fuentes embebidas R8C, aprobada sólo en fixture aislado, idéntica antes/después; se exige el texto exacto **y** recurso PDF `R8C_`. No se normalizan caracteres ni se relajan criterios. Las comparaciones históricas R8C siguen verificando la ruta anterior.

CI `39267429721`: emisión/prueba/historial y texto exacto ya satisfactorios; el escritorio nativo alojado limitó 1366 px a 1028 px. No se acepta 1028 como 1366 ni se elimina la aserción: se ejecutan los 14 casos operativos con backend Windows nativo y los seis casos exactos de viewport en proceso Windows offscreen separado. Se conservan todos los tests de teclado/PDF/geometría y el mínimo de espacio útil para la vista PDF. Las capturas y EXE extraído siguen comprobando ambas resoluciones a las tres escalas. No acredita pantalla física Windows 10/11 ni amplía timeouts.

CI `39268806975`: los 14 casos nativos y los seis viewports pasaron; antes/después pasó al 100 %. A 125 % el controlador de medición de R8C intentaba pulsar Actualizar en el panel PDF oculto por el selector compacto. Se corrige el recorrido de la prueba: seleccionar la vista PDF por teclado antes de pulsar su botón, contar ese cambio y exigir que los controles pulsados sean visibles. Los setups vuelven explícitamente a Datos antes de editar/recuperar. No se toca R8C ni se sustituye la comprobación real de PDF por un estado de widget; se mantiene `preview_matches` obligatorio. La tabla anterior se limita explícitamente al 100 %; las trazas de ventanas compactas cuentan también el cambio a PDF.

Se evita recrear trabajo al retroceder, se comparte CAS entre tres paneles, se conserva el error PDF en la presentación guiada, se cancela el temporizador al cerrar y se bloquean ambas presentaciones durante operaciones críticas. La prueba no aumenta copias ni transforma trial en producción.

No hay OCR/búsqueda semántica ni metadata inventada. Fuente fija en selección, PDF variable en revisión. Estados individuales usan gestor existente. Opciones físicas/estado conservan complejidad controlada en pestañas. Reducción de carga cognitiva, Word real, Windows físico, impresora y lotes grandes requieren aceptación conjunta posterior. Permanecen límites conservadores de recorte/fuentes/contraste R8C. No se atribuye validación documental a un test UI, ni aceptación funcional/GMP a esta entrega.
