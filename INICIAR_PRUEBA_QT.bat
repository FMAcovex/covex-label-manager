@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv-qt\Scripts\python.exe" py -3.11 -m venv .venv-qt
if errorlevel 1 goto fail
".venv-qt\Scripts\python.exe" -m pip install --require-hashes --only-binary=:all: -r requirements-windows.lock -r prototypes\industrial_qt\requirements-windows.lock
if errorlevel 1 goto fail
".venv-qt\Scripts\python.exe" qt_visual_poc.py
if errorlevel 1 goto fail
exit /b 0
:fail
echo No se ha podido iniciar la prueba. Requiere Python 3.11 x64 y acceso a dependencias.
pause
exit /b 1
