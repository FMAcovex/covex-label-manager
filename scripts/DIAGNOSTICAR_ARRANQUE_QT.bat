@echo off
setlocal EnableExtensions DisableDelayedExpansion
title COVEX Label Manager - comprobacion del arranque
cd /d "%~dp0"
if errorlevel 1 (
  echo [ERROR] No se puede acceder a la carpeta del portable.
  goto :instructions
)
echo =============================================================
echo COVEX LABEL MANAGER - DIAGNOSTICO DE ARRANQUE (DEMO)
echo No cambia permisos, antivirus, registro ni datos GMP.
echo =============================================================
echo.
if not exist "%~dp0BUILD_MANIFEST.json" (
  echo [ERROR] Falta BUILD_MANIFEST.json. El paquete puede estar incompleto.
  goto :instructions
)
if not exist "%~dp0COVEXLabelManager_Qt.exe" (
  echo [BLOQUEADO] Falta COVEXLabelManager_Qt.exe.
  echo Compruebe la cuarentena del antivirus. NO restaure ni excluya
  echo archivos sin revision de Seguridad/IT.
  goto :instructions
)
if not exist "%~dp0legacy\COVEXLabelManager_Legacy.exe" (
  echo [BLOQUEADO] Falta el ejecutable auxiliar legacy.
  echo Compruebe la cuarentena del antivirus: el portable esta incompleto.
  goto :instructions
)
if not exist "%~dp0_internal" (
  echo [BLOQUEADO] Falta la carpeta _internal con dependencias.
  echo Compruebe que extrajo TODO el ZIP y la cuarentena del antivirus.
  goto :instructions
)
echo Se abrira la DEMO con documentos ficticios.
echo Esta ventana permanecera abierta para mostrar el codigo de salida.
echo.
start "" /wait "%~dp0COVEXLabelManager_Qt.exe" --demo
set "exit_code=%errorlevel%"
echo.
echo =============================================================
echo La aplicacion ha terminado. Codigo de salida: %exit_code%
if not exist "%~dp0COVEXLabelManager_Qt.exe" (
  echo [ALERTA] El ejecutable ya no esta en la carpeta tras arrancar.
  echo Revise la deteccion en el antivirus sin restaurar el archivo.
)
if not exist "%~dp0legacy\COVEXLabelManager_Legacy.exe" (
  echo [ALERTA] El ejecutable auxiliar ya no esta en su carpeta.
)
if "%exit_code%"=="0" (
  echo Salida 0: no demuestra que el cierre fuera solicitado por el usuario.
) else (
  echo Salida distinta de 0: revise el codigo y los registros de seguridad.
)
:instructions
echo.
echo Comparta con soporte: nombre de deteccion, archivo puesto en
echo cuarentena, hora aproximada y codigo de salida (si aparece).
echo No comparta etiquetas reales ni datos GMP.
echo No desactive antivirus, no restaure archivos ni ejecute como admin.
echo.
pause
endlocal
