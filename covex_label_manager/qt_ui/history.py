"""Native history and controlled reprint UI using shared production services."""
import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QHBoxLayout,QVBoxLayout,QSplitter,QLineEdit,QTableWidget,
    QTableWidgetItem,QHeaderView,QAbstractItemView,QTabWidget,QPlainTextEdit,QDialog,QFormLayout,
    QDialogButtonBox,QCheckBox,QMessageBox,QPushButton,QComboBox,QScrollArea)
from .window import label,button,vbox,box
from .pdf_view import PdfPane


class HistoryMixin:
    def __init__(self,session):
        self.history_ready=False;self.history_id=None;self.history_report=None
        super().__init__(session)
        self.history_page=self.build_native_history();self.stack.addWidget(self.history_page);self.history_ready=True
        self.refresh_native_history()
    def build_native_history(self):
        page=QWidget();layout=vbox(page,20,10)
        row=QHBoxLayout();self.history_heading=label('Historial y reimpresión','title');row.addWidget(self.history_heading);row.addStretch();self.history_compact=QComboBox();self.history_compact.addItems(['Historial y detalle','PDF registrado']);self.history_compact.currentIndexChanged.connect(self.adapt_history_layout);self.history_compact.hide();row.addWidget(self.history_compact);row.addWidget(button('Actualizar',self.refresh_native_history));layout.addLayout(row)
        layout.addWidget(label('PDF registrados · La generación del PDF no confirma la impresión física.','subtle'))
        self.history_search=QLineEdit();self.history_search.setPlaceholderText('Buscar producto, revisión, variante, fecha, operador o motivo…');self.history_search.textChanged.connect(self.filter_native_history);layout.addWidget(self.history_search)
        split=QSplitter(Qt.Orientation.Horizontal);self.history_split=split
        left=box();ll=vbox(left,10,8)
        self.history_table=QTableWidget(0,8);self.history_table.setHorizontalHeaderLabels(['Emisión','Fecha','Producto / revisión','Variante','Etiquetas','Operador','Origen','Motivo'])
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows);self.history_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers);self.history_table.setAlternatingRowColors(True);self.history_table.verticalHeader().hide()
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents);self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.itemSelectionChanged.connect(self.select_native_issue);ll.addWidget(self.history_table,2)
        self.history_detail=QTabWidget();self.history_text={}
        for key,title in [('summary','Resumen documental'),('values','Datos de lote'),('containers','Recipientes'),('format','Formato y estado')]:
            text=QPlainTextEdit();text.setReadOnly(True);self.history_text[key]=text;self.history_detail.addTab(text,title)
        ll.addWidget(self.history_detail,1);left.setMinimumHeight(330);scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(left);scroll.setFrameShape(QScrollArea.Shape.NoFrame);split.addWidget(scroll);self.history_left=scroll
        right=box();rl=vbox(right,12,8);self.history_pdf=PdfPane(self.api);rl.addWidget(self.history_pdf,1);split.addWidget(right);self.history_right=right
        split.setSizes([690,760]);split.setStretchFactor(0,1);split.setStretchFactor(1,1);layout.addWidget(split,1)
        self.history_feedback=label('Seleccione una emisión para verificar su PDF y consultar sus datos.','subtle');self.history_feedback.setWordWrap(True);layout.addWidget(self.history_feedback)
        row=QHBoxLayout();row.addWidget(button('Verificar y ver PDF',self.preview_native_issue));row.addStretch();self.reprint_button=button('Reimpresión controlada…',self.native_reprint,'primary');row.addWidget(self.reprint_button);layout.addLayout(row)
        return page
    def navigate(self,key):
        if key=='history' and getattr(self,'history_ready',False):
            if not self.flush_emission_work() or not self.resolve_work():return
            self.work_dock.hide();self.refresh_native_history();self.stack.setCurrentWidget(self.history_page)
            for name,b in self.nav.items():b.setChecked(name==key)
            return
        super().navigate(key)
    def refresh_native_history(self):
        if not getattr(self,'history_ready',False):return
        table=self.history_table;selected=self.history_id;table.blockSignals(True)
        try:
            rows=self.api.issues();table.setRowCount(len(rows))
            for index,row in enumerate(rows):
                variant=self.api.variant(row['design_variant_id']) if row['design_variant_id'] else None
                values=[f"#{row['id']}",row['created_at'][:19],row['name']+' / '+row['version'],variant['code'] if variant else 'Heredada',
                    str(len(json.loads(row['selected_indices']))*row['copies_per_container']),row['operator'],f"#{row['source_issue_id']}" if row['source_issue_id'] else 'Original',row['reason'] or '—']
                for col,text in enumerate(values):
                    item=QTableWidgetItem(text);item.setToolTip(text);item.setData(Qt.ItemDataRole.UserRole,row['id']);table.setItem(index,col,item)
            self.filter_native_history()
            if selected:
                for r in range(table.rowCount()):
                    if table.item(r,0).data(Qt.ItemDataRole.UserRole)==selected:table.selectRow(r);break
        finally:table.blockSignals(False)
        self.select_native_issue()
    def filter_native_history(self,*_):
        text=self.history_search.text().casefold().strip()
        for row in range(self.history_table.rowCount()):
            self.history_table.setRowHidden(row,bool(text and text not in ' '.join(self.history_table.item(row,c).text().casefold() for c in range(self.history_table.columnCount()))))
    def select_native_issue(self):
        self.history_pdf.clear('Pulse Verificar y ver PDF para consultar el documento registrado.');self.history_report=None
        row=self.history_table.currentRow()
        if row<0:
            self.history_id=None;self.reprint_button.setEnabled(False)
            for t in self.history_text.values():t.clear()
            return
        self.history_id=self.history_table.item(row,0).data(Qt.ItemDataRole.UserRole)
        try:
            report=self.api.history.inspect(self.history_id);self.history_report=report;i=report['issue'];v=self.api.version(i['version_id']);variant=self.api.variant(i['design_variant_id']) if i['design_variant_id'] else None
            numbers=', '.join(map(str,json.loads(i['selected_indices'])))
            snapshot='Snapshot de diseño verificado' if report['snapshot'] else 'Histórico sin snapshot de diseño'
            text=f"Emisión #{i['id']} · {i['created_at'][:19]}\n{v['name']} · Revisión {v['version']}\nVariante: {variant['code']+' · '+variant['name'] if variant else 'Diseño heredado'}\nResponsable: {i['operator']}\n\n{snapshot}\nPDF: {'hash verificado' if i['pdf_sha256'] else 'sin hash registrado'}\nRecipientes del lote: {i['count_containers']}\nNúmeros originales: {numbers}\nCopias por recipiente: {i['copies_per_container']}\n\nReimpresión de: {i['source_issue_id'] or '—'}\nMotivo: {i['reason'] or '—'}\n\nPDF generado. Impresión física no confirmada."
            if report['snapshot']:
                approval=report['snapshot']['variant_approval'] or report['snapshot']['revision_approval'];text+='\n\nAprobación documental externa\n'+str(approval.get('approved_by') or '—')+' · '+str(approval.get('approval_ref') or '—')
            self.history_text['summary'].setPlainText(text)
            def fields(data):return '\n'.join(k+': '+str(value) for k,value in data.items()) or 'Sin datos adicionales.'
            self.history_text['values'].setPlainText(fields(json.loads(i['variables_json'])))
            self.history_text['containers'].setPlainText('\n\n'.join('Recipiente '+n+'\n'+fields(data) for n,data in json.loads(i['per_container_json'] or '{}').items()) or 'Todos los recipientes heredan los datos comunes del lote.')
            p=json.loads(i['profile_json']);status=json.loads(i['status_json'] or '{}')
            self.history_text['format'].setPlainText(f"Etiqueta: {p['width_mm']} × {p['height_mm']} mm\nA4: {'Horizontal' if p.get('orientation')=='landscape' else 'Vertical'}\nMargen: {p.get('margin_mm',0)} mm · Separación: {p.get('gap_mm',0)} mm\nCasilla inicial: {p.get('start_slot',1)}\nDesplazamiento: {p.get('offset_x_mm',0)} / {p.get('offset_y_mm',0)} mm\nImpresora de referencia: {p.get('printer_name') or '—'}\n\nEstado de material: "+{'ninguna':'Sin etiqueta de estado','sin_analizar':'Sin analizar','aprobado':'Aprobado','rechazado':'Rechazado'}.get(status.get('kind','ninguna'),status.get('kind',''))+'\n'+fields({k:v for k,v in status.items() if k not in ('kind','placement')}))
            self.history_feedback.setText('\n'.join(report['warnings']+([report['blocked']] if report['blocked'] else ['PDF disponible. Reimpresión sujeta a comprobación documental y motivo.'])))
            self.reprint_button.setEnabled(report['reprint_allowed'] and not self.legacy_process)
        except Exception as ex:
            self.history_feedback.setText(self.operator_error(ex));self.reprint_button.setEnabled(False)
            for t in self.history_text.values():t.clear()
    def preview_native_issue(self):
        if self.history_id is None:return False
        try:
            report=self.api.history.inspect(self.history_id)
            self.history_pdf.validator=lambda:self.api.history.inspect(report['issue']['id'])
            self.history_pdf.load(report['path'],'PDF histórico · #'+str(self.history_id),'PDF registrado · Impresión física no confirmada.');self.history_compact.setCurrentIndex(1);return True
        except Exception as ex:
            self.history_pdf.clear();self.history_feedback.setText(self.operator_error(ex));return False
    def native_reprint(self):
        if self.history_id is None or self.native_busy or self.legacy_process:return
        try:report=self.api.history.inspect(self.history_id)
        except Exception as ex:self.history_feedback.setText(self.operator_error(ex));return
        if not report['reprint_allowed']:self.history_feedback.setText(report['blocked']);return
        dialog=QDialog(self);dialog.setWindowTitle('Reimpresión controlada · #'+str(self.history_id));dialog.resize(650,460);layout=vbox(dialog)
        layout.addWidget(label('Se conservan diseño, datos, copias y números originales.','panelTitle'));form=QFormLayout()
        selection=QLineEdit(','.join(map(str,json.loads(report['issue']['selected_indices']))));reason=QLineEdit();slot=QLineEdit('1')
        form.addRow('Números originales (1-3,5)',selection);form.addRow('Motivo obligatorio',reason);form.addRow('Casilla inicial A4',slot);layout.addLayout(form)
        warning=label('\n'.join(report['warnings']),'subtle');warning.setWordWrap(True);layout.addWidget(warning)
        ack=QCheckBox('He revisado y acepto expresamente estas limitaciones del registro heredado.');ack.setVisible(bool(report['warnings']));layout.addWidget(ack)
        summary=label('','subtle');summary.setWordWrap(True);layout.addWidget(summary);error=label('');error.setObjectName('fieldError');error.setWordWrap(True);layout.addWidget(error)
        actions=QHBoxLayout();preview=button('PDF de prueba',lambda:execute(True));issue=button('Registrar reimpresión…',lambda:execute(False),'primary');actions.addWidget(preview);actions.addWidget(issue);layout.addLayout(actions)
        close=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);close.button(QDialogButtonBox.StandardButton.Close).setText('Cerrar');close.rejected.connect(dialog.reject);layout.addWidget(close)
        def validate(*_):
            try:
                _,indices,profile,plan=self.api.history.prepare(self.history_id,selection.text(),reason.text(),slot.text(),ack.isChecked(),report['token'])
                summary.setText(f"{len(indices)} números · {report['issue']['copies_per_container']} copias · {plan.count_physical} etiquetas · {plan.pages} hojas A4. Impresión física no confirmada.");error.clear();preview.setEnabled(True);issue.setEnabled(True);return True
            except Exception as ex:error.setText(self.operator_error(ex));preview.setEnabled(False);issue.setEnabled(False);return False
        def execute(proof):
            if not validate():return
            if not proof and QMessageBox.question(dialog,'Confirmar reimpresión',summary.text()+'\n\nRegistrar esta reimpresión con el motivo indicado?',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Yes:return
            preview.setEnabled(False);issue.setEnabled(False)
            try:
                with self.emission_busy():pk,path,result=self.api.history.reproduce(self.history_id,selection.text(),reason.text(),self.api.setting('operator'),start_slot=slot.text(),acknowledge_legacy=ack.isChecked(),expected_token=report['token'],proof=proof)
                if proof:
                    proof_dialog=QDialog(dialog);proof_dialog.setWindowTitle('PRUEBA de reimpresión · Sin registro');proof_dialog.resize(850,800);proof_layout=vbox(proof_dialog);pdf=PdfPane(self.api);proof_layout.addWidget(pdf,1);pdf.load(path,'PRUEBA de reimpresión','PRUEBA · Sin registro de emisión.');closer=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);closer.button(QDialogButtonBox.StandardButton.Close).setText('Cerrar');closer.rejected.connect(proof_dialog.reject);proof_layout.addWidget(closer);proof_dialog.exec()
                else:
                    dialog.accept();self.history_id=pk;self.refresh_native_history();self.preview_native_issue();self.history_feedback.setText(f'Reimpresión #{pk} registrada. Impresión física no confirmada.')
            except Exception as ex:error.setText(self.operator_error(ex))
            finally:preview.setEnabled(True);issue.setEnabled(True)
        for field in (selection,reason,slot):field.textChanged.connect(validate)
        ack.toggled.connect(validate);validate();dialog.exec()
    def set_mutations_enabled(self,enabled):
        super().set_mutations_enabled(enabled)
        if hasattr(self,'history_page'):self.history_page.setEnabled(enabled)
    def adapt_history_layout(self,*_):
        if not hasattr(self,'history_right'):return
        compact=self.height()<650;self.history_compact.setVisible(compact);self.history_pdf.compact(compact);self.history_heading.setStyleSheet('font-size:21px;' if compact else '')
        self.history_left.setVisible(not compact or self.history_compact.currentIndex()==0);self.history_right.setVisible(not compact or self.history_compact.currentIndex()==1)
    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,'history_split'):self.adapt_history_layout()
        if hasattr(self,'nav'):self.nav['history'].setToolTip('Historial · Consulta y reimpresión nativas Qt')
