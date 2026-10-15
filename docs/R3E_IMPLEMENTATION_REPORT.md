# R3E — Implementación y aceptación técnica

Base: `main` `46314a4b83c51e5cc45cccfce4c50925a59a8bfe`. Rama: `feature/r3e-visual-design-print`. PR #13. Sin merge.

## Comportamiento implementado

**R3E1.** Accesos visibles «+ Nuevo campo» y «Dibujar campo» junto a los elementos. Dibujo mediante rectángulo y confirmación; formulario de identificador, etiqueta, tipo/dibujo, tamaño de fuente, texto fijo, requerido, negrita y bloqueo. Ocho tiradores por campo editable, medidas numéricas, feedback en mm, cuadrícula y snap opcionales. Creación, desplazamiento y redimensionado usan el `LayoutHistory` y la validación existentes. Fuente fija, geometría auxiliar, anclas, selección múltiple y herramientas anteriores conservadas. Revisión aprobada/retirada y variante no DRAFT permanecen protegidas; se ofrece crear/derivar variante mediante el ciclo existente, que puede rechazar revisiones retiradas. Fuente tipográfica: la del motor (Arial o alternativa compatible), sin editar la fuente del maestro.

**R3E2.** Diseñador Qt accesible desde «Formato y emisión» del trabajo. A4/A3/A5/Carta/personalizado 50–1000 mm por lado; orientación; cuadrícula clásica y distribución libre. Plantillas de un número exacto de posiciones, independiente de recipientes/copias; ajuste automático, arrastre, ocho tiradores, medidas de selección, teclado (1 mm; Mayús 0,1 mm), reglas, cuadrícula, snap, alineación/distribución, borrado, undo/redo/restablecer y cancelación. Miniaturas del maestro se escalan proporcionalmente; PDF de prueba con datos del trabajo se abre dentro del diálogo con el visor PyMuPDF multipágina existente. La miniatura del lienzo representa el maestro; el PDF es la comprobación de los datos variables. Campos internos del maestro no se redistribuyen al cambiar una casilla.

**R3E3.** La geometría compartida `sheet_layout` produce las cajas que usa PyMuPDF para prueba, emisión definitiva y calibración. Se conservan selección, numeración, estados integrado/independiente, copias 1–2 y huecos iniciales; las posiciones se repiten en orden entre páginas. El preflight usa la casilla más restrictiva para legibilidad. Aplicar actualiza el trabajo mediante generación/CAS e invalida la vista previa; la emisión definitiva sigue exigiendo vista previa vigente. Reimpresión conserva papel, posiciones, datos y snapshot; solo permite la selección y casilla inicial autorizadas por el contrato previo.

## Persistencia y compatibilidad

- SQLite v4, tablas y triggers sin modificación. Los perfiles históricos A4 conservan su aritmética, orientación, offsets y parámetros; pruebas comparan capacidad/posiciones/paginación con la fórmula original.
- Distribución: `layout_version=1`, `paper`, `layout_mode`, dimensiones personalizadas y `slots` ordenados en mm. Valores de versión/papel/modo/orientación desconocidos, medidas no finitas, colisiones y cajas fuera de límites bloquean el render/aceptación.
- Perfiles nuevos en `layout_profiles/<id>.json`: contrato, generación, fecha, nombre y perfil, hash canónico, bloqueo OS y escritura atómica. Identificadores nuevos en UI conservan los perfiles anteriores. Servicio permite actualizaciones con generación esperada. ZIP de backup incluye perfiles y trabajos; bloqueo de catálogo compartido evita mezclar versiones durante copia.
- Trabajos históricos mantienen envoltura JSON contrato 1. Trabajos con distribución nueva usan contrato 2, que R3D rechaza antes de abrir/escribir. Contrato 2 sin distribución versión 1 se rechaza.
- El snapshot SQL mantiene contrato 1 por la restricción existente de SQLite. En distribuciones nuevas, `design.sheet_layout` incorpora la configuración de salida (sin `start_slot`, cuya variación ya permite el contrato de reimpresión y que se conserva en `profile`) y `design.approved_base_design_sha256` conserva la huella del diseño base aprobado; la huella del snapshot incluye ambos. No se altera el diseño/variante aprobado. El lector R3D compara su diseño sin esta extensión con el snapshot y bloquea su reproducción. Gate con fuente R3D sin modificar verifica ambos rechazos.
- Tkinter actual bloquea trabajos y reimpresiones de formatos nuevos, indicando usar Qt. Los perfiles SQLite siguen limitados a A4 histórico; los formatos nuevos se guardan desde el diseñador.

## Evidencia reproducible

- `tests/test_r3e_layout.py`: 45 casos geométricos y de persistencia, geometría A4 histórica, PDF real en cinco papeles, 1/2/5 posiciones, 1/2 copias, varias páginas y casilla inicial, límites/colisiones, perfiles/CAS/hash/backup, trabajo reabierto y emisión sintética.
- `tests/test_r3e_qt.py`: controles reales, dibujo/creación, guardado/reapertura, ratón sobre tiradores, undo, cancelación y bloqueo de aceptación/documental.
- `main_qt.py --r3e-check <informe.json> --capture <carpeta>`: captura widgets reales con documentos sintéticos, prueba PDF/cajas con tolerancia máxima 0,1 mm, emisión definitiva exclusivamente sintética, snapshot y reimpresión A3.
- CI Qt ejecuta regresiones anteriores y R3E, smoke desde fuente y portable a factores Qt 1 y 1,5, además del gate R3D. Mantiene CI de núcleo/Tk/portable Windows y migración independiente. Resultados y capturas dentro del artefacto `R3E-Qt-Visual-Design-<sha>`, junto al ZIP portable Qt y acompañante Tk.
- Capturas a objetivo físico 1920×1080 y 1366×768. A 150 %, el segundo usa 910×512 unidades lógicas (1365×768 píxeles de widget por redondeo). JSON registra tamaño lógico, DPR y objetivo para no confundir emulación Qt con aceptación en monitor físico Windows. Ventanas pequeñas usan panel de propiedades desplazable; el zoom no modifica mm.
- Matriz original de 87 capacidades conservada íntegra; extensión de trazabilidad en `R3E_PARITY.md`. Los resultados finales sobre HEAD deben consultarse en Actions; no se presupone aprobación de CI.

## Pendientes de aceptación externa

Word real, impresión física al 100 %, hardware COVEX, impresora A3, monitores/Windows 10 y 11 reales, revisión del operador y validación GMP siguen PENDIENTES. El registro 00-R1 no recibe aprobación documental. La emulación 150 % y las pruebas en Windows Server CI no acreditan esas pruebas externas. No se imprimen etiquetas automáticamente ni se despliega a producción.
