# Cambios por pantalla y estado de incidencias

La [auditoría original](../UX_AUDIT_R6B/INCIDENCIAS.md) permanece como baseline. «Corregido» significa verificación automatizada y visual sintética en el alcance indicado, no aceptación presencial ni validación GMP.

## Organización aplicada

| Pantalla | Cambios y equivalencia de comandos |
|---|---|
| Biblioteca | Inspector con cuerpo desplazable y acciones operativas fijas al pie. «Abrir PDF maestro» → `open_document(False)`; «Abrir documento original» → `open_document(True)`. Un único botón de registro de aprobación dentro del Inspector → `approve_revision`; no se confunde consulta con aprobación. |
| Cabecera / navegación | Se mantienen Biblioteca, Editor, Emisión, Historial y Configuración. Nombres visibles en compacto; cabecera menos alta. «Documento» reúne selección, revisiones, metadatos, comparación y aprobación; «Intercambio» reúne importación, exportación, conciliación y compatibilidad. Los callbacks originales permanecen. |
| Revisiones y variantes | `RevisionBrowserDialog` Qt permite consultar y elegir revisión/variante, seleccionar en Biblioteca o abrir en Editor sin cambiar estados documentales. El catálogo Tk permanece como compatibilidad explícita, no como desvío de consulta nativa. |
| Editor | Elementos a la izquierda; lienzo central; Campo y variante / Trabajo de lote a la derecha. Crear campo, guardar diseño, deshacer/rehacer y herramientas conservan sus controladores. «Ampliar lienzo / Mostrar paneles» es explícito y reversible; no hay ocultación por resize. «Restablecer diseño guardado» conserva texto y alcance al redimensionar. |
| Trabajo de lote | El mismo WorkPanel deja de ser dock global y queda dentro del Editor. Datos conservados al navegar y al volver a la pestaña. Se mantienen guardar, recuperar y vínculos; las operaciones menos frecuentes están en `⋯`. Prueba PDF y emisión se centralizan en Emisión, accesible desde el panel, evitando dos botoneras de producción simultáneas. |
| Centro de emisión | Guardar trabajo se distingue de guardar diseño. Pegar Excel, guardar perfil y hoja patrón son visibles antes del formulario. «Hoja patrón…» genera la prueba de hoja; «Aplicar medidas de impresora…» captura mediciones; ninguna acredita comprobación física. Las reglas de emisión y validación del servicio no cambian. |
| Historial | Acciones contextuales usan apertura y reimpresión existentes. El visor compacto mantiene zoom, apertura, ampliación y advertencia de PDF de prueba. Snapshot y reimpresión controlada no se reconstruyen desde el diseño actual. |
| Configuración | No muestra ni comprime el trabajo del Editor. Sus funciones de mantenimiento, diagnóstico, preaceptación y UAT permanecen. Formularios y modales comparten política adaptable. |
| Diálogos | `AdaptiveDialog` envuelve el contenido una sola vez, limita tamaño al área lógica y deja botones de pie fuera del scroll. Guarda señales y validación existentes. UAT mantiene guardado visible; conciliación mantiene comparación/exportación accesibles. Diálogos nativos del sistema no se reemplazan. |
| Sistema visual | Menor densidad de cabecera y barras, contraste de texto secundario `#4B6268`, foco visible, espaciado consistente, nombres para símbolos y formularios. Traducción oficial Qt `qtbase_es` para botones estándar, sin cambiar textos operativos específicos. |

Implementación de composición: `qt_ui/workspace.py`; adaptación/accesibilidad: `qt_ui/responsive.py`; navegación y menús: `qt_ui/functional.py`; selector: `qt_ui/revision_browser.py`. Las guardas siguen en servicios: el estado de un menú no concede autorización ni sustituye validación documental.

## Registro de cierre y pendientes

| ID | Situación en esta entrega | Evidencia / límite |
|---|---|---|
| UX-01 | Corregido | Prueba de callbacks de fuentes y único registro dentro del Inspector; capturas 03 y 24. |
| UX-02 | Corregido | Selector Qt nativo; cancelar/seleccionar no muta documentos; estados 35 y dynamic-14. Compatibilidad Tk conservada. |
| UX-03 | Corregido en área Qt ensayada | 52 estados × 6; pies y límites verificados. Diálogos nativos de Windows requieren comprobación presencial. |
| UX-04 | Corregido | Lienzo ≥45 % del alto cliente en seis tamaños; paneles recuperables explícitamente; estado 07. |
| UX-05 | Corregido en acciones principales | Inspector fijo, pegado/perfil/hoja visibles; controles secundarios desplazables/contextuales; estados 03, 10 y 14. |
| UX-06 | Corregido | Navegar a cuatro destinos retiene lote y no muestra dock; volver al Editor recupera la pestaña y sus datos; estado 34. |
| UX-07 | Corregido | Test visor compacto 910×472, herramientas y nota visibles; estado 18. |
| UX-08 | Corregido | Documento / Intercambio; menús contextuales por entidad y equivalencia de callbacks cubierta en pruebas. |
| UX-09 | Corregido en terminología | Hoja patrón frente a medidas de impresora; no se declara calibración física por generar un PDF. |
| UX-10 | Corregido | Texto único «Restablecer diseño guardado» comprobado en seis tamaños; controlador original. |
| UX-11 | Corregido | Menú según transición DRAFT/PENDING/APPROVED/retirada, con motivo de deshabilitación; guardas del motor intactas. |
| UX-12 | Corregido en botones; parcial en informes | Botones estándar españoles, captions específicos conservados. JSON técnico original permanece: no se transforma en un informe humano nuevo. |
| UX-13 | Parcial verificado | Nombres accesibles de símbolos/campos y foco Ctrl+K; contraste medido. UIA, Narrador, tabulación completa y alto contraste Windows pendientes. |
| UX-14 | Corregido para tokens ensayados | Texto secundario real ≥4,5:1 sobre superficies principales; no certifica todas las combinaciones WCAG. |
| UX-15 | Diferido, sin cambio de concurrencia | Conversión síncrona sigue existiendo. Intervención independiente con diseño de worker/transacciones y prueba Word real. |
| UX-16 | Corregido documentalmente | Matriz actual de 87 IDs, 78 Qt / 2 mixtas / 7 motor; clasificación R3C marcada histórica en documento raíz. |
| UX-17 | Corregido en presentación | Diseño y lote separados; prueba y emisión centralizadas; recuperar/vincular conservados. Persistencias no unificadas. |
| UX-18 | No demostrado | No se convierte la sospecha en pérdida funcional afirmada ni se elimina capacidad. Falta caso histórico reproducible. |
| UX-19 | Corregido | Presentación a tres decimales; se conserva el valor bruto al no editarlo. Test conserva perfil calibrado y firma completa tras editar lote; cálculos internos intactos. |

## Revisión operativa propuesta

Flujo frecuente: Biblioteca → seleccionar revisión → Editor si procede modificar diseño → preparar trabajo → Emisión → prueba PDF → emisión con confirmación existente → Historial → reimpresión con motivo. La aprobación documental es una operación explícita distinta, con evidencias y guardas originales; no forma parte de guardar diseño ni de generar prueba.

Administración: Intercambio para carga/conciliación/exportación/compatibilidad; Configuración para instalación, diagnóstico y preaceptación. No se añaden pasos administrativos al flujo de emisión. No se publican cifras de ahorro temporal sin cronometraje presencial: la reducción demostrada es de botoneras duplicadas y desvíos de navegación, no una medición de productividad.
