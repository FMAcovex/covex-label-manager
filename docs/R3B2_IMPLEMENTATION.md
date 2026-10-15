# R3B2 — variantes controladas y migración SQLite v4

Base: `e83953b023a6c40702a276745a1fcaeae278dbd1`. Esquema de PR #8 autorizado el 15/10/2026. Desarrollo en PR #9, sin integrar #5/#8, main intacta y sin merge autorizado. Exclusivamente documentos/datos sintéticos en pruebas y capturas.

## Puerta Windows superada antes del desarrollo funcional

La ejecución [38697576941, intento 2](https://github.com/FMAcovex/covex-label-manager/actions/runs/38697576941/attempts/2) terminó correctamente tras pasar el repositorio a público. Código de cabecera ensayado `139df90a…`, árbol de merge de prueba `66a3bfae…`. No se había cambiado código para desbloquear facturación. El workflow Windows preexistente también pasó.

Resultado extraído de logs de CI: [R3B2_MIGRATION_WINDOWS_RESULTS.json](R3B2_MIGRATION_WINDOWS_RESULTS.json). Windows Server 2022/Python 3.11.9, cinco terminaciones abruptas por `os._exit(73)` con restauración exacta. Ocho intentos de escritores antiguos rechazados: fuentes Tk/Qt y ambos EXE reconstruidos SIN CAMBIOS desde el commit base, tanto bajo exclusión OS como frente a directorio barrera. `windows_old_executables_proven=true`. Eso permitió comenzar variantes, PDF e interfaz. El recibo local anterior se conserva como evidencia histórica explícitamente Linux, no como prueba del código funcional posterior.

## Persistencia y compatibilidad

Dos tablas nuevas, `design_variants` y `schema_migrations`, tres columnas opcionales en `issues`. Auditoría existente reutilizada, sin tabla adicional de fuentes, trabajos, snapshots o adjuntos. Revisiones y diseños de variantes separados de forma persistente. No se cambian IDs/UID existentes, referencias, archivos ni registros previos. Históricos conservan las tres columnas NULL. Nueva instalación sin recursos privados tiene biblioteca vacía.

El Store nuevo reconoce v4 antes de DDL/WAL y valida contrato/esquema. Una carpeta v3 se copia con SQLite backup API y archivos íntegros; staging se verifica antes de mover la base activa a `storage_v4/labels.sqlite` y crear `labels.sqlite` como directorio barrera. La normalización aditiva de 0.1/0.2 se hace únicamente en staging, preservando el backup original. Corte recuperable por journal, sin afirmar atomicidad entre archivos. Esquemas futuros, incompletos desconocidos, corrupción, falta de espacio, lector antiguo Windows o carrera legacy impiden publicación. No semillas de maestros/00-R1 al migrar instalaciones existentes. Las pruebas históricas conservan su objetivo y se adaptan a las rutas/formato de backup nuevo.

Backup normal y restauración incluyen evidencias, barrera, manifiestos, fuentes, emisiones y snapshot consistente de DB/WAL. Recuperador offline disponible por los entrypoints Qt/Tk; restauración nunca sobrescribe otra instalación. La restauración gráfica asistida sigue fuera de alcance.

## Variantes y aprobación

Creación/derivación DRAFT con UID, código, nombre y motivo; origen restringido a misma revisión. DRAFT→PENDING congela edición; PENDING→DRAFT requiere motivo. PENDING→APPROVED requiere revisión vigente/elegible, diseño/base/fuentes íntegros y aprobación externa: responsable, referencia, fecha, operador del registro y copia verificada de evidencia. Aprobación nunca llama a `Store.approve` ni retira otras variantes. APPROVED/RETIRED no se editan; derivar nunca copia aprobación. Retirada/cancelación exige motivo y conserva historial/evidencia. Aprobación externa no equivale a firma electrónica.

Copia de evidencia a nombre exclusivo, fsync y doble comprobación SHA-256 antes de transacción. Estado+audit se confirman juntos. Si falla archivo/SQL/audit, no hay aprobación; el archivo ya copiado queda conservado y la excepción informa de su ruta como evidencia sin vincular. Tras interrupción antes del commit la situación es equivalente: archivo sin referencia, nunca aprobación automática. Backups conservan también esos archivos para diagnóstico. No se implementa un recolector automático que pueda borrar evidencia.

Serialización canónica v1: números decimales sin exponente ni -0, float mediante su representación decimal roundtrip, Unicode NFC en claves/valores, claves ordenadas y UTF-8, sin NaN/Infinity ni claves Unicode duplicadas. Vector independiente del entorno esperado `c59ed642cbc30ff3b0fbcea26eb3c0e32718a6ebfc1a4ce16959401d83ce33ad`. Comparación optimista por generación y revalidación dentro de transacciones IMMEDIATE.

## PDF, emisiones e historial

Adaptador crea un diccionario nuevo de revisión con layout de variante; fuentes y state documental permanecen reales. Motor PDF sin cambios. Cada PDF definitivo generado por servicio produce contrato en memoria con diseño, identidad/generación, aprobaciones, perfil efectivo, maestro de estado y hash del PDF. Registrar emisión revalida estados, fuentes/evidencia, datos de render y PDF; no admite un PDF arbitrario sin contrato. SQLite rechaza toda inserción nueva sin snapshot válido, también con variante NULL; snapshot y vínculo quedan congelados. El snapshot conserva el diseño realmente renderizado, no una consulta posterior que pudiera haber cambiado.

Reimpresión nueva usa snapshot y variante original, números originales, vínculo y motivo; retirada bloquea nuevas salidas. Histórico NULL mantiene la revisión documentada y advierte que no acredita reproducción exacta; nunca rellena retrospectivamente ese snapshot. Consultar PDF histórico íntegro sigue disponible. No se declara emisión física por generar PDF.

Geometría y perfiles separados: recorte/campos/área y formato nominal reutilizable son diseño; papel/márgenes/offset/copias/escala puntual de impresión son perfil. El nominal exige proporción compatible con fondo fijo. Cambiar recorte de borrador mantiene su escala nominal uniforme; no modifica la composición fija. Prueba geométrica compara desplazamiento calculado del campo con glifos PDF (tolerancia 0.1 mm).

## Biblioteca y Editor

Selector por revisión en Inspector y Editor, sin multiplicar filas/recuentos/favoritos de revisión. Menú Variantes: crear, derivar, tamaño nominal, enviar, devolver, registrar aprobación, retirar, comparación documental y evidencia. Editor usa las herramientas completas de R3B1 sobre DRAFT y guarda por generación. Historial de undo/redo y buffers se reinician al cambiar identidad. La aprobación muestra ambos estados por separado; perfiles no guardan cambios estructurales. Comparación documental legible con diferencias resaltadas.

Tkinter conservado, protocolo de escritor 4 en puente y selección explícita de variante. Editor Tk guarda la variante, nunca su revisión. Emisión Tk recibe el diseño resuelto; pruebas nuevas de puente verifican PDF marcado sin issue y emisión definitiva SINTÉTICA con snapshot de variante en fuentes y portable. No persistencia de trabajos ni sincronización de variables R3B3.

## Evidencias y límites

Pruebas locales funcionales en curso: regresión completa, migración, estados, generaciones obsoletas entre conexiones, fallo de audit con evidencia copiada, aprobación congelada/coexistencia/derivación, evidencia alterada, snapshots con/sin variante, SQL sin snapshot, retiro entre render/registro, geometría y reimpresión, backup/restauración de aprobación. Capturas son de widgets Qt reales con PDF sintético, nunca mockups ni maestros COVEX. La CI ejecuta esas mismas comprobaciones y genera capturas/fuente/portable a 100/125/150 %. Resultados finales se anotarán tras completar CI sobre último commit.

Conservadas las 87 IDs de la matriz y la cobertura heredada. 00-R1 sigue revisión heredada PENDING. Pendientes: Word real, impresión física al 100 %, Windows 10/11 y equipos COVEX, aceptación de uso previsto/validación GMP. Los resultados de Windows Server CI no sustituyen esas pruebas. Auditoría SQLite local no es inviolable; no hay firma electrónica, usuarios/servidor nuevos, R3B3, R3C ni conectores.

### Confirmación de actualización de instalaciones existentes

Qt y Tk solicitan autorización expresa antes de abrir SQLite antiguo, crear carpetas,
backups o locks. Cancelar es la opción predeterminada y deja idéntico el inventario
de archivos. El acceso sin interfaz falla cerrado (`MigrationConsentRequired`); no
existe un interruptor de entorno que autorice silenciosamente. El migrador offline
exige `confirmed=True`; las pruebas sintéticas lo declaran explícitamente. Instalación
nueva y v4 ya verificada no solicitan consentimiento. Después de recuperar a v3 se
requiere una nueva decisión; recuperar una publicación v4 completa no repite el cambio.
La aceptación de esta actualización no aprueba revisiones ni variantes.
