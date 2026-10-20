"""Qt master reconciliation wizard: map columns, compare, filter, export. No writes."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog,QFileDialog,QMessageBox,QComboBox,QFormLayout,
    QHBoxLayout,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QWidget,
    QDialogButtonBox)
from .window import vbox,label,button
from .responsive import AdaptiveDialog as QDialog
from ..master_reconciliation import source_sheets,read_master,FIELDS,norm,checked_mapping


GUESSES={
 'name':('denominación','denominacion','nombre','etiqueta','nombre etiqueta','descripcion'),
 'version':('revisión','revision','versión','version','rev'),
 'code':('código','codigo','referencia','cod.'),
 'origin':('origen','propietario'),
 'customer':('cliente','customer'),
 'product':('producto','product'),
 'language':('idioma','language','lenguaje'),
 'state':('estado','situación','situacion','vigencia')
}

# Only user-facing strings change; exported report keeps stable machine codes.
RESULT_LABELS={
    'MATCHED':'Coincide',
    'MISSING_LABEL':'Etiqueta ausente en biblioteca',
    'MISSING_REVISION':'Revisión ausente en biblioteca',
    'METADATA_DIFFERENCE':'Datos distintos',
    'STATE_DIFFERENCE':'Estado documental diferente',
    'AMBIGUOUS':'Identidad ambigua',
    'DUPLICATE_MASTER_ROW':'Fila repetida en máster',
    'INVALID_MASTER_ROW':'Fila del máster no válida',
    'ONLY_IN_APP':'Solo en biblioteca',
}
ATTENTION_RESULTS=frozenset(RESULT_LABELS)-{'MATCHED','ONLY_IN_APP'}
EXPLANATIONS={
    'MATCHED':'La etiqueta, revisión y datos comparados coinciden.',
    'MISSING_LABEL':'La etiqueta no se ha localizado; puede faltar en la biblioteca o tener otra identidad.',
    'MISSING_REVISION':'La etiqueta existe, pero la revisión indicada no aparece en la biblioteca.',
    'METADATA_DIFFERENCE':'Revise los datos comparados; no se actualizarán automáticamente.',
    'STATE_DIFFERENCE':'Difieren los estados documentales. Verifique las evidencias antes de actuar.',
    'AMBIGUOUS':'Más de una etiqueta podría corresponder a esta fila. Hay que verificar su identidad.',
    'DUPLICATE_MASTER_ROW':'Esta identidad se repite en el libro seleccionado.',
    'INVALID_MASTER_ROW':'Revise la fila de origen; puede contener valores numéricos o fórmulas.',
    'ONLY_IN_APP':'No aparece en este listado. Un libro parcial no autoriza retirarla o borrarla.',
}

class MasterReconciliationDialog(QDialog):
    def __init__(self,parent,api,path):
        super().__init__(parent)
        self.api=api
        self.path=path
        self.report=None
        self._source_table=None
        self._displayed_records=[]
        self.setWindowTitle('Conciliar libro máster · Comparación sin cambios')
        self.resize(1060,730)
        layout=vbox(self,12,8)
        heading=label('Comparar el libro máster con la biblioteca','panelTitle')
        layout.addWidget(heading)
        notice=label(
            'Solo lectura · 1. Elija una hoja  2. Compruebe las columnas '
            '3. Compare y revise las diferencias. No importa, aprueba, '
            'retira ni elimina etiquetas.', 'subtle',
        )
        notice.setWordWrap(True)
        layout.addWidget(notice)
        sheetrow=QHBoxLayout()
        sheetrow.addWidget(label('Hoja o listado'))
        self.sheets=QComboBox()
        self.sheets.setObjectName('reconcileSheet')
        self.sheets.setAccessibleName('Hoja del libro máster para comparar')
        self.sheets.addItems(source_sheets(path))
        self.sheets.currentIndexChanged.connect(self.refresh_columns)
        sheetrow.addWidget(self.sheets,1)
        layout.addLayout(sheetrow)

        primary=QFormLayout()
        primary.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        self.inputs={}
        names={'name':'Denominación *','version':'Revisión *','code':'Código / referencia',
               'origin':'Origen','customer':'Cliente','product':'Producto',
               'language':'Idioma','state':'Estado documental'}
        self.optional_columns=QWidget()
        optional=QFormLayout(self.optional_columns)
        optional.setContentsMargins(8,4,8,4)
        optional.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        for key in FIELDS:
            combo=QComboBox()
            combo.setObjectName('reconcileColumn_'+key)
            combo.setMinimumWidth(180)
            combo.setAccessibleName('Columna de '+names[key])
            combo.currentIndexChanged.connect(self.mapping_changed)
            self.inputs[key]=combo
            (primary if key in ('name','version','code') else optional).addRow(names[key],combo)
        layout.addLayout(primary)
        self.show_columns=button('Más columnas para comparar ▸',lambda:None)
        self.show_columns.setCheckable(True)
        self.show_columns.toggled.connect(self.toggle_optional_columns)
        layout.addWidget(self.show_columns)
        layout.addWidget(self.optional_columns)
        self.optional_columns.hide()

        self.mapping_note=label('', 'subtle')
        self.mapping_note.setWordWrap(True)
        layout.addWidget(self.mapping_note)
        actions=QHBoxLayout()
        self.compare=button('Comparar sin modificar datos',self.run_compare,'primary')
        self.compare.setObjectName('reconcileCompare')
        actions.addWidget(self.compare)
        actions.addStretch()
        actions.addWidget(label('Mostrar'))
        self.filter=QComboBox()
        self.filter.setObjectName('reconcileFilter')
        self.filter.addItem('Todos los resultados','')
        self.filter.currentIndexChanged.connect(self.display_results)
        actions.addWidget(self.filter)
        layout.addLayout(actions)
        self.summary=label('Seleccione la hoja y confirme las columnas para comparar.','subtle')
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        self.table=QTableWidget(0,6)
        self.table.setObjectName('reconcileResults')
        self.table.setAccessibleName('Resultados de la conciliación · Solo lectura')
        self.table.setHorizontalHeaderLabels(
            ['Fila','Resultado','Denominación','Código','Revisión','Diferencias'],
        )
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.itemSelectionChanged.connect(self.show_selection_details)
        layout.addWidget(self.table,1)
        self.detail=label(
            'Seleccione una fila para ver qué significa el resultado y cómo revisarlo.',
            'subtle',
        )
        self.detail.setWordWrap(True)
        self.detail.setObjectName('reconcileExplanation')
        layout.addWidget(self.detail)
        footer=QHBoxLayout()
        self.export=button('Exportar informe ZIP…',self.export_result)
        self.export.setEnabled(False)
        self.export.setToolTip(
            'Incluye CSV, JSON y huellas de origen. Solo guarda un informe local; '
            'no modifica el catálogo ni aprueba documentación.',
        )
        footer.addWidget(self.export)
        footer.addStretch()
        close=QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close.rejected.connect(self.reject)
        footer.addWidget(close)
        layout.addLayout(footer)
        self.refresh_columns()

    def toggle_optional_columns(self,visible):
        self.optional_columns.setVisible(visible)
        self.show_columns.setText(
            'Ocultar columnas opcionales ▾' if visible
            else 'Más columnas para comparar ▸',
        )

    def mapping_changed(self,*_):
        self.report=None
        self.export.setEnabled(False)
        self.table.setRowCount(0)
        self._displayed_records=[]
        self.detail.setText('Compare para ver diferencias. No se realizan cambios en datos.')
        self.filter.blockSignals(True)
        self.filter.clear()
        self.filter.addItem('Todos los resultados','')
        self.filter.blockSignals(False)
        mapping={k:combo.currentData() for k,combo in self.inputs.items()}
        try:
            if self._source_table is None:
                raise ValueError('Seleccione una hoja válida.')
            checked_mapping(self._source_table,mapping)
            self.compare.setEnabled(True)
            self.mapping_note.setText(
                'Columnas obligatorias completas. Los campos adicionales '
                'solo se comparan cuando se han asociado a una columna.',
            )
        except ValueError as ex:
            self.compare.setEnabled(False)
            self.mapping_note.setText(
                'Revise las columnas: '+str(ex),
            )

    def refresh_columns(self,*_):
        self._source_table=None
        try:
            table=read_master(self.path,self.sheets.currentText())
        except Exception as ex:
            self.mapping_changed()
            self.summary.setText('No se ha podido leer la hoja: '+str(ex))
            return
        self._source_table=table
        for key,combo in self.inputs.items():
            combo.blockSignals(True)
            combo.clear()
            combo.addItem('— No comparar —',None)
            for col in table['headers']:
                combo.addItem(col,col)
            matches=[
                col for col in table['headers']
                if norm(col) in tuple(norm(v) for v in GUESSES[key])
            ]
            if len(matches)==1:
                combo.setCurrentIndex(combo.findData(matches[0]))
            combo.blockSignals(False)
        self.mapping_changed()
        self.summary.setText(
            f"{len(table['rows'])} filas encontradas. Revise al menos Denominación "
            "y Revisión antes de comparar. Los códigos numéricos de Excel deben "
            "guardarse como texto para conservar ceros.",
        )

    def run_compare(self):
        from ..master_reconciliation import reconcile
        mapping={k:combo.currentData() for k,combo in self.inputs.items()}
        try:
            self.report=reconcile(
                self.api,self.path,self.sheets.currentText(),mapping,
            )
        except Exception as ex:
            self.report=None
            self.export.setEnabled(False)
            QMessageBox.warning(self,'Conciliación no realizada',str(ex))
            return
        self.export.setEnabled(True)
        counts=self.report['summary']['counts']
        attention=sum(counts.get(status,0) for status in ATTENTION_RESULTS)
        self.filter.blockSignals(True)
        self.filter.clear()
        self.filter.addItem('Todos los resultados','')
        if attention:
            self.filter.addItem(f'Requieren revisión ({attention})','__ATTENTION__')
        for kind,count in counts.items():
            if count:
                self.filter.addItem(
                    f'{RESULT_LABELS.get(kind,kind)} ({count})',kind,
                )
        if self.report['only_in_app']:
            self.filter.addItem(
                f"Solo en biblioteca ({len(self.report['only_in_app'])})",
                'ONLY_IN_APP',
            )
        self.filter.blockSignals(False)
        self.display_results()

    def display_results(self,*_):
        if not self.report:
            return
        choice=self.filter.currentData() or ''
        records=self.report['results']
        if choice=='ONLY_IN_APP':
            records=[{
                'source_row':'—','status':'ONLY_IN_APP',
                'master':{
                    'name':r['name'],'code':r['code'],'version':r['revision'],
                },
                'differences':['Revisar si el listado máster es completo; no eliminar automáticamente'],
            } for r in self.report['only_in_app']]
        elif choice=='__ATTENTION__':
            records=[r for r in records if r['status'] in ATTENTION_RESULTS]
        elif choice:
            records=[r for r in records if r['status']==choice]
        shown=records[:1000]
        self._displayed_records=shown
        self.table.setRowCount(len(shown))
        for i,r in enumerate(shown):
            row=r['master']
            values=[
                str(r['source_row']),
                RESULT_LABELS.get(r['status'],r['status']),
                row['name'],row['code'],row['version'],
                ' | '.join(r['differences']),
            ]
            for j,value in enumerate(values):
                cell=QTableWidgetItem(str(value))
                cell.setToolTip(str(value))
                if j==1:
                    cell.setData(Qt.ItemDataRole.UserRole,r['status'])
                self.table.setItem(i,j,cell)
        summary=self.report['summary']
        coverage=summary['coverage_percent']
        ratio='No calculable' if coverage is None else f'{coverage:.2f}%'
        self.summary.setText(
            f"Coinciden {summary['matched']} de {summary['compared']} filas comparadas "
            f"· Cobertura orientativa: {ratio} "
            f"· {summary['extra_app_revisions']} revisiones solo en biblioteca "
            f"· Mostrando {len(shown)} de {len(records)}. "
            'El libro puede ser parcial; ningún resultado modifica datos.',
        )
        self.detail.setText(
            'Seleccione una fila para interpretar el resultado. '
            'Las discrepancias requieren revisión documental.',
        )

    def show_selection_details(self):
        current=self.table.currentRow()
        if current<0 or current>=len(self._displayed_records):
            return
        row=self._displayed_records[current]
        explanation=EXPLANATIONS.get(row['status'],'Comprobar el documento de origen.')
        diffs=' · '.join(row['differences'])
        self.detail.setText(
            RESULT_LABELS.get(row['status'],row['status'])+' · '+explanation+
            (' Detalle: '+diffs if diffs else ''),
        )

    def export_result(self):
        if not self.report:return
        target,_=QFileDialog.getSaveFileName(self,'Guardar informe R5C',
                    'Conciliacion_COVEX_R5C.zip','ZIP (*.zip)')
        if not target:return
        try:
            from ..master_reconciliation import export_report
            result=export_report(self.api,self.path,self.report,target)
            QMessageBox.information(self,'Informe verificado',
                f"ZIP creado con {result['rows']} filas del libro y evidencia SHA-256. "
                'No equivale a una aprobación documental ni a un backup.')
        except Exception as ex:QMessageBox.warning(self,'Exportación no realizada',str(ex))
