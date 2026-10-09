"""Interactive visual proof, consuming existing LocalServices on fictional data."""
import copy
import json
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPixmap, QImage, QColor, QPen, QBrush, QKeySequence, QShortcut
from PySide6.QtWidgets import (QMainWindow, QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QComboBox, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QStackedWidget, QScrollArea, QDialog, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsItem, QListWidget, QDoubleSpinBox, QCheckBox, QFormLayout,
    QMenu, QMessageBox, QTabWidget, QGridLayout)
from .style import STYLE, icon

STATE={'APPROVED':('Vigente','#E2F2E9','#247454'),
       'PENDING':('Pendiente','#FFF0D7','#90651D'),'RETIRED':('Retirada','#F4E6E7','#986066')}
FILTERS={'category':'Categoría','origin':'Origen','state':'Estado','family':'Familia',
         'type':'Tipo','customer':'Cliente','country':'País','language':'Idioma',
         'version':'Versión','acquisition':'Incorporación'}

def label(text,kind=None):
    w=QLabel(text)
    if kind:w.setObjectName(kind)
    if kind in ('subtle','panelTitle'):w.setWordWrap(True)
    return w

def button(text,callback,kind=None,ico=None):
    w=QPushButton(text)
    if kind:w.setObjectName(kind)
    if ico:w.setIcon(icon(ico,'white' if kind=='primary' else '#607B80'))
    w.clicked.connect(callback);return w

def box(parent=None):
    w=QFrame(parent);w.setObjectName('surface');return w

def vbox(w,margins=18,spacing=12):
    lay=QVBoxLayout(w);lay.setContentsMargins(margins,margins,margins,margins);lay.setSpacing(spacing);return lay

def pixmap(image):
    im=image.convert('RGB');raw=im.tobytes()
    return QPixmap.fromImage(QImage(raw,im.width,im.height,im.width*3,QImage.Format.Format_RGB888).copy())

class Preview(QGraphicsView):
    def __init__(self):
        super().__init__();self.setScene(QGraphicsScene(self))
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter);self.auto_fit=True;self.fit_scale=1;self.zoom_label=None
    def set_image(self,im):
        self.scene().clear();self.scene().addPixmap(pixmap(im))
        self.scene().setSceneRect(self.scene().itemsBoundingRect().adjusted(-30,-30,30,30));self.fit()
    def fit(self):
        self.auto_fit=True;self.fitInView(self.sceneRect(),Qt.AspectRatioMode.KeepAspectRatio);self.fit_scale=self.transform().m11();self.update_zoom_label()
    def zoom(self,factor):
        scale=self.transform().m11()
        if .02<scale*factor<8:self.auto_fit=False;self.scale(factor,factor);self.update_zoom_label()
    def update_zoom_label(self):
        if self.zoom_label:self.zoom_label.setText(f"{self.transform().m11()/max(.001,self.fit_scale)*100:.0f}%")
    def wheelEvent(self,event):
        self.zoom(1.12 if event.angleDelta().y()>0 else 1/1.12);event.accept()
    def resizeEvent(self,event):
        super().resizeEvent(event)
        if self.auto_fit:self.fit()

class FieldItem(QGraphicsRectItem):
    def __init__(self,field,index,width,height,editable,changed):
        super().__init__(0,0,field['w']*width,field['h']*height)
        self.field=field;self.index=index;self.width=width;self.height=height;self.changed=changed
        self.setPen(QPen(QColor('#147D71'),1.5,Qt.PenStyle.DashLine))
        self.setBrush(QBrush(QColor(20,125,113,18)))
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable|
                      QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,editable and not field.get('locked'))
        self.setPos(field['x']*width,field['y']*height)
    def itemChange(self,change,value):
        if change==QGraphicsItem.GraphicsItemChange.ItemPositionChange and hasattr(self,'width'):
            value.setX(max(0,min(value.x(),self.width-self.rect().width())))
            value.setY(max(0,min(value.y(),self.height-self.rect().height())))
        if change==QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged and hasattr(self,'changed'):
            self.field['x']=self.pos().x()/self.width;self.field['y']=self.pos().y()/self.height
            self.changed(self.index)
        return super().itemChange(change,value)

class StudioProof(QMainWindow):
    def __init__(self,session):
        super().__init__();self.session=session;self.api=session.services
        self.rows=[];self.row=None;self.mode='all';self.filters={};self.nav={};self.loading=False
        self.layouts={};self.current_editor_id=None;self.field_items=[];self.column_preferences={};self.compact_mode=None
        self.setWindowTitle('COVEX Label Manager · Industrial Moderno · PRUEBA VISUAL')
        self.resize(1500,940);self.setMinimumSize(820,450);self.setStyleSheet(STYLE)
        root=QWidget();root.setObjectName('workspace');self.setCentralWidget(root)
        outer=vbox(root,0,0);header=QFrame();self.header=header;header.setObjectName('header');header.setFixedHeight(78)
        h=QHBoxLayout(header);h.setContentsMargins(26,12,26,12);h.setSpacing(12)
        brand=QVBoxLayout();self.brand_title=label('COVEX  /  LABEL MANAGER','brand');brand.addWidget(self.brand_title)
        brand.addWidget(label('Diseño y emisión de etiquetas','headerNote'));h.addLayout(brand);h.addSpacing(26)
        for key,text,ico in [('library','Biblioteca','library'),('editor','Editor','editor'),
                             ('emission','Emisión','print'),('history','Historial','clock'),('settings','Configuración','settings')]:
            b=button(text,lambda checked=False,k=key:self.navigate(k),'nav')
            b.setIcon(icon(ico,'#C9DCDD'));b.setCheckable(True);self.nav[key]=b;h.addWidget(b)
        h.addStretch();note=label('PRUEBA VISUAL\nSolo datos ficticios','headerNote');note.setAlignment(Qt.AlignmentFlag.AlignRight)
        h.addWidget(note);outer.addWidget(header)
        self.stack=QStackedWidget();outer.addWidget(self.stack,1)
        self.library=self.build_library();self.stack.addWidget(self.library)
        self.editor=self.build_editor();self.stack.addWidget(self.editor)
        self.catalog=self.build_catalog();self.stack.addWidget(self.catalog)
        self.statusBar().showMessage('Entorno de ejemplo temporal · No abre ni modifica los datos locales del usuario')
        self.search_shortcut=QShortcut(QKeySequence('Ctrl+K'),self)
        self.search_shortcut.activated.connect(self.quick_search)
        self.refresh();self.select_version(session.initial_id);self.navigate('library')

    def build_library(self):
        page=QWidget();lay=vbox(page,22,12)
        row=QHBoxLayout();title=QVBoxLayout();title.addWidget(label('Biblioteca de etiquetas','title'))
        self.library_subtitle=label('Busca, comprueba la revisión y abre tu etiqueta.','subtle');title.addWidget(self.library_subtitle)
        row.addLayout(title);row.addStretch()
        row.addWidget(button('Documentos y acciones',self.actions_menu,ico='plus'));lay.addLayout(row)
        searchrow=QHBoxLayout();self.search=QLineEdit();self.search.setObjectName('search')
        self.search.setPlaceholderText('Buscar por código, denominación, producto o cliente…')
        self.search.addAction(icon('search'),QLineEdit.ActionPosition.LeadingPosition)
        self.search.setToolTip('Ctrl+K abre y enfoca esta búsqueda');self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.refresh);searchrow.addWidget(self.search,1)
        searchrow.addWidget(label('Ctrl+K','subtle'));lay.addLayout(searchrow)
        frequent=QHBoxLayout()
        for key in ('category','origin','state'):
            frequent.addWidget(label(FILTERS[key],'subtle'));c=self.make_filter(key)
            c.setMinimumWidth(105);c.setMaximumWidth(210);frequent.addWidget(c,1)
        self.advanced_button=button('Más filtros',self.toggle_advanced,ico='filter');self.advanced_button.setCheckable(True)
        frequent.addWidget(self.advanced_button);frequent.addWidget(button('Limpiar',self.reset_filters));lay.addLayout(frequent)
        toolbar=QHBoxLayout();self.view_buttons={}
        for key,text,ico in [('all','Todas','library'),('favorites','Favoritas','star'),('recent','Recientes','clock')]:
            b=button(text,lambda checked=False,k=key:self.set_mode(k),'view',ico)
            b.setCheckable(True);b.setChecked(key=='all');self.view_buttons[key]=b;toolbar.addWidget(b)
        self.count=label('','subtle');toolbar.addWidget(self.count);toolbar.addStretch()
        toolbar.addWidget(button('Columnas',self.columns_menu))
        self.inspector_button=button('Inspector',self.toggle_inspector,ico='expand');self.inspector_button.setCheckable(True)
        self.inspector_button.setChecked(True);toolbar.addWidget(self.inspector_button);lay.addLayout(toolbar)
        self.library_split=QSplitter();self.library_split.setHandleWidth(10)
        self.advanced=box();self.advanced.setMinimumWidth(190);self.advanced.setMaximumWidth(235)
        ll=vbox(self.advanced,14,8);ll.addWidget(label('FILTROS AVANZADOS','section'))
        fields=QWidget();fields.setStyleSheet('background:white;');al=QGridLayout(fields);al.setContentsMargins(0,0,0,0);al.setSpacing(8)
        for i,key in enumerate(('family','type','customer','country','language','version','acquisition')):
            al.addWidget(label(FILTERS[key],'subtle'),i*2,0);al.addWidget(self.make_filter(key),i*2+1,0)
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(fields);scroll.setFrameShape(QFrame.Shape.NoFrame)
        ll.addWidget(scroll,1);ll.addWidget(label('Los filtros se combinan.','subtle'))
        ll.addWidget(button('Cerrar filtros',self.toggle_advanced));self.library_split.addWidget(self.advanced);self.advanced.hide()
        center=box();cl=vbox(center,0,0)
        self.table=QTableWidget(0,9);self.table.setHorizontalHeaderLabels(['','CÓDIGO','DENOMINACIÓN','TIPO','VERSIÓN','ORIGEN','CLIENTE','PAÍS','ESTADO'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False);self.table.setWordWrap(False);self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(46);self.table.setMinimumHeight(110)
        header=self.table.horizontalHeader();header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        for c,width in enumerate([38,102,260,105,82,95,115,90,105]):self.table.setColumnWidth(c,width)
        header.setSectionResizeMode(2,QHeaderView.ResizeMode.Stretch)
        header.setMinimumSectionSize(35)
        for position,column in enumerate((0,1,2,4,8,5,6,3,7)):header.moveSection(header.visualIndex(column),position)
        self.table.itemSelectionChanged.connect(self.selected)
        self.table.cellDoubleClicked.connect(lambda *_:self.open_editor())
        self.table.cellClicked.connect(lambda r,c:self.favorite() if c==0 else None)
        header.sectionClicked.connect(self.sort_table);self.library_split.splitterMoved.connect(self.adapt_columns)
        cl.addWidget(self.table,1)
        self.selection_help=QWidget();help_l=vbox(self.selection_help,20,10)
        help_l.addWidget(label('CONTINUAR CON LA SELECCIÓN','section'))
        self.selection_summary=label('','panelTitle');help_l.addWidget(self.selection_summary)
        help_l.addWidget(label('1  Comprueba el estado y la revisión en el inspector.\n2  Amplía el documento para revisar los detalles.\n3  Abre en Editor para continuar. La aprobación se controla por separado.','subtle'))
        a=QHBoxLayout();a.addWidget(button('Ver inspector',lambda:self.set_inspector(True),ico='expand'))
        a.addWidget(button('Abrir en Editor',self.open_editor,'primary','arrow'));a.addStretch();help_l.addLayout(a)
        cl.addWidget(self.selection_help);self.selection_help.hide()
        hint=label('Doble clic: Editor · Estrella: favoritas · Columnas: metadatos adicionales','subtle')
        hint.setContentsMargins(14,10,14,10);cl.addWidget(hint);self.library_split.addWidget(center)
        self.inspector=box();self.inspector.setMinimumWidth(310);self.inspector.setMaximumWidth(380)
        il=vbox(self.inspector,16,8)
        titlebar=QHBoxLayout();titlebar.addWidget(label('INSPECTOR','section'));titlebar.addStretch()
        titlebar.addWidget(button('Ocultar',lambda:self.set_inspector(False)));il.addLayout(titlebar)
        self.doc_title=label('','panelTitle');il.addWidget(self.doc_title)
        self.badge=label('','badge');il.addWidget(self.badge,0,Qt.AlignmentFlag.AlignLeft)
        self.preview=Preview();self.preview.setMinimumHeight(145);self.preview.setMaximumHeight(220);il.addWidget(self.preview,1)
        controls=QHBoxLayout();controls.setSpacing(5)
        controls.addWidget(button('−',lambda:self.preview.zoom(1/1.2)))
        controls.addWidget(button('+',lambda:self.preview.zoom(1.2)))
        self.preview.zoom_label=label('100%','subtle');controls.addWidget(self.preview.zoom_label)
        controls.addWidget(button('Ajustar',self.preview.fit));controls.addWidget(button('Ampliar',self.enlarge))
        for i in range(controls.count()):
            widget=controls.itemAt(i).widget()
            if isinstance(widget,QPushButton):widget.setStyleSheet('padding:7px 8px;')
        il.addLayout(controls)
        self.inspector_tabs=QTabWidget();il.addWidget(self.inspector_tabs,1)
        info=QWidget();info_l=vbox(info,10,8);self.meta=label('');self.meta.setWordWrap(True)
        self.meta.setStyleSheet('background:white;');self.meta.setTextFormat(Qt.TextFormat.PlainText);self.meta.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        info_scroll=QScrollArea();info_scroll.setWidgetResizable(True);info_scroll.setWidget(self.meta)
        info_scroll.setStyleSheet('QScrollArea {background:white;border:none;}');info_scroll.setFrameShape(QFrame.Shape.NoFrame);info_l.addWidget(info_scroll)
        self.inspector_tabs.addTab(info,'Información')
        versions=QWidget();vl=vbox(versions,10,8);vl.addWidget(label('REVISIÓN DOCUMENTAL','section'))
        self.revision=QComboBox();self.revision.currentIndexChanged.connect(self.revision_changed);vl.addWidget(self.revision)
        self.doc_note=label('','subtle');vl.addWidget(self.doc_note)
        vl.addWidget(button('Revisiones y variantes',lambda:self.show_access('document')));vl.addStretch()
        self.inspector_tabs.addTab(versions,'Versiones')
        documents=QWidget();dl=vbox(documents,10,8)
        dl.addWidget(label('PDF ficticio · Fuente local temporal','subtle'))
        for text,action in [('Ficha completa y referencias',self.document_details),
            ('Documentos y aprobación externa',lambda:self.show_access('document')),
            ('Importaciones PDF / Word',lambda:self.show_access('import'))]:dl.addWidget(button(text,action))
        dl.addStretch();self.inspector_tabs.addTab(documents,'Documentos')
        actions=QHBoxLayout();self.favorite_button=button('Favorita',self.favorite,ico='star');actions.addWidget(self.favorite_button)
        actions.addWidget(button('Abrir en Editor',self.open_editor,'primary','arrow'));il.addLayout(actions)
        il.addWidget(button('Ver accesos de emisión',lambda:self.navigate('emission'),ico='print'))
        self.inspector_panel=QScrollArea();self.inspector_panel.setWidgetResizable(True)
        self.inspector_panel.setWidget(self.inspector);self.inspector_panel.setFrameShape(QFrame.Shape.NoFrame)
        self.inspector_panel.setMinimumWidth(330);self.inspector_panel.setMaximumWidth(380);self.inspector.setMinimumHeight(535)
        self.library_split.addWidget(self.inspector_panel);self.library_split.setSizes([220,920,330])
        self.library_split.setStretchFactor(1,1);lay.addWidget(self.library_split,1)
        return page

    def set_inspector(self,visible):
        self.inspector_panel.setVisible(visible);self.inspector_button.setChecked(visible)
        QTimer.singleShot(0,self.adapt_columns)
    def toggle_inspector(self):
        self.set_inspector(self.inspector_button.isChecked())
    def columns_menu(self):
        menu=QMenu(self)
        for col,title in [(3,'Tipo'),(5,'Origen'),(6,'Cliente'),(7,'País')]:
            action=menu.addAction(title);action.setCheckable(True);action.setChecked(not self.table.isColumnHidden(col))
            action.triggered.connect(lambda checked,c=col:self.choose_column(c,checked))
        menu.addSeparator();menu.addAction('Restablecer adaptación automática',self.reset_columns)
        menu.exec(self.cursor().pos())
    def choose_column(self,column,visible):
        self.column_preferences[column]=visible;self.adapt_columns()
    def reset_columns(self):
        self.column_preferences.clear();self.adapt_columns()
    def adapt_columns(self,*_):
        if not hasattr(self,'table'):return
        width=self.table.viewport().width()
        for col,threshold in [(3,1400),(5,950),(6,1200),(7,1500)]:
            self.table.setColumnHidden(col,not self.column_preferences.get(col,width>=threshold))
        # Core columns never disappear. User-selected extras may scroll horizontally.
        for col in (0,1,2,4,8):self.table.setColumnHidden(col,False)
        self.table.setColumnWidth(1,96 if width<750 else 108)
        self.table.setColumnWidth(4,78);self.table.setColumnWidth(8,102)

    def make_filter(self,key):
        c=QComboBox();c.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon);c.setMinimumContentsLength(8);c.addItem('Todos','')
        for value in self.api.library.facets()[key]:c.addItem(STATE[value][0] if key=='state' else value,value)
        c.currentIndexChanged.connect(self.refresh);self.filters[key]=c
        c.setEnabled(c.count()>1);return c
    def toggle_advanced(self):
        self.advanced.setVisible(not self.advanced.isVisible());self.advanced_button.setChecked(self.advanced.isVisible());QTimer.singleShot(0,self.adapt_columns)
    def set_mode(self,mode):
        self.mode=mode
        for key,b in self.view_buttons.items():b.setChecked(key==mode)
        self.refresh()
    def reset_filters(self):
        self.loading=True;self.search.clear()
        for c in self.filters.values():c.setCurrentIndex(0)
        self.loading=False;self.set_mode('all')
    def refresh(self,*_):
        if self.loading:return
        selected=self.row['version_id'] if self.row else None
        self.rows=self.api.library.entries(self.search.text(),{k:c.currentData() for k,c in self.filters.items()},self.mode)
        if self.mode!='recent':self.rows.sort(key=lambda r:(r['code'], -r['version_id']))
        self.table.blockSignals(True);self.table.setRowCount(len(self.rows))
        for i,r in enumerate(self.rows):
            values=['★' if r['favorite'] else '☆',r['code'],r['name'],r.get('type',''),r['version'],r['origin'],r['customer'],r.get('country',''),STATE[r['state']][0]]
            for c,value in enumerate(values):
                item=QTableWidgetItem(value);item.setData(Qt.ItemDataRole.UserRole,r['version_id'])
                item.setToolTip(value);self.table.setItem(i,c,item)
            self.table.item(i,8).setForeground(QColor(STATE[r['state']][2]))
        self.table.blockSignals(False);self.count.setText(f'{len(self.rows)} revisiones')
        few=0<len(self.rows)<=5;self.selection_help.setVisible(few)
        self.table.setMaximumHeight(max(170,60+46*len(self.rows)) if few else 16777215)
        active=sum(bool(c.currentData()) for k,c in self.filters.items() if k not in ('category','origin','state'))
        self.advanced_button.setText('Más filtros'+(f' ({active})' if active else ''))
        QTimer.singleShot(0,self.adapt_columns)
        if self.rows:self.select_version(selected if any(r['version_id']==selected for r in self.rows) else self.rows[0]['version_id'])
        else:self.row=None;self.inspector.setEnabled(False);self.preview.scene().clear();self.doc_title.setText('Sin resultados');self.meta.clear();self.revision.clear();self.doc_note.clear();self.badge.clear()
    def sort_table(self,column):
        self.table.sortItems(column,Qt.SortOrder.AscendingOrder)
    def select_version(self,vid):
        for i in range(self.table.rowCount()):
            if self.table.item(i,0).data(Qt.ItemDataRole.UserRole)==vid:
                self.table.selectRow(i);self.selected();return True
        return False
    def selected(self):
        i=self.table.currentRow()
        if i<0 or not self.table.item(i,0):return
        vid=self.table.item(i,0).data(Qt.ItemDataRole.UserRole)
        self.row=next(r for r in self.rows if r['version_id']==vid)
        self.inspector.setEnabled(True);self.doc_title.setText(self.row['name'])
        text,bg,fg=STATE[self.row['state']];self.badge.setText(text)
        self.badge.setStyleSheet(f'background:{bg};color:{fg};')
        v=dict(self.api.version(vid));self.preview.set_image(self.api.thumbnail(v,width_px=850))
        metadata=[('Código',self.row['code']),('Versión',self.row['version']),
                  ('Dimensiones',f"{v['base_w_mm']:g} × {v['base_h_mm']:g} mm"),('Producto',self.row.get('product',''))]
        metadata += [(title,self.row.get(key,'')) for key,title in FILTERS.items() if key not in ('state','version')]
        self.meta.setText('\n\n'.join(f'{title}   {value or "Sin dato"}' for title,value in metadata))
        self.selection_summary.setText(f"{self.row['code']} · {self.row['name']} · {self.row['version']}")
        self.revision.blockSignals(True);self.revision.clear()
        for r in self.api.versions(self.row['id']):
            self.revision.addItem(f"Revisión {r['version']}  ·  {STATE[r['state']][0]}",r['id'])
        self.revision.setCurrentIndex(self.revision.findData(vid));self.revision.blockSignals(False)
        self.doc_note.setText('Aprobación ficticia de demostración.' if v['state']=='APPROVED' else 'Pendiente de aprobación.\nConsultar y editar no autoriza la emisión.')
        self.favorite_button.setText('Favorita' if self.row['favorite'] else 'Favorita')
    def revision_changed(self,index):
        vid=self.revision.itemData(index)
        if vid is not None and not self.select_version(vid):
            QMessageBox.information(self,'Revisión fuera del filtro','Esta revisión está fuera del resultado actual. Ajusta los filtros para seleccionarla.')
            self.revision.blockSignals(True);self.revision.setCurrentIndex(self.revision.findData(self.row['version_id']));self.revision.blockSignals(False)
    def favorite(self):
        if self.row:self.api.library.favorite(self.row);self.refresh()
    def enlarge(self):
        if not self.row:return
        dialog=QDialog(self);dialog.setWindowTitle('Vista ampliada · Documento ficticio');dialog.resize(1000,740)
        lay=vbox(dialog);lay.addWidget(label(self.row['name'],'panelTitle'))
        view=Preview();view.set_image(self.api.thumbnail(self.api.version(self.row['version_id']),width_px=1800))
        lay.addWidget(view,1);controls=QHBoxLayout()
        controls.addWidget(button('−',lambda:view.zoom(1/1.2)));controls.addWidget(button('+',lambda:view.zoom(1.2)))
        controls.addWidget(button('Ajustar documento',view.fit));controls.addStretch();controls.addWidget(button('Cerrar',dialog.accept))
        lay.addLayout(controls);lay.addWidget(label('Proporciones conservadas · Zoom: rueda · Arrastra para desplazar el documento','subtle'))
        QTimer.singleShot(0,view.fit);dialog.exec()
    def quick_search(self):
        self.navigate('library');self.search.setFocus();self.search.selectAll()
    def actions_menu(self):
        menu=QMenu(self)
        menu.addAction('Ficha completa del ejemplo',self.document_details)
        for title,key in [('Ficha y documentos de ejemplo','document'),('Importar PDF / Word','import'),
                          ('Importar carpeta','import'),('Nueva revisión y variantes','document'),
                          ('Registrar aprobación externa','document'),('Metadatos','document'),('Comparar revisiones','document')]:
            menu.addAction(title,lambda k=key:self.show_access(k))
        menu.exec(self.cursor().pos())
    def document_details(self):
        if not self.row:return
        dialog=QDialog(self);dialog.setWindowTitle('Ficha documental · Datos ficticios');dialog.resize(680,540)
        lay=vbox(dialog);lay.addWidget(label(self.row['name'],'panelTitle'))
        text='\n'.join(f'{key}: {value}' for key,value in self.row.items() if value is not None)
        info=QLabel(text);info.setWordWrap(True);info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(info);lay.addWidget(scroll,1)
        lay.addWidget(button('Cerrar',dialog.accept));dialog.exec()
    def show_access(self,key):
        self.navigate(key)
    def navigate(self,key):
        for name,b in self.nav.items():b.setChecked(name==key)
        if key=='library':self.stack.setCurrentWidget(self.library)
        elif key=='editor':
            if self.current_editor_id is None:self.open_editor()
            else:self.stack.setCurrentWidget(self.editor)
        else:
            self.catalog_title.setText({'emission':'Emisión e impresión','history':'Historial y trazabilidad',
                'settings':'Configuración y datos','document':'Documentos y revisiones','import':'Importaciones'}.get(key,'Funciones actuales'))
            self.catalog_text.setText('Este módulo no se ha migrado en la prueba visual. Sus funciones siguen disponibles en la aplicación Tkinter actual. La matriz de conservación identifica cada acceso y su destino previsto.')
            self.stack.setCurrentWidget(self.catalog)
    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,'table'):
            compact=event.size().width()<1200
            short=event.size().height()<650
            self.header.setFixedHeight(58 if short else 78)
            self.library_subtitle.setVisible(not short)
            self.library.layout().setContentsMargins(*([14]*4 if short else [22]*4))
            self.library.layout().setSpacing(8 if short else 12)
            self.search.setStyleSheet('padding:8px 12px;font-size:14px;' if short else '')
            if self.compact_mode!=compact:
                self.compact_mode=compact
                self.set_inspector(not compact)
                if compact and self.advanced.isVisible():self.toggle_advanced()
            self.brand_title.setText('COVEX / LABELS' if event.size().width()<1300 else 'COVEX  /  LABEL MANAGER')
            for key,title in [('history','Historial'),('settings','Configuración')]:
                self.nav[key].setText('' if compact else title);self.nav[key].setToolTip(title)
            if hasattr(self,'editor_advanced_button'):
                self.editor_note.setVisible(not short)
                self.editor_title.setStyleSheet('font-size:21px;' if short else '')
                self.editor.layout().setContentsMargins(*([14]*4 if short else [24]*4))
                self.editor.layout().setSpacing(8 if short else 14)
                if event.size().width()<1100:self.tools_scroll.hide()
                elif event.oldSize().width()<1100:self.tools_scroll.show()
                self.editor_advanced_button.setText('Avanzadas' if compact else 'Herramientas avanzadas')
                self.editor_fit_button.setText('Ajustar' if compact else 'Ajustar a pantalla')
                self.editor_reset_button.setText('Restablecer' if compact else 'Restablecer ejemplo')
            QTimer.singleShot(0,self.adapt_columns)
    def build_catalog(self):
        page=QWidget();lay=vbox(page,32);self.catalog_title=label('Funciones actuales','title');lay.addWidget(self.catalog_title)
        self.catalog_text=label('');self.catalog_text.setWordWrap(True);lay.addWidget(self.catalog_text)
        info=label('Conservación obligatoria\n\n• Maestros, revisiones, variantes y aprobación documental externa\n• Importación PDF / Word / carpeta, metadatos y catálogo CM\n• Campos, recorte, anclaje Word, reajuste avanzado y espacio de estado\n• Emisión A4, numeración, pesos/lotes por envase y etiquetas de estado\n• Seguridad y preflight, perfiles, calibración y reimpresión controlada\n• Historial, integridad, auditoría local, configuraciones y backups\n\nLa prueba no emite, importa ni aprueba documentos de producción.','panelTitle')
        info.setWordWrap(True);lay.addWidget(info);lay.addWidget(button('Volver a Biblioteca',lambda:self.navigate('library')));lay.addStretch()
        return page

    def build_editor(self):
        page=QWidget();lay=vbox(page,24,14)
        head=QHBoxLayout();titles=QVBoxLayout();self.editor_title=label('Editor de ejemplo','title');titles.addWidget(self.editor_title)
        self.editor_note=label('Organización visual del futuro Editor · Funciones avanzadas aún no migradas','subtle');titles.addWidget(self.editor_note)
        head.addLayout(titles);head.addStretch();head.addWidget(button('Paneles',self.editor_panels_menu));head.addWidget(button('Biblioteca',lambda:self.navigate('library'),ico='library'));lay.addLayout(head)
        toolbar=box();tl=QHBoxLayout(toolbar);tl.setContentsMargins(12,8,12,8)
        tl.addWidget(label('LIENZO','section'));self.editor_fit_button=button('Ajustar a pantalla',lambda:self.canvas.fit(),ico='expand');tl.addWidget(self.editor_fit_button)
        tl.addWidget(button('−',lambda:self.canvas.zoom(1/1.2)));tl.addWidget(button('+',lambda:self.canvas.zoom(1.2)))
        self.canvas_zoom_label=label('100%','subtle');tl.addWidget(self.canvas_zoom_label)
        tl.addStretch();self.editor_advanced_button=button('Herramientas avanzadas',self.toggle_editor_advanced,ico='settings')
        self.editor_advanced_button.setCheckable(True);tl.addWidget(self.editor_advanced_button)
        self.editor_reset_button=button('Restablecer ejemplo',self.reset_layout);tl.addWidget(self.editor_reset_button);lay.addWidget(toolbar)
        split=QSplitter();split.setHandleWidth(14)
        tools=box();self.editor_tools=tools;tools.setMinimumWidth(170);tools.setMaximumWidth(230);ll=vbox(tools,16)
        ll.addWidget(label('ELEMENTOS','section'));ll.addWidget(label('Campos variables','panelTitle'))
        self.field_list=QListWidget();self.field_list.currentRowChanged.connect(self.select_field);ll.addWidget(self.field_list,1)
        tip=label('Selecciona un campo.\nPuedes moverlo en un borrador.\n\nDiseño fijo: PDF original.\nNo es composición nativa.','subtle');tip.setWordWrap(True);self.editor_tip=tip;ll.addWidget(tip)
        self.tools_scroll=QScrollArea();self.tools_scroll.setWidgetResizable(True);self.tools_scroll.setWidget(tools)
        self.tools_scroll.setFrameShape(QFrame.Shape.NoFrame);self.tools_scroll.setMinimumWidth(180);self.tools_scroll.setMaximumWidth(240)
        split.addWidget(self.tools_scroll)
        self.canvas=Preview();self.canvas.zoom_label=self.canvas_zoom_label;self.canvas.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.canvas.scene().selectionChanged.connect(self.scene_selection);split.addWidget(self.canvas)
        props=box();props.setMinimumWidth(270);props.setMaximumWidth(320);pl=vbox(props,20,16)
        pl.addWidget(label('PROPIEDADES','section'));self.field_title=label('Selecciona un campo','panelTitle');pl.addWidget(self.field_title)
        self.name_input=QLineEdit();self.name_input.textEdited.connect(self.change_name);pl.addWidget(self.name_input)
        pl.addWidget(label('POSICIÓN Y TAMAÑO','section'));form=QFormLayout();form.setSpacing(12);self.spins={}
        for key,text in [('x','X'),('y','Y'),('w','Ancho'),('h','Alto')]:
            spin=QDoubleSpinBox();spin.setRange(0,1000);spin.setSuffix(' mm');spin.setDecimals(2)
            spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
            spin.valueChanged.connect(self.change_geometry);self.spins[key]=spin;form.addRow(text,spin)
        pl.addLayout(form);pl.addWidget(label('TEXTO','section'))
        self.font_size=QDoubleSpinBox();self.font_size.setRange(6,80);self.font_size.setSuffix(' pt');self.font_size.valueChanged.connect(self.change_flags);pl.addWidget(self.font_size)
        self.font_size.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.bold=QCheckBox('Negrita');self.required=QCheckBox('Campo obligatorio');self.locked=QCheckBox('Bloquear posición')
        self.bold.toggled.connect(self.change_flags);pl.addWidget(self.bold)
        self.editor_advanced=QWidget();av=vbox(self.editor_advanced,0,8);av.addWidget(label('COMPORTAMIENTO','section'))
        for check in (self.required,self.locked):check.toggled.connect(self.change_flags);av.addWidget(check)
        av.addWidget(label('Accesos previstos · aún en la app actual','subtle'))
        for text in ('Reajuste y escalado','Recorte y anclaje Word','Seguridad y límites'):
            av.addWidget(button(text,lambda:self.show_access('document')))
        av.addWidget(label('Herramientas no migradas.\nNo modifica el motor PDF.','subtle'))
        self.editor_advanced.hide();ll.insertWidget(ll.count()-1,self.editor_advanced)
        pl.addStretch();self.edit_status=label('','subtle');self.edit_status.setWordWrap(True);pl.addWidget(self.edit_status)
        props_scroll=QScrollArea();self.properties_scroll=props_scroll;props_scroll.setWidgetResizable(True);props_scroll.setWidget(props)
        props_scroll.setFrameShape(QFrame.Shape.NoFrame);props_scroll.setMinimumWidth(280);props_scroll.setMaximumWidth(340)
        split.addWidget(props_scroll);split.setSizes([190,980,290]);split.setStretchFactor(1,1);lay.addWidget(split,1)
        lay.addWidget(label('Prueba visual: los cambios de campos son temporales y no se guardan ni aprueban.','subtle'))
        return page
    def editor_panels_menu(self):
        menu=QMenu(self)
        for title,panel in [('Elementos y herramientas',self.tools_scroll),('Propiedades',self.properties_scroll)]:
            action=menu.addAction(title);action.setCheckable(True);action.setChecked(panel.isVisible())
            action.triggered.connect(lambda checked,p=panel:p.setVisible(checked))
        menu.exec(self.cursor().pos())
    def toggle_editor_advanced(self):
        visible=self.editor_advanced_button.isChecked();self.editor_advanced.setVisible(visible)
        if visible:self.tools_scroll.show()
        self.editor_tip.setVisible(not visible)
        self.editor_tools.setMinimumWidth(250 if visible else 170);self.editor_tools.setMaximumWidth(280 if visible else 230)
        self.tools_scroll.setMinimumWidth(260 if visible else 180);self.tools_scroll.setMaximumWidth(285 if visible else 240)
        QTimer.singleShot(0,self.canvas.fit)
    def open_editor(self):
        if not self.row:return
        self.api.library.opened(self.row);vid=self.row['version_id']
        if vid==self.current_editor_id:self.navigate('editor');return
        self.current_editor_id=vid;self.editor_version=dict(self.api.version(vid))
        self.layouts.setdefault(vid,copy.deepcopy(json.loads(self.editor_version['fields_json'])))
        self.fields=self.layouts[vid];self.draw_editor();self.navigate('editor')
    def draw_editor(self):
        self.loading=True;v=self.editor_version
        self.editor_title.setText(v['name']+'  /  '+v['version'])
        self.editor_note.setText('Borrador ficticio · Puedes seleccionar y mover campos' if v['state']=='PENDING' else 'Revisión vigente ficticia · Solo lectura')
        scene=self.canvas.scene();scene.clear();self.field_items=[]
        im=self.api.thumbnail(v,width_px=1500);scene.addPixmap(pixmap(im));self.image_w,self.image_h=im.size
        self.field_list.clear()
        for i,f in enumerate(self.fields):
            item=FieldItem(f,i,im.width,im.height,v['state']=='PENDING',self.moved)
            scene.addItem(item);self.field_items.append(item);self.field_list.addItem(f['label'])
            text=scene.addText(f['key']);text.setDefaultTextColor(QColor('#147D71'));text.setParentItem(item);text.setPos(4,-3)
            text.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        scene.setSceneRect(QRectF(-45,-45,im.width+90,im.height+90));self.loading=False
        self.field_list.setCurrentRow(0);self.select_field(0);QTimer.singleShot(0,self.canvas.fit)
    def scene_selection(self):
        if self.loading:return
        selected=[x for x in self.canvas.scene().selectedItems() if isinstance(x,FieldItem)]
        if selected:self.field_list.setCurrentRow(selected[0].index)
    def select_field(self,index):
        if self.loading or index<0 or index>=len(self.field_items):return
        self.loading=True
        for i,item in enumerate(self.field_items):item.setSelected(i==index)
        f=self.fields[index];self.field_title.setText(f['label']);self.name_input.setText(f['label'])
        for key,spin in self.spins.items():
            spin.setValue(f[key]*self.editor_version['base_w_mm' if key in ('x','w') else 'base_h_mm'])
        self.font_size.setValue(f['font_pt']);self.bold.setChecked(f.get('bold',False))
        self.required.setChecked(f.get('required',False));self.locked.setChecked(f.get('locked',False))
        editable=self.editor_version['state']=='PENDING'
        for widget in [self.name_input,self.font_size,self.bold,self.required,self.locked,*self.spins.values()]:widget.setEnabled(editable)
        self.edit_status.setText('Cambios solo en memoria.\nSin guardado ni aprobación.' if editable else 'Una revisión vigente no se edita.\nCrear revisión sigue en la app actual.')
        self.loading=False
    def moved(self,index):
        if not self.loading and self.field_list.currentRow()==index:self.select_field(index)
    def change_geometry(self,*_):
        index=self.field_list.currentRow()
        if self.loading or index<0:return
        f=self.fields[index];self.loading=True
        for key,spin in self.spins.items():f[key]=spin.value()/self.editor_version['base_w_mm' if key in ('x','w') else 'base_h_mm']
        f['w']=max(.01,min(f['w'],1));f['h']=max(.01,min(f['h'],1));f['x']=min(f['x'],1-f['w']);f['y']=min(f['y'],1-f['h'])
        item=self.field_items[index];item.setRect(0,0,f['w']*self.image_w,f['h']*self.image_h)
        item.setPos(f['x']*self.image_w,f['y']*self.image_h);self.loading=False;self.select_field(index)
    def change_name(self,value):
        index=self.field_list.currentRow()
        if not self.loading and index>=0:
            self.fields[index]['label']=value;self.field_list.item(index).setText(value);self.field_title.setText(value)
    def change_flags(self,*_):
        index=self.field_list.currentRow()
        if self.loading or index<0:return
        f=self.fields[index];f.update(bold=self.bold.isChecked(),required=self.required.isChecked(),locked=self.locked.isChecked(),font_pt=self.font_size.value())
        self.field_items[index].setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,not f['locked'])
    def reset_layout(self):
        if self.current_editor_id is None:return
        self.layouts[self.current_editor_id]=copy.deepcopy(json.loads(self.editor_version['fields_json']))
        self.fields=self.layouts[self.current_editor_id];self.draw_editor()
