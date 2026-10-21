"""Fase C: safe diagnostic launcher is included without bypassing endpoint controls."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_diagnostic_launcher_reports_quarantine_without_bypassing_security():
    launcher = (ROOT / "scripts/DIAGNOSTICAR_ARRANQUE_QT.bat").read_text(encoding="utf-8")
    assert 'if not exist "%~dp0COVEXLabelManager_Qt.exe"' in launcher
    assert 'if not exist "%~dp0legacy\\COVEXLabelManager_Legacy.exe"' in launcher
    assert 'if not exist "%~dp0_internal"' in launcher
    assert 'start "" /wait "%~dp0COVEXLabelManager_Qt.exe" --demo' in launcher
    assert "set \"exit_code=%errorlevel%\"" in launcher
    assert "pause" in launcher
    forbidden = ("set-mppreference", "add-mppreference", "restore and add exception",
                 "bypass", "powershell -enc", "runas ", "reg add ")
    for token in forbidden:
        assert token not in launcher.lower()


def test_verified_qt_portable_contains_operator_diagnostic_launcher():
    workflow = (ROOT / ".github/workflows/r3a-qt.yml").read_text(encoding="utf-8")
    assert "Copy-Item scripts/DIAGNOSTICAR_ARRANQUE_QT.bat dist/COVEXLabelManager_Qt/" in workflow
    assert workflow.index("Copy-Item scripts/DIAGNOSTICAR_ARRANQUE_QT.bat") < workflow.index(
        "python scripts/build_manifest.py dist/COVEXLabelManager_Qt"
    )
    assert "scripts/verify_portable_archive.py COVEXLabelManager_Qt.zip" in workflow
