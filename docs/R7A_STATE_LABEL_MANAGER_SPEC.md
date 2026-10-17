# R7A — Gestor de etiquetas de estado | Especificación de implementación

**Proyecto:** COVEX Label Manager (PySide6, portable Windows, almacenamiento local SQLite).  
**Repositorio:** `FMAcovex/covex-label-manager`.  
**Base inicial verificada:** `main` `a18363890a1535906348a652e59d866e7122ab05` (PR #29 fusionada).  
**Naturaleza de este documento:** especificación para desarrollo; **no representa funcionalidad implementada, aprobación documental, validación GMP ni aceptación de impresión física**.  
**Nombre de hito:** R7A. Se mantiene R6C reservado al cierre de aceptación definido en `docs/R6_ACCEPTANCE_PROTOCOL.md`.

## 1. Objetivo y alcance

Crear un **Gestor de etiquetas de estado** nativo en PySide6, coherente con la estética Industrial Moderno, con tres clases: **Sin analizar** (`sin_analizar`), **Aprobado** (`aprobado`) y **Rechazado** (`rechazado`).

El usuario debe poder:
1. Importar **Word (`.docx`) o PDF** de origen autorizado y sus revisiones, **desde archivos locales**, individualmente o desde **un documento común que contenga varios estados**.
2. Reconocer/seleccionar estado, página y recorte de cada etiqueta con **previsualización real y confirmación manual**. No deducir vigencia del nombre del archivo ni aprobar automáticamente.
3. Configurar tamaño, proporción, zonas, campos variables y su posición mediante un **editor gráfico** reutilizando herramientas Qt existentes, sin alterar elementos fijos de un original aprobado.
4. Crear **borradores y nuevas revisiones**, consultar historial, comparar diseños y **registrar aprobación documental externa** solo con referencia y verificación explícita. La app no constituye sistema de aprobación GMP ni simula firma electrónica.
5. Emitir las etiquetas de estado como **integradas** en la etiqueta principal o **independientes**, conservando los controles documentales de emisión y las reimpresiones históricas.
6. Identificar de forma clara qué versión está vigente, pendiente, retirada, no disponible o afectada por fallos de integridad.

**No introducir en GitHub:** Word/PDF corporativos, diseños reales, datos de producto, referencias privadas, bases SQLite de usuario, emisiones reales, capturas con información de producción. Usar solo documentos sintéticos en tests/CI. La instalación nueva permanece vacía hasta la importación local.

## 2. Estado de partida verificado

- `storage.py`: tabla heredada `status_masters` con **clave primaria `kind`**, una única fila por estado; `status_master(kind)`, `status_masters()`, `approve_status_master()`. La carga opcional de `ESTADOS_MASTER_00.docx/pdf` desde recursos es heredada y **no debe distribuir originales**.
- `geometry.py`: `STATUS_CROPS` y `STATUS_NAMES` son geometrías y denominaciones de la referencia histórica, **no reglas genéricas para nuevos diseños**.
- `engine.py`: `_paint_status()` utiliza coordenadas fijas por clase basadas en el diseño histórico; `_status_settings()` exige estado aprobado e integridad PDF/original en emisión definitiva.
- `qt_ui/settings.py`: permite visualizar los tres maestros y registrar aprobación externa de una revisión pendiente; **no permite importarlos, editarlos o crear nuevas revisiones**.
- Ya existe emisión integrada/independiente, datos de estado, trabajo recuperable, vista previa, aprobación documental de etiquetas de producto, variantes, historial y reimpresión. **Reutilizar, no duplicar**.
- `SQLite v4` y los snapshots históricos existentes deben conservar su lectura. La incorporación de revisiones de estado requerirá una migración aditiva segura y documentada: no reinterpretar ni renumerar las emisiones previas.

## 3. Experiencia de usuario PySide6

### Pantalla «Etiquetas de estado»
Acceso visible desde la navegación (o Configuración si el diseño final justifica esa ubicación), sin acudir a Tkinter. Presentar tres tarjetas/filas con categoría, revisión vigente, estado documental, tamaño, origen, fecha/referencia documental y miniatura.

Acciones:
- **Importar diseño** (Word/PDF); **Nueva revisión**; **Ver original**; **Editar diseño** (solo borrador); **Comparar revisiones**; **Historial**; **Registrar aprobación externa**; **Retirar** (con motivo y confirmación).
- Mensajes y colores no ambiguos: «Sin analizar» es el **tipo de etiqueta**; «Pendiente», «Aprobada documentalmente» y «Retirada» son **estados de revisión de la plantilla**, nunca el estado de calidad del material.
- Acciones bloqueadas deben explicar cómo habilitarlas. No ocultar el historial.

### Asistente de importación
1. Elegir archivo(s) local(es) Word/PDF, verificar extensiones, tamaño razonable, legibilidad y ausencia de conversión parcial. Convertir Word de forma controlada con las dependencias locales existentes y mostrar el PDF resultante; si Word no está disponible, error recuperable, sin aprobación ni alta parcial.
2. Tipo de origen: documento individual por estado o **documento común de dos/tres etiquetas**. Mostrar página completa y dejar escoger por estado **página y rectángulo de recorte**, con zoom y medidas visibles en mm. No asumir siempre los tres recortes históricos.
3. El usuario confirma identidad, revisión documental, fuente, código/identificador si existe, fecha/referencia de autorización externa y observaciones. **No inventar los metadatos ausentes**; no asignar por defecto revisión «00» sin verificar.
4. Vista previa de las tres etiquetas resultantes; advertencia sobre texto demasiado pequeño, recorte incompleto, orientación y posible diferencia Word/PDF. El duplicado de hash o de revisión documental conduce a comparar y decidir explícitamente, no a sobrescribir.
5. Guardar originales y render PDF derivados **en almacenamiento local**, huellas SHA-256 y relaciones estables; confirmar operación de forma transaccional. Si se cancela o falla un paso, no dejar revisión activada ni archivos huérfanos sin trazabilidad.
6. Soportar importar **solo PDF**; si existen Word y PDF autorizados relacionados, vincular ambos y registrar la relación. No exigir un Word inexistente ni tratar un PDF exportado de Word como fuente corporativa autorizada por sí mismo.

### Editor de diseño
- Editor visual para recorte, dimensiones físicas, relación de aspecto, anclaje, alineación, zona de seguridad y previsualización de impresión. Reutilizar R3E y diseñador de hojas.
- Campos variables **configurables para cada diseño/revisión** (p. ej. lote, fecha, persona, caducidad/reanálisis y otros que existan realmente), con etiqueta, clave estable, tipo, obligatoriedad, formato, caja en coordenadas propias del recorte o mm, tamaño/tipografía, ajuste y detección de desbordamientos. No asumir que los tres estados llevan idénticos campos.
- Mostrar claramente el **texto fijo proveniente del documento** frente a **datos variables que completa el usuario**. Los textos, colores, pictogramas y composición fijos aprobados **no se reescriben silenciosamente**.
- Una revisión **aprobada/retirada es inmutable**. Modificar geometría, composición o campos de una plantilla aprobada exige nuevo borrador o variante derivada con motivo y aprobación independiente.
- Previsualización con datos ficticios marcada **PRUEBA – NO APTO PARA USO GMP**. Ajuste proporcional predeterminado y ajuste avanzado opcional; no estirar arbitrariamente un diseño aprobado.

## 4. Modelo de datos y migración

Implementar una **entidad de revisiones de estado** (UID estable, `kind`, `revision`, `state`, referencia/fecha de origen, fichero original, PDF renderizado, hashes, página/recorte, dimensiones, campos JSON, responsable/referencia/fecha de aprobación externa, fecha/motivo de retiro, identidad de antecesor). Añadir índices y restricciones que garanticen **como máximo una revisión vigente aprobada por clase**.

La tabla heredada `status_masters(kind PRIMARY KEY)` **no puede representar varias revisiones**: elegir una migración aditiva a historial nuevo con vista/compatibilidad heredada, o migración estructural segura y probada. Conservar IDs, hashes y referencias previas sin asignar aprobaciones nuevas. Exigir:
- Snapshot SQLite y consentimiento antes de migrar, `PRAGMA foreign_key_check`, versionado del esquema y tests desde v4 con datos ficticios.
- Preservación exacta de originales y derivados, emisiones y reimpresiones; backup/restore con archivos de estados.
- Si la revisión antigua no tiene trazabilidad suficiente, mostrar estado «legado/no conciliado» y bloqueo seguro para nuevas emisiones; **no inventar versión ni referencia de aprobación**.
- No modificar bases de usuario reales en CI, ni guardar maestros corporativos en el ejecutable.
- Si falla migración, no perder v4; registrar causa y proporcionar recuperación.

**Regla crucial:** la selección de una revisión de estado para emitir debe guardar y comprobar la **identidad y huellas exactas de esa revisión**. La aprobación/retiro posterior o cambio de plantilla no puede sustituir silenciosamente el PDF ya previsualizado o emitido.

## 5. Motor, emisión e historial

- Mantener el renderizado de estado heredado solo para maestros cuyo esquema/huella coincidan con el diseño histórico, mientras se migra. Para nuevos diseños implementar renderizado **dirigido por configuración por revisión**: recorte dinámico, posiciones de campos y validaciones, sin `STATUS_CROPS` ni coordenadas globales de `_paint_status()` como supuesto.
- Antes de la emisión final verificar en la misma operación: revisión explícita vigente, aprobación externa registrada, integridad de Word/PDF, campos requeridos, dimensiones, lote/fechas aplicables, perfil, colisiones, vista previa vigente y confirmación. Si se retira la revisión entre vista previa y emisión, bloquear e invalidar la previsualización.
- Los datos de estado **no cambian la disposición de calidad real de un lote**. La impresión de «Aprobado» o «Rechazado» no constituye decisión QA ni operación en ERP/QMS.
- Emisión integrada y separada, hojas A4/A3/A5/Carta/personalizado cuando el diseñador/centro lo admita, perfiles y copias por recipiente, escalado no deformante; respetar las restricciones existentes sobre tamaño y borde.
- Incluir en el snapshot de cada emisión: `status_kind`, UID de revisión de estado, hash del PDF/origen, geometría/configuración, datos de campos, perfil y enlace a emisión. Las reimpresiones reproducen la revisión emitida originalmente; **no usan el maestro actualmente vigente**. Para historial legado no verificable, avisar/bloquear de forma segura, sin reconstrución inventada.

## 6. Reglas de estados documentales

Flujo recomendado: **BORRADOR → PENDIENTE DE APROBACIÓN EXTERNA → VIGENTE**; alternativamente **RETIRADA** o **ANULADA** con motivo y registro. Separar el estado documental de plantilla del tipo `sin_analizar/aprobado/rechazado`.

El registro de aprobación no equivale a firma electrónica: requerir evidencia/referencia externa, fecha, responsable, confirmación de que el documento coincide con la fuente y verificación de integridad. La sustitución de una versión vigente debe ser explícita y transaccional; el histórico anterior queda inmutable y consultable. No permitir dos vigentes para una misma clase, ni borrar aprobados o usados en emisiones.

## 7. Orden de implementación

**R7A1 — Persistencia e importación**  
Modelo de revisiones, migración v4→nuevo esquema, servicios, integridad/backup, importador Word/PDF individual/multietiqueta, selección página/recorte, duplicados. Tests sin UI.

**R7A2 — Interfaz y editor Qt**  
Pantalla de estados, asistente visual, miniaturas, historial/comparador, editor de campos/medidas, borradores, avisos claros, responsividad a 1366×768 y distintos DPI. Sin Tk y sin duplicar motores.

**R7A3 — Control documental, emisión y regresiones**  
Aprobación externa, retiro/reemplazo, render dirigido por revisión, vista previa, bloqueo de fuentes no vigentes, identidad/snapshot en emisión y reimpresión, migración/CI/portable Windows. Pruebas con fuentes sintéticas y manuales reales pendientes.

Puede implementarse en **una PR de código** con commits por bloque, si la validación de esquema y los límites de alcance lo permiten. No hacer squash ni merge sin inspección final y autorización del propietario.

## 8. Pruebas de aceptación obligatorias

1. Importar un PDF individual para cada tipo y un DOCX/PDF común con recortes diferentes; las tres miniaturas representan el recorte realmente elegido.
2. Importar PDF sin Word; vincular Word+PDF cuando existan; error de Word sin conversor no produce alta parcial.
3. Cambiar nombre/código, tamaño, campos y recorte solo en borrador. No se modifica un documento/revisión aprobada.
4. Nueva revisión no sobrescribe la antigua; duplicados de hash y revisión se detectan; consulta y comparación reproducibles.
5. No permitir emisión definitiva desde borrador/pendiente/retirada, archivo corrupto, hash alterado o campos obligatorios inválidos; PDF de prueba claramente marcado.
6. Emisiones de las tres clases correctas, como integrado e independiente; zoom/escala y márgenes sin desbordamientos, campos/fechas por estado.
7. Retirar o sustituir la revisión durante una vista previa invalida la autorización de emisión.
8. La reimpresión conserva exactamente la revisión y datos de estado del histórico aun cuando exista una revisión más nueva; fallar de manera segura si falta snapshot o fichero.
9. Migrar v4 sintética con estados y emisiones previas: backup, hashes, IDs y acceso a histórico intactos; fallo de migración recuperable.
10. No degradar las **87 capacidades** documentadas, las CI de núcleo/migración/Qt, las regresiones Windows, archivo portable con manifiesto CRC/SHA-256, interfaz nativa y puente legado cuando corresponda.
11. Sin originales ni datos reales en repo, logs, capturas, artefactos CI o ZIP. Los documentos reales se incorporan **después y localmente** para UAT con autorización.
12. Impresión física, Word Office real, calibración de medidas, cierre R6C y validación GMP **permanecen pendientes** aunque todos los tests sintéticos pasen.

## 9. Fuera de alcance

Sincronización directa SharePoint/ERP, aprobación o cambio real del estado QA del material, impresión que constituya firma electrónica, reconocimiento OCR del texto fijo, generación automática de diseños corporativos, edición libre de textos legales de revisiones aprobadas, datos reales en GitHub, permisos multiusuario y validación GMP automática.

## 10. Criterio de entrega

Entregar PR de código **en borrador** y portable Windows verificable, con informe por bloques, lista de archivos modificados, migración y reversibilidad, evidencia de las CI, pruebas Qt/sintéticas, guía de uso con documentos reales solo en estación autorizada y matriz de conservación funcional. Solicitar aceptación visual/pruebas reales antes de fusión. El estado de desarrollo no debe confundirse con autorización documental o validación de uso productivo.
