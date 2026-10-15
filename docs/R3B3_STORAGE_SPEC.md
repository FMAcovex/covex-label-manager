# R3B3 · Trabajos de emisión locales (propuesta previa a implementación)

Base: R3B2, PR #9, SQLite v4. Exclusivamente datos sintéticos. No R3C.

## Decisión y compatibilidad

No se amplía SQLite: user_version=4, checksum, tablas, índices y triggers de R3B2
permanecen idénticos. Un trabajo es un borrador editable y recuperable, no un registro
de emisión ni una aprobación. Una tabla adicional no es necesaria en esta aplicación
portable de un usuario: no hay consultas relacionales de lotes ni servidores externos.
El historial definitivo y la auditoría continúan en SQLite.

`data/emission_work/<uid>.json` contiene un sobre `contract=1`, payload y SHA-256 de
la representación canónica de ese payload. Cada payload contiene UID, nombre,
generación, fechas, revisión/variante (ID y UID), huella documental, valores de lote,
valores por recipiente, perfil de formato/impresión, selección de recipientes,
repeticiones, estado de etiqueta y fase DRAFT/EMITTING/ISSUED. Se permiten borradores
incompletos; generar prueba o emitir aplica las validaciones del motor y del servicio.
La geometría y textos maestros nunca se guardan en los campos variables del trabajo.

Los escritores R3B1 siguen bloqueados por storage_v4. R3B2 puede abrir SQLite v4,
pero no conoce trabajos; no modifica sus archivos ni sus snapshots. Un formato de
trabajo desconocido se rechaza, nunca se reinterpreta ni se sobrescribe. El backup
completo incluye estos archivos y sus copias anteriores; restaurar conserva UID y
generaciones. No hay conversión de históricos ni creación automática de variantes.
00-R1 permanece revisión heredada pendiente.

## Durabilidad y concurrencia

Cada lectura/escritura y emisión de un trabajo adquiere un lock OS por trabajo
(msvcrt en Windows; flock en POSIX), no un simple timestamp. La muerte de un proceso
libera el lock. Escritura: validar sobre/versión/checksum, comparar generación
esperada, guardar copia anterior validada, escribir temporal único, flush/fsync,
replace y fsync del directorio donde procede. Un error nunca anuncia «guardado».
Conservar los bytes introducidos en pantalla y bloquear navegación/cierre ante
fallo; ofrecer reintento o carga explícita de la versión guardada. Nunca sobrescribir
silenciosamente una generación externa ni sustituir un archivo corrupto por uno vacío.
Una copia anterior se restaura sólo mediante acción explícita y conserva el archivo
corrupto para diagnóstico. Las temporales incompletas no se consideran trabajos.

Qt y Tk usan el mismo repositorio y contrato. Antes de abrir el puente Qt guarda y
entrega UID + generación, queda bloqueado hasta que termina el proceso y después
recarga el trabajo. Tk rechaza un handoff obsoleto. La edición independiente usa CAS
por generación: el segundo escritor debe recargar, sin mezclar datos de lotes.
Autoguardado con debounce y flush antes de cambiar trabajo, abrir puente o cerrar.
Los trabajos persistidos se muestran al reiniciar; no se elige ni emite uno en silencio.

## Documento y emisión

El trabajo fija revisión/variante y huella de diseño/fuentes/aprobación. Un cambio
externo bloquea emisión, conserva datos variables y requiere actualización explícita
del vínculo o un trabajo nuevo. Una variante no aprobada admite preparación/prueba,
nunca emisión definitiva. Guardar borrador no genera PDF, issue ni aprobación.

Emitir mantiene el lock del trabajo, guarda primero una intención EMITTING con
operation_uid y generación/datos exactos; revalida documentación, renderiza por el
adaptador existente y registra issue+audit en una transacción SQLite que revalida de
nuevo. El snapshot incorpora work UID/operation UID/generación y hash de datos. La
comparación documental excluye exclusivamente este metadato de trabajo. El contrato
SQLite de snapshot de R3B2 sigue aplicándose a todas las rutas heredadas y reimpresiones.

Si SQLite confirma y falla la actualización del JSON, al reiniciar se consulta el
operation_uid del snapshot y se marca ISSUED sin reemitir. Si no existe issue, queda
un intento interrumpido y se exige recuperación explícita; un PDF huérfano se conserva
para diagnóstico, nunca se registra por su mera existencia. No hay transacción
atómica distribuida entre archivo y SQLite: intención durable y reconciliación
idempotente cubren esa frontera. Un trabajo emitido queda congelado; nuevas emisiones
requieren copiar a un trabajo nuevo, sin reutilizar operation_uid.

## Interfaz y aceptación

Panel Qt compartido en Editor y Emisión: lista de trabajos, crear/copiar/recuperar,
valores de lote, tabla por recipiente y configuración de formato. Guardar borrador y
emitir definitivamente son acciones distintas. Emisión definitiva utiliza el puente
Tk durante la transición; Tk edita y autoguarda el mismo trabajo. El Editor estructural
R3B1 y la selección/aprobación de variantes R3B2 se mantienen separados.

Pruebas antes de aceptación: CAS entre procesos, cierre forzoso antes/después de
replace y de commit SQLite, checksum/copia anterior, disco/escritura fallidos,
reinicio, Qt→Tk→Qt con lote/recipientes/perfil, generación/documentación obsoletos,
variante pendiente/retirada, doble emisión, snapshot histórico NULL sin cambios,
backup/restauración completa, 87 capacidades, fuente/portable Windows y capturas
reales sintéticas. Word real, impresión física, equipos COVEX y GMP siguen pendientes.
