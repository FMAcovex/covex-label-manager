# Diagnóstico ejecutivo y evaluación UX/UI

## Resultado y alcance

La principal deuda es de organización y adaptación de una aplicación funcional, no una pérdida demostrada del motor. La interfaz nativa ha avanzado más que parte de sus textos y documentación histórica. El usuario puede encontrar una invitación a usar la «versión anterior» junto a controles Qt que ya realizan la operación. Esa contradicción hace plausible la percepción de funciones perdidas, aunque exista una ruta alternativa.

Se revisan los módulos completos de interfaz mediante inventario AST, los controladores que conectan cada familia de controles, la resolución de métodos de `FunctionalWindow`, las 87 filas históricas y las pruebas existentes. Se ejecuta la suite íntegra y se recorren estados sintéticos con widgets reales. El inventario observado no equivale a haber accionado todos los controles ni a haber validado accesibilidad con un lector de pantalla: las lagunas se señalan en REGRESION.md.

## Fortalezas que debe conservar el rediseño

- Biblioteca, Editor, Emisión, Historial y Configuración tienen rutas nativas. Selección de revisión, estados escritos y documentos ficticios con marca permiten distinguir situaciones.
- El diseño fijo está protegido; cambios estructurales requieren guardado explícito. Los trabajos tienen guardado local y reconciliación; no debe confundirse con la aprobación documental.
- La emisión exige revisión documental utilizable, datos, preflight y vista previa actualizada. La prueba PDF lleva marca y no registra emisión definitiva.
- La aprobación de revisión exige responsable, referencia, reconocimiento explícito y confirmación; retirar la vigente se advierte. La variante mantiene su ciclo y evidencia propios.
- Historial verifica PDF/snapshot y exige motivo para una reimpresión; el envío al driver no se presenta como confirmación física.
- El verde petróleo, superficies claras, tipografía coherente e iconografía lineal son una base Industrial Moderno aprovechable; cambiar la organización no exige sustituir toda la identidad visual.

## Evaluación profesional por dimensión

| Dimensión | Observación | Consecuencia / criterio propuesto |
|---|---|---|
| Jerarquía | Varias barras por pantalla; botones primarios para crear campo, abrir editor, aprobar o emitir en contextos próximos. | Una acción principal por tarea/contexto; acciones documentales separadas del trabajo de lote. |
| Navegación | «Revisiones y variantes» llega al catálogo heredado; el menú Documentos mezcla edición, importación, exportación y conciliación. | Entradas agrupadas y nombres de tarea; ninguna ruta de compatibilidad como acceso ordinario a una función ya Qt. |
| Consistencia | Aprobación de revisión, aprobación de variante y aprobación de maestro de estado usan formularios distintos. | Compartir patrón visual y vocabulario sin fusionar entidades, requisitos ni servicios de aprobación. |
| Reconocimiento | En modo compacto, Historial/Configuración pierden el texto visible, y paneles del Editor se ocultan por anchura. | Mantener nombres cortos o menú etiquetado y estado visible de los paneles. |
| Legibilidad | Controles laterales cortan textos largos; metadatos y advertencias usan texto pequeño y claro. | Reflujo, etiquetas completas, ancho mínimo útil, contraste medido y texto de avisos priorizado. |
| Espacio | En 1366×768/100 % la zona de lienzo inicial queda reducida por cabeceras; mostrar datos del trabajo reduce más el área central. | Cabecera contextual compacta y panel derecho por pestañas; probar una sola columna en pequeño. |
| Adaptación | Umbrales fijos `<1200`, `<1100`, `<650`; diálogos con mínimos de contenido superiores al área objetivo al 150 %. | Adaptar a espacio efectivo en DIP, scroll en formularios y pie de confirmación accesible. |
| Prevención de error | Guardas fuertes en servicios; algunos menús muestran acciones no aplicables y explican el fallo solo después. | Deshabilitación contextual con motivo accesible; volver a validar en el servicio siempre. |
| Aprendizaje | «Variante», «revisión», «trabajo», «diseño heredado», «calibrar hoja» y «calibrar impresora» aparecen sin una explicación conjunta. | Ayuda contextual breve que diga qué cambia y qué se conserva; esquema de entidades en onboarding del producto. |
| Eficiencia | Hay accesos repetidos con el mismo controlador y trayectos que obligan a abrir un panel o regresar a Emisión. | Consolidar presentación, conservar acceso a todas las operaciones y no reducir controles de confirmación de alto riesgo. |
| Accesibilidad | Son numerosos los `accessibleName` vacíos en el registro de widgets y botones «+»/«−» sin nombre explícito. QFormLayout puede aportar asociación implícita. | No afirmar que todo campo es inaccesible. Probar el árbol accesible, foco, teclado, lector y contraste. |
| Feedback | Dos avisos de preflight pueden resumir una lista mayor y los detalles quedar en otra pestaña/scroll. | Resumen navegable por error con foco en destino; no limitar la corrección a descubrir la pestaña correcta. |

## ¿Se ha perdido funcionalidad anterior?

La [matriz de 87 IDs](CONSERVACION_87.md) localiza las capacidades en la versión actual. El recuento de rutas es 78 Qt, 2 mixtas y 7 de motor/procedimiento. No significa 100 % aceptado ni prueba positiva independiente por cada ID. La matriz histórica principal quedó en el hito R3C; D14, I02, M11 y C01–C07/C10 ya no deben considerarse exclusivamente heredadas.

Hay tres regresiones de experiencia demostradas: acceso residual al catálogo de transición en lugar de la gestión nativa, paneles que desaparecen o pierden espacio en pequeño y duplicación de aprobación con textos diferentes. No hay golden screenshots históricas suficientes para afirmar que un estilo, icono o distribución concreta de R3 fue eliminado erróneamente. El diseño libre del fondo fijo, OCR universal, QR dinámico, firma electrónica, multiusuario y restauración ZIP automática desde UI no pertenecen a las 87 capacidades implementadas: no deben presentarse como pérdidas.

## Riesgo y decisión

La recomendación es aprobar primero las correcciones P1 de adaptación y rutas, y después una consolidación por fases. El riesgo GMP indicado en incidencias es una estimación del peligro de interpretación/operación; no demuestra una emisión incorrecta, un fallo de integridad o una validación GMP. Los controles de servicio y las confirmaciones no se deben debilitar para reducir clics.

No se recomienda declarar R6C aceptado por este informe: faltan Windows 10/11 con fuentes y escalado reales, teclado/lector de pantalla, conversión Word instalada, impresión/calibración sobre papel y sesiones con operadores autorizados.
