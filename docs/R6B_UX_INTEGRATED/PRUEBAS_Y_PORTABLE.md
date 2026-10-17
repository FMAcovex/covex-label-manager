# Regresión, CI y portable

La entrega `46d3eab` fue **NO CONFORME** en Windows pese a sus CI verdes. Los resultados de la tabla siguiente son el hito histórico previo; no constituyen aceptación de la nueva entrega. Ver [correcciones, nuevas pruebas y comparativa](CORRECCIONES_ACEPTACION.md). El nuevo portable debe proceder del commit posterior que cierre esas incidencias, no del artefacto anterior.

## Evidencia local

Entorno sintético aislado: Linux, Python 3.12.14, Qt 6.8.3, Fusion; Xorg dummy para capturas y offscreen para suites. No se abre una instalación productiva, no se usan documentos reales, no se despacha a impresora.

| Comprobación | Resultado |
|---|---|
| `python -m pytest -q` | 412 aprobadas, 2 omitidas; suite completa existente, 33 casos UX parametrizados y 6 de integridad del ZIP. |
| Self-check de widgets Qt a factores 1 / 1.25 / 1.5 | 86 comprobaciones por factor, `ok=true`, puente Qt/Tk verificado. |
| Variant, work, emission y R3E checks | `ok=true`; puente Qt/Tk en variantes/trabajo; recuperación, emisión e historial sintéticos. |
| Gate visual | 53 estados × 6 = 318 PNG, sin errores de límites/pies; 129 SVG seleccionados versionados. |
| Precisión | Valores físicos no editados conservan representación original, perfil y firma; test de round-trip calibrado. |
| Vida útil de pantallas | Self-check de 86 controles en subproceso con GC forzado entre diálogos; sin caída nativa. Ver [diagnóstico](CI_QT_FIX.md). |
| Integridad portable | CRC, inventario y SHA256 de cada archivo del ZIP; ejecutables Qt/Legacy y recurso visual obligatorios. |

Los PNG y manifiestos locales están en `test-results/ux-integrated/`; los SVG y el resumen de hashes están en esta carpeta. Los artefactos de CI conservan PNG y JSON sin introducir binarios en Git. La matriz documenta cobertura por familias, no 87 aceptaciones manuales independientes. Los 2 skips locales corresponden a Word real y semántica de compartición de archivos Windows; no se cuentan como aprobados.

Reproducción con dependencias del repositorio instaladas:

```bash
python -m pytest -q
python -m pytest -q tests/test_r6b_ux_qt.py
python -m pytest -q tests/test_r6b_acceptance_fixes_qt.py tests/test_mass_units.py
python main_qt.py --import-check test-results/import-process.json
python scripts/ux_acceptance_visual.py --width 1366 --height 768
QT_SCALE_FACTOR=1.5 python scripts/ux_visual_gate.py --width 1366 --height 768
python main_qt.py --self-check test-results/ux-self.json --verify-bridge
python main_qt.py --variant-check test-results/ux-variants.json --verify-bridge
python main_qt.py --work-check test-results/ux-work.json --verify-bridge
python main_qt.py --emission-check test-results/ux-emission.json
python main_qt.py --r3e-check test-results/ux-layout.json
python scripts/check_repository_content.py
python scripts/verify_portable_archive.py COVEXLabelManager_Qt.zip --report test-results/qt-archive-integrity.json
```

Repetir gate con factores `1`, `1.25`, `1.5` y ambas resoluciones. No confundir `QT_SCALE_FACTOR` con cambiar físicamente la resolución/DPI del monitor. El runner visual cancela los diálogos capturados y no acepta aprobaciones: prepara exclusivamente fixtures sintéticos mediante los servicios existentes en una base temporal.

## Tres CI de GitHub

Estado y enlaces de la ejecución de esta rama se registran al completar las ejecuciones. Deben aprobar:

1. **Qt editor and functional transition**: regresión Qt, widgets reales a tres escalas, seis gates visuales nuevos, puente Tk y portable Qt congelado con checks existentes.
2. **R3B2 migration safety gate**: consentimiento, migración y compatibilidad SQLite v4; sin cambios al esquema en esta PR.
3. **Windows tests and portable build**: suite core/Tk y portable heredado.

No se modifica el guard de contenido, locks ni versiones de acciones para lograr resultados. Las seis capturas Windows complementan, no sustituyen, las pruebas presenciales.

## Probar el portable actualizado en Windows

1. Abrir la ejecución **Qt editor and functional transition** de esta PR/rama y comprobar SHA y estado satisfactorio. Descargar el artefacto `R3E-Qt-Visual-Design-<SHA>` (no el portable Tk de la otra CI). Dentro contiene `COVEXLabelManager_Qt.zip`, informes y capturas. Comparar `Get-FileHash .\COVEXLabelManager_Qt.zip -Algorithm SHA256` con `qt-ZIP_SHA256.txt` y `qt-archive-integrity.json`. El manifest interno registra el commit del checkout de CI (puede ser el merge de prueba de GitHub) y los hashes de todos los archivos.
2. Extraer **toda** la carpeta a un directorio de prueba nuevo y con permisos de escritura. Conservar `_internal`, recursos y `legacy`; no copiar solamente el EXE ni sobrescribir una instalación productiva. El acompañante Legacy es necesario para compatibilidad residual.
3. Ejecutar desde PowerShell un check sintético, antes de abrir datos propios:

```powershell
$result = Join-Path $env:TEMP 'covex-ux-check.json'
$p = Start-Process '.\COVEXLabelManager_Qt.exe' -ArgumentList @('--self-check', $result, '--verify-bridge') -Wait -PassThru
Get-Content $result
$p.ExitCode
```

El resultado debe tener `ok=true`, `count=86` y puente correcto. Esta modalidad usa fixtures temporales. Para ensayo interactivo, usar exclusivamente una copia/instalación sintética separada conforme al procedimiento de datos de prueba existente; cancelar cualquier migración de una base no destinada al ensayo. No ensayar sobre datos reales ni aceptar aprobaciones ficticias en un catálogo real.

4. En Windows, probar cada resolución 1366×768 y 1920×1080 a 100 %, 125 % y 150 % desde Configuración de pantalla; reiniciar la aplicación tras cambiar escala. No combinar esa prueba física con `QT_SCALE_FACTOR` adicional. Registrar tamaño de pantalla, escala, versión Windows, SHA, capturas y defectos.
5. Recorrer Biblioteca/Inspector/filtros, fuentes, selector de revisiones y variantes, Editor y recuperación de paneles; editar un lote sintético, navegar a Configuración y volver, comprobar datos y ausencia de dock residual. Cancelar importación, aprobación y reimpresión y comprobar ausencia de cambios. Verificar estados pendientes/aprobados/retirados y motivos de acciones deshabilitadas.
6. Abrir Emisión, comprobar distinción guardar diseño/trabajo, hoja patrón/medidas de impresora, precisión de medidas, PDF de prueba y visor compacto. Revisar Historial con snapshots sintéticos; cualquier emisión/reimpresión de ensayo se registra como tal en entorno sintético y no se despacha a una impresora productiva.
7. Abrir UAT, conciliación, preaceptación, configuración y diálogos; verificar scroll, botones al pie, teclado, foco, textos y traducción estándar. Probar Narrador/UIA/alto contraste y navegación solo teclado: su aceptación permanece pendiente aunque el gate geométrico sea verde.

La validación GMP, Word/Office real, calibración física, papel, driver, impresora y aprobación humana son actividades separadas. Documentar sus evidencias sin atribuirles éxito por una CI o un PDF.

Para esta entrega, añadir obligatoriamente los seis pasos de aceptación de [Correcciones de aceptación](CORRECCIONES_ACEPTACION.md). El EXE admite `--import-check <ruta.json>`: debe finalizar con código 0, `ok=true` y 18 escenarios. Es una ejecución sintética aislada y no sustituye probar el asistente manualmente. Las CI lo repiten desde fuente y EXE congelado a tres escalas, y capturan antes/después en Windows.
