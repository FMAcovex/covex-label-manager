# Roadmap de implementación para aprobación

Esta auditoría no inicia R6C ni modifica la aplicación. Las fases siguientes se proponen para PR independientes después de aprobar el alcance. No requieren cambiar SQLite v4 ni las reglas de aprobación, integridad, emisión o historial.

| Fase | Alcance / incidencias | Tipo y esfuerzo orientativo | Dependencias | Puerta de salida |
|---|---|---|---|---|
| 0 · Decisión y baseline | Confirmar alternativa A/B; contrastar UX-18 con casos concretos/artefactos; aprobar vocabulario y métricas | Investigación, 1–2 días + agenda de operadores | Revisión de este informe y evidencias sintéticas | Mapa de 87 IDs aceptado, casos de «función perdida» especificados o mantenidos como no confirmados |
| 1 · Correcciones localizadas | UX-01/02/06/09/10/12/14/16/19: rutas nativas, dock contextual, nombres, contraste, precisión presentada y documentación | Quick wins, 2–4 días acumulados | Aprobación de textos/rutas; tests existentes; round-trip numérico | Ninguna pérdida de acción; regresión de estados, navegación, cancelación y contraste |
| 2 · Adaptación y jerarquía | UX-03/04/05/07: modales con scroll, barras compactas, paneles recuperables, visor con mandos visibles | Estructural, 4–7 días | Prototipo aprobado en 1366/150 y 1920/100; contrato de dock | Seis configuraciones sin overflow de acciones críticas; resultados visuales revisados |
| 3 · Modelo de comandos y flujo | UX-08/11/17: agrupación de menús, disponibilidad por estado, separación diseño/trabajo | Estructural, 3–5 días | Navegación de fase 2; matriz comando→servicio→test | 87 IDs conservadas, pruebas positivas y negativas de cada comando afectado |
| 4 · Importación y accesibilidad | UX-13/15: teclado/árbol accesible; worker aislado para conversiones largas si medición lo confirma | Estructural, 4–8 días | Perfilado sintético; diseño de concurrencia/SQLite; Windows disponible | Cancelación segura, progreso, sin compartir conexión UI; lector de pantalla y foco verificados |
| 5 · Validación operativa autorizada | Regresión completa, Windows real, Word, impresora/calibración, pruebas con operadores; protocolo R6 | Validación externa; duración no estimada desde Linux | Revisión Calidad/IT, hardware/documentos autorizados y procedimiento | Evidencia y aprobación formal separadas; nunca aceptar automáticamente por suite verde |

Los esfuerzos no deben sumarse como fecha comprometida: hay dependencias, revisión y tareas que pueden combinarse. Los riesgos físicos/GMP solo se cierran con responsables y evidencias autorizadas.

## Reglas de implementación

1. Cada PR identifica las filas de conservación afectadas, controles reubicados, rutas nuevas, alias temporales y pruebas de cancelación/bloqueo.
2. Reubicar o consolidar un botón no elimina su capacidad. Un acceso nuevo no reemplaza al anterior hasta demostrar equivalencia funcional y accesibilidad aprobada.
3. Mantener servicios y SQLite v4; no trasladar la única validación al UI ni convertir una confirmación en aprobación implícita.
4. No retirar Tkinter, tocar evidencias reales, regenerar snapshots históricos ni convertir «entregado al driver» en «impreso» dentro de una mejora visual.
5. PR pequeñas, sin squash/merge por el agente en esta auditoría. El estado de revisión de este informe no equivale a autorización de todas las fases.

## Criterio para empezar R6C

Resolver o aceptar formalmente los P1 demostrados, registrar qué queda pendiente por plataforma y aprobar un plan de regresión. UX-15 es un riesgo de arquitectura que requiere medición; no bloquear por una cifra de rendimiento inventada. La aceptación de uso y validación GMP sigue el protocolo documental correspondiente, no este roadmap.
