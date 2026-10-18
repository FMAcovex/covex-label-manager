"""R7A Qt smoke tests: all examples are synthetic, never real COVEX masters."""
import json
import zipfile

import fitz
import pytest

pytest.importorskip("PySide6")
from test_r3a_qt import studio
from covex_label_manager.status_design import make_layout
from covex_label_manager.qt_ui.status_fields_dialog import StatusFieldsDialog
from covex_label_manager.qt_ui.status_history_dialog import StatusHistoryDialog


def synthetic_source(tmp_path):
    path = tmp_path / "fictitious_status_source.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=595, height=842)
        for n, color in enumerate(((1, 1, 0), (.5, .8, .4), (1, .3, .3))):
            top = 45 + n * 235
            page.draw_rect(fitz.Rect(55, top, 530, top+185), fill=color)
            page.insert_text((70, top+35), "SYNTHETIC STATUS " + str(n), fontsize=16)
        doc.save(path)
    return path


def add_three(catalog, path):
    entries = []
    for i, kind in enumerate(("sin_analizar", "aprobado", "rechazado")):
        top = 45+i*235
        entries.append({"kind": kind, "revision": "00",
                        "layout": make_layout(path, kind, crop=[55, top, 530, top+185])})
    return catalog.import_many(path, entries)


def test_status_entries_are_visible_and_navigable_from_library(studio, tmp_path):
    window, session, app = studio
    assert set(window.status_library_buttons) == {
        "sin_analizar", "aprobado", "rechazado"}
    source = synthetic_source(tmp_path)
    ids = add_three(session.services.status_catalog, source)
    window.refresh_status_manager()
    assert "Rev. 00" in window.status_library_buttons["aprobado"].text()
    window.open_library_status("rechazado")
    assert window.stack.currentWidget() is window.status_manager
    assert window.selected_status_uid() == ids[2]
    window.navigate("library")
    window.search.setText("Sin analizar")
    app.processEvents()
    assert window.status_library_buttons["sin_analizar"].isVisible()
    assert not window.status_library_buttons["rechazado"].isVisible()
    window.search.clear()


def test_visual_field_editor_moves_and_saves_draft(studio, tmp_path):
    window, session, app = studio
    src = synthetic_source(tmp_path)
    uid = session.services.status_catalog.import_many(
        src, [{"kind": "aprobado", "revision": "00",
               "layout": make_layout(src, "aprobado", crop=[55, 280, 530, 465])}])[0]
    record = session.services.status_catalog.get(uid)
    editor = StatusFieldsDialog(session.services, record, window)
    editor.layout["fields"].append({
        "key": "lote", "label": "Lote", "rect": [120, 350, 300, 379],
        "font_size": 10.0, "bold": False, "required": True})
    editor.draw(0)
    app.processEvents()
    original = editor.layout["fields"][0]["rect"][0]
    editor.shapes[0].moveBy(12, 0)
    editor.moved(0)
    assert editor.layout["fields"][0]["rect"][0] > original
    editor.save()
    updated = session.services.status_catalog.get(uid)
    values = json.loads(updated["layout_json"])
    assert len(values["fields"]) == 1
    assert values["fields"][0]["key"] == "lote"
    editor.close()


def test_status_issue_history_is_accessible_from_native_history(studio, tmp_path):
    window, session, app = studio
    src = synthetic_source(tmp_path)
    uid = session.services.status_catalog.import_many(
        src, [{"kind": "rechazado", "revision": "00",
               "layout": make_layout(src, "rechazado", crop=[55, 515, 530, 700])}])[0]
    catalog = session.services.status_catalog
    catalog.submit(uid)
    catalog.approve(uid, "Revisor ficticio", "EVIDENCIA-DEMO-001", confirmation=True)
    issue_uid, pdf = catalog.emit(uid, {}, "Operador ficticio", width_mm=60)
    window.navigate("history")
    assert window.history_page.isVisible()
    dialog = StatusHistoryDialog(session.services, window)
    assert dialog.table.rowCount() == 1
    assert dialog.selected_uid() == issue_uid
    assert dialog.selected()
    assert dialog.pdf.path == pdf
    assert "Historial de estados" in [
        control.text() for control in window.history_page.findChildren(
            __import__("PySide6.QtWidgets", fromlist=["QPushButton"]).QPushButton)]
    dialog.close()


def test_status_catalogue_is_in_consistent_verified_backup(studio, tmp_path):
    window, session, app = studio
    path = synthetic_source(tmp_path)
    add_three(session.services.status_catalog, path)
    zipped = session.services.backup()
    with zipfile.ZipFile(zipped) as archive:
        entries = archive.namelist()
        assert "status_catalog.sqlite" in entries
        assert "status_catalog.sqlite-wal" not in entries
        assert "status_catalog.sqlite-shm" not in entries
        assert "backup-manifest.json" in entries
    from covex_label_manager.migration_v4 import verify_backup
    manifest = verify_backup(zipped)
    assert "status_catalog.sqlite" in manifest["files"]
