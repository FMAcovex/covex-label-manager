# Plan de regresión visual y funcional

## Verificación realizada en esta auditoría

`python -m pytest -q --junitxml=test-results/ux-audit-baseline.xml`, sobre el commit base con Python 3.12.14, PySide6 6.8.3 y `QT_QPA_PLATFORM=offscreen`: **373 passed, 2 skipped, 85,14 s**. Las omisiones son Word real (requiere ensayo explícito) y bloqueo SQLite de lectores antiguos en Windows (requiere runner Windows). `uv pip check` pasa. Los resultados son de la máquina actual, no de CI Windows ni del portable.

Las capturas finales usan Qt **xcb sobre Xorg dummy**, Fusion y factores `QT_SCALE_FACTOR=1/1.25/1.5`; reproducen 51 estados en cada uno de los dos tamaños de ventana: **306 capturas**, seis manifiestos sin errores del harness. Se incluyen 123 SVG de widgets reales seleccionados en la galería; los PNG quedan ignorados con hashes registrados. La cuenta definitiva de SVG se puede comprobar en EVIDENCIAS.md y no representa otros tantos tests de comportamiento.

El recorrido visual verifica producción de preview, habilitación posterior de emisión, apertura/cancelación de modales, carga de historial sintético, estados de configuración, menús y dos rutas residuales. Para obtener Historial crea un registro en la base temporal sintética mediante el servicio normal; no envía impresión ni acepta aprobaciones documentales. Los formularios de UAT permanecen sin resultados aceptados.

## Cobertura funcional que debe conservarse

| Área / capacidades | Suites existentes de referencia | Regresión requerida en cambios futuros |
|---|---|---|
| Biblioteca B01–B13 | test_r3a_qt | Filtros combinados, limpiar, favoritas/recientes, selección, doble clic/Enter, Ctrl+K, columnas y recuperación de paneles. |
| Documentos D01–D14, importación I01–I05 | test_r3a_qt, test_core, test_r3f_qt, test_r5a_catalog, test_r5b_migration, test_r5c_qt/reconciliation | Fuentes íntegras; consulta/clone/aprobación separados; cancelar no cambia estado; nueva revisión retira solo cuando procede. |
| Editor E01–E15 | test_editor_layout, test_r3b1_qt, test_r3e_qt | Crear, mover, tiradores, multi, bloqueo, key única, recorte/ancla/auxiliares/estado; undo/redo, guardar y reabrir sin tocar el maestro fijo. |
| Variantes y SQLite v4 | test_variants_v4, test_migration_v4, test_migration_consent | Ciclo independiente, nominal, evidencia/hash, generación/CAS, migración solo tras consentimiento y conservación de UID. |
| Trabajos M01–M18 | test_emission_work, test_emission_work_qt/tk, test_r3c_emission_qt, test_mass_units | Autoguardado de lote ≠ guardado de diseño; herencia por recipiente, Unicode/multilínea, pesos, retención y cambio de documento controlados. |
| Emisión y fallos | test_r3c_emission_qt, test_emission_work | Prueba marcada sin issue; confirmar producción; token/preview/PDF manipulados bloqueados; fallo antes/después de commit reconciliado sin duplicados. |
| Hoja/perfiles P01–P07 | test_r3e_layout/qt, test_r4a_layout/qt, test_r4b_calibration/qt | Grid/libre, papel, orientación, proporción, capacidad/overflow, casillas usadas, perfiles inválidos conservados, calibración vinculada a geometría. |
| Impresión nativa | test_r4c_dispatch/qt | No imprimir draft/prueba como definitivo; cancelación sin envío; PDF alterado bloqueado; fallo/handoff auditados sin afirmar papel impreso. |
| Historial H01–H05 | test_r3c_history, test_r3c_history_qt | Hash/snapshot, datos históricos, motivo, números originales, retirada, legacy con advertencia y rechazo de reimpresión inválida. |
| Configuración C01–C10 | test_r3d_settings_qt, test_publication | Operador, copia con manifiesto, ruta readonly, CM acumulativo/duplicados, maestro estado con cotejo, auditoría/recuentos. |
| Aceptación | test_r6a_acceptance/qt, test_r6b_session/qt | NO ACEPTADO; 14 casos, generaciones inmutables, PASS exige evidencia; errores no fabrican aceptación. |

Los 884 sitios de UI no tienen todos una prueba directa de clic identificada. La asociación por símbolo del inventario no sustituye cobertura de ramas, accesibilidad o revisión visual. Las pruebas de servicio de importación R5B no demuestran por sí solas la selección de todas las combinaciones de widgets del diálogo controlado.

## Matriz visual para cada PR de interfaz

Ejecutar las seis combinaciones; registrar área física objetivo, tamaño lógico real, DPR, fuentes, plataforma, commit y estado. Comparar con baseline aprobada de la misma plataforma. Linux sintético es una capa; los portables deben ensayarse en Windows real.

| Vista | Estados mínimos | Aserción funcional y visual |
|---|---|---|
| Biblioteca | Vacía; 1/5/1000 revisiones; búsqueda sin resultados; filtros/favoritas/recientes; pendiente/vigente/retirada; inspector oculto/abierto | Identidad y estado legibles; selección retenida; tabla esencial y rutas nativas accesibles. |
| Editor | Pendiente limpio/cambios; variante DRAFT/PENDING/APPROVED/RETIRED; fuente alterada; ningún/uno/varios campos; bloqueado | No editar vigente; guardar/undo correctos; lienzo útil; textos sin corte; paneles recuperables. |
| Dock/trabajo | Abierto en Editor y cambio a cada destino; sin trabajo, DRAFT, EMITTING, ISSUED, conflicto de generación | Sin dock residual ni pérdida de datos; título del documento y trabajo no contradictorios. |
| Emisión | Sin trabajo; lote válido; error por campo; excepción de recipiente; sin numerador; multilínea larga; prueba/preview obsoleto/definitivo | Error con destino; acciones según estado; todo dato persiste; no duplicar issue tras fallo. |
| PDF | Una/múltiples páginas; zoom mínimo/máximo; ampliado; prueba/definitivo; hash incorrecto | Marca y contexto siempre visibles; zoom relativo no confundido con escala física. |
| Historial | Vacío/registro/snapshot heredado/reimpresión; PDF ausente/alterado; revisión retirada | Detalle legible, consulta y bloqueo correctos, motivo/origen conservados. |
| Configuración | Todas las categorías; identificador inválido; duplicados; maestro estado sin fuente/pending/vigente; auditoría larga | Sin dock residual; formularios con scroll; no aprobar al seleccionar ni al navegar. |
| Modales | Revisión, variante, recorte, ancla, escala, auxiliares, salida, hoja, calibración, importación, conciliación, R6A/R6B | Contenido y cierre/confirmación dentro del área objetivo; cancelación limpia; botón por defecto seguro. |

### Método de comparación propuesto

Baseline aprobada por plataforma/fuentes/factor, con fixtures y nombres estables. Comparar geometrías, áreas visibles, presencia/estado de acciones y asociación de errores; usar diferencias de imagen con tolerancia de antialiasing solo como detector para revisión humana. Enmascarar únicamente hora/rutas temporales/UID sintéticos, nunca estado documental, cantidades, advertencias o resultados. No convertir una diferencia de píxeles en fallo GMP automático.

En esta auditoría **no** se añade un algoritmo de comparación con golden histórica ni se afirma que las 306 imágenes hayan sido inspeccionadas individualmente. Se revisan manualmente estados representativos y extremos descritos en EVIDENCIAS.md.

## Lagunas que deben cerrar las siguientes fases

- Tests específicos para UX-01/02/06: destino de cada botón de Inspector y ocultación del dock al navegar a los cinco destinos; confirmar retención de datos y diseño.
- Prueba parametrizada de tamaños reales de diálogos y acceso al pie, no solo `resize()` o captura completa de una ventana que se desborda.
- Recorrido por teclado de menús/formularios, foco tras error/cancelación y ausencia de trampas; árbol accesible con UIA/lector Windows. No inferirlo de nombres vacíos o de la suite verde.
- Medir rendimiento de importación/conversión sobre archivos sintéticos grandes; pausa máxima de UI, posibilidad de detener entre archivos, doble clic/reintentos y cierre seguro.
- Revisión manual de cada familia de transición de variantes, aperturas de fuentes/visor externo, selectores SO y todos los modales fuera del recorrido capturado. Inventario fuente ≠ prueba de apertura de todas sus ramas.
- Windows 10/11 1366×768/1920×1080 con 100/125/150 %, fuentes reales, Word/LibreOffice instalado, lectura antigua SQLite y portable completo. CI Windows debe quedar satisfactorio antes de integración conforme a CONTRIBUTING.
- Medidas físicas, papel parcialmente usado, orientación/carga, driver/spooler, duplicado por reintento y aceptación documental por responsables autorizados. Sin impresión ni aprobación automática.

La auditoría se entrega en borrador documental. Ninguna laguna se cierra modificando assertions, ocultando controles o marcando manualmente una prueba como superada.
