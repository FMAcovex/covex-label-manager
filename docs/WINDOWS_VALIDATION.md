# Portable Windows: construcción y aceptación pendientes

## Preparado y comprobado en este entorno Linux

Python 3.11.9 x64, PyInstaller 6.16.0 y dependencias directas/transitivas fijadas en `requirements-windows.lock` con hashes de wheels Windows. Se han descargado y comprobado los 17 paquetes y sus hashes; resolución sin conflictos en el comprobador de paquetes para el destino. Esto no ejecuta código Windows.

Un único workflow `windows-portable.yml`, runner `windows-2022`, acciones fijadas por commit, permisos de lectura y sin secretos. Ejecuta control de contenido y pytest con fixtures sintéticos, compila onedir, lanza el EXE con `--self-check`, conserva resultados y ZIP completo durante 14 días. No crea releases ni despliega aplicaciones. `--self-check` usa datos temporales, comprueba recursos/SQLite/render PDF y elimina la instancia. No inicia la interfaz ni Word y no imprime.

`BUILD_WINDOWS.bat` utiliza el mismo lock, exige Python 3.11.9 y rechaza reconstruir un destino que tenga `data`. El manifest de construcción registra commit, entorno, paquetes y hashes de archivos. Es un procedimiento repetible con entradas controladas; no se ha demostrado que dos ZIP sean idénticos byte a byte. El runner hospedado puede cambiar; archivar manifest y artefacto de la versión aceptada.

## Falta exactamente

1. Crear/reutilizar el repositorio privado autorizado; subir la rama y tags autorizados. Habilitar Actions y ejecutar el workflow. Resolver cualquier fallo real de Windows antes de distribuir el ZIP. No hay EXE compilado en esta entrega.
2. Extraer el ZIP completo en un Windows x64 compatible, en ruta escribible (por ejemplo carpeta de usuario), sin Python instalado. Comprobar apertura/cierre, búsqueda, filtros, favoritos, doble clic, Ctrl+K, edición de borradores y visor PDF. Probar rutas con espacios y caracteres españoles. El EXE y `_internal` se distribuyen juntos.
3. Actualizar una COPIA de los datos existentes: cierre, copia íntegra de `data`, nuevo programa en otra carpeta y traslado de `data` o misma ruta `COVEX_LABEL_DATA`. Comparar maestros, perfiles, variantes, UID, preferencias e historial. Cerrar/reabrir y restaurar una copia de seguridad. Conservar respaldo anterior. No probar primero sobre el único dato de producción.
4. Revisar documentalmente 00-R1 y sus PDFs antes de activarla: responsable y referencia real. El estado recibido es PENDING; las aprobaciones automatizadas usan instancias desechables, no los datos de COVEX. Verificar bloqueo de 00 defectuosa, de versiones retiradas y de documentos alterados.
5. Importar DOC/DOCX reales con Microsoft Word de escritorio instalado: el adaptador actual usa Word COM por PowerShell. Si no hay Word, el fallback exige LibreOffice localizable en PATH. Ninguno se incluye en el portable. Comparar recorte, tablas, páginas y tipografías contra el original; registrar versión del conversor. Actions no acredita esta conversión. Sin conversor, importar PDF.
6. Imprimir PDFs de prueba en la impresora/driver/papel habituales al 100%, sin ajustar a página. Medir ancho, alto, offsets y límites de la numeración; probar A4 completo, varias páginas, copias/envases, zona de seguridad y perfiles. Registrar evidencia y aceptar la calibración. La aplicación registra generación PDF, no confirma impresión física.
7. Comprobar permisos/antivirus/SmartScreen en el entorno real. No hay firma de código; decidir con IT si la distribución interna necesita firmarse. Una firma no sustituye la validación funcional.

## Criterio de aceptación

No marcar Windows, Word o impresión como verificados hasta adjuntar equipo/Windows, commit y hash del ZIP, resultados y evidencia real, responsable y fecha. Después aprobar distribución interna y validación de uso prevista según los procedimientos de COVEX. Mantener R3 sin implementar hasta aprobación visual.

Referencias técnicas: [PyInstaller](https://pyinstaller.org/en/stable/) requiere construir Windows en Windows; [seguridad de Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions) recomienda fijar acciones a commits completos. No se ha intentado compilación cruzada Linux → Windows.


## Descargar el primer portable cuando exista un build satisfactorio

1. Entrar con la cuenta autorizada al repositorio privado; pestaña Actions.
2. Abrir el workflow Windows tests and portable build y elegir la ejecución satisfactoria correspondiente al commit de la PR/versión aceptada. Si aún no se ha ejecutado, publicar la PR o usar Run workflow en una rama que contenga el workflow una vez que esté disponible en main.
3. En Artifacts descargar COVEXLabelManager-Windows-COMMIT. El ZIP exterior contiene COVEXLabelManager_Windows.zip y resultados de prueba; revisar pytest.xml, self-check.json y ZIP_SHA256.txt. Los artefactos caducan a los 14 días.
4. Extraer el ZIP interior completo en una carpeta NUEVA y escribible. Conservar EXE y _internal juntos. Biblioteca nueva vacía: no contiene documentación real. Para actualizar, trasladar una copia íntegra de data junto al EXE o mantener COVEX_LABEL_DATA.
5. Ejecutar COVEXLabelManager.exe y probar con datos ficticios; completar la lista de aceptación anterior. Un job verde comprueba build/pruebas/núcleo empaquetado, no Word, interfaz operativa ni impresión física.

No distribuir el ZIP fuera del entorno autorizado. No crear releases públicas. El portátil carece de actualizador automático; las próximas versiones se extraen aparte y conservan la carpeta local existente.
