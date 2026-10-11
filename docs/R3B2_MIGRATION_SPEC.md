# R3B2 — Especificación de migración y variantes controladas

Estado: **PROPUESTA PENDIENTE DE APROBACIÓN; NO IMPLEMENTADA**. Fecha: 11/10/2026.
Repositorio: `FMAcovex/covex-label-manager`. Base comprobada mediante árbol remoto: `e83953b023a6c40702a276745a1fcaeae278dbd1` (main, squash PR #6). Rama: `chore/r3b2-migration-spec`.

Esta entrega contiene documentación, no DDL ejecutable, migrador ni modificaciones de aplicación o datos. La aprobación de esta especificación autorizará el desarrollo posterior en una PR verificable; no implica merge, despliegue ni aprobación documental de etiquetas. R3B3, R3C, incidencia #7 y conectores quedan fuera.

## 1. Contraste con el código actual y la PR #5

Se inspeccionaron `storage.py`, `services.py`, `editor_layout.py`, `integrity.py`, `engine.py`, `library_service.py`, `qt_ui/functional.py`, `qt_ui/advanced_editor.py`, `qt_legacy.py`, `qt_transition.py`, `gui.py`, las instrucciones de actualización y la matriz. No se abrió ninguna base COVEX. La PR #5 se consultó en `6a24bd4ed4eb1a98af860587cf6393cc9a2a6d0d`; no se integra ni se copia su ROADMAP antiguo.

| Hallazgo en main | Consecuencia para R3B2 |
|---|---|
| `versions` conserva fuentes, geometría y aprobación juntas | Se mantiene como revisión heredada; variantes hijas separadas, sin transformar registros existentes. |
| `Store.approve` retira TODAS las revisiones APPROVED de una etiqueta | Nuevo servicio de aprobación de variantes; nunca delegar en `approve`. La política histórica de revisión se conserva. |
| `_schema` comprueba columnas, crea tablas/triggers y fija siempre `user_version=3` | Sustituir inicialización por despacho de migraciones ordenadas, con validación previa y sin rebajar versiones. |
| `_backup_before_migration` detecta columnas concretas y copia solo SQLite | No detectaría esta ampliación. Hace falta backup completo consistente y manifiesto verificable antes del cambio. |
| `save_pending_layout` compara diseño completo y fuente en `BEGIN IMMEDIATE` | Reutilizar validación geométrica y concurrencia, pero escribir variantes por otro método y por generación. |
| `layout_from_version` usa campos, recorte y zona de estado; `version_with_layout` crea un diccionario nuevo | Base adecuada para adaptador sin escribir ni sustituir `versions`. |
| `LocalServices.render` recarga revisión por ID, descartando cualquier geometría enviada por UI | Resolver revisión + variante dentro del servicio; enviar un DTO resuelto al motor después de revalidar. |
| `issues` guarda variables, perfil, estado, PDF/hash y enlace de reimpresión, pero no snapshot de diseño | Añadir asociación opcional y snapshot solo para emisiones NUEVAS; no inventar snapshots históricos. |
| Reimpresión Tk reconstruye desde revisión actual | Con snapshot nuevo, resolverlo explícitamente; históricos sin snapshot mantienen ruta heredada y muestran esa limitación. |
| Puente pasa destino, revisión y carpeta, no variante | Añadir selección opcional de variante a ambos extremos del puente empaquetado; no introducir trabajos/autoguardado. |
| `_seed_r1_variant` realmente crea `versions.version='00-R1'` | Sigue siendo revisión heredada PENDING; no se mueve, clona ni aprueba por migración. |

La PR #5 recomendaba `source_documents` y variantes PENDING/APPROVED/RETIRED sin concretar la barrera antigua. Esta propuesta sustituye esas recomendaciones para R3B2: no tabla de fuentes; DRAFT explícito; evidencia local identificada; protocolo de corte y bloqueo antiguo verificable. R3B1 ya está integrado: sus herramientas no son pendientes como decía el plan original.

## 2. Separación persistente y alcance mínimo

| Concepto | Persistencia/contrato |
|---|---|
| Maestro original protegido | Archivos actuales `sources`, `pdf_masters`, `status_masters` y rutas/hashes de revisión. Comprobación de integridad; ninguna operación de variante escribe estos archivos. |
| Revisión documental | `versions`, conservando ID, UID, código, estados, geometría heredada, fuentes y aprobación. |
| Variante reutilizable | Nueva `design_variants`, hija de una revisión exacta. Layout completo propio y tamaño nominal; no archivos maestros duplicados. |
| Futuro trabajo de emisión | Contrato reservado `{revision_uid, variant_uid|null, design_hash}`; NO tabla de trabajos, datos de lote persistidos ni autoguardado en R3B2. |
| Emisión histórica | `issues` intacta en sus columnas anteriores; nuevas columnas opcionales para variante y snapshot. |

**No hace falta `source_documents`:** `versions.original_file/source_sha256` y `master_pdf/pdf_sha256` ya identifican original y PDF de referencia, y la variante puede resolverlos por FK. Una segunda tabla duplicaría autoridad, exigiría backfill y reconciliación de rutas sin aportar una relación necesaria. No se añade `master_id` redundante. Si en otro hito se requieren varios archivos fuente por revisión, deduplicación o un ciclo documental independiente, se estudiará entonces. Las evidencias externas son archivos de aprobación, no maestros ni sustitutos del original.

Protegido significa inmutable por los servicios y verificado por hash; no protección absoluta contra un administrador que manipule SQLite o el disco. No se presenta auditoría local como firma electrónica o registro inviolable.

## 3. Esquema propuesto: versión SQLite 4

**DOS tablas nuevas:** `schema_migrations` y `design_variants`. Se reutiliza `audit` para los eventos, sin tabla adicional de eventos. Tres columnas nuevas en `issues`. Ninguna eliminación/renumeración de filas o columnas anteriores. No nueva tabla de revisiones, fuentes, trabajos o snapshots: cada snapshot pertenece a su emisión.

### 3.1 `schema_migrations`

| Campo | Tipo y restricción |
|---|---|
| `version` | INTEGER PRIMARY KEY; positivo; esta migración registra 4 |
| `migration_id` | TEXT NOT NULL UNIQUE, `r3b2_variants_v4` |
| `migration_checksum` | TEXT NOT NULL; SHA-256 del contrato de migración distribuido |
| `applied_at`, `app_build` | TEXT NOT NULL; instante con zona y versión/build exacto |

No fabricar filas para migraciones antiguas: su origen se identifica por inspección de esquema, versión 3 y manifiesto previo. El backup y las fases de corte van en manifiesto externo, no en la DB que podría estar dañada. Además, `settings` conserva claves nuevas `storage_format=4`, `minimum_writer_protocol=4`. Son controles para binarios NUEVOS; por sí solos no bloquean el antiguo.

### 3.2 `design_variants`

| Campo | Tipo/restricción/propósito |
|---|---|
| `id` | INTEGER PRIMARY KEY |
| `uid` | TEXT NOT NULL UNIQUE; 32 hex minúsculas, generado antes del INSERT, no vacío |
| `revision_id` | INTEGER NOT NULL REFERENCES versions(id), ON DELETE/UPDATE RESTRICT |
| `origin_variant_id` | INTEGER NULL REFERENCES design_variants(id), RESTRICT; distinto de sí mismo y misma revisión |
| `code` | TEXT NOT NULL; identificación normalizada, estable; UNIQUE(revision_id,code) |
| `name`, `reason` | TEXT NOT NULL, trim no vacío; denominación y motivo explícitos |
| `state` | TEXT NOT NULL, CHECK IN ('DRAFT','PENDING','APPROVED','RETIRED'); DRAFT por defecto |
| `design_contract` | INTEGER NOT NULL CHECK =1 |
| `design_json` | TEXT NOT NULL, objeto JSON validado por servicio; contrato descrito abajo |
| `design_sha256` | TEXT NOT NULL; SHA-256 canónico exacto del diseño; 64 hex minúsculas |
| `base_revision_sha256` | TEXT NOT NULL; huella canónica de identidad documental + layout de revisión al crear; 64 hex |
| `generation` | INTEGER NOT NULL DEFAULT 1, CHECK >0; comparación optimista de cada mutación |
| `created_at`, `created_by`, `updated_at` | TEXT NOT NULL; instantes con zona y operador local identificado |
| `approved_by`, `approval_ref`, `approval_date` | TEXT NULL; responsable externo, referencia y fecha documental ISO YYYY-MM-DD |
| `approval_recorded_at`, `approval_recorded_by` | TEXT NULL; instante/operador que registra la aprobación en la aplicación |
| `approved_design_sha256` | TEXT NULL; hash exacto aprobado, igual a design_sha256 |
| `evidence_path`, `evidence_sha256` | TEXT NULL; ruta relativa al data y hash SHA-256 de evidencia copiada, sin sobrescritura |
| `retired_at`, `retired_by`, `retirement_reason` | TEXT NULL; obligatorios al retirar/cancelar |

Una evidencia documental por aprobación es el mínimo: si son varios documentos, incorporar un expediente único PDF o ZIP y verificar su hash. No construir un gestor de adjuntos en este hito. Guardar en `approval_evidence/<variant_uid>/<sha256>.<ext>`; no guardar solo un enlace mutable. Abrir carpeta para consultar ZIP sin extraer contenido automáticamente. Rutas fuera de data, enlaces simbólicos que escapen y nombres peligrosos se rechazan.

Restricciones SQL: UID/hash con longitud y alfabeto correctos; name/reason/code no vacíos; metadatos de aprobación completos en APPROVED; ausencia de todos ellos en DRAFT/PENDING; RETIRED conserva todos los campos de aprobación o ninguno (cancelación anterior a aprobar), nunca parciales. Metadatos de retirada completos solo en RETIRED. `approved_design_sha256=design_sha256` cuando haya aprobación. Fecha e instantes se validan además en servicio. JSON válido mediante CHECK `json_valid/json_type`: su disponibilidad en las librerías SQLite del portable es precondición probada, no un CHECK omitido silenciosamente.

Índices: UID y `(revision_id,code)` únicos; `(revision_id,state,id)` para selector; `origin_variant_id` para derivados. No índice de unicidad parcial por APPROVED: impediría coexistencia. Código: trim + uppercase ASCII `[A-Z0-9][A-Z0-9._-]{0,39}` para comparación estable; nombres admiten Unicode. Identidad completa etiqueta/revisión/código y UID global, no código global forzado.

Triggers de defensa: identidad `id/uid/revision_id/origin_variant_id/code/created_*` inmutable; origen debe existir en misma revisión al INSERT y no ser self-reference; vínculo solo a fila existente impide ciclos nuevos porque después no puede cambiarse. No DELETE de variantes. APPROVED permite únicamente transición a RETIRED con motivo, auditoría de servicio y generation+1; todos los demás campos se conservan. RETIRED no permite UPDATE ni reaprobación. PENDING no permite cambiar diseño/nombre/motivo: volver a DRAFT explícitamente. Transiciones fuera de la tabla de §4 se rechazan. Comprobaciones geométricas/hashes de disco no se atribuyen a triggers SQLite: se hacen en servicio.

`design_json` contrato 1: `{layout:{fields:[],crop:[x0,y0,x1,y1],area:[]}, nominal_size_mm:{width,height}}`. Se preservan todas las claves de campos R3B1 (anclas, locked, draw, erase, second_x, next_w, tipografía, etc.), sin proyección que las pierda. Recorte en puntos PDF; campos/área en coordenadas normalizadas, como hoy. Dimensiones nominales positivas finitas y proporcionales al recorte: tolerancia de ratio 1e-6; no deformar fondo. Default nominal calculado sin redondear con 25.4/72. Cambiar nominal al adaptar un envase es cambio aprobado de variante; una escala puntual de impresión admitida por el motor sigue siendo perfil de emisión y se guarda en su snapshot. No se promete remaquetación libre del contenido fijo del PDF.

Hash: JSON UTF-8 canónico, claves ordenadas, separadores sin espacios, sin NaN/Infinity, arrays en orden; números finitos normalizados a representación definida por contrato, -0→0. Se prueban vectores de hash fuentes/portable. `design_sha256` cubre contrato, layout y nominal. `base_revision_sha256` cubre UID revisión/etiqueta, código revisión, origen/referencia cliente, rutas/hashes fuente y PDF y layout heredado; excluye estado/fechas de aprobación para permitir aprobar luego la revisión pendiente. Nombre/motivo quedan congelados por reglas de aprobación y registrados junto al hash en audit. Un cambio de base relevante exige crear otra variante desde la base actual; no actualizar automáticamente esa huella.

### 3.3 Ampliación de `issues`

| Columna | Restricción |
|---|---|
| `design_variant_id` | INTEGER NULL REFERENCES design_variants(id), RESTRICT |
| `design_snapshot_json` | TEXT NULL; contrato inmutable de diseño utilizado |
| `design_snapshot_sha256` | TEXT NULL; hash canónico del snapshot |

Índice `issues(design_variant_id)`. Trigger comprueba que variante pertenece a `issues.version_id`, y que snapshot/hash aparecen juntos; si hay variante exige snapshot. Tras insertar no se actualizan identidad, vínculo, snapshot/hash. No bloqueo indiscriminado de columnas históricas de estado del PDF. El servicio nuevo exige snapshot incluso sin variante para toda emisión nueva. Migración deja las TRES columnas NULL en TODAS las emisiones anteriores; no asigna variantes ni infiere diseño desde revisiones actuales.

Snapshot contrato 1: identidad etiqueta/revisión/variante opcional; design hash; layout completo y nominal; rutas/hashes fuentes; aprobación documental registrada y hash evidencia si hay variante; perfil efectivo (incluye ajustes/escala); selección y geometría del maestro de estado con archivos/hashes/aprobación; build del software/contrato del motor. Variables, recipientes y numeración permanecen en columnas existentes, sin duplicarlas innecesariamente. El PDF final mantiene su propio hash existente.

El snapshot es inmutable por aplicación/trigger y verificable por hash; depende de archivos conservados, no incrusta el PDF. Abrir el PDF histórico sigue verificando su hash. Reproducirlo exige archivos correspondientes; no emplear la variante actual como reemplazo. Retirada posterior bloquea NUEVA emisión/reimpresión desde diseño retirado; el PDF histórico íntegro sigue consultable. No reconstruir un histórico sin snapshot como si lo tuviera: conservar comportamiento heredado con advertencia y aprobación de revisión actual, sin promocionarlo a evidencia exacta.

## 4. Estados y aprobación externa

| De → A | Acción y condiciones |
|---|---|
| creación → DRAFT | Revisión explícita, UID/código/nombre/motivo; snapshot completo del diseño de revisión u origen de la misma revisión. Verificar fuentes; sin aprobación heredada. |
| DRAFT → DRAFT | Guardar diseño validado, expected_generation, huella base y fuentes verificadas; audit antes/después. |
| DRAFT → PENDING | Solicitar revisión: congelar geometría y denominación; validación del contrato/layout/fuentes y motivo. Puede basarse en revisión pendiente, pero no podrá aprobarse todavía. |
| PENDING → DRAFT | Devolver a edición con motivo; audit y generation+1; no borrar historia. |
| PENDING → APPROVED | Revisión APPROVED y elegible, base sin cambios, geometría válida, prueba sintética/render revisable, evidencia íntegra y responsable/referencia/fecha externa obligatorios. Registro explícito; no firma electrónica. |
| APPROVED → RETIRED | Responsable, instante y motivo; conserva aprobación/diseño/evidencia. No retira variantes hermanas. |
| DRAFT/PENDING → RETIRED | Cancelación explícita con responsable y motivo; aprobación NULL. |
| APPROVED/RETIRED → nueva DRAFT | Derivar con nuevo UID/código/motivo y vínculo al origen; copiar diseño, nunca aprobación. |

No APPROVED→DRAFT, RETIRED→APPROVED ni aprobación automática. `approve_variant` no llama a `Store.approve`, ni altera revisiones ni otras variantes. Actualizaciones y entrada `audit` se confirman en la MISMA transacción `BEGIN IMMEDIATE`; si falla audit, tampoco cambia estado. Auditoría con eventos CREATE_VARIANT, SAVE_VARIANT, SUBMIT_VARIANT, RETURN_VARIANT, APPROVE_VARIANT, RETIRE_VARIANT; subject `variant:<uid>` y detail JSON con operador, motivo, identidad, generación, antes/después y hashes (layout anterior/nuevo al guardar para reconstrucción). No tabla adicional de eventos.

La revisión retirada bloquea emisión de todas sus variantes aunque su estado siga APPROVED; se muestra “aprobada, revisión base retirada”, sin reescribirlas. La revisión pendiente bloquea aprobación de variante. Elegibilidad efectiva requiere revisión APPROVED, variante APPROVED si elegida, fuentes/evidencia/base/hash intactos y maestro de estado autorizado cuando se usa. Conservar `verify_renderable` y bloqueo del PDF de desbordamiento conocido, incluso si se renombra o selecciona variante. 00-R1 sigue PENDING, y nunca se usa como atajo para aprobar variante.

Solo DRAFT editable. Prueba en DRAFT/PENDING con marca de prueba y SIN `add_issue`. RETIRED solo consulta, incluso con test_mode; nunca emisión definitiva. Cancelar un diálogo o prueba no aprueba nada. Revalidar en servicio al abrir, guardar, aprobar, renderizar y registrar emisión, no solo habilitar/deshabilitar botones.

## 5. Instalación sobre data 0.3.1/R3B1 y bloqueo del antiguo

La versión del programa 0.3.1 y SQLite `user_version=3` son conceptos distintos. Antes de cualquier escritura, el nuevo Store inspeccionará formato/ruta/esquema en modo lectura; rechaza versiones futuras, esquemas parciales o manifiestos incoherentes. No ejecuta `_schema` ni semillas al iniciar migración. Una base legacy con versión 0 requiere normalización previa reconocida en staging y su propia prueba; no se acepta por tener columnas parecidas. R3B2 se valida primero para v3 exacto, y variantes vacías en instalación nueva.

### Barrera propuesta, parte de la aprobación del esquema

Los ejecutables antiguos ignoran settings y `user_version`, y SQLite no ofrece un trigger que impida su PRAGMA ni toda lectura/escritura. No basta elevar a 4, un lock cooperativo ni “no usar el EXE viejo”. Se propone **cambiar solo la ruta de la base activa** a `data/storage_v4/labels.sqlite` y convertir la ruta legacy `data/labels.sqlite` en un **directorio barrera**, con README indicando incompatibilidad. El SQLite antiguo falla al conectar a un directorio, antes de `_schema`, seeds o emisiones. Archivos fuente, PDF, emisiones y referencias relativas conservan sus rutas; los IDs/UID no cambian.

El nuevo portable/Tk/Qt/backup resolverán la ruta activa desde contrato fijo de formato más `data/storage-format.json`; nunca desde un path externo arbitrario. El manifiesto registra `storage_format=4`, protocolo escritor 4 y migration_id. El Store nuevo comprueba directorio barrera y manifiesto antes de usar v4; si falta cualquiera, se niega a abrir para escritura y propone recuperación. Un ejecutable futuro también verifica máximo/mínimo antes de WAL/DDL. No hay fallback silencioso a una base vacía legacy. Cambiar `COVEX_LABEL_DATA` a otra carpeta restaurada es otra instalación, no acceso a esta base.

La barrera protege ejecutables antiguos sin modificar que apunten al data habitual, no scripts/admin que eliminen la barrera o apunten manualmente al archivo interior. No se hace una promesa contra manipulación deliberada. Mantener el antiguo funcionando dentro del mismo data v4 no se admite; el Tkinter conservado es el empaquetado NUEVO, actualizado al mismo protocolo, no el EXE 0.3.1.

### Protocolo de migración futura (no ejecutado en esta entrega)

1. Cerrar Qt, Tk y cualquier instancia. Obtener exclusión de carpeta y, en Windows, handles del SQLite legacy/WAL/SHM que impidan nuevos lectores/escritores de esos archivos durante corte (share-delete solo si necesario para rename), verificando ausencia de sesiones; los binarios antiguos no respetan lockfiles. Si no se puede garantizar quiescencia, abortar. Un handle del archivo renombrado NO bloquea la creación de otro archivo en su nombre anterior. Esta limitación se trata en el paso 6; no atribuir esa garantía a un lockfile. Prueba Windows del protocolo obligatoria antes de entregar migrador.
2. Inventario en lectura: user_version, SQL de sqlite_master, columnas/índices/triggers conocidos, conteos, claves/UID, FK, estados, rutas y hashes. `PRAGMA integrity_check`='ok', `foreign_key_check` vacío. Inconsistencias no se reparan automáticamente. Hash de todas las filas antiguas en serialización por tabla/PK, incluyendo audit/settings.
3. Backup completo fuera del conjunto que se va a cambiar: SQLite backup API incorpora WAL; originales, PDFs, status_masters, emisiones y demás datos persistentes; cache excluible, backups anteriores no se anidan. Guardar manifiesto SHA-256 de cada archivo y DB snapshot, versión/build y resultado de integridad. No registrar BACKUP en la base legacy durante este procedimiento. Verificar extracción/lectura y espacio disponible para backup + staging + recuperación. Si fuente histórica falta o no coincide, bloquear migración y emitir informe; no actualizar hashes.
4. Crear `backups/<migration_id>/staging/storage_v4/labels.sqlite` desde snapshot. Aplicar v3→v4 en UNA transacción explícita (no `executescript` con commits implícitos): tablas, columnas, índices, checks/triggers, ledger/settings nuevas y `user_version=4` al final. Rollback completo si cualquier instrucción falla. No seeds ni ajustes ACETONA/00-R1. Migración idempotente por versión+checksum+esquema; no reaplicar un 4 ya válido.
5. Verificar staging: integridad/FK, contrato de esquema, filas antiguas idénticas en sus columnas originales, todas las columnas nuevas de issues NULL, cero variantes, archivos/hashes sin cambio, 00-R1 mismo ID/UID/PENDING. Cerrar DB/checkpoint v4; no publicar WAL vivo. Fsync donde corresponda.
6. Escribir journal externo durable con fases PREPARED, LEGACY_ISOLATED, BARRIER_INSTALLED, PUBLISHED, VERIFIED y rutas/hash de artefactos. Aislar la antigua labels.sqlite y sus sidecars en backup de migración cerrado; instalar directorio barrera manteniendo exclusión de OS hasta terminar. La operación entre varios archivos NO se declara atómica: cualquier fase incompleta se detecta y recupera. Crear la barrera exclusivamente con mkdir que falle si ya existe el nombre, sin borrar/reemplazar nada. Si un antiguo ejecutable gana la carrera y crea otro labels.sqlite entre rename y mkdir, abortar antes de publicar v4, conservar ese archivo y el backup y requerir cierre/recuperación; nunca descartarlo ni unirlo a staging. Así el antiguo no conoce ni escribe la base migrada y un corte competido no se presenta como éxito. Las pruebas Windows deben demostrar bloqueo antes del rename y aborto seguro de esta carrera. Una instalación que no pueda garantizar cierre y recuperación no migra.
7. Publicar v4 desde staging a storage_v4 y manifiesto por rename en mismo volumen, con barrera ya instalada. Abrir nueva DB, revalidar, registrar MIGRATE_V4 en audit sin modificar entradas previas y marcar VERIFIED. Solo entonces habilitar aplicación. Mantener backup anterior y journal; no eliminarlos al iniciar.

No almacenar nuevos archivos maestros ni convertir revisiones. `versions`, `issues` previas y las 87 capacidades deben verse al terminar. 00-R1 no recibe evento de aprobación. Bibliotecas sin variantes muestran “Diseño heredado de la revisión”. El backup normal nuevo debe incluir DB activa, manifiesto y barrera reconstruible, excluyendo WAL/SHM, staging y backups anteriores; no seguir el código actual que asume exclusivamente `labels.sqlite` en raíz y podría empaquetar dos bases.

## 6. Fallos y recuperación

| Fallo | Resultado exigido |
|---|---|
| Inventario, integridad, hash, espacio o backup | No tocar legacy ni habilitar v4; diagnóstico y cierre. |
| DDL/corte antes de publicar | Staging se revierte/descarta; legacy no se altera en contenido. Si ya se aisló, journal dirige recuperación. |
| Proceso muere entre aislamiento/barrera/publicación | Nuevo arranque entra solo en recuperación, no crea base vacía, no seeds y no abre escritura. Revalidar originales/backup; completar corte válido o restaurar instalación v3 cerrada. |
| Antigua instancia intentó abrir durante corte | Impedirla con exclusión de OS; si aparece archivo legacy inesperado, abortar/aislar y no descartar sus datos. No mezclar dos bases. |
| Base v4 falla comprobación tras publicación | Detener; conservar v4/journal para diagnóstico; restaurar copia íntegra verificada en otra carpeta y abrir con versión correspondiente. |
| Retorno a v3 tras uso real de v4 | No downgrade SQL. Restaurar backup completo PRE-v4 en carpeta distinta con EXE anterior; advertir que cambios posteriores NO están allí y conservar v4 para recuperarlos. |
| Backup corrupto o evidencia/documento ausente | No declarar recuperación correcta. No recalcular hash para ocultarlo. |

Una restauración completa compara inventario y contenido, no solo que SQLite abra. Añadir instrucciones de recuperación a docs de actualización en PR de implementación. Ensayos con cortes de proceso en CADA fase y disco lleno, backup imposible, locks activos y reinicio repetido. El migrador no borra backups automáticamente.

## 7. Adaptador y emisión, cambios mínimos del motor

Nuevo resolvedor de servicio `resolve_design(revision_id, variant_id=None, purpose)` retorna DTO nuevo, identidad y hash esperados. Carga revisión/variante desde DB, comprueba relación/estados/base/archivos, deep-copy y `version_with_layout` para sustituir únicamente layout/base dimensions EN MEMORIA. Conserva ID/UID revisión, rutas/hashes, datos documentales y state real: nunca fabricar APPROVED para pasar validación. El DTO lleva por separado variant UID/state/hash; el motor recibe su contrato anterior. Preview y geometría usan el mismo resolvedor, nominal y perfil efectivo.

`LocalServices.render` deja de descartar la variante al recargar; accepts selección explícita, no diccionarios de UI como autoridad. Con `variant_id=None` resuelve layout legado sin crear variante. Mantener `render_emission`, sus controles de archivo, marcas de prueba, bounds y estados. La elegibilidad de variante se añade en servicio/registro, no reescribiendo PDF. No modificar composiciones fijas ni cambiar fuente para crear una variante.

Al generar salida definitiva, token interno incluye revisión/variante/design hash/generation y snapshot completo del diseño realmente renderizado. Antes de publicar archivo/insertar issue, revalidar token en transacción y archivo PDF/hash; retiro o cambio concurrente bloquea registro y éxito. No regenerar snapshot desde el estado actualizado después del render. Staging PDF y publicación controlada; fallos de DB no dejan una emisión presentada como exitosa; archivo huérfano se informa y no registra como emitido. No introducir work_drafts ni automatización R3B3. `add_issue` directo sin contrato validado no debe permitir burlar la asociación; la ruta heredada nueva genera snapshot de revisión.

El puente nuevo transporta revision_id y variant UID opcional y usa mismo servicio. No cambiar silenciosamente selección a revisión al abrir Tk. Qt mantiene bloqueo mientras acompaña Tk; variantes abiertas por Tk deben usar adaptador de editor y servicios comunes, no `replace_pending_fields` sobre revisión. Prohibir usar un acompañante antiguo/otro build; no copiar la variante al diseño de revisión para hacerlo compatible. Identidad de selección/layout de cada vista debe incluir `(revision_uid,variant_uid|null)`, no solo current_editor_id, evitando cachés cruzadas. Conservar flujo heredado sin variante.

## 8. Biblioteca y Editor PySide6

Biblioteca mantiene filas por revisión y sus filtros/favoritos/recentes; no multiplicar filas ni contadores de revisiones por cada variante. En detalle: selector “Diseño heredado” + variantes de revisión con código, nombre, dimensiones y estado; retiradas consultables mediante filtro. Acciones Crear variante, Derivar, Enviar a revisión, Registrar aprobación externa, Retirar, Consultar evidencia. La selección nunca elige automáticamente la última aprobada: puede haber varias; recordar selección solo en memoria en R3B2. Al cambiar revisión se limpia variante incompatible.

Editor mantiene lienzo central, paneles y todas las herramientas R3B1: recorte/anclas/relocalización, geometría mm, bloqueos, alineación/distribución, zona de estado, undo/redo. Cabecera muestra etiqueta → revisión → variante y ambos estados. “Guardar variante” solo DRAFT; “Crear variante derivada” para aprobada. Diseño heredado pendiente conserva edición de revisión explícita con mensaje del objeto que se guarda. Cambiar objeto exige guardar/descartar/cancelar cambios en memoria; separar histories por identidad. No habilitar autoguardado.

Comparación documental en panel/diálogo de dos columnas revisión/variante: UID/códigos, origen/fuente/rutas/hashes, base fingerprint, layout y dimensiones, responsable/referencia/fecha de aprobación, evidencia y retirada. Mostrar qué se hereda y qué cambió, sin sustituir aprobación de revisión por aprobación de variante. Comparación visual existente se conserva; superposición/diferencias gráficas generales no se desarrolla aquí.

Ajustes exclusivos de impresión (papel A4/orientación, márgenes/gap, offset/calibración, slot inicial, marcas, impresora, copias/recipientes) permanecen en perfil/emisión, no cambian hash de variante ni exigen una nueva variante. Escala proporcional puntual se registra en perfil/snapshot; adaptación nominal reutilizable es una decisión explícita de diseño. Cambiar recorte/posición/tamaño de campos/área, fuente, anclajes o composición sí cambia diseño; no se guarda bajo un perfil para eludir aprobación. Zoom es vista, nunca geometría ni variante.

## 9. Ejemplos sintéticos antes/después

IDs ilustrativos, hashes expresados como símbolos, no maestros ni datos de COVEX. Ejemplos de contrato, no base ejecutada.

| Entidad antes (v3) | Inmediatamente después (v4) |
|---|---|
| labels id=10 uid=L10, SYNTHETIC-A | Misma fila, columnas y UID |
| versions id=100 uid=R100, revisión 00 APPROVED, fuentes S100/P100, layout H100 | Exactamente igual; ninguna variante creada |
| versions id=101 uid=R101, revisión 00-R1 PENDING | Exactamente igual, continúa revisión; cero variantes automáticas |
| issues id=500 uid=I500 version_id=100, PDF/hash Q500 y perfil propio | Mismos campos previos; variant/snapshot/hash=NULL |
| audit id=700 con evento histórico | Mismo contenido; MIGRATE_V4 se añade después |
| data/labels.sqlite v3 y archivos en rutas originales | Activa en storage_v4/labels.sqlite v4, legacy labels.sqlite directorio barrera; rutas de documentos/emisiones iguales |

Ejemplo POSTERIOR a aprobación y desarrollo: usuario crea id=200 uid=V200 code=BOTE-80X50 desde R100, motivo “Formato de envase sintético”, estado DRAFT y layout propio. Si la proporción heredada no permite 80×50 sin deformación, validar/corregir geometría autorizada o rechazar; no forzar el fondo PDF. PENDING y aprobación registrada con fecha/responsable/ref/evidencia producen APPROVED, hash DV200. Otra variante V201 puede aprobarse sin retirar V200. Derivar V202 desde V200 crea DRAFT sin aprobación. Cambiar V200 directamente se rechaza. Retirar V200 registra motivo y deja V201 igual.

Nueva issue I501 referencia R100/V201 y snapshot SH501; posterior retiro/cambio de otra variante no altera I501 ni Q501. Fuentes/H100 tampoco cambian. Issue I500 sigue sin snapshot: consultar PDF Q500 íntegro, no inferir que usó V201. Una variante creada desde R101 puede permanecer DRAFT/PENDING, pero su aprobación/emisión definitiva se rechaza mientras R101 siga PENDING. Ningún ejemplo implica aprobar 00-R1.

## 10. Criterios de aceptación y pruebas de implementación

Esta entrega NO declara superadas pruebas funcionales ni Windows nuevas. La PR de implementación debe aportar resultados sobre commit final, capturas de aplicación REAL con documentos sintéticos y matriz preservando las 87 IDs (no sustituirlas por una lista nueva). Windows CI no equivale a prueba de Windows 10/11, Word real, impresora/equipo COVEX o validación GMP.

| ID | Prueba / aceptación verificable |
|---|---|
| M01 | v3 sintética con revisiones/00-R1, UID/hash/rutas, metadata/preferencias, perfiles, materiales, estados, emisiones/reimpresiones y audit: igualdad exacta de columnas previas antes/después; 0 variantes y nuevos campos issues NULL. |
| M02 | Migración vacía y v3 válida, repetición idempotente, desconocida/futura/parcial/checksum distinto: solo rutas autorizadas; ni downgrade ni seeds ni reparación silenciosa. |
| M03 | DDL y cada fase de corte con excepción/muerte/disco lleno: rollback o recuperación por journal sin duplicación ni pérdida; integridad/FK y manifiesto verificado tras restaurar. |
| M04 | Backup con WAL activo y archivos completos: extraer en carpeta aislada, comparar todas las filas/hashes y abrir v3; no depender del archivo DB principal copiado en vivo. |
| M05 | EXE/fuentes 0.3.1/R3B1 y Qt/Tk antiguos contra data v4 en Windows: falla antes de escribir; hash DB activa, audit, fuentes y emisiones igual antes/después. Durante corte: abrir archivo legacy bloqueado por OS; carrera de creación tras rename fuerza aborto antes de publicar y preserva archivo inesperado; ningún proceso antiguo puede escribir v4. |
| V01 | Unique code/UID, FK y origen misma revisión, self/ciclos, nombre/motivo vacíos, inválidos JSON/numéricos: rechazo en servicio y restricciones SQL pertinentes. |
| V02 | Tabla completa de transiciones: aprobadas congeladas, retiradas inmutables, PENDING devuelve a DRAFT con motivo, coexistencia aprobadas y derivación sin copiar aprobación. Fallo audit revierte mutación. |
| V03 | Falta responsable/ref/fecha/evidencia, archivo/hash alterado, revisión PENDING/RETIRED, base cambiada, hash incorrecto o generación obsoleta: no aprobar ni emitir. La integridad de revisión y variante se comprueba por separado. |
| G01 | Fixture baseline/textbox/continuation/paragraph, erase, second_x/next_w, locked/anclas, recorte y área: no pérdida de claves ni diferencias entre adaptación de revisión/variante al render. |
| G02 | Posiciones/dimensiones calculadas y PDF a tamaños nominales/proporcionales: tolerancia propuesta ≤0.1 mm, conversión numérica ≤1e-6 mm; no deformación. Seguridad/glifos actuales conservados. Prueba del desbordamiento conocido mantiene bloqueo. |
| G03 | Recorte, anclas, relocalización (alcance existente), selección múltiple, alineación/distribución y undo/redo siguen funcionando; zoom/perfil no mutan revisión/variante; cambios estructurales sí requieren DRAFT. |
| H01 | Emisión NUEVA con/sin variante lleva snapshot real/hash; fuente/variante de otra revisión rechazada; render pendiente solo prueba con marca y sin issue; retirada no emite. |
| H02 | Cambio/retirada entre render y registro se detecta; fallo PDF/DB no declara éxito. Reimpresión nueva usa snapshot, enlaza source_issue_id y motivo; no resuelve otra variante ni permite diseño retirado. |
| H03 | Históricos conservan PDF/hash/UID/ref/variables/perfiles, snapshot NULL y consulta íntegra; no backfill ficticio. No prometer reproducción exacta de registros sin snapshot. |
| UI01 | Capturas reales sintéticas: Biblioteca selector y comparación, Editor DRAFT editable, PENDING congelada, APPROVED solo lectura, dos aprobadas coexistentes, retirada/base retirada y diálogo de evidencia. Diseño responsive/ventana mínima actual sin solapamientos. |
| UI02 | Cambiar revisión/variante sin cruzar buffers/histories; guardado explícito; mismas herramientas R3B1. Qt→Tk→Qt con variante seleccionada, revisión intacta, bloqueo durante acompañante y build correcto. |
| R01 | Regresión suite existente, controles Qt y portable Windows/compilación/núcleo/puente. Matriz de las 87 capacidades con evidencia de cada ID afectada, y ningún ID eliminado. |

Puerta de aceptación: usuario aprueba esquema, ruta/barrera, estados y criterios antes de programar; después una PR de R3B2 con verificaciones sobre último commit y revisión visual. Si implementación necesita otra tabla, cambiar fuentes históricas o una estrategia distinta de corte, volver a presentar diff de esquema y razón antes de migrar datos. Main no se modifica en esta entrega; PR #5 sigue borrador sin integrar. R3B3/R3C/conectores no iniciados.
