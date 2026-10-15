# R3C · Paridad Qt/Tk y aceptación

Base: main `86475779b1eac6f39c9098e0e9d67dd2de51d5fe`. Rama
`feature/r3c-native-emission`. R3A/B1/B2/B3 integradas, R3C sujeto a revisión.
Solo datos sintéticos. No se modifica SQLite v4 ni el motor PDF.

## Funciones de emisión completamente nativas

| Bloque | Qt | Contrato compartido / compatibilidad |
|---|---|---|
| Selección | Revisión, variante y nombre al crear; abrir/copiar/recuperar trabajo | WorkRepository; identidad y generación independientes, sin heredar emisión |
| Datos | Lote multilínea, tabla por recipiente, herencia de vacíos, limpiar fila por menú contextual, pegado Excel | Mismos valores y validador PN/PB; autoguardado CAS, anterior copia recuperable |
| Formato | Cantidad/copias/rangos, tamaño proporcional/restaurar diseño, orientación A4, margen, separación, desplazamientos, seguridad, casilla inicial, marcas e impresora de referencia | Perfiles reutilizables; configuración de impresión separada de geometría documental |
| Estado de material | Sin estado/sin analizar/aprobado/rechazado, fecha/responsable/condiciones, integrada/independiente | Maestros aprobados íntegros; aprobar material no es aprobar documento |
| Vista previa | PDF real con datos del trabajo, páginas, ajuste/zoom y visor externo | Misma composición del motor, prueba marcada; geometría/textos comparados con definitivo |
| Borrador/prueba/emisión | Tres acciones diferentes; prueba exportable sin historial; confirmación expresa de definitivo | WorkRepository.issue → emission_contract → restricciones SQLite; ninguna emisión alternativa |
| Historial | Búsqueda, tabla, resumen documental, datos de lote/recipientes, formato y estado; PDF verificado | PDF generado e impresión física diferenciados |
| Reimpresión | Rangos originales, motivo, prueba, casilla inicial y confirmación; datos/diseño/copias conservados | HistoryService común Qt/Tk; fingerprint de origen y revalidación en transacción |
| Integridad | Bloqueo por PDF/snapshot alterado, retirada, identidad/aprobación incompatible, estados obsoletos | Hash de PDF, diseño, fuente y evidencia; histórico NULL mantiene advertencia expresa |
| Recuperación | Reinicio, conflicto visible sin borrar pantalla, recuperar intento o copia anterior | DRAFT/EMITTING/ISSUED existentes; reconciliación posterior a commit, sin reemitir automáticamente |

En Qt se puede preparar, emitir, consultar y reimprimir sin lanzar ni importar
Tkinter. El acompañante continúa distribuido para las funciones siguientes.

## Funciones que todavía requieren Tkinter

- Comparador básico de imágenes entre revisiones (D14); la comparación documental
  revisión/variante ya existe en Qt y se mantiene.
- Importación por carpeta con progreso/cancelación (I02). La importación individual
  Qt se conserva; Word sigue requiriendo su conversor local y prueba real.
- Configuración de operador y ubicación de datos, backup, catálogo CM y duplicados,
  aprobación/revisión de maestros de estado, auditoría local y recuentos del Inicio
  heredado (C01–C07/C10 y aprobación de M11).
- Editor anterior, emisión e historial anteriores permanecen como compatibilidad;
  ya no son obligatorios para los flujos nativos enumerados arriba.

Se conservan los accesos existentes de Biblioteca/Editor, el puente con bloqueo de
mutaciones mientras está abierto y las pruebas de ida/vuelta de R3B3. Restaurar
ZIP sigue siendo un procedimiento con aplicaciones cerradas/CLI, no una nueva UI.

## Criterios de aceptación verificables

1. Borrador y prueba no añaden issues; definitivo exige vista previa actual, datos
   válidos y confirmación. Una cancelación no modifica historial.
2. Toda emisión nueva tiene snapshot válido; sin variante también. Históricos NULL
   no se completan retrospectivamente. Snapshot y números originales en reimpresión.
3. Datos extensos y pesos incoherentes impiden definitivo, con avisos de campo.
   Estado/variante pendiente permiten únicamente prueba; retirada bloquea generación.
4. Edición concurrente conserva la pantalla; generación/documentación obsoleta o
   PDF de vista previa alterado impiden confirmar. Commit interrumpido se reconcilia.
5. Fallo de registro de reimpresión no se presenta como éxito; se elimina su PDF
   nuevo si el sistema de archivos lo permite. Un fallo de trabajo conserva EMITTING.
6. Fuentes y textos fijos intactos, esquema v4 idéntico, 00-R1 PENDING. Las 87 IDs
   permanecen: 66 Qt, 4 parciales, 10 anteriores y 7 motor (ver matriz).
7. Capturas de Qt real con fixtures sintéticos y smoke nativo a 100/125/150 %,
   1920×1080 y 1366×768; prueba del portable compilado sin dependencia Tk nativa.

## Evidencias reproducibles

- `tests/test_r3c_emission_qt.py`: prueba/exportación, cancelación, emisión,
  snapshot, duplicación, conflicto después del diálogo, preview alterada y textos largos.
- `tests/test_r3c_history.py`, `test_r3c_history_qt.py`: historial, prueba/reimpresión,
  números/datos/snapshot, motivo, retirada, corrupción, concurrencia y fallo de inserción.
- `tests/test_emission_work*.py`: persistencia, backup/restauración, muerte real de
  procesos y reconciliación, Qt/Tk, compatibilidad, estados documentales.
- Suites previas de variantes, geometría, fuentes, consentimiento y migración;
  barrera storage_v4 y EXE anteriores comprobados por el gate Windows conservado.
- `main_qt.py --self-check informe.json`: 80 controles anteriores adaptados únicamente
  a navegación ahora nativa. `--emission-check informe.json --capture carpeta`:
  32 controles de base y controles compactos adicionales, geometría del texto de trabajo entre prueba/definitivo,
  snapshots, reinicio, conflictos, historial, reimpresión y ausencia de importación Tk.
- Workflow Qt conserva pruebas de variantes y puente R3B3; compila Qt y acompañante
  una vez, comprueba el portable y entrega ZIP, JSON, XML y capturas. Resultado CI
  y enlace al artefacto se registran en la PR; no se atribuye éxito a un job pendiente.

Pruebas locales completas previas al ajuste compacto: 201 pasan, 4 omitidas por dependencias/plataforma; 80
controles de interacción y 32–34 nativos pasan en Linux offscreen. Se añade además reconciliación de reimpresión tras fallo posterior al commit. Windows se valida
por CI en el commit entregado y sus resultados prevalecen para el portable.

Pendientes externos: Word/Office real, impresión física y reglas/calibración en
impresora, Windows 10/11 y equipos COVEX, aceptación operativa y validación GMP.
No se afirma impresión realizada, firma electrónica ni auditoría inviolable.
Sin R4/R5 ni Business Central/SharePoint.

Ajuste de aceptación visual: en ventanas de poca altura se alternan datos/PDF, con
resumen y acciones siempre visibles, scroll de los formularios y PDF ampliable.
Se verifica una altura útil de vista previa, además de los límites de ventana.
Las comparaciones de texto extraído normalizan el guion discrecional de las fuentes
Windows y los espacios inseparables; los textos y el motor PDF no cambian.
La CI comparte cobertura: núcleo/Tk en su job, Qt/consentimiento en el suyo, sin
ejecutar por duplicado toda la regresión del núcleo con PySide6 instalado.
