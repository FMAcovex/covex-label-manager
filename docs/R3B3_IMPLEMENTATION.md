# R3B2+B3 · Entrega conjunta para aceptación

Dos controles independientes: PR #9 (R3B2, consentimiento v3→v4 y variantes) y PR #10
(R3B3, dependiente de #9). Main e83953b0… no integrada. Datos sólo sintéticos.
La decisión previa está en `R3B3_STORAGE_SPEC.md`, publicada antes de implementar.

## Persistencia y límites transaccionales

SQLite permanece exactamente en v4: no tablas/columnas/índices/triggers nuevos.
El esquema y su checksum se comprueban en regresión. Cada trabajo local independiente
fija ID+UID de revisión y variante, diseño/fuentes/estado/aprobación, valores comunes,
valores por recipiente, formato, selección, copias y etiqueta de estado.

Sobre JSON canónico con checksum y contrato 1. Se comparan huellas canónicas,
incluido Unicode compuesto/descompuesto; el adaptador empareja identificadores de
campos en memoria sin cambiar claves almacenadas ni textos fijos. Rechazo de formatos desconocidos,
rutas/locks enlazados y archivos corruptos. Guardado atómico, fsync, copia anterior,
lock OS no bloqueante por trabajo y CAS por generación. Un fallo conserva pantalla
y bloquea navegación/cierre. Recargar requiere descarte explícito si hay cambios.
La recuperación de una copia conserva el archivo corrupto y usa generación nueva
que no puede coincidir con una pantalla anterior. Los .tmp nunca se interpretan como
trabajos. Backup/restauración incluye trabajos, copias y evidencias; excluye locks.
No hay servidor, servicio residente, sincronización externa ni base paralela.

Guardar borrador admite datos incompletos y no crea PDF, issue ni aprobación.
Para emitir, se comprueban parámetros/documentación y se guarda EMITTING + operación
antes de renderizar. El servicio existente y SQLite vuelven a validar estado,
snapshot, evidencia y datos. El snapshot incluye UID/operación/generación/hash del
trabajo. Una transacción IMMEDIATE rechaza operaciones duplicadas. ISSUED no admite
edición: se copia a otro UID para preparar un nuevo lote.

Archivo y SQLite no comparten transacción. Tras un corte posterior al commit, se
reconcilia por operation_uid del snapshot y se muestra la emisión existente sin
repetirla. Antes del commit se muestra intento interrumpido y se exige recuperar;
se conservan PDF huérfanos para diagnóstico y jamás se registran por su existencia.
Una copia anterior no puede restaurarse sobre un trabajo con issue ya registrado.
Una modificación documental conserva valores y bloquea emitir hasta actualización
explícita del vínculo, seguida de revisión por el usuario. No se cambia geometría
maestra al guardar un perfil ni textos fijos en ningún caso. Motor PDF intacto.

## Uso

En Biblioteca seleccione revisión/variante y prepare un trabajo. En Emisión puede
crear, abrir, copiar o recuperar trabajos. Los trabajos existentes aparecen al
reiniciar, sin selección ni emisión automática. Datos de lote, recipientes, formato
y estado se editan en pestañas. «Guardar borrador» y «Emitir…» son acciones distintas.

En Editor, «Datos del trabajo» abre el mismo panel y mantiene separada la edición
estructural, que requiere guardado explícito. La identidad de revisión/variante del
trabajo siempre se muestra. Al abrir Tk, Qt guarda primero y entrega UID+generación,
bloquea su edición y recarga al terminar. Tk permite editar/autoguardar los mismos
valores, configuración y recipientes; una generación obsoleta falla sin mezclar lotes.
También ofrece copiar, recuperar y actualizar explícitamente el vínculo documental.
La confirmación definitiva en Tk registra la emisión; generar PDF no acredita
impresión física. Las rutas heredadas y reimpresión mantienen el contrato SQLite v4.

## Pruebas y aceptación

- Migración R3B2: cancelación sin cambios en disco, autorización Qt/Tk, cinco cortes,
  backup/restauración exacta, lector/escritor antiguo bloqueados; CI #9 independiente.
- Trabajos: datos incompletos, reinicio, CAS entre instancias, lock entre procesos y
  liberación al morir, fallo de replace, checksum/copia anterior, backup/restauración.
- Emisión: muerte real de proceso en INTENT/RENDERED/COMMITTED, una única emisión,
  rechazo de documento/variante cambiados, pendiente/retirada, snapshot/historial.
- Interfaz real: Qt autoguarda, comparte panel Editor/Emisión, conserva pantalla en
  conflicto; Tk conserva cambios al navegar/reiniciar y no cierra tras fallo.
- Integración: fuente/portable Windows, Qt→Tk→Qt de lote, PN/PB/lote individual y
  offset; prueba marcada sin issue y definitiva sintética con variante/snapshot.
- Regresión: 87 IDs conservadas y 80 controles Qt de R3A/R3B1, geometría, aprobación,
  fuentes, historial y reimpresiones. Capturas reales sintéticas en artefactos CI.

Resultados locales y Windows exactos, hashes y enlaces de artefactos se consignan
junto al commit probado en las dos PR; no equivalen a aceptación del usuario.
Pendientes: Word real/Office, impresión física, Windows 10/11 y equipos COVEX,
validación GMP y aceptación del uso previsto. Auditoría local sin firma electrónica
ni garantía de inviolabilidad. No R3C, Business Central ni SharePoint.
