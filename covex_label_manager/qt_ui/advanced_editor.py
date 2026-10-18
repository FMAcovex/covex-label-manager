"""R3B1 pending-layout tools, preserving the Industrial Moderno shell."""
import copy
import json
from PySide6.QtCore import Qt, QRectF, QTimer
from PySide6.QtGui import QColor, QPen, QBrush, QKeySequence, QShortcut
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QDialog,
    QDialogButtonBox, QDoubleSpinBox, QCheckBox, QComboBox, QLineEdit, QListWidget,
    QAbstractItemView, QMessageBox, QGraphicsRectItem, QGraphicsItem, QPushButton, QLabel,
    QSplitter)
from .window import Preview, pixmap, label, button, vbox
from .responsive import AdaptiveDialog as QDialog
from ..editor_layout import (LayoutHistory, layout_from_version, version_with_layout,
    validate_layout, recrop, move_field, align_fields, scale_fields, anchor_field,
    relocate_anchors, source_identity, check_locked_changes, MM_PER_POINT)


def spin(value, maximum=10000, suffix=' mm', minimum=0):
    result = QDoubleSpinBox(); result.setDecimals(3); result.setRange(minimum, maximum)
    result.setSuffix(suffix); result.setValue(value)
    return result


class RectangleView(Preview):
    def __init__(self, image, bounds, changed):
        super().__init__(); self.set_image(image); self.bounds = bounds; self.changed = changed
        self.iw, self.ih = image.size; self.start = None; self.outline = None
        self.setDragMode(Preview.DragMode.NoDrag)

    def point(self, event):
        p = self.mapToScene(event.position().toPoint()); b = self.bounds
        return (b[0]+max(0, min(p.x(), self.iw))/self.iw*(b[2]-b[0]),
                b[1]+max(0, min(p.y(), self.ih))/self.ih*(b[3]-b[1]))

    def paint_rect(self, rect):
        b = self.bounds; x0,y0,x1,y1 = rect
        if self.outline: self.scene().removeItem(self.outline)
        self.outline = self.scene().addRect(QRectF((x0-b[0])*self.iw/(b[2]-b[0]),
            (y0-b[1])*self.ih/(b[3]-b[1]), (x1-x0)*self.iw/(b[2]-b[0]),
            (y1-y0)*self.ih/(b[3]-b[1])), QPen(QColor('#147D71'), 2), QBrush(QColor(20,125,113,25)))
        self.outline.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: self.start = self.point(event); event.accept()
        else: super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.start:
            x,y = self.point(event); a,b = self.start
            self.changed([min(x,a),min(y,b),max(x,a),max(y,b)])
            event.accept()
        else: super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.start:
            self.mouseMoveEvent(event); self.start = None; event.accept()
        else: super().mouseReleaseEvent(event)


class RectangleDialog(QDialog):
    def __init__(self, parent, title, image, bounds, rect, min_side=0):
        super().__init__(parent); self.setWindowTitle(title); self.resize(920,650)
        self.bounds = bounds; self.min_side = min_side; self.busy = False
        layout = vbox(self); layout.addWidget(label(title,'panelTitle'))
        layout.addWidget(label('Arrastra sobre el documento o introduce límites en mm. La fuente permanece intacta.','subtle'))
        body = QHBoxLayout(); self.view = RectangleView(image,bounds,self.from_drag); body.addWidget(self.view,1)
        panel = QWidget(); pl = vbox(panel,8); form = QFormLayout(); self.inputs=[]
        for name, value in zip(('Izquierda','Superior','Derecha','Inferior'),rect):
            entry = spin(value*MM_PER_POINT); entry.valueChanged.connect(self.from_form)
            form.addRow(name,entry); self.inputs.append(entry)
        pl.addLayout(form); self.error = label('','subtle'); pl.addWidget(self.error); pl.addStretch()
        body.addWidget(panel); layout.addLayout(body,1)
        self.extra = QVBoxLayout(); layout.addLayout(self.extra)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept_valid); buttons.rejected.connect(self.reject); layout.addWidget(buttons)
        self.from_form()

    def from_drag(self, rect):
        self.busy = True
        for entry,value in zip(self.inputs,rect): entry.setValue(value*MM_PER_POINT)
        self.busy = False; self.from_form()

    def from_form(self):
        if self.busy: return
        self.selection_rect = [s.value()/MM_PER_POINT for s in self.inputs]
        self.view.paint_rect(self.selection_rect)
        self.error.setText(f'Tamaño seleccionado: {(self.selection_rect[2]-self.selection_rect[0])*MM_PER_POINT:.3f} × {(self.selection_rect[3]-self.selection_rect[1])*MM_PER_POINT:.3f} mm')

    def accept_valid(self):
        b = self.bounds; r = self.selection_rect
        if not (b[0] <= r[0] < r[2] <= b[2]+.001 and b[1] <= r[1] < r[3] <= b[3]+.001):
            self.error.setText('Los límites deben estar dentro del documento.'); return
        if min(r[2]-r[0],r[3]-r[1]) < self.min_side:
            self.error.setText('El recorte necesita al menos 7,06 mm por lado.'); return
        self.accept()


from .resize_item import ResizableRect


class EditorFieldItem(ResizableRect):
    def __init__(self, field, index, width, height, crop, editable, released):
        self.index = index; self.field = copy.deepcopy(field); self.iw = width; self.ih = height
        self.offset = -field['font_pt']*1.06*height/(crop[3]-crop[1]) if field.get('draw') in ('baseline','continuation') else 0
        vh = max(field['h']*height, -self.offset*1.3) if self.offset else field['h']*height
        super().__init__(0,0,field['w']*width,vh)
        self.setPen(QPen(QColor('#147D71'),1.5,Qt.PenStyle.DashLine))
        self.setBrush(QBrush(QColor(20,125,113,18)))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,editable and not field.get('locked'))
        self.setPos(field['x']*width,field['y']*height+self.offset); self.released = released
        self.original_rect = QRectF(self.rect())
        self.enable_handles(editable and not field.get('locked'))

    def mouseMoveEvent(self,event):
        super().mouseMoveEvent(event)
        if hasattr(self,'feedback'):self.feedback()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event); self.released()


class AdvancedEditorMixin:
    def __init__(self, session):
        self._gesture_dispatch = False
        self.design = None; self.expected_layout = None; self.output_profile = None
        self._drawing = False; self._selection_sync = False
        super().__init__(session)
        self.setWindowTitle('COVEX Label Manager · R3B1 Qt · Editor avanzado')
        for note in self.header.findChildren(QLabel):
            if 'R3A Qt' in note.text(): note.setText('R3B1 Qt · Local')
        self.statusBar().showMessage('Editor avanzado Qt · Centro de emisión nativo disponible')

    def build_editor(self):
        page = super().build_editor()
        # Replace only the advanced tool contents, keeping the approved shell.
        layout = self.editor_advanced.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget(): item.widget().setParent(None)
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget(): child.widget().setParent(None)
        self.tool_sections = {}; self.design_buttons = []
        def section(title):
            toggle = QPushButton('▸ '+title); toggle.setCheckable(True)
            content = QWidget(); cl = vbox(content,0,6); content.hide()
            toggle.toggled.connect(lambda checked,c=content,t=toggle,n=title:(c.setVisible(checked),t.setText(('▾ ' if checked else '▸ ')+n)))
            layout.addWidget(toggle); layout.addWidget(content); self.tool_sections[title]=(toggle,content)
            return cl
        def action(cl,text,callback):
            b = button(text,callback); b.setToolTip(text); cl.addWidget(b); self.design_buttons.append(b); return b
        doc = section('Documento')
        action(doc,'Recorte visual / mm',self.edit_crop)
        anchor_button=action(doc,'Anclar a referencia',self.edit_anchor); anchor_button.setToolTip('Anclar campo al texto extraído del PDF o Word convertido; sin editar el original.')
        relocate_button=action(doc,'Relocalizar referencias',self.relocate); relocate_button.setToolTip('Solo anclas verificables de la misma fuente o plantillas reconocidas ACETONA/EDROFONIO. No adapta automáticamente nuevas revisiones Word/PDF.')
        fld = section('Campo')
        action(fld,'Quitar campo',self.remove_field)
        fld.addWidget(self.required); fld.addWidget(self.locked)
        self.draw_mode = QComboBox()
        for name,key in [('Caja de texto','textbox'),('Línea base','baseline'),('Continuación','continuation'),('Párrafo','paragraph')]: self.draw_mode.addItem(name,key)
        self.draw_mode.setToolTip('Modo de dibujo conservado por el motor PDF. Continuación requiere configuración de segunda línea.')
        self.draw_mode.activated.connect(self.change_draw_mode); fld.addWidget(self.draw_mode)
        action(fld,'Borrado y continuación',self.edit_auxiliary)
        comp = section('Composición')
        self.alignment = QComboBox()
        for title,key in [('Izquierda','left'),('Centro horizontal','center_x'),('Derecha','right'),('Arriba','top'),('Centro vertical','center_y'),('Abajo','bottom'),('Distribuir horizontalmente','distribute_x'),('Distribuir verticalmente','distribute_y')]: self.alignment.addItem(title,key)
        comp.addWidget(self.alignment); action(comp,'Aplicar a selección',self.align_selection)
        scale_button=action(comp,'Reajuste proporcional',self.edit_scale); scale_button.setToolTip('Reajusta los campos seleccionados; no cambia el tamaño físico de la etiqueta ni el zoom de visualización.')
        self.format_button = button('Formato físico y prueba',self.edit_output); self.format_button.setToolTip('Escalado físico proporcional de la etiqueta completa para impresión y PDF de prueba. Independiente del reajuste de campos y del zoom de visualización.'); comp.addWidget(self.format_button)
        state = section('Estado y límites')
        action(state,'Zona de estado visual / mm',self.edit_status_area)
        state.addWidget(label('Prepare los datos variables y emita desde el Centro de emisión.','subtle'))
        legacy_button=button('Editor anterior (compatibilidad)…',lambda:self.open_legacy('editor')); legacy_button.setToolTip('Abre una aplicación separada para compatibilidad. Conserva los mismos datos y bloquea la edición simultánea.'); state.addWidget(legacy_button)
        self.editor_legacy_button=legacy_button
        self.field_action_bar=QWidget();row=QHBoxLayout(self.field_action_bar);row.setContentsMargins(0,0,0,0)
        self.new_field_button=button('+ Nuevo campo',self.quick_add_field,'primary')
        self.draw_field_button=button('Dibujar campo',self.draw_new_field)
        row.addWidget(self.new_field_button); row.addWidget(self.draw_field_button)
        page.layout().insertWidget(2,self.field_action_bar)
        self.field_snap=QCheckBox('Snap de campos a 1 mm');self.editor_tools.layout().insertWidget(1,self.field_snap)
        self.field_grid=QCheckBox('Cuadrícula de campos (10 mm)');self.field_grid.toggled.connect(lambda *_:self.draw_editor() if self.design else None);self.editor_tools.layout().insertWidget(2,self.field_grid)
        self.variant_edit_button=button('Ajustar campos de revisión vigente…',self.editable_variant)
        row.addWidget(self.variant_edit_button);row.addStretch()
        self.editor_tools.layout().insertWidget(2,label('Solo se editan campos variables superpuestos. El maestro fijo permanece protegido.','subtle'))
        self.field_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.field_list.itemSelectionChanged.connect(self.list_selection)
        self.field_list.setToolTip('Ctrl: varios campos. Mayús: intervalo. Los campos bloqueados no se transforman.')
        action(fld,'Añadir campo especial…',self.add_field)
        self.editor_tools.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        for entry in self.spins.values(): entry.setDecimals(3)
        self.font_size.setRange(3,80)
        self.save_button.setText('Guardar diseño pendiente')
        self.editor_reset_button.setText('Restablecer diseño')
        self.editor_reset_button.setToolTip('Restablecer campos, recorte y zona de estado al diseño guardado; se puede deshacer.')
        page.layout().itemAt(page.layout().count()-1).widget().setText('Fuente fija protegida · Diseño: guardado explícito · Sin autoguardado de trabajos ni sincronización de variables')
        toolbar = page.layout().itemAt(1).widget().layout()
        self.undo_button = button('Deshacer',self.undo_edit); self.redo_button = button('Rehacer',self.redo_edit)
        toolbar.insertWidget(1,self.undo_button); toolbar.insertWidget(2,self.redo_button)
        self.undo_shortcut = QShortcut(QKeySequence('Ctrl+Z'),page); self.undo_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.undo_shortcut.activated.connect(self.undo_edit)
        self.redo_shortcut = QShortcut(QKeySequence('Ctrl+Shift+Z'),page); self.redo_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.redo_shortcut.activated.connect(self.redo_edit)
        return page

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self.nav['emission'].setToolTip('Emisión · Acceso a la versión anterior Tkinter')
        if hasattr(self,'editor_reset_button'):
            self.editor_reset_button.setText('Restablecer' if event.size().width()<1200 else 'Restablecer diseño')

    def editor_record(self,version_id=None):
        return self.api.version(version_id if version_id is not None else self.current_editor_id)

    def editable(self):
        if self.design is None or self.legacy_process: return False
        v = self.editor_record()
        return v is not None and v['state'] == 'PENDING'

    def selected_indices(self):
        return sorted({i.row() for i in self.field_list.selectedIndexes()})

    def open_editor(self):
        if not self.row: return
        vid = self.row['version_id']
        try: self.api.open_document(vid)
        except (ValueError,OSError) as ex: QMessageBox.warning(self,'Documento no disponible',str(ex)); return
        if vid != self.current_editor_id:
            if not self.resolve_work(): return
            self.current_editor_id = vid; self.editor_version = dict(self.editor_record(vid))
            self.expected_layout = layout_from_version(self.editor_version); self.design = LayoutHistory(self.expected_layout)
            self.expected_source = source_identity(self.editor_version)
            self.output_profile = None
            self.sync_design(); self.api.library.opened(self.row); self.draw_editor(fit=True)
        self.navigate('editor'); self.update_dirty()

    def sync_design(self):
        self.fields = self.design.state['fields']; self.layouts[self.current_editor_id] = self.fields
        self.original_fields[self.current_editor_id] = copy.deepcopy(self.design.clean['fields'])
        self.editor_version = version_with_layout(self.editor_version,self.design.state)

    def draw_editor(self, fit=False):
        # A release callback still has C++ QGraphicsItem/ResizeHandle frames on
        # the stack. Commit geometry now, but never scene.clear() those objects
        # until Qt has returned from their virtual mouseReleaseEvent.
        if self._gesture_dispatch:
            if not hasattr(self, '_gesture_redraw'):
                self._gesture_redraw = QTimer(self)
                self._gesture_redraw.setSingleShot(True)
                self._gesture_redraw.timeout.connect(self.draw_editor)
            self._gesture_redraw.start(0)
            return
        if hasattr(self, '_gesture_redraw'):self._gesture_redraw.stop()
        if self.design is None: return
        indices = self.selected_indices(); self._drawing = True; self.loading = True
        self.sync_design(); v = self.editor_version
        self.editor_title.setText(v['name']+'  /  '+v['version'])
        self.editor_note.setText(('Diseño pendiente' if v['state']=='PENDING' else 'Revisión vigente o retirada · Solo lectura')+
                                 f" · {v['base_w_mm']:.2f} × {v['base_h_mm']:.2f} mm de origen")
        self.canvas.end_draw();self.draw_field_button.setText('Dibujar campo')
        scene = self.canvas.scene(); scene.clear(); self.field_items=[]
        try:
            self.api.editor_page_rect(self.current_editor_id)
            im = self.api.thumbnail(v,width_px=1500)
        except (ValueError,OSError,RuntimeError) as ex:
            scene.addText('Documento no disponible: '+str(ex)); self.field_list.clear()
            self.loading=False; self._drawing=False; self.disable_properties(); self.update_dirty(); return
        scene.addPixmap(pixmap(im)); self.image_w,self.image_h=im.size
        if self.field_grid.isChecked():
            bw=self.editor_version['base_w_mm'];bh=self.editor_version['base_h_mm']
            for x in range(0,int(bw)+1,10):scene.addLine(x/bw*im.width,0,x/bw*im.width,im.height,QPen(QColor('#C4D9DB'),.5))
            for y in range(0,int(bh)+1,10):scene.addLine(0,y/bh*im.height,im.width,y/bh*im.height,QPen(QColor('#C4D9DB'),.5))
        area = self.design.state['area']
        if area:
            x,y,w,h = area
            scene.addRect(QRectF(x*im.width,y*im.height,w*im.width,h*im.height),QPen(QColor('#AE5BC0'),2,Qt.PenStyle.DashLine))
            text = scene.addText('RESERVA ESTADO'); text.setDefaultTextColor(QColor('#85369A')); text.setPos(x*im.width,y*im.height)
            text.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.field_list.clear()
        for i,f in enumerate(self.fields):
            item = EditorFieldItem(f,i,im.width,im.height,self.design.state['crop'],self.editable(),self.finish_graphic_gesture)
            item.feedback=lambda item=item:self.statusBar().showMessage(f"Campo: X {(item.x()+item.rect().x())/self.image_w*self.editor_version['base_w_mm']:.2f} mm · Y {(item.y()+item.rect().y()-item.offset)/self.image_h*self.editor_version['base_h_mm']:.2f} mm · Ancho {item.rect().width()/self.image_w*self.editor_version['base_w_mm']:.2f} mm · Alto {item.rect().height()/self.image_h*self.editor_version['base_h_mm']:.2f} mm")
            scene.addItem(item); self.field_items.append(item); self.field_list.addItem(self.field_description(f))
            self.field_list.item(i).setToolTip(f['key']+' · '+('Posición bloqueada' if f.get('locked') else 'Posición editable'))
            text = scene.addText(f['key']); text.setDefaultTextColor(QColor('#147D71')); text.setParentItem(item); text.setPos(4,-3)
            text.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
            item.caption = text
        scene.setSceneRect(QRectF(-45,-45,im.width+90,im.height+90))
        indices = [i for i in indices if i < len(self.fields)] or ([0] if self.fields else [])
        for i in indices: self.field_list.item(i).setSelected(True); self.field_items[i].setSelected(True)
        self.loading=False; self._drawing=False
        if indices: self.select_field(indices[0])
        else: self.disable_properties()
        if fit: QTimer.singleShot(0,self.canvas.fit)
        self.update_dirty()

    def disable_properties(self):
        for widget in [self.name_input,self.key_input,self.font_size,self.bold,self.required,self.locked,self.draw_mode,*self.spins.values()]: widget.setEnabled(False)
        self.field_title.setText('Selecciona un campo')

    def scene_selection(self):
        if self.loading or self._selection_sync: return
        selected = [x.index for x in self.canvas.scene().selectedItems() if isinstance(x,EditorFieldItem)]
        self._selection_sync=True
        self.field_list.blockSignals(True); self.field_list.clearSelection()
        for i in selected: self.field_list.item(i).setSelected(True)
        self.field_list.blockSignals(False); self._selection_sync=False
        if selected: self.show_properties(min(selected))
        else: self.disable_properties()

    def list_selection(self):
        if self.loading or self._selection_sync: return
        self._selection_sync=True; selected=self.selected_indices()
        for i,item in enumerate(self.field_items): item.setSelected(i in selected)
        self._selection_sync=False
        if selected: self.show_properties(selected[0])
        else: self.disable_properties()

    def select_field(self, index):
        if self.loading or self.design is None or not 0 <= index < len(self.fields): return
        if index not in self.selected_indices():
            self.field_list.blockSignals(True); self.field_list.clearSelection(); self.field_list.item(index).setSelected(True); self.field_list.blockSignals(False)
        self.list_selection(); self.show_properties(index)

    def show_properties(self, index):
        self.commit_pending_properties()
        self.property_index=index; self.loading=True; f=self.fields[index]
        self.field_title.setText(f['label']); self.name_input.setText(f['label']); self.key_input.setText(f['key'])
        for key,entry in self.spins.items(): entry.setValue(f[key]*self.editor_version['base_w_mm' if key in ('x','w') else 'base_h_mm'])
        self.font_size.setValue(f['font_pt']); self.bold.setChecked(f.get('bold',False))
        self.required.setChecked(f.get('required',False)); self.locked.setChecked(f.get('locked',False))
        self.draw_mode.setCurrentIndex(self.draw_mode.findData(f.get('draw','textbox')))
        enabled=self.editable()
        for widget in [self.name_input,self.key_input,self.font_size,self.bold,self.required,self.locked,self.draw_mode]: widget.setEnabled(enabled)
        for entry in self.spins.values(): entry.setEnabled(enabled and not f.get('locked'))
        self.loading=False
        if hasattr(self,'delete_field_button'):
            selected=self.selected_indices()
            self.delete_field_button.setEnabled(enabled and bool(selected) and not any(self.fields[i].get('locked') for i in selected))

    def commit_pending_properties(self):
        if self.loading or not self.editable() or getattr(self,'_committing_properties',False):return
        self._committing_properties=True
        try:
            for entry in (*self.spins.values(),self.font_size):entry.interpretText()
        finally:self._committing_properties=False

    @staticmethod
    def field_description(field):
        return field['label']+(' · obligatorio' if field.get('required') else '')+(' · bloqueado' if field.get('locked') else '')

    def refresh_field_overlays(self):
        """Property typing never tears down the scene, focus, selection or zoom."""
        self.sync_design();self.loading=True
        try:
            for i, (item, field) in enumerate(zip(self.field_items,self.fields)):
                item.field=copy.deepcopy(field)
                item.offset=-field['font_pt']*1.06*self.image_h/(self.design.state['crop'][3]-self.design.state['crop'][1]) if field.get('draw') in ('baseline','continuation') else 0
                height=max(field['h']*self.image_h,-item.offset*1.3) if item.offset else field['h']*self.image_h
                item.setRect(0,0,field['w']*self.image_w,height)
                item.setPos(field['x']*self.image_w,field['y']*self.image_h+item.offset)
                item.original_rect=QRectF(item.rect())
                movable=self.editable() and not field.get('locked')
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,movable)
                if bool(item.handles)!=movable:
                    for handle in item.handles:self.canvas.scene().removeItem(handle)
                    item.enable_handles(movable)
                item.position_handles();item.caption.setPlainText(field['key'])
                self.field_list.item(i).setText(self.field_description(field))
            if hasattr(self,'property_index') and 0<=self.property_index<len(self.fields):
                field=self.fields[self.property_index]
                self.field_title.setText(field['label'])
                for entry in self.spins.values():entry.setEnabled(self.editable() and not field.get('locked'))
        finally:self.loading=False
        self.update_dirty()

    def command(self, title, candidate, *, rebuild=True):
        if not self.editable(): return False
        try:
            validate_layout(candidate,self.api.editor_page_rect(self.current_editor_id))
            check_locked_changes(self.design.state,candidate)
            changed=self.design.push(candidate,title)
            if changed:
                if rebuild:self.draw_editor()
                else:self.refresh_field_overlays()
            return changed
        except (ValueError,PermissionError,OSError) as ex:
            QMessageBox.warning(self,'Cambio no realizado',str(ex)); self.draw_editor(); return False

    def apply_operation(self, title, operation):
        if not self.editable(): return False
        try: return self.command(title,operation())
        except (ValueError,PermissionError,OSError) as ex:
            QMessageBox.warning(self,'Cambio no realizado',str(ex)); return False

    def change_geometry(self,*_):
        if self.loading or not self.editable() or not hasattr(self,'property_index'): return
        index=self.property_index; candidate=copy.deepcopy(self.design.state); f=candidate['fields'][index]
        if f.get('locked'): return
        x=self.spins['x'].value()/self.editor_version['base_w_mm']; y=self.spins['y'].value()/self.editor_version['base_h_mm']
        move_field(f,x-f['x'],y-f['y'],candidate['crop'])
        f['w']=self.spins['w'].value()/self.editor_version['base_w_mm']; f['h']=self.spins['h'].value()/self.editor_version['base_h_mm']
        self.command('Geometría en mm',candidate,rebuild=False)

    def change_name(self,value):
        if self.loading or not self.editable() or not hasattr(self,'property_index'): return
        candidate=copy.deepcopy(self.design.state); candidate['fields'][self.property_index]['label']=value
        self.command('Nombre del campo',candidate,rebuild=False)

    def change_key(self,value):
        if self.loading or not self.editable() or not hasattr(self,'property_index'): return
        candidate=copy.deepcopy(self.design.state); candidate['fields'][self.property_index]['key']=value
        self.command('Identificador del campo',candidate,rebuild=False)

    def change_flags(self,*_):
        if self.loading or not self.editable() or not hasattr(self,'property_index'): return
        candidate=copy.deepcopy(self.design.state)
        candidate['fields'][self.property_index].update(bold=self.bold.isChecked(),required=self.required.isChecked(),locked=self.locked.isChecked(),font_pt=self.font_size.value())
        self.command('Propiedades de texto / bloqueo',candidate,rebuild=False)

    def change_draw_mode(self,*_):
        if self.loading or not self.editable(): return
        candidate=copy.deepcopy(self.design.state); f=candidate['fields'][self.property_index]
        mode=self.draw_mode.currentData(); f['draw']=mode
        if mode=='continuation': f.setdefault('second_x',f['x']); f.setdefault('next_w',f['w']); f.setdefault('max_lines',3)
        self.command('Modo de dibujo',candidate,rebuild=False)

    def moved(self,index):
        # Kept for callers of the R3A controller; graphical gestures commit on release.
        self.drag_finished()

    def finish_graphic_gesture(self):
        self._gesture_dispatch = True
        try:self.drag_finished()
        finally:self._gesture_dispatch = False

    def drag_finished(self):
        if not self.editable(): self.draw_editor(); return
        candidate=copy.deepcopy(self.design.state)
        for item in self.field_items:
            f=candidate['fields'][item.index]
            dx=item.pos().x()/self.image_w-f['x']; dy=(item.pos().y()-item.offset)/self.image_h-f['y']
            if self.field_snap.isChecked() and (abs(dx)>1e-9 or abs(dy)>1e-9):
                bw=self.editor_version['base_w_mm'];bh=self.editor_version['base_h_mm']
                dx=round((f['x']+dx)*bw)/bw-f['x'];dy=round((f['y']+dy)*bh)/bh-f['y']
            if abs(dx)>1e-9 or abs(dy)>1e-9:
                try: move_field(f,dx,dy,candidate['crop'])
                except ValueError: self.draw_editor(); return
            r=item.rect(); old=item.original_rect
            if r!=old:
                f['x']+=r.left()/self.image_w; f['y']+=r.top()/self.image_h
                f['w']=r.width()/self.image_w; f['h']=r.height()/self.image_h
        self.command('Mover / redimensionar selección',candidate)

    def update_dirty(self):
        if self._initializing or self.design is None: return
        self.dirty=self.design.dirty; self.recheck_actions()
        self.edit_status.setText('Cambios de diseño sin guardar.' if self.dirty else ('Diseño guardado. Sin autoguardado.' if self.editable() else 'Revisión vigente o retirada: solo lectura.'))
        self.save_button.setText('Guardar diseño')
        if hasattr(self,'editor_document_note'):
            state={'PENDING':'Pendiente de aprobación','APPROVED':'Vigente','RETIRED':'Retirada'}[self.editor_version['state']]
            variant=self.api.variant(self.current_variant_id) if self.current_variant_id is not None else None
            variant_note=(' · Variante '+variant['code']+' · '+{'DRAFT':'Borrador editable','PENDING':'Pendiente de aprobación','APPROVED':'Aprobada documentalmente','RETIRED':'Retirada'}[variant['state']]) if variant else ' · Diseño de revisión'
            restriction='' if self.editable() else ('\nSolo lectura: cree una variante en borrador para editar.' if self.editor_version['state']=='APPROVED' else '\nSolo lectura: revisión retirada; no permite edición ni emisión.')
            self.editor_document_note.setText('Revisión '+self.editor_version['version']+' · '+state+variant_note+restriction)
            self.editor_document_note.setToolTip('El original Word/PDF permanece protegido. '+('Edición permitida; guardar no aprueba.' if self.editable() else 'Diseño protegido. Cree una variante en borrador desde una revisión vigente para modificar los campos.'))

    def recheck_actions(self):
        super().recheck_actions()
        if not hasattr(self,'undo_button'): return
        enabled=self.editable()
        self.new_field_button.setEnabled(enabled); self.draw_field_button.setEnabled(enabled)
        self.variant_edit_button.setVisible(not enabled)
        can_derive=bool(self.current_editor_id and self.editor_version['state']=='APPROVED')
        self.variant_edit_button.setEnabled(can_derive and self.legacy_process is None)
        self.variant_edit_button.setToolTip('Crea una copia editable de los campos sin tocar la revisión vigente. La variante requiere aprobación documental para emitir.' if can_derive else 'Solo se crean variantes de ajuste desde revisiones vigentes.')
        self.undo_button.setEnabled(enabled and bool(self.design.undo_states)); self.redo_button.setEnabled(enabled and bool(self.design.redo_states))
        for b in self.design_buttons: b.setEnabled(enabled)
        if hasattr(self,'delete_field_button'):
            selected=self.selected_indices()
            self.delete_field_button.setEnabled(enabled and bool(selected) and not any(self.fields[i].get('locked') for i in selected))
            self.delete_field_button.setToolTip('Desbloquee la posición antes de eliminar.' if any(self.fields[i].get('locked') for i in selected) else 'Eliminar los campos seleccionados; no modifica el PDF original.')
        if self.design:
            current=self.editor_record(); self.editor_version['state']=current['state']
            if not enabled: self.disable_properties()

    def undo_edit(self):
        if self.editable(): self.design.undo(); self.draw_editor()

    def redo_edit(self):
        if self.editable(): self.design.redo(); self.draw_editor()

    def reset_layout(self):
        if self.design is None: return
        self.command('Restablecer diseño guardado',copy.deepcopy(self.design.clean))

    def save_work(self):
        self.commit_pending_properties()
        if not self.editable(): return False
        try:
            self.api.save_editor_layout(self.current_editor_id,self.design.state,self.expected_layout,self.expected_source)
            self.expected_layout=copy.deepcopy(self.design.state); self.design.mark_clean()
            self.editor_version=dict(self.editor_record()); self.sync_design()
            self.refresh(); self.draw_editor(); return True
        except (ValueError,PermissionError,OSError) as ex:
            QMessageBox.warning(self,'No guardado',str(ex)); return False

    def resolve_work(self):
        if self.design is not None:self.commit_pending_properties()
        if self.design is None or not self.design.dirty: return True
        answer=QMessageBox.question(self,'Diseño sin guardar','Guardar el diseño pendiente antes de cambiar de revisión, cerrar o abrir Tkinter?',
            QMessageBox.StandardButton.Save|QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)
        if answer==QMessageBox.StandardButton.Cancel: return False
        if answer==QMessageBox.StandardButton.Save: return self.save_work()
        self.design=LayoutHistory(self.design.clean); self.draw_editor(); return True

    def poll_legacy(self):
        if self.legacy_process is None or self.legacy_process.poll() is None: return
        from ..diagnostics import event
        event('legacy_finish', returncode=self.legacy_process.returncode)
        code=self.legacy_process.returncode; self.legacy_process=None
        self.set_mutations_enabled(True); self.refresh_facets(); self.refresh()
        if self.current_editor_id is not None:
            self.editor_version=dict(self.editor_record()); self.expected_layout=layout_from_version(self.editor_version)
            self.expected_source=source_identity(self.editor_version)
            self.design=LayoutHistory(self.expected_layout); self.draw_editor(fit=True)
        self.recheck_actions(); self.statusBar().showMessage('Tkinter cerrado; diseño recargado.' if code==0 else f'Tkinter terminó con código {code}. Revisar antes de continuar.')

    def editable_variant(self):
        if self.current_editor_id is None or self.editor_version['state']!='APPROVED':return
        if QMessageBox.question(self,'Ajustar campos de revisión vigente',
            'Se creará una variante en BORRADOR para recolocar, redimensionar y configurar campos. '
            'La revisión aprobada y sus originales permanecerán intactos. '
            'La variante NO podrá utilizarse para emisión definitiva hasta su aprobación documental. '
            '¿Crear una variante editable?',
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Yes:return
        self.select_version(self.current_editor_id)
        self.library_variant_id=self.current_variant_id
        self.create_variant_ui(self.current_variant_id is not None,field_adjustment=True)

    def draw_new_field(self):
        if not self.editable(): return
        if self.canvas.drawing:
            self.canvas.end_draw();self.draw_field_button.setText('Dibujar campo');return
        self.canvas.begin_draw();self.draw_field_button.setText('Cancelar dibujo')
        self.statusBar().showMessage('Arrastre un rectángulo sobre la etiqueta. Después edite sus propiedades a la derecha.')

    def add_field_from_canvas(self, region):
        self.draw_field_button.setText('Dibujar campo')
        if not self.editable():return
        region=region.intersected(QRectF(0,0,self.image_w,self.image_h))
        if region.width()<5 or region.height()<5:
            self.statusBar().showMessage('Área demasiado pequeña. Dibuje un rectángulo dentro de la etiqueta.');return
        self.quick_add_field([region.x()/self.image_w,region.y()/self.image_h,region.width()/self.image_w,region.height()/self.image_h])

    def quick_add_field(self, rect=None):
        if not self.editable():return
        existing={f['key'] for f in self.fields};number=1
        while f'campo_{number}' in existing:number+=1
        x,y,width,height=rect if isinstance(rect,list) else [.1,.1,.4,.08]
        candidate=copy.deepcopy(self.design.state)
        candidate['fields'].append(dict(key=f'campo_{number}',label=f'Campo {number}',x=x,y=y,w=width,h=height,font_pt=12,bold=False,required=False,locked=False,draw='textbox'))
        if self.command('Añadir campo',candidate):
            self.field_list.setCurrentRow(len(self.fields)-1)
            self.name_input.setFocus();self.name_input.selectAll()

    def add_field(self, rect=None):
        if not self.editable(): return
        dialog=QDialog(self); dialog.setWindowTitle('Nuevo campo variable'); layout=vbox(dialog); form=QFormLayout()
        key=QLineEdit(); name=QLineEdit(); size=spin(12,80,' pt',3)
        kind=QComboBox()
        for text,value in [('Texto','textbox'),('Numeración','numero'),('Texto fijo','texto_fijo'),('Párrafo','paragraph'),('Línea base','baseline')]: kind.addItem(text,value)
        kind.currentIndexChanged.connect(lambda *_: key.setText(kind.currentData()) if kind.currentData() in ('numero','texto_fijo') else None)
        fixed=QLineEdit();form.addRow('Contenido de texto fijo',fixed)
        required=QCheckBox('Obligatorio'); locked=QCheckBox('Bloqueado'); bold=QCheckBox('Negrita')
        for title,e in [('Identificador único',key),('Etiqueta',name),('Tipo / dibujo',kind),('Tamaño de fuente',size)]:form.addRow(title,e)
        layout.addLayout(form)
        for e in (required,locked,bold):layout.addWidget(e)
        error=label('Fuente del motor PDF: Arial o alternativa compatible.','subtle');layout.addWidget(error)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);layout.addWidget(buttons)
        def accept():
            k=key.text().strip()
            if not k or any(f['key']==k for f in self.fields):error.setText('Introduzca un identificador único.');return
            dialog.accept()
        buttons.accepted.connect(accept);buttons.rejected.connect(dialog.reject)
        if dialog.exec()!=QDialog.DialogCode.Accepted:return
        x,y,w,h=rect if isinstance(rect,list) else [.1,.1,.4,.08]
        mode=kind.currentData(); k=key.text().strip()
        candidate=copy.deepcopy(self.design.state)
        candidate['fields'].append(dict(key=k,label=name.text().strip() or k,x=x,y=y,w=w,h=h,font_pt=size.value(),bold=bold.isChecked(),required=required.isChecked(),locked=locked.isChecked(),draw=mode if mode not in ('numero','texto_fijo') else 'textbox',text=fixed.text()))
        self.command('Agregar campo',candidate)

    def remove_field(self):
        indices=self.selected_indices()
        if not self.editable() or not indices: return
        if QMessageBox.question(self,'Quitar campos',f'Quitar {len(indices)} campo(s) del diseño pendiente?')!=QMessageBox.StandardButton.Yes: return
        candidate=copy.deepcopy(self.design.state)
        candidate['fields']=[f for i,f in enumerate(candidate['fields']) if i not in indices]
        self.command('Quitar campos',candidate)

    def edit_crop(self):
        if not self.editable(): return
        try:
            image,rect,_=self.api.master_preview(self.editor_version,width=950,height=700)
            dialog=RectangleDialog(self,'Recorte del documento',image,list(rect),self.design.state['crop'],20)
            if dialog.exec()==QDialog.DialogCode.Accepted:
                self.apply_operation('Recorte',lambda:recrop(self.design.state,dialog.selection_rect))
                self.canvas.fit()
        except (ValueError,OSError) as ex: QMessageBox.warning(self,'Recorte no disponible',str(ex))

    def edit_status_area(self):
        if not self.editable(): return
        c=self.design.state['crop']; w=c[2]-c[0]; h=c[3]-c[1]
        a=self.design.state['area'] or [.08,.77,.84,.15]; rect=[a[0]*w,a[1]*h,(a[0]+a[2])*w,(a[1]+a[3])*h]
        image=self.api.thumbnail(self.editor_version,width_px=1000)
        dialog=RectangleDialog(self,'Reserva para etiqueta de estado',image,[0,0,w,h],rect)
        use=QCheckBox('Usar zona de estado'); use.setChecked(True); dialog.extra.addWidget(use)
        master=QComboBox(); master.addItem('Sin referencia de proporción',None)
        for m in self.api.status_masters(): master.addItem(m['name']+' / '+m['version']+' / '+m['state'],dict(m))
        dialog.extra.addWidget(master)
        if dialog.exec()!=QDialog.DialogCode.Accepted: return
        r=dialog.selection_rect; area=[r[0]/w,r[1]/h,(r[2]-r[0])/w,(r[3]-r[1])/h] if use.isChecked() else []
        m=master.currentData()
        if area and m:
            mc=json.loads(m['crop_json']); ratio=(mc[2]-mc[0])/(mc[3]-mc[1]); actual=(r[2]-r[0])/(r[3]-r[1])
            if abs(actual/ratio-1)>.01:
                if QMessageBox.question(self,'Proporción de estado',f'Reserva con proporción distinta del maestro seleccionado ({ratio:.3f}). Puede dejar espacios blancos. Conservar como diseño pendiente?')!=QMessageBox.StandardButton.Yes: return
        candidate=copy.deepcopy(self.design.state); candidate['area']=area; self.command('Zona de estado',candidate)

    def edit_anchor(self):
        indices=self.selected_indices()
        if not self.editable() or len(indices)!=1:
            QMessageBox.information(self,'Anclaje','Seleccione un único campo editable.'); return
        try:
            spans=self.api.editor_spans(self.current_editor_id)
            if not spans: raise ValueError('PDF sin texto extraíble. Ubique el campo manualmente; no se realiza OCR.')
            image,rect,_=self.api.master_preview(self.editor_version,width=1000,height=650)
            dialog=QDialog(self); dialog.setWindowTitle('Referencia PDF / Word convertido'); dialog.resize(1000,650)
            layout=vbox(dialog); layout.addWidget(label('Selecciona el texto fijo inmediatamente anterior al campo. Las coincidencias repetidas requieren elección explícita.','subtle'))
            search=QLineEdit(); search.setPlaceholderText('Buscar texto de referencia'); layout.addWidget(search)
            body=QSplitter(); ls=QListWidget(); view=RectangleView(image,list(rect),lambda *_:None); body.addWidget(ls); body.addWidget(view); body.setSizes([300,650]); layout.addWidget(body,1)
            for i,sp in enumerate(spans):
                ls.addItem(f"{sp['bbox'][0]*MM_PER_POINT:.1f}, {sp['bbox'][1]*MM_PER_POINT:.1f} mm · {sp['text']}")
                ls.item(i).setData(Qt.ItemDataRole.UserRole,i)
            search.textChanged.connect(lambda text:[ls.item(i).setHidden(text.casefold() not in spans[i]['text'].casefold()) for i in range(len(spans))])
            ls.currentRowChanged.connect(lambda i:view.paint_rect(spans[i]['bbox']) if i>=0 else None)
            buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(lambda:dialog.accept() if ls.currentRow()>=0 and not ls.currentItem().isHidden() else None); buttons.rejected.connect(dialog.reject); layout.addWidget(buttons)
            if dialog.exec()==QDialog.DialogCode.Accepted:
                pos=ls.currentItem().data(Qt.ItemDataRole.UserRole); sp=spans[pos]
                occurrence=sum(s['text']==sp['text'] for s in spans[:pos])
                self.apply_operation('Anclar a texto',lambda:anchor_field(self.design.state,indices[0],sp,occurrence,self.editor_version['pdf_sha256']))
        except (ValueError,OSError) as ex: QMessageBox.warning(self,'Anclaje no disponible',str(ex))

    def relocate(self):
        if not self.editable(): return
        anchored=any(f.get('anchor') for f in self.fields)
        message=('Relocalizar solo anclas verificables de la misma fuente, conservando desplazamientos?' if anchored else 'Recalcular solo con plantilla reconocida ACETONA/EDROFONIO? Sustituye campos y zona de estado; puede deshacerse.')
        message+='\nNo adapta automáticamente el diseño a cualquier nueva revisión Word/PDF.'
        if QMessageBox.question(self,'Relocalización',message)!=QMessageBox.StandardButton.Yes: return
        operation=(lambda:relocate_anchors(self.design.state,self.api.editor_spans(self.current_editor_id),self.editor_version['pdf_sha256'])) if anchored else (lambda:self.api.editor_template_layout(self.current_editor_id,self.design.state['crop']))
        self.apply_operation('Relocalizar referencias',operation)

    def align_selection(self):
        self.apply_operation('Alinear selección',lambda:align_fields(self.design.state,self.selected_indices(),self.alignment.currentData()))

    def edit_scale(self):
        if not self.editable(): return
        dialog=QDialog(self); dialog.setWindowTitle('Reajuste proporcional de campos'); layout=vbox(dialog)
        layout.addWidget(label('Transforma campos variables autorizados. El fondo fijo y el tamaño físico de salida no cambian.','subtle'))
        factor=spin(100,1000,' %',1); layout.addWidget(factor)
        font=QCheckBox('Escalar también tipografía'); font.setChecked(True); layout.addWidget(font)
        area=QCheckBox('Incluir zona de estado'); layout.addWidget(area)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject); layout.addWidget(buttons)
        if dialog.exec()==QDialog.DialogCode.Accepted:
            self.apply_operation('Reajuste proporcional',lambda:scale_fields(self.design.state,self.selected_indices(),factor.value()/100,font.isChecked(),area.isChecked()))

    def edit_auxiliary(self):
        indices=self.selected_indices()
        if not self.editable() or len(indices)!=1: return
        f=self.fields[indices[0]]; w=self.editor_version['base_w_mm']; h=self.editor_version['base_h_mm']
        dialog=QDialog(self); dialog.setWindowTitle('Borrado y continuación del campo'); layout=vbox(dialog)
        layout.addWidget(label('Zona de borrado autorizada en el PDF derivado; no modifica el original. Coordenadas desde el recorte.','subtle'))
        enabled=QCheckBox('Usar zona de borrado'); enabled.setChecked(bool(f.get('erase'))); layout.addWidget(enabled)
        form=QFormLayout(); entries=[]
        erase=f.get('erase') or [f['x'],f['y'],f['w'],f['h']]
        for name,val,dim in zip(('Borrado X','Borrado Y','Borrado ancho','Borrado alto'),erase,(w,h,w,h)):
            entry=spin(val*dim); form.addRow(name,entry); entries.append(entry)
        sx=spin(f.get('second_x',f['x'])*w); nw=spin(f.get('next_w',f['w'])*w); lines=spin(f.get('max_lines',3),20,' líneas',1); lines.setDecimals(0)
        form.addRow('Segunda línea X',sx); form.addRow('Ancho continuación',nw); form.addRow('Máximo de líneas',lines); layout.addLayout(form)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject); layout.addWidget(buttons)
        if dialog.exec()!=QDialog.DialogCode.Accepted: return
        candidate=copy.deepcopy(self.design.state); field=candidate['fields'][indices[0]]
        if field.get('locked'): QMessageBox.information(self,'Campo bloqueado','Desbloquee el campo para modificar su geometría auxiliar.'); return
        if enabled.isChecked(): field['erase']=[s.value()/d for s,d in zip(entries,(w,h,w,h))]
        else: field.pop('erase',None)
        if field.get('draw')=='continuation': field.update(second_x=sx.value()/w,next_w=nw.value()/w,max_lines=int(lines.value()))
        self.command('Borrado / continuación',candidate)

    def edit_output(self):
        if self.design is None or self.legacy_process: return
        dialog=QDialog(self); dialog.setWindowTitle('Formato físico y prueba PDF'); dialog.resize(690,630); layout=vbox(dialog)
        layout.addWidget(label('Escala física proporcional del motor existente. No es zoom ni cambia el diseño. Seleccione el perfil guardado en su trabajo del Centro de emisión.','subtle'))
        profiles=[dict(p) for p in self.api.profile_list()]; combo=QComboBox(); combo.addItem('Medidas del diseño',None)
        for p in profiles: combo.addItem(p['name'],p)
        layout.addWidget(combo)
        profile=self.output_profile or dict(name='',width_mm=self.editor_version['base_w_mm'],height_mm=self.editor_version['base_h_mm'],paper='A4',orientation='portrait',margin_mm=8,gap_mm=3,offset_x_mm=0,offset_y_mm=0,start_slot=1,crop_marks=0,printer_name='',safety_mm=0)
        form=QFormLayout(); inputs={}
        for key,title in [('width_mm','Ancho de casilla'),('height_mm','Alto de casilla'),('margin_mm','Margen A4'),('gap_mm','Separación'),('safety_mm','Seguridad interior')]:
            entry=spin(profile[key],1000,minimum=.1 if key in ('width_mm','height_mm') else 0); form.addRow(title,entry); inputs[key]=entry
        orientation=QComboBox(); orientation.addItem('A4 vertical','portrait'); orientation.addItem('A4 horizontal','landscape'); orientation.setCurrentIndex(orientation.findData(profile['orientation'])); form.addRow('Hoja',orientation)
        name=QLineEdit(profile.get('name','')); form.addRow('Nombre para guardar perfil',name); layout.addLayout(form)
        summary=label('','subtle'); layout.addWidget(summary)
        def current():
            p=copy.deepcopy(profile); p.update({k:e.value() for k,e in inputs.items()}); p['orientation']=orientation.currentData(); p['name']=name.text().strip(); return p
        def update(*_):
            p=current(); bw=self.editor_version['base_w_mm']; bh=self.editor_version['base_h_mm']; factor=min(p['width_mm']/bw,p['height_mm']/bh)
            try:
                plan=self.api.sheet_plan(p,1)
                summary.setText(f"Etiqueta impresa: {bw*factor:.3f} × {bh*factor:.3f} mm · Escala {factor*100:.2f}% · {plan.capacity} casillas. Verificar impresión al 100 %.")
            except ValueError as ex: summary.setText(str(ex))
        def choose(index):
            chosen=combo.itemData(index)
            if chosen:
                profile.update(chosen)
                for k,e in inputs.items(): e.setValue(profile[k])
                name.setText(profile['name']); orientation.setCurrentIndex(orientation.findData(profile['orientation']))
            update()
        combo.currentIndexChanged.connect(choose)
        for e in inputs.values(): e.valueChanged.connect(update)
        orientation.currentIndexChanged.connect(update); update()
        def proof():
            try:
                self.output_profile=current(); path,warnings=self.api.preview_editor_layout(self.current_editor_id,self.design.state,self.output_profile)
                image,count=self.api.preview_pdf(path,maxwidth=1000)
                preview=QDialog(dialog); preview.setWindowTitle('PDF de prueba — sin emisión definitiva'); preview.resize(800,800); pl=vbox(preview)
                pl.addWidget(label('Renderizado por el motor PDF con datos variables vacíos. No prueba datos de trabajo ni registra historial.','subtle'))
                view=Preview(); view.set_image(image); pl.addWidget(view,1)
                summary=f"{warnings['physical']} etiquetas de prueba · {warnings['pages']} hojas A4. Impresión al 100 %, sin ajustar a página."
                if warnings.get('warnings'):summary+='\nAvisos: '+' · '.join(warnings['warnings'])
                note=label(summary,'subtle');note.setWordWrap(True);pl.addWidget(note)
                close=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);close.button(QDialogButtonBox.StandardButton.Close).setText('Cerrar');close.rejected.connect(preview.reject);pl.addWidget(close);preview.exec()
            except (ValueError,OSError) as ex: QMessageBox.warning(dialog,'Prueba no generada',str(ex))
        def save_profile():
            p=current()
            try:
                if not p['name']: raise ValueError('Nombre de perfil obligatorio.')
                self.api.sheet_plan(p,1)
                if any(x['name']==p['name'] for x in profiles):
                    if QMessageBox.question(dialog,'Actualizar perfil','Actualizar el perfil existente? No cambia ni aprueba el diseño.')!=QMessageBox.StandardButton.Yes: return
                self.api.add_profile(p); self.output_profile=p; summary.setText('Perfil guardado. Selecciónelo en el Centro de emisión; los datos variables pertenecen al trabajo.')
            except (ValueError,OSError) as ex: QMessageBox.warning(dialog,'Perfil no guardado',str(ex))
        layout.addWidget(button('Ver PDF de prueba',proof)); layout.addWidget(button('Guardar perfil de salida',save_profile))
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel); buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject); layout.addWidget(buttons)
        if dialog.exec()==QDialog.DialogCode.Accepted: self.output_profile=current()

