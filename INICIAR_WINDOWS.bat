@echo off
setlocal
cd /d "%~dp0"
if exist "dist\COVEXLabelManager\COVEXLabelManager.exe" (
    start "" "dist\COVEXLabelManager\COVEXLabelManager.exe"
    exit /b 0
)
where py >nul 2>nul
if %errorlevel% neq 0 goto :no_python
py -3 -c "import sys; assert sys.version_info >= (3,11)" >nul 2>nul
if %errorlevel% neq 0 goto :no_python
if not exist .venv\Scripts\python.exe (
    py -3 -m venv .venv
    if errorlevel 1 goto :err
)
.venv\Scripts\python.exe -c "from pathlib import Path; import sys; p=Path('.venv/requirements.installed');sys.exit(0 if p.exists() and p.read_bytes()==Path('requirements.txt').read_bytes() else 1)" >nul 2>nul
if errorlevel 1 (
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 goto :err
    copy /y requirements.txt .venv\requirements.installed >nul
)
.venv\Scripts\python.exe main.py
if errorlevel 1 goto :err
exit /b 0
:no_python
echo Instale Python 3.11 o posterior desde python.org con el lanzador py.
pause
exit /b 1
:err
echo No se pudo iniciar. Revise el mensaje anterior.
pause
exit /b 1
