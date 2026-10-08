# COVEX Label Manager — Plan maestro vivo

Versión de aplicación: 0.3.1 (consolidación de R1/R2; referencia histórica `v0.3.0-reference` sin originales). Revisado: 08/10/2026.

Este inventario contrasta las propuestas aceptadas del chat con README, traspaso, código, pruebas y muestras del proyecto recuperado. **Aprobada** significa acordada como requisito; no significa implementada ni validada GMP. Solo se consideran implementadas las funciones verificadas en este paquete. La comprobación física en Windows/impresora sigue pendiente.

Leyenda: **Implementada** = código verificado; **Parcial** = existe una parte indicada; **Pendiente** = acordada, aún sin desarrollo; **Propuesta** = posibilidad que necesita concretarse. La versión de software y los hitos R1–R5 no son equivalentes.

## Prioridad y secuencia

R1/R2 consolidados en 0.3.1 → R3A (Biblioteca y navegación) → revisión e integración autorizada → R3B (Editor y trabajos) → revisión e integración autorizada → R3C (Emisión y controles). R2.5 continúa pendiente, sin descartarse; se programará expresamente. R4/R5 siguen posteriores. R3A se desarrolla en rama para revisión. No se ha desarrollado R2.5, R3B, R3C, R4, R5 ni conexiones externas.

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
| R3 | Identidad visual Label Studio, editor central y propiedades contextuales | Aprobada como fase | Pendiente de propuesta y validación visual antes de implementación. R2 introduce identidad de biblioteca, sin rediseñar toda la aplicación. |
| R3 | Migración de Tkinter a PySide6 | Propuesta aceptada como dirección | Pendiente de decisión técnica de R3. Actualmente Tkinter. No se requiere para el funcionamiento local de R1/R2. |
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
| Diseño | Reajuste avanzado | Aprobada | Parcial: editor de campos, posiciones en mm, recorte, anclas PDF y zona de estado; R1 variante derivada específica. Recolocar libremente textos fijos, tablas, pictogramas e imágenes requiere R3. |
| Diseño | Variantes por envase/material con aprobación independiente | Aprobada | Parcial: R1 usa revisión pendiente identificada. Modelo general de variantes separado de revisión documental pendiente. |
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
| Entrega | Portable Windows sin servidor | Aprobada | Fuentes y compilación `--onedir` preparados; EXE sin compilar/verificar en este entorno. |
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
| R3 | No implementado. Próximo paso: diseñar y aprobar visualmente biblioteca, editor central y propiedades; decidir tecnología de interfaz antes de programar. |

## Política de publicación y desarrollo oficial

Solo código, pruebas sintéticas y documentación técnica. No maestros, etiquetas reales, catálogo, emisiones, bases, capturas reales ni historial que contenga esos documentos. 00-R1 sigue PENDING hasta aprobación documental local; un tag/PR/build no la aprueba. Una instalación nueva tiene biblioteca vacía. Todas las revisiones posteriores se realizan en ramas y PR, con pruebas y revisión antes de integrar en main. R3 no iniciado.


## Secuencia R3 aprobada — 08/10/2026

| Fase | Alcance aprobado | Estado |
|---|---|---|
| R3A | Inicio en Biblioteca; cabecera horizontal Biblioteca/Editor/Emisión/Historial/Configuración; tres paneles, filtros y búsqueda inmediata, favoritos/recientes, Ctrl+K, doble clic y acciones; conservación del trabajo durante navegación | Implementación en rama, pendiente de revisión visual e integración autorizada. Tkinter/ttk renovado. |
| R3B | Editor central profesional, Vista/Preparar emisión/Ajuste avanzado; datos sincronizados; autoguardado local, recuperación/descartar/eliminar trabajos; maestro/revisión/variante/trabajo/emisión diferenciados; formatos reutilizables y controles sobre cambios estructurales | Aprobado, pendiente. No comenzado. |
| R3C | Centro de emisión con hoja/preflight Correcto/Advertencia/Bloqueo, prueba frente a definitiva, historial operativo y evidencia externa de aprobación; distinguir PDF/solicitud de impresión/confirmación física | Aprobado, pendiente. No comenzado. |
| R2.5 | Comparador visual de versiones, superposición y diferencias | Aprobado, pendiente. Se conserva acceso al comparador básico existente; no sustituye R2.5. |

Cada fase tendrá rama/PR/pruebas/capturas propias y requiere autorización antes del merge. R3B parte de R3A ya integrada y R3C de R3B ya integrada. R3A no introduce guardado automático de trabajos ni nuevas migraciones y no cambia geometría PDF. Vista de tabla predeterminada; tarjetas opcionales pospuestas. No inventar metadatos/elementos editables; las limitaciones del formato fuente deben ser visibles.

Aprobación externa: registrar responsable, fecha, referencia/evidencia y vigencia cuando se implemente su alcance en R3B/R3C, sin firma electrónica, autenticación compleja ni circuito multiusuario. Una modificación invalidante requerirá nueva aprobación; guardar/tag/build no aprueba. 00-R1 permanece pendiente.
