# COVEX Label Manager — Plan maestro vivo

Situación R6B-UX: [implementación UX-1/2/3 y evidencias](docs/R6B_UX_INTEGRATED/README.md),
alternativa A, conservación de 87 capacidades y entrega en PR borrador. Pendientes:
UX-15 (concurrencia Word), UIA/teclado y pruebas físicas Windows, calibración/impresión
y aceptación humana. No adelanta la validación GMP ni autoriza R6C automáticamente.
La planificación siguiente conserva la cronología de los hitos anteriores.

Aceptación Windows de `46d3eab`: **NO CONFORME**. [Correcciones funcionales solicitadas](docs/R6B_UX_INTEGRATED/CORRECCIONES_ACEPTACION.md): cierre seguro del importador, asistente, masas kg/g/mg, vista previa automática y variantes por estado. Requieren nuevo portable y aceptación humana; no autorizan R6C, squash ni merge.

Versión de aplicación: 0.3.1 (consolidación de R1/R2; referencia histórica `v0.3.0-reference` sin originales). Revisado: 15/10/2026. R3A Qt integrada como hito de desarrollo por squash de PR #4 en `5d27de30ce98ee89f17485225e3a45b92f544484`; no equivale a validación GMP.

Este inventario contrasta las propuestas aceptadas del chat con README, traspaso, código, pruebas y muestras del proyecto recuperado. **Aprobada** significa acordada como requisito; no significa implementada ni validada GMP. Solo se consideran implementadas las funciones verificadas en este paquete. La comprobación física en Windows/impresora sigue pendiente.

Leyenda: **Implementada** = código verificado; **Parcial** = existe una parte indicada; **Pendiente** = acordada, aún sin desarrollo; **Propuesta** = posibilidad que necesita concretarse. La versión de software y los hitos R1–R5 no son equivalentes.

## Prioridad y secuencia

R1/R2 → R3A/B1/B2/B3 integradas en main `86475779b1eac6f39c9098e0e9d67dd2de51d5fe` → R3C implementado en rama para revisión. R4/R5 y conectores pendientes, fuera de alcance.

## Revisiones acordadas

| Hito | Funcionalidad | Decisión | Estado y evidencia |
|---|---|---|---|
| R1 | Corregir columna aparente y numeración de Edrofonio | Aprobada | Implementada como variante pendiente 00-R1. `render_geometry.py`, `test_r1.py`, PDFs de dos y tres envases. |
| R1 | Investigar causa real | Aprobada | Verificada: tabla anidada de Word más ancha que marco exterior y restauración artificial de borde tras enmascarar. evidencia privada excluida de GitHub. |
| R1 | Respetar marco y dimensiones físicas | Aprobada | Variante basada en marco exterior de la fuente local, sin sobrescribir originales. Reajuste interior identificado y pendiente de revisión. |
| R1 | Zona de seguridad configurable | Aprobada | Implementada en mm finales, perfil y pantalla de emisión. Predeterminada 0 para no imponer una nueva restricción a maestros existentes. |
| R1 | Bloquear desbordamientos antes de guardar PDF | Aprobada | Implementada: cajas de campo, ancho de texto y cajas reales de glifos, incluida línea base. El original Edrofonio 00 con defecto no se emite; se consulta o se utiliza 00-R1. |
| R1 | Regresión de otros maestros | Aprobada | Acetona y los tres estados, integrados e independientes, incluidos en las muestras y pruebas. No equivale a validación del catálogo completo. |
| R2 | Sustituir desplegable por Biblioteca | Aprobada | Implementada en emisión y Maestro, con selección explícita de revisión. `library_ui.py`, prueba gráfica. |
| R2 | Búsqueda dinámica por código, nombre, producto, cliente y metadatos | Aprobada | Implementada, varios términos y búsqueda sin distinción de acentos. Metadatos no documentados permanecen vacíos. |
| R2 | Filtros combinables | Aprobada | Categoría, familia, tipo, origen, cliente, país, idioma, revisión, estado e incorporación. Opciones obtenidas del catálogo; filtros sin fuente deshabilitados. |
| R2 | Previsualización y doble clic | Aprobada | Implementada: imagen de plantilla, ficha de revisiones, selección de la revisión exacta. |
| R2 | Favoritos y recientes | Aprobada | Persistentes. Favorito por etiqueta; recientes conservan la última revisión abierta/seleccionada. |
| R2 | Buscador rápido Ctrl+K | Aprobada | Implementado mediante Biblioteca modal; también accesible por botón y teclado. |
| R2 | Separar COVEX, cliente e incorporación | Aprobada | Origen COVEX/CLIENTE independiente de procedencia de importación y del estado documental. Fuentes históricas desconocidas se muestran sin registro. |
| R2 | Incorporar metadatos posteriormente | Aprobada | Valores opcionales con referencia fuente obligatoria, sin modificar PDFs ni la aprobación de versiones. Contrato extensible para ampliar claves. |
| R2.5 | Comparador con superposición y diferencias gráficas | Aprobada | Pendiente. La v0.2 solo tenía imágenes en paralelo y comparación de configuración. El trabajo preliminar apartado no está incluido en esta entrega. |
| R3 | Identidad visual Label Studio, editor central y propiedades contextuales | Aprobada como fase | Industrial Moderno aprobado definitivamente en Biblioteca y Editor; R3A Qt integrada. R3B amplía capacidades sin nuevo rediseño general. |
| R3 | Migración de Tkinter a PySide6 | Aprobada como tecnología objetivo | PySide6 en R3A integrada; Tkinter y puente conservados para capacidades aún no migradas. |
| R4 | Centro de impresión y perfiles | Aprobada | Parcial: pantalla, formatos A4, orientación, márgenes, separación, perfiles e impresora ya existentes. No se desarrollan nuevas funciones R4 ahora. |
| R4 | Calibración por impresora | Aprobada | Parcial: hoja de prueba y desplazamientos X/Y guardados en perfiles. Validación física pendiente. |
| R4 | Aprovechamiento de hojas usadas | Aprobada | Parcial: casilla inicial; marcar posiciones ocupadas arbitrarias visualmente está pendiente. |
| R4 | Reimpresión controlada por números/rangos y motivo | Aprobada | Implementada en v0.2: conserva datos y número original, registra relación con emisión original, verifica hash y vigencia. |
| R4 | Impresión directa y confirmación física | Aprobada como objetivo | Parcial: generar/abrir PDF. Sin envío nativo a impresora ni confirmación física registrada. |
| R5 | Importación masiva Excel de productos/lotes/cantidades | Aprobada | Pendiente. Pegar PN/PB por envase desde TSV/CSV ya existe; no equivale a esta función. |
| R5 | QR y códigos de barras dinámicos | Aprobada | Pendiente; estándares y contenidos por concretar. No generar GS1 automáticamente sin definir datos/reglas. |
| R5 | Etiquetas vinculadas | Aprobada | Parcial: dos copias idénticas por envase y estado integrado. Vincular varios diseños diferentes en un único trabajo está pendiente. |
| R5 | Emisiones recurrentes y repetición con nuevos datos | Aprobada | Pendiente. Reimpresión histórica existente no equivale a nueva emisión recurrente. |

## Funciones del primer plan y del traspaso

| Área | Función | Decisión | Estado real |
|---|---|---|---|
| Maestro | Productos, etiquetas, categorías, anexos y versiones | Aprobada | Parcial: entidades etiqueta/versiones, importación de catálogo local (datos reales excluidos) y categorías; relación formal producto-etiqueta pendiente. |
| Maestro | Migración automática inicial del libro máster | Aprobada | Pendiente. Importación local individual/carpeta existe; no se ha migrado el libro completo de SharePoint. |
| Maestro | Ignorar archivos temporales y detectar versiones | Aprobada | Parcial: importador local descarta `~$`, propone identidad; conciliación automática de vigencias pendiente. |
| Maestro | Conciliación con CM y etiquetas sin asociación | Aprobada | Parcial: catálogo y duplicidades de código; conciliación bidireccional completa pendiente. No se fusionan códigos automáticamente. |
| Maestro | Pendiente/vigente/retirada, revisión documental | Aprobada | Implementada; estado separado del nombre y revisiones aprobadas protegidas. No es firma electrónica cualificada. |
| Plantillas | Conservar Word/PDF original y comprobar integridad | Aprobada | Implementada, SHA-256 y copia de originales. R1 añade un PDF derivado, no sustituye fuentes. |
| Plantillas | Versiones de EGP, anexo y fichero diferenciadas | Aprobada | Parcial: anexo y revisión de fichero; modelo completo para todos los metadatos EGP pendiente. |
| Plantillas | Importar Word, PDF e imagen | Aprobada | Implementada; Word requiere Word/LibreOffice. Importación multipágina requiere preparar la página específica. Selector/separación de subetiquetas general pendiente. |
| Plantillas | Etiquetas de cliente cerradas o con campos autorizados | Aprobada | Implementada mediante origen CLIENTE, original conservado y campos opcionales. Gestión ampliada de referencias/aceptación por producto pendiente. |
| Diseño | Escalado proporcional rápido | Aprobada | Implementada: ajuste sin deformar el conjunto a área elegida y perfiles reutilizables. |
| Diseño | Reajuste avanzado | Aprobada | Parcial: editor de campos, posiciones en mm, recorte, anclas PDF y zona de estado; R1 variante derivada específica. R3B1 migra herramientas de campos; edición libre de textos fijos, tablas, pictogramas e imágenes queda fuera hasta verificar viabilidad e impacto documental. |
| Diseño | Variantes por envase/material con aprobación independiente | Aprobada | Implementada R3B2: variantes independientes, aprobación externa y congelación; R1 sigue revisión heredada pendiente. |
| Diseño | Reglas, cuadrícula, zoom, alineación y objetos bloqueados | Aprobada | Parcial: coordenadas y bloqueo de posición; herramientas completas de composición pendientes. |
| Emisión | Datos variables, numeración correlativa y dos copias | Aprobada | Implementada. |
| Emisión | Datos individuales PN/PB/lote/conservación por recipiente | Aprobada | Implementada, herencia de datos comunes y validación PN/PB. |
| Emisión | Estados Sin analizar/Aprobado/Rechazado | Aprobada | Implementada, diseño original integrado o independiente, lote heredado según campos reales del maestro. Emitir Aprobado no aprueba el material. |
| Emisión | Selector inteligente según material/cliente/destino | Aprobada | Parcial: búsqueda y filtros R2; selección automática por reglas y resolución de ambigüedades pendientes. |
| Emisión | Validación de obligatorios, fechas y textos | Aprobada | Implementada para campos/configuraciones actuales; reglas específicas de cada categoría pendientes. |
| Emisión | Verificación reglamentaria CLP/ADR y mínimos de pictogramas | Aprobada como objetivo | Pendiente. Avisos de texto pequeño son técnicos; no constituyen validación reglamentaria. |
| Trazabilidad | Historial de datos, PDF, versión, perfil y reimpresión | Aprobada | Implementada localmente; PDFs de prueba no entran como emisiones productivas. |
| Trazabilidad | Auditoría inviolable, permisos y firma electrónica | Propuesta de evolución | Pendiente de alcance. La auditoría local SQLite no es inviolable ni multiusuario. |
| Persistencia | Actualizar sin perder maestros, ajustes ni historial | Aprobada | Implementada con carpeta `data` separada, migración aditiva y snapshot previo. |
| Persistencia | Copia de seguridad y restauración | Aprobada | Parcial: ZIP consistente; restauración manual con aplicación cerrada. Asistente de restauración pendiente. |
| Entrega | Portable Windows sin servidor | Aprobada | Portable R3A construido y comprobado en CI Windows; aceptación real Windows 10/11 y equipos COVEX pendiente. |
| Calidad | Verificación Windows, A4 al 100%, validación de uso previsto | Aprobada | Pendiente; no declarar este prototipo como validado GMP. |

## Arquitectura e integraciones futuras

| Área | Decisión | Estado |
|---|---|---|
| Modularidad local, contratos y UID | Aprobada ahora | Implementada de forma incremental: UI → servicios locales → repositorio/motor. No se introduce servidor. |
| GitHub privado, pruebas y construcción Windows | Aprobada como preparación | Repositorio privado FMAcovex/covex-label-manager creado. Código incorporado por PR #1; workflow Windows ejecutado. Protección efectiva de main limitada por el plan actual. |
| Business Central | Base ampliable aprobada; conexión excluida ahora | Solo documentación breve en `ARCHITECTURE.md`. Sin cliente API, credenciales, infraestructura ni sincronización. |
| SharePoint | Evolución futura contemplada | Pendiente; conservar hashes/versiones y revisar antes de activar nuevos documentos. |
| Otras apps COVEX | Evolución futura contemplada | Pendiente de contrato y casos de uso; no escribir directamente en bases ajenas. |
| Multiusuario o base central | Posibilidad futura, no implantación actual | Pendiente de necesidad real; no compartir SQLite activo entre usuarios. |
| ERP/RFID complejo | No priorizado | Fuera de la fase actual. |

## Mantenimiento en GitHub

En cada revisión: actualizar fecha/versión, función y alcance real, pruebas/evidencias y pendientes. Nunca convertir una propuesta en implementación por estar mencionada en una PR. Una función solo pasa a implementada tras revisar su código y resultado. Conservar la diferencia entre aprobación del requisito, aprobación documental de diseño y validación del software.

## Consolidación antes de R3 — 08/10/2026

| Elemento | Estado y evidencia |
|---|---|
| Referencia original 0.3.0 | Referencia documental `v0.3.0-reference`; el original y su historial con documentos se mantienen fuera del remoto. |
| Controles documentales | Parche 0.3.1: bloqueo del PDF defectuoso por SHA-256, integridad antes de aprobar/copiar, recarga del estado antes de emitir. Pruebas adaptadas a fixtures sintéticos, sin originales. |
| Geometría | Comprobación histórica privada de la consolidación; no se publican los maestros ni sus reproducciones. |
| GitHub | Cuenta FMAcovex comprobada. No aparece repositorio Label Manager. Repositorio privado creado y verificado. Incorporación por PR; comprobar estado real de CI. |
| Construcción Windows | Un workflow, dependencias transitivas con hashes y comprobación del núcleo empaquetado preparados. Actions #3 satisfactorio en Windows Server 2022: 49 tests pasan, 1 omitido, build y núcleo empaquetado pasan. Aceptación Windows 10/11, Word e impresión pendientes. |
| R3 | Situación histórica al 08/10, superada: R3A Qt integrada el 09/10 y diseño aprobado. R3B permanece en planificación, sin implementación autorizada. |

## Política de publicación y desarrollo oficial

Solo código, pruebas sintéticas y documentación técnica. No maestros, etiquetas reales, catálogo, emisiones, bases, capturas reales ni historial que contenga esos documentos. 00-R1 sigue PENDING hasta aprobación documental local; un tag/PR/build no la aprueba. Una instalación nueva tiene biblioteca vacía. Todas las revisiones posteriores se realizan en ramas y PR, con pruebas y revisión antes de integrar en main. R3A integrada; R3B/R3C no implementadas.


## Secuencia aprobada para R3 — actualizada 11/10/2026

Repositorio privado operativo: FMAcovex/covex-label-manager; main incorpora R3A Qt en `5d27de30ce98ee89f17485225e3a45b92f544484` sobre la base 0.3.1. Toda revisión se desarrolla en rama y PR, sin commits directos ni integración sin autorización.

| Etapa | Decisión | Estado verificado |
|---|---|---|
| R3A Qt | Aprobados Industrial Moderno/Biblioteca y PySide6; conservar 87 capacidades | Integrada por squash de PR #4; aprobada como hito de desarrollo. Biblioteca/Editor Qt y acceso explícito a herramientas Tk conservados. Sin aceptación real de Word, impresión, equipos COVEX ni validación GMP. |
| R3B | Aprobada como siguiente fase del plan | Plan R3B aprobado; R3B1 implementado en rama, pendiente de revisión/integración. R3B2/R3B3 sin implementar; migraciones sujetas a revisión previa. |
| R3C | Aprobada como fase posterior | Pendiente; no iniciada. No se amplía el centro de emisión ahora. |
| R2.5 | Comparador visual/superposición/diferencias | Pendiente; no descartado. Comparación básica continúa en versión anterior. |

PR #2 Tk y #3 prueba Qt cerradas como sustituidas, sin integrarlas; referencias y ramas conservadas. PR #4 integrada. Se reutilizan el criterio de vistas retenidas y la composición visual; se descartan la reconstrucción de pantallas al navegar, los datos ficticios como persistencia de producción y botones que simulen módulos migrados. La prueba ficticia sigue disponible exclusivamente por modo demo/verificación. Integraciones, R4/R5 y ampliaciones R3B/R3C no se desarrollan en esta rama.

## Plan R3B — propuesta técnica 11/10/2026

Informe de código y contratos: [propuesta técnica aprobada (PR #5)](https://github.com/FMAcovex/covex-label-manager/blob/docs/r3b-architecture-plan/docs/R3B_TECHNICAL_PROPOSAL.md). Propuesta aprobada; R3B1 autorizado e implementado únicamente en rama. R3B2/R3B3 siguen planificados; no se autoriza todavía cambiar SQLite.

| Bloque | Alcance previsto | Dependencias y aceptación |
|---|---|---|
| R3B1 | Recorte, anclaje PDF/Word convertido, relocalización con alcance explícito, zona de estado y ajustes mm nativos; alineación/distribución y deshacer/rehacer como ampliaciones. Escala física separada del zoom. | Sin cambio SQLite; reutilizar servicios/motor y conservar modos especiales. Implementación en rama; matriz, pruebas y capturas para revisión antes de integrar. |
| R3B2 | Maestro protegido, revisión existente y variante de diseño separada con motivo, estado y aprobación externa; adaptador para motor e historial. | Propuesta de migración aditiva y backup/restauración antes de cambiar SQLite. No convertir automáticamente revisiones históricas. 00-R1 sigue PENDING. |
| R3B3 | Trabajos independientes, autoguardado local, recuperación y contrato compartido Qt/Tk para variables/configuración/recipientes. | Distinguir guardado de diseño y trabajo; cesión exclusiva y control de generación. Probar ida/vuelta antes de declarar sincronización; preparar contrato para R3C. |

Ramas propuestas: `feature/r3b1-qt-advanced-editor`, `feature/r3b2-design-variants` y `feature/r3b3-work-drafts-bridge`, con PR independientes en secuencia desde main autorizado. Planificación en `docs/r3b-architecture-plan`; main intacta; solo R3B1 autorizado para implementación. Integración mediante PR requiere confirmación.

Pruebas previstas: geometría/dimensiones físicas y concordancia lienzo–PDF; recorte/anclas y undo/redo; variantes, vigencia e integridad; migración y compatibilidad de registros; autoguardado/reinicio/fallos; navegación y cesión Qt/Tk; bloqueo de emisiones no autorizadas; conservación de las 87 capacidades; build/portable Windows y regresión. Solo fixtures sintéticos. Word real, impresión física, Windows 10/11, equipos COVEX y GMP continúan pendientes.

Autoguardado nunca aprueba variantes, altera maestros vigentes ni registra emisión definitiva. No transferir datos de lote entre etiquetas/revisiones. El puente se conserva hasta migración y comprobación efectiva de las capacidades. Sin servidores ni conectores Business Central/SharePoint; R3C no se implementa ahora.

## R3B1 — implementación en revisión

Rama `feature/r3b1-qt-advanced-editor`: [alcance, límites y pruebas](docs/R3B1_QT_EDITOR.md). Editor Qt conserva la composición Industrial Moderno y añade recorte visual/mm, anclas explícitas del PDF, relocalización acotada, reserva de estado, modos de dibujo y geometría auxiliar, alineación/distribución, reajuste proporcional y deshacer/rehacer completo. Formato físico/perfiles y PDF de prueba reutilizan el motor. Guardado explícito del diseño completo con comparación transaccional e integridad; esquema SQLite permanece en versión 3.

Sin implementación R3B2/R3B3: variantes continúan en el modelo heredado; no hay autoguardado de trabajos ni sincronización de variables Editor/Emisión. Emisión definitiva y módulos no migrados mantienen Tkinter/puente. La aprobación documental de 00-R1 y las pruebas reales pendientes no cambian.

## Estado vigente — R3C en revisión (15/10/2026)

Las notas anteriores conservan la planificación histórica y no describen el estado
actual de main. R3A/B1/B2/B3 están integradas en la base obligatoria indicada arriba.
SQLite es v4, con variantes independientes y trabajos JSON recuperables.

R3C1: Centro de emisión Qt, selección revisión/variante/trabajo, datos de lote y
recipientes, perfiles/A4, vista previa PDF real, prueba y emisión definitiva por
WorkRepository. R3C2: historial Qt y reimpresión controlada mediante servicio común
Qt/Tk. R3C3: consolidación Industrial Moderno, resumen legible del PDF y «Cerrar»
(incidencia #7), regresión, capturas sintéticas y portable Windows por CI.

Sin migración adicional ni reescritura del motor. Maestro y textos fijos protegidos;
00-R1 continúa PENDING. 87 capacidades conservadas: 66 Qt, 4 parciales, 10 anteriores,
7 motor. Tk permanece para comparación de imágenes, importación por carpeta y
Configuración/CM/maestros de estado/auditoría/Inicio heredado.

[Implementación R3C](docs/R3C_IMPLEMENTATION.md) · [Paridad y pruebas](docs/R3C_PARITY.md)
· [Matriz de 87 capacidades](docs/FUNCTIONAL_PRESERVATION_MATRIX.md).

Entrega sujeta a revisión de PR, sin squash/merge autorizado. CI se ejecuta sobre
el commit entregado; enlaces y resultados en la PR. Word real, impresión física,
Windows 10/11/equipos COVEX, aceptación y validación GMP siguen pendientes.

## R8A — Estabilización y diagnóstico (pendiente de revisión)

Auditoría de ciclos de vida, protección de borradores y concurrencia, diagnóstico
local privado y exportable, estrés sintético source/portable extraído. Sin migración
ni retirada de capacidades. [Alcance, evidencia y pruebas](docs/R8A_STABILITY_DIAGNOSTICS.md).
No atribuye sin evidencia los cierres intermitentes a una causa única. R8B (Editor),
R8C (propiedades visuales de estados) y R8D (asistentes) siguen fuera de alcance.
