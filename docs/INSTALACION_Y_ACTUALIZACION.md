# Instalación y actualización — 0.3.1 consolidación R1/R2

## Primera instalación

Extraer el ZIP completo. Instalar Python 3.11+ con el lanzador `py` y ejecutar `INICIAR_WINDOWS.bat`. Necesita conexión la primera vez para instalar las dependencias fijadas. La aplicación y su base funcionan localmente, sin servidor.

No contiene EXE compilado. `BUILD_WINDOWS.bat` construye `dist/COVEXLabelManager/` en Windows. Esa carpeta completa es portable e incluye dependencias; el equipo de destino no necesita Python. El script rechaza un destino que ya tenga `data`. Compilar desde una carpeta limpia; `--ci` evita pausas para procesos automatizados.

## Actualizar desde 0.1/0.2/0.3.0

1. Cerrar todas las ventanas de la aplicación.
2. Copiar la carpeta completa `data` a un lugar protegido; contiene más que SQLite.
3. Extraer el programa nuevo en otra carpeta. Si se usará EXE, compilarlo antes de incorporar datos.
4. Copiar el `data` existente junto al nuevo `main.py` o al EXE, o mantener la misma ruta absoluta `COVEX_LABEL_DATA`.
5. Iniciar la nueva versión. Se crea un snapshot SQLite antes de la migración. Se añaden zona de seguridad, UID y preferencias/metadatos de Biblioteca. No se sustituyen registros existentes por una base nueva.
6. Confirmar maestros, campos personalizados, perfiles e historial. Edrofonio de referencia tendrá la variante pendiente 00-R1; revisar antes de activarla. La 00 original sigue disponible para consulta, bloqueada para emitir por su defecto conocido.
7. Verificar PDF y medidas en Windows e impresión al 100% en la impresora habitual.

No actualizar sobre una base activa ni sincronizar SQLite abierto con SharePoint/OneDrive. No compartirlo entre usuarios simultáneos.

## Copias y restauración manual

Administración → copia de seguridad genera un ZIP con snapshot consistente de SQLite, archivos y preferencias, sin cache ni backups anteriores. Para restaurar: cerrar aplicación, apartar el `data` actual, extraer la copia íntegra en `data` y abrir la misma versión o una superior que migre su esquema. Conservar el original hasta comprobar el resultado. No abrir una base ya migrada con una versión antigua: volver a la copia completa anterior para un retorno.

No existe todavía asistente de restauración ni firma electrónica. Son pendientes del ROADMAP.

Para construir de forma controlada: Windows x64, Python 3.11.9 x64 y `BUILD_WINDOWS.bat` desde carpeta limpia. La ejecución desde fuentes admite otras versiones 3.11+, pero no es el perfil fijado de compilación. La actualización 0.3.0 → 0.3.1 no modifica el esquema (continúa en 3); conserva datos y no necesita una nueva migración. Ver `WINDOWS_VALIDATION.md`.


## R3B2 — formato de almacenamiento 4

Versión de desarrollo pendiente de revisión/integración; no aplicar a datos reales durante estas pruebas. Al iniciar sobre una carpeta existente cerrada, la aplicación prepara backup completo verificado y staging antes de publicar `storage_v4/labels.sqlite`. `labels.sqlite` de raíz pasa a ser un directorio barrera para ejecutables antiguos. No eliminarlo. Originales, maestros PDF y emisiones conservan sus rutas y hashes. No abrir este data con un ejecutable anterior ni copiar solo la base.

La migración no crea variantes, no rellena snapshots históricos y no crea/aprueba 00-R1. Toda emisión nueva requiere snapshot de diseño y contrato de render; la edición/aprobación de variantes está separada de revisión y perfil. Los EXE Tk y Qt incluidos deben ser del mismo portable R3B2.

Si se interrumpe una migración, el inicio bloquea escritura. Con todas las ventanas cerradas, recuperación offline:

```text
COVEXLabelManager_Qt.exe --recover-data RUTA_DATA --recovery-report RUTA_INFORME.json
```

El mismo argumento funciona con el portable Tk o `python main.py`. El recibo indica formato restaurado v3 o v4. No se mezclan bases: si apareció un archivo legacy inesperado, conservarlo junto al backup y restaurar en carpeta distinta; el recuperador aborta antes de eliminar cualquier archivo ajeno. Las copias previas están en `backups/v4-<id>/pre-v4.zip`, con manifiesto SHA-256. Para volver al ejecutable anterior, restaurar íntegramente ese backup pre-v4 en otra carpeta; los cambios hechos después de migrar no están en esa copia.

Backup desde la aplicación incluye DB activa, manifiestos, barrera, maestros, emisiones y evidencia externa. Su restauración en una carpeta nueva puede verificarse con `restore_backup` del módulo de migración; el ZIP es legible con herramientas normales. No sobrescribir un data existente al restaurar. La UI de restauración asistida sigue pendiente, como antes. Si falla el registro de aprobación, el archivo de evidencia puede conservarse sin vincular en `approval_evidence/<UID>`: no se considera aprobación y se informa de su ruta. No eliminar evidencias vinculadas a aprobaciones, aunque la variante esté retirada.
