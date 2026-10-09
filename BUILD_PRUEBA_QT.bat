@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv-qt\Scripts\python.exe" py -3.11 -m venv .venv-qt
if errorlevel 1 goto fail
".venv-qt\Scripts\python.exe" -m pip install --require-hashes --only-binary=:all: -r requirements-windows.lock -r prototypes\industrial_qt\requirements-windows.lock
if errorlevel 1 goto fail
".venv-qt\Scripts\python.exe" scripts\check_build_destination.py dist\COVEXLabelManager_Visual_Qt
if errorlevel 1 goto fail
".venv-qt\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onedir --windowed --name COVEXLabelManager_Visual_Qt --add-data "prototypes/industrial_qt/chevron.svg;prototypes/industrial_qt" --exclude-module tkinter --exclude-module PySide6.QtQml --exclude-module PySide6.QtQuick qt_visual_poc.py
if errorlevel 1 goto fail
echo Portable de prueba: dist\COVEXLabelManager_Visual_Qt. Copie la carpeta completa.
pause
exit /b 0
:fail
echo Compilacion no completada.
pause
exit /b 1
