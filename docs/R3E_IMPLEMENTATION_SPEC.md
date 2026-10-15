# R3E — Editor visual de campos y diseñador interactivo de hojas

**Estado:** especificación de implementación, todavía sin código funcional ni validación.
**Base obligatoria:** `main` `46314a4b83c51e5cc45cccfce4c50925a59a8bfe` (R3A, B1, B2, B3, C y D integradas).
**PR de desarrollo:** `feature/r3e-visual-design-print`. No hacer merge hasta autorización explícita.

## 0. Problema observado durante UAT
1. En Editor, el botón «Agregar campo» existe pero se encuentra oculto en Ajuste avanzado → Campo; solo permite editar revisiones pendientes o variantes DRAFT. No es evidente para el operador por qué la creación está deshabilitada en versiones aprobadas.
2. En Emisión, ancho/alto, márgenes, separación, casilla inicial y desplazamientos se introducen numéricamente. No hay lienzo interactivo para cuadrar varias etiquetas sobre papel, crear posiciones libres o ajustar con ratón.
3. `engine.py::plan_sheet` está codificado para A4 (210×297 mm) y cuadrícula regular. Las funciones de renderizado, hoja de calibración y textos de UI presuponen A4.
4. `storage.py` ya incluye `profiles.paper`, pero `add_profile()` no conserva ese atributo; los trabajos JSON conservan un `profile` ampliable. `emission_work.parameters()` admite 1–100 copias, mientras `engine.render_emission()` **solo permite 1 o 2**. No permitir «5 etiquetas/hoja» confundirlo con cinco copias/recipiente.
5. Las pruebas A4 y snapshots/reimpresión existentes son contratos obligatorios. Nunca convertir una revisión o variante aprobada en editable directamente.

## 1. UX de Editor — incorporación y transformación de campos
- Mostrar junto a la lista de elementos un botón destacado «+ Nuevo campo» y una acción «Dibujar campo» con explicación del estado. No depender de abrir el acordeón Ajuste avanzado.
- Flujo de dibujo: cursor cruz; arrastrar rectángulo sobre el recorte del maestro; medida inicial en mm, confirmación de rectángulo, formulario compacto (identificador único, etiqueta, tipo de campo, fuente/tamaño, requerido, bloqueo y modo de dibujo); Cancelar deja el diseño intacto.
- Selección, desplazamiento y **redimensionado mediante ocho tiradores** visibles, con ratón; alternativa por panel numérico editable a resolución de 0,1 mm o superior. Soporte de zoom visual separado del tamaño físico. Cuadrícula y snap opcionales.
- Reutilizar `AdvancedEditorMixin`, `LayoutHistory` y la validación de geometría/documento existente, no implementar un segundo editor paralelo. Todas las operaciones del ratón son comandos undo/redo, incluida la creación y el redimensionado.
- Si la revisión es APPROVED o RETIRED, no habilitar mutación sobre ella: explicar motivo y ofrecer «Crear variante editable» o derivar variante, según las transiciones permitidas. Solo editar revisión PENDING o variante DRAFT de revisión no retirada; el usuario confirma la nueva variante y esta comienza sin aprobación documental.
- Campos fijados/bloqueados no se pueden arrastrar ni redimensionar; no recolocar textos, imágenes, tablas o dibujos fijos del PDF maestro. No fingir edición de toda la composición si realmente solo se superponen campos variables; avisar de esa limitación.
- Validar identificadores, colisiones relevantes, recorte, tamaños positivos, límites y legibilidad; conservar anclas, estado, auxiliares, multi-selección y edición avanzada anterior.
- Vista previa actualizada sin registrar aprobación ni emisión. `00-R1` sigue PENDING.

## 2. UX del diseñador de hojas — desde Emisión
- Acción principal «Diseñar hoja…» accesible desde `WorkPanel` / Centro de Emisión, además de conservar todos los controles numéricos actuales para usuarios avanzados.
- Diálogo amplio PySide6 con **papel en escala gráfica** y pestaña o panel de propiedades; paleta Industrial Moderno coherente con R3D, modales de fondo claro, diseño usable a 1366×768 y 150 %.
- Elegir formato A4, A3, A5, Carta y personalizado (ancho/alto explícitos con límites verificables). Vertical/horizontal. No considerar papel disponible en impresora sin prueba física; indicarlo en ayuda.
- Diferenciar tres cifras: «etiquetas distribuidas en cada hoja», «recipientes del trabajo» y «copias por recipiente». Plantillas de 1, 2, 4, 5, 6... posiciones por hoja y «Ajustar automáticamente». La cantidad física a imprimir sigue procediendo del trabajo y de su selección.
- Dos modos de composición distintos y explícitos:
  1. **Cuadrícula clásica:** motor A4 heredado como comportamiento idéntico para perfiles existentes; filas/columnas, margen, separación y casilla inicial automáticos.
  2. **Distribución libre:** lista ordenada de posiciones por hoja con coordenadas X/Y y ancho/alto en mm, arrastre de cada caja, tiradores, guías, reglas, snap, centrar/alinear/distribuir, selección y borrado controlado; se pueden crear cinco cajas donde al operador le convenga.
- La vista previa de cajas representa las **casillas físicas** y no equivale al redimensionado arbitrario de los campos internos. Por defecto el contenido maestro se escala proporcionalmente dentro de cada caja, sin distorsión ni alteración del maestro. Mostrar tamaño efectivo y escala. No cambiar tipo de papel solo en la UI sin que el PDF lo refleje.
- Las cajas no pueden solaparse accidentalmente ni salir de la hoja o área imprimible definida. Ante límites/colisiones, bloquear aceptación o señalar explícitamente cada infracción. Zoom del lienzo no cambia milímetros.
- Movimiento por teclado y cuadro de medidas; feedback numérico en mm durante drag/resize; botones Deshacer, Rehacer, Restablecer y Cancelar. Vista A4/A3 proporcional con miniaturas y PDF de prueba real; no sustituir verificación PDF por simple dibujo de cajas.
- «Aplicar al trabajo» actualiza el `profile` del trabajo mediante su repositorio con control de generación. Guardar un borrador no emite. Se puede guardar un **perfil reutilizable** con identificador, nombre y evidencia de edición, sin modificar revisiones/variantes documentales.
- Una distribución libre de cinco posiciones se repite determinísticamente en páginas sucesivas para trabajos mayores. Precisa numeración, copias, selección de recipientes y huecos libres de la primera hoja; no generar copias adicionales ficticias por definir cinco posiciones.

## 3. Diseño técnico y compatibilidad (decisiones preferidas)
- Definir **un único planificador geométrico** compartido entre el lienzo y PyMuPDF, p.ej. `PaperSpec`, `LayoutSlot`, `SheetLayout`, con conversión mm↔puntos PDF y mm↔píxeles de vista; fuente única de verdad para posiciones, tamaños, número de páginas y margen.
- Modelo JSON tipado/versionado para nuevas opciones en `work.profile`, manteniendo como default `paper=A4` y `layout_mode=grid` para trabajos existentes. Validación estricta y fail-closed de valores desconocidos.
- Preferir **sin cambio de SQLite v4**. Se admite almacenar configuraciones complejas de perfiles en `data/layout_profiles/` mediante un servicio explícito que implemente escritura atómica, versión, hash de integridad y bloqueo de concurrencia. Reutilizar perfiles SQLite existentes, incluidos los perfiles A4. No reutilizar `profiles.paper` como prueba falsa de compatibilidad si `add_profile` lo descarta. Estas configuraciones deben incluirse en backups ZIP y recuperación. Si la propuesta exige migración de esquema, detenerla y presentar un diseño de migración/reversión para aprobación, sin aplicarla a datos reales.
- Preservar **exactamente** la ruta de render A4/cuadrícula de perfiles históricos o demostrar paridad geométrica antes de centralizarla. No cambiar silenciosamente parámetros A4 guardados. A3/A5/Carta/libre solo en rutas explícitamente compatibles.
- No abrir ni escribir un nuevo perfil libre/A3 desde Tkinter/EXE antiguo mediante un fallback a A4: bloquear de forma comprensible o usar únicamente el visor/servicio nativo y las rutas antiguas soportadas. Mantener acompañante Tkinter para D14/I02.
- Reimpresión: conservar huella, revisión/variante, papel, geometría/slots, datos, numeración original y PDF de procedencia. No permitir un layout diferente en reimpresión ni sobreescribir históricos sin snapshot. Las selecciones permitidas y el tratamiento de huecos deben ser deterministas y auditables.
- Normalizar en preflight el límite de **1–2 copias por recipiente** entre `emission_work`, motor y Qt salvo requerimiento independiente/justificado para modificarlo. «5 etiquetas por hoja» no cambia este límite.
- Conservar `WorkRepository`, `emission_contract`, snapshots, verificación de integridad PDF, bloqueo de repetición, `source_documents` originales, variantes inmutables y límites de seguridad del motor. PDFs de prueba siempre marcados; nunca registrar emisión definitiva de PENDING.
- Impresión física seguirá siendo mediante visor del sistema al 100 %, no imprimir silenciosamente. Formato A3 requiere impresora física capaz de A3: prueba posterior específica.

## 4. Entregas / orden en la misma PR
**R3E1:** editor con nuevo campo por botón y dibujo, tiradores de resize, estados, ayudas, undo/redo y pruebas sintéticas.

**R3E2:** planificador compartido A4/A3/A5/Carta/custom, 1/5 posiciones por hoja, vista interactiva QGraphicsScene, cuadrícula heredada y distribución libre, perfiles persistentes y tests geométricos.

**R3E3:** conexión con `WorkPanel`, previsualización PyMuPDF real, emisión de prueba y definitiva, historial/reimpresión coherentes, UX compacta y controles Windows. No iniciar fases posteriores.

Separar en commits reconocibles, **sin merge**, sin modificar datos reales y sin usar Word/etiquetas reales en repositorio.

## 5. Pruebas de aceptación obligatorias
1. Crear nuevo campo en revisión PENDING y variante DRAFT por botón y por ratón; guardar/reabrir; claves duplicadas bloqueadas; ratón mueve/redimensiona dentro de recorte; undo/redo; locked, APPROVED/RETIRED no editables; ofrecer derivación sin aprobar.
2. A4 histórico produce mismas dimensiones, posiciones, páginas y recuentos. Ensayar 1, 2 y **5 etiquetas distribuidas por hoja** con distintas cantidades reales de recipientes; más de una página; casilla inicial; cambio de copias 1/2; seleccionar rangos; comportamiento de estado integrado/independiente.
3. A3/A5/Carta/custom: `page.rect` PDF exacto en mm, margen, seguridad, sin fuera-de-página ni solapes; arrastrar y redimensionar en QGraphicsView modifica el PDF de prueba con error máximo 0,1 mm en cajas (no solo una imagen mock).
4. Escalado proporcional sin distorsión, textos largos, fuentes, recorte y advertencias de legibilidad; prueba marcada e integridad de snapshots definitivos. Verificar pdf preview antes de emitir.
5. Persistencia del trabajo después de reinicio/cierre, perfiles guardados y reapertura, concurrencia/conflicto, cancelación sin cambios, backup/restore sintéticos; fail-closed de formato no soportado en puente Tk.
6. Reimpresión en formato nuevo conserva geometría, datos/recipientes originales y motivo; histórico antiguo sin snapshot mantiene advertencia.
7. Tests Windows PySide6 reales: captura Editor nuevo campo, campo redimensionado, papel A4 con 1 y 5, A3 libre, alineación, PDF de prueba, error fuera de límites y ventana compacta 1366×768/150 %; también 1920×1080/100 % y tema oscuro con diálogos claros.
8. Matriz de **87 capacidades**, sin desaparición de botones heredados; CI Qt/núcleo/Windows/migración satisfactorias. Las suites existentes deben permanecer sin saltarse ni borrar pruebas por conveniencia.
9. Word real, impresión física, hardware COVEX, Windows 10/11 reales y validación GMP siguen PENDIENTES. Registro `00-R1` continúa pendiente documental.

## 6. Entrega y recursos
- Aprovechar el código actual en `qt_ui/advanced_editor.py`, `qt_ui/variants.py`, `qt_ui/work.py`, `qt_ui/emission_centre.py`, `engine.py`, `emission_contract.py`, `storage.py`.
- Al comenzar: revisar la implementación exacta y comparar con este contrato; corregir solo desviaciones demostradas; preferir cambios localizados frente a reescribir el sistema.
- Evitar CI completa por cada cambio pequeño: tests locales/dirigidos durante E1/E2; CI Windows completa sobre último commit y cuando sea necesario. No declarar verde sin resultados sobre HEAD.
- Entregar PR (puede continuar esta misma rama/PR), artefactos portables Windows, capturas sintéticas, matriz de paridad y lista de riesgos/pendientes para aceptación.
- **Prohibido squash/merge, despliegue productivo, datos reales, conectores o R4 sin autorización expresa.**
