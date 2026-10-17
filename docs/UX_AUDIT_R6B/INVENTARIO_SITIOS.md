# Inventario estático de sitios de interfaz

Registro generado por AST de todo `qt_ui`, `main_qt.py` y el consentimiento de migración. Cada sitio contiene contexto, línea, expresión completa, expansión de bucles, controlador explícito y referencias de tests en [inventario-sitios.json](inventario-sitios.json).

Un sitio de construcción no equivale a un control visible: la herencia elimina, mueve o reconecta controles. Los tests asociados se buscan por símbolo y son referencias para revisar; **no prueban por sí solos clic ni cobertura del sitio**. Véase INVENTARIO.md para resolución del controlador efectivo y alcance.

| ID | Pantalla/clase y método | Tipo | Fuente | Controlador explícito | Test por símbolo |
|---|---|---|---|---|---|
| S0001 | ReadinessDialog.__init__ | label | [covex_label_manager/qt_ui/acceptance_dialog.py:9](../../covex_label_manager/qt_ui/acceptance_dialog.py#L9) | Señales/registro JSON | Sin vínculo directo |
| S0002 | ReadinessDialog.__init__ | label | [covex_label_manager/qt_ui/acceptance_dialog.py:10](../../covex_label_manager/qt_ui/acceptance_dialog.py#L10) | Señales/registro JSON | Sin vínculo directo |
| S0003 | ReadinessDialog.__init__ | label | [covex_label_manager/qt_ui/acceptance_dialog.py:12](../../covex_label_manager/qt_ui/acceptance_dialog.py#L12) | Señales/registro JSON | Sin vínculo directo |
| S0004 | ReadinessDialog.__init__ | QTableWidget | [covex_label_manager/qt_ui/acceptance_dialog.py:13](../../covex_label_manager/qt_ui/acceptance_dialog.py#L13) | Señales/registro JSON | Sin vínculo directo |
| S0005 | ReadinessDialog.__init__ | button | [covex_label_manager/qt_ui/acceptance_dialog.py:17](../../covex_label_manager/qt_ui/acceptance_dialog.py#L17) | self.run | 2 |
| S0006 | ReadinessDialog.__init__ | button | [covex_label_manager/qt_ui/acceptance_dialog.py:18](../../covex_label_manager/qt_ui/acceptance_dialog.py#L18) | self.export_zip | Sin vínculo directo |
| S0007 | ReadinessDialog.__init__ | QDialogButtonBox | [covex_label_manager/qt_ui/acceptance_dialog.py:20](../../covex_label_manager/qt_ui/acceptance_dialog.py#L20) | Señales/registro JSON | 23 |
| S0008 | ReadinessDialog.__init__ | connect | [covex_label_manager/qt_ui/acceptance_dialog.py:21](../../covex_label_manager/qt_ui/acceptance_dialog.py#L21) | self.reject | 2 |
| S0009 | ReadinessDialog.run | warning | [covex_label_manager/qt_ui/acceptance_dialog.py:26](../../covex_label_manager/qt_ui/acceptance_dialog.py#L26) | Señales/registro JSON | Sin vínculo directo |
| S0010 | ReadinessDialog.export_zip | getSaveFileName | [covex_label_manager/qt_ui/acceptance_dialog.py:37](../../covex_label_manager/qt_ui/acceptance_dialog.py#L37) | Señales/registro JSON | Sin vínculo directo |
| S0011 | ReadinessDialog.export_zip | question | [covex_label_manager/qt_ui/acceptance_dialog.py:39](../../covex_label_manager/qt_ui/acceptance_dialog.py#L39) | Señales/registro JSON | 23 |
| S0012 | ReadinessDialog.export_zip | information | [covex_label_manager/qt_ui/acceptance_dialog.py:45](../../covex_label_manager/qt_ui/acceptance_dialog.py#L45) | Señales/registro JSON | Sin vínculo directo |
| S0013 | ReadinessDialog.export_zip | warning | [covex_label_manager/qt_ui/acceptance_dialog.py:48](../../covex_label_manager/qt_ui/acceptance_dialog.py#L48) | Señales/registro JSON | Sin vínculo directo |
| S0014 | spin | QDoubleSpinBox | [covex_label_manager/qt_ui/advanced_editor.py:17](../../covex_label_manager/qt_ui/advanced_editor.py#L17) | Señales/registro JSON | Sin vínculo directo |
| S0015 | RectangleView.mousePressEvent | button | [covex_label_manager/qt_ui/advanced_editor.py:42](../../covex_label_manager/qt_ui/advanced_editor.py#L42) | Señales/registro JSON | Sin vínculo directo |
| S0016 | RectangleDialog.__init__ | label | [covex_label_manager/qt_ui/advanced_editor.py:62](../../covex_label_manager/qt_ui/advanced_editor.py#L62) | Señales/registro JSON | Sin vínculo directo |
| S0017 | RectangleDialog.__init__ | label | [covex_label_manager/qt_ui/advanced_editor.py:63](../../covex_label_manager/qt_ui/advanced_editor.py#L63) | Señales/registro JSON | Sin vínculo directo |
| S0018 | RectangleDialog.__init__ | RectangleView | [covex_label_manager/qt_ui/advanced_editor.py:64](../../covex_label_manager/qt_ui/advanced_editor.py#L64) | Señales/registro JSON | 3 |
| S0019 | RectangleDialog.__init__ | connect | [covex_label_manager/qt_ui/advanced_editor.py:67](../../covex_label_manager/qt_ui/advanced_editor.py#L67) | self.from_form | Sin vínculo directo |
| S0020 | RectangleDialog.__init__ | addRow | [covex_label_manager/qt_ui/advanced_editor.py:68](../../covex_label_manager/qt_ui/advanced_editor.py#L68) | Señales/registro JSON | Sin vínculo directo |
| S0021 | RectangleDialog.__init__ | label | [covex_label_manager/qt_ui/advanced_editor.py:69](../../covex_label_manager/qt_ui/advanced_editor.py#L69) | Señales/registro JSON | Sin vínculo directo |
| S0022 | RectangleDialog.__init__ | QDialogButtonBox | [covex_label_manager/qt_ui/advanced_editor.py:72](../../covex_label_manager/qt_ui/advanced_editor.py#L72) | Señales/registro JSON | 23 |
| S0023 | RectangleDialog.__init__ | connect | [covex_label_manager/qt_ui/advanced_editor.py:73](../../covex_label_manager/qt_ui/advanced_editor.py#L73) | self.accept_valid | 1 |
| S0024 | RectangleDialog.__init__ | connect | [covex_label_manager/qt_ui/advanced_editor.py:73](../../covex_label_manager/qt_ui/advanced_editor.py#L73) | self.reject | 2 |
| S0025 | AdvancedEditorMixin.build_editor.section | QPushButton | [covex_label_manager/qt_ui/advanced_editor.py:144](../../covex_label_manager/qt_ui/advanced_editor.py#L144) | Señales/registro JSON | Sin vínculo directo |
| S0026 | AdvancedEditorMixin.build_editor.section | connect | [covex_label_manager/qt_ui/advanced_editor.py:146](../../covex_label_manager/qt_ui/advanced_editor.py#L146) | lambda checked, c=content, t=toggle, n=title: (c.setVisible(checked), t.setText(('▾ ' if checked else '▸ ') + n)) | 15 |
| S0027 | AdvancedEditorMixin.build_editor.action | button | [covex_label_manager/qt_ui/advanced_editor.py:150](../../covex_label_manager/qt_ui/advanced_editor.py#L150) | callback | Sin vínculo directo |
| S0028 | AdvancedEditorMixin.build_editor | action | [covex_label_manager/qt_ui/advanced_editor.py:152](../../covex_label_manager/qt_ui/advanced_editor.py#L152) | self.edit_crop | 1 |
| S0029 | AdvancedEditorMixin.build_editor | action | [covex_label_manager/qt_ui/advanced_editor.py:153](../../covex_label_manager/qt_ui/advanced_editor.py#L153) | self.edit_anchor | Sin vínculo directo |
| S0030 | AdvancedEditorMixin.build_editor | action | [covex_label_manager/qt_ui/advanced_editor.py:154](../../covex_label_manager/qt_ui/advanced_editor.py#L154) | self.relocate | 1 |
| S0031 | AdvancedEditorMixin.build_editor | action | [covex_label_manager/qt_ui/advanced_editor.py:156](../../covex_label_manager/qt_ui/advanced_editor.py#L156) | self.add_field | 1 |
| S0032 | AdvancedEditorMixin.build_editor | action | [covex_label_manager/qt_ui/advanced_editor.py:156](../../covex_label_manager/qt_ui/advanced_editor.py#L156) | self.remove_field | 1 |
| S0033 | AdvancedEditorMixin.build_editor | QComboBox | [covex_label_manager/qt_ui/advanced_editor.py:158](../../covex_label_manager/qt_ui/advanced_editor.py#L158) | Señales/registro JSON | Sin vínculo directo |
| S0034 | AdvancedEditorMixin.build_editor | addItem | [covex_label_manager/qt_ui/advanced_editor.py:159](../../covex_label_manager/qt_ui/advanced_editor.py#L159) | Señales/registro JSON | Sin vínculo directo |
| S0035 | AdvancedEditorMixin.build_editor | connect | [covex_label_manager/qt_ui/advanced_editor.py:161](../../covex_label_manager/qt_ui/advanced_editor.py#L161) | self.change_draw_mode | Sin vínculo directo |
| S0036 | AdvancedEditorMixin.build_editor | action | [covex_label_manager/qt_ui/advanced_editor.py:162](../../covex_label_manager/qt_ui/advanced_editor.py#L162) | self.edit_auxiliary | Sin vínculo directo |
| S0037 | AdvancedEditorMixin.build_editor | QComboBox | [covex_label_manager/qt_ui/advanced_editor.py:164](../../covex_label_manager/qt_ui/advanced_editor.py#L164) | Señales/registro JSON | Sin vínculo directo |
| S0038 | AdvancedEditorMixin.build_editor | addItem | [covex_label_manager/qt_ui/advanced_editor.py:165](../../covex_label_manager/qt_ui/advanced_editor.py#L165) | Señales/registro JSON | Sin vínculo directo |
| S0039 | AdvancedEditorMixin.build_editor | action | [covex_label_manager/qt_ui/advanced_editor.py:166](../../covex_label_manager/qt_ui/advanced_editor.py#L166) | self.align_selection | 1 |
| S0040 | AdvancedEditorMixin.build_editor | action | [covex_label_manager/qt_ui/advanced_editor.py:167](../../covex_label_manager/qt_ui/advanced_editor.py#L167) | self.edit_scale | Sin vínculo directo |
| S0041 | AdvancedEditorMixin.build_editor | button | [covex_label_manager/qt_ui/advanced_editor.py:168](../../covex_label_manager/qt_ui/advanced_editor.py#L168) | self.edit_output | 2 |
| S0042 | AdvancedEditorMixin.build_editor | action | [covex_label_manager/qt_ui/advanced_editor.py:170](../../covex_label_manager/qt_ui/advanced_editor.py#L170) | self.edit_status_area | 1 |
| S0043 | AdvancedEditorMixin.build_editor | button | [covex_label_manager/qt_ui/advanced_editor.py:171](../../covex_label_manager/qt_ui/advanced_editor.py#L171) | self.edit_output | 2 |
| S0044 | AdvancedEditorMixin.build_editor | label | [covex_label_manager/qt_ui/advanced_editor.py:172](../../covex_label_manager/qt_ui/advanced_editor.py#L172) | Señales/registro JSON | Sin vínculo directo |
| S0045 | AdvancedEditorMixin.build_editor | button | [covex_label_manager/qt_ui/advanced_editor.py:173](../../covex_label_manager/qt_ui/advanced_editor.py#L173) | lambda: self.open_legacy('editor') | Sin vínculo directo |
| S0046 | AdvancedEditorMixin.build_editor | button | [covex_label_manager/qt_ui/advanced_editor.py:175](../../covex_label_manager/qt_ui/advanced_editor.py#L175) | self.add_field | 1 |
| S0047 | AdvancedEditorMixin.build_editor | button | [covex_label_manager/qt_ui/advanced_editor.py:176](../../covex_label_manager/qt_ui/advanced_editor.py#L176) | self.draw_new_field | Sin vínculo directo |
| S0048 | AdvancedEditorMixin.build_editor | QCheckBox | [covex_label_manager/qt_ui/advanced_editor.py:179](../../covex_label_manager/qt_ui/advanced_editor.py#L179) | Señales/registro JSON | Sin vínculo directo |
| S0049 | AdvancedEditorMixin.build_editor | QCheckBox | [covex_label_manager/qt_ui/advanced_editor.py:180](../../covex_label_manager/qt_ui/advanced_editor.py#L180) | Señales/registro JSON | Sin vínculo directo |
| S0050 | AdvancedEditorMixin.build_editor | connect | [covex_label_manager/qt_ui/advanced_editor.py:180](../../covex_label_manager/qt_ui/advanced_editor.py#L180) | lambda *_: self.draw_editor() if self.design else None | 18 |
| S0051 | AdvancedEditorMixin.build_editor | button | [covex_label_manager/qt_ui/advanced_editor.py:181](../../covex_label_manager/qt_ui/advanced_editor.py#L181) | self.editable_variant | 2 |
| S0052 | AdvancedEditorMixin.build_editor | label | [covex_label_manager/qt_ui/advanced_editor.py:183](../../covex_label_manager/qt_ui/advanced_editor.py#L183) | Señales/registro JSON | Sin vínculo directo |
| S0053 | AdvancedEditorMixin.build_editor | connect | [covex_label_manager/qt_ui/advanced_editor.py:185](../../covex_label_manager/qt_ui/advanced_editor.py#L185) | self.list_selection | Sin vínculo directo |
| S0054 | AdvancedEditorMixin.build_editor | button | [covex_label_manager/qt_ui/advanced_editor.py:195](../../covex_label_manager/qt_ui/advanced_editor.py#L195) | self.undo_edit | 7 |
| S0055 | AdvancedEditorMixin.build_editor | button | [covex_label_manager/qt_ui/advanced_editor.py:195](../../covex_label_manager/qt_ui/advanced_editor.py#L195) | self.redo_edit | 4 |
| S0056 | AdvancedEditorMixin.build_editor | QShortcut | [covex_label_manager/qt_ui/advanced_editor.py:197](../../covex_label_manager/qt_ui/advanced_editor.py#L197) | Señales/registro JSON | Sin vínculo directo |
| S0057 | AdvancedEditorMixin.build_editor | connect | [covex_label_manager/qt_ui/advanced_editor.py:198](../../covex_label_manager/qt_ui/advanced_editor.py#L198) | self.undo_edit | 7 |
| S0058 | AdvancedEditorMixin.build_editor | QShortcut | [covex_label_manager/qt_ui/advanced_editor.py:199](../../covex_label_manager/qt_ui/advanced_editor.py#L199) | Señales/registro JSON | Sin vínculo directo |
| S0059 | AdvancedEditorMixin.build_editor | connect | [covex_label_manager/qt_ui/advanced_editor.py:200](../../covex_label_manager/qt_ui/advanced_editor.py#L200) | self.redo_edit | 4 |
| S0060 | AdvancedEditorMixin.open_editor | warning | [covex_label_manager/qt_ui/advanced_editor.py:224](../../covex_label_manager/qt_ui/advanced_editor.py#L224) | Señales/registro JSON | Sin vínculo directo |
| S0061 | AdvancedEditorMixin.draw_editor | addItem | [covex_label_manager/qt_ui/advanced_editor.py:268](../../covex_label_manager/qt_ui/advanced_editor.py#L268) | Señales/registro JSON | Sin vínculo directo |
| S0062 | AdvancedEditorMixin.draw_editor | addItem | [covex_label_manager/qt_ui/advanced_editor.py:268](../../covex_label_manager/qt_ui/advanced_editor.py#L268) | Señales/registro JSON | Sin vínculo directo |
| S0063 | AdvancedEditorMixin.command | warning | [covex_label_manager/qt_ui/advanced_editor.py:329](../../covex_label_manager/qt_ui/advanced_editor.py#L329) | Señales/registro JSON | Sin vínculo directo |
| S0064 | AdvancedEditorMixin.apply_operation | warning | [covex_label_manager/qt_ui/advanced_editor.py:335](../../covex_label_manager/qt_ui/advanced_editor.py#L335) | Señales/registro JSON | Sin vínculo directo |
| S0065 | AdvancedEditorMixin.save_work | warning | [covex_label_manager/qt_ui/advanced_editor.py:429](../../covex_label_manager/qt_ui/advanced_editor.py#L429) | Señales/registro JSON | Sin vínculo directo |
| S0066 | AdvancedEditorMixin.resolve_work | question | [covex_label_manager/qt_ui/advanced_editor.py:433](../../covex_label_manager/qt_ui/advanced_editor.py#L433) | Señales/registro JSON | 23 |
| S0067 | AdvancedEditorMixin.editable_variant | question | [covex_label_manager/qt_ui/advanced_editor.py:451](../../covex_label_manager/qt_ui/advanced_editor.py#L451) | Señales/registro JSON | 23 |
| S0068 | AdvancedEditorMixin.add_field | QDialog | [covex_label_manager/qt_ui/advanced_editor.py:472](../../covex_label_manager/qt_ui/advanced_editor.py#L472) | Señales/registro JSON | Sin vínculo directo |
| S0069 | AdvancedEditorMixin.add_field | QLineEdit | [covex_label_manager/qt_ui/advanced_editor.py:473](../../covex_label_manager/qt_ui/advanced_editor.py#L473) | Señales/registro JSON | Sin vínculo directo |
| S0070 | AdvancedEditorMixin.add_field | QLineEdit | [covex_label_manager/qt_ui/advanced_editor.py:473](../../covex_label_manager/qt_ui/advanced_editor.py#L473) | Señales/registro JSON | Sin vínculo directo |
| S0071 | AdvancedEditorMixin.add_field | QComboBox | [covex_label_manager/qt_ui/advanced_editor.py:474](../../covex_label_manager/qt_ui/advanced_editor.py#L474) | Señales/registro JSON | Sin vínculo directo |
| S0072 | AdvancedEditorMixin.add_field | addItem | [covex_label_manager/qt_ui/advanced_editor.py:475](../../covex_label_manager/qt_ui/advanced_editor.py#L475) | Señales/registro JSON | Sin vínculo directo |
| S0073 | AdvancedEditorMixin.add_field | connect | [covex_label_manager/qt_ui/advanced_editor.py:476](../../covex_label_manager/qt_ui/advanced_editor.py#L476) | lambda *_: key.setText(kind.currentData()) if kind.currentData() in ('numero', 'texto_fijo') else None | 16 |
| S0074 | AdvancedEditorMixin.add_field | QLineEdit | [covex_label_manager/qt_ui/advanced_editor.py:477](../../covex_label_manager/qt_ui/advanced_editor.py#L477) | Señales/registro JSON | Sin vínculo directo |
| S0075 | AdvancedEditorMixin.add_field | addRow | [covex_label_manager/qt_ui/advanced_editor.py:477](../../covex_label_manager/qt_ui/advanced_editor.py#L477) | Señales/registro JSON | Sin vínculo directo |
| S0076 | AdvancedEditorMixin.add_field | QCheckBox | [covex_label_manager/qt_ui/advanced_editor.py:478](../../covex_label_manager/qt_ui/advanced_editor.py#L478) | Señales/registro JSON | Sin vínculo directo |
| S0077 | AdvancedEditorMixin.add_field | QCheckBox | [covex_label_manager/qt_ui/advanced_editor.py:478](../../covex_label_manager/qt_ui/advanced_editor.py#L478) | Señales/registro JSON | Sin vínculo directo |
| S0078 | AdvancedEditorMixin.add_field | QCheckBox | [covex_label_manager/qt_ui/advanced_editor.py:478](../../covex_label_manager/qt_ui/advanced_editor.py#L478) | Señales/registro JSON | Sin vínculo directo |
| S0079 | AdvancedEditorMixin.add_field | addRow | [covex_label_manager/qt_ui/advanced_editor.py:479](../../covex_label_manager/qt_ui/advanced_editor.py#L479) | Señales/registro JSON | Sin vínculo directo |
| S0080 | AdvancedEditorMixin.add_field | label | [covex_label_manager/qt_ui/advanced_editor.py:482](../../covex_label_manager/qt_ui/advanced_editor.py#L482) | Señales/registro JSON | Sin vínculo directo |
| S0081 | AdvancedEditorMixin.add_field | QDialogButtonBox | [covex_label_manager/qt_ui/advanced_editor.py:483](../../covex_label_manager/qt_ui/advanced_editor.py#L483) | Señales/registro JSON | 23 |
| S0082 | AdvancedEditorMixin.add_field | connect | [covex_label_manager/qt_ui/advanced_editor.py:488](../../covex_label_manager/qt_ui/advanced_editor.py#L488) | accept | Sin vínculo directo |
| S0083 | AdvancedEditorMixin.add_field | connect | [covex_label_manager/qt_ui/advanced_editor.py:488](../../covex_label_manager/qt_ui/advanced_editor.py#L488) | dialog.reject | 2 |
| S0084 | AdvancedEditorMixin.remove_field | question | [covex_label_manager/qt_ui/advanced_editor.py:499](../../covex_label_manager/qt_ui/advanced_editor.py#L499) | Señales/registro JSON | Sin vínculo directo |
| S0085 | AdvancedEditorMixin.edit_crop | warning | [covex_label_manager/qt_ui/advanced_editor.py:512](../../covex_label_manager/qt_ui/advanced_editor.py#L512) | Señales/registro JSON | Sin vínculo directo |
| S0086 | AdvancedEditorMixin.edit_status_area | QCheckBox | [covex_label_manager/qt_ui/advanced_editor.py:520](../../covex_label_manager/qt_ui/advanced_editor.py#L520) | Señales/registro JSON | Sin vínculo directo |
| S0087 | AdvancedEditorMixin.edit_status_area | QComboBox | [covex_label_manager/qt_ui/advanced_editor.py:521](../../covex_label_manager/qt_ui/advanced_editor.py#L521) | Señales/registro JSON | Sin vínculo directo |
| S0088 | AdvancedEditorMixin.edit_status_area | addItem | [covex_label_manager/qt_ui/advanced_editor.py:521](../../covex_label_manager/qt_ui/advanced_editor.py#L521) | Señales/registro JSON | Sin vínculo directo |
| S0089 | AdvancedEditorMixin.edit_status_area | addItem | [covex_label_manager/qt_ui/advanced_editor.py:522](../../covex_label_manager/qt_ui/advanced_editor.py#L522) | Señales/registro JSON | Sin vínculo directo |
| S0090 | AdvancedEditorMixin.edit_status_area | question | [covex_label_manager/qt_ui/advanced_editor.py:530](../../covex_label_manager/qt_ui/advanced_editor.py#L530) | Señales/registro JSON | Sin vínculo directo |
| S0091 | AdvancedEditorMixin.edit_anchor | information | [covex_label_manager/qt_ui/advanced_editor.py:536](../../covex_label_manager/qt_ui/advanced_editor.py#L536) | Señales/registro JSON | Sin vínculo directo |
| S0092 | AdvancedEditorMixin.edit_anchor | QDialog | [covex_label_manager/qt_ui/advanced_editor.py:541](../../covex_label_manager/qt_ui/advanced_editor.py#L541) | Señales/registro JSON | Sin vínculo directo |
| S0093 | AdvancedEditorMixin.edit_anchor | label | [covex_label_manager/qt_ui/advanced_editor.py:542](../../covex_label_manager/qt_ui/advanced_editor.py#L542) | Señales/registro JSON | Sin vínculo directo |
| S0094 | AdvancedEditorMixin.edit_anchor | QLineEdit | [covex_label_manager/qt_ui/advanced_editor.py:543](../../covex_label_manager/qt_ui/advanced_editor.py#L543) | Señales/registro JSON | Sin vínculo directo |
| S0095 | AdvancedEditorMixin.edit_anchor | QSplitter | [covex_label_manager/qt_ui/advanced_editor.py:544](../../covex_label_manager/qt_ui/advanced_editor.py#L544) | Señales/registro JSON | Sin vínculo directo |
| S0096 | AdvancedEditorMixin.edit_anchor | QListWidget | [covex_label_manager/qt_ui/advanced_editor.py:544](../../covex_label_manager/qt_ui/advanced_editor.py#L544) | Señales/registro JSON | Sin vínculo directo |
| S0097 | AdvancedEditorMixin.edit_anchor | RectangleView | [covex_label_manager/qt_ui/advanced_editor.py:544](../../covex_label_manager/qt_ui/advanced_editor.py#L544) | Señales/registro JSON | Sin vínculo directo |
| S0098 | AdvancedEditorMixin.edit_anchor | addItem | [covex_label_manager/qt_ui/advanced_editor.py:546](../../covex_label_manager/qt_ui/advanced_editor.py#L546) | Señales/registro JSON | Sin vínculo directo |
| S0099 | AdvancedEditorMixin.edit_anchor | connect | [covex_label_manager/qt_ui/advanced_editor.py:548](../../covex_label_manager/qt_ui/advanced_editor.py#L548) | lambda text: [ls.item(i).setHidden(text.casefold() not in spans[i]['text'].casefold()) for i in range(len(spans))] | 3 |
| S0100 | AdvancedEditorMixin.edit_anchor | connect | [covex_label_manager/qt_ui/advanced_editor.py:549](../../covex_label_manager/qt_ui/advanced_editor.py#L549) | lambda i: view.paint_rect(spans[i]['bbox']) if i >= 0 else None | Sin vínculo directo |
| S0101 | AdvancedEditorMixin.edit_anchor | QDialogButtonBox | [covex_label_manager/qt_ui/advanced_editor.py:550](../../covex_label_manager/qt_ui/advanced_editor.py#L550) | Señales/registro JSON | 23 |
| S0102 | AdvancedEditorMixin.edit_anchor | connect | [covex_label_manager/qt_ui/advanced_editor.py:551](../../covex_label_manager/qt_ui/advanced_editor.py#L551) | lambda: dialog.accept() if ls.currentRow() >= 0 and (not ls.currentItem().isHidden()) else None | 2 |
| S0103 | AdvancedEditorMixin.edit_anchor | connect | [covex_label_manager/qt_ui/advanced_editor.py:551](../../covex_label_manager/qt_ui/advanced_editor.py#L551) | dialog.reject | 2 |
| S0104 | AdvancedEditorMixin.edit_anchor | warning | [covex_label_manager/qt_ui/advanced_editor.py:556](../../covex_label_manager/qt_ui/advanced_editor.py#L556) | Señales/registro JSON | Sin vínculo directo |
| S0105 | AdvancedEditorMixin.relocate | question | [covex_label_manager/qt_ui/advanced_editor.py:563](../../covex_label_manager/qt_ui/advanced_editor.py#L563) | Señales/registro JSON | Sin vínculo directo |
| S0106 | AdvancedEditorMixin.edit_scale | QDialog | [covex_label_manager/qt_ui/advanced_editor.py:572](../../covex_label_manager/qt_ui/advanced_editor.py#L572) | Señales/registro JSON | Sin vínculo directo |
| S0107 | AdvancedEditorMixin.edit_scale | label | [covex_label_manager/qt_ui/advanced_editor.py:573](../../covex_label_manager/qt_ui/advanced_editor.py#L573) | Señales/registro JSON | Sin vínculo directo |
| S0108 | AdvancedEditorMixin.edit_scale | QCheckBox | [covex_label_manager/qt_ui/advanced_editor.py:575](../../covex_label_manager/qt_ui/advanced_editor.py#L575) | Señales/registro JSON | Sin vínculo directo |
| S0109 | AdvancedEditorMixin.edit_scale | QCheckBox | [covex_label_manager/qt_ui/advanced_editor.py:576](../../covex_label_manager/qt_ui/advanced_editor.py#L576) | Señales/registro JSON | Sin vínculo directo |
| S0110 | AdvancedEditorMixin.edit_scale | QDialogButtonBox | [covex_label_manager/qt_ui/advanced_editor.py:577](../../covex_label_manager/qt_ui/advanced_editor.py#L577) | Señales/registro JSON | 23 |
| S0111 | AdvancedEditorMixin.edit_scale | connect | [covex_label_manager/qt_ui/advanced_editor.py:578](../../covex_label_manager/qt_ui/advanced_editor.py#L578) | dialog.accept | Sin vínculo directo |
| S0112 | AdvancedEditorMixin.edit_scale | connect | [covex_label_manager/qt_ui/advanced_editor.py:578](../../covex_label_manager/qt_ui/advanced_editor.py#L578) | dialog.reject | 2 |
| S0113 | AdvancedEditorMixin.edit_auxiliary | QDialog | [covex_label_manager/qt_ui/advanced_editor.py:586](../../covex_label_manager/qt_ui/advanced_editor.py#L586) | Señales/registro JSON | Sin vínculo directo |
| S0114 | AdvancedEditorMixin.edit_auxiliary | label | [covex_label_manager/qt_ui/advanced_editor.py:587](../../covex_label_manager/qt_ui/advanced_editor.py#L587) | Señales/registro JSON | Sin vínculo directo |
| S0115 | AdvancedEditorMixin.edit_auxiliary | QCheckBox | [covex_label_manager/qt_ui/advanced_editor.py:588](../../covex_label_manager/qt_ui/advanced_editor.py#L588) | Señales/registro JSON | Sin vínculo directo |
| S0116 | AdvancedEditorMixin.edit_auxiliary | addRow | [covex_label_manager/qt_ui/advanced_editor.py:592](../../covex_label_manager/qt_ui/advanced_editor.py#L592) | Señales/registro JSON | Sin vínculo directo |
| S0117 | AdvancedEditorMixin.edit_auxiliary | addRow | [covex_label_manager/qt_ui/advanced_editor.py:594](../../covex_label_manager/qt_ui/advanced_editor.py#L594) | Señales/registro JSON | Sin vínculo directo |
| S0118 | AdvancedEditorMixin.edit_auxiliary | addRow | [covex_label_manager/qt_ui/advanced_editor.py:594](../../covex_label_manager/qt_ui/advanced_editor.py#L594) | Señales/registro JSON | Sin vínculo directo |
| S0119 | AdvancedEditorMixin.edit_auxiliary | addRow | [covex_label_manager/qt_ui/advanced_editor.py:594](../../covex_label_manager/qt_ui/advanced_editor.py#L594) | Señales/registro JSON | Sin vínculo directo |
| S0120 | AdvancedEditorMixin.edit_auxiliary | QDialogButtonBox | [covex_label_manager/qt_ui/advanced_editor.py:595](../../covex_label_manager/qt_ui/advanced_editor.py#L595) | Señales/registro JSON | 23 |
| S0121 | AdvancedEditorMixin.edit_auxiliary | connect | [covex_label_manager/qt_ui/advanced_editor.py:596](../../covex_label_manager/qt_ui/advanced_editor.py#L596) | dialog.accept | Sin vínculo directo |
| S0122 | AdvancedEditorMixin.edit_auxiliary | connect | [covex_label_manager/qt_ui/advanced_editor.py:596](../../covex_label_manager/qt_ui/advanced_editor.py#L596) | dialog.reject | 2 |
| S0123 | AdvancedEditorMixin.edit_auxiliary | information | [covex_label_manager/qt_ui/advanced_editor.py:599](../../covex_label_manager/qt_ui/advanced_editor.py#L599) | Señales/registro JSON | Sin vínculo directo |
| S0124 | AdvancedEditorMixin.edit_output | QDialog | [covex_label_manager/qt_ui/advanced_editor.py:607](../../covex_label_manager/qt_ui/advanced_editor.py#L607) | Señales/registro JSON | Sin vínculo directo |
| S0125 | AdvancedEditorMixin.edit_output | label | [covex_label_manager/qt_ui/advanced_editor.py:608](../../covex_label_manager/qt_ui/advanced_editor.py#L608) | Señales/registro JSON | Sin vínculo directo |
| S0126 | AdvancedEditorMixin.edit_output | QComboBox | [covex_label_manager/qt_ui/advanced_editor.py:609](../../covex_label_manager/qt_ui/advanced_editor.py#L609) | Señales/registro JSON | Sin vínculo directo |
| S0127 | AdvancedEditorMixin.edit_output | addItem | [covex_label_manager/qt_ui/advanced_editor.py:609](../../covex_label_manager/qt_ui/advanced_editor.py#L609) | Señales/registro JSON | Sin vínculo directo |
| S0128 | AdvancedEditorMixin.edit_output | addItem | [covex_label_manager/qt_ui/advanced_editor.py:610](../../covex_label_manager/qt_ui/advanced_editor.py#L610) | Señales/registro JSON | Sin vínculo directo |
| S0129 | AdvancedEditorMixin.edit_output | addRow | [covex_label_manager/qt_ui/advanced_editor.py:615](../../covex_label_manager/qt_ui/advanced_editor.py#L615) | Señales/registro JSON | Sin vínculo directo |
| S0130 | AdvancedEditorMixin.edit_output | QComboBox | [covex_label_manager/qt_ui/advanced_editor.py:616](../../covex_label_manager/qt_ui/advanced_editor.py#L616) | Señales/registro JSON | Sin vínculo directo |
| S0131 | AdvancedEditorMixin.edit_output | addItem | [covex_label_manager/qt_ui/advanced_editor.py:616](../../covex_label_manager/qt_ui/advanced_editor.py#L616) | Señales/registro JSON | Sin vínculo directo |
| S0132 | AdvancedEditorMixin.edit_output | addItem | [covex_label_manager/qt_ui/advanced_editor.py:616](../../covex_label_manager/qt_ui/advanced_editor.py#L616) | Señales/registro JSON | Sin vínculo directo |
| S0133 | AdvancedEditorMixin.edit_output | addRow | [covex_label_manager/qt_ui/advanced_editor.py:616](../../covex_label_manager/qt_ui/advanced_editor.py#L616) | Señales/registro JSON | Sin vínculo directo |
| S0134 | AdvancedEditorMixin.edit_output | QLineEdit | [covex_label_manager/qt_ui/advanced_editor.py:617](../../covex_label_manager/qt_ui/advanced_editor.py#L617) | Señales/registro JSON | 32 |
| S0135 | AdvancedEditorMixin.edit_output | addRow | [covex_label_manager/qt_ui/advanced_editor.py:617](../../covex_label_manager/qt_ui/advanced_editor.py#L617) | Señales/registro JSON | Sin vínculo directo |
| S0136 | AdvancedEditorMixin.edit_output | label | [covex_label_manager/qt_ui/advanced_editor.py:618](../../covex_label_manager/qt_ui/advanced_editor.py#L618) | Señales/registro JSON | Sin vínculo directo |
| S0137 | AdvancedEditorMixin.edit_output | connect | [covex_label_manager/qt_ui/advanced_editor.py:634](../../covex_label_manager/qt_ui/advanced_editor.py#L634) | choose | Sin vínculo directo |
| S0138 | AdvancedEditorMixin.edit_output | connect | [covex_label_manager/qt_ui/advanced_editor.py:635](../../covex_label_manager/qt_ui/advanced_editor.py#L635) | update | Sin vínculo directo |
| S0139 | AdvancedEditorMixin.edit_output | connect | [covex_label_manager/qt_ui/advanced_editor.py:636](../../covex_label_manager/qt_ui/advanced_editor.py#L636) | update | Sin vínculo directo |
| S0140 | AdvancedEditorMixin.edit_output.proof | QDialog | [covex_label_manager/qt_ui/advanced_editor.py:641](../../covex_label_manager/qt_ui/advanced_editor.py#L641) | Señales/registro JSON | Sin vínculo directo |
| S0141 | AdvancedEditorMixin.edit_output.proof | label | [covex_label_manager/qt_ui/advanced_editor.py:642](../../covex_label_manager/qt_ui/advanced_editor.py#L642) | Señales/registro JSON | Sin vínculo directo |
| S0142 | AdvancedEditorMixin.edit_output.proof | Preview | [covex_label_manager/qt_ui/advanced_editor.py:643](../../covex_label_manager/qt_ui/advanced_editor.py#L643) | Señales/registro JSON | Sin vínculo directo |
| S0143 | AdvancedEditorMixin.edit_output.proof | label | [covex_label_manager/qt_ui/advanced_editor.py:646](../../covex_label_manager/qt_ui/advanced_editor.py#L646) | Señales/registro JSON | Sin vínculo directo |
| S0144 | AdvancedEditorMixin.edit_output.proof | QDialogButtonBox | [covex_label_manager/qt_ui/advanced_editor.py:647](../../covex_label_manager/qt_ui/advanced_editor.py#L647) | Señales/registro JSON | 23 |
| S0145 | AdvancedEditorMixin.edit_output.proof | button | [covex_label_manager/qt_ui/advanced_editor.py:647](../../covex_label_manager/qt_ui/advanced_editor.py#L647) | Señales/registro JSON | 23 |
| S0146 | AdvancedEditorMixin.edit_output.proof | connect | [covex_label_manager/qt_ui/advanced_editor.py:647](../../covex_label_manager/qt_ui/advanced_editor.py#L647) | preview.reject | 2 |
| S0147 | AdvancedEditorMixin.edit_output.proof | warning | [covex_label_manager/qt_ui/advanced_editor.py:648](../../covex_label_manager/qt_ui/advanced_editor.py#L648) | Señales/registro JSON | Sin vínculo directo |
| S0148 | AdvancedEditorMixin.edit_output.save_profile | question | [covex_label_manager/qt_ui/advanced_editor.py:655](../../covex_label_manager/qt_ui/advanced_editor.py#L655) | Señales/registro JSON | Sin vínculo directo |
| S0149 | AdvancedEditorMixin.edit_output.save_profile | warning | [covex_label_manager/qt_ui/advanced_editor.py:657](../../covex_label_manager/qt_ui/advanced_editor.py#L657) | Señales/registro JSON | Sin vínculo directo |
| S0150 | AdvancedEditorMixin.edit_output | button | [covex_label_manager/qt_ui/advanced_editor.py:658](../../covex_label_manager/qt_ui/advanced_editor.py#L658) | proof | Sin vínculo directo |
| S0151 | AdvancedEditorMixin.edit_output | button | [covex_label_manager/qt_ui/advanced_editor.py:658](../../covex_label_manager/qt_ui/advanced_editor.py#L658) | save_profile | Sin vínculo directo |
| S0152 | AdvancedEditorMixin.edit_output | QDialogButtonBox | [covex_label_manager/qt_ui/advanced_editor.py:659](../../covex_label_manager/qt_ui/advanced_editor.py#L659) | Señales/registro JSON | 23 |
| S0153 | AdvancedEditorMixin.edit_output | connect | [covex_label_manager/qt_ui/advanced_editor.py:659](../../covex_label_manager/qt_ui/advanced_editor.py#L659) | dialog.accept | Sin vínculo directo |
| S0154 | AdvancedEditorMixin.edit_output | connect | [covex_label_manager/qt_ui/advanced_editor.py:659](../../covex_label_manager/qt_ui/advanced_editor.py#L659) | dialog.reject | 2 |
| S0155 | CatalogExchangeMixin.review_catalog_folder | getExistingDirectory | [covex_label_manager/qt_ui/catalog_exchange_ui.py:12](../../covex_label_manager/qt_ui/catalog_exchange_ui.py#L12) | Señales/registro JSON | Sin vínculo directo |
| S0156 | CatalogExchangeMixin.review_catalog_folder | QDialog | [covex_label_manager/qt_ui/catalog_exchange_ui.py:16](../../covex_label_manager/qt_ui/catalog_exchange_ui.py#L16) | Señales/registro JSON | Sin vínculo directo |
| S0157 | CatalogExchangeMixin.review_catalog_folder | label | [covex_label_manager/qt_ui/catalog_exchange_ui.py:18](../../covex_label_manager/qt_ui/catalog_exchange_ui.py#L18) | Señales/registro JSON | Sin vínculo directo |
| S0158 | CatalogExchangeMixin.review_catalog_folder | QPlainTextEdit | [covex_label_manager/qt_ui/catalog_exchange_ui.py:21](../../covex_label_manager/qt_ui/catalog_exchange_ui.py#L21) | Señales/registro JSON | 4 |
| S0159 | CatalogExchangeMixin.review_catalog_folder | QDialogButtonBox | [covex_label_manager/qt_ui/catalog_exchange_ui.py:23](../../covex_label_manager/qt_ui/catalog_exchange_ui.py#L23) | Señales/registro JSON | 23 |
| S0160 | CatalogExchangeMixin.review_catalog_folder | connect | [covex_label_manager/qt_ui/catalog_exchange_ui.py:24](../../covex_label_manager/qt_ui/catalog_exchange_ui.py#L24) | dialog.reject | 2 |
| S0161 | CatalogExchangeMixin.review_catalog_folder | warning | [covex_label_manager/qt_ui/catalog_exchange_ui.py:26](../../covex_label_manager/qt_ui/catalog_exchange_ui.py#L26) | Señales/registro JSON | Sin vínculo directo |
| S0162 | CatalogExchangeMixin.export_entire_library | getSaveFileName | [covex_label_manager/qt_ui/catalog_exchange_ui.py:30](../../covex_label_manager/qt_ui/catalog_exchange_ui.py#L30) | Señales/registro JSON | Sin vínculo directo |
| S0163 | CatalogExchangeMixin.export_entire_library | question | [covex_label_manager/qt_ui/catalog_exchange_ui.py:33](../../covex_label_manager/qt_ui/catalog_exchange_ui.py#L33) | Señales/registro JSON | 23 |
| S0164 | CatalogExchangeMixin.export_entire_library | information | [covex_label_manager/qt_ui/catalog_exchange_ui.py:41](../../covex_label_manager/qt_ui/catalog_exchange_ui.py#L41) | Señales/registro JSON | Sin vínculo directo |
| S0165 | CatalogExchangeMixin.export_entire_library | warning | [covex_label_manager/qt_ui/catalog_exchange_ui.py:44](../../covex_label_manager/qt_ui/catalog_exchange_ui.py#L44) | Señales/registro JSON | Sin vínculo directo |
| S0166 | CatalogExchangeMixin.reconcile_master | getOpenFileName | [covex_label_manager/qt_ui/catalog_exchange_ui.py:48](../../covex_label_manager/qt_ui/catalog_exchange_ui.py#L48) | Señales/registro JSON | Sin vínculo directo |
| S0167 | CatalogExchangeMixin.reconcile_master | warning | [covex_label_manager/qt_ui/catalog_exchange_ui.py:54](../../covex_label_manager/qt_ui/catalog_exchange_ui.py#L54) | Señales/registro JSON | Sin vínculo directo |
| S0168 | CompareDialog.__init__ | QComboBox | [covex_label_manager/qt_ui/compare.py:19](../../covex_label_manager/qt_ui/compare.py#L19) | Señales/registro JSON | Sin vínculo directo |
| S0169 | CompareDialog.__init__ | QComboBox | [covex_label_manager/qt_ui/compare.py:19](../../covex_label_manager/qt_ui/compare.py#L19) | Señales/registro JSON | Sin vínculo directo |
| S0170 | CompareDialog.__init__ | addItem | [covex_label_manager/qt_ui/compare.py:22](../../covex_label_manager/qt_ui/compare.py#L22) | Señales/registro JSON | Sin vínculo directo |
| S0171 | CompareDialog.__init__ | addItem | [covex_label_manager/qt_ui/compare.py:22](../../covex_label_manager/qt_ui/compare.py#L22) | Señales/registro JSON | Sin vínculo directo |
| S0172 | CompareDialog.__init__ | label | [covex_label_manager/qt_ui/compare.py:25](../../covex_label_manager/qt_ui/compare.py#L25) | Señales/registro JSON | Sin vínculo directo |
| S0173 | CompareDialog.__init__ | label | [covex_label_manager/qt_ui/compare.py:26](../../covex_label_manager/qt_ui/compare.py#L26) | Señales/registro JSON | Sin vínculo directo |
| S0174 | CompareDialog.__init__ | QTabWidget | [covex_label_manager/qt_ui/compare.py:28](../../covex_label_manager/qt_ui/compare.py#L28) | Señales/registro JSON | Sin vínculo directo |
| S0175 | CompareDialog.__init__ | Preview | [covex_label_manager/qt_ui/compare.py:29](../../covex_label_manager/qt_ui/compare.py#L29) | Señales/registro JSON | Sin vínculo directo |
| S0176 | CompareDialog.__init__ | Preview | [covex_label_manager/qt_ui/compare.py:29](../../covex_label_manager/qt_ui/compare.py#L29) | Señales/registro JSON | Sin vínculo directo |
| S0177 | CompareDialog.__init__ | addTab | [covex_label_manager/qt_ui/compare.py:31](../../covex_label_manager/qt_ui/compare.py#L31) | Señales/registro JSON | Sin vínculo directo |
| S0178 | CompareDialog.__init__ | Preview | [covex_label_manager/qt_ui/compare.py:32](../../covex_label_manager/qt_ui/compare.py#L32) | Señales/registro JSON | Sin vínculo directo |
| S0179 | CompareDialog.__init__ | label | [covex_label_manager/qt_ui/compare.py:33](../../covex_label_manager/qt_ui/compare.py#L33) | Señales/registro JSON | Sin vínculo directo |
| S0180 | CompareDialog.__init__ | QSlider | [covex_label_manager/qt_ui/compare.py:34](../../covex_label_manager/qt_ui/compare.py#L34) | Señales/registro JSON | Sin vínculo directo |
| S0181 | CompareDialog.__init__ | addTab | [covex_label_manager/qt_ui/compare.py:36](../../covex_label_manager/qt_ui/compare.py#L36) | Señales/registro JSON | Sin vínculo directo |
| S0182 | CompareDialog.__init__ | label | [covex_label_manager/qt_ui/compare.py:37](../../covex_label_manager/qt_ui/compare.py#L37) | Señales/registro JSON | Sin vínculo directo |
| S0183 | CompareDialog.__init__ | button | [covex_label_manager/qt_ui/compare.py:38](../../covex_label_manager/qt_ui/compare.py#L38) | self.accept | Sin vínculo directo |
| S0184 | CompareDialog.__init__ | connect | [covex_label_manager/qt_ui/compare.py:39](../../covex_label_manager/qt_ui/compare.py#L39) | self.refresh_comparison | Sin vínculo directo |
| S0185 | CompareDialog.__init__ | connect | [covex_label_manager/qt_ui/compare.py:40](../../covex_label_manager/qt_ui/compare.py#L40) | self.refresh_comparison | Sin vínculo directo |
| S0186 | CompareDialog.__init__ | connect | [covex_label_manager/qt_ui/compare.py:41](../../covex_label_manager/qt_ui/compare.py#L41) | self.refresh_overlay | Sin vínculo directo |
| S0187 | CompareMixin.compare_revisions | information | [covex_label_manager/qt_ui/compare.py:96](../../covex_label_manager/qt_ui/compare.py#L96) | Señales/registro JSON | Sin vínculo directo |
| S0188 | ControlledImportDialog.__init__ | label | [covex_label_manager/qt_ui/controlled_import.py:12](../../covex_label_manager/qt_ui/controlled_import.py#L12) | Señales/registro JSON | Sin vínculo directo |
| S0189 | ControlledImportDialog.__init__ | QTableWidget | [covex_label_manager/qt_ui/controlled_import.py:13](../../covex_label_manager/qt_ui/controlled_import.py#L13) | Señales/registro JSON | 5 |
| S0190 | ControlledImportDialog.__init__ | QComboBox | [covex_label_manager/qt_ui/controlled_import.py:20](../../covex_label_manager/qt_ui/controlled_import.py#L20) | Señales/registro JSON | Sin vínculo directo |
| S0191 | ControlledImportDialog.__init__ | addItem | [covex_label_manager/qt_ui/controlled_import.py:20](../../covex_label_manager/qt_ui/controlled_import.py#L20) | Señales/registro JSON | Sin vínculo directo |
| S0192 | ControlledImportDialog.__init__ | addItem | [covex_label_manager/qt_ui/controlled_import.py:22](../../covex_label_manager/qt_ui/controlled_import.py#L22) | Señales/registro JSON | Sin vínculo directo |
| S0193 | ControlledImportDialog.__init__ | addItem | [covex_label_manager/qt_ui/controlled_import.py:22](../../covex_label_manager/qt_ui/controlled_import.py#L22) | Señales/registro JSON | Sin vínculo directo |
| S0194 | ControlledImportDialog.__init__ | QComboBox | [covex_label_manager/qt_ui/controlled_import.py:24](../../covex_label_manager/qt_ui/controlled_import.py#L24) | Señales/registro JSON | Sin vínculo directo |
| S0195 | ControlledImportDialog.__init__ | addItem | [covex_label_manager/qt_ui/controlled_import.py:24](../../covex_label_manager/qt_ui/controlled_import.py#L24) | Señales/registro JSON | Sin vínculo directo |
| S0196 | ControlledImportDialog.__init__ | addItem | [covex_label_manager/qt_ui/controlled_import.py:25](../../covex_label_manager/qt_ui/controlled_import.py#L25) | Señales/registro JSON | Sin vínculo directo |
| S0197 | ControlledImportDialog.__init__ | button | [covex_label_manager/qt_ui/controlled_import.py:28](../../covex_label_manager/qt_ui/controlled_import.py#L28) | self.edit_identity | Sin vínculo directo |
| S0198 | ControlledImportDialog.__init__ | QProgressBar | [covex_label_manager/qt_ui/controlled_import.py:29](../../covex_label_manager/qt_ui/controlled_import.py#L29) | Señales/registro JSON | Sin vínculo directo |
| S0199 | ControlledImportDialog.__init__ | label | [covex_label_manager/qt_ui/controlled_import.py:30](../../covex_label_manager/qt_ui/controlled_import.py#L30) | Señales/registro JSON | Sin vínculo directo |
| S0200 | ControlledImportDialog.__init__ | button | [covex_label_manager/qt_ui/controlled_import.py:31](../../covex_label_manager/qt_ui/controlled_import.py#L31) | self.start | 2 |
| S0201 | ControlledImportDialog.__init__ | button | [covex_label_manager/qt_ui/controlled_import.py:32](../../covex_label_manager/qt_ui/controlled_import.py#L32) | self.stop | 5 |
| S0202 | ControlledImportDialog.__init__ | button | [covex_label_manager/qt_ui/controlled_import.py:33](../../covex_label_manager/qt_ui/controlled_import.py#L33) | self.close_requested | Sin vínculo directo |
| S0203 | ControlledImportDialog.__init__ | connect | [covex_label_manager/qt_ui/controlled_import.py:34](../../covex_label_manager/qt_ui/controlled_import.py#L34) | self.step | 2 |
| S0204 | ControlledImportDialog.edit_identity | QDialog | [covex_label_manager/qt_ui/controlled_import.py:38](../../covex_label_manager/qt_ui/controlled_import.py#L38) | Señales/registro JSON | Sin vínculo directo |
| S0205 | ControlledImportDialog.edit_identity | QLineEdit | [covex_label_manager/qt_ui/controlled_import.py:40](../../covex_label_manager/qt_ui/controlled_import.py#L40) | Señales/registro JSON | Sin vínculo directo |
| S0206 | ControlledImportDialog.edit_identity | addRow | [covex_label_manager/qt_ui/controlled_import.py:40](../../covex_label_manager/qt_ui/controlled_import.py#L40) | Señales/registro JSON | Sin vínculo directo |
| S0207 | ControlledImportDialog.edit_identity | QDialogButtonBox | [covex_label_manager/qt_ui/controlled_import.py:41](../../covex_label_manager/qt_ui/controlled_import.py#L41) | Señales/registro JSON | 23 |
| S0208 | ControlledImportDialog.edit_identity | connect | [covex_label_manager/qt_ui/controlled_import.py:41](../../covex_label_manager/qt_ui/controlled_import.py#L41) | dlg.accept | Sin vínculo directo |
| S0209 | ControlledImportDialog.edit_identity | connect | [covex_label_manager/qt_ui/controlled_import.py:41](../../covex_label_manager/qt_ui/controlled_import.py#L41) | dlg.reject | 2 |
| S0210 | ControlledImportDialog.start | warning | [covex_label_manager/qt_ui/controlled_import.py:54](../../covex_label_manager/qt_ui/controlled_import.py#L54) | Señales/registro JSON | Sin vínculo directo |
| S0211 | ControlledImportDialog.start | question | [covex_label_manager/qt_ui/controlled_import.py:56](../../covex_label_manager/qt_ui/controlled_import.py#L56) | Señales/registro JSON | 23 |
| S0212 | EmissionCentreMixin.build_emission_page | label | [covex_label_manager/qt_ui/emission_centre.py:27](../../covex_label_manager/qt_ui/emission_centre.py#L27) | Señales/registro JSON | Sin vínculo directo |
| S0213 | EmissionCentreMixin.build_emission_page | label | [covex_label_manager/qt_ui/emission_centre.py:28](../../covex_label_manager/qt_ui/emission_centre.py#L28) | Señales/registro JSON | Sin vínculo directo |
| S0214 | EmissionCentreMixin.build_emission_page | QComboBox | [covex_label_manager/qt_ui/emission_centre.py:29](../../covex_label_manager/qt_ui/emission_centre.py#L29) | Señales/registro JSON | Sin vínculo directo |
| S0215 | EmissionCentreMixin.build_emission_page | addItems | [covex_label_manager/qt_ui/emission_centre.py:29](../../covex_label_manager/qt_ui/emission_centre.py#L29) | Señales/registro JSON | Sin vínculo directo |
| S0216 | EmissionCentreMixin.build_emission_page | connect | [covex_label_manager/qt_ui/emission_centre.py:29](../../covex_label_manager/qt_ui/emission_centre.py#L29) | self.adapt_emission_layout | Sin vínculo directo |
| S0217 | EmissionCentreMixin.build_emission_page | button | [covex_label_manager/qt_ui/emission_centre.py:30](../../covex_label_manager/qt_ui/emission_centre.py#L30) | lambda: self.navigate('library') | 10 |
| S0218 | EmissionCentreMixin.build_emission_page | label | [covex_label_manager/qt_ui/emission_centre.py:31](../../covex_label_manager/qt_ui/emission_centre.py#L31) | Señales/registro JSON | Sin vínculo directo |
| S0219 | EmissionCentreMixin.build_emission_page | QSplitter | [covex_label_manager/qt_ui/emission_centre.py:32](../../covex_label_manager/qt_ui/emission_centre.py#L32) | Señales/registro JSON | Sin vínculo directo |
| S0220 | EmissionCentreMixin.build_emission_page | button | [covex_label_manager/qt_ui/emission_centre.py:37](../../covex_label_manager/qt_ui/emission_centre.py#L37) | self.paste_work_containers | Sin vínculo directo |
| S0221 | EmissionCentreMixin.build_emission_page | button | [covex_label_manager/qt_ui/emission_centre.py:37](../../covex_label_manager/qt_ui/emission_centre.py#L37) | self.save_emission_profile | 1 |
| S0222 | EmissionCentreMixin.build_emission_page | button | [covex_label_manager/qt_ui/emission_centre.py:37](../../covex_label_manager/qt_ui/emission_centre.py#L37) | self.calibrate_emission | Sin vínculo directo |
| S0223 | EmissionCentreMixin.build_emission_page | QScrollArea | [covex_label_manager/qt_ui/emission_centre.py:38](../../covex_label_manager/qt_ui/emission_centre.py#L38) | Señales/registro JSON | Sin vínculo directo |
| S0224 | EmissionCentreMixin.build_emission_page | label | [covex_label_manager/qt_ui/emission_centre.py:39](../../covex_label_manager/qt_ui/emission_centre.py#L39) | Señales/registro JSON | Sin vínculo directo |
| S0225 | EmissionCentreMixin.build_emission_page | button | [covex_label_manager/qt_ui/emission_centre.py:40](../../covex_label_manager/qt_ui/emission_centre.py#L40) | self.preview_emission_work | 8 |
| S0226 | EmissionCentreMixin.build_emission_page | PdfPane | [covex_label_manager/qt_ui/emission_centre.py:41](../../covex_label_manager/qt_ui/emission_centre.py#L41) | Señales/registro JSON | 2 |
| S0227 | EmissionCentreMixin.build_emission_page | label | [covex_label_manager/qt_ui/emission_centre.py:43](../../covex_label_manager/qt_ui/emission_centre.py#L43) | Señales/registro JSON | Sin vínculo directo |
| S0228 | EmissionCentreMixin.build_emission_page | label | [covex_label_manager/qt_ui/emission_centre.py:44](../../covex_label_manager/qt_ui/emission_centre.py#L44) | Señales/registro JSON | Sin vínculo directo |
| S0229 | EmissionCentreMixin.build_emission_page | button | [covex_label_manager/qt_ui/emission_centre.py:45](../../covex_label_manager/qt_ui/emission_centre.py#L45) | self.flush_emission_work | 5 |
| S0230 | EmissionCentreMixin.build_emission_page | button | [covex_label_manager/qt_ui/emission_centre.py:46](../../covex_label_manager/qt_ui/emission_centre.py#L46) | self.proof_emission_work | 1 |
| S0231 | EmissionCentreMixin.build_emission_page | button | [covex_label_manager/qt_ui/emission_centre.py:47](../../covex_label_manager/qt_ui/emission_centre.py#L47) | self.work_options | Sin vínculo directo |
| S0232 | EmissionCentreMixin.build_emission_page | button | [covex_label_manager/qt_ui/emission_centre.py:48](../../covex_label_manager/qt_ui/emission_centre.py#L48) | self.issue_emission_work | 6 |
| S0233 | EmissionCentreMixin.build_emission_page | button | [covex_label_manager/qt_ui/emission_centre.py:49](../../covex_label_manager/qt_ui/emission_centre.py#L49) | self.print_emission_pdf | 3 |
| S0234 | EmissionCentreMixin.emission_error | warning | [covex_label_manager/qt_ui/emission_centre.py:136](../../covex_label_manager/qt_ui/emission_centre.py#L136) | Señales/registro JSON | Sin vínculo directo |
| S0235 | EmissionCentreMixin.proof_emission_work | getSaveFileName | [covex_label_manager/qt_ui/emission_centre.py:156](../../covex_label_manager/qt_ui/emission_centre.py#L156) | Señales/registro JSON | Sin vínculo directo |
| S0236 | EmissionCentreMixin.issue_emission_work | question | [covex_label_manager/qt_ui/emission_centre.py:170](../../covex_label_manager/qt_ui/emission_centre.py#L170) | Señales/registro JSON | 23 |
| S0237 | EmissionCentreMixin.new_emission_work | QDialog | [covex_label_manager/qt_ui/emission_centre.py:190](../../covex_label_manager/qt_ui/emission_centre.py#L190) | Señales/registro JSON | Sin vínculo directo |
| S0238 | EmissionCentreMixin.new_emission_work | label | [covex_label_manager/qt_ui/emission_centre.py:191](../../covex_label_manager/qt_ui/emission_centre.py#L191) | Señales/registro JSON | Sin vínculo directo |
| S0239 | EmissionCentreMixin.new_emission_work | QComboBox | [covex_label_manager/qt_ui/emission_centre.py:192](../../covex_label_manager/qt_ui/emission_centre.py#L192) | Señales/registro JSON | Sin vínculo directo |
| S0240 | EmissionCentreMixin.new_emission_work | QComboBox | [covex_label_manager/qt_ui/emission_centre.py:192](../../covex_label_manager/qt_ui/emission_centre.py#L192) | Señales/registro JSON | Sin vínculo directo |
| S0241 | EmissionCentreMixin.new_emission_work | QLineEdit | [covex_label_manager/qt_ui/emission_centre.py:192](../../covex_label_manager/qt_ui/emission_centre.py#L192) | Señales/registro JSON | Sin vínculo directo |
| S0242 | EmissionCentreMixin.new_emission_work | addItem | [covex_label_manager/qt_ui/emission_centre.py:199](../../covex_label_manager/qt_ui/emission_centre.py#L199) | Señales/registro JSON | Sin vínculo directo |
| S0243 | EmissionCentreMixin.new_emission_work.variants | addItem | [covex_label_manager/qt_ui/emission_centre.py:201](../../covex_label_manager/qt_ui/emission_centre.py#L201) | Señales/registro JSON | Sin vínculo directo |
| S0244 | EmissionCentreMixin.new_emission_work.variants | addItem | [covex_label_manager/qt_ui/emission_centre.py:202](../../covex_label_manager/qt_ui/emission_centre.py#L202) | Señales/registro JSON | Sin vínculo directo |
| S0245 | EmissionCentreMixin.new_emission_work | connect | [covex_label_manager/qt_ui/emission_centre.py:203](../../covex_label_manager/qt_ui/emission_centre.py#L203) | variants | Sin vínculo directo |
| S0246 | EmissionCentreMixin.new_emission_work | addRow | [covex_label_manager/qt_ui/emission_centre.py:207](../../covex_label_manager/qt_ui/emission_centre.py#L207) | Señales/registro JSON | Sin vínculo directo |
| S0247 | EmissionCentreMixin.new_emission_work | addRow | [covex_label_manager/qt_ui/emission_centre.py:207](../../covex_label_manager/qt_ui/emission_centre.py#L207) | Señales/registro JSON | Sin vínculo directo |
| S0248 | EmissionCentreMixin.new_emission_work | addRow | [covex_label_manager/qt_ui/emission_centre.py:207](../../covex_label_manager/qt_ui/emission_centre.py#L207) | Señales/registro JSON | Sin vínculo directo |
| S0249 | EmissionCentreMixin.new_emission_work | label | [covex_label_manager/qt_ui/emission_centre.py:208](../../covex_label_manager/qt_ui/emission_centre.py#L208) | Señales/registro JSON | Sin vínculo directo |
| S0250 | EmissionCentreMixin.new_emission_work | QDialogButtonBox | [covex_label_manager/qt_ui/emission_centre.py:209](../../covex_label_manager/qt_ui/emission_centre.py#L209) | Señales/registro JSON | 23 |
| S0251 | EmissionCentreMixin.new_emission_work | button | [covex_label_manager/qt_ui/emission_centre.py:209](../../covex_label_manager/qt_ui/emission_centre.py#L209) | Señales/registro JSON | 23 |
| S0252 | EmissionCentreMixin.new_emission_work | button | [covex_label_manager/qt_ui/emission_centre.py:209](../../covex_label_manager/qt_ui/emission_centre.py#L209) | Señales/registro JSON | 23 |
| S0253 | EmissionCentreMixin.new_emission_work | connect | [covex_label_manager/qt_ui/emission_centre.py:215](../../covex_label_manager/qt_ui/emission_centre.py#L215) | create | Sin vínculo directo |
| S0254 | EmissionCentreMixin.new_emission_work | connect | [covex_label_manager/qt_ui/emission_centre.py:215](../../covex_label_manager/qt_ui/emission_centre.py#L215) | dialog.reject | 2 |
| S0255 | EmissionCentreMixin.work_options | addAction | [covex_label_manager/qt_ui/emission_centre.py:217](../../covex_label_manager/qt_ui/emission_centre.py#L217) | self.recover_emission_work | 1 |
| S0256 | EmissionCentreMixin.work_options | addAction | [covex_label_manager/qt_ui/emission_centre.py:217](../../covex_label_manager/qt_ui/emission_centre.py#L217) | self.refresh_work_binding | Sin vínculo directo |
| S0257 | EmissionCentreMixin.paste_work_containers | getMultiLineText | [covex_label_manager/qt_ui/emission_centre.py:221](../../covex_label_manager/qt_ui/emission_centre.py#L221) | Señales/registro JSON | 20 |
| S0258 | EmissionCentreMixin.save_emission_profile | getText | [covex_label_manager/qt_ui/emission_centre.py:231](../../covex_label_manager/qt_ui/emission_centre.py#L231) | Señales/registro JSON | Sin vínculo directo |
| S0259 | EmissionCentreMixin.save_emission_profile | question | [covex_label_manager/qt_ui/emission_centre.py:236](../../covex_label_manager/qt_ui/emission_centre.py#L236) | Señales/registro JSON | 23 |
| S0260 | EmissionCentreMixin.save_emission_profile | addItem | [covex_label_manager/qt_ui/emission_centre.py:239](../../covex_label_manager/qt_ui/emission_centre.py#L239) | Señales/registro JSON | Sin vínculo directo |
| S0261 | EmissionCentreMixin.save_emission_profile | addItem | [covex_label_manager/qt_ui/emission_centre.py:240](../../covex_label_manager/qt_ui/emission_centre.py#L240) | Señales/registro JSON | Sin vínculo directo |
| S0262 | FolderImportDialog.__init__ | label | [covex_label_manager/qt_ui/folder_import.py:20](../../covex_label_manager/qt_ui/folder_import.py#L20) | Señales/registro JSON | Sin vínculo directo |
| S0263 | FolderImportDialog.__init__ | label | [covex_label_manager/qt_ui/folder_import.py:21](../../covex_label_manager/qt_ui/folder_import.py#L21) | Señales/registro JSON | Sin vínculo directo |
| S0264 | FolderImportDialog.__init__ | QTableWidget | [covex_label_manager/qt_ui/folder_import.py:25](../../covex_label_manager/qt_ui/folder_import.py#L25) | Señales/registro JSON | Sin vínculo directo |
| S0265 | FolderImportDialog.__init__ | QProgressBar | [covex_label_manager/qt_ui/folder_import.py:40](../../covex_label_manager/qt_ui/folder_import.py#L40) | Señales/registro JSON | Sin vínculo directo |
| S0266 | FolderImportDialog.__init__ | label | [covex_label_manager/qt_ui/folder_import.py:41](../../covex_label_manager/qt_ui/folder_import.py#L41) | Señales/registro JSON | Sin vínculo directo |
| S0267 | FolderImportDialog.__init__ | button | [covex_label_manager/qt_ui/folder_import.py:42](../../covex_label_manager/qt_ui/folder_import.py#L42) | self.start | 2 |
| S0268 | FolderImportDialog.__init__ | button | [covex_label_manager/qt_ui/folder_import.py:43](../../covex_label_manager/qt_ui/folder_import.py#L43) | self.stop | 5 |
| S0269 | FolderImportDialog.__init__ | button | [covex_label_manager/qt_ui/folder_import.py:45](../../covex_label_manager/qt_ui/folder_import.py#L45) | self.close_requested | Sin vínculo directo |
| S0270 | FolderImportDialog.__init__ | connect | [covex_label_manager/qt_ui/folder_import.py:46](../../covex_label_manager/qt_ui/folder_import.py#L46) | self.step | 2 |
| S0271 | FolderImportDialog.start | question | [covex_label_manager/qt_ui/folder_import.py:50](../../covex_label_manager/qt_ui/folder_import.py#L50) | Señales/registro JSON | 23 |
| S0272 | FolderImportMixin.import_folder_native | getExistingDirectory | [covex_label_manager/qt_ui/folder_import.py:101](../../covex_label_manager/qt_ui/folder_import.py#L101) | Señales/registro JSON | Sin vínculo directo |
| S0273 | FolderImportMixin.import_folder_native | information | [covex_label_manager/qt_ui/folder_import.py:106](../../covex_label_manager/qt_ui/folder_import.py#L106) | Señales/registro JSON | Sin vínculo directo |
| S0274 | FolderImportMixin.import_folder_native | warning | [covex_label_manager/qt_ui/folder_import.py:116](../../covex_label_manager/qt_ui/folder_import.py#L116) | Señales/registro JSON | Sin vínculo directo |
| S0275 | BaseFunctionalWindow.__init__ | QShortcut | [covex_label_manager/qt_ui/functional.py:25](../../covex_label_manager/qt_ui/functional.py#L25) | Señales/registro JSON | 3 |
| S0276 | BaseFunctionalWindow.__init__ | connect | [covex_label_manager/qt_ui/functional.py:26](../../covex_label_manager/qt_ui/functional.py#L26) | self.open_editor | 32 |
| S0277 | BaseFunctionalWindow.__init__ | connect | [covex_label_manager/qt_ui/functional.py:27](../../covex_label_manager/qt_ui/functional.py#L27) | self.poll_legacy | Sin vínculo directo |
| S0278 | BaseFunctionalWindow.__init__ | connect | [covex_label_manager/qt_ui/functional.py:28](../../covex_label_manager/qt_ui/functional.py#L28) | self.recheck_actions | 3 |
| S0279 | BaseFunctionalWindow.build_library | connect | [covex_label_manager/qt_ui/functional.py:38](../../covex_label_manager/qt_ui/functional.py#L38) | replacements[widget.text()] | 20 |
| S0280 | BaseFunctionalWindow.build_library | label | [covex_label_manager/qt_ui/functional.py:39](../../covex_label_manager/qt_ui/functional.py#L39) | Señales/registro JSON | Sin vínculo directo |
| S0281 | BaseFunctionalWindow.build_library | QCheckBox | [covex_label_manager/qt_ui/functional.py:40](../../covex_label_manager/qt_ui/functional.py#L40) | Señales/registro JSON | Sin vínculo directo |
| S0282 | BaseFunctionalWindow.build_library | connect | [covex_label_manager/qt_ui/functional.py:42](../../covex_label_manager/qt_ui/functional.py#L42) | self.remember_filter_choice | Sin vínculo directo |
| S0283 | BaseFunctionalWindow.build_library | button | [covex_label_manager/qt_ui/functional.py:44](../../covex_label_manager/qt_ui/functional.py#L44) | lambda: self.open_legacy('emitir') | Sin vínculo directo |
| S0284 | BaseFunctionalWindow.build_library | button | [covex_label_manager/qt_ui/functional.py:45](../../covex_label_manager/qt_ui/functional.py#L45) | lambda: self.open_legacy('emitir', mode='test') | Sin vínculo directo |
| S0285 | BaseFunctionalWindow.build_library | button | [covex_label_manager/qt_ui/functional.py:50](../../covex_label_manager/qt_ui/functional.py#L50) | self.approve_revision | 2 |
| S0286 | BaseFunctionalWindow.refresh_facets | addItem | [covex_label_manager/qt_ui/functional.py:73](../../covex_label_manager/qt_ui/functional.py#L73) | Señales/registro JSON | Sin vínculo directo |
| S0287 | BaseFunctionalWindow.refresh_facets | addItem | [covex_label_manager/qt_ui/functional.py:74](../../covex_label_manager/qt_ui/functional.py#L74) | Señales/registro JSON | Sin vínculo directo |
| S0288 | BaseFunctionalWindow.open_legacy | information | [covex_label_manager/qt_ui/functional.py:106](../../covex_label_manager/qt_ui/functional.py#L106) | Señales/registro JSON | Sin vínculo directo |
| S0289 | BaseFunctionalWindow.open_legacy | warning | [covex_label_manager/qt_ui/functional.py:113](../../covex_label_manager/qt_ui/functional.py#L113) | Señales/registro JSON | Sin vínculo directo |
| S0290 | BaseFunctionalWindow.build_catalog | button | [covex_label_manager/qt_ui/functional.py:128](../../covex_label_manager/qt_ui/functional.py#L128) | self.open_catalog_legacy | Sin vínculo directo |
| S0291 | BaseFunctionalWindow.actions_menu | addAction | [covex_label_manager/qt_ui/functional.py:142](../../covex_label_manager/qt_ui/functional.py#L142) | action | Sin vínculo directo |
| S0292 | BaseFunctionalWindow.actions_menu | addAction | [covex_label_manager/qt_ui/functional.py:144](../../covex_label_manager/qt_ui/functional.py#L144) | self.review_catalog_folder | Sin vínculo directo |
| S0293 | BaseFunctionalWindow.actions_menu | addAction | [covex_label_manager/qt_ui/functional.py:145](../../covex_label_manager/qt_ui/functional.py#L145) | self.import_folder_native | Sin vínculo directo |
| S0294 | BaseFunctionalWindow.actions_menu | addAction | [covex_label_manager/qt_ui/functional.py:146](../../covex_label_manager/qt_ui/functional.py#L146) | self.export_entire_library | Sin vínculo directo |
| S0295 | BaseFunctionalWindow.actions_menu | addAction | [covex_label_manager/qt_ui/functional.py:147](../../covex_label_manager/qt_ui/functional.py#L147) | self.reconcile_master | Sin vínculo directo |
| S0296 | BaseFunctionalWindow.actions_menu | addAction | [covex_label_manager/qt_ui/functional.py:148](../../covex_label_manager/qt_ui/functional.py#L148) | self.compare_revisions | Sin vínculo directo |
| S0297 | BaseFunctionalWindow.open_document | warning | [covex_label_manager/qt_ui/functional.py:155](../../covex_label_manager/qt_ui/functional.py#L155) | Señales/registro JSON | Sin vínculo directo |
| S0298 | BaseFunctionalWindow.ask_form | QDialog | [covex_label_manager/qt_ui/functional.py:157](../../covex_label_manager/qt_ui/functional.py#L157) | Señales/registro JSON | Sin vínculo directo |
| S0299 | BaseFunctionalWindow.ask_form | label | [covex_label_manager/qt_ui/functional.py:158](../../covex_label_manager/qt_ui/functional.py#L158) | Señales/registro JSON | Sin vínculo directo |
| S0300 | BaseFunctionalWindow.ask_form | QLineEdit | [covex_label_manager/qt_ui/functional.py:160](../../covex_label_manager/qt_ui/functional.py#L160) | Señales/registro JSON | Sin vínculo directo |
| S0301 | BaseFunctionalWindow.ask_form | addRow | [covex_label_manager/qt_ui/functional.py:160](../../covex_label_manager/qt_ui/functional.py#L160) | Señales/registro JSON | Sin vínculo directo |
| S0302 | BaseFunctionalWindow.ask_form | QDialogButtonBox | [covex_label_manager/qt_ui/functional.py:162](../../covex_label_manager/qt_ui/functional.py#L162) | Señales/registro JSON | 23 |
| S0303 | BaseFunctionalWindow.ask_form | connect | [covex_label_manager/qt_ui/functional.py:163](../../covex_label_manager/qt_ui/functional.py#L163) | dialog.accept | Sin vínculo directo |
| S0304 | BaseFunctionalWindow.ask_form | connect | [covex_label_manager/qt_ui/functional.py:163](../../covex_label_manager/qt_ui/functional.py#L163) | dialog.reject | 2 |
| S0305 | BaseFunctionalWindow.mutate | action | [covex_label_manager/qt_ui/functional.py:168](../../covex_label_manager/qt_ui/functional.py#L168) | Señales/registro JSON | Sin vínculo directo |
| S0306 | BaseFunctionalWindow.mutate | warning | [covex_label_manager/qt_ui/functional.py:169](../../covex_label_manager/qt_ui/functional.py#L169) | Señales/registro JSON | Sin vínculo directo |
| S0307 | BaseFunctionalWindow.approve_revision | information | [covex_label_manager/qt_ui/functional.py:187](../../covex_label_manager/qt_ui/functional.py#L187) | Señales/registro JSON | Sin vínculo directo |
| S0308 | BaseFunctionalWindow.import_document | getOpenFileName | [covex_label_manager/qt_ui/functional.py:196](../../covex_label_manager/qt_ui/functional.py#L196) | Señales/registro JSON | Sin vínculo directo |
| S0309 | BaseFunctionalWindow.build_editor | button | [covex_label_manager/qt_ui/functional.py:210](../../covex_label_manager/qt_ui/functional.py#L210) | self.save_work | 10 |
| S0310 | BaseFunctionalWindow.build_editor | label | [covex_label_manager/qt_ui/functional.py:212](../../covex_label_manager/qt_ui/functional.py#L212) | Señales/registro JSON | Sin vínculo directo |
| S0311 | BaseFunctionalWindow.build_editor | QLineEdit | [covex_label_manager/qt_ui/functional.py:213](../../covex_label_manager/qt_ui/functional.py#L213) | Señales/registro JSON | Sin vínculo directo |
| S0312 | BaseFunctionalWindow.build_editor | connect | [covex_label_manager/qt_ui/functional.py:214](../../covex_label_manager/qt_ui/functional.py#L214) | self.change_key | Sin vínculo directo |
| S0313 | BaseFunctionalWindow.build_editor | button | [covex_label_manager/qt_ui/functional.py:216](../../covex_label_manager/qt_ui/functional.py#L216) | self.add_field | 1 |
| S0314 | BaseFunctionalWindow.build_editor | button | [covex_label_manager/qt_ui/functional.py:216](../../covex_label_manager/qt_ui/functional.py#L216) | self.remove_field | 1 |
| S0315 | BaseFunctionalWindow.build_editor | connect | [covex_label_manager/qt_ui/functional.py:221](../../covex_label_manager/qt_ui/functional.py#L221) | lambda checked=False, t=target: self.open_legacy(t) | Sin vínculo directo |
| S0316 | BaseFunctionalWindow.open_editor | warning | [covex_label_manager/qt_ui/functional.py:239](../../covex_label_manager/qt_ui/functional.py#L239) | Señales/registro JSON | Sin vínculo directo |
| S0317 | BaseFunctionalWindow.save_work | warning | [covex_label_manager/qt_ui/functional.py:273](../../covex_label_manager/qt_ui/functional.py#L273) | Señales/registro JSON | Sin vínculo directo |
| S0318 | BaseFunctionalWindow.resolve_work | question | [covex_label_manager/qt_ui/functional.py:276](../../covex_label_manager/qt_ui/functional.py#L276) | Señales/registro JSON | 23 |
| S0319 | BaseFunctionalWindow.add_field | getText | [covex_label_manager/qt_ui/functional.py:283](../../covex_label_manager/qt_ui/functional.py#L283) | Señales/registro JSON | Sin vínculo directo |
| S0320 | BaseFunctionalWindow.add_field | warning | [covex_label_manager/qt_ui/functional.py:285](../../covex_label_manager/qt_ui/functional.py#L285) | Señales/registro JSON | Sin vínculo directo |
| S0321 | BaseFunctionalWindow.remove_field | question | [covex_label_manager/qt_ui/functional.py:291](../../covex_label_manager/qt_ui/functional.py#L291) | Señales/registro JSON | Sin vínculo directo |
| S0322 | BaseFunctionalWindow.closeEvent | information | [covex_label_manager/qt_ui/functional.py:295](../../covex_label_manager/qt_ui/functional.py#L295) | Señales/registro JSON | Sin vínculo directo |
| S0323 | HistoryMixin.build_native_history | label | [covex_label_manager/qt_ui/history.py:19](../../covex_label_manager/qt_ui/history.py#L19) | Señales/registro JSON | Sin vínculo directo |
| S0324 | HistoryMixin.build_native_history | QComboBox | [covex_label_manager/qt_ui/history.py:19](../../covex_label_manager/qt_ui/history.py#L19) | Señales/registro JSON | Sin vínculo directo |
| S0325 | HistoryMixin.build_native_history | addItems | [covex_label_manager/qt_ui/history.py:19](../../covex_label_manager/qt_ui/history.py#L19) | Señales/registro JSON | Sin vínculo directo |
| S0326 | HistoryMixin.build_native_history | connect | [covex_label_manager/qt_ui/history.py:19](../../covex_label_manager/qt_ui/history.py#L19) | self.adapt_history_layout | Sin vínculo directo |
| S0327 | HistoryMixin.build_native_history | button | [covex_label_manager/qt_ui/history.py:19](../../covex_label_manager/qt_ui/history.py#L19) | self.refresh_native_history | Sin vínculo directo |
| S0328 | HistoryMixin.build_native_history | label | [covex_label_manager/qt_ui/history.py:20](../../covex_label_manager/qt_ui/history.py#L20) | Señales/registro JSON | Sin vínculo directo |
| S0329 | HistoryMixin.build_native_history | QLineEdit | [covex_label_manager/qt_ui/history.py:21](../../covex_label_manager/qt_ui/history.py#L21) | Señales/registro JSON | Sin vínculo directo |
| S0330 | HistoryMixin.build_native_history | connect | [covex_label_manager/qt_ui/history.py:21](../../covex_label_manager/qt_ui/history.py#L21) | self.filter_native_history | Sin vínculo directo |
| S0331 | HistoryMixin.build_native_history | QSplitter | [covex_label_manager/qt_ui/history.py:22](../../covex_label_manager/qt_ui/history.py#L22) | Señales/registro JSON | Sin vínculo directo |
| S0332 | HistoryMixin.build_native_history | QTableWidget | [covex_label_manager/qt_ui/history.py:24](../../covex_label_manager/qt_ui/history.py#L24) | Señales/registro JSON | Sin vínculo directo |
| S0333 | HistoryMixin.build_native_history | connect | [covex_label_manager/qt_ui/history.py:28](../../covex_label_manager/qt_ui/history.py#L28) | self.select_native_issue | Sin vínculo directo |
| S0334 | HistoryMixin.build_native_history | QTabWidget | [covex_label_manager/qt_ui/history.py:29](../../covex_label_manager/qt_ui/history.py#L29) | Señales/registro JSON | Sin vínculo directo |
| S0335 | HistoryMixin.build_native_history | QPlainTextEdit | [covex_label_manager/qt_ui/history.py:31](../../covex_label_manager/qt_ui/history.py#L31) | Señales/registro JSON | Sin vínculo directo |
| S0336 | HistoryMixin.build_native_history | addTab | [covex_label_manager/qt_ui/history.py:31](../../covex_label_manager/qt_ui/history.py#L31) | Señales/registro JSON | Sin vínculo directo |
| S0337 | HistoryMixin.build_native_history | QScrollArea | [covex_label_manager/qt_ui/history.py:32](../../covex_label_manager/qt_ui/history.py#L32) | Señales/registro JSON | Sin vínculo directo |
| S0338 | HistoryMixin.build_native_history | PdfPane | [covex_label_manager/qt_ui/history.py:33](../../covex_label_manager/qt_ui/history.py#L33) | Señales/registro JSON | 2 |
| S0339 | HistoryMixin.build_native_history | label | [covex_label_manager/qt_ui/history.py:35](../../covex_label_manager/qt_ui/history.py#L35) | Señales/registro JSON | Sin vínculo directo |
| S0340 | HistoryMixin.build_native_history | button | [covex_label_manager/qt_ui/history.py:36](../../covex_label_manager/qt_ui/history.py#L36) | self.preview_native_issue | 1 |
| S0341 | HistoryMixin.build_native_history | button | [covex_label_manager/qt_ui/history.py:37](../../covex_label_manager/qt_ui/history.py#L37) | self.print_historical_pdf | 1 |
| S0342 | HistoryMixin.build_native_history | button | [covex_label_manager/qt_ui/history.py:38](../../covex_label_manager/qt_ui/history.py#L38) | self.native_reprint | 1 |
| S0343 | HistoryMixin.native_reprint | QDialog | [covex_label_manager/qt_ui/history.py:110](../../covex_label_manager/qt_ui/history.py#L110) | Señales/registro JSON | Sin vínculo directo |
| S0344 | HistoryMixin.native_reprint | label | [covex_label_manager/qt_ui/history.py:111](../../covex_label_manager/qt_ui/history.py#L111) | Señales/registro JSON | Sin vínculo directo |
| S0345 | HistoryMixin.native_reprint | QLineEdit | [covex_label_manager/qt_ui/history.py:112](../../covex_label_manager/qt_ui/history.py#L112) | Señales/registro JSON | 35 |
| S0346 | HistoryMixin.native_reprint | QLineEdit | [covex_label_manager/qt_ui/history.py:112](../../covex_label_manager/qt_ui/history.py#L112) | Señales/registro JSON | Sin vínculo directo |
| S0347 | HistoryMixin.native_reprint | QLineEdit | [covex_label_manager/qt_ui/history.py:112](../../covex_label_manager/qt_ui/history.py#L112) | Señales/registro JSON | Sin vínculo directo |
| S0348 | HistoryMixin.native_reprint | addRow | [covex_label_manager/qt_ui/history.py:113](../../covex_label_manager/qt_ui/history.py#L113) | Señales/registro JSON | Sin vínculo directo |
| S0349 | HistoryMixin.native_reprint | addRow | [covex_label_manager/qt_ui/history.py:113](../../covex_label_manager/qt_ui/history.py#L113) | Señales/registro JSON | Sin vínculo directo |
| S0350 | HistoryMixin.native_reprint | addRow | [covex_label_manager/qt_ui/history.py:113](../../covex_label_manager/qt_ui/history.py#L113) | Señales/registro JSON | Sin vínculo directo |
| S0351 | HistoryMixin.native_reprint | label | [covex_label_manager/qt_ui/history.py:114](../../covex_label_manager/qt_ui/history.py#L114) | Señales/registro JSON | 7 |
| S0352 | HistoryMixin.native_reprint | QCheckBox | [covex_label_manager/qt_ui/history.py:115](../../covex_label_manager/qt_ui/history.py#L115) | Señales/registro JSON | Sin vínculo directo |
| S0353 | HistoryMixin.native_reprint | label | [covex_label_manager/qt_ui/history.py:116](../../covex_label_manager/qt_ui/history.py#L116) | Señales/registro JSON | Sin vínculo directo |
| S0354 | HistoryMixin.native_reprint | label | [covex_label_manager/qt_ui/history.py:116](../../covex_label_manager/qt_ui/history.py#L116) | Señales/registro JSON | Sin vínculo directo |
| S0355 | HistoryMixin.native_reprint | button | [covex_label_manager/qt_ui/history.py:117](../../covex_label_manager/qt_ui/history.py#L117) | lambda: execute(True) | Sin vínculo directo |
| S0356 | HistoryMixin.native_reprint | button | [covex_label_manager/qt_ui/history.py:117](../../covex_label_manager/qt_ui/history.py#L117) | lambda: execute(False) | Sin vínculo directo |
| S0357 | HistoryMixin.native_reprint | QDialogButtonBox | [covex_label_manager/qt_ui/history.py:118](../../covex_label_manager/qt_ui/history.py#L118) | Señales/registro JSON | 23 |
| S0358 | HistoryMixin.native_reprint | button | [covex_label_manager/qt_ui/history.py:118](../../covex_label_manager/qt_ui/history.py#L118) | Señales/registro JSON | 23 |
| S0359 | HistoryMixin.native_reprint | connect | [covex_label_manager/qt_ui/history.py:118](../../covex_label_manager/qt_ui/history.py#L118) | dialog.reject | 2 |
| S0360 | HistoryMixin.native_reprint.execute | question | [covex_label_manager/qt_ui/history.py:126](../../covex_label_manager/qt_ui/history.py#L126) | Señales/registro JSON | 34 |
| S0361 | HistoryMixin.native_reprint.execute | QDialog | [covex_label_manager/qt_ui/history.py:131](../../covex_label_manager/qt_ui/history.py#L131) | Señales/registro JSON | Sin vínculo directo |
| S0362 | HistoryMixin.native_reprint.execute | PdfPane | [covex_label_manager/qt_ui/history.py:131](../../covex_label_manager/qt_ui/history.py#L131) | Señales/registro JSON | 2 |
| S0363 | HistoryMixin.native_reprint.execute | QDialogButtonBox | [covex_label_manager/qt_ui/history.py:131](../../covex_label_manager/qt_ui/history.py#L131) | Señales/registro JSON | 23 |
| S0364 | HistoryMixin.native_reprint.execute | button | [covex_label_manager/qt_ui/history.py:131](../../covex_label_manager/qt_ui/history.py#L131) | Señales/registro JSON | 23 |
| S0365 | HistoryMixin.native_reprint.execute | connect | [covex_label_manager/qt_ui/history.py:131](../../covex_label_manager/qt_ui/history.py#L131) | proof_dialog.reject | 2 |
| S0366 | HistoryMixin.native_reprint | connect | [covex_label_manager/qt_ui/history.py:136](../../covex_label_manager/qt_ui/history.py#L136) | validate | Sin vínculo directo |
| S0367 | HistoryMixin.native_reprint | connect | [covex_label_manager/qt_ui/history.py:137](../../covex_label_manager/qt_ui/history.py#L137) | validate | Sin vínculo directo |
| S0368 | MasterReconciliationDialog.__init__ | label | [covex_label_manager/qt_ui/master_reconcile_ui.py:28](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L28) | Señales/registro JSON | Sin vínculo directo |
| S0369 | MasterReconciliationDialog.__init__ | label | [covex_label_manager/qt_ui/master_reconcile_ui.py:30](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L30) | Señales/registro JSON | Sin vínculo directo |
| S0370 | MasterReconciliationDialog.__init__ | label | [covex_label_manager/qt_ui/master_reconcile_ui.py:34](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L34) | Señales/registro JSON | Sin vínculo directo |
| S0371 | MasterReconciliationDialog.__init__ | QComboBox | [covex_label_manager/qt_ui/master_reconcile_ui.py:35](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L35) | Señales/registro JSON | Sin vínculo directo |
| S0372 | MasterReconciliationDialog.__init__ | addItems | [covex_label_manager/qt_ui/master_reconcile_ui.py:35](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L35) | Señales/registro JSON | Sin vínculo directo |
| S0373 | MasterReconciliationDialog.__init__ | connect | [covex_label_manager/qt_ui/master_reconcile_ui.py:36](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L36) | self.refresh_columns | Sin vínculo directo |
| S0374 | MasterReconciliationDialog.__init__ | QComboBox | [covex_label_manager/qt_ui/master_reconcile_ui.py:43](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L43) | Señales/registro JSON | Sin vínculo directo |
| S0375 | MasterReconciliationDialog.__init__ | addRow | [covex_label_manager/qt_ui/master_reconcile_ui.py:43](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L43) | Señales/registro JSON | Sin vínculo directo |
| S0376 | MasterReconciliationDialog.__init__ | button | [covex_label_manager/qt_ui/master_reconcile_ui.py:46](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L46) | self.run_compare | 1 |
| S0377 | MasterReconciliationDialog.__init__ | QComboBox | [covex_label_manager/qt_ui/master_reconcile_ui.py:48](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L48) | Señales/registro JSON | Sin vínculo directo |
| S0378 | MasterReconciliationDialog.__init__ | addItem | [covex_label_manager/qt_ui/master_reconcile_ui.py:48](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L48) | Señales/registro JSON | Sin vínculo directo |
| S0379 | MasterReconciliationDialog.__init__ | connect | [covex_label_manager/qt_ui/master_reconcile_ui.py:49](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L49) | self.display_results | Sin vínculo directo |
| S0380 | MasterReconciliationDialog.__init__ | button | [covex_label_manager/qt_ui/master_reconcile_ui.py:51](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L51) | self.export_result | Sin vínculo directo |
| S0381 | MasterReconciliationDialog.__init__ | label | [covex_label_manager/qt_ui/master_reconcile_ui.py:54](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L54) | Señales/registro JSON | Sin vínculo directo |
| S0382 | MasterReconciliationDialog.__init__ | QTableWidget | [covex_label_manager/qt_ui/master_reconcile_ui.py:56](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L56) | Señales/registro JSON | Sin vínculo directo |
| S0383 | MasterReconciliationDialog.__init__ | QDialogButtonBox | [covex_label_manager/qt_ui/master_reconcile_ui.py:63](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L63) | Señales/registro JSON | 23 |
| S0384 | MasterReconciliationDialog.__init__ | connect | [covex_label_manager/qt_ui/master_reconcile_ui.py:64](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L64) | self.reject | 2 |
| S0385 | MasterReconciliationDialog.refresh_columns | addItem | [covex_label_manager/qt_ui/master_reconcile_ui.py:70](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L70) | Señales/registro JSON | Sin vínculo directo |
| S0386 | MasterReconciliationDialog.refresh_columns | addItem | [covex_label_manager/qt_ui/master_reconcile_ui.py:77](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L77) | Señales/registro JSON | Sin vínculo directo |
| S0387 | MasterReconciliationDialog.refresh_columns | addItem | [covex_label_manager/qt_ui/master_reconcile_ui.py:78](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L78) | Señales/registro JSON | Sin vínculo directo |
| S0388 | MasterReconciliationDialog.run_compare | warning | [covex_label_manager/qt_ui/master_reconcile_ui.py:90](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L90) | Señales/registro JSON | Sin vínculo directo |
| S0389 | MasterReconciliationDialog.run_compare | addItem | [covex_label_manager/qt_ui/master_reconcile_ui.py:93](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L93) | Señales/registro JSON | Sin vínculo directo |
| S0390 | MasterReconciliationDialog.run_compare | addItem | [covex_label_manager/qt_ui/master_reconcile_ui.py:95](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L95) | Señales/registro JSON | Sin vínculo directo |
| S0391 | MasterReconciliationDialog.run_compare | addItem | [covex_label_manager/qt_ui/master_reconcile_ui.py:97](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L97) | Señales/registro JSON | 4 |
| S0392 | MasterReconciliationDialog.export_result | getSaveFileName | [covex_label_manager/qt_ui/master_reconcile_ui.py:128](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L128) | Señales/registro JSON | Sin vínculo directo |
| S0393 | MasterReconciliationDialog.export_result | information | [covex_label_manager/qt_ui/master_reconcile_ui.py:134](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L134) | Señales/registro JSON | Sin vínculo directo |
| S0394 | MasterReconciliationDialog.export_result | warning | [covex_label_manager/qt_ui/master_reconcile_ui.py:137](../../covex_label_manager/qt_ui/master_reconcile_ui.py#L137) | Señales/registro JSON | Sin vínculo directo |
| S0395 | PdfPane.__init__ | label | [covex_label_manager/qt_ui/pdf_view.py:12](../../covex_label_manager/qt_ui/pdf_view.py#L12) | Señales/registro JSON | Sin vínculo directo |
| S0396 | PdfPane.__init__ | QComboBox | [covex_label_manager/qt_ui/pdf_view.py:14](../../covex_label_manager/qt_ui/pdf_view.py#L14) | Señales/registro JSON | Sin vínculo directo |
| S0397 | PdfPane.__init__ | connect | [covex_label_manager/qt_ui/pdf_view.py:14](../../covex_label_manager/qt_ui/pdf_view.py#L14) | self.page_changed | Sin vínculo directo |
| S0398 | PdfPane.__init__ | Preview | [covex_label_manager/qt_ui/pdf_view.py:16](../../covex_label_manager/qt_ui/pdf_view.py#L16) | Señales/registro JSON | Sin vínculo directo |
| S0399 | PdfPane.__init__ | label | [covex_label_manager/qt_ui/pdf_view.py:16](../../covex_label_manager/qt_ui/pdf_view.py#L16) | Señales/registro JSON | Sin vínculo directo |
| S0400 | PdfPane.__init__ | button | [covex_label_manager/qt_ui/pdf_view.py:17](../../covex_label_manager/qt_ui/pdf_view.py#L17) | self.view.fit | 2 |
| S0401 | PdfPane.__init__ | button | [covex_label_manager/qt_ui/pdf_view.py:17](../../covex_label_manager/qt_ui/pdf_view.py#L17) | lambda: self.view.zoom(1 / 1.2) | 2 |
| S0402 | PdfPane.__init__ | button | [covex_label_manager/qt_ui/pdf_view.py:17](../../covex_label_manager/qt_ui/pdf_view.py#L17) | lambda: self.view.zoom(1.2) | 2 |
| S0403 | PdfPane.__init__ | button | [covex_label_manager/qt_ui/pdf_view.py:17](../../covex_label_manager/qt_ui/pdf_view.py#L17) | self.expand_pdf | Sin vínculo directo |
| S0404 | PdfPane.__init__ | button | [covex_label_manager/qt_ui/pdf_view.py:22](../../covex_label_manager/qt_ui/pdf_view.py#L22) | self.open_pdf | Sin vínculo directo |
| S0405 | PdfPane.__init__ | label | [covex_label_manager/qt_ui/pdf_view.py:23](../../covex_label_manager/qt_ui/pdf_view.py#L23) | Señales/registro JSON | Sin vínculo directo |
| S0406 | PdfPane.load | addItem | [covex_label_manager/qt_ui/pdf_view.py:29](../../covex_label_manager/qt_ui/pdf_view.py#L29) | Señales/registro JSON | Sin vínculo directo |
| S0407 | PdfPane.expand_pdf | QDialog | [covex_label_manager/qt_ui/pdf_view.py:47](../../covex_label_manager/qt_ui/pdf_view.py#L47) | Señales/registro JSON | Sin vínculo directo |
| S0408 | PdfPane.expand_pdf | PdfPane | [covex_label_manager/qt_ui/pdf_view.py:47](../../covex_label_manager/qt_ui/pdf_view.py#L47) | Señales/registro JSON | 2 |
| S0409 | PdfPane.expand_pdf | QDialogButtonBox | [covex_label_manager/qt_ui/pdf_view.py:49](../../covex_label_manager/qt_ui/pdf_view.py#L49) | Señales/registro JSON | 23 |
| S0410 | PdfPane.expand_pdf | button | [covex_label_manager/qt_ui/pdf_view.py:49](../../covex_label_manager/qt_ui/pdf_view.py#L49) | Señales/registro JSON | 23 |
| S0411 | PdfPane.expand_pdf | connect | [covex_label_manager/qt_ui/pdf_view.py:49](../../covex_label_manager/qt_ui/pdf_view.py#L49) | dialog.reject | 2 |
| S0412 | print_registered_pdf | question | [covex_label_manager/qt_ui/print_control.py:66](../../covex_label_manager/qt_ui/print_control.py#L66) | Señales/registro JSON | 23 |
| S0413 | print_registered_pdf | QPrintDialog | [covex_label_manager/qt_ui/print_control.py:79](../../covex_label_manager/qt_ui/print_control.py#L79) | Señales/registro JSON | Sin vínculo directo |
| S0414 | PrintWorkflowMixin._send_registered_to_printer | warning | [covex_label_manager/qt_ui/print_control.py:125](../../covex_label_manager/qt_ui/print_control.py#L125) | Señales/registro JSON | Sin vínculo directo |
| S0415 | CalibrationDialog.__init__ | label | [covex_label_manager/qt_ui/printer_calibration_ui.py:19](../../covex_label_manager/qt_ui/printer_calibration_ui.py#L19) | Señales/registro JSON | Sin vínculo directo |
| S0416 | CalibrationDialog.__init__ | QLineEdit | [covex_label_manager/qt_ui/printer_calibration_ui.py:26](../../covex_label_manager/qt_ui/printer_calibration_ui.py#L26) | Señales/registro JSON | 32 |
| S0417 | CalibrationDialog.__init__ | addRow | [covex_label_manager/qt_ui/printer_calibration_ui.py:28](../../covex_label_manager/qt_ui/printer_calibration_ui.py#L28) | Señales/registro JSON | 2 |
| S0418 | CalibrationDialog.__init__ | QLineEdit | [covex_label_manager/qt_ui/printer_calibration_ui.py:41](../../covex_label_manager/qt_ui/printer_calibration_ui.py#L41) | Señales/registro JSON | Sin vínculo directo |
| S0419 | CalibrationDialog.__init__ | addRow | [covex_label_manager/qt_ui/printer_calibration_ui.py:41](../../covex_label_manager/qt_ui/printer_calibration_ui.py#L41) | Señales/registro JSON | Sin vínculo directo |
| S0420 | CalibrationDialog.__init__ | label | [covex_label_manager/qt_ui/printer_calibration_ui.py:42](../../covex_label_manager/qt_ui/printer_calibration_ui.py#L42) | Señales/registro JSON | Sin vínculo directo |
| S0421 | CalibrationDialog.__init__ | button | [covex_label_manager/qt_ui/printer_calibration_ui.py:44](../../covex_label_manager/qt_ui/printer_calibration_ui.py#L44) | self.proof | 5 |
| S0422 | CalibrationDialog.__init__ | QDialogButtonBox | [covex_label_manager/qt_ui/printer_calibration_ui.py:46](../../covex_label_manager/qt_ui/printer_calibration_ui.py#L46) | Señales/registro JSON | 23 |
| S0423 | CalibrationDialog.__init__ | button | [covex_label_manager/qt_ui/printer_calibration_ui.py:47](../../covex_label_manager/qt_ui/printer_calibration_ui.py#L47) | Señales/registro JSON | 23 |
| S0424 | CalibrationDialog.__init__ | connect | [covex_label_manager/qt_ui/printer_calibration_ui.py:48](../../covex_label_manager/qt_ui/printer_calibration_ui.py#L48) | self.accept_calibration | 2 |
| S0425 | CalibrationDialog.__init__ | connect | [covex_label_manager/qt_ui/printer_calibration_ui.py:48](../../covex_label_manager/qt_ui/printer_calibration_ui.py#L48) | self.reject | 2 |
| S0426 | CalibrationDialog.proof | QDialog | [covex_label_manager/qt_ui/printer_calibration_ui.py:55](../../covex_label_manager/qt_ui/printer_calibration_ui.py#L55) | Señales/registro JSON | Sin vínculo directo |
| S0427 | CalibrationDialog.proof | PdfPane | [covex_label_manager/qt_ui/printer_calibration_ui.py:57](../../covex_label_manager/qt_ui/printer_calibration_ui.py#L57) | Señales/registro JSON | 2 |
| S0428 | CalibrationDialog.proof | QDialogButtonBox | [covex_label_manager/qt_ui/printer_calibration_ui.py:59](../../covex_label_manager/qt_ui/printer_calibration_ui.py#L59) | Señales/registro JSON | 23 |
| S0429 | CalibrationDialog.proof | connect | [covex_label_manager/qt_ui/printer_calibration_ui.py:60](../../covex_label_manager/qt_ui/printer_calibration_ui.py#L60) | dlg.reject | 2 |
| S0430 | RevisionApprovalDialog.__init__ | label | [covex_label_manager/qt_ui/revision_approval.py:12](../../covex_label_manager/qt_ui/revision_approval.py#L12) | Señales/registro JSON | Sin vínculo directo |
| S0431 | RevisionApprovalDialog.__init__ | label | [covex_label_manager/qt_ui/revision_approval.py:13](../../covex_label_manager/qt_ui/revision_approval.py#L13) | Señales/registro JSON | Sin vínculo directo |
| S0432 | RevisionApprovalDialog.__init__ | label | [covex_label_manager/qt_ui/revision_approval.py:16](../../covex_label_manager/qt_ui/revision_approval.py#L16) | Señales/registro JSON | Sin vínculo directo |
| S0433 | RevisionApprovalDialog.__init__ | label | [covex_label_manager/qt_ui/revision_approval.py:24](../../covex_label_manager/qt_ui/revision_approval.py#L24) | Señales/registro JSON | Sin vínculo directo |
| S0434 | RevisionApprovalDialog.__init__ | QLineEdit | [covex_label_manager/qt_ui/revision_approval.py:27](../../covex_label_manager/qt_ui/revision_approval.py#L27) | Señales/registro JSON | Sin vínculo directo |
| S0435 | RevisionApprovalDialog.__init__ | QLineEdit | [covex_label_manager/qt_ui/revision_approval.py:28](../../covex_label_manager/qt_ui/revision_approval.py#L28) | Señales/registro JSON | Sin vínculo directo |
| S0436 | RevisionApprovalDialog.__init__ | addRow | [covex_label_manager/qt_ui/revision_approval.py:29](../../covex_label_manager/qt_ui/revision_approval.py#L29) | Señales/registro JSON | 2 |
| S0437 | RevisionApprovalDialog.__init__ | addRow | [covex_label_manager/qt_ui/revision_approval.py:29](../../covex_label_manager/qt_ui/revision_approval.py#L29) | Señales/registro JSON | 2 |
| S0438 | RevisionApprovalDialog.__init__ | QCheckBox | [covex_label_manager/qt_ui/revision_approval.py:31](../../covex_label_manager/qt_ui/revision_approval.py#L31) | Señales/registro JSON | Sin vínculo directo |
| S0439 | RevisionApprovalDialog.__init__ | QDialogButtonBox | [covex_label_manager/qt_ui/revision_approval.py:34](../../covex_label_manager/qt_ui/revision_approval.py#L34) | Señales/registro JSON | 23 |
| S0440 | RevisionApprovalDialog.__init__ | QPushButton | [covex_label_manager/qt_ui/revision_approval.py:35](../../covex_label_manager/qt_ui/revision_approval.py#L35) | Señales/registro JSON | Sin vínculo directo |
| S0441 | RevisionApprovalDialog.__init__ | connect | [covex_label_manager/qt_ui/revision_approval.py:36](../../covex_label_manager/qt_ui/revision_approval.py#L36) | self.commit | 11 |
| S0442 | RevisionApprovalDialog.__init__ | connect | [covex_label_manager/qt_ui/revision_approval.py:36](../../covex_label_manager/qt_ui/revision_approval.py#L36) | self.reject | 2 |
| S0443 | RevisionApprovalDialog.__init__ | connect | [covex_label_manager/qt_ui/revision_approval.py:38](../../covex_label_manager/qt_ui/revision_approval.py#L38) | self.update_state | Sin vínculo directo |
| S0444 | RevisionApprovalDialog.__init__ | connect | [covex_label_manager/qt_ui/revision_approval.py:38](../../covex_label_manager/qt_ui/revision_approval.py#L38) | self.update_state | Sin vínculo directo |
| S0445 | RevisionApprovalDialog.__init__ | connect | [covex_label_manager/qt_ui/revision_approval.py:39](../../covex_label_manager/qt_ui/revision_approval.py#L39) | self.update_state | Sin vínculo directo |
| S0446 | RevisionApprovalDialog.commit | warning | [covex_label_manager/qt_ui/revision_approval.py:49](../../covex_label_manager/qt_ui/revision_approval.py#L49) | Señales/registro JSON | Sin vínculo directo |
| S0447 | RevisionApprovalDialog.commit | warning | [covex_label_manager/qt_ui/revision_approval.py:52](../../covex_label_manager/qt_ui/revision_approval.py#L52) | Señales/registro JSON | Sin vínculo directo |
| S0448 | RevisionApprovalDialog.commit | question | [covex_label_manager/qt_ui/revision_approval.py:61](../../covex_label_manager/qt_ui/revision_approval.py#L61) | Señales/registro JSON | 23 |
| S0449 | RevisionApprovalDialog.commit | warning | [covex_label_manager/qt_ui/revision_approval.py:68](../../covex_label_manager/qt_ui/revision_approval.py#L68) | Señales/registro JSON | Sin vínculo directo |
| S0450 | _scroll_tab | QScrollArea | [covex_label_manager/qt_ui/settings.py:20](../../covex_label_manager/qt_ui/settings.py#L20) | Señales/registro JSON | Sin vínculo directo |
| S0451 | _scroll_tab | addTab | [covex_label_manager/qt_ui/settings.py:24](../../covex_label_manager/qt_ui/settings.py#L24) | Señales/registro JSON | Sin vínculo directo |
| S0452 | _section | label | [covex_label_manager/qt_ui/settings.py:31](../../covex_label_manager/qt_ui/settings.py#L31) | Señales/registro JSON | Sin vínculo directo |
| S0453 | _section | label | [covex_label_manager/qt_ui/settings.py:33](../../covex_label_manager/qt_ui/settings.py#L33) | Señales/registro JSON | Sin vínculo directo |
| S0454 | _read_only_table | QTableWidget | [covex_label_manager/qt_ui/settings.py:41](../../covex_label_manager/qt_ui/settings.py#L41) | Señales/registro JSON | Sin vínculo directo |
| S0455 | SettingsMixin.build_native_settings | label | [covex_label_manager/qt_ui/settings.py:69](../../covex_label_manager/qt_ui/settings.py#L69) | Señales/registro JSON | Sin vínculo directo |
| S0456 | SettingsMixin.build_native_settings | label | [covex_label_manager/qt_ui/settings.py:70](../../covex_label_manager/qt_ui/settings.py#L70) | Señales/registro JSON | Sin vínculo directo |
| S0457 | SettingsMixin.build_native_settings | QTabWidget | [covex_label_manager/qt_ui/settings.py:77](../../covex_label_manager/qt_ui/settings.py#L77) | Señales/registro JSON | Sin vínculo directo |
| S0458 | SettingsMixin.build_native_settings | label | [covex_label_manager/qt_ui/settings.py:96](../../covex_label_manager/qt_ui/settings.py#L96) | Señales/registro JSON | Sin vínculo directo |
| S0459 | SettingsMixin.build_native_settings | label | [covex_label_manager/qt_ui/settings.py:97](../../covex_label_manager/qt_ui/settings.py#L97) | Señales/registro JSON | Sin vínculo directo |
| S0460 | SettingsMixin.build_native_settings | button | [covex_label_manager/qt_ui/settings.py:103](../../covex_label_manager/qt_ui/settings.py#L103) | self.refresh_native_settings | 1 |
| S0461 | SettingsMixin.build_native_settings | label | [covex_label_manager/qt_ui/settings.py:105](../../covex_label_manager/qt_ui/settings.py#L105) | Señales/registro JSON | Sin vínculo directo |
| S0462 | SettingsMixin.build_native_settings | button | [covex_label_manager/qt_ui/settings.py:109](../../covex_label_manager/qt_ui/settings.py#L109) | self.open_acceptance_readiness | Sin vínculo directo |
| S0463 | SettingsMixin.build_native_settings | button | [covex_label_manager/qt_ui/settings.py:110](../../covex_label_manager/qt_ui/settings.py#L110) | self.open_uat_session | Sin vínculo directo |
| S0464 | SettingsMixin.build_native_settings | button | [covex_label_manager/qt_ui/settings.py:111](../../covex_label_manager/qt_ui/settings.py#L111) | lambda: self.navigate('library') | 10 |
| S0465 | SettingsMixin.build_native_settings | QLineEdit | [covex_label_manager/qt_ui/settings.py:117](../../covex_label_manager/qt_ui/settings.py#L117) | Señales/registro JSON | Sin vínculo directo |
| S0466 | SettingsMixin.build_native_settings | button | [covex_label_manager/qt_ui/settings.py:121](../../covex_label_manager/qt_ui/settings.py#L121) | self.save_settings_operator | 1 |
| S0467 | SettingsMixin.build_native_settings | QLineEdit | [covex_label_manager/qt_ui/settings.py:124](../../covex_label_manager/qt_ui/settings.py#L124) | Señales/registro JSON | Sin vínculo directo |
| S0468 | SettingsMixin.build_native_settings | button | [covex_label_manager/qt_ui/settings.py:128](../../covex_label_manager/qt_ui/settings.py#L128) | self.copy_settings_path | Sin vínculo directo |
| S0469 | SettingsMixin.build_native_settings | button | [covex_label_manager/qt_ui/settings.py:131](../../covex_label_manager/qt_ui/settings.py#L131) | self.create_settings_backup | 1 |
| S0470 | SettingsMixin.build_native_settings | label | [covex_label_manager/qt_ui/settings.py:132](../../covex_label_manager/qt_ui/settings.py#L132) | Señales/registro JSON | Sin vínculo directo |
| S0471 | SettingsMixin.build_native_settings | label | [covex_label_manager/qt_ui/settings.py:145](../../covex_label_manager/qt_ui/settings.py#L145) | Señales/registro JSON | Sin vínculo directo |
| S0472 | SettingsMixin.build_native_settings | button | [covex_label_manager/qt_ui/settings.py:147](../../covex_label_manager/qt_ui/settings.py#L147) | self.import_settings_cm | 1 |
| S0473 | SettingsMixin.build_native_settings | button | [covex_label_manager/qt_ui/settings.py:161](../../covex_label_manager/qt_ui/settings.py#L161) | self.approve_settings_status | 1 |
| S0474 | SettingsMixin.build_native_settings | button | [covex_label_manager/qt_ui/settings.py:172](../../covex_label_manager/qt_ui/settings.py#L172) | self.refresh_native_settings | 1 |
| S0475 | SettingsMixin.build_native_settings | button | [covex_label_manager/qt_ui/settings.py:177](../../covex_label_manager/qt_ui/settings.py#L177) | lambda: self.open_legacy('admin') | Sin vínculo directo |
| S0476 | SettingsMixin.navigate | information | [covex_label_manager/qt_ui/settings.py:184](../../covex_label_manager/qt_ui/settings.py#L184) | Señales/registro JSON | Sin vínculo directo |
| S0477 | SettingsMixin.save_settings_operator | warning | [covex_label_manager/qt_ui/settings.py:259](../../covex_label_manager/qt_ui/settings.py#L259) | Señales/registro JSON | Sin vínculo directo |
| S0478 | SettingsMixin.save_settings_operator | warning | [covex_label_manager/qt_ui/settings.py:267](../../covex_label_manager/qt_ui/settings.py#L267) | Señales/registro JSON | Sin vínculo directo |
| S0479 | SettingsMixin.create_settings_backup | question | [covex_label_manager/qt_ui/settings.py:277](../../covex_label_manager/qt_ui/settings.py#L277) | Señales/registro JSON | 23 |
| S0480 | SettingsMixin.create_settings_backup | information | [covex_label_manager/qt_ui/settings.py:289](../../covex_label_manager/qt_ui/settings.py#L289) | Señales/registro JSON | Sin vínculo directo |
| S0481 | SettingsMixin.create_settings_backup | warning | [covex_label_manager/qt_ui/settings.py:295](../../covex_label_manager/qt_ui/settings.py#L295) | Señales/registro JSON | Sin vínculo directo |
| S0482 | SettingsMixin.import_settings_cm | getOpenFileName | [covex_label_manager/qt_ui/settings.py:301](../../covex_label_manager/qt_ui/settings.py#L301) | Señales/registro JSON | Sin vínculo directo |
| S0483 | SettingsMixin.import_settings_cm | warning | [covex_label_manager/qt_ui/settings.py:307](../../covex_label_manager/qt_ui/settings.py#L307) | Señales/registro JSON | Sin vínculo directo |
| S0484 | SettingsMixin.import_settings_cm | question | [covex_label_manager/qt_ui/settings.py:313](../../covex_label_manager/qt_ui/settings.py#L313) | Señales/registro JSON | 23 |
| S0485 | SettingsMixin.import_settings_cm | warning | [covex_label_manager/qt_ui/settings.py:327](../../covex_label_manager/qt_ui/settings.py#L327) | Señales/registro JSON | Sin vínculo directo |
| S0486 | SettingsMixin.approve_settings_status | information | [covex_label_manager/qt_ui/settings.py:333](../../covex_label_manager/qt_ui/settings.py#L333) | Señales/registro JSON | Sin vínculo directo |
| S0487 | SettingsMixin.approve_settings_status | warning | [covex_label_manager/qt_ui/settings.py:340](../../covex_label_manager/qt_ui/settings.py#L340) | Señales/registro JSON | Sin vínculo directo |
| S0488 | SettingsMixin.approve_settings_status | QDialog | [covex_label_manager/qt_ui/settings.py:345](../../covex_label_manager/qt_ui/settings.py#L345) | Señales/registro JSON | Sin vínculo directo |
| S0489 | SettingsMixin.approve_settings_status | label | [covex_label_manager/qt_ui/settings.py:349](../../covex_label_manager/qt_ui/settings.py#L349) | Señales/registro JSON | Sin vínculo directo |
| S0490 | SettingsMixin.approve_settings_status | QLineEdit | [covex_label_manager/qt_ui/settings.py:356](../../covex_label_manager/qt_ui/settings.py#L356) | Señales/registro JSON | Sin vínculo directo |
| S0491 | SettingsMixin.approve_settings_status | QLineEdit | [covex_label_manager/qt_ui/settings.py:358](../../covex_label_manager/qt_ui/settings.py#L358) | Señales/registro JSON | Sin vínculo directo |
| S0492 | SettingsMixin.approve_settings_status | addRow | [covex_label_manager/qt_ui/settings.py:360](../../covex_label_manager/qt_ui/settings.py#L360) | Señales/registro JSON | Sin vínculo directo |
| S0493 | SettingsMixin.approve_settings_status | addRow | [covex_label_manager/qt_ui/settings.py:361](../../covex_label_manager/qt_ui/settings.py#L361) | Señales/registro JSON | Sin vínculo directo |
| S0494 | SettingsMixin.approve_settings_status | QCheckBox | [covex_label_manager/qt_ui/settings.py:363](../../covex_label_manager/qt_ui/settings.py#L363) | Señales/registro JSON | Sin vínculo directo |
| S0495 | SettingsMixin.approve_settings_status | label | [covex_label_manager/qt_ui/settings.py:366](../../covex_label_manager/qt_ui/settings.py#L366) | Señales/registro JSON | Sin vínculo directo |
| S0496 | SettingsMixin.approve_settings_status | QDialogButtonBox | [covex_label_manager/qt_ui/settings.py:369](../../covex_label_manager/qt_ui/settings.py#L369) | Señales/registro JSON | 23 |
| S0497 | SettingsMixin.approve_settings_status | button | [covex_label_manager/qt_ui/settings.py:372](../../covex_label_manager/qt_ui/settings.py#L372) | Señales/registro JSON | 23 |
| S0498 | SettingsMixin.approve_settings_status | button | [covex_label_manager/qt_ui/settings.py:373](../../covex_label_manager/qt_ui/settings.py#L373) | Señales/registro JSON | 23 |
| S0499 | SettingsMixin.approve_settings_status.validate | button | [covex_label_manager/qt_ui/settings.py:376](../../covex_label_manager/qt_ui/settings.py#L376) | Señales/registro JSON | 23 |
| S0500 | SettingsMixin.approve_settings_status | connect | [covex_label_manager/qt_ui/settings.py:378](../../covex_label_manager/qt_ui/settings.py#L378) | validate | Sin vínculo directo |
| S0501 | SettingsMixin.approve_settings_status | connect | [covex_label_manager/qt_ui/settings.py:379](../../covex_label_manager/qt_ui/settings.py#L379) | validate | Sin vínculo directo |
| S0502 | SettingsMixin.approve_settings_status | connect | [covex_label_manager/qt_ui/settings.py:380](../../covex_label_manager/qt_ui/settings.py#L380) | validate | Sin vínculo directo |
| S0503 | SettingsMixin.approve_settings_status | connect | [covex_label_manager/qt_ui/settings.py:381](../../covex_label_manager/qt_ui/settings.py#L381) | lambda: dialog.accept() if validate() else error.setText('Complete los datos y el cotejo.') | 15 |
| S0504 | SettingsMixin.approve_settings_status | connect | [covex_label_manager/qt_ui/settings.py:382](../../covex_label_manager/qt_ui/settings.py#L382) | dialog.reject | 2 |
| S0505 | SettingsMixin.approve_settings_status | warning | [covex_label_manager/qt_ui/settings.py:395](../../covex_label_manager/qt_ui/settings.py#L395) | Señales/registro JSON | Sin vínculo directo |
| S0506 | SettingsMixin.open_acceptance_readiness | warning | [covex_label_manager/qt_ui/settings.py:404](../../covex_label_manager/qt_ui/settings.py#L404) | Señales/registro JSON | Sin vínculo directo |
| S0507 | SettingsMixin.open_uat_session | warning | [covex_label_manager/qt_ui/settings.py:411](../../covex_label_manager/qt_ui/settings.py#L411) | Señales/registro JSON | Sin vínculo directo |
| S0508 | OccupiedSlotsDialog.__init__ | label | [covex_label_manager/qt_ui/sheet_designer.py:48](../../covex_label_manager/qt_ui/sheet_designer.py#L48) | Señales/registro JSON | Sin vínculo directo |
| S0509 | OccupiedSlotsDialog.__init__ | QScrollArea | [covex_label_manager/qt_ui/sheet_designer.py:52](../../covex_label_manager/qt_ui/sheet_designer.py#L52) | Señales/registro JSON | Sin vínculo directo |
| S0510 | OccupiedSlotsDialog.__init__ | QCheckBox | [covex_label_manager/qt_ui/sheet_designer.py:56](../../covex_label_manager/qt_ui/sheet_designer.py#L56) | Señales/registro JSON | Sin vínculo directo |
| S0511 | OccupiedSlotsDialog.__init__ | label | [covex_label_manager/qt_ui/sheet_designer.py:66](../../covex_label_manager/qt_ui/sheet_designer.py#L66) | Señales/registro JSON | Sin vínculo directo |
| S0512 | OccupiedSlotsDialog.__init__ | QDialogButtonBox | [covex_label_manager/qt_ui/sheet_designer.py:68](../../covex_label_manager/qt_ui/sheet_designer.py#L68) | Señales/registro JSON | 23 |
| S0513 | OccupiedSlotsDialog.__init__ | connect | [covex_label_manager/qt_ui/sheet_designer.py:69](../../covex_label_manager/qt_ui/sheet_designer.py#L69) | self.accept | Sin vínculo directo |
| S0514 | OccupiedSlotsDialog.__init__ | connect | [covex_label_manager/qt_ui/sheet_designer.py:69](../../covex_label_manager/qt_ui/sheet_designer.py#L69) | self.reject | 2 |
| S0515 | SheetDesigner.__init__ | label | [covex_label_manager/qt_ui/sheet_designer.py:87](../../covex_label_manager/qt_ui/sheet_designer.py#L87) | Señales/registro JSON | Sin vínculo directo |
| S0516 | SheetDesigner.__init__ | label | [covex_label_manager/qt_ui/sheet_designer.py:88](../../covex_label_manager/qt_ui/sheet_designer.py#L88) | Señales/registro JSON | Sin vínculo directo |
| S0517 | SheetDesigner.__init__ | Preview | [covex_label_manager/qt_ui/sheet_designer.py:89](../../covex_label_manager/qt_ui/sheet_designer.py#L89) | Señales/registro JSON | Sin vínculo directo |
| S0518 | SheetDesigner.__init__ | QScrollArea | [covex_label_manager/qt_ui/sheet_designer.py:90](../../covex_label_manager/qt_ui/sheet_designer.py#L90) | Señales/registro JSON | Sin vínculo directo |
| S0519 | SheetDesigner.__init__ | QComboBox | [covex_label_manager/qt_ui/sheet_designer.py:91](../../covex_label_manager/qt_ui/sheet_designer.py#L91) | Señales/registro JSON | Sin vínculo directo |
| S0520 | SheetDesigner.__init__ | addItems | [covex_label_manager/qt_ui/sheet_designer.py:91](../../covex_label_manager/qt_ui/sheet_designer.py#L91) | Señales/registro JSON | Sin vínculo directo |
| S0521 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:91](../../covex_label_manager/qt_ui/sheet_designer.py#L91) | Señales/registro JSON | 1 |
| S0522 | SheetDesigner.__init__ | QComboBox | [covex_label_manager/qt_ui/sheet_designer.py:92](../../covex_label_manager/qt_ui/sheet_designer.py#L92) | Señales/registro JSON | Sin vínculo directo |
| S0523 | SheetDesigner.__init__ | addItem | [covex_label_manager/qt_ui/sheet_designer.py:92](../../covex_label_manager/qt_ui/sheet_designer.py#L92) | Señales/registro JSON | Sin vínculo directo |
| S0524 | SheetDesigner.__init__ | addItem | [covex_label_manager/qt_ui/sheet_designer.py:92](../../covex_label_manager/qt_ui/sheet_designer.py#L92) | Señales/registro JSON | Sin vínculo directo |
| S0525 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:92](../../covex_label_manager/qt_ui/sheet_designer.py#L92) | Señales/registro JSON | Sin vínculo directo |
| S0526 | SheetDesigner.__init__ | QComboBox | [covex_label_manager/qt_ui/sheet_designer.py:93](../../covex_label_manager/qt_ui/sheet_designer.py#L93) | Señales/registro JSON | Sin vínculo directo |
| S0527 | SheetDesigner.__init__ | addItem | [covex_label_manager/qt_ui/sheet_designer.py:93](../../covex_label_manager/qt_ui/sheet_designer.py#L93) | Señales/registro JSON | Sin vínculo directo |
| S0528 | SheetDesigner.__init__ | addItem | [covex_label_manager/qt_ui/sheet_designer.py:93](../../covex_label_manager/qt_ui/sheet_designer.py#L93) | Señales/registro JSON | Sin vínculo directo |
| S0529 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:93](../../covex_label_manager/qt_ui/sheet_designer.py#L93) | Señales/registro JSON | Sin vínculo directo |
| S0530 | SheetDesigner.__init__ | QDoubleSpinBox | [covex_label_manager/qt_ui/sheet_designer.py:96](../../covex_label_manager/qt_ui/sheet_designer.py#L96) | Señales/registro JSON | Sin vínculo directo |
| S0531 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:96](../../covex_label_manager/qt_ui/sheet_designer.py#L96) | Señales/registro JSON | Sin vínculo directo |
| S0532 | SheetDesigner.__init__ | connect | [covex_label_manager/qt_ui/sheet_designer.py:97](../../covex_label_manager/qt_ui/sheet_designer.py#L97) | self.controls_changed | Sin vínculo directo |
| S0533 | SheetDesigner.__init__ | QSpinBox | [covex_label_manager/qt_ui/sheet_designer.py:98](../../covex_label_manager/qt_ui/sheet_designer.py#L98) | Señales/registro JSON | Sin vínculo directo |
| S0534 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:98](../../covex_label_manager/qt_ui/sheet_designer.py#L98) | Señales/registro JSON | 6 |
| S0535 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:99](../../covex_label_manager/qt_ui/sheet_designer.py#L99) | Señales/registro JSON | 1 |
| S0536 | SheetDesigner.__init__ | button | [covex_label_manager/qt_ui/sheet_designer.py:99](../../covex_label_manager/qt_ui/sheet_designer.py#L99) | self.arrange | 1 |
| S0537 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:100](../../covex_label_manager/qt_ui/sheet_designer.py#L100) | Señales/registro JSON | Sin vínculo directo |
| S0538 | SheetDesigner.__init__ | button | [covex_label_manager/qt_ui/sheet_designer.py:100](../../covex_label_manager/qt_ui/sheet_designer.py#L100) | self.auto_arrange | Sin vínculo directo |
| S0539 | SheetDesigner.__init__ | button | [covex_label_manager/qt_ui/sheet_designer.py:101](../../covex_label_manager/qt_ui/sheet_designer.py#L101) | self.mark_used_slots | 1 |
| S0540 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:102](../../covex_label_manager/qt_ui/sheet_designer.py#L102) | Señales/registro JSON | Sin vínculo directo |
| S0541 | SheetDesigner.__init__ | QCheckBox | [covex_label_manager/qt_ui/sheet_designer.py:103](../../covex_label_manager/qt_ui/sheet_designer.py#L103) | Señales/registro JSON | Sin vínculo directo |
| S0542 | SheetDesigner.__init__ | QCheckBox | [covex_label_manager/qt_ui/sheet_designer.py:103](../../covex_label_manager/qt_ui/sheet_designer.py#L103) | Señales/registro JSON | Sin vínculo directo |
| S0543 | SheetDesigner.__init__ | connect | [covex_label_manager/qt_ui/sheet_designer.py:103](../../covex_label_manager/qt_ui/sheet_designer.py#L103) | self.redraw | Sin vínculo directo |
| S0544 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:103](../../covex_label_manager/qt_ui/sheet_designer.py#L103) | Señales/registro JSON | Sin vínculo directo |
| S0545 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:103](../../covex_label_manager/qt_ui/sheet_designer.py#L103) | Señales/registro JSON | Sin vínculo directo |
| S0546 | SheetDesigner.__init__ | QDoubleSpinBox | [covex_label_manager/qt_ui/sheet_designer.py:106](../../covex_label_manager/qt_ui/sheet_designer.py#L106) | Señales/registro JSON | Sin vínculo directo |
| S0547 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:106](../../covex_label_manager/qt_ui/sheet_designer.py#L106) | Señales/registro JSON | Sin vínculo directo |
| S0548 | SheetDesigner.__init__ | connect | [covex_label_manager/qt_ui/sheet_designer.py:106](../../covex_label_manager/qt_ui/sheet_designer.py#L106) | self.numeric_box | 1 |
| S0549 | SheetDesigner.__init__ | QComboBox | [covex_label_manager/qt_ui/sheet_designer.py:107](../../covex_label_manager/qt_ui/sheet_designer.py#L107) | Señales/registro JSON | Sin vínculo directo |
| S0550 | SheetDesigner.__init__ | addItems | [covex_label_manager/qt_ui/sheet_designer.py:107](../../covex_label_manager/qt_ui/sheet_designer.py#L107) | Señales/registro JSON | Sin vínculo directo |
| S0551 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:107](../../covex_label_manager/qt_ui/sheet_designer.py#L107) | Señales/registro JSON | Sin vínculo directo |
| S0552 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:108](../../covex_label_manager/qt_ui/sheet_designer.py#L108) | Señales/registro JSON | 1 |
| S0553 | SheetDesigner.__init__ | button | [covex_label_manager/qt_ui/sheet_designer.py:108](../../covex_label_manager/qt_ui/sheet_designer.py#L108) | lambda: self.align(align.currentIndex()) | 1 |
| S0554 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:109](../../covex_label_manager/qt_ui/sheet_designer.py#L109) | Señales/registro JSON | Sin vínculo directo |
| S0555 | SheetDesigner.__init__ | button | [covex_label_manager/qt_ui/sheet_designer.py:109](../../covex_label_manager/qt_ui/sheet_designer.py#L109) | self.remove | Sin vínculo directo |
| S0556 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:110](../../covex_label_manager/qt_ui/sheet_designer.py#L110) | Señales/registro JSON | Sin vínculo directo |
| S0557 | SheetDesigner.__init__ | button | [covex_label_manager/qt_ui/sheet_designer.py:110](../../covex_label_manager/qt_ui/sheet_designer.py#L110) | self.preview | Sin vínculo directo |
| S0558 | SheetDesigner.__init__ | QComboBox | [covex_label_manager/qt_ui/sheet_designer.py:112](../../covex_label_manager/qt_ui/sheet_designer.py#L112) | Señales/registro JSON | Sin vínculo directo |
| S0559 | SheetDesigner.__init__ | addItem | [covex_label_manager/qt_ui/sheet_designer.py:112](../../covex_label_manager/qt_ui/sheet_designer.py#L112) | Señales/registro JSON | Sin vínculo directo |
| S0560 | SheetDesigner.__init__ | addItem | [covex_label_manager/qt_ui/sheet_designer.py:113](../../covex_label_manager/qt_ui/sheet_designer.py#L113) | Señales/registro JSON | Sin vínculo directo |
| S0561 | SheetDesigner.__init__ | connect | [covex_label_manager/qt_ui/sheet_designer.py:114](../../covex_label_manager/qt_ui/sheet_designer.py#L114) | self.load_profile | Sin vínculo directo |
| S0562 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:114](../../covex_label_manager/qt_ui/sheet_designer.py#L114) | Señales/registro JSON | 1 |
| S0563 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:114](../../covex_label_manager/qt_ui/sheet_designer.py#L114) | Señales/registro JSON | Sin vínculo directo |
| S0564 | SheetDesigner.__init__ | button | [covex_label_manager/qt_ui/sheet_designer.py:114](../../covex_label_manager/qt_ui/sheet_designer.py#L114) | self.save_profile | Sin vínculo directo |
| S0565 | SheetDesigner.__init__ | label | [covex_label_manager/qt_ui/sheet_designer.py:116](../../covex_label_manager/qt_ui/sheet_designer.py#L116) | Señales/registro JSON | 1 |
| S0566 | SheetDesigner.__init__ | addRow | [covex_label_manager/qt_ui/sheet_designer.py:120](../../covex_label_manager/qt_ui/sheet_designer.py#L120) | Señales/registro JSON | 1 |
| S0567 | SheetDesigner.__init__ | label | [covex_label_manager/qt_ui/sheet_designer.py:121](../../covex_label_manager/qt_ui/sheet_designer.py#L121) | Señales/registro JSON | Sin vínculo directo |
| S0568 | SheetDesigner.__init__ | button | [covex_label_manager/qt_ui/sheet_designer.py:123](../../covex_label_manager/qt_ui/sheet_designer.py#L123) | fn | Sin vínculo directo |
| S0569 | SheetDesigner.__init__ | QDialogButtonBox | [covex_label_manager/qt_ui/sheet_designer.py:125](../../covex_label_manager/qt_ui/sheet_designer.py#L125) | Señales/registro JSON | 23 |
| S0570 | SheetDesigner.__init__ | button | [covex_label_manager/qt_ui/sheet_designer.py:126](../../covex_label_manager/qt_ui/sheet_designer.py#L126) | Señales/registro JSON | 23 |
| S0571 | SheetDesigner.__init__ | connect | [covex_label_manager/qt_ui/sheet_designer.py:126](../../covex_label_manager/qt_ui/sheet_designer.py#L126) | self.accept_valid | 1 |
| S0572 | SheetDesigner.__init__ | connect | [covex_label_manager/qt_ui/sheet_designer.py:126](../../covex_label_manager/qt_ui/sheet_designer.py#L126) | self.reject | 2 |
| S0573 | SheetDesigner.__init__ | connect | [covex_label_manager/qt_ui/sheet_designer.py:127](../../covex_label_manager/qt_ui/sheet_designer.py#L127) | self.controls_changed | Sin vínculo directo |
| S0574 | SheetDesigner.__init__ | connect | [covex_label_manager/qt_ui/sheet_designer.py:128](../../covex_label_manager/qt_ui/sheet_designer.py#L128) | self.selection | Sin vínculo directo |
| S0575 | SheetDesigner.redraw | addItem | [covex_label_manager/qt_ui/sheet_designer.py:191](../../covex_label_manager/qt_ui/sheet_designer.py#L191) | Señales/registro JSON | Sin vínculo directo |
| S0576 | SheetDesigner.redraw | button | [covex_label_manager/qt_ui/sheet_designer.py:203](../../covex_label_manager/qt_ui/sheet_designer.py#L203) | Señales/registro JSON | 23 |
| S0577 | SheetDesigner.redraw | button | [covex_label_manager/qt_ui/sheet_designer.py:205](../../covex_label_manager/qt_ui/sheet_designer.py#L205) | Señales/registro JSON | 23 |
| S0578 | SheetDesigner.save_profile | getText | [covex_label_manager/qt_ui/sheet_designer.py:257](../../covex_label_manager/qt_ui/sheet_designer.py#L257) | Señales/registro JSON | Sin vínculo directo |
| S0579 | SheetDesigner.save_profile | getText | [covex_label_manager/qt_ui/sheet_designer.py:259](../../covex_label_manager/qt_ui/sheet_designer.py#L259) | Señales/registro JSON | Sin vínculo directo |
| S0580 | UatSessionDialog.__init__ | label | [covex_label_manager/qt_ui/uat_session_dialog.py:18](../../covex_label_manager/qt_ui/uat_session_dialog.py#L18) | Señales/registro JSON | Sin vínculo directo |
| S0581 | UatSessionDialog.__init__ | label | [covex_label_manager/qt_ui/uat_session_dialog.py:19](../../covex_label_manager/qt_ui/uat_session_dialog.py#L19) | Señales/registro JSON | Sin vínculo directo |
| S0582 | UatSessionDialog.__init__ | button | [covex_label_manager/qt_ui/uat_session_dialog.py:24](../../covex_label_manager/qt_ui/uat_session_dialog.py#L24) | self.new_session | Sin vínculo directo |
| S0583 | UatSessionDialog.__init__ | button | [covex_label_manager/qt_ui/uat_session_dialog.py:25](../../covex_label_manager/qt_ui/uat_session_dialog.py#L25) | self.open_session | Sin vínculo directo |
| S0584 | UatSessionDialog.__init__ | button | [covex_label_manager/qt_ui/uat_session_dialog.py:26](../../covex_label_manager/qt_ui/uat_session_dialog.py#L26) | self.verify | 1 |
| S0585 | UatSessionDialog.__init__ | label | [covex_label_manager/qt_ui/uat_session_dialog.py:29](../../covex_label_manager/qt_ui/uat_session_dialog.py#L29) | Señales/registro JSON | Sin vínculo directo |
| S0586 | UatSessionDialog.__init__ | QSplitter | [covex_label_manager/qt_ui/uat_session_dialog.py:31](../../covex_label_manager/qt_ui/uat_session_dialog.py#L31) | Señales/registro JSON | Sin vínculo directo |
| S0587 | UatSessionDialog.__init__ | QTableWidget | [covex_label_manager/qt_ui/uat_session_dialog.py:32](../../covex_label_manager/qt_ui/uat_session_dialog.py#L32) | Señales/registro JSON | Sin vínculo directo |
| S0588 | UatSessionDialog.__init__ | connect | [covex_label_manager/qt_ui/uat_session_dialog.py:38](../../covex_label_manager/qt_ui/uat_session_dialog.py#L38) | self.select_case | Sin vínculo directo |
| S0589 | UatSessionDialog.__init__ | label | [covex_label_manager/qt_ui/uat_session_dialog.py:41](../../covex_label_manager/qt_ui/uat_session_dialog.py#L41) | Señales/registro JSON | Sin vínculo directo |
| S0590 | UatSessionDialog.__init__ | addRow | [covex_label_manager/qt_ui/uat_session_dialog.py:42](../../covex_label_manager/qt_ui/uat_session_dialog.py#L42) | Señales/registro JSON | Sin vínculo directo |
| S0591 | UatSessionDialog.__init__ | QComboBox | [covex_label_manager/qt_ui/uat_session_dialog.py:43](../../covex_label_manager/qt_ui/uat_session_dialog.py#L43) | Señales/registro JSON | Sin vínculo directo |
| S0592 | UatSessionDialog.__init__ | addItem | [covex_label_manager/qt_ui/uat_session_dialog.py:44](../../covex_label_manager/qt_ui/uat_session_dialog.py#L44) | Señales/registro JSON | Sin vínculo directo |
| S0593 | UatSessionDialog.__init__ | addRow | [covex_label_manager/qt_ui/uat_session_dialog.py:45](../../covex_label_manager/qt_ui/uat_session_dialog.py#L45) | Señales/registro JSON | 2 |
| S0594 | UatSessionDialog.__init__ | QLineEdit | [covex_label_manager/qt_ui/uat_session_dialog.py:46](../../covex_label_manager/qt_ui/uat_session_dialog.py#L46) | Señales/registro JSON | Sin vínculo directo |
| S0595 | UatSessionDialog.__init__ | addRow | [covex_label_manager/qt_ui/uat_session_dialog.py:46](../../covex_label_manager/qt_ui/uat_session_dialog.py#L46) | Señales/registro JSON | 2 |
| S0596 | UatSessionDialog.__init__ | QLineEdit | [covex_label_manager/qt_ui/uat_session_dialog.py:47](../../covex_label_manager/qt_ui/uat_session_dialog.py#L47) | Señales/registro JSON | Sin vínculo directo |
| S0597 | UatSessionDialog.__init__ | addRow | [covex_label_manager/qt_ui/uat_session_dialog.py:48](../../covex_label_manager/qt_ui/uat_session_dialog.py#L48) | Señales/registro JSON | 2 |
| S0598 | UatSessionDialog.__init__ | QPlainTextEdit | [covex_label_manager/qt_ui/uat_session_dialog.py:49](../../covex_label_manager/qt_ui/uat_session_dialog.py#L49) | Señales/registro JSON | Sin vínculo directo |
| S0599 | UatSessionDialog.__init__ | addRow | [covex_label_manager/qt_ui/uat_session_dialog.py:50](../../covex_label_manager/qt_ui/uat_session_dialog.py#L50) | Señales/registro JSON | 1 |
| S0600 | UatSessionDialog.__init__ | QLineEdit | [covex_label_manager/qt_ui/uat_session_dialog.py:52](../../covex_label_manager/qt_ui/uat_session_dialog.py#L52) | Señales/registro JSON | Sin vínculo directo |
| S0601 | UatSessionDialog.__init__ | button | [covex_label_manager/qt_ui/uat_session_dialog.py:54](../../covex_label_manager/qt_ui/uat_session_dialog.py#L54) | self.choose_evidence | Sin vínculo directo |
| S0602 | UatSessionDialog.__init__ | addRow | [covex_label_manager/qt_ui/uat_session_dialog.py:55](../../covex_label_manager/qt_ui/uat_session_dialog.py#L55) | Señales/registro JSON | Sin vínculo directo |
| S0603 | UatSessionDialog.__init__ | label | [covex_label_manager/qt_ui/uat_session_dialog.py:56](../../covex_label_manager/qt_ui/uat_session_dialog.py#L56) | Señales/registro JSON | Sin vínculo directo |
| S0604 | UatSessionDialog.__init__ | addRow | [covex_label_manager/qt_ui/uat_session_dialog.py:57](../../covex_label_manager/qt_ui/uat_session_dialog.py#L57) | Señales/registro JSON | Sin vínculo directo |
| S0605 | UatSessionDialog.__init__ | button | [covex_label_manager/qt_ui/uat_session_dialog.py:58](../../covex_label_manager/qt_ui/uat_session_dialog.py#L58) | self.save_case | 2 |
| S0606 | UatSessionDialog.__init__ | addRow | [covex_label_manager/qt_ui/uat_session_dialog.py:59](../../covex_label_manager/qt_ui/uat_session_dialog.py#L59) | Señales/registro JSON | 2 |
| S0607 | UatSessionDialog.__init__ | QDialogButtonBox | [covex_label_manager/qt_ui/uat_session_dialog.py:61](../../covex_label_manager/qt_ui/uat_session_dialog.py#L61) | Señales/registro JSON | 23 |
| S0608 | UatSessionDialog.__init__ | connect | [covex_label_manager/qt_ui/uat_session_dialog.py:62](../../covex_label_manager/qt_ui/uat_session_dialog.py#L62) | self.reject | 2 |
| S0609 | UatSessionDialog._warn | warning | [covex_label_manager/qt_ui/uat_session_dialog.py:65](../../covex_label_manager/qt_ui/uat_session_dialog.py#L65) | Señales/registro JSON | Sin vínculo directo |
| S0610 | UatSessionDialog.new_session | getOpenFileName | [covex_label_manager/qt_ui/uat_session_dialog.py:68](../../covex_label_manager/qt_ui/uat_session_dialog.py#L68) | Señales/registro JSON | Sin vínculo directo |
| S0611 | UatSessionDialog.new_session | QDialog | [covex_label_manager/qt_ui/uat_session_dialog.py:70](../../covex_label_manager/qt_ui/uat_session_dialog.py#L70) | Señales/registro JSON | Sin vínculo directo |
| S0612 | UatSessionDialog.new_session | QLineEdit | [covex_label_manager/qt_ui/uat_session_dialog.py:76](../../covex_label_manager/qt_ui/uat_session_dialog.py#L76) | Señales/registro JSON | Sin vínculo directo |
| S0613 | UatSessionDialog.new_session | addRow | [covex_label_manager/qt_ui/uat_session_dialog.py:77](../../covex_label_manager/qt_ui/uat_session_dialog.py#L77) | Señales/registro JSON | Sin vínculo directo |
| S0614 | UatSessionDialog.new_session | QDialogButtonBox | [covex_label_manager/qt_ui/uat_session_dialog.py:79](../../covex_label_manager/qt_ui/uat_session_dialog.py#L79) | Señales/registro JSON | 23 |
| S0615 | UatSessionDialog.new_session | connect | [covex_label_manager/qt_ui/uat_session_dialog.py:80](../../covex_label_manager/qt_ui/uat_session_dialog.py#L80) | dialog.accept | Sin vínculo directo |
| S0616 | UatSessionDialog.new_session | connect | [covex_label_manager/qt_ui/uat_session_dialog.py:80](../../covex_label_manager/qt_ui/uat_session_dialog.py#L80) | dialog.reject | 2 |
| S0617 | UatSessionDialog.new_session | getSaveFileName | [covex_label_manager/qt_ui/uat_session_dialog.py:83](../../covex_label_manager/qt_ui/uat_session_dialog.py#L83) | Señales/registro JSON | Sin vínculo directo |
| S0618 | UatSessionDialog.open_session | getOpenFileName | [covex_label_manager/qt_ui/uat_session_dialog.py:92](../../covex_label_manager/qt_ui/uat_session_dialog.py#L92) | Señales/registro JSON | Sin vínculo directo |
| S0619 | UatSessionDialog.choose_evidence | getOpenFileName | [covex_label_manager/qt_ui/uat_session_dialog.py:132](../../covex_label_manager/qt_ui/uat_session_dialog.py#L132) | Señales/registro JSON | Sin vínculo directo |
| S0620 | UatSessionDialog.save_case | question | [covex_label_manager/qt_ui/uat_session_dialog.py:142](../../covex_label_manager/qt_ui/uat_session_dialog.py#L142) | Señales/registro JSON | 23 |
| S0621 | UatSessionDialog.verify | information | [covex_label_manager/qt_ui/uat_session_dialog.py:158](../../covex_label_manager/qt_ui/uat_session_dialog.py#L158) | Señales/registro JSON | Sin vínculo directo |
| S0622 | VariantsMixin.build_library | QComboBox | [covex_label_manager/qt_ui/variants.py:23](../../covex_label_manager/qt_ui/variants.py#L23) | Señales/registro JSON | Sin vínculo directo |
| S0623 | VariantsMixin.build_library | connect | [covex_label_manager/qt_ui/variants.py:24](../../covex_label_manager/qt_ui/variants.py#L24) | self.choose_library_variant | Sin vínculo directo |
| S0624 | VariantsMixin.build_library | button | [covex_label_manager/qt_ui/variants.py:25](../../covex_label_manager/qt_ui/variants.py#L25) | self.variant_menu | Sin vínculo directo |
| S0625 | VariantsMixin.build_library | label | [covex_label_manager/qt_ui/variants.py:27](../../covex_label_manager/qt_ui/variants.py#L27) | Señales/registro JSON | Sin vínculo directo |
| S0626 | VariantsMixin.build_editor | label | [covex_label_manager/qt_ui/variants.py:31](../../covex_label_manager/qt_ui/variants.py#L31) | Señales/registro JSON | Sin vínculo directo |
| S0627 | VariantsMixin.build_editor | QComboBox | [covex_label_manager/qt_ui/variants.py:32](../../covex_label_manager/qt_ui/variants.py#L32) | Señales/registro JSON | Sin vínculo directo |
| S0628 | VariantsMixin.build_editor | connect | [covex_label_manager/qt_ui/variants.py:33](../../covex_label_manager/qt_ui/variants.py#L33) | self.choose_editor_variant | Sin vínculo directo |
| S0629 | VariantsMixin.build_editor | button | [covex_label_manager/qt_ui/variants.py:34](../../covex_label_manager/qt_ui/variants.py#L34) | self.variant_menu | Sin vínculo directo |
| S0630 | VariantsMixin.fill_variants | addItem | [covex_label_manager/qt_ui/variants.py:37](../../covex_label_manager/qt_ui/variants.py#L37) | Señales/registro JSON | Sin vínculo directo |
| S0631 | VariantsMixin.fill_variants | addItem | [covex_label_manager/qt_ui/variants.py:40](../../covex_label_manager/qt_ui/variants.py#L40) | Señales/registro JSON | Sin vínculo directo |
| S0632 | VariantsMixin.save_work | warning | [covex_label_manager/qt_ui/variants.py:113](../../covex_label_manager/qt_ui/variants.py#L113) | Señales/registro JSON | Sin vínculo directo |
| S0633 | VariantsMixin.variant_menu | addAction | [covex_label_manager/qt_ui/variants.py:135](../../covex_label_manager/qt_ui/variants.py#L135) | self.create_variant_ui | Sin vínculo directo |
| S0634 | VariantsMixin.variant_menu | addAction | [covex_label_manager/qt_ui/variants.py:139](../../covex_label_manager/qt_ui/variants.py#L139) | action | Sin vínculo directo |
| S0635 | VariantsMixin.create_variant_ui | warning | [covex_label_manager/qt_ui/variants.py:146](../../covex_label_manager/qt_ui/variants.py#L146) | Señales/registro JSON | Sin vínculo directo |
| S0636 | VariantsMixin.create_variant_ui | warning | [covex_label_manager/qt_ui/variants.py:150](../../covex_label_manager/qt_ui/variants.py#L150) | Señales/registro JSON | Sin vínculo directo |
| S0637 | VariantsMixin.create_variant_ui | warning | [covex_label_manager/qt_ui/variants.py:165](../../covex_label_manager/qt_ui/variants.py#L165) | Señales/registro JSON | Sin vínculo directo |
| S0638 | VariantsMixin.create_variant_ui | warning | [covex_label_manager/qt_ui/variants.py:170](../../covex_label_manager/qt_ui/variants.py#L170) | Señales/registro JSON | Sin vínculo directo |
| S0639 | VariantsMixin.edit_nominal_size | warning | [covex_label_manager/qt_ui/variants.py:179](../../covex_label_manager/qt_ui/variants.py#L179) | Señales/registro JSON | Sin vínculo directo |
| S0640 | VariantsMixin.variant_transition | question | [covex_label_manager/qt_ui/variants.py:188](../../covex_label_manager/qt_ui/variants.py#L188) | Señales/registro JSON | Sin vínculo directo |
| S0641 | VariantsMixin.approve_variant_ui | getOpenFileName | [covex_label_manager/qt_ui/variants.py:196](../../covex_label_manager/qt_ui/variants.py#L196) | Señales/registro JSON | Sin vínculo directo |
| S0642 | VariantsMixin.approve_variant_ui | question | [covex_label_manager/qt_ui/variants.py:198](../../covex_label_manager/qt_ui/variants.py#L198) | Señales/registro JSON | Sin vínculo directo |
| S0643 | VariantsMixin.compare_variant | QDialog | [covex_label_manager/qt_ui/variants.py:209](../../covex_label_manager/qt_ui/variants.py#L209) | Señales/registro JSON | Sin vínculo directo |
| S0644 | VariantsMixin.compare_variant | QTableWidget | [covex_label_manager/qt_ui/variants.py:212](../../covex_label_manager/qt_ui/variants.py#L212) | Señales/registro JSON | Sin vínculo directo |
| S0645 | VariantsMixin.compare_variant | QDialogButtonBox | [covex_label_manager/qt_ui/variants.py:240](../../covex_label_manager/qt_ui/variants.py#L240) | Señales/registro JSON | 23 |
| S0646 | VariantsMixin.compare_variant | connect | [covex_label_manager/qt_ui/variants.py:240](../../covex_label_manager/qt_ui/variants.py#L240) | dialog.reject | 2 |
| S0647 | VariantsMixin.open_variant_evidence | warning | [covex_label_manager/qt_ui/variants.py:244](../../covex_label_manager/qt_ui/variants.py#L244) | Señales/registro JSON | Sin vínculo directo |
| S0648 | label | QLabel | [covex_label_manager/qt_ui/window.py:20](../../covex_label_manager/qt_ui/window.py#L20) | Señales/registro JSON | Sin vínculo directo |
| S0649 | button | QPushButton | [covex_label_manager/qt_ui/window.py:26](../../covex_label_manager/qt_ui/window.py#L26) | Señales/registro JSON | Sin vínculo directo |
| S0650 | button | connect | [covex_label_manager/qt_ui/window.py:29](../../covex_label_manager/qt_ui/window.py#L29) | callback | Sin vínculo directo |
| S0651 | Preview.__init__ | QGraphicsScene | [covex_label_manager/qt_ui/window.py:43](../../covex_label_manager/qt_ui/window.py#L43) | Señales/registro JSON | Sin vínculo directo |
| S0652 | StudioWindow.__init__ | label | [covex_label_manager/qt_ui/window.py:93](../../covex_label_manager/qt_ui/window.py#L93) | Señales/registro JSON | Sin vínculo directo |
| S0653 | StudioWindow.__init__ | label | [covex_label_manager/qt_ui/window.py:94](../../covex_label_manager/qt_ui/window.py#L94) | Señales/registro JSON | Sin vínculo directo |
| S0654 | StudioWindow.__init__ | button | [covex_label_manager/qt_ui/window.py:97](../../covex_label_manager/qt_ui/window.py#L97) | lambda checked=False, k=key: self.navigate(k) | 10 |
| S0655 | StudioWindow.__init__ | label | [covex_label_manager/qt_ui/window.py:99](../../covex_label_manager/qt_ui/window.py#L99) | Señales/registro JSON | Sin vínculo directo |
| S0656 | StudioWindow.__init__ | QStackedWidget | [covex_label_manager/qt_ui/window.py:101](../../covex_label_manager/qt_ui/window.py#L101) | Señales/registro JSON | Sin vínculo directo |
| S0657 | StudioWindow.__init__ | QShortcut | [covex_label_manager/qt_ui/window.py:106](../../covex_label_manager/qt_ui/window.py#L106) | Señales/registro JSON | Sin vínculo directo |
| S0658 | StudioWindow.__init__ | connect | [covex_label_manager/qt_ui/window.py:107](../../covex_label_manager/qt_ui/window.py#L107) | self.quick_search | Sin vínculo directo |
| S0659 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:112](../../covex_label_manager/qt_ui/window.py#L112) | Señales/registro JSON | Sin vínculo directo |
| S0660 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:113](../../covex_label_manager/qt_ui/window.py#L113) | Señales/registro JSON | Sin vínculo directo |
| S0661 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:115](../../covex_label_manager/qt_ui/window.py#L115) | self.actions_menu | Sin vínculo directo |
| S0662 | StudioWindow.build_library | QLineEdit | [covex_label_manager/qt_ui/window.py:116](../../covex_label_manager/qt_ui/window.py#L116) | Señales/registro JSON | Sin vínculo directo |
| S0663 | StudioWindow.build_library | addAction | [covex_label_manager/qt_ui/window.py:118](../../covex_label_manager/qt_ui/window.py#L118) | QLineEdit.ActionPosition.LeadingPosition | Sin vínculo directo |
| S0664 | StudioWindow.build_library | connect | [covex_label_manager/qt_ui/window.py:120](../../covex_label_manager/qt_ui/window.py#L120) | self.refresh | 1 |
| S0665 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:121](../../covex_label_manager/qt_ui/window.py#L121) | Señales/registro JSON | Sin vínculo directo |
| S0666 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:124](../../covex_label_manager/qt_ui/window.py#L124) | Señales/registro JSON | Sin vínculo directo |
| S0667 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:126](../../covex_label_manager/qt_ui/window.py#L126) | self.toggle_advanced | 2 |
| S0668 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:127](../../covex_label_manager/qt_ui/window.py#L127) | self.reset_filters | Sin vínculo directo |
| S0669 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:130](../../covex_label_manager/qt_ui/window.py#L130) | lambda checked=False, k=key: self.set_mode(k) | Sin vínculo directo |
| S0670 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:132](../../covex_label_manager/qt_ui/window.py#L132) | Señales/registro JSON | Sin vínculo directo |
| S0671 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:133](../../covex_label_manager/qt_ui/window.py#L133) | self.columns_menu | Sin vínculo directo |
| S0672 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:134](../../covex_label_manager/qt_ui/window.py#L134) | self.toggle_inspector | Sin vínculo directo |
| S0673 | StudioWindow.build_library | QSplitter | [covex_label_manager/qt_ui/window.py:136](../../covex_label_manager/qt_ui/window.py#L136) | Señales/registro JSON | Sin vínculo directo |
| S0674 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:138](../../covex_label_manager/qt_ui/window.py#L138) | Señales/registro JSON | Sin vínculo directo |
| S0675 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:141](../../covex_label_manager/qt_ui/window.py#L141) | Señales/registro JSON | Sin vínculo directo |
| S0676 | StudioWindow.build_library | QScrollArea | [covex_label_manager/qt_ui/window.py:142](../../covex_label_manager/qt_ui/window.py#L142) | Señales/registro JSON | Sin vínculo directo |
| S0677 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:143](../../covex_label_manager/qt_ui/window.py#L143) | Señales/registro JSON | Sin vínculo directo |
| S0678 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:144](../../covex_label_manager/qt_ui/window.py#L144) | self.toggle_advanced | 2 |
| S0679 | StudioWindow.build_library | QTableWidget | [covex_label_manager/qt_ui/window.py:146](../../covex_label_manager/qt_ui/window.py#L146) | Señales/registro JSON | Sin vínculo directo |
| S0680 | StudioWindow.build_library | connect | [covex_label_manager/qt_ui/window.py:157](../../covex_label_manager/qt_ui/window.py#L157) | self.selected | Sin vínculo directo |
| S0681 | StudioWindow.build_library | connect | [covex_label_manager/qt_ui/window.py:158](../../covex_label_manager/qt_ui/window.py#L158) | lambda *_: self.open_editor() | 32 |
| S0682 | StudioWindow.build_library | connect | [covex_label_manager/qt_ui/window.py:159](../../covex_label_manager/qt_ui/window.py#L159) | lambda r, c: self.favorite() if c == 0 else None | 3 |
| S0683 | StudioWindow.build_library | connect | [covex_label_manager/qt_ui/window.py:160](../../covex_label_manager/qt_ui/window.py#L160) | self.sort_table | Sin vínculo directo |
| S0684 | StudioWindow.build_library | connect | [covex_label_manager/qt_ui/window.py:160](../../covex_label_manager/qt_ui/window.py#L160) | self.adapt_columns | Sin vínculo directo |
| S0685 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:163](../../covex_label_manager/qt_ui/window.py#L163) | Señales/registro JSON | Sin vínculo directo |
| S0686 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:165](../../covex_label_manager/qt_ui/window.py#L165) | Señales/registro JSON | Sin vínculo directo |
| S0687 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:169](../../covex_label_manager/qt_ui/window.py#L169) | Señales/registro JSON | Sin vínculo directo |
| S0688 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:170](../../covex_label_manager/qt_ui/window.py#L170) | lambda: self.set_inspector(False) | Sin vínculo directo |
| S0689 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:171](../../covex_label_manager/qt_ui/window.py#L171) | Señales/registro JSON | Sin vínculo directo |
| S0690 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:172](../../covex_label_manager/qt_ui/window.py#L172) | Señales/registro JSON | Sin vínculo directo |
| S0691 | StudioWindow.build_library | Preview | [covex_label_manager/qt_ui/window.py:173](../../covex_label_manager/qt_ui/window.py#L173) | Señales/registro JSON | Sin vínculo directo |
| S0692 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:175](../../covex_label_manager/qt_ui/window.py#L175) | lambda: self.preview.zoom(1 / 1.2) | Sin vínculo directo |
| S0693 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:176](../../covex_label_manager/qt_ui/window.py#L176) | lambda: self.preview.zoom(1.2) | Sin vínculo directo |
| S0694 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:177](../../covex_label_manager/qt_ui/window.py#L177) | Señales/registro JSON | Sin vínculo directo |
| S0695 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:178](../../covex_label_manager/qt_ui/window.py#L178) | self.preview.fit | 1 |
| S0696 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:178](../../covex_label_manager/qt_ui/window.py#L178) | self.enlarge | Sin vínculo directo |
| S0697 | StudioWindow.build_library | QTabWidget | [covex_label_manager/qt_ui/window.py:183](../../covex_label_manager/qt_ui/window.py#L183) | Señales/registro JSON | Sin vínculo directo |
| S0698 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:184](../../covex_label_manager/qt_ui/window.py#L184) | Señales/registro JSON | Sin vínculo directo |
| S0699 | StudioWindow.build_library | QScrollArea | [covex_label_manager/qt_ui/window.py:186](../../covex_label_manager/qt_ui/window.py#L186) | Señales/registro JSON | Sin vínculo directo |
| S0700 | StudioWindow.build_library | addTab | [covex_label_manager/qt_ui/window.py:188](../../covex_label_manager/qt_ui/window.py#L188) | Señales/registro JSON | Sin vínculo directo |
| S0701 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:189](../../covex_label_manager/qt_ui/window.py#L189) | Señales/registro JSON | Sin vínculo directo |
| S0702 | StudioWindow.build_library | QComboBox | [covex_label_manager/qt_ui/window.py:190](../../covex_label_manager/qt_ui/window.py#L190) | Señales/registro JSON | Sin vínculo directo |
| S0703 | StudioWindow.build_library | connect | [covex_label_manager/qt_ui/window.py:190](../../covex_label_manager/qt_ui/window.py#L190) | self.revision_changed | Sin vínculo directo |
| S0704 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:191](../../covex_label_manager/qt_ui/window.py#L191) | Señales/registro JSON | Sin vínculo directo |
| S0705 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:192](../../covex_label_manager/qt_ui/window.py#L192) | lambda: self.show_access('document') | Sin vínculo directo |
| S0706 | StudioWindow.build_library | QScrollArea | [covex_label_manager/qt_ui/window.py:193](../../covex_label_manager/qt_ui/window.py#L193) | Señales/registro JSON | Sin vínculo directo |
| S0707 | StudioWindow.build_library | addTab | [covex_label_manager/qt_ui/window.py:194](../../covex_label_manager/qt_ui/window.py#L194) | Señales/registro JSON | Sin vínculo directo |
| S0708 | StudioWindow.build_library | label | [covex_label_manager/qt_ui/window.py:196](../../covex_label_manager/qt_ui/window.py#L196) | Señales/registro JSON | Sin vínculo directo |
| S0709 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:199](../../covex_label_manager/qt_ui/window.py#L199) | action | Sin vínculo directo |
| S0710 | StudioWindow.build_library | QScrollArea | [covex_label_manager/qt_ui/window.py:200](../../covex_label_manager/qt_ui/window.py#L200) | Señales/registro JSON | Sin vínculo directo |
| S0711 | StudioWindow.build_library | addTab | [covex_label_manager/qt_ui/window.py:201](../../covex_label_manager/qt_ui/window.py#L201) | Señales/registro JSON | Sin vínculo directo |
| S0712 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:202](../../covex_label_manager/qt_ui/window.py#L202) | self.favorite | 3 |
| S0713 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:203](../../covex_label_manager/qt_ui/window.py#L203) | self.open_editor | 32 |
| S0714 | StudioWindow.build_library | button | [covex_label_manager/qt_ui/window.py:204](../../covex_label_manager/qt_ui/window.py#L204) | lambda: self.navigate('emission') | 10 |
| S0715 | StudioWindow.build_library | QScrollArea | [covex_label_manager/qt_ui/window.py:205](../../covex_label_manager/qt_ui/window.py#L205) | Señales/registro JSON | Sin vínculo directo |
| S0716 | StudioWindow.columns_menu | addAction | [covex_label_manager/qt_ui/window.py:220](../../covex_label_manager/qt_ui/window.py#L220) | Señales/registro JSON | Sin vínculo directo |
| S0717 | StudioWindow.columns_menu | connect | [covex_label_manager/qt_ui/window.py:221](../../covex_label_manager/qt_ui/window.py#L221) | lambda checked, c=col: self.choose_column(c, checked) | Sin vínculo directo |
| S0718 | StudioWindow.columns_menu | addAction | [covex_label_manager/qt_ui/window.py:222](../../covex_label_manager/qt_ui/window.py#L222) | self.reset_columns | Sin vínculo directo |
| S0719 | StudioWindow.make_filter | QComboBox | [covex_label_manager/qt_ui/window.py:239](../../covex_label_manager/qt_ui/window.py#L239) | Señales/registro JSON | Sin vínculo directo |
| S0720 | StudioWindow.make_filter | addItem | [covex_label_manager/qt_ui/window.py:239](../../covex_label_manager/qt_ui/window.py#L239) | Señales/registro JSON | Sin vínculo directo |
| S0721 | StudioWindow.make_filter | addItem | [covex_label_manager/qt_ui/window.py:240](../../covex_label_manager/qt_ui/window.py#L240) | Señales/registro JSON | Sin vínculo directo |
| S0722 | StudioWindow.make_filter | connect | [covex_label_manager/qt_ui/window.py:241](../../covex_label_manager/qt_ui/window.py#L241) | self.refresh | 1 |
| S0723 | StudioWindow.selected | addItem | [covex_label_manager/qt_ui/window.py:297](../../covex_label_manager/qt_ui/window.py#L297) | Señales/registro JSON | Sin vínculo directo |
| S0724 | StudioWindow.revision_changed | information | [covex_label_manager/qt_ui/window.py:304](../../covex_label_manager/qt_ui/window.py#L304) | Señales/registro JSON | Sin vínculo directo |
| S0725 | StudioWindow.enlarge | QDialog | [covex_label_manager/qt_ui/window.py:310](../../covex_label_manager/qt_ui/window.py#L310) | Señales/registro JSON | Sin vínculo directo |
| S0726 | StudioWindow.enlarge | label | [covex_label_manager/qt_ui/window.py:311](../../covex_label_manager/qt_ui/window.py#L311) | Señales/registro JSON | 16 |
| S0727 | StudioWindow.enlarge | Preview | [covex_label_manager/qt_ui/window.py:312](../../covex_label_manager/qt_ui/window.py#L312) | Señales/registro JSON | Sin vínculo directo |
| S0728 | StudioWindow.enlarge | button | [covex_label_manager/qt_ui/window.py:314](../../covex_label_manager/qt_ui/window.py#L314) | lambda: view.zoom(1 / 1.2) | Sin vínculo directo |
| S0729 | StudioWindow.enlarge | button | [covex_label_manager/qt_ui/window.py:314](../../covex_label_manager/qt_ui/window.py#L314) | lambda: view.zoom(1.2) | Sin vínculo directo |
| S0730 | StudioWindow.enlarge | label | [covex_label_manager/qt_ui/window.py:315](../../covex_label_manager/qt_ui/window.py#L315) | Señales/registro JSON | Sin vínculo directo |
| S0731 | StudioWindow.enlarge | button | [covex_label_manager/qt_ui/window.py:316](../../covex_label_manager/qt_ui/window.py#L316) | view.fit | 1 |
| S0732 | StudioWindow.enlarge | button | [covex_label_manager/qt_ui/window.py:316](../../covex_label_manager/qt_ui/window.py#L316) | dialog.accept | Sin vínculo directo |
| S0733 | StudioWindow.enlarge | label | [covex_label_manager/qt_ui/window.py:317](../../covex_label_manager/qt_ui/window.py#L317) | Señales/registro JSON | Sin vínculo directo |
| S0734 | StudioWindow.actions_menu | addAction | [covex_label_manager/qt_ui/window.py:323](../../covex_label_manager/qt_ui/window.py#L323) | self.document_details | Sin vínculo directo |
| S0735 | StudioWindow.actions_menu | addAction | [covex_label_manager/qt_ui/window.py:327](../../covex_label_manager/qt_ui/window.py#L327) | lambda k=key: self.show_access(k) | Sin vínculo directo |
| S0736 | StudioWindow.document_details | QDialog | [covex_label_manager/qt_ui/window.py:331](../../covex_label_manager/qt_ui/window.py#L331) | Señales/registro JSON | Sin vínculo directo |
| S0737 | StudioWindow.document_details | label | [covex_label_manager/qt_ui/window.py:332](../../covex_label_manager/qt_ui/window.py#L332) | Señales/registro JSON | 16 |
| S0738 | StudioWindow.document_details | QLabel | [covex_label_manager/qt_ui/window.py:334](../../covex_label_manager/qt_ui/window.py#L334) | Señales/registro JSON | Sin vínculo directo |
| S0739 | StudioWindow.document_details | QScrollArea | [covex_label_manager/qt_ui/window.py:335](../../covex_label_manager/qt_ui/window.py#L335) | Señales/registro JSON | Sin vínculo directo |
| S0740 | StudioWindow.document_details | button | [covex_label_manager/qt_ui/window.py:336](../../covex_label_manager/qt_ui/window.py#L336) | dialog.accept | Sin vínculo directo |
| S0741 | StudioWindow.build_catalog | label | [covex_label_manager/qt_ui/window.py:379](../../covex_label_manager/qt_ui/window.py#L379) | Señales/registro JSON | Sin vínculo directo |
| S0742 | StudioWindow.build_catalog | label | [covex_label_manager/qt_ui/window.py:380](../../covex_label_manager/qt_ui/window.py#L380) | Señales/registro JSON | Sin vínculo directo |
| S0743 | StudioWindow.build_catalog | label | [covex_label_manager/qt_ui/window.py:381](../../covex_label_manager/qt_ui/window.py#L381) | Señales/registro JSON | Sin vínculo directo |
| S0744 | StudioWindow.build_catalog | button | [covex_label_manager/qt_ui/window.py:382](../../covex_label_manager/qt_ui/window.py#L382) | lambda: self.navigate('library') | 10 |
| S0745 | StudioWindow.build_editor | label | [covex_label_manager/qt_ui/window.py:387](../../covex_label_manager/qt_ui/window.py#L387) | Señales/registro JSON | Sin vínculo directo |
| S0746 | StudioWindow.build_editor | label | [covex_label_manager/qt_ui/window.py:388](../../covex_label_manager/qt_ui/window.py#L388) | Señales/registro JSON | Sin vínculo directo |
| S0747 | StudioWindow.build_editor | button | [covex_label_manager/qt_ui/window.py:389](../../covex_label_manager/qt_ui/window.py#L389) | self.editor_panels_menu | Sin vínculo directo |
| S0748 | StudioWindow.build_editor | button | [covex_label_manager/qt_ui/window.py:389](../../covex_label_manager/qt_ui/window.py#L389) | lambda: self.navigate('library') | 10 |
| S0749 | StudioWindow.build_editor | label | [covex_label_manager/qt_ui/window.py:391](../../covex_label_manager/qt_ui/window.py#L391) | Señales/registro JSON | Sin vínculo directo |
| S0750 | StudioWindow.build_editor | button | [covex_label_manager/qt_ui/window.py:391](../../covex_label_manager/qt_ui/window.py#L391) | lambda: self.canvas.fit() | 4 |
| S0751 | StudioWindow.build_editor | button | [covex_label_manager/qt_ui/window.py:392](../../covex_label_manager/qt_ui/window.py#L392) | lambda: self.canvas.zoom(1 / 1.2) | 3 |
| S0752 | StudioWindow.build_editor | button | [covex_label_manager/qt_ui/window.py:392](../../covex_label_manager/qt_ui/window.py#L392) | lambda: self.canvas.zoom(1.2) | 3 |
| S0753 | StudioWindow.build_editor | label | [covex_label_manager/qt_ui/window.py:393](../../covex_label_manager/qt_ui/window.py#L393) | Señales/registro JSON | Sin vínculo directo |
| S0754 | StudioWindow.build_editor | button | [covex_label_manager/qt_ui/window.py:394](../../covex_label_manager/qt_ui/window.py#L394) | self.toggle_editor_advanced | Sin vínculo directo |
| S0755 | StudioWindow.build_editor | button | [covex_label_manager/qt_ui/window.py:396](../../covex_label_manager/qt_ui/window.py#L396) | self.reset_layout | Sin vínculo directo |
| S0756 | StudioWindow.build_editor | QSplitter | [covex_label_manager/qt_ui/window.py:397](../../covex_label_manager/qt_ui/window.py#L397) | Señales/registro JSON | Sin vínculo directo |
| S0757 | StudioWindow.build_editor | label | [covex_label_manager/qt_ui/window.py:399](../../covex_label_manager/qt_ui/window.py#L399) | Señales/registro JSON | Sin vínculo directo |
| S0758 | StudioWindow.build_editor | label | [covex_label_manager/qt_ui/window.py:399](../../covex_label_manager/qt_ui/window.py#L399) | Señales/registro JSON | Sin vínculo directo |
| S0759 | StudioWindow.build_editor | QListWidget | [covex_label_manager/qt_ui/window.py:400](../../covex_label_manager/qt_ui/window.py#L400) | Señales/registro JSON | Sin vínculo directo |
| S0760 | StudioWindow.build_editor | connect | [covex_label_manager/qt_ui/window.py:400](../../covex_label_manager/qt_ui/window.py#L400) | self.select_field | Sin vínculo directo |
| S0761 | StudioWindow.build_editor | label | [covex_label_manager/qt_ui/window.py:401](../../covex_label_manager/qt_ui/window.py#L401) | Señales/registro JSON | Sin vínculo directo |
| S0762 | StudioWindow.build_editor | QScrollArea | [covex_label_manager/qt_ui/window.py:402](../../covex_label_manager/qt_ui/window.py#L402) | Señales/registro JSON | Sin vínculo directo |
| S0763 | StudioWindow.build_editor | Preview | [covex_label_manager/qt_ui/window.py:405](../../covex_label_manager/qt_ui/window.py#L405) | Señales/registro JSON | Sin vínculo directo |
| S0764 | StudioWindow.build_editor | connect | [covex_label_manager/qt_ui/window.py:406](../../covex_label_manager/qt_ui/window.py#L406) | self.scene_selection | Sin vínculo directo |
| S0765 | StudioWindow.build_editor | label | [covex_label_manager/qt_ui/window.py:408](../../covex_label_manager/qt_ui/window.py#L408) | Señales/registro JSON | Sin vínculo directo |
| S0766 | StudioWindow.build_editor | label | [covex_label_manager/qt_ui/window.py:408](../../covex_label_manager/qt_ui/window.py#L408) | Señales/registro JSON | Sin vínculo directo |
| S0767 | StudioWindow.build_editor | QLineEdit | [covex_label_manager/qt_ui/window.py:409](../../covex_label_manager/qt_ui/window.py#L409) | Señales/registro JSON | Sin vínculo directo |
| S0768 | StudioWindow.build_editor | connect | [covex_label_manager/qt_ui/window.py:409](../../covex_label_manager/qt_ui/window.py#L409) | self.change_name | Sin vínculo directo |
| S0769 | StudioWindow.build_editor | label | [covex_label_manager/qt_ui/window.py:410](../../covex_label_manager/qt_ui/window.py#L410) | Señales/registro JSON | Sin vínculo directo |
| S0770 | StudioWindow.build_editor | QDoubleSpinBox | [covex_label_manager/qt_ui/window.py:412](../../covex_label_manager/qt_ui/window.py#L412) | Señales/registro JSON | Sin vínculo directo |
| S0771 | StudioWindow.build_editor | connect | [covex_label_manager/qt_ui/window.py:414](../../covex_label_manager/qt_ui/window.py#L414) | self.change_geometry | Sin vínculo directo |
| S0772 | StudioWindow.build_editor | addRow | [covex_label_manager/qt_ui/window.py:414](../../covex_label_manager/qt_ui/window.py#L414) | Señales/registro JSON | Sin vínculo directo |
| S0773 | StudioWindow.build_editor | label | [covex_label_manager/qt_ui/window.py:415](../../covex_label_manager/qt_ui/window.py#L415) | Señales/registro JSON | Sin vínculo directo |
| S0774 | StudioWindow.build_editor | QDoubleSpinBox | [covex_label_manager/qt_ui/window.py:416](../../covex_label_manager/qt_ui/window.py#L416) | Señales/registro JSON | Sin vínculo directo |
| S0775 | StudioWindow.build_editor | connect | [covex_label_manager/qt_ui/window.py:416](../../covex_label_manager/qt_ui/window.py#L416) | self.change_flags | Sin vínculo directo |
| S0776 | StudioWindow.build_editor | QCheckBox | [covex_label_manager/qt_ui/window.py:418](../../covex_label_manager/qt_ui/window.py#L418) | Señales/registro JSON | Sin vínculo directo |
| S0777 | StudioWindow.build_editor | QCheckBox | [covex_label_manager/qt_ui/window.py:418](../../covex_label_manager/qt_ui/window.py#L418) | Señales/registro JSON | Sin vínculo directo |
| S0778 | StudioWindow.build_editor | QCheckBox | [covex_label_manager/qt_ui/window.py:418](../../covex_label_manager/qt_ui/window.py#L418) | Señales/registro JSON | Sin vínculo directo |
| S0779 | StudioWindow.build_editor | connect | [covex_label_manager/qt_ui/window.py:419](../../covex_label_manager/qt_ui/window.py#L419) | self.change_flags | Sin vínculo directo |
| S0780 | StudioWindow.build_editor | label | [covex_label_manager/qt_ui/window.py:420](../../covex_label_manager/qt_ui/window.py#L420) | Señales/registro JSON | Sin vínculo directo |
| S0781 | StudioWindow.build_editor | connect | [covex_label_manager/qt_ui/window.py:421](../../covex_label_manager/qt_ui/window.py#L421) | self.change_flags | Sin vínculo directo |
| S0782 | StudioWindow.build_editor | label | [covex_label_manager/qt_ui/window.py:422](../../covex_label_manager/qt_ui/window.py#L422) | Señales/registro JSON | Sin vínculo directo |
| S0783 | StudioWindow.build_editor | button | [covex_label_manager/qt_ui/window.py:424](../../covex_label_manager/qt_ui/window.py#L424) | lambda: self.show_access('document') | Sin vínculo directo |
| S0784 | StudioWindow.build_editor | label | [covex_label_manager/qt_ui/window.py:425](../../covex_label_manager/qt_ui/window.py#L425) | Señales/registro JSON | Sin vínculo directo |
| S0785 | StudioWindow.build_editor | label | [covex_label_manager/qt_ui/window.py:427](../../covex_label_manager/qt_ui/window.py#L427) | Señales/registro JSON | Sin vínculo directo |
| S0786 | StudioWindow.build_editor | QScrollArea | [covex_label_manager/qt_ui/window.py:428](../../covex_label_manager/qt_ui/window.py#L428) | Señales/registro JSON | Sin vínculo directo |
| S0787 | StudioWindow.build_editor | label | [covex_label_manager/qt_ui/window.py:431](../../covex_label_manager/qt_ui/window.py#L431) | Señales/registro JSON | Sin vínculo directo |
| S0788 | StudioWindow.editor_panels_menu | addAction | [covex_label_manager/qt_ui/window.py:436](../../covex_label_manager/qt_ui/window.py#L436) | Señales/registro JSON | Sin vínculo directo |
| S0789 | StudioWindow.editor_panels_menu | connect | [covex_label_manager/qt_ui/window.py:437](../../covex_label_manager/qt_ui/window.py#L437) | lambda checked, p=panel: p.setVisible(checked) | Sin vínculo directo |
| S0790 | StudioWindow.draw_editor | addItem | [covex_label_manager/qt_ui/window.py:462](../../covex_label_manager/qt_ui/window.py#L462) | Señales/registro JSON | Sin vínculo directo |
| S0791 | StudioWindow.draw_editor | addItem | [covex_label_manager/qt_ui/window.py:462](../../covex_label_manager/qt_ui/window.py#L462) | Señales/registro JSON | Sin vínculo directo |
| S0792 | WorkPanel.__init__ | QComboBox | [covex_label_manager/qt_ui/work.py:29](../../covex_label_manager/qt_ui/work.py#L29) | Señales/registro JSON | Sin vínculo directo |
| S0793 | WorkPanel.__init__ | button | [covex_label_manager/qt_ui/work.py:30](../../covex_label_manager/qt_ui/work.py#L30) | self.open_selected | Sin vínculo directo |
| S0794 | WorkPanel.__init__ | button | [covex_label_manager/qt_ui/work.py:32](../../covex_label_manager/qt_ui/work.py#L32) | window.new_emission_work | Sin vínculo directo |
| S0795 | WorkPanel.__init__ | button | [covex_label_manager/qt_ui/work.py:32](../../covex_label_manager/qt_ui/work.py#L32) | window.copy_emission_work | Sin vínculo directo |
| S0796 | WorkPanel.__init__ | button | [covex_label_manager/qt_ui/work.py:33](../../covex_label_manager/qt_ui/work.py#L33) | window.reload_emission_work | 1 |
| S0797 | WorkPanel.__init__ | label | [covex_label_manager/qt_ui/work.py:36](../../covex_label_manager/qt_ui/work.py#L36) | Señales/registro JSON | Sin vínculo directo |
| S0798 | WorkPanel.__init__ | label | [covex_label_manager/qt_ui/work.py:37](../../covex_label_manager/qt_ui/work.py#L37) | Señales/registro JSON | Sin vínculo directo |
| S0799 | WorkPanel.__init__ | QTabWidget | [covex_label_manager/qt_ui/work.py:38](../../covex_label_manager/qt_ui/work.py#L38) | Señales/registro JSON | Sin vínculo directo |
| S0800 | WorkPanel.__init__ | QScrollArea | [covex_label_manager/qt_ui/work.py:43](../../covex_label_manager/qt_ui/work.py#L43) | Señales/registro JSON | Sin vínculo directo |
| S0801 | WorkPanel.__init__ | addTab | [covex_label_manager/qt_ui/work.py:43](../../covex_label_manager/qt_ui/work.py#L43) | Señales/registro JSON | Sin vínculo directo |
| S0802 | WorkPanel.__init__ | QTableWidget | [covex_label_manager/qt_ui/work.py:44](../../covex_label_manager/qt_ui/work.py#L44) | Señales/registro JSON | Sin vínculo directo |
| S0803 | WorkPanel.__init__ | connect | [covex_label_manager/qt_ui/work.py:48](../../covex_label_manager/qt_ui/work.py#L48) | self.changed | 5 |
| S0804 | WorkPanel.__init__ | addTab | [covex_label_manager/qt_ui/work.py:48](../../covex_label_manager/qt_ui/work.py#L48) | Señales/registro JSON | 1 |
| S0805 | WorkPanel.__init__ | QAction | [covex_label_manager/qt_ui/work.py:51](../../covex_label_manager/qt_ui/work.py#L51) | Señales/registro JSON | 1 |
| S0806 | WorkPanel.__init__ | connect | [covex_label_manager/qt_ui/work.py:51](../../covex_label_manager/qt_ui/work.py#L51) | self.clear_container_row | Sin vínculo directo |
| S0807 | WorkPanel.__init__ | addAction | [covex_label_manager/qt_ui/work.py:51](../../covex_label_manager/qt_ui/work.py#L51) | Señales/registro JSON | Sin vínculo directo |
| S0808 | WorkPanel.__init__ | connect | [covex_label_manager/qt_ui/work.py:52](../../covex_label_manager/qt_ui/work.py#L52) | self.tab_changed | Sin vínculo directo |
| S0809 | WorkPanel.__init__ | button | [covex_label_manager/qt_ui/work.py:55](../../covex_label_manager/qt_ui/work.py#L55) | self.design_sheet | 2 |
| S0810 | WorkPanel.__init__ | addRow | [covex_label_manager/qt_ui/work.py:55](../../covex_label_manager/qt_ui/work.py#L55) | Señales/registro JSON | Sin vínculo directo |
| S0811 | WorkPanel.__init__ | button | [covex_label_manager/qt_ui/work.py:56](../../covex_label_manager/qt_ui/work.py#L56) | self.calibrate_printer | Sin vínculo directo |
| S0812 | WorkPanel.__init__ | addRow | [covex_label_manager/qt_ui/work.py:57](../../covex_label_manager/qt_ui/work.py#L57) | Señales/registro JSON | Sin vínculo directo |
| S0813 | WorkPanel.__init__ | QLineEdit | [covex_label_manager/qt_ui/work.py:59](../../covex_label_manager/qt_ui/work.py#L59) | Señales/registro JSON | Sin vínculo directo |
| S0814 | WorkPanel.__init__ | connect | [covex_label_manager/qt_ui/work.py:59](../../covex_label_manager/qt_ui/work.py#L59) | self.changed | 5 |
| S0815 | WorkPanel.__init__ | addRow | [covex_label_manager/qt_ui/work.py:59](../../covex_label_manager/qt_ui/work.py#L59) | Señales/registro JSON | Sin vínculo directo |
| S0816 | WorkPanel.__init__ | QLineEdit | [covex_label_manager/qt_ui/work.py:62](../../covex_label_manager/qt_ui/work.py#L62) | Señales/registro JSON | Sin vínculo directo |
| S0817 | WorkPanel.__init__ | connect | [covex_label_manager/qt_ui/work.py:62](../../covex_label_manager/qt_ui/work.py#L62) | self.changed | 5 |
| S0818 | WorkPanel.__init__ | addRow | [covex_label_manager/qt_ui/work.py:62](../../covex_label_manager/qt_ui/work.py#L62) | Señales/registro JSON | Sin vínculo directo |
| S0819 | WorkPanel.__init__ | QCheckBox | [covex_label_manager/qt_ui/work.py:63](../../covex_label_manager/qt_ui/work.py#L63) | Señales/registro JSON | Sin vínculo directo |
| S0820 | WorkPanel.__init__ | addRow | [covex_label_manager/qt_ui/work.py:63](../../covex_label_manager/qt_ui/work.py#L63) | Señales/registro JSON | Sin vínculo directo |
| S0821 | WorkPanel.__init__ | addRow | [covex_label_manager/qt_ui/work.py:64](../../covex_label_manager/qt_ui/work.py#L64) | Señales/registro JSON | 1 |
| S0822 | WorkPanel.__init__ | button | [covex_label_manager/qt_ui/work.py:64](../../covex_label_manager/qt_ui/work.py#L64) | self.restore_size | 1 |
| S0823 | WorkPanel.__init__ | connect | [covex_label_manager/qt_ui/work.py:65](../../covex_label_manager/qt_ui/work.py#L65) | lambda _, k=key: self.scale_size(k) | 1 |
| S0824 | WorkPanel.__init__ | QComboBox | [covex_label_manager/qt_ui/work.py:66](../../covex_label_manager/qt_ui/work.py#L66) | Señales/registro JSON | Sin vínculo directo |
| S0825 | WorkPanel.__init__ | addItem | [covex_label_manager/qt_ui/work.py:66](../../covex_label_manager/qt_ui/work.py#L66) | Señales/registro JSON | Sin vínculo directo |
| S0826 | WorkPanel.__init__ | addItem | [covex_label_manager/qt_ui/work.py:66](../../covex_label_manager/qt_ui/work.py#L66) | Señales/registro JSON | Sin vínculo directo |
| S0827 | WorkPanel.__init__ | connect | [covex_label_manager/qt_ui/work.py:66](../../covex_label_manager/qt_ui/work.py#L66) | self.changed | 5 |
| S0828 | WorkPanel.__init__ | addRow | [covex_label_manager/qt_ui/work.py:66](../../covex_label_manager/qt_ui/work.py#L66) | Señales/registro JSON | Sin vínculo directo |
| S0829 | WorkPanel.__init__ | QComboBox | [covex_label_manager/qt_ui/work.py:67](../../covex_label_manager/qt_ui/work.py#L67) | Señales/registro JSON | Sin vínculo directo |
| S0830 | WorkPanel.__init__ | addItem | [covex_label_manager/qt_ui/work.py:67](../../covex_label_manager/qt_ui/work.py#L67) | Señales/registro JSON | Sin vínculo directo |
| S0831 | WorkPanel.__init__ | addItem | [covex_label_manager/qt_ui/work.py:67](../../covex_label_manager/qt_ui/work.py#L67) | Señales/registro JSON | Sin vínculo directo |
| S0832 | WorkPanel.__init__ | connect | [covex_label_manager/qt_ui/work.py:67](../../covex_label_manager/qt_ui/work.py#L67) | self.changed | 5 |
| S0833 | WorkPanel.__init__ | addRow | [covex_label_manager/qt_ui/work.py:67](../../covex_label_manager/qt_ui/work.py#L67) | Señales/registro JSON | Sin vínculo directo |
| S0834 | WorkPanel.__init__ | QComboBox | [covex_label_manager/qt_ui/work.py:68](../../covex_label_manager/qt_ui/work.py#L68) | Señales/registro JSON | Sin vínculo directo |
| S0835 | WorkPanel.__init__ | addItem | [covex_label_manager/qt_ui/work.py:68](../../covex_label_manager/qt_ui/work.py#L68) | Señales/registro JSON | Sin vínculo directo |
| S0836 | WorkPanel.__init__ | addItem | [covex_label_manager/qt_ui/work.py:69](../../covex_label_manager/qt_ui/work.py#L69) | Señales/registro JSON | Sin vínculo directo |
| S0837 | WorkPanel.__init__ | addItem | [covex_label_manager/qt_ui/work.py:72](../../covex_label_manager/qt_ui/work.py#L72) | Señales/registro JSON | Sin vínculo directo |
| S0838 | WorkPanel.__init__ | connect | [covex_label_manager/qt_ui/work.py:73](../../covex_label_manager/qt_ui/work.py#L73) | self.apply_profile | 1 |
| S0839 | WorkPanel.__init__ | addRow | [covex_label_manager/qt_ui/work.py:73](../../covex_label_manager/qt_ui/work.py#L73) | Señales/registro JSON | 2 |
| S0840 | WorkPanel.__init__ | label | [covex_label_manager/qt_ui/work.py:75](../../covex_label_manager/qt_ui/work.py#L75) | Señales/registro JSON | 1 |
| S0841 | WorkPanel.__init__ | addRow | [covex_label_manager/qt_ui/work.py:79](../../covex_label_manager/qt_ui/work.py#L79) | Señales/registro JSON | 1 |
| S0842 | WorkPanel.__init__ | QScrollArea | [covex_label_manager/qt_ui/work.py:80](../../covex_label_manager/qt_ui/work.py#L80) | Señales/registro JSON | Sin vínculo directo |
| S0843 | WorkPanel.__init__ | addTab | [covex_label_manager/qt_ui/work.py:80](../../covex_label_manager/qt_ui/work.py#L80) | Señales/registro JSON | Sin vínculo directo |
| S0844 | WorkPanel.__init__ | QComboBox | [covex_label_manager/qt_ui/work.py:81](../../covex_label_manager/qt_ui/work.py#L81) | Señales/registro JSON | Sin vínculo directo |
| S0845 | WorkPanel.__init__ | addItem | [covex_label_manager/qt_ui/work.py:82](../../covex_label_manager/qt_ui/work.py#L82) | Señales/registro JSON | Sin vínculo directo |
| S0846 | WorkPanel.__init__ | connect | [covex_label_manager/qt_ui/work.py:83](../../covex_label_manager/qt_ui/work.py#L83) | self.changed | 5 |
| S0847 | WorkPanel.__init__ | addRow | [covex_label_manager/qt_ui/work.py:83](../../covex_label_manager/qt_ui/work.py#L83) | Señales/registro JSON | Sin vínculo directo |
| S0848 | WorkPanel.__init__ | QComboBox | [covex_label_manager/qt_ui/work.py:84](../../covex_label_manager/qt_ui/work.py#L84) | Señales/registro JSON | Sin vínculo directo |
| S0849 | WorkPanel.__init__ | addItem | [covex_label_manager/qt_ui/work.py:84](../../covex_label_manager/qt_ui/work.py#L84) | Señales/registro JSON | Sin vínculo directo |
| S0850 | WorkPanel.__init__ | addItem | [covex_label_manager/qt_ui/work.py:84](../../covex_label_manager/qt_ui/work.py#L84) | Señales/registro JSON | Sin vínculo directo |
| S0851 | WorkPanel.__init__ | connect | [covex_label_manager/qt_ui/work.py:84](../../covex_label_manager/qt_ui/work.py#L84) | self.changed | 5 |
| S0852 | WorkPanel.__init__ | addRow | [covex_label_manager/qt_ui/work.py:84](../../covex_label_manager/qt_ui/work.py#L84) | Señales/registro JSON | Sin vínculo directo |
| S0853 | WorkPanel.__init__ | QLineEdit | [covex_label_manager/qt_ui/work.py:87](../../covex_label_manager/qt_ui/work.py#L87) | Señales/registro JSON | Sin vínculo directo |
| S0854 | WorkPanel.__init__ | connect | [covex_label_manager/qt_ui/work.py:87](../../covex_label_manager/qt_ui/work.py#L87) | self.changed | 5 |
| S0855 | WorkPanel.__init__ | addRow | [covex_label_manager/qt_ui/work.py:87](../../covex_label_manager/qt_ui/work.py#L87) | Señales/registro JSON | Sin vínculo directo |
| S0856 | WorkPanel.__init__ | addTab | [covex_label_manager/qt_ui/work.py:88](../../covex_label_manager/qt_ui/work.py#L88) | Señales/registro JSON | Sin vínculo directo |
| S0857 | WorkPanel.__init__ | button | [covex_label_manager/qt_ui/work.py:89](../../covex_label_manager/qt_ui/work.py#L89) | window.flush_emission_work | 5 |
| S0858 | WorkPanel.__init__ | button | [covex_label_manager/qt_ui/work.py:90](../../covex_label_manager/qt_ui/work.py#L90) | window.recover_emission_work | 1 |
| S0859 | WorkPanel.__init__ | button | [covex_label_manager/qt_ui/work.py:91](../../covex_label_manager/qt_ui/work.py#L91) | window.proof_emission_work | 1 |
| S0860 | WorkPanel.__init__ | button | [covex_label_manager/qt_ui/work.py:91](../../covex_label_manager/qt_ui/work.py#L91) | window.issue_emission_work | 6 |
| S0861 | WorkPanel.__init__ | button | [covex_label_manager/qt_ui/work.py:92](../../covex_label_manager/qt_ui/work.py#L92) | window.refresh_work_binding | Sin vínculo directo |
| S0862 | WorkPanel.with_error | label | [covex_label_manager/qt_ui/work.py:111](../../covex_label_manager/qt_ui/work.py#L111) | Señales/registro JSON | Sin vínculo directo |
| S0863 | WorkPanel.refresh_choices | addItem | [covex_label_manager/qt_ui/work.py:139](../../covex_label_manager/qt_ui/work.py#L139) | Señales/registro JSON | Sin vínculo directo |
| S0864 | WorkPanel.display | QLineEdit | [covex_label_manager/qt_ui/work.py:162](../../covex_label_manager/qt_ui/work.py#L162) | Señales/registro JSON | 32 |
| S0865 | WorkPanel.display | connect | [covex_label_manager/qt_ui/work.py:168](../../covex_label_manager/qt_ui/work.py#L168) | self.changed | 5 |
| S0866 | WorkPanel.display | addRow | [covex_label_manager/qt_ui/work.py:168](../../covex_label_manager/qt_ui/work.py#L168) | Señales/registro JSON | Sin vínculo directo |
| S0867 | WorkPanel.calibrate_printer | warning | [covex_label_manager/qt_ui/work.py:230](../../covex_label_manager/qt_ui/work.py#L230) | Señales/registro JSON | Sin vínculo directo |
| S0868 | WorkPanel.design_sheet.proof | QDialog | [covex_label_manager/qt_ui/work.py:248](../../covex_label_manager/qt_ui/work.py#L248) | Señales/registro JSON | Sin vínculo directo |
| S0869 | WorkPanel.design_sheet.proof | PdfPane | [covex_label_manager/qt_ui/work.py:248](../../covex_label_manager/qt_ui/work.py#L248) | Señales/registro JSON | 2 |
| S0870 | WorkPanel.design_sheet.proof | QDialogButtonBox | [covex_label_manager/qt_ui/work.py:248](../../covex_label_manager/qt_ui/work.py#L248) | Señales/registro JSON | 23 |
| S0871 | WorkPanel.design_sheet.proof | connect | [covex_label_manager/qt_ui/work.py:248](../../covex_label_manager/qt_ui/work.py#L248) | dialog.reject | 2 |
| S0872 | WorkPanel.design_sheet | warning | [covex_label_manager/qt_ui/work.py:255](../../covex_label_manager/qt_ui/work.py#L255) | Señales/registro JSON | Sin vínculo directo |
| S0873 | EmissionWorkMixin.__init__ | connect | [covex_label_manager/qt_ui/work.py:272](../../covex_label_manager/qt_ui/work.py#L272) | self.flush_emission_work | 5 |
| S0874 | EmissionWorkMixin.__init__ | QDockWidget | [covex_label_manager/qt_ui/work.py:274](../../covex_label_manager/qt_ui/work.py#L274) | Señales/registro JSON | Sin vínculo directo |
| S0875 | EmissionWorkMixin.__init__ | button | [covex_label_manager/qt_ui/work.py:278](../../covex_label_manager/qt_ui/work.py#L278) | self.show_editor_work | 1 |
| S0876 | EmissionWorkMixin.build_emission_page | label | [covex_label_manager/qt_ui/work.py:286](../../covex_label_manager/qt_ui/work.py#L286) | Señales/registro JSON | Sin vínculo directo |
| S0877 | EmissionWorkMixin.work_action | action | [covex_label_manager/qt_ui/work.py:324](../../covex_label_manager/qt_ui/work.py#L324) | Señales/registro JSON | Sin vínculo directo |
| S0878 | EmissionWorkMixin.work_action | warning | [covex_label_manager/qt_ui/work.py:325](../../covex_label_manager/qt_ui/work.py#L325) | Señales/registro JSON | Sin vínculo directo |
| S0879 | EmissionWorkMixin.new_emission_work.create | getText | [covex_label_manager/qt_ui/work.py:336](../../covex_label_manager/qt_ui/work.py#L336) | Señales/registro JSON | Sin vínculo directo |
| S0880 | EmissionWorkMixin.reload_emission_work | question | [covex_label_manager/qt_ui/work.py:352](../../covex_label_manager/qt_ui/work.py#L352) | Señales/registro JSON | 23 |
| S0881 | EmissionWorkMixin.refresh_work_binding | question | [covex_label_manager/qt_ui/work.py:357](../../covex_label_manager/qt_ui/work.py#L357) | Señales/registro JSON | 23 |
| S0882 | EmissionWorkMixin.recover_emission_work | question | [covex_label_manager/qt_ui/work.py:366](../../covex_label_manager/qt_ui/work.py#L366) | Señales/registro JSON | 23 |
| S0883 | EmissionWorkMixin.closeEvent | warning | [covex_label_manager/qt_ui/work.py:411](../../covex_label_manager/qt_ui/work.py#L411) | Señales/registro JSON | Sin vínculo directo |
| S0884 | qt_confirmation | question | [covex_label_manager/migration_consent.py:11](../../covex_label_manager/migration_consent.py#L11) | Señales/registro JSON | 23 |
