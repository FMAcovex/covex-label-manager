# R6B-UX integrado — UX-1 + UX-2 + UX-3

Implementación de la alternativa A (evolución Industrial Moderno), sobre `main` `6b4f5076b644fc445bb8a143d116091c9f4c9c64`, en `feature/r6b-ux-integrated`. Referencia obligatoria: auditoría `02f7ba7`, integrada por PR #28. La auditoría y sus evidencias no se modifican.

Los tres bloques se han aplicado consecutivamente: estructura adaptable, reorganización de operaciones y consolidación visual. No cambian servicios, esquema SQLite v4, motor PDF, cálculos físicos, reglas de aprobación, numeración, snapshots ni reimpresión. Las reubicaciones usan los controles/controladores existentes; no hay aprobaciones automáticas ni simulaciones de funciones productivas.

## Documentación y evidencia

- [Cambios por pantalla, comandos e incidencias](CAMBIOS_Y_ESTADO.md).
- [Conservación de las 87 capacidades](CONSERVACION_87.md), con rutas y familias de pruebas; no equivale a aceptación individual presencial.
- [Comparativa antes/después y galería](COMPARATIVA_VISUAL.md): seis combinaciones, 318 capturas y 129 SVG sintéticos seleccionados.
- [Resultados geométricos, hashes y procedencia](resultados-visuales.json).
- [Pruebas reproducibles, CI y guía del portable](PRUEBAS_Y_PORTABLE.md).
- [Causa raíz y corrección de la caída nativa Qt](CI_QT_FIX.md).

Resultado local tras corregir CI: 411 pruebas aprobadas, 2 omitidas; 32 casos de regresión UX y 6 de integridad del portable. El lienzo del Editor a 1366×768/150 % de la serie visual integrada pasa de 104 a 282 DIP de alto, sin esconder automáticamente paneles. No queda dock de lote en Configuración. Los diálogos críticos tienen cuerpo desplazable y pie de acciones accesible.

## Límites y decisión de revisión

UX-15 (concurrencia Word) se difiere expresamente; UX-18 continúa sin demostración histórica. UX-13 se cubre en nombres, foco y contraste comprobables, no en certificación UIA/lector Windows. El inventario presenta resumen y tabla legibles, con JSON íntegro desplegable. La evidencia Linux emula tamaños/escala de ventana; la CI Windows y la prueba presencial son capas distintas. No se declara validación GMP, aprobación documental real ni impresión física satisfactoria.

Una única PR en borrador para revisar código, capturas y resultados CI. No hacer squash ni merge durante esta entrega. R6C y las decisiones de aceptación siguen pendientes de aprobación humana.
