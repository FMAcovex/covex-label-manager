"""Native Qt revision comparison: read-only, optional overlay and documentary changes."""
import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QHBoxLayout,QVBoxLayout,QComboBox,QSlider,QTabWidget,QWidget,QMessageBox
from .window import Preview,button,label,vbox,pixmap


class CompareDialog(QDialog):
    def __init__(self,parent,api,label_id,selected_id=None):
        super().__init__(parent)
        self.api=api
        self.versions=[dict(v) for v in api.versions(label_id)]
        if len(self.versions)<2:raise ValueError('Se necesitan al menos dos revisiones de la misma etiqueta.')
        self.setWindowTitle('Comparar revisiones · Solo consulta')
        self.resize(1120,750)
        self.setMinimumSize(720,470)
        root=vbox(self,12,9)
        head=QHBoxLayout()
        self.first=QComboBox();self.second=QComboBox()
        for v in self.versions:
            caption=f"Revisión {v['version']} · {v['state']} · #{v['id']}"
            self.first.addItem(caption,v['id']);self.second.addItem(caption,v['id'])
        a=next((i for i,v in enumerate(self.versions) if v['id']==selected_id),0)
        self.first.setCurrentIndex(a);self.second.setCurrentIndex(1 if a==0 else 0)
        head.addWidget(label('Revisión A'));head.addWidget(self.first,1)
        head.addWidget(label('Revisión B'));head.addWidget(self.second,1)
        root.addLayout(head)
        tabs=QTabWidget();root.addWidget(tabs,1)
        side=QWidget();side_layout=QHBoxLayout(side);self.left=Preview();self.right=Preview()
        side_layout.addWidget(self.left,1);side_layout.addWidget(self.right,1)
        tabs.addTab(side,'En paralelo')
        overlay=QWidget();overlay_layout=QVBoxLayout(overlay);self.overlay=Preview();overlay_layout.addWidget(self.overlay,1)
        slider_row=QHBoxLayout();slider_row.addWidget(label('Opacidad de revisión B'))
        self.opacity=QSlider(Qt.Orientation.Horizontal);self.opacity.setRange(0,100);self.opacity.setValue(50)
        slider_row.addWidget(self.opacity,1);overlay_layout.addLayout(slider_row)
        tabs.addTab(overlay,'Superposición visual')
        self.summary=label('','subtle');self.summary.setWordWrap(True);root.addWidget(self.summary)
        footer=QHBoxLayout();footer.addStretch();footer.addWidget(button('Cerrar',self.accept));root.addLayout(footer)
        self.first.currentIndexChanged.connect(self.refresh_comparison)
        self.second.currentIndexChanged.connect(self.refresh_comparison)
        self.opacity.valueChanged.connect(self.refresh_overlay)
        self.images=None;self.refresh_comparison()

    def documentary_differences(self):
        a=self.api.version(self.first.currentData())
        b=self.api.version(self.second.currentData())
        changes=[]
        for key,text in [('pdf_sha256','PDF maestro'),('source_sha256','Fuente documental'),
                         ('fields_json','Campos variables'),('crop_json','Recorte'),
                         ('status_area_json','Zona de estado')]:
            if key in a.keys() and key in b.keys():
                left,right=a[key],b[key]
                if key.endswith('_json'):
                    try:left=json.loads(left);right=json.loads(right)
                    except (ValueError,TypeError):pass
                if left!=right:changes.append(text)
        return changes

    def refresh_comparison(self,*_):
        if self.first.currentData()==self.second.currentData():
            self.images=None;self.left.scene().clear();self.right.scene().clear();self.overlay.scene().clear()
            self.summary.setText('Seleccione dos revisiones diferentes.')
            return
        try:
            a=self.api.thumbnail(self.api.version(self.first.currentData()),width_px=750)
            b=self.api.thumbnail(self.api.version(self.second.currentData()),width_px=750)
            self.images=(a,b);self.left.set_image(a);self.right.set_image(b)
            changes=self.documentary_differences()
            self.summary.setText('Diferencias documentales: '+(', '.join(changes) if changes else 'no detectadas en los elementos comparados')+
                '. La superposición es una ayuda visual, no constituye aprobación ni comparación píxel a píxel certificada.')
            self.refresh_overlay()
        except (ValueError,OSError,RuntimeError) as ex:
            self.images=None;self.summary.setText('No se pudo comprobar la integridad o visualizar la fuente: '+str(ex))
            self.left.scene().clear();self.right.scene().clear();self.overlay.scene().clear()

    def refresh_overlay(self,*_):
        if self.images is None:return
        from PIL import Image
        a,b=self.images
        canvas=(max(a.width,b.width),max(a.height,b.height))
        lhs=Image.new('RGBA',canvas,'white');rhs=Image.new('RGBA',canvas,'white')
        lhs.paste(a.convert('RGBA'),((canvas[0]-a.width)//2,(canvas[1]-a.height)//2))
        rhs.paste(b.convert('RGBA'),((canvas[0]-b.width)//2,(canvas[1]-b.height)//2))
        merged=Image.blend(lhs,rhs,self.opacity.value()/100)
        self.overlay.set_image(merged.convert('RGB'))


class CompareMixin:
    def compare_revisions(self):
        if self.legacy_process is not None or not self.row:return
        if not self.flush_emission_work() or not self.resolve_work():return
        try:
            dialog=CompareDialog(self,self.api,self.row['id'],self.row['version_id'])
            dialog.exec()
        except (ValueError,OSError) as ex:
            QMessageBox.information(self,'Comparación no disponible',str(ex))
