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


def test_mini_mode_allows_small_pdf_with_visible_legibility_notice(studio):
    """Mini mode is explicitly chosen, durable and limited to size advisories."""
    import fitz
    w,session,app=studio
    api=session.services
    vid=next(row['version_id'] for row in api.library.entries() if row['state']=='APPROVED')
    work=api.work.create(vid,name='DEMO tamaño mini, ensayo de lectura')
    v=api.version(vid)
    width=35.
    height=width*float(v['base_h_mm'])/float(v['base_w_mm'])
    physical=dict(work['profile'],width_mm=width,height_mm=height)
    ready=api.work.save(work['uid'],work['generation'],{
        'profile':physical,'values':{'lote':'MINI-001','pn':'1 kg','pb':'2 kg'},
        'count':'3'})
    review=api.review_work(ready['uid'],ready['generation'])
    assert not review['production_allowed']
    assert any('pequeno' in entry['message'].lower() for entry in review['errors'])
    w.load_emission_work(ready['uid'])
    w.navigate('emission')
    panel=w.emission_panel
    assert not panel.mini_mode.isChecked()
    panel.mini_mode.setChecked(True)
    assert w.flush_emission_work()
    saved=api.work.get(ready['uid'])
    assert saved['profile']['mini_mode'] is True
    review=api.review_work(saved['uid'],saved['generation'])
    assert review['production_allowed'],review['errors']
    assert any('mini' in msg.lower() for msg in review['warnings'])
    target=api.output_path('cache','test-physical-mini.pdf')
    report=api.work.proof(saved['uid'],saved['generation'],target)
    assert any('pequeno' in msg.lower() for msg in report['warnings'])
    from covex_label_manager.engine import blocking_render_warnings
    assert blocking_render_warnings(report['warnings'],saved['profile'])==[]
    with fitz.open(target) as pdf:
        text=''.join(page.get_text() for page in pdf)
        assert 'MINI-001' in text and pdf.page_count>=1
    panel.mini_mode.setChecked(False)
    assert w.flush_emission_work()
    assert not api.review_work(w.emission_work['uid'],w.emission_work['generation'])['production_allowed']
    assert not api.issues()


def test_mini_mode_does_not_override_real_blocking_warnings(studio):
    from covex_label_manager.engine import blocking_render_warnings
    p={'mini_mode':True}
    warnings=['Texto pequeno (2.9 pt) en Lote: requiere revisar el formato.',
              'Contraste insuficiente (1.2:1).','Recorte protegido: texto crítico']
    assert blocking_render_warnings(warnings,p)==warnings[1:]
