"""Interactive visual proof, consuming existing LocalServices on fictional data."""
import copy
import json
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPixmap, QImage, QColor, QPen, QBrush, QKeySequence, QShortcut
from PySide6.QtWidgets import (QMainWindow, QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QComboBox, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QStackedWidget, QScrollArea, QDialog, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsItem, QListWidget, QDoubleSpinBox, QCheckBox, QFormLayout,
    QMenu, QMessageBox)
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
        self.setAlignment(Qt.AlignmentFlag.AlignCenter);self.auto_fit=True
    def set_image(self,im):
        self.scene().clear();self.scene().addPixmap(pixmap(im))
        self.scene().setSceneRect(self.scene().itemsBoundingRect().adjusted(-30,-30,30,30));self.fit()
    def fit(self):
        self.auto_fit=True;self.fitInView(self.sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)
    def zoom(self,factor):
        scale=self.transform().m11()
        if .1<scale*factor<6:self.auto_fit=False;self.scale(factor,factor)
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
        self.layouts={};self.current_editor_id=None;self.field_items=[]
        self.setWindowTitle('COVEX Label Manager · Industrial Moderno · PRUEBA VISUAL')
        self.resize(1500,940);self.setMinimumSize(1050,720);self.setStyleSheet(STYLE)
        root=QWidget();root.setObjectName('workspace');self.setCentralWidget(root)
        outer=vbox(root,0,0);header=QFrame();header.setObjectName('header');header.setFixedHeight(78)
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
        page=QWidget();lay=vbox(page,26,18)
        row=QHBoxLayout();title=QVBoxLayout();title.addWidget(label('Biblioteca de etiquetas','title'))
        subtitle=label('Encuentra un diseño, revisa su versión y continúa trabajando.','subtle');subtitle.setWordWrap(False);title.addWidget(subtitle)
        row.addLayout(title);row.addStretch()
        actions=button('Documentos y acciones',self.actions_menu,ico='plus');row.addWidget(actions);lay.addLayout(row)
        searchrow=QHBoxLayout();self.search=QLineEdit();self.search.setObjectName('search')
        self.search.setPlaceholderText('Buscar por código, nombre, producto o cliente…')
        self.search.addAction(icon('search'),QLineEdit.ActionPosition.LeadingPosition)
        self.search.setToolTip('Ctrl+K abre y enfoca esta búsqueda')
        self.search.setClearButtonEnabled(True);self.search.textChanged.connect(self.refresh)
        searchrow.addWidget(self.search,1);searchrow.addWidget(label('Ctrl+K','subtle'))
        self.advanced_button=button('Filtros avanzados',self.toggle_advanced,ico='filter')
        self.advanced_button.setCheckable(True);searchrow.addWidget(self.advanced_button);lay.addLayout(searchrow)
        frequent=QHBoxLayout()
        for key in ('category','origin','state'):
            frequent.addWidget(label(FILTERS[key],'subtle'))
            c=self.make_filter(key);c.setMinimumWidth(160);frequent.addWidget(c)
        frequent.addStretch();frequent.addWidget(button('Limpiar',self.reset_filters))
        self.count=label('','subtle');frequent.addWidget(self.count);lay.addLayout(frequent)
        self.library_split=QSplitter();self.library_split.setHandleWidth(14)
        left=box();left.setMinimumWidth(190);ll=vbox(left,16,6);ll.addWidget(label('TU BIBLIOTECA','section'))
        self.view_buttons={}
        for key,text,ico in [('all','Todas','library'),('favorites','Favoritas','star'),('recent','Recientes','clock')]:
            b=button(text,lambda checked=False,k=key:self.set_mode(k),'view',ico)
            b.setCheckable(True);b.setChecked(key=='all');self.view_buttons[key]=b;ll.addWidget(b)
        ll.addSpacing(20);self.advanced=QWidget();al=vbox(self.advanced,0,9);al.addWidget(label('AFINAR RESULTADOS','section'))
        for key in ('family','type','customer','country','language','version','acquisition'):
            al.addWidget(label(FILTERS[key],'subtle'));al.addWidget(self.make_filter(key))
        self.advanced.hide();ll.addWidget(self.advanced)
        ll.addStretch();ll.addWidget(label('Los filtros se combinan.\nSin datos: no se inventan valores.','subtle'))
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(left);scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.library_split.addWidget(scroll)
        center=box();cl=vbox(center,0,0)
        self.table=QTableWidget(0,9);self.table.setHorizontalHeaderLabels(['','CÓDIGO','DENOMINACIÓN','TIPO','VERSIÓN','ORIGEN','CLIENTE','PAÍS','ESTADO'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False);self.table.setWordWrap(False);self.table.verticalHeader().hide();self.table.verticalHeader().setDefaultSectionSize(46)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        for c,w in enumerate([32,98,240,110,84,88,112,94,105]):self.table.setColumnWidth(c,w)
        # Documentary state precedes secondary metadata at smaller widths.
        self.table.horizontalHeader().moveSection(3,7)
        self.table.horizontalHeader().moveSection(self.table.horizontalHeader().visualIndex(8),4)
        self.table.itemSelectionChanged.connect(self.selected);self.table.cellDoubleClicked.connect(lambda *_:self.open_editor())
        self.table.cellClicked.connect(lambda r,c:self.favorite() if c==0 else None)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_table)
        cl.addWidget(self.table,1)
        hint=label('Doble clic para abrir en Editor   ·   Arrastra los encabezados para ajustar columnas','subtle')
        hint.setContentsMargins(16,14,16,14);cl.addWidget(hint);self.library_split.addWidget(center)
        self.inspector=box();self.inspector.setMinimumWidth(290);self.inspector.setMaximumWidth(380)
        outer_il=vbox(self.inspector,20,10)
        details=QWidget();details.setObjectName('details');details.setStyleSheet('QWidget#details {background:white;}')
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setStyleSheet('QScrollArea {background:white;border:none;}')
        scroll.setWidget(details);scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer_il.addWidget(scroll,1);il=vbox(details,0,10);il.addWidget(label('DISEÑO SELECCIONADO','section'))
        self.doc_title=label('','panelTitle');self.doc_title.setWordWrap(True);il.addWidget(self.doc_title)
        self.badge=label('','badge');il.addWidget(self.badge,0,Qt.AlignmentFlag.AlignLeft)
        self.preview=Preview();self.preview.setMinimumHeight(140);self.preview.setMaximumHeight(180);il.addWidget(self.preview)
        il.addWidget(button('Ampliar vista previa',self.enlarge,ico='expand'))
        self.meta=label('');self.meta.setWordWrap(True);self.meta.setTextFormat(Qt.TextFormat.PlainText);il.addWidget(self.meta)
        revision_label=label('REVISIÓN DOCUMENTAL','section');il.addWidget(revision_label)
        self.revision=QComboBox();self.revision.currentIndexChanged.connect(self.revision_changed);il.addWidget(self.revision)
        self.doc_note=label('','subtle');self.doc_note.setWordWrap(True);il.addWidget(self.doc_note);il.addStretch()
        # Revision/state remain visible before scrollable document details.
        il.insertWidget(3,revision_label);il.insertWidget(4,self.revision)
        il=outer_il
        self.favorite_button=button('Añadir a favoritas',self.favorite,ico='star');il.addWidget(self.favorite_button)
        il.addWidget(button('Abrir en Editor',self.open_editor,'primary','arrow'))
        il.addWidget(button('Ver accesos de emisión',lambda:self.navigate('emission'),ico='print'))
        self.library_split.addWidget(self.inspector);self.library_split.setSizes([205,900,310])
        self.library_split.setStretchFactor(1,1);lay.addWidget(self.library_split,1)
        return page

    def make_filter(self,key):
        c=QComboBox();c.addItem('Todos','')
        for value in self.api.library.facets()[key]:c.addItem(STATE[value][0] if key=='state' else value,value)
        c.currentIndexChanged.connect(self.refresh);self.filters[key]=c
        c.setEnabled(c.count()>1);return c
    def toggle_advanced(self):
        self.advanced.setVisible(not self.advanced.isVisible());self.advanced_button.setChecked(self.advanced.isVisible())
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
        self.meta.setText(f"{self.row['code']}  ·  {v['base_w_mm']:g} × {v['base_h_mm']:g} mm\n{self.row['origin']}  ·  {self.row['category']}"+('\n'+self.row['customer'] if self.row['customer'] else ''))
        self.meta.setToolTip('\n'.join(f'{title}: {self.row.get(key,"")}' for key,title in FILTERS.items() if self.row.get(key)))
        self.revision.blockSignals(True);self.revision.clear()
        for r in self.api.versions(self.row['id']):
            self.revision.addItem(f"Revisión {r['version']}  ·  {STATE[r['state']][0]}",r['id'])
        self.revision.setCurrentIndex(self.revision.findData(vid));self.revision.blockSignals(False)
        self.doc_note.setText('Aprobación ficticia de demostración.' if v['state']=='APPROVED' else 'Pendiente de aprobación.\nConsultar y editar no autoriza la emisión.')
        self.favorite_button.setText('Quitar de favoritas' if self.row['favorite'] else 'Añadir a favoritas')
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
        lay.addWidget(view,1);lay.addWidget(label('Rueda: zoom  ·  Arrastrar: desplazar  ·  Solo documento ficticio','subtle'));dialog.exec()
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
            compact=event.size().width()<1400
            # Secondary metadata remain accessible in the inspector/tooltips and at larger widths.
            self.table.setColumnHidden(3,compact);self.table.setColumnHidden(7,compact)
            self.table.setColumnHidden(6,event.size().width()<1250)
            self.table.setColumnHidden(5,event.size().width()<1200)
            small=event.size().width()<1200
            self.table.setColumnWidth(2,200 if small else 240)
            self.table.setColumnWidth(4,70 if small else 84)
            self.table.setColumnWidth(8,90 if small else 105)
            self.brand_title.setText('COVEX / LABELS' if event.size().width()<1300 else 'COVEX  /  LABEL MANAGER')
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
        head.addLayout(titles);head.addStretch();head.addWidget(button('Biblioteca',lambda:self.navigate('library'),ico='library'));lay.addLayout(head)
        toolbar=box();tl=QHBoxLayout(toolbar);tl.setContentsMargins(12,8,12,8)
        tl.addWidget(label('LIENZO','section'));tl.addWidget(button('Ajustar a pantalla',lambda:self.canvas.fit(),ico='expand'))
        tl.addWidget(button('−',lambda:self.canvas.zoom(1/1.2)));tl.addWidget(button('+',lambda:self.canvas.zoom(1.2)))
        tl.addStretch();tl.addWidget(button('Herramientas avanzadas',lambda:self.show_access('document'),ico='settings'))
        tl.addWidget(button('Restablecer ejemplo',self.reset_layout));lay.addWidget(toolbar)
        split=QSplitter();split.setHandleWidth(14)
        tools=box();tools.setMinimumWidth(170);tools.setMaximumWidth(230);ll=vbox(tools,16)
        ll.addWidget(label('ELEMENTOS','section'));ll.addWidget(label('Campos variables','panelTitle'))
        self.field_list=QListWidget();self.field_list.currentRowChanged.connect(self.select_field);ll.addWidget(self.field_list,1)
        tip=label('Selecciona un campo.\nPuedes moverlo en un borrador.\n\nDiseño fijo: PDF original.\nNo es composición nativa.','subtle');tip.setWordWrap(True);ll.addWidget(tip);split.addWidget(tools)
        self.canvas=Preview();self.canvas.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.canvas.scene().selectionChanged.connect(self.scene_selection);split.addWidget(self.canvas)
        props=box();props.setMinimumWidth(270);props.setMaximumWidth(320);pl=vbox(props,20,16)
        pl.addWidget(label('PROPIEDADES','section'));self.field_title=label('Selecciona un campo','panelTitle');pl.addWidget(self.field_title)
        self.name_input=QLineEdit();self.name_input.textEdited.connect(self.change_name);pl.addWidget(self.name_input)
        pl.addWidget(label('POSICIÓN Y TAMAÑO','section'));form=QFormLayout();form.setSpacing(12);self.spins={}
        for key,text in [('x','X'),('y','Y'),('w','Ancho'),('h','Alto')]:
            spin=QDoubleSpinBox();spin.setRange(0,1000);spin.setSuffix(' mm');spin.setDecimals(2)
            spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
            spin.valueChanged.connect(self.change_geometry);self.spins[key]=spin;form.addRow(text,spin)
        pl.addLayout(form);pl.addWidget(label('TEXTO Y COMPORTAMIENTO','section'))
        self.font_size=QDoubleSpinBox();self.font_size.setRange(6,80);self.font_size.setSuffix(' pt');self.font_size.valueChanged.connect(self.change_flags);pl.addWidget(self.font_size)
        self.font_size.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.bold=QCheckBox('Negrita');self.required=QCheckBox('Campo obligatorio');self.locked=QCheckBox('Bloquear posición')
        for check in (self.bold,self.required,self.locked):check.toggled.connect(self.change_flags);pl.addWidget(check)
        pl.addStretch();self.edit_status=label('','subtle');self.edit_status.setWordWrap(True);pl.addWidget(self.edit_status)
        split.addWidget(props);split.setSizes([190,980,290]);split.setStretchFactor(1,1);lay.addWidget(split,1)
        lay.addWidget(label('Prueba visual: los cambios de campos son temporales y no se guardan ni aprueban.','subtle'))
        return page
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
