@echo off
setlocal
cd /d "%~dp0"
py -3.11 -m venv .venv-qt
if errorlevel 1 exit /b 1
.venv-qt\Scripts\python -m pip install --require-hashes --only-binary=:all: -r requirements-windows.lock -r requirements-qt-windows.lock
if errorlevel 1 exit /b 1
.venv-qt\Scripts\python main_qt.py %*
