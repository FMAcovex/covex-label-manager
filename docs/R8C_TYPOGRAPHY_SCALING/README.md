# R8C — tipografía, prueba controlada y composición de estados

Base: R8B `56399394424896a1adbd56a91882a7eb49282632`. Rama `feature/r8c-typography-status-scaling`, PR en borrador contra `feature/r8b-editor-ux`. Cadena R8A → R8B → R8C sin merge ni squash. Evidencias exclusivamente sintéticas; no valida GMP ni solicita aceptación manual intermedia.

## R8C1 — motor tipográfico

Los campos pueden optar explícitamente por `typography.contract=1`: Helvetica/Nimbus Sans (alternativa profesional a Arial), Times/Nimbus Roman o Courier/Nimbus Mono; regular, negrita, cursiva o ambas. Tamaño original en puntos, color `#RRGGBB`, izquierda/centro/derecha, arriba/centro/abajo en cajas, líneas por palabras o sin ajuste. Desbordamiento: **bloquear**, sin reducir, truncar ni deformar automáticamente.

Los doce programas de fuente se obtienen de los recursos incorporados de PyMuPDF 1.26.6 / MuPDF 1.26.11. Se verifican por SHA-256 y se embeben en el PDF. Recurso ausente, distinto o glifo no disponible: aviso y bloqueo; reparar portable o preparar una variante, nunca sustitución silenciosa de una fuente aprobada. No se busca Arial instalada para diseños nuevos. Helvetica no promete identidad de métricas con todas las versiones de Arial.

Se miden también los trazos reales de cada glifo y sus salientes, no sólo el ancho de avance. Una «f» cursiva puede sobresalir por ambos lados: el origen se compensa únicamente si escaparía de la caja y se bloquea si los trazos completos no caben. El recorte de texto fijo reserva además un margen conservador de un em; puede exigir área mayor/variante aun si el cuadro de extracción parecía caber. Regresiones izquierda/centro/derecha y comprobación adicional en el EXE extraído. La ruta histórica no se modifica.

Los campos **sin** `typography` conservan la ruta histórica `_fonts()` y sus métricas; no se añaden valores por defecto a JSON anteriores. La prueba comparativa exige raster PDF histórico idéntico entre R8B y R8C en el mismo Windows. Esto no convierte la selección histórica dependiente del sistema en una garantía entre SO.

Fuentes URW bajo SIL OFL 1.1: [copyright y licencia íntegros](URW-FONTS-OFL.txt), incluidos en ambos ZIP. Origen oficial: [MuPDF 1.26.11, recursos URW](https://github.com/ArtifexSoftware/mupdf/tree/1.26.11/resources/fonts/urw). El CFF Nimbus Sans Regular oficial tiene el mismo SHA-256 que el recurso utilizado (`366720e0…91d706`). No se añaden TTF propietarios. PyMuPDF mantiene su licencia dual AGPL/comercial preexistente; esta fase no cambia ni acredita el régimen jurídico de distribución de toda la aplicación.

## R8C2 — Editor de tres zonas

Propiedades agrupadas en Contenido, Tipografía y Geometría, con scroll. Identificador, nombre, tipo y ejemplo; texto fijo sólo si es un campo superpuesto ya admitido por el contrato, nunca el Word/PDF maestro. Tamaño, negrita, familia/estilo/color/alineación/líneas; X/Y/anchura/altura y bloqueo de posición. Los modos anclados baseline/continuation no ofrecen alineación vertical incompatible.

«PDF real» alterna el lienzo con el PDF de prueba del motor, usando ejemplos, sin guardar/aprobar ni registrar emisión. Al editar se actualiza con retardo breve. El lienzo permanece vivo: selección, zoom, objetos nativos y deshacer/rehacer conservados. Se mantiene el guardado documental explícito y el bloqueo de revisiones vigentes. R8A/R8B continúan cubriendo cierre, gestos y concurrencia.

## R8C3 — apariencia durante emisión

Centro de emisión → **Ajustar apariencia del campo…**. Selección de campo variable, valor de lote sólo lectura, tamaño, estilo, color, alineación y geometría en mm. No se ajustan desde aquí numeración ni textos fijos. El bloqueo de posición y los límites del diseño se revalidan en el contrato.

| Modo | Efecto permitido | Emisión definitiva |
| --- | --- | --- |
| Ajuste aislado en diálogo | PDF real PRUEBA / NO GMP; Cancelar descarta | No registra ni modifica trabajo/revisión |
| Aplicar sólo al trabajo de prueba | Guarda apariencia en borrador recuperable, sin cambiar valores comunes/por recipiente | Bloqueada en revisión, antes de INTENT y en el motor, incluso sin UI |
| Restablecer campo / diseño de origen | Quita los parches temporales | Vuelven a aplicarse todas las guardas documentales habituales |
| Crear variante documental | Traslada el diseño a variante DRAFT y nuevo trabajo, con código/nombre/motivo y acceso al Editor | Requiere revisión y evidencia de aprobación externa; nunca se aprueba desde el diálogo |

No hay rangos operativos de apariencia previamente autorizados en el contrato base. Por tanto **ningún** parche temporal se trata como autorizado para producción. Un ajuste vacío pero explícito tampoco concede aprobación. Los cambios externos, generación y token de vista previa siguen invalidando resultados obsoletos.

Mover un campo temporal utiliza el comando geométrico existente: conserva conjuntamente desplazamiento de ancla, máscara autorizada y continuación al trasladarlo a variante. No se deja un ancla antigua que pueda revertir la posición al relocalizar posteriormente. El original y sus valores permanecen intactos; las regresiones comprueban las coordenadas auxiliares.

## R8C4 — escalado de estados

Trabajo → Estado → Composición física:

- **Histórico · sin cambios**: ruta previa para diseños antiguos, sin reinterpretación.
- **Ajustar sin deformar**: factor `min(ancho_destino/ancho_origen, alto_destino/alto_origen)`; alineación elegible y dimensión efectiva/margen libre total visibles.
- **Rellenar · recorte protegido**: factor `max(...)`; calcula ventana fuente visible y recorte. No estira texto ni geometría. Se bloquea si se pierde texto fijo, campo variable (incluso opcional), imagen, trazo, borde o símbolo. Sólo se ignora como fondo un rectángulo plano sin borde que cubra el recorte aprobado.

Fondo y variables se componen en puntos de la página fuente y se transforman **juntos**. R7A/R7B utilizan la misma implementación en PDF individual y combinado. El maestro histórico conserva su compositor original en una capa intermedia cuando se solicita composición explícita; el recorte sigue protegido. En independiente, el destino es la casilla física completa, no una caja previamente ajustada.

La capa del maestro histórico registra también sus fuentes propias; regresión para los tres tipos. El mínimo tipográfico se mide después de la transformación (p. ej. 5 pt fuente × 2 = 10 pt físicos), no se confunde con el tamaño del original. La ruta nueva avisa/bloquea también texto fijo visible demasiado pequeño y conserva ese diagnóstico en los metadatos del PDF de prueba y en su vista previa.

Si el fondo contiene un límite o contenido crítico en el borde, rellenar puede ser imposible: se indica el contenido afectado y se ofrece ajustar, ampliar el área o preparar revisión/variante. No se elimina el borde para lograr un resultado aparentemente lleno. El tipo «Aprobado» sigue siendo distinto de la aprobación documental.

## R8C5 — campos de estados

Editor de estados: mismas propiedades tipográficas, geometría y ejemplos; «PDF real» para inspección dinámica de los valores de ejemplo. Guardado por `save_draft(expected_layout_sha=...)`; aprobadas/pendientes no editables, nueva revisión explícita. Contrato 2 conserva las propiedades al cerrar/abrir. El gestor individual añade área alto/ancho, composición y PDF previo dinámico. En histórico, la altura se calcula proporcionalmente y no se presenta como editable.

Los valores de emisión individual y combinada siguen entrando por los formularios propios, no se extraen de ejemplos ni del color de la etiqueta. Las tres clases amarilla/verde/roja se prueban con diseños sintéticos conservando su arte y texto fijo.

## R8C6 — vista fiel y errores

Todas las vistas usan el PDF real, no un texto Qt aproximado. Las dimensiones son físicas; el zoom no las altera. El Centro conserva identificación de revisión/variante; el resultado muestra área, escala, dimensión efectiva, margen o recorte previsto. El render comprueba cajas, métricas de la fuente embebida y límites finales. No caber bloquea incluso una prueba: no se presenta un PDF incompleto como válido. Tamaño final menor de 6 pt: aviso de prueba y bloqueo definitivo para la nueva ruta.

Contraste: sólo se afirma detección en regiones de fondo uniforme reconocibles; referencia de luminancia 4,5:1. Si el fondo no puede determinarse de forma fiable, no se atribuye conformidad. Un contraste detectado insuficiente se avisa en prueba y bloquea producción; no se impone otro color. Baselines históricas sin caja vertical no reciben una estimación inventada.

## R8C7 — reutilización sin catálogo paralelo

- Variantes existentes: geometría y tipografía documental, mismo ciclo DRAFT/PENDING/APPROVED/RETIRED, evidencia y hashes.
- **Copiar trabajo**: reutiliza formato, estado y apariencia temporal, conservando su condición de prueba, sin heredar emisión ni operación.
- Perfiles existentes: formato físico/hoja/calibración. Al guardar formato se excluye apariencia temporal y se explica la diferencia. Guardar un perfil no aprueba un diseño.
- Preferencias de vista y zoom no alteran contratos documentales. No se crea otro catálogo de «plantillas aprobadas».

## Contratos y compatibilidad histórica

| Contrato | Cambio | Protección |
| --- | --- | --- |
| Campos producto JSON | `typography` opcional, anidado y versionado; `example` opcional | Validación de familias/color/tipos/rangos; JSON anterior intacto |
| Diseño estado | Lee 1; escribe 2 al introducir tipografía/ejemplos | Un lector anterior rechaza contrato 2 en vez de perder atributos durante normalización |
| Trabajo sidecar | Lee 1/2/3; 3 para prueba/composición/diseño tipográfico | CAS, checksum, copia anterior y negativa de lectores R8B |
| Snapshot emisión v4 | Conserva contrato SQL 1; marcador de render dentro del diseño nuevo | Hash incluye semántica y SHA de fuentes; el lector R8B no puede reproducir ignorando la tipografía |
| SQLite producto / catálogo estados | **Sin modificación de esquema** | v4, integridad y claves externas comprobadas |

Snapshots/PDF antiguos no se migran ni reinterpretan. Una reimpresión individual de estado copia exactamente el PDF registrado y verifica bytes/hash. Producto conserva snapshots, fuente y evidencia; las reproducciones controladas mantienen geometría/datos, aunque un nuevo PDF registrado puede tener metadatos/identificador distintos. El PDF histórico original permanece exacto e intacto.

## Evidencia y regresión

`tests/test_r8c_typography.py`: 12 fuentes/estilos embebidos, RGB, nueve alineaciones, métricas reales, desbordamiento, tamaños, glifo/fuente ausentes, fit/fill, transformación común, recorte crítico, contraste, contratos antiguos/nuevos, persistencia, restauración, bloqueo antes de INTENT, estado individual/combinado y copia histórica exacta.

`tests/test_r8c_typography_qt.py`: seis viewports, scroll sin desbordamiento horizontal, objetos/zoom/undo, PDF real, cancelar/aplicar/reabrir/restaurar, nueva variante y aprobación externa **sólo en fixture aislado**, snapshot/historial, editor de estados y destrucción nativa sin callback sobre canvas borrado. Se mantienen todas las pruebas anteriores y se amplía la regresión estática contra ocultar métodos de QWidget.

`scripts/r8c_visual.py`: misma fixture sobre R8B exacta y R8C, 1366×768 / 1920×1080, 100/125/150 %. Antes: seis capturas por escala. Después y ZIP extraído: doce por escala. Guarda PNG, PDFs sintéticos, hashes e informe JSON; comprueba doce fuentes y seis combinaciones producto/estado. `r8c_compare_evidence.py` exige raster histórico idéntico. `r8c_backward_gate.py` ejecuta lectores R8B sin modificar y exige rechazo de nuevos trabajos/reproducciones incompatibles.

Windows usa backend nativo para interacciones/regresiones. Las capturas grandes exactas usan Qt **offscreen en Windows**, porque el escritorio alojado limita el tamaño de ventanas. Esto no sustituye aceptación física Windows 10/11, Word, impresora o validación GMP. Los controles antiguos source/frozen, importador, estabilidad R8A, R8B, variantes, Qt↔Tk e historial siguen en la CI.

Primera CI Qt (`39220939672`): los 86 self-checks y regresiones nativas previas pasaron, pero la captura de Estados a 125 % solicitó 1068 px y recibió 1073 px. Se mantiene la aceptación exacta: el PDF inactivo deja de imponer su mínimo al lienzo y su barra de herramientas se reorganiza en dos filas en paneles estrechos, sin reducir letra ni retirar comandos. Se añaden regresiones de mínimo oculto, herramientas accesibles y destrucción de shapes/canvas nativos. No se cambia el límite temporal de los jobs ni se elimina ninguna comprobación histórica.

Segunda CI (`39222467851`): resoluciones exactas R8B ya satisfactorias; la extracción de texto del ejemplo con **Arial histórica Windows** devolvió el guion como U+00AD. Se conserva esa ruta/métrica histórica. La regresión R8C selecciona explícitamente la nueva fuente embebida y sigue exigiendo `SYN-EXAMPLE` exacto, además de comprobar su recurso PDF R8C. La comparación de raster anterior/posterior sigue comprobando la ruta histórica sin normalizar caracteres ni omitir aserciones. Los nuevos temporizadores se detienen al cerrar diálogos y al apagar la sesión.

### Comparación visual y ejemplos PDF

En el artefacto técnico, carpeta `r8c-visual/`:

| Evidencia | Antes | Después / EXE extraído |
| --- | --- | --- |
| Editor | `before-1/1366-editor.png` | `source-1/1366-editor.png`, `1366-editor-pdf.png` |
| Estados | `before-1/1366-status.png` | `source-1/1366-status.png`, `1366-status-pdf.png` |
| Emisión | `before-1/1366-emission.png` | `source-1/1366-trial-appearance.png`, `1366-emission.png` |
| Ajustar | Proporción histórica | `aprobado-fit.pdf`, `combined-aprobado-fit.pdf` |
| Rellenar | No disponible | `aprobado-fill.pdf`, `combined-aprobado-fill.pdf` |
| Otros colores | Arte sintético amarillo/rojo | Mismos pares `sin_analizar-*` y `rechazado-*` |

Cada PDF tiene también PNG `*-pdf.png`. Para el estado sintético 200×100 pt en área 70×70 mm: Ajustar = 70×35 mm, margen vertical total 35 mm; Rellenar = 70×70 mm, ventana fuente 100×100 pt, recorte horizontal total 100 pt (35,28 mm fuente), sin pérdida crítica. No extrapolar estos ejemplos a documentos internos.

Resultados finales, commit exacto, tres CI, SHA del ZIP y enlaces de portable/evidencias se registran en la PR una vez terminados. No se declara verde una ejecución pendiente. El portable no incluye capturas, PDFs sintéticos ni bases de pruebas.

## Riesgos residuales y R8D

- Recorte conservador: documentos con borde o imágenes amplias pueden requerir variante; no hay reconocimiento semántico/OCR que autorice ignorar contenido.
- Fondos complejos/transparencias, contraste visual humano, símbolos particulares y legibilidad física requieren revisión conjunta posterior. Ningún aviso equivale a conformidad GMP.
- Catálogo reducido de caracteres de las fuentes incorporadas: glifos no soportados bloquean, sin fallback ni fuentes del sistema. Nuevos idiomas/fuentes requieren ampliar contrato y pruebas.
- No hay edición nativa de Word/PDF fijo ni estiramiento automático. Los ajustes de baseline conservan su ancla; alineación vertical se limita a cajas/párrafos.
- Los PDF de prueba se generan en cache; la limpieza respeta los cierres y trabajadores R8A. Ninguna prueba cierra forzosamente un escritor documental.
- R8D puede guiar la elección de formato/modo y explicar incidencias, reutilizando estos contratos y servicios. No debe añadir aprobaciones automáticas, ocultar capacidades o crear un catálogo paralelo. **R8D no se implementa aquí.**

[Auditoría técnica previa](AUDITORIA_CONTRATOS.md) · [87 capacidades](CONSERVACION_87.md).
