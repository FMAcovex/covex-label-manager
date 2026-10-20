"""R8-RC3: status inspector buttons execute relevant native actions.

Synthetic PDFs only. Regression also protects ordinary product navigation.
"""
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QPushButton

from test_r3a_qt import studio
from test_r7a_status_qt import add_three, synthetic_source


def inspector_button(window, caption):
    return next(
        button for button in window.inspector.findChildren(QPushButton)
        if button.text() == caption
    )


def test_real_status_inspector_buttons_preserve_selected_revision(studio, tmp_path):
    window, session, app = studio
    ids = add_three(session.services.status_catalog, synthetic_source(tmp_path))
    window.refresh_status_manager()
    window.navigate("library")

    assert window.select_version("status:" + ids[1])
    window.inspector_tabs.setCurrentIndex(1)
    app.processEvents()
    QTest.mouseClick(inspector_button(window, "Revisiones y variantes"),
                     Qt.MouseButton.LeftButton)
    assert window.stack.currentWidget() is window.status_manager
    assert window.selected_status_uid() == ids[1]

    window.navigate("library")
    assert window.select_version("status:" + ids[2])
    window.inspector_tabs.setCurrentIndex(2)
    app.processEvents()
    QTest.mouseClick(inspector_button(window, "Documentos y aprobación externa"),
                     Qt.MouseButton.LeftButton)
    assert window.stack.currentWidget() is window.status_manager
    assert window.selected_status_uid() == ids[2]

    window.navigate("library")
    assert window.select_version("status:" + ids[0])
    QTest.mouseClick(inspector_button(window, "Ver accesos de emisión"),
                     Qt.MouseButton.LeftButton)
    assert window.stack.currentWidget() is window.status_manager
    assert window.selected_status_uid() == ids[0]


def test_product_inspector_emission_route_remains_unchanged(studio):
    window, session, app = studio
    window.navigate("library")
    vid = window.rows[0]["version_id"]
    assert window.select_version(vid)
    QTest.mouseClick(inspector_button(window, "Ver accesos de emisión"),
                     Qt.MouseButton.LeftButton)
    assert window.stack.currentWidget() is window.emission_page
