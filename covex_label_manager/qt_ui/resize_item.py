"""Eight visible handles, one geometry command per completed gesture."""
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem

class ResizeHandle(QGraphicsRectItem):
    def __init__(self, parent, hx, hy):
        super().__init__(-4,-4,8,8,parent); self.hx=hx; self.hy=hy
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        self.setBrush(QBrush(QColor('white'))); self.setPen(QPen(QColor('#147D71')))
        self.setCursor(Qt.CursorShape.SizeAllCursor); self.setZValue(20)
    def mousePressEvent(self,e):
        p=self.parentItem(); self.origin=QRectF(p.rect()); self.start=p.mapFromScene(e.scenePos()); e.accept()
    def mouseMoveEvent(self,e):
        p=self.parentItem(); d=p.mapFromScene(e.scenePos())-self.start; r=QRectF(self.origin)
        if self.hx==0:r.setLeft(min(r.right()-1,r.left()+d.x()))
        if self.hx==1:r.setRight(max(r.left()+1,r.right()+d.x()))
        if self.hy==0:r.setTop(min(r.bottom()-1,r.top()+d.y()))
        if self.hy==1:r.setBottom(max(r.top()+1,r.bottom()+d.y()))
        p.setRect(r); p.position_handles(); e.accept()
    def mouseReleaseEvent(self,e):
        self.mouseMoveEvent(e); e.accept(); self.parentItem().released()

class ResizableRect(QGraphicsRectItem):
    def enable_handles(self, enabled):
        self.handles=[ResizeHandle(self,x,y) for x,y in [(0,0),(.5,0),(1,0),(0,.5),(1,.5),(0,1),(.5,1),(1,1)]] if enabled else []
        self.position_handles()
    def position_handles(self):
        r=self.rect()
        for h in getattr(self,'handles',[]):
            h.setPos(r.left()+h.hx*r.width(),r.top()+h.hy*r.height()); h.setVisible(self.isSelected())
    def itemChange(self,change,value):
        result=super().itemChange(change,value)
        if change==QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:self.position_handles()
        return result
