# Arquitectura local de COVEX Label Manager

Aplicación 0.3.1, consolidación de R1/R2. Escritorio portable Windows, un usuario, funcionamiento local. Sin servidores, microservicios, clientes ERP ni infraestructura de integración.

## Organización actual

| Módulo | Responsabilidad |
|---|---|
| `gui.py` | Interfaz de emisión, editor de campos, administración e historial heredados. |
| `library_ui.py` | Biblioteca R2: búsqueda, filtros, selección y previsualización. No consulta SQLite. |
| `services.py` | Fachada local de casos de uso: importación, renderizado, lectura de maestros, destinos de salida, integridad y backup. |
| `library_service.py` | Reglas de búsqueda, filtros, favoritos, recientes y metadatos; independiente de Tk y SQLite. |
| `contracts.py` | Protocolo `LibraryRepository`, claves de filtros y metadatos. |
| `storage.py` | SQLite, consultas, migraciones, versiones, auditoría y archivos controlados. |
| `engine.py` | Composición PDF/A4, datos por envase, validaciones geométricas y estados. |
| `integrity.py` | Integridad de documentos y bloqueo de huella conocida defectuosa antes de aprobación/renderizado. |
| `render_geometry.py` | Adaptación controlada de la tabla anidada Edrofonio. Genera un PDF derivado pendiente. |
| `geometry.py`, `vessels.py` | Geometría de maestros y validaciones de datos por recipiente. |
| `importer.py`, `cm.py`, `paths.py` | Conversión local, lectura CM y rutas de instalación/datos. |
| `resources/` | Directorio reservado; no distribuye referencias, documentos ni datos originales. Pruebas generan fixtures ficticios fuera del paquete. |
| `tests/`, `docs/`, `.github/` | Verificación, evidencias, documentación y preparación de CI. |

La UI consume servicios locales. Se han extraído el SQL de auditoría, la copia de SQLite, la lectura de maestros, la importación y los destinos de salida que antes residían en `gui.py`. La ventana ya no tiene acceso público a `.db` o `.root`. Las rutas devueltas para abrir un PDF pertenecen a un caso de uso, no a una consulta SQL desde la UI.

Para conservar compatibilidad sin reescribir toda la aplicación, `LocalServices` tiene una lista explícita de operaciones heredadas delegadas al repositorio. No es un contenedor de dependencias ni un servicio de red. La Biblioteca nueva dispone además de un contrato propio. Cuando se extraigan otras pantallas se sustituirá esa compatibilidad por métodos de caso de uso explícitos. El motor conserva sus funciones probadas, invocadas por la fachada.

## Identidad, configuración y persistencia

- Los enteros actuales siguen siendo claves internas y se conservan las referencias históricas.
- Etiquetas, versiones, materiales del catálogo y emisiones disponen además de `uid` estable, aleatorio de 128 bits, persistido y con índice único. No se utiliza el código de producto como identidad única porque CM contiene códigos repetidos.
- El producto de fabricación todavía no es una entidad formal asociada a etiqueta: `materials.uid` identifica los registros del catálogo y `product` es un metadato opcional documentado. La asociación formal queda en ROADMAP; no se inventan registros de producto.
- Hoy una versión contiene la plantilla PDF y su configuración. `version_uid` identifica esa plantilla concreta. No hay todavía una entidad independiente de plantilla nativa/variante; al introducirla en R3 se asignará UID propio y relación explícita con la revisión original, conservando `version_uid`.
- `label_metadata` guarda clave, valor y referencia fuente. Campos desconocidos permanecen vacíos. Las claves ampliables se registran en `contracts.py`; el servicio no deduce valores del nombre.
- Origen del diseño, incorporación y estado documental son atributos diferentes. La importación no concede vigencia.
- Preferencias guardan favorito por etiqueta y última revisión utilizada. No modifican el diseño aprobado.
- `data/` vive fuera del código. Incluye SQLite, originales, PDFs, emisiones y backups; `COVEX_LABEL_DATA` permite una ubicación absoluta alternativa.
- Migración aditiva con snapshot SQLite previo y `PRAGMA user_version=3`. Nuevas identidades no cambian claves numéricas ni registros históricos. Los nuevos datos se crean con UID mediante triggers.
- Copia ZIP usa `Connection.backup`, incluyendo el estado confirmado del WAL; evita copiar una base activa de manera inconsistente. No incluye cache ni otras copias.

R1 crea `00-R1` pendiente solo desde la fuente 00 ya almacenada localmente y con huella conocida e íntegra. No necesita distribuir documentos originales. Nunca sobreescribe una revisión aprobada o campos personalizados. La fuente 00 se conserva para consulta, pero se bloquea su emisión por el defecto conocido. La referencia derivada documenta el reajuste interior al marco físico exterior; debe revisarse antes de activarla.

## Contratos futuros sin implementarlos ahora

Un adaptador externo podrá obtener datos y transformarlos al modelo del caso de uso, sin entrar en Tk ni ejecutar SQL del repositorio. La base local seguirá siendo el sistema autónomo. Para una futura entrada externa se deberían incluir: `source_system`, identificador externo, fecha de lectura, correspondencia de campos, valores recibidos, resultado de validación y estado de revisión. Estos atributos de sincronización **no se han implementado** en esta fase; la referencia de metadatos actual no equivale a un motor de sincronización.

### Business Central

Posibilidad futura: adaptador que consulte las API REST oficiales disponibles para el entorno COVEX y utilice autenticación Microsoft Entra/OAuth. Antes de desarrollarlo habrá que confirmar despliegue online/on-premises, versión, sociedad, permisos, entidades disponibles y si se necesitan API propias para campos no expuestos. No se presupone que lotes, fechas u órdenes estén accesibles por un endpoint estándar concreto.

Correspondencia de códigos, denominaciones, clientes, lotes y órdenes se definiría sobre una muestra real de datos. Validar campos, fechas/unidades, duplicidades y versiones de origen antes de proponer datos para emisión. Tratar errores o conflictos como incidencias revisables, sin sobrescribir información local confirmada automáticamente. Business Central no está validado GMP en COVEX: datos recibidos serían propuestas de origen externo, y no podrían activar ni modificar plantillas aprobadas.

Para una app portable interactiva se estudiaría autenticación de usuario con almacenamiento protegido por Windows. No incluir secretos de aplicación ni tokens en el ejecutable, ZIP, SQLite o Git. Un posible acceso desatendido exige una decisión posterior de IT; no se instala infraestructura para ello ahora.

Referencias oficiales consultadas el 08/10/2026:

- [API v2.0 de Business Central](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/)
- [OAuth y Microsoft Entra para Business Central](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/authenticate-web-services-using-oauth)

### SharePoint y otras aplicaciones

Un adaptador documental futuro descargará una copia, registrará identificadores de documento/versión y huella y la presentará como pendiente de revisión. No se usará SharePoint como ubicación de SQLite activo. Otras apps COVEX intercambiarían datos por un contrato versionado de exportación/API; no mediante escritura directa en sus tablas. No hay conectores ni credenciales en esta entrega.

## Riesgos y deuda técnica acotada

`gui.py` sigue siendo grande y contiene coordinación de pantallas heredadas. No bloquea futuras integraciones porque sus accesos a persistencia/renderizado pasan por servicios, pero su extracción por casos de uso debe continuar cuando se modifique cada módulo. El editor actual no es composición nativa completa. La auditoría local no es inviolable. Un futuro entorno multiusuario requerirá repositorio central y controles de concurrencia/acceso; no bastará con compartir este SQLite. Son decisiones posteriores, no infraestructura instalada preventivamente.

## Preparación GitHub

La copia recibida no tenía Git. Ahora hay repositorio local con referencia documental `v0.3.0-reference` y rama de consolidación sin originales; todavía sin remoto. Se ha comprobado la cuenta FMAcovex: no aparece un repositorio Label Manager. Consulte `GITHUB_PREPARATION.md`: estructura, exclusiones de datos, CI de pruebas y generación Windows preparados. Antes de R3 conviene guardar esta base en un único repositorio privado y verificar una compilación Windows. No se ha creado un repositorio remoto.

## Viabilidad de R3

Biblioteca, búsqueda, repositorio y motor son reutilizables mediante servicios locales. R3 podrá sustituir o reorganizar las vistas en biblioteca/editor central/propiedades sin cambiar SQLite ni los maestros. Extraer los controladores grandes de `gui.py` al modificar cada pantalla y definir casos de uso explícitos para abrir revisión, modificar borrador, previsualizar y guardar. No prometer composición nativa de tablas/textos fijos: hoy el editor ajusta campos sobre PDF. Elegir Tkinter reorganizado o PySide6 tras validar el diseño y el coste de migración. No se ha implementado ese cambio.

En 0.3.1 `LocalServices.render` vuelve a leer la revisión persistida, evitando emitir desde una selección antigua ya retirada. El motor mantiene también el control de aprobación; `Store.add_issue` rechaza el registro de revisiones no aprobadas. Integridad documental se comprueba antes de aprobar o clonar. Ninguno de estos controles convierte la auditoría SQLite en un registro inviolable.

## Distribución sin documentación confidencial

El repositorio y portable no contienen maestros, etiquetas reales ni catálogo. SQLite, fuentes y PDFs se conservan únicamente en data/ o COVEX_LABEL_DATA. Una instalación nueva empieza vacía; la misma carpeta de datos mantiene maestros y configuraciones al actualizar. Tests usan generadores de documentos planos con aviso SYNTHETIC; nunca una redacción o reproducción de etiquetas reales. El historial remoto parte de una referencia documental, porque el historial anterior contenía originales. La referencia histórica no se presenta como copia binaria exacta de esa entrega. El build rechaza data, SQLite o una ruta COVEX_LABEL_DATA bajo el destino de reconstrucción. No hay actualizador que copie una base inicial sobre datos del usuario.


## Repositorio operativo y transición R3A Qt

FMAcovex/covex-label-manager es el repositorio privado oficial, main 0.3.1 y Actions Windows operativos. No se integra directamente PR #2 ni #3. `feature/r3a-qt-functional` mantiene `main.py`, `gui.py`, motor, esquema SQLite y rutas existentes sin cambios.

- `main_qt.py`: entrada opcional Qt, separada del ejecutable distribuido; modo demo/verificación explícito y temporal.
- `qt_ui/`: widgets Industrial Moderno y controlador de Biblioteca/trabajo activo. No lee SQLite, maestros ni carpetas por su cuenta: utiliza servicios.
- `qt_transition.py`: fachada local pequeña que amplía servicios existentes con elegibilidad documental, acceso a documentos y preferencias. Sin API/red/infraestructura.
- `qt_legacy.py` y `legacy_qt_bridge.py`: aplicación Tk en proceso independiente, misma carpeta de datos y revisión seleccionada. Un solo compañero a la vez; Qt bloquea edición mientras esté abierto y refresca al cerrarse. Tk y Qt no comparten bucles de eventos. La distribución anterior conserva su entrada original.
- Configuración de campos Qt: cambios en memoria, guardado explícito de pendiente mediante `replace_pending_fields`, detección de estado o configuración externos antes de guardar, Guardar/Descartar/Cancelar al cambiar/cerrar. Sin autoguardado ni recuperación R3B. El ajuste completo de recorte/estado/Word sigue en Tk.
- Configuraciones Qt usan nuevas claves `qt_remember_filters`/`qt_filters_expanded` en la tabla settings existente. No se modifica esquema ni se reemplazan maestros, preferencias anteriores o histórico.

El paquete experimental contiene Qt y compañero Tk; ninguno incluye data o documentos originales. El compañero recibe COVEX_LABEL_DATA desde la ubicación de servicios Qt. Se prueba con datos ficticios y con PDF de prueba marcado sin alta de emisión, también para revisiones vigentes. Conservación del 100 % exige la matriz de 87 capacidades, regresión y aceptación del propietario antes de sustituir la distribución. Integraciones futuras continúan documentadas conceptualmente, sin conexiones reales ni infraestructura nueva.
## Composición Qt R6B-UX

`qt_ui/responsive.py` adapta cuerpos y pies de diálogos sin intervenir en servicios;
`workspace.py` compone paneles existentes dentro del Editor y fija acciones del Inspector;
`revision_browser.py` consulta revisiones/variantes mediante los servicios existentes.
El WorkPanel conserva su controlador y persistencia, pero ya no es un dock global.
SQLite v4, contratos PDF, snapshots y guardas documentales no cambian.
Ver [rutas y equivalencia funcional](docs/R6B_UX_INTEGRATED/CAMBIOS_Y_ESTADO.md).

La [ampliación tras NO CONFORME](docs/R6B_UX_INTEGRATED/CORRECCIONES_ACEPTACION.md) incorpora un asistente sobre R5B, unidades kg/g/mg y `PreviewTask`: QThread espera un único proceso `preview_render` no productivo, con conexión SQLite y estado MuPDF propios, snapshot de entrada y comprobación de generación/token antes de adoptar el PDF. El render no comparte los hilos del visor Qt ni mantiene el bloqueo exclusivo de trabajo; no registra emisiones. El sufijo documental determina la conversión de masa, sin modificar maestros ni SQLite v4. Los contadores de importación no pueden ocultar `QDialog.done(int)`.
Las secciones anteriores documentan la evolución previa.

## R8A: ciclo de vida y diagnóstico privado

`diagnostics.py` registra únicamente eventos técnicos de esquema cerrado y exporta
un ZIP separado del backup documental. El cierre drena PreviewTask antes de liberar
servicios; la geometría de un gesto se confirma sin destruir el QGraphicsItem dentro
de su evento nativo. Los borradores de estado avisan al descartar y cotejan el hash
esperado dentro de su transacción. Sin esquema nuevo ni cambio del motor.
Ver [auditoría, intervención y límites](docs/R8A_STABILITY_DIAGNOSTICS.md).
