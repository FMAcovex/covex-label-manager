"""R8-RC2 regression tests: acceptance findings reproduced on synthetic Qt fixtures."""
import pytest
pytest.importorskip("PySide6")
from PySide6.QtWidgets import QDialog

from test_r3a_qt import studio
from covex_label_manager.qt_ui.sheet_designer import SheetDesigner
from covex_label_manager.qt_ui.text_appearance import TextAppearance
from covex_label_manager.qt_ui.controlled_import import ControlledImportDialog


def test_sheet_designer_quantities_are_explicit_and_do_not_fill_unused_slots(studio):
    w, session, app = studio
    work = w.api.work.create(session.initial_id, name="RC2 synthetic sheet")
    # Existing profile stays unchanged until dialog is accepted and CAS saved.
    original = dict(work["profile"])
    dialog = SheetDesigner(w, original, quantities={"count": "1", "copies": "1", "selection": ""})
    dialog.count.setValue(2)  # positions per sheet, not copies
    dialog.arrange()
    assert dialog.quantities() == {"count": "1", "copies": "1"}
    assert "1 etiquetas reales" in dialog.quantity_summary.text()
    dialog.copy_count.setValue(2)
    assert dialog.quantities() == {"count": "1", "copies": "2"}
    assert "2 etiquetas reales" in dialog.quantity_summary.text()
    assert w.api.work.get(work["uid"])["copies"] == "1"
    dialog.reject()
    assert w.api.work.get(work["uid"])["profile"] == original


def test_sheet_designer_commits_profile_and_copies_to_same_work(studio, monkeypatch):
    w, session, app = studio
    work = w.api.work.create(session.initial_id, name="RC2 sheet commit")
    w.emission_work = work
    w.refresh_work_panels()
    w.preview_timer.stop()
    def accepted(d):
        d.copy_count.setValue(2)
        d.count.setValue(2)
        d.arrange()
        return QDialog.DialogCode.Accepted
    monkeypatch.setattr(SheetDesigner, "exec", accepted)
    w.emission_panel.design_sheet()
    committed = w.api.work.get(work["uid"])
    assert committed["count"] == "1"
    assert committed["copies"] == "2"
    assert committed["profile"]["layout_mode"] == "free"
    assert len(committed["profile"]["slots"]) == 2
    assert w.emission_work["generation"] == committed["generation"]


def test_activation_of_embedded_font_is_explicit(studio):
    w, session, app = studio
    panel = TextAppearance(w)
    assert panel.family.currentData() is None
    assert not panel.align.isEnabled()
    assert panel.activate_font.isVisibleTo(w) or not panel.isVisible()
    panel.select_editable_font()
    assert panel.family.currentData() == "sans"
    assert panel.align.isEnabled() and panel.wrap.isEnabled()
    assert panel.configuration()["family"] == "sans"
    panel.deleteLater()


def test_emission_blockers_are_visible_for_unapproved_design(studio):
    w, session, app = studio
    pending = session.initial_id
    work = w.api.work.create(pending, name="RC2 pending")
    w.emission_work = work
    w.refresh_work_panels()
    w.preview_timer.stop()
    review = w.refresh_emission_review()
    assert not review["production_allowed"]
    assert not w.native_issue.isEnabled()
    assert "No se puede emitir" in w.emission_blockers.text()
    assert w.emission_blockers.text().strip() != ""


def test_bulk_import_classification_never_forces_blocked_rows(studio, tmp_path):
    w, session, app = studio
    class FakeApi:
        def catalog_migration_preview(self, folder):
            return {"files": [
                {"source": "alpha.pdf", "name": "alpha", "version": "00", "category": "synthetic", "status": "REVIEW_REQUIRED"},
                {"source": "beta.pdf", "name": "beta", "version": "00", "category": "synthetic", "status": "REVIEW_REQUIRED"},
                {"source": "blocked.pdf", "name": "blocked", "version": "00", "category": "synthetic", "status": "BLOCKED_UNSAFE"},
            ]}
        def labels(self): return []
    dialog = ControlledImportDialog(w, FakeApi(), folder=tmp_path)
    dialog.pages.setCurrentIndex(1)
    dialog.select_all_rows()
    assert dialog.selected_rows() == [0, 1, 2]
    dialog.bulk_new_labels()
    assert [x.currentData() for x in dialog.row_actions] == ["NEW_LABEL", "NEW_LABEL", None]
    assert not dialog.confirm_identity.isChecked()
    dialog.bulk_new_revisions()
    assert [x.currentData() for x in dialog.row_actions] == ["NEW_REVISION", "NEW_REVISION", None]
    assert not dialog.targets[0].currentData()
    with pytest.raises(ValueError, match="seleccione destino"):
        dialog.selected()
    dialog.reject()


def test_compact_emission_keeps_all_blockers_and_pdf_space(studio):
    """Short viewport must never let a long warning list hide the native PDF."""
    w, session, app = studio
    w.navigate("emission")
    w.resize(910, 472)  # 1366x768 desktop with Windows scale factor 150 %
    w.emission_blockers.setText(
        "No se puede emitir definitivamente:\n"
        + "\n".join(f"• Motivo de bloqueo documental número {n}" for n in range(12))
    )
    w.emission_feedback.setText("Revise antes de emitir: " + "Error documental. " * 8)
    w.adapt_emission_layout()
    w.emission_compact.setCurrentIndex(1)  # PDF tab must be the active compact pane.
    app.processEvents()
    assert w.emission_compact.isVisible()
    assert not w.emission_blockers_scroll.isVisible()
    assert not w.emission_feedback.isVisible()
    assert not w.emission_summary.isVisible()
    assert w.compact_blockers_button.isVisible()
    assert "número 11" in w.emission_blockers.text()
    assert "número 11" in w.compact_blockers_button.toolTip()
    assert w.emission_pdf.view.height() > 70


def test_integrated_status_legacy_short_number_uses_measured_ink():
    """Historical R7B integrated overlay must accept one digit in a short box."""
    import fitz
    from covex_label_manager.engine import _paint_status_r7b, LayoutError
    with fitz.open() as origin, fitz.open() as result:
        origin.new_page(width=120,height=90)
        canvas=result.new_page(width=120,height=90)
        field={'key':'campo_2','label':'Campo 2','rect':[10,10,25,18.5],
               'font_size':10,'bold':False,'required':True}
        contract={'contract':1,'page':0,'crop':[0,0,120,90],'fields':[field]}
        status={'fields':{'campo_2':'1'}}
        _paint_status_r7b(canvas,origin,{'r7b_layout':contract,'kind':'aprobado'},
                          fitz.Rect(0,0,120,90),{},status,True,[])
        assert '1' in canvas.get_text()
        field['rect']=[10,10,25,15]
        with pytest.raises(LayoutError,match='excede'):
            _paint_status_r7b(result.new_page(width=120,height=90),origin,
                              {'r7b_layout':contract,'kind':'aprobado'},
                              fitz.Rect(0,0,120,90),{},status,True,[])


def test_emission_options_expose_real_size_and_documentary_numbering(studio,monkeypatch):
    """Physical sizing is available; 1/N never appears without an approved field."""
    from PySide6.QtWidgets import QMessageBox
    window,session,app=studio
    work=window.api.work.create(session.initial_id,name='Synthetic sizing and numbering')
    window.load_emission_work(work['uid'])
    window.navigate('emission')
    window.open_emission_size_settings()
    app.processEvents()
    assert window.emission_panel.tabs.currentIndex()==2
    assert window.emission_panel.profile_inputs['width_mm'].hasFocus()
    assert window.api.work.get(work['uid'])['profile']==work['profile']
    notes=[]
    monkeypatch.setattr(QMessageBox,'information',
                        lambda _window,title,message:notes.append((title,message)))
    window.explain_container_numbering()
    assert notes and 'Numeración' in notes[-1][0]
    assert 'variante' in notes[-1][1].lower() or 'contiene el campo' in notes[-1][1]
