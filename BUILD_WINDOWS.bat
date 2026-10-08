@echo off
setlocal
cd /d "%~dp0"
echo COVEX Label Manager v0.3.1 - Consolidacion R1-R2 - Crear Windows portable
where py >nul 2>nul
if errorlevel 1 goto :no_python
py -3.11 -c "import sys; assert sys.version_info[:3] == (3,11,9)" >nul 2>nul
if errorlevel 1 goto :no_python
if exist "dist\COVEXLabelManager\data" (
  echo Hay datos de usuario en dist\COVEXLabelManager\data.
  echo Para protegerlos, compile desde otra carpeta recien extraida del ZIP.
  echo Despues siga docs\INSTALACION_Y_ACTUALIZACION.md.
  if /I not "%~1"=="--ci" pause
  exit /b 1
)
py -3.11 scripts\check_build_destination.py dist\COVEXLabelManager
if errorlevel 1 goto :err
if not exist .venv\Scripts\python.exe py -3.11 -m venv .venv
if errorlevel 1 goto :err
.venv\Scripts\python.exe -c "import sys; assert sys.version_info[:3] == (3,11,9)"
if errorlevel 1 goto :no_python
.venv\Scripts\python.exe -m pip install pip==25.2
if errorlevel 1 goto :err
.venv\Scripts\python.exe -m pip install --require-hashes --only-binary=:all: -r requirements-windows.lock
if errorlevel 1 goto :err
.venv\Scripts\python.exe -m pip check
if errorlevel 1 goto :err
.venv\Scripts\python.exe -m pytest -q
if errorlevel 1 goto :err
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onedir --windowed --name COVEXLabelManager --add-data "resources;resources" main.py
if errorlevel 1 goto :err
.venv\Scripts\python.exe scripts\build_manifest.py dist\COVEXLabelManager
if errorlevel 1 goto :err
echo Portable creado en dist\COVEXLabelManager.
echo Copie la carpeta completa. Conserve data al actualizar.
if /I not "%~1"=="--ci" pause
exit /b 0
:no_python
echo Instale Python 3.11.9 x64 con el lanzador py. Use una .venv nueva de esa version.
:err
echo Error al compilar. Revise el mensaje anterior.
if /I not "%~1"=="--ci" pause
exit /b 1
