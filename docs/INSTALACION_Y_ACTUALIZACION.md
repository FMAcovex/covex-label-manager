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
