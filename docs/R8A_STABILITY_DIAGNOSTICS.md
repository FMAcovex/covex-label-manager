# R8A — Estabilidad, diagnóstico y fiabilidad

Base auditada: `main` en `6ba8fa7d7e8409d5d6e33d206ccb39ab8c2cbd01` (R7B-AC1 integrado).
Implementación limitada; sin cambio de framework, migración ni reorganización visual R8B/C/D.
La entrega y sus resultados exactos se registran en la PR R8A, no constituyen aceptación GMP.

## R8A1 — Auditoría y evidencia

No se dispone de un volcado del cierre intermitente observado por el usuario. **No se
ha establecido una causa única de esos cierres.** Los defectos de abajo se identifican
por código y regresiones; no se atribuye retrospectivamente el incidente a ninguno.

| ID | Clasificación / prioridad | Evidencia y consecuencia | Intervención y regresión |
| --- | --- | --- | --- |
| ST-01 | Defecto demostrado / alta | `StatusFieldsDialog.geometry` oculta `QWidget.geometry()`. El antecedente R7B-AC1 ocultaba `layout()`; no son prueba de un mismo fallo nativo. | `geometry_note`; prueba de métodos invocables y análisis estático. |
| ST-02 | Defectos demostrados / media | Otros atributos ocultan `QWidget.rect/actions/window` en recorte, importador, WorkPanel y navegador documental. | `selection_rect`, `row_actions`, `controller`; mismos controles, acciones y criterios. |
| ST-03 | Riesgo de vida C++ fundamentado / alta | Soltar un `EditorFieldItem/ResizeHandle` ejecuta `drag_finished → command → draw_editor → scene.clear` dentro de su propio evento nativo. El objeto se elimina antes de retornar. No se afirma haber reproducido un crash por ello. | Se confirma geometría inmediatamente, pero el redibujado se difiere mediante temporizador propiedad del controlador. Prueba exige objeto vivo al retornar y eliminado tras procesar eventos. Undo/redo y guardado se conservan. |
| ST-04 | Defecto demostrado / alta | Salir del editor de campos de estado descarta cambios, incluidas propiedades todavía no aplicadas, sin advertencia. | Guardar/Descartar/Cancelar por `reject` (también Escape/X); guardar fallido mantiene el candidato. |
| ST-05 | Defecto demostrado / alta | Dos diálogos abiertos sobre un mismo DRAFT pueden guardar sucesivamente y sobrescribir el primero. | Comparación de hash esperado dentro de `BEGIN IMMEDIATE`, antes del UPDATE. Sin cambio de esquema. Conflicto explícito, sin sobrescritura ni aprobación. |
| ST-06 | Riesgo fundamentado / alta | `QApplication.quit` no equivale a `closeEvent`: el finally podía cerrar sesión sin drenar PreviewTask. | Finalización explícita: detener timers, solicitar cancelación, esperar al trabajador con límite, guardar trabajo antes de liberar servicios. No destruir QThread activo. |
| ST-07 | Riesgo de reentrada demostrado por prueba / alta | `emission_busy` procesa eventos mientras hay una operación síncrona; era posible solicitar cierre durante una emisión. | Se rechaza el cierre mientras `native_busy`, sin terminar escritores. |
| ST-08 | Riesgo fundamentado / media | `fitInView` sin políticas de scrollbar estables en los lienzos nuevos de estado puede reentrar durante resize nativo. | Reutilizar Preview y su guardia de ajuste existente, sin cambiar el compositor PDF ni la estética. |
| ST-09 | Deficiencia demostrada / media | Fallo de borrado de temporales puede ocultar el resultado del trabajador o escapar de un callback Qt. Vistas previas automáticas invalidadas acumulaban PDF temporales. | Limpieza tolerante a OSError con registro técnico; descartar exclusivamente el PDF automático propio en cache, nunca un maestro/emisión/exportación. |
| ST-10 | Deficiencia demostrada / alta | No había diagnóstico transversal ni indicación de sesión sin cierre normal. | Registros privados limitados, hooks, marcador, eventos de operación y exportación desde Configuración. |
| ST-11 | Hipótesis no confirmada | Antivirus, impresora, Word, controlador gráfico, fallo del sistema/energía o interacción no cubierta. | Recoger informe técnico y contexto mínimo; no desactivar defensas ni modificar documentos por suposición. |

### Componentes revisados y decisiones de conservación

- `main_qt.py`: QApplication, excepciones, bucle, sesión y cierre; coordinador de finalización añadido.
- `functional/window/workspace`: MRO, navegación, propiedades QObject y reparenting. Se conserva la composición existente, sin reescritura.
- `advanced_editor/status_fields_dialog/resize_item/status_crop_dialog`: escenas, arrastre, selección, callbacks y métodos Qt. No se modifica la geometría documental aprobada.
- `emission_centre/preview_task/preview_render`: proceso PDF separado, token/generación/serie, timer de debounce, limpieza, rechazo de resultados obsoletos. MuPDF y SQLite no se comparten entre hilos.
- `work/emission_work`: guardado atómico, CAS de generación, copia previa, EMITTING/ISSUED y reconciliación de operación. Se mantienen los contratos y pruebas existentes de interrupción antes/después del commit y prohibición de repetición silenciosa.
- `variants/status_manager/status_catalog/status_combined`: guardas documentales, transacciones y evidencias. Solo se añade precondición optimista al guardado del DRAFT de estado.
- `storage/schema_v4/migration_v4`: SQLite v4, transacciones, backup y escritor anterior. No se ha demostrado necesidad de migración: **ninguna migración nueva**.
- `qt_legacy`: proceso separado, protocolo 4 y bloqueo de mutaciones Qt hasta terminar. No se mata un proceso documental; el cierre normal exige cerrar Tk primero.
- PyInstaller/workflows: mismos locks verificados, pruebas source/frozen, inventario/CRC/SHA-256; prueba adicional del ZIP realmente extraído. La descarga Qt de aceptación no contiene capturas/informes; evidencias aparte.

### Historial de CI

Se consultaron ejecuciones y jobs anteriores, incluida la Qt fallida `39125175332`
(commit `0bca139`, fallo del job de regresión Qt) y la corrección posterior
`205e299` de `layout`, seguida de la Qt verde `39125930746` (`ea1a605`).
La consulta `gh run view --log-failed` de la ejecución fallida no devolvió contenido
en este entorno; no se inventa una excepción a partir de ese resultado.
La explicación del antecedente procede del cambio de código R7B-AC1, no de un
traceback recuperado. La base `6ba8fa7` tenía CI de núcleo verde `39130321879`.

## R8A2 — Tareas y protección de datos

La vista previa sigue siendo **no productiva**, en un proceso independiente. El
QThread solo espera su resultado. La cancelación es cooperativa: si el proceso ya
está calculando, se deja terminar y se descarta su salida; no interrumpe una emisión.
El subprocess conserva timeout de 90 s. El cierre normal durante vista previa
mantiene la ventana viva y permite reintentar al finalizar. La finalización del
runtime tiene espera máxima de 95 s para el trabajador y no libera SQLite si este
sigue activo. La interfaz no espera bloqueada durante el cierre normal rechazado.
No existe terminación forzada de Tk, Word o procesos de escritura documental.

Al cerrar se conserva el autoguardado del trabajo; un fallo de guardado impide el
cierre normal y mantiene los datos en pantalla. El diseño conserva guardado
explícito. Cancelar un cierre no debe dejar desactivada la actualización automática.
No se promete recuperar un diseño no guardado tras un corte nativo/eléctrico.

Se mantienen preflight, hash del PDF, revisión/token actual, confirmación definitiva,
snapshot, intención persistida, reconciliación, auditoría, historial y reimpresión.
Un ZIP técnico no es un backup documental ni una autorización de recuperación.
No se restauran datos controlados automáticamente.

## R8A3 — Diagnóstico local y privacidad

Configuración → Resumen → **Exportar informe de diagnóstico…**.

Ubicación normal: `diagnostics/` dentro de la carpeta de datos configurada. Si no
es escribible: `%LOCALAPPDATA%/COVEXLabelManager/diagnostics/<clave-opaca>/` en
Windows (fallback local equivalente en Linux). No requiere escribir en el ejecutable.

- Identificador aleatorio de sesión; versión, fase, Python, Qt, arquitectura,
  sistema, condición frozen y commit del BUILD_MANIFEST cuando está disponible.
- `technical.jsonl`: eventos técnicos con esquema cerrado; 256 KiB por archivo,
  tres respaldos rotativos (aprox. 1 MiB total), hasta 16 marcadores de sesión.
- Hooks de excepción principal y `threading`; fallos de PreviewTask y procesos
  reflejados por código de salida/estado; eventos Qt critical/fatal sin su texto.
- Inicio/cierre normal y marcador de sesión no finalizada. Puede significar corte,
  cierre forzado, otra instancia o un fallo; **no se etiqueta automáticamente como crash**.
- Navegación/editor, inicio/fin de vista previa, salida obsoleta/cancelada, errores
  operativos y cierre bloqueado. No se registran nombres ni identidades documentales.
- Errores Python: categoría fija y archivo relativo/línea del paquete, **nunca**
  mensaje, traceback bruto, código fuente, variables locales ni excepciones encadenadas.
- ZIP: estado técnico y logs conocidos, no búsqueda recursiva de DATA; excluye
  symlinks, revalida campos al exportar, escritura temporal + reemplazo atómico.
  No incluye SQLite, documentos, lotes, clientes, operador, fuentes, historial,
  instantáneas, tokens, argumentos de proceso ni rutas corporativas completas.
- Mensaje no modal y limitado en frecuencia ante excepción no controlada. No
  presenta un traceback al operador ni afirma que la operación haya sido exitosa.

### Límites del diagnóstico nativo

Se mantiene `-X faulthandler` en CI **exclusivamente sintética**. No se activa un
volcado bruto automático en instalaciones reales: puede contener rutas/identificadores
que incumplan la minimización solicitada. Los eventos Qt fatal/critical pueden dejar
una señal técnica, pero no garantizan capturar access violations, aborts, apagados o
fallos del sistema. Un fallo nativo puede dejar solo el marcador sin cierre.
El registro Aplicación de Windows/Historial de confiabilidad puede aportar código
y módulo; su recogida requiere revisar/redactar datos personales y rutas, y no se
incluye automáticamente en el ZIP. No se promete captura universal mediante Python.

## R8A4 — Regresión y estabilidad

| Cobertura solicitada | Verificación |
| --- | --- |
| Inicio/cierre y portable extraído | `--stability-check`, QApplication real, ejecutado desde el ZIP extraído en Windows CI. |
| Editor y navegación repetidos | 8 ciclos rápidos, 6 módulos/ciclo, 2 resoluciones, guardado/selección y diálogo de estado por ciclo. |
| Campos: crear/mover/redimensionar | Interacciones nativas R7B-AC1 existentes + regresiones R8A de vida de objetos y recorrido sintético. |
| Previas al modificar/cambiar trabajo | Pruebas R6B existentes y verificación de PDF final tras descartar datos obsoletos. |
| Cierre durante previa y operación ocupada | Ventana permanece abierta, espera/cancelación del trabajador, conexión SQLite válida. |
| Cancelación | Antes del lanzamiento: ningún proceso; durante cálculo: descartar salida sin tocar registros. |
| Recuperación y concurrencia | Trabajo persistido/reabierto, generación obsoleta rechazada, dos editores de estado enfrentados. |
| Estados e historial | Emisión sintética independiente y pruebas R7A/B existentes de PDF/snapshot/reimpresión/combinada. |
| SQLite e interrupciones | `integrity_check` de ambos catálogos, `foreign_key_check`, suites existentes de emisión y migración con interrupción controlada. |
| Diagnóstico y exportación | Hooks, sesiones incompletas, límites/rotación, fallback escribible, datos sensibles sintéticos, symlink y archivo alterado. |

Pruebas rápidas obligatorias: `tests/test_r8a_diagnostics.py` y
`tests/test_r8a_stability_qt.py`; se ejecutan antes de la suite Qt completa.
Recorrido source y portable extraído con escalas 100/125/150 %, en tamaños lógicos
calculados desde 1366×768 y 1920×1080 (mismo margen de escritorio del gate existente).
El gate visual existente conserva todas sus capturas y aserciones.

Estrés prolongado opcional, independiente de las pruebas rápidas:

```text
COVEXLabelManager_Qt.exe --stability-check informe-sintetico.json --stability-rounds 20
```

40 ciclos en total; límite configurable de 100 rondas/resolución y watchdog global
de 120 s. El resultado debe tener `ok=true`, integridad y todas las condiciones;
salida sin informe, timeout o excepción son fallo, nunca éxito por defecto. La espera
de render depende de un predicado comprobable, no de un retardo fijo de aceptación.

El criterio cubierto es cero cierres inesperados/pérdidas en estos escenarios, **no
una garantía absoluta ante fallos intermitentes no reproducidos**. CI verde y portable
íntegro no acreditan Word real, impresión física, Windows 10/11 en equipos COVEX,
aceptación de usuario ni validación GMP.

## Conservación y siguientes fases

Las 87 capacidades históricas no se retiran; se conservan también las ampliaciones
R7A/B/AC1: estados independientes/combinados, Biblioteca integrada y editor visual.
No cambian SQLite v4, originales, revisiones aprobadas, restricciones de aprobación,
identificadores, motor PDF, formato de hoja, auditoría, historial o recuperaciones.
La matriz histórica sigue en `docs/FUNCTIONAL_PRESERVATION_MATRIX.md` y la conciliación
UX en `docs/R6B_UX_INTEGRATED/CONSERVACION_87.md`; R8A no redefine su significado GMP.

R8B: reorganización del Editor; R8C: tipografía/color/alineación/escalado de estados;
R8D: asistentes básicos. No se desarrollan aquí.

### Aceptación manual mínima (solo datos sintéticos)

1. Abrir/cerrar repetidamente Editor y campos de estado, mover/redimensionar y
   comprobar Guardar/Descartar/Cancelar, también con X/Escape.
2. Cambiar datos durante vista previa, cerrar mientras calcula y reabrir el trabajo;
   comprobar que se recupera la última generación guardada y no aparece emisión extra.
3. Exportar diagnóstico desde Configuración. Si se produce un cierre inesperado,
   reabrir, exportar y comunicar hora aproximada/módulo/acción, sin documentos reales.

PR en borrador, sin merge ni squash; aceptación del propietario pendiente.
