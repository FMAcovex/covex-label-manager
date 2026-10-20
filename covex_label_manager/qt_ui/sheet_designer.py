"""Native millimetre sheet designer; edits an isolated copy until acceptance."""
import copy
import re
from dataclasses import asdict
from PySide6.QtCore import Qt, QRectF, QTimer
from PySide6.QtGui import QColor, QPen, QBrush, QPalette
from PySide6.QtWidgets import (QDialog,QWidget,QHBoxLayout,QFormLayout,QComboBox,QSpinBox,
 QDoubleSpinBox,QCheckBox,QDialogButtonBox,QScrollArea,QLineEdit,QInputDialog,QGraphicsItem,QGridLayout)
from .window import vbox,label,button,Preview,pixmap
from .responsive import AdaptiveDialog as QDialog
from .resize_item import ResizableRect
from ..sheet_layout import PAPERS,paper_size,slots,template
from ..engine import plan_sheet
from ..editor_layout import LayoutHistory
from ..layout_profiles import LayoutProfiles

class ProfileHistory(LayoutHistory):
    # Sheet drafts may temporarily be invalid. Acceptance/rendering validate them.
    def push(self,state,title):
        if state==self.state:return False
        self.undo_states.append((copy.deepcopy(self.state),title));self.redo_states.clear();self.state=copy.deepcopy(state);return True

class SlotItem(ResizableRect):
    def __init__(self,box,index,owner,editable):
        super().__init__(0,0,box.width,box.height);self.index=index;self.owner=owner;self.released=owner.gesture;self.feedback=owner.selection
        self.setPos(box.x,box.y);self.setPen(QPen(QColor('#147D71'),.4));self.setBrush(QBrush(QColor(20,125,113,35)))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable,editable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,editable)
        self.enable_handles(editable)
    def mousePressEvent(self,e):
        self.setFocus();super().mousePressEvent(e)
    def mouseMoveEvent(self,e):
        super().mouseMoveEvent(e);self.owner.selection()
    def mouseReleaseEvent(self,e):super().mouseReleaseEvent(e);self.released()
    def keyPressEvent(self,e):
        delta={Qt.Key.Key_Left:(-1,0),Qt.Key.Key_Right:(1,0),Qt.Key.Key_Up:(0,-1),Qt.Key.Key_Down:(0,1)}.get(e.key())
        if delta and self.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsMovable:
            step=.1 if e.modifiers() & Qt.KeyboardModifier.ShiftModifier else 1
            self.moveBy(delta[0]*step,delta[1]*step);self.released();e.accept()
        else:super().keyPressEvent(e)

class OccupiedSlotsDialog(QDialog):
    """Choose already-used label stock locations on the FIRST physical sheet."""
    def __init__(self,parent,capacity,start,occupied):
        super().__init__(parent)
        self.setWindowTitle('Casillas ya utilizadas · primera hoja')
        self.resize(520,510)
        layout=vbox(self,12,9)
        note=label('Marque las casillas que ya contienen una etiqueta o no pueden reutilizarse. '
                   'Las anteriores a la casilla inicial ya se omiten. '
                   'Las hojas siguientes comienzan completamente libres.','subtle')
        note.setWordWrap(True);layout.addWidget(note)
        area=QScrollArea();area.setWidgetResizable(True)
        content=QWidget();grid=QGridLayout(content)
        self.checks={}
        for index in range(1,capacity+1):
            check=QCheckBox(str(index))
            if index<start:
                check.setChecked(True);check.setEnabled(False)
                check.setToolTip('Ya reservada por la casilla inicial.')
            else:
                check.setChecked(index in occupied)
                check.setToolTip(f'Casilla {index}: marcar si ya se ha usado.')
            self.checks[index]=check
            grid.addWidget(check,(index-1)//6,(index-1)%6)
        area.setWidget(content);layout.addWidget(area,1)
        layout.addWidget(label('Las casillas marcadas NO recibirán contenido del PDF. '
                               'Verifique físicamente el sentido de carga del papel.','subtle'))
        actions=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        actions.accepted.connect(self.accept);actions.rejected.connect(self.reject)
        layout.addWidget(actions)
        self.start_slot=start

    def occupied(self):
        return [i for i,box in self.checks.items() if i>=self.start_slot and box.isChecked()]


class SheetDesigner(QDialog):
    def __init__(self,parent,profile,proof=None,root=None,counts='',thumbnail=None,nominal=None,quantities=None):
        super().__init__(parent);self.setWindowTitle('Diseñador de hojas · mm');self.resize(1120,700)
        # AdaptiveDialog applies the available-screen bounds when shown. Avoid
        # borrowing a QScreen wrapper from this transient dialog at construction.
        self.thumbnail=thumbnail;self.nominal=nominal
        self.initial_quantities = dict(quantities or {})
        self.history=ProfileHistory(copy.deepcopy(profile));self.profile=copy.deepcopy(profile);self.proof=proof;self.busy=False;self.items=[];self.repo=LayoutProfiles(root) if root else None
        palette=self.palette()
        for role,colour in ((QPalette.ColorRole.Window,'#F4F7F8'),(QPalette.ColorRole.Base,'#FFFFFF'),(QPalette.ColorRole.Text,'#203B40'),(QPalette.ColorRole.WindowText,'#203B40'),(QPalette.ColorRole.Button,'#FFFFFF'),(QPalette.ColorRole.ButtonText,'#203B40')):palette.setColor(role,QColor(colour))
        self.setPalette(palette)
        self.setStyleSheet('QDialog { background:#F4F7F8; color:#203B40; }')
        layout=vbox(self,10,6);layout.addWidget(label('Posiciones por hoja ≠ recipientes ≠ copias por recipiente','panelTitle'))
        layout.addWidget(label(counts+' · El contenido se escala proporcionalmente. Papel sujeto a prueba física; imprimir al 100 %.','subtle'))
        row=QHBoxLayout();self.view=Preview();self.view.setDragMode(Preview.DragMode.RubberBandDrag);row.addWidget(self.view,1)
        panel=QWidget();form=QFormLayout(panel);form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows);self.property_form=form;scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(panel);scroll.setMinimumWidth(270);scroll.setMaximumWidth(340);row.addWidget(scroll);layout.addLayout(row,1)
        self.paper=QComboBox();self.paper.addItems([*PAPERS,'custom']);form.addRow('Papel',self.paper)
        self.orientation=QComboBox();self.orientation.addItem('Vertical','portrait');self.orientation.addItem('Horizontal','landscape');form.addRow('Orientación',self.orientation)
        self.mode=QComboBox();self.mode.addItem('Cuadrícula clásica','grid');self.mode.addItem('Distribución libre','free');form.addRow('Composición',self.mode)
        self.measures={}
        for key,title,default,low,high in [('paper_width_mm','Papel ancho',210,50,1000),('paper_height_mm','Papel alto',297,50,1000),('width_mm','Casilla ancho',80,5,1000),('height_mm','Casilla alto',50,5,1000),('margin_mm','Margen',8,0,40),('gap_mm','Separación',3,0,50),('start_slot','Casilla inicial',1,1,1000)]:
            e=QDoubleSpinBox();e.setDecimals(0 if key=='start_slot' else 2);e.setRange(low,high);e.setValue(float(profile.get(key,default)));e.setSuffix('' if key=='start_slot' else ' mm');form.addRow(title,e);self.measures[key]=e
            e.valueChanged.connect(self.controls_changed)
        for key in ('width_mm','height_mm'):
            self.measures[key].setToolTip('Entre 5 y 10 mm requiere activar «Permitir etiqueta mini» en Formato y emisión.')
        self.count=QSpinBox();self.count.setRange(1,100);self.count.setValue(len(profile.get('slots',[])) or 5);form.addRow('Posiciones / hoja',self.count)
        # Quantity and sheet geometry are edited together in a detached draft.
        self.vessel_count=QSpinBox();self.vessel_count.setRange(1,10000)
        self.vessel_count.setValue(int(self.initial_quantities.get('count',1)))
        self.copy_count=QSpinBox();self.copy_count.setRange(1,2)
        self.copy_count.setValue(int(self.initial_quantities.get('copies',1)))
        form.addRow('Recipientes del trabajo',self.vessel_count)
        form.addRow('Copias por recipiente',self.copy_count)
        self.quantity_summary=label('','subtle');self.quantity_summary.setWordWrap(True)
        form.addRow(self.quantity_summary)
        for control in (self.vessel_count,self.copy_count):
            control.valueChanged.connect(self.quantities_changed)
        form.addRow(button('Distribuir estas posiciones',self.arrange))
        form.addRow(button('Ajustar automáticamente',self.auto_arrange))
        self.used_slots_button=button('Marcar casillas ya utilizadas…',self.mark_used_slots)
        form.addRow(self.used_slots_button)
        self.snap=QCheckBox('Snap a 1 mm');self.grid=QCheckBox('Cuadrícula de 10 mm');self.grid.setChecked(True);self.grid.toggled.connect(self.redraw);form.addRow(self.snap);form.addRow(self.grid)
        self.box_inputs={}
        for k,t in [('x','X'),('y','Y'),('width','Ancho'),('height','Alto')]:
            e=QDoubleSpinBox();e.setDecimals(2);e.setRange(0,1000);e.setSuffix(' mm');form.addRow('Selección '+t,e);self.box_inputs[k]=e;e.editingFinished.connect(self.numeric_box)
        align=QComboBox();align.addItems(['Izquierda','Arriba','Centrar en hoja','Distribuir horizontal','Distribuir vertical']);form.addRow(align)
        form.addRow(button('Alinear selección',lambda:self.align(align.currentIndex())))
        form.addRow(button('Eliminar selección',self.remove))
        form.addRow(button('Ver PDF de prueba real',self.preview))
        if self.repo:
            self.saved=QComboBox();self.saved.addItem('Perfil reutilizable…',None)
            for p in self.repo.list(tolerate_corrupt=True):self.saved.addItem(p['name'],p)
            self.saved.activated.connect(self.load_profile);form.addRow(self.saved);form.addRow(button('Guardar perfil…',self.save_profile))
            if self.repo.invalid_files:
                self.profile_corruption_warning=label(
                    f'Hay {len(self.repo.invalid_files)} perfil(es) no legibles. No se han alterado. '
                    'Revise los archivos con Calidad/IT antes de utilizarlos.', 'fieldError')
                self.profile_corruption_warning.setWordWrap(True)
                form.addRow(self.profile_corruption_warning)
        self.error=label('','subtle');layout.addWidget(self.error)
        actions=QHBoxLayout()
        for t,fn in [('Deshacer',self.undo),('Rehacer',self.redo),('Restablecer',self.reset),('Ajustar vista',self.view.fit),('+',lambda:self.view.zoom(1.2)),('−',lambda:self.view.zoom(1/1.2))]:actions.addWidget(button(t,fn))
        layout.addLayout(actions)
        self.buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText('Aplicar al trabajo');self.buttons.accepted.connect(self.accept_valid);self.buttons.rejected.connect(self.reject);layout.addWidget(self.buttons)
        for e in (self.paper,self.orientation,self.mode):e.currentIndexChanged.connect(self.controls_changed)
        self.view.scene().selectionChanged.connect(self.selection)
        self.sync();self.redraw();self.update_quantity_summary();QTimer.singleShot(0,self.view,self.view.fit)

    def sync(self):
        self.busy=True;p=self.profile
        self.paper.setCurrentText(p.get('paper','A4'));self.orientation.setCurrentIndex(max(0,self.orientation.findData(p.get('orientation','portrait'))));self.mode.setCurrentIndex(max(0,self.mode.findData(p.get('layout_mode','grid'))))
        for k,e in self.measures.items():e.setValue(float(p.get(k,210 if k=='paper_width_mm' else 297 if k=='paper_height_mm' else e.value())))
        for k in ('paper_width_mm','paper_height_mm'):self.property_form.setRowVisible(self.measures[k],p.get('paper')=='custom')
        for k in ('width_mm','height_mm'):self.property_form.setRowVisible(self.measures[k],p.get('layout_mode','grid')=='grid')
        self.busy=False
    def push(self,p,title):
        self.history.push(p,title);self.profile=copy.deepcopy(self.history.state);self.sync();self.redraw();self.update_quantity_summary()
    def controls_changed(self,*_):
        if self.busy:return
        p=copy.deepcopy(self.profile);p.update(layout_version=1,paper=self.paper.currentText(),orientation=self.orientation.currentData(),layout_mode=self.mode.currentData())
        p.update({k:int(e.value()) if k=='start_slot' else e.value() for k,e in self.measures.items()})
        if p['layout_mode']=='free' and not p.get('slots'):p['slots']=template(p,self.count.value())
        self.push(p,'Propiedades de hoja')
    def arrange(self):
        p=copy.deepcopy(self.profile);p.update(layout_version=1,layout_mode='free',offset_x_mm=0,offset_y_mm=0,start_slot=1);p['slots']=template(p,self.count.value());p.pop('occupied_slots',None);self.push(p,'Distribución automática')
    def auto_arrange(self):
        p=copy.deepcopy(self.profile);p.update(layout_version=1,layout_mode='grid',start_slot=1);p.pop('slots',None);p.pop('occupied_slots',None);self.push(p,'Cuadrícula automática')

    def mark_used_slots(self):
        # Inspect the current geometry without an existing occupancy mask.
        from ..sheet_layout import available_first_page
        profile=copy.deepcopy(self.profile);profile.pop('occupied_slots',None)
        try:
            plan=plan_sheet(profile,1)
            occupied=self.profile.get('occupied_slots',[])
            if not isinstance(occupied,list):
                raise ValueError('Lista de casillas utilizadas no válida.')
            dialog=OccupiedSlotsDialog(self,plan.capacity,int(profile.get('start_slot',1)),occupied)
            if dialog.exec()!=QDialog.DialogCode.Accepted:return
            profile['layout_version']=1
            chosen=dialog.occupied()
            if chosen:profile['occupied_slots']=chosen
            self.push(profile,'Reservar casillas de la primera hoja')
        except (ValueError,TypeError,KeyError) as ex:
            self.error.setText('No se han actualizado las casillas: '+str(ex))
    def redraw(self,*_):
        self.busy=True;scene=self.view.scene();scene.clear();self.items=[]
        try:
            pw,ph=paper_size(self.profile);scene.addRect(0,0,pw,ph,QPen(QColor('#82999D'),.4),QBrush(QColor('white')))
            if self.grid.isChecked():
                for x in range(0,int(pw)+1,10):scene.addLine(x,0,x,ph,QPen(QColor('#E3EBED'),.15))
                for y in range(0,int(ph)+1,10):scene.addLine(0,y,pw,y,QPen(QColor('#E3EBED'),.15))
            for x in range(0,int(pw)+1,20):
                t=scene.addText(str(x));t.setScale(.24);t.setPos(x,-6)
            for y in range(0,int(ph)+1,20):
                t=scene.addText(str(y));t.setScale(.24);t.setPos(-9,y)
            m=float(self.profile.get('margin_mm',8));scene.addRect(m,m,pw-2*m,ph-2*m,QPen(QColor('#C49F65'),.3,Qt.PenStyle.DashLine))
            # Display invalid free boxes too, with an explicit blocking error below.
            if self.profile.get('layout_mode')=='free':
                from ..sheet_layout import LayoutSlot
                try:boxes=slots(self.profile)
                except ValueError:
                    ox=float(self.profile.get('offset_x_mm',0));oy=float(self.profile.get('offset_y_mm',0))
                    boxes=[LayoutSlot(s['x']+ox,s['y']+oy,s['width'],s['height']) for s in self.profile.get('slots',[])]
            else:boxes=slots(self.profile)
            reserved=set(self.profile.get('occupied_slots',[]))
            start=int(self.profile.get('start_slot',1))
            from ..emission_work import selection_indices
            from ..sheet_layout import physical_placements
            selected_count=len(selection_indices(
                self.initial_quantities.get('selection',''),self.vessel_count.value()))
            physical=selected_count*self.copy_count.value()
            planned_first=set()
            # Rendering must never depend on a successful emission plan:
            # otherwise the first invalid free position silently clears ALL
            # boxes from the canvas, making recovery with the mouse impossible.
            plan_error=None
            try:
                plan=plan_sheet(self.profile,1)
                for page_number,slot_index in physical_placements(self.profile,plan.capacity,physical):
                    if page_number>0:break
                    planned_first.add(slot_index)
            except (ValueError,KeyError,TypeError) as ex:
                plan_error=str(ex)
                # Show the intended first-sheet occupants for editing only.
                # These are NOT an emission authorization or physical plan.
                for index in range(max(0,start-1),len(boxes)):
                    if index+1 not in reserved:
                        planned_first.add(index)
                        if len(planned_first)>=physical:break
            invalid_positions=set()
            if plan_error:
                match=re.search(r'(?:Posición|Solapamiento en posición) (\d+)',plan_error)
                if match:invalid_positions.add(int(match.group(1)))
            for i,b in enumerate(boxes):
                item=SlotItem(b,i,self,self.profile.get('layout_mode')=='free');scene.addItem(item);self.items.append(item)
                invalid=i+1 in invalid_positions
                if invalid:
                    item.setBrush(QBrush(QColor(198,62,51,85)))
                    item.setPen(QPen(QColor('#C63E33'),1))
                    item.setToolTip(f'Posición {i+1}: {plan_error}. Corrija sus dimensiones o desplácela dentro del margen.')
                elif i+1<start or i+1 in reserved:
                    item.setBrush(QBrush(QColor(191,74,65,100)))
                    item.setPen(QPen(QColor('#AD4742'),.55))
                if self.thumbnail and i in planned_first and b.width>0 and b.height>0:
                    image=scene.addPixmap(pixmap(self.thumbnail));image.setParentItem(item);scale=min(b.width/self.thumbnail.width,b.height/self.thumbnail.height);image.setScale(scale);image.setPos((b.width-self.thumbnail.width*scale)/2,(b.height-self.thumbnail.height*scale)/2);image.setAcceptedMouseButtons(Qt.MouseButton.NoButton);image.setZValue(-1)
                status=(' · REVISAR' if invalid else ' · USADA' if i+1<start or i+1 in reserved else ' · ETIQUETA' if i in planned_first else ' · VACÍA')
                t=scene.addText(str(i+1)+status);t.setParentItem(item);t.setScale(.3);t.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
            scene.setSceneRect(-12,-9,pw+20,ph+18)
            if plan_error:
                self.error.setText('No se puede aplicar: '+plan_error+' · Posiciones conservadas para corregirlas (rojo = revisar).')
                self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            else:
                from ..sheet_layout import available_first_page
                usable=available_first_page(self.profile,plan.capacity)
                self.error.setText(f'{pw:g} × {ph:g} mm · {plan.capacity} posiciones / hoja · {len(usable)} libres · {len(planned_first)} se imprimirán en la primera hoja · casillas rojas = ocupadas · Zoom independiente del PDF')
                self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        except (ValueError,KeyError,TypeError) as ex:
            self.error.setText('No se puede aplicar: '+str(ex));self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.busy=False
    def selection(self):
        if self.busy:return
        selected=[i for i in self.items if i.isSelected()]
        if not selected:return
        b=selected[0];r=b.rect();vals=(b.x()+r.x(),b.y()+r.y(),r.width(),r.height())
        for e,v in zip(self.box_inputs.values(),vals):e.setValue(v)
        if self.nominal:
            scale=min(vals[2]/self.nominal[0],vals[3]/self.nominal[1]);self.error.setText(f'Selección: {vals[0]:.2f}, {vals[1]:.2f} mm · Caja {vals[2]:.2f} × {vals[3]:.2f} mm · Contenido efectivo {self.nominal[0]*scale:.2f} × {self.nominal[1]*scale:.2f} mm · Escala {scale*100:.1f}%')
    def gesture(self):
        if self.profile.get('layout_mode')!='free':return
        p=copy.deepcopy(self.profile);boxes=[]
        for b in self.items:
            r=b.rect();v=[b.x()+r.x()-float(p.get('offset_x_mm',0)),b.y()+r.y()-float(p.get('offset_y_mm',0)),r.width(),r.height()]
            if self.snap.isChecked():v=[round(x) for x in v]
            boxes.append(dict(zip(('x','y','width','height'),v)))
        p['slots']=boxes;self.push(p,'Mover / redimensionar posiciones')
    def numeric_box(self):
        selected=[i.index for i in self.items if i.isSelected()]
        if self.profile.get('layout_mode')!='free' or not selected:return
        p=copy.deepcopy(self.profile);p['slots'][selected[0]]={k:e.value() for k,e in self.box_inputs.items()}
        p['slots'][selected[0]]['x']-=float(p.get('offset_x_mm',0));p['slots'][selected[0]]['y']-=float(p.get('offset_y_mm',0));self.push(p,'Medidas de posición')
    def align(self,mode):
        selected=[i.index for i in self.items if i.isSelected()]
        if self.profile.get('layout_mode')!='free' or not selected:return
        p=copy.deepcopy(self.profile);boxes=[p['slots'][i] for i in selected];pw,ph=paper_size(p)
        for b in boxes:
            if mode==0:b['x']=min(x['x'] for x in boxes)
            elif mode==1:b['y']=min(x['y'] for x in boxes)
            elif mode==2:b['x']=(pw-b['width'])/2;b['y']=(ph-b['height'])/2
        if mode in (3,4) and len(boxes)>2:
            k,dim=('x','width') if mode==3 else ('y','height');ordered=sorted(boxes,key=lambda b:b[k]);end=ordered[-1][k]+ordered[-1][dim];gap=(end-ordered[0][k]-sum(b[dim] for b in ordered))/(len(ordered)-1);pos=ordered[0][k]
            for b in ordered:b[k]=pos;pos+=b[dim]+gap
        self.push(p,'Alinear / distribuir')
    def remove(self):
        selected={i.index for i in self.items if i.isSelected()}
        if self.profile.get('layout_mode')!='free' or not selected:return
        p=copy.deepcopy(self.profile);p['slots']=[b for i,b in enumerate(p['slots']) if i not in selected];self.push(p,'Eliminar posiciones')
    def undo(self):self.history.undo();self.profile=copy.deepcopy(self.history.state);self.sync();self.redraw();self.update_quantity_summary()
    def redo(self):self.history.redo();self.profile=copy.deepcopy(self.history.state);self.sync();self.redraw();self.update_quantity_summary()
    def reset(self):self.push(copy.deepcopy(self.history.clean),'Restablecer')
    def quantities_changed(self,*_):
        self.update_quantity_summary()
        self.redraw()

    def quantities(self):
        return {'count':str(self.vessel_count.value()),'copies':str(self.copy_count.value())}

    def update_quantity_summary(self,*_):
        try:
            from ..emission_work import selection_indices
            selected=len(selection_indices(self.initial_quantities.get('selection',''),self.vessel_count.value()))
            total=selected*self.copy_count.value()
            from ..sheet_layout import physical_placements
            plan=plan_sheet(self.profile,1)
            last=None
            for last in physical_placements(self.profile,plan.capacity,total):
                pass
            pages=last[0]+1
            self.quantity_summary.setText(
                f'{selected} recipientes elegidos · {total} etiquetas reales · {plan.capacity} posiciones por hoja · {pages} hojas. '
                'Las posiciones vacías no generan copias. '
                'Los cambios de cantidades se guardarán al aplicar el diseño.')
        except (ValueError,KeyError,TypeError) as ex:
            self.quantity_summary.setText('Distribución todavía no válida: '+str(ex))

    def accept_valid(self):
        try:plan_sheet(self.profile,1)
        except ValueError as ex:self.error.setText(str(ex));return
        self.accept()
    def preview(self):
        try:
            plan_sheet(self.profile,1)
            if self.proof:self.proof(copy.deepcopy(self.profile),self,self.quantities())
        except (ValueError,OSError) as ex:self.error.setText('PDF no generado: '+str(ex))
    def save_profile(self):
        uid,ok=QInputDialog.getText(self,'Guardar perfil','Identificador (letras, números, guion):')
        if not ok:return
        name,ok=QInputDialog.getText(self,'Guardar perfil','Nombre:')
        if not ok:return
        try:
            existing=next((p for p in self.repo.list() if p['uid']==uid),None)
            if existing:raise ValueError('Use un identificador nuevo para conservar la evidencia anterior.')
            physical=copy.deepcopy(self.profile);physical.pop('trial_appearance',None)
            self.repo.save(uid,name,physical);self.error.setText('Formato físico guardado, sin apariencia temporal ni aprobación documental. Para conservar la apariencia use Copiar trabajo o una variante.')
        except (ValueError,OSError) as ex:self.error.setText(str(ex))
    def load_profile(self,*_):
        p=self.saved.currentData()
        if p:self.push(copy.deepcopy(p['profile']),'Cargar perfil')
