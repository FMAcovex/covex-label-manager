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


def test_status_entries_are_rows_in_shared_library_not_overlay_buttons(studio, tmp_path):
    window, session, app = studio
    assert not hasattr(window, "status_library_buttons")
    assert not hasattr(window, "status_library_group")
    source = synthetic_source(tmp_path)
    ids = add_three(session.services.status_catalog, source)
    window.refresh_status_manager()
    window.navigate("library")

    def markers():
        return [
            window.table.item(index, 0).data(__import__(
                "PySide6.QtCore", fromlist=["Qt"]).Qt.ItemDataRole.UserRole)
            for index in range(window.table.rowCount())
        ]

    assert all("status:" + uid in markers() for uid in ids)
    for uid in ids:
        row = markers().index("status:" + uid)
        assert window.table.item(row, 3).text() == "Etiqueta de estado"
        assert window.table.item(row, 4).text() == "00"
    assert window.select_version("status:" + ids[2])
    assert window.row is None  # no fabricated product identity
    assert "Rechazado" in window.doc_title.text()
    assert "Etiqueta de estado" in window.meta.text()

    window.search.setText("Sin analizar")
    app.processEvents()
    assert "status:" + ids[0] in markers()
    assert "status:" + ids[2] not in markers()
    window.search.clear()

    category = window.filters["category"]
    index = category.findData("Etiquetas de estado")
    assert index > 0
    category.setCurrentIndex(index)
    app.processEvents()
    assert set(markers()) == {"status:" + uid for uid in ids}
    window.reset_filters()
    window.open_library_status("rechazado")
    assert window.stack.currentWidget() is window.status_manager
    assert window.selected_status_uid() == ids[2]


def test_visual_field_editor_mouse_draw_move_resize_save_reopen(studio, tmp_path):
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtTest import QTest
    window, session, app = studio
    src = synthetic_source(tmp_path)
    uid = session.services.status_catalog.import_many(
        src, [{"kind": "aprobado", "revision": "00",
               "layout": make_layout(src, "aprobado", crop=[55, 280, 530, 465])}])[0]
    record = session.services.status_catalog.get(uid)
    editor = StatusFieldsDialog(session.services, record, window)
    editor.show()
    app.processEvents()

    # Critical UAT path: click the *real button* and draw on the actual canvas.
    QTest.mouseClick(editor.new_field_button, Qt.MouseButton.LeftButton)
    assert editor.view.drawing
    start = editor.view.mapFromScene(QPointF(90, 55))
    end = editor.view.mapFromScene(QPointF(220, 115))
    QTest.mousePress(editor.view.viewport(), Qt.MouseButton.LeftButton, pos=start)
    QTest.mouseMove(editor.view.viewport(), end)
    QTest.mouseRelease(editor.view.viewport(), Qt.MouseButton.LeftButton, pos=end)
    app.processEvents()
    assert not editor.view.drawing
    assert len(editor.layout["fields"]) == 1
    assert editor.items.currentRow() == 0

    editor.key.setText("lote")
    editor.name.setText("Lote de prueba")
    editor.required.setChecked(True)
    assert editor.apply_properties()
    original = editor.layout["fields"][0]["rect"][0]
    editor.shapes[0].moveBy(12, 0)
    editor.shapes[0].released()
    assert editor.layout["fields"][0]["rect"][0] > original

    width_before = (editor.layout["fields"][0]["rect"][2]
                    - editor.layout["fields"][0]["rect"][0])
    rectangle = editor.shapes[0].rect()
    rectangle.setRight(rectangle.right() + 15)
    editor.shapes[0].setRect(rectangle)
    editor.shapes[0].handles[-1].parentItem().released()
    width_after = (editor.layout["fields"][0]["rect"][2]
                   - editor.layout["fields"][0]["rect"][0])
    assert width_after > width_before
    editor.save()

    reloaded = session.services.status_catalog.get(uid)
    fields = json.loads(reloaded["layout_json"])["fields"]
    assert len(fields) == 1
    assert fields[0]["key"] == "lote"
    assert fields[0]["label"] == "Lote de prueba"
    assert fields[0]["required"] is True
    another = StatusFieldsDialog(session.services, reloaded, window)
    assert another.layout["fields"] == fields
    another.close()
    editor.close()


def test_library_double_click_routes_to_draft_status_editor(studio, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QDialog
    window, session, app = studio
    uid = add_three(session.services.status_catalog, synthetic_source(tmp_path))[0]
    window.refresh_status_manager()
    window.navigate("library")
    window.select_version("status:" + uid)
    opened = []
    def capture(dialog):
        opened.append(dialog.revision["uid"])
        return QDialog.DialogCode.Rejected
    monkeypatch.setattr(StatusFieldsDialog, "exec", capture)
    window.open_editor()
    assert opened == [uid]


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


def test_status_links_are_exposed_from_native_emission(studio):
    window, session, app = studio
    assert window.status_emission_button.text() == "Estados ▾"
    texts = [action.text() for action in window.status_emission_menu.actions()]
    assert texts == ["Sin analizar", "Aprobado", "Rechazado"]
    # A compact header shortcut must not add a vertical row to the emission
    # page: the shared PDF preview needs sufficient height at laptop DPI.
    assert window.emission_page.layout().itemAt(1).widget() is window.emission_document
