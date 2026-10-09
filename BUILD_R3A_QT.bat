@echo off
setlocal
cd /d "%~dp0"
py -3.11 -m venv .venv-qt
if errorlevel 1 exit /b 1
.venv-qt\Scripts\python -m pip install --require-hashes --only-binary=:all: -r requirements-windows.lock -r requirements-qt-windows.lock
if errorlevel 1 exit /b 1
.venv-qt\Scripts\python scripts\check_build_destination.py dist\COVEXLabelManager_Qt
if errorlevel 1 exit /b 1
.venv-qt\Scripts\python -m PyInstaller --noconfirm --clean --onedir --windowed --name COVEXLabelManager_Qt --add-data "covex_label_manager/qt_ui/chevron.svg;covex_label_manager/qt_ui" --add-data "resources;resources" --exclude-module tkinter main_qt.py
if errorlevel 1 exit /b 1
.venv-qt\Scripts\python scripts\check_build_destination.py dist\COVEXLabelManager_Legacy
if errorlevel 1 exit /b 1
.venv-qt\Scripts\python -m PyInstaller --noconfirm --clean --onedir --windowed --name COVEXLabelManager_Legacy --add-data "resources;resources" --exclude-module PySide6 legacy_qt_bridge.py
if errorlevel 1 exit /b 1
xcopy /E /I /Y dist\COVEXLabelManager_Legacy dist\COVEXLabelManager_Qt\legacy
