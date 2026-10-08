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

## Repositorio oficial operativo

Fuente oficial: repositorio privado `FMAcovex/covex-label-manager`, rama `main`. PR #1 integrada; `v0.3.1` identifica `bd6e92e11f2116f18bec8dd2ab9cf0bf61fef16e`. Actions #7 generó portable y pasó 49 tests (1 omitido), además de comprobar el núcleo del EXE en Windows Server 2022. `v0.3.0-reference` es una referencia documental sin originales.

Main carece de protección efectiva por el plan actual. Todas las revisiones se incorporan por ramas y PR, sin commits directos ni force push. R3A se presenta en `feature/r3a-studio-navigation`; su PR no se integra sin autorización del propietario. No se publican maestros/documentos/datos de usuario ni credenciales.

## Viabilidad de R3

Biblioteca, búsqueda, repositorio y motor son reutilizables mediante servicios locales. R3 podrá sustituir o reorganizar las vistas en biblioteca/editor central/propiedades sin cambiar SQLite ni los maestros. Extraer los controladores grandes de `gui.py` al modificar cada pantalla y definir casos de uso explícitos para abrir revisión, modificar borrador, previsualizar y guardar. No prometer composición nativa de tablas/textos fijos: hoy el editor ajusta campos sobre PDF. R3A reorganiza Tkinter, con la decisión y limitaciones descritas al final de este documento. La migración a PySide6 no se ha iniciado.

En 0.3.1 `LocalServices.render` vuelve a leer la revisión persistida, evitando emitir desde una selección antigua ya retirada. El motor mantiene también el control de aprobación; `Store.add_issue` rechaza el registro de revisiones no aprobadas. Integridad documental se comprueba antes de aprobar o clonar. Ninguno de estos controles convierte la auditoría SQLite en un registro inviolable.

## Distribución sin documentación confidencial

El repositorio y portable no contienen maestros, etiquetas reales ni catálogo. SQLite, fuentes y PDFs se conservan únicamente en data/ o COVEX_LABEL_DATA. Una instalación nueva empieza vacía; la misma carpeta de datos mantiene maestros y configuraciones al actualizar. Tests usan generadores de documentos planos con aviso SYNTHETIC; nunca una redacción o reproducción de etiquetas reales. El historial remoto parte de una referencia documental, porque el historial anterior contenía originales. La referencia histórica no se presenta como copia binaria exacta de esa entrega. El build rechaza data, SQLite o una ruta COVEX_LABEL_DATA bajo el destino de reconstrucción. No hay actualizador que copie una base inicial sobre datos del usuario.


## R3A: decisión de interfaz y conservación de sesión

Se mantiene Tkinter/ttk en R3A. La reorganización moderna de Biblioteca y navegación se logra sin reemplazar servicios, motor ni almacenamiento. `studio_ui.py` contiene la cabecera horizontal y el contenedor de vistas; `library_ui.py` reutiliza LibraryService y presenta filtros, tabla e inspector en paneles ajustables/ocultables. La UI recibe imágenes y datos por LocalServices; no lee SQLite ni documentos directamente.

Las pantallas se crean una vez y se conservan al navegar. Los filtros/selección de Biblioteca y datos de emisión permanecen en memoria. El Editor incorpora el componente de campos existente, reutilizable también en su ventana independiente, y conserva ajustes al salir y volver. Cambiar a otra revisión con datos/ajustes sin guardar requiere confirmación; no se transfieren lotes a otra etiqueta. Esto **no es autoguardado ni recuperación tras reinicio**: dichos trabajos persistidos pertenecen a R3B. El historial actualiza su listado al entrar; Biblioteca refresca registros/facetas conservando filtros.

`LocalServices.emission_eligibility` consulta el estado persistido y las guardas de integridad existentes para habilitar Preparar emisión. No sustituye el preflight ni aprueba un documento. Las revisiones pendientes siguen accesibles para inspección/edición y PDF de prueba mediante Emisión; la emisión definitiva mantiene los controles existentes.

R3A no añade entidad de variante ni migra la base (schema 3), y no cambia funciones de composición PDF. La estructura documental actual lista revisiones y permite consultar sus referencias; 00-R1 continúa pendiente. El modelo separado de variantes y trabajos, sincronización Editor/Emisión, autoguardado y recuperación se abordarán en R3B, y el Centro de emisión/preflight en R3C. R2.5 sigue pendiente: solo se conserva el comparador básico ya existente.

### Tkinter frente a PySide6

Tkinter: menor riesgo y dependencias, reutilización íntegra de diálogos y controles, portable ya probado. Permite renovar composición, tipografía UI, colores y paneles, pero exige más trabajo manual para herramientas de un editor complejo. PySide6: Qt Widgets aporta QMainWindow/QDockWidget/QSplitter y una base más rica para un Studio avanzado; requeriría adaptar pantallas/diálogos/eventos, fijar dependencias adicionales y validar plugins y tamaño del portable. La distribución Qt también exige revisar las condiciones de licencia de los módulos elegidos. No se añade Qt ni se afirma que esa migración esté aprobada.

Ambas opciones permiten build Windows: se conserva el workflow PyInstaller onedir con dependencias/hashes existentes. Un cambio futuro a Qt mantendría motor/repositorio y exigiría verificar el empaquetado Qt en Windows, sin servidores ni base remota. Referencias oficiales: [ttk](https://docs.python.org/3/library/tkinter.ttk.html), [QMainWindow](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QMainWindow.html), [PyInstaller Qt hooks](https://pyinstaller.org/en/v6.16.0/hooks-config.html).

R3B y R3C solo comenzarán tras integración autorizada de su fase precedente. En ninguna fase se implementan ERP/SharePoint, firma electrónica o aprobación multiusuario. La aprobación real se realiza fuera de la aplicación; el registro administrativo y su evidencia no constituyen firma GMP.
