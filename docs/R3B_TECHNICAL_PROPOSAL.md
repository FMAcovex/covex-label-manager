# R3B — Propuesta técnica para revisión
Fecha: 11/10/2026. Base inspeccionada: main `5d27de30ce98ee89f17485225e3a45b92f544484`, squash de PR #4. **Solo planificación; ninguna fase R3B implementada.**

## 1. Estado real del Editor
Se revisaron `qt_ui/functional.py`, `qt_ui/window.py`, `gui.py:AdvancedEditor`, `services.py`, `geometry.py`, `engine.py`, `storage.py`, `qt_legacy.py`, `qt_transition.py`, ARCHITECTURE y la matriz de conservación.

| Capacidad | Estado en main |
|---|---|
| Seleccionar campos en lista/lienzo; arrastrar y bloquear posición | Nativa Qt. |
| Posición y dimensiones en mm; nombre, identificador, origen del dato, fuente, negrita y obligatoriedad | Nativa Qt para campos variables. |
| Agregar, quitar y restablecer campos; guardar configuración pendiente | Nativa Qt; guardado explícito, validación de límites/identificadores y comprobación de cambios externos en campos. |
| Zoom, ajuste del lienzo, navegación conservando edición; vigente/retirada solo lectura | Nativa Qt. El porcentaje describe visualización, no escala física. |
| Recorte visual/numérico; anclaje a texto; relocalización; zona de estado | Tkinter AdvancedEditor y servicios existentes. |
| Formato físico, escalado proporcional de salida, seguridad y perfiles | Motor existente y pantallas Tkinter; los accesos Qt abren la versión anterior. |
| Alineación geométrica múltiple, distribución, deshacer/rehacer | Ampliaciones nuevas; no son funcionalidades completas ya migradas. |
| Datos de emisión recuperables al cerrar; sincronización Editor–Emisión | No existen todavía. Retener una vista durante la sesión no equivale a persistir trabajos. |

La matriz conserva **87 filas** (33 Qt, 7 parciales, 40 anteriores y 7 motor). Es la línea base R3A, no evidencia de Editor completo. Su redacción histórica de aceptación pendiente no anula la aprobación e integración posterior; en cada PR R3B se actualizarán evidencias de las filas afectadas, conservando sus IDs y sin cambiar clasificaciones por intención.

## 2. R3B1: herramientas avanzadas nativas
Mantener la composición Industrial Moderno, lienzo central y propiedades contextuales. Propuesta de cuatro secciones plegables: **Documento** (recorte y referencias), **Campo** (geometría y tipografía), **Composición** (alineación y escala) y **Estado y límites**. Barra breve de deshacer/rehacer; selección visible y herramientas deshabilitadas según contexto.

Migrar recorte visual con coordenadas exactas y previsualización antes/después, usando `master_preview` y `rebase_layout`. Conservar coordenadas absolutas, zonas de borrado, continuación y zona de estado; rechazar recortes que excluyan contenido autorizado. No modificar el archivo fuente.

Migrar anclaje mediante `master_spans`: el código lee texto del **PDF de referencia, incluido el convertido desde Word**; no edita Word ni ofrece OCR. Mostrar candidatos y selección explícita cuando el texto se repita. Guardar referencia verificable (hash del documento, página, texto, ocurrencia, caja/línea base y desplazamiento); no aceptar coincidencias ambiguas automáticamente.

Migrar relocalización con comparación y confirmación. `locate_fields` está especializado en ACETONA/EDROFONIO y puede reemplazar ajustes manuales: conservar ese alcance, tratar documentos sin referencias reconocidas mediante ajuste manual. La resolución genérica de anclas persistentes será ampliación nueva, con pruebas propias, no promesa de detector universal.

Migrar zona de estado y su geometría en mm; verificar límites, solapamientos y proporción frente al maestro de estado seleccionado, evitando extrapolar la proporción fija de la herramienta actual. Mantener modos de dibujo `baseline/textbox/continuation`, `erase`, `second_x` y `next_w`.

Completar alineación/distribución de campos autorizados, selección múltiple, bloqueo respetado por todas las operaciones y deshacer/rehacer de comandos sobre **campos + recorte + estado**. Un arrastre constituye una operación; guardar fija el punto limpio; cambiar documento delimita el historial. Toda operación debe poder cancelarse sin cambios parciales.

Separar **escala de visualización**, **dimensiones físicas de salida** (motor proporcional existente) y **transformación de geometría**. Llevar los controles de salida a Qt sin reescribir el PDF; avisar de espacios resultantes al conservar proporciones. Validar la transformación conjunta de campos y estado. El fondo fijo sigue protegido: redistribuir campos no implica recomponer textos fijos, tablas o imágenes. Su edición libre exige estudio técnico/documental independiente y queda fuera de R3B1.

Modelo de edición en memoria y fachada de servicios reutilizada; ningún cambio SQLite en R3B1. El guardado ampliará la comparación del estado original al conjunto completo del diseño, no solo `fields_json`. La verificación de estado, geometría e integridad debe estar en servicios, además de la interfaz. Los metadatos de anclaje solo se guardarán como extensión compatible del JSON existente tras probar lectores anteriores.

## 3. R3B2: separación documental y variantes
Hoy `versions` mezcla revisión documental y configuración de diseño; `approve` retira todas las revisiones vigentes de una etiqueta. No reutilizar ese comportamiento para aprobar una variante.

| Entidad recomendada | Responsabilidad |
|---|---|
| Maestro original protegido | Archivos originales y derivados identificados por hashes; registro de procedencia inmutable. |
| Revisión documental | Mantener `versions`, UID, estado, fuente y aprobación existentes. |
| Variante de diseño | Nueva entidad hija de una revisión: UID, código, motivo, estado, diseño, fechas y aprobación externa. |
| Trabajo de emisión | Datos/configuración en preparación y referencia exacta a revisión/variante. |
| Emisión histórica | Mantener `issues`; añadir referencia/snapshot de variante y trabajo cuando proceda. |

Proponer tablas aditivas `source_documents` (registro de archivos existentes, sin sustituirlos) y `design_variants`. La variante tendrá referencia a revisión y maestro, variante de origen opcional, identificación única dentro de la revisión, motivo, geometría/configuración, hash del diseño, estado PENDING/APPROVED/RETIRED y responsable/referencia/fecha de aprobación. La aprobación es externa registrada, no firma electrónica. Una variante aprobada queda congelada; modificarla crea otra pendiente. No retira otras variantes ni revisiones salvo acción explícita definida para su línea de sustitución.

Compatibilidad: conservar todos los IDs, UIDs, estados, rutas y hashes actuales. Una revisión histórica **no se convierte automáticamente en variante**. Un adaptador resolverá el diseño heredado cuando no haya variante seleccionada; la creación/conversión será explícita y trazable. **00-R1 continúa como revisión heredada PENDING**; su eventual vinculación al modelo nuevo exige revisión documental y nunca promoción automática.

Antes de tocar SQLite: entregar especificación de migración, ejemplos sintéticos antes/después y prueba de restauración. El código actual fija `user_version=3` y detecta ciertas columnas para su snapshot: habrá que reemplazarlo por migraciones ordenadas que detecten también las nuevas tablas, hagan copia consistente de base y archivos, comprueben integridad y aborten ante esquemas incompatibles. No borrar columnas ni reescribir registros históricos. Compatibilidad de datos no significa que un ejecutable antiguo pueda editar variantes nuevas: definir mínimo de versión y bloqueo de apertura/escritura incompatible, o retorno a copia anterior con aplicación cerrada.

La fachada resolverá revisión + variante al formato que espera el motor, manteniendo su validación. Emisión definitiva exige revisión elegible, variante aprobada si existe, integridad válida y maestros de estado autorizados. Almacenar snapshot de diseño usado; nunca reconstruir una emisión histórica con la variante actualmente vigente.

## 4. R3B3: trabajos y autoguardado local
Nueva entidad propuesta `work_drafts`: UID y nombre del trabajo; versión del contrato; UID de etiqueta/revisión/variante opcional; huella del diseño de base; variables comunes; lote y datos por recipiente; números seleccionados, cantidades/copias; formato/perfil y estado de etiqueta; operador, estado DRAFT/EMITTED/ARCHIVED, creación/modificación y contador de generación.

Autoguardado con breve espera tras cambios, transacción local y confirmación visual de la última escritura completada. Vaciar cambios al navegar, cerrar y ceder al puente; informar y permitir cancelar el cierre si falla. Recuperar tras reinicio el último estado confirmado, incluida información todavía incompleta o inválida para emitir. Probar interrupción abrupta y documentar el intervalo máximo aún no confirmado.

Cada trabajo independiente; cambiar etiqueta/revisión crea o selecciona otro trabajo, sin trasladar lotes. Duplicar será explícito y revisado. Si el diseño cambia o se retira desde la última apertura, marcar conflicto y exigir reconciliación; no adaptar silenciosamente los datos. Guardar trabajo **no guarda modificaciones de diseño**: estas siguen mediante acción explícita sobre diseño pendiente. Separar ambos indicadores y botones.

Autoguardado no llama a aprobación, modificación de maestro ni `add_issue`. Solo la acción de emisión definitiva validada crea historial y enlaza el trabajo; un PDF de prueba continúa separado. Prevenir doble registro ante reintentos y tratar fallo entre crear PDF y registrar emisión sin declarar éxito.

## 5. Contrato compartido con Emisión Tkinter
Crear servicio local común `WorkService` con operaciones crear/cargar/guardar/ceder/recuperar/finalizar, validación de identidad y actualización condicionada por generación. Editor Qt y Emisión Tk consumen el mismo contrato; posteriormente R3C reutiliza esos adaptadores de dominio.

Actualmente el puente pasa destino/revisión y carpeta de datos; no transmite variables. Propuesta: pasar UID de trabajo y token de cesión, nunca datos sensibles por argumentos. Qt confirma guardado y cede escritura; Tk valida identidad/huella y adquiere el trabajo. Tk persiste cambios mediante el mismo servicio; al terminar confirma generación y libera; Qt recarga y revalida. Probar **Qt → Tk y Tk → Qt**, incluyendo datos por recipiente, cancelación y fallo.

Mantener Qt bloqueado durante el acompañante. Añadir exclusión entre instancias sobre la carpeta de datos y titularidad controlada del trabajo; el bloqueo actual de widgets no protege frente a otros procesos. Recuperar una cesión huérfana solo comprobando que el escritor anterior no sigue activo. Mientras el acompañante esté abierto, ninguna otra instancia podrá modificar diseños o emitir en paralelo. Lecturas y escrituras internas se serializarán mediante servicios/transacciones locales, sin servidor. No declarar sincronización completa hasta superar pruebas en ambas direcciones.

## 6. Dependencias, riesgos y pruebas
Orden recomendado: R3B1 → R3B2 → R3B3. R3B1 funciona sobre revisiones pendientes actuales; R3B2 añade el adaptador sin romper ese editor; R3B3 admite revisión heredada sin variante. Riesgos principales: PDF sin texto o referencias duplicadas, modos de dibujo especiales, discrepancia lienzo/PDF, estado cambiado tras cargar, pérdida al ceder procesos, fallos de disco y ejecutables antiguos sobre esquema nuevo.

| Prueba prevista | Criterio de aceptación |
|---|---|
| Geometría física/escala | Conversión puntos–mm y proporciones; recorte y estado dentro de límites; comparar medidas calculadas/PDF con tolerancia explícita acordada. |
| Lienzo vs PDF final | Fixtures sintéticos baseline, textbox, continuation, borrado y estado; comprobar posiciones y glifos además de capturas. |
| Recorte/anclaje/relocalización | Conservar anclas; rechazar exclusión, ausencia/ambigüedad; deshacer/rehacer recupera diseño completo. |
| Variantes y migración | Revisiones/00-R1 sin promoción; hashes/UID/historial conservados; rollback desde backup; versión incompatible bloqueada. |
| Borradores | Reinicio, varios trabajos, datos incompletos, fallo de guardado y recuperación tras interrupción; ningún lote cruza identidades. |
| Navegación/puente | Ida y vuelta Qt/Tk, generación obsoleta, segunda instancia, cierre inesperado y revalidación documental. |
| Emisión no autorizada | Revisión/variante/estado pendiente o retirado, archivo alterado y doble registro bloqueados también en servicios. |
| Conservación/Windows | Revisar las 87 IDs, núcleo y widgets, portátil fuente/EXE y puente empaquetado; capturas habilitado/bloqueado/pendiente y regresión. |

Solo documentos sintéticos en GitHub. Permanecen pendientes pruebas reales de Word/conversión, Windows 10/11 y equipos COVEX, impresión física y validación GMP; los resultados de CI no las sustituyen. Esta entrega revisa código/documentación, no vuelve a ejecutar pruebas funcionales ni acredita capacidades nuevas.

## 7. Ramas y PR propuestas
| Rama | PR y puerta de revisión |
|---|---|
| `docs/r3b-architecture-plan` | Este informe y ROADMAP corregido; solo documentación, sin integrar automáticamente. |
| `feature/r3b1-qt-advanced-editor` | Herramientas nativas + comandos + regresión/matriz/capturas; iniciar solo tras autorización. |
| `feature/r3b2-design-variants` | Primero especificación de migración revisable; implementación solo tras aprobación de esa propuesta. |
| `feature/r3b3-work-drafts-bridge` | Contrato/persistencia de trabajos + ambos adaptadores + pruebas de sincronización y portable. |

Cada rama parte de main con su prerrequisito ya integrado y autorizado; no apilar tres fases sin revisión. Mantener Tkinter y accesos explícitos para capacidades aún anteriores. No comenzar R3C, R2.5, R4/R5 ni integraciones Business Central/SharePoint dentro de estas PR.
