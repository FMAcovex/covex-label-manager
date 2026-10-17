# Auditoría integral UX/UI antes de R6C

Fecha: 17/10/2026. Base auditada: `main` **afd0b06454c54e1e722596c37a6f6557883f2c16**, después de integrar la PR #27. Rama de entrega: `chore/ux-audit-r6b`. Aplicación PySide6; Tkinter se inspecciona como compatibilidad. Esta carpeta contiene documentación y evidencia sintética; no implementa el rediseño ni constituye aceptación GMP.

La aplicación conserva una base funcional amplia y verificable, pero la acumulación de barras, modales, términos de transición y accesos paralelos penaliza la localización y el espacio de trabajo. **No se ha demostrado la eliminación de una de las 87 capacidades históricas. Sí se han demostrado rutas confusas, controles redundantes, paneles residuales y problemas de adaptación.** El resultado no justifica retirar Tkinter ni empezar a cambiar estados documentales o reglas de emisión.

La prioridad previa a R6C es corregir la jerarquía de acciones y la adaptación de Editor, diálogos y Emisión, conservando todas las operaciones y sus guardas. La disponibilidad de una función, la paridad visual histórica y su aceptación operativa son tres cosas distintas.

| Entregable | Contenido |
|---|---|
| [Diagnóstico ejecutivo](DIAGNOSTICO.md) | Heurísticas, fortalezas, problemas demostrados y límites. |
| [Inventario por pantalla](INVENTARIO.md) | Controles, acciones, controladores efectivos y estados; lectura de la herencia. |
| [Inventario de sitios](INVENTARIO_SITIOS.md) | Índice exhaustivo de construcciones, señales y menús estáticos. |
| [Registro estático completo](inventario-sitios.json) | Expresiones, expansiones de bucles y referencias de pruebas por símbolo. |
| [Registro observado](inventario-runtime.json) | Controles por estado, geometría, habilitación, visibilidad, menús y hashes de capturas. |
| [Conservación de las 87 capacidades](CONSERVACION_87.md) | Cada ID original, ruta efectiva, controlador, evidencia y limitación. |
| [Incidencias priorizadas](INCIDENCIAS.md) | Severidad, impacto, frecuencia, riesgo GMP, esfuerzo, dependencias y reproducción. |
| [Experiencia operativa](FLUJOS_OPERATIVOS.md) | Preparación, modificación, aprobación, emisión y reimpresión; pasos y pantallas. |
| [Navegación y rediseño](ARQUITECTURA_Y_PROPUESTAS.md) | Alternativas A/B, menús, paneles y dirección Industrial Moderno. |
| [Roadmap](ROADMAP.md) | Correcciones rápidas, cambios estructurales y puertas de aceptación. |
| [Plan de regresión](REGRESION.md) | Cobertura existente y verificaciones pendientes antes de implementar. |
| [Evidencias](EVIDENCIAS.md) | Galería de SVG reales y seis combinaciones de tamaño/factor Qt. |
| [Método reproducible](METODO.md) | Entorno, comandos, alcance, limitaciones y herramientas de auditoría. |

Evidencia funcional de base: **373 pruebas pasan, 2 se omiten** (conversión Word real y semántica Windows de bloqueo SQLite). Datos exclusivamente ficticios, generados por fixtures. La aprobación ficticia preexistente de `DemoSession` es un estado del fixture; la auditoría no acepta aprobaciones de documentos ni resultados de UAT. La generación de una emisión sintética temporal permite comprobar Historial sin enviar trabajos a una impresora.

Las propuestas requieren revisión y aprobación antes de una PR de implementación. SQLite v4, integridad, revisiones/variantes, evidencias, trazabilidad, emisión e historial deben mantenerse. Sin squash, merge, migración de datos ni validación productiva en esta auditoría.
