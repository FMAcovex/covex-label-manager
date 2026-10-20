"""Industrial Moderno palette; Qt Widgets only, no theme/network dependencies."""
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor
from pathlib import Path

STYLE="""
QWidget { font-family: "Segoe UI", "DejaVu Sans"; font-size: 13px; color: #223B40; }
QMainWindow, QWidget#workspace { background: #F3F6F7; }
QFrame#header { background: #173940; border: none; }
QFrame#header QLabel { color: white; }
QLabel#brand { font-size: 17px; font-weight: 700; letter-spacing: 1px; }
QLabel#headerNote { color: #B9D0D0; font-size: 11px; }
QPushButton { background: white; border: 1px solid #DCE5E7; border-radius: 6px; padding: 7px 10px; min-height:16px; font-weight: 600; }
QPushButton:hover:enabled { border-color: #147D71; background: #F0F8F6; }
QPushButton:pressed:enabled { background: #DBEEE9; }
QPushButton:disabled { color: #98ABAF; background: #EFF3F4; border-color: #E5EBED; }
QPushButton#primary { background: #147D71; color: white; border-color: #147D71; }
QPushButton#primary:hover:enabled { background: #10695F; }
QPushButton#primary:disabled { color: #73858A; background: #E7ECEE; border-color: #D4DEE1; }
QPushButton#nav { color: #C9DCDD; background: transparent; border: none; padding: 12px 17px; border-radius: 6px; }
QPushButton#nav:checked { color: white; background: #2C535A; }
QPushButton#nav:hover { color: white; background: #284C53; }
QPushButton#view { text-align: left; border: none; background: transparent; padding: 11px 12px; }
QPushButton#view:checked { background: #E4F1ED; color: #116C62; }
QLabel#title { font-size: 22px; font-weight: 700; color: #173940; }
QLabel#subtle { color: #4B6268; font-size: 12px; }
QLabel#section { font-size: 12px; font-weight: 700; color: #4B6268; letter-spacing: .4px; }
QLabel#panelTitle { font-size: 18px; font-weight: 700; }
QLabel#badge { padding: 5px 9px; border-radius: 5px; font-size: 11px; font-weight: 600; }
QFrame#surface { background: white; border: 1px solid #E0E8EA; border-radius: 9px; }
QFrame#editorProperties { background: white; }
QFrame#surface QLabel { background: transparent; }
QLineEdit { background: white; border: 1px solid #DCE5E7; border-radius: 6px; padding: 7px; selection-background-color: #147D71; }
QLineEdit:focus { border: 1px solid #147D71; }
QLineEdit#search { font-size: 15px; padding: 13px 15px; border-radius: 9px; }
QComboBox { background: white; border: 1px solid #DCE5E7; padding: 8px 10px; border-radius: 6px; min-height: 18px; }
QComboBox::drop-down { border: none; width: 23px; }
QComboBox::down-arrow { image: url(CHEVRON_PATH); width: 14px; height: 14px; }
QComboBox QAbstractItemView { background: white; selection-background-color: #E4F1ED; selection-color: #173940; }
QTableWidget { background: white; border: none; gridline-color: #EFF3F4; selection-background-color: #E4F1ED; selection-color: #173940; outline: none; }
QTableWidget::item { padding: 6px 10px; border-bottom: 1px solid #EFF3F4; }
QHeaderView::section { background: #F7F9FA; color: #4B6268; padding: 9px 10px; border: none; border-bottom: 1px solid #E0E8EA; font-size: 12px; font-weight: 600; }
QScrollBar:vertical { background: transparent; width: 9px; margin: 3px; }
QScrollBar:horizontal { background: transparent; height: 9px; margin: 3px; }
QScrollBar::handle { background: #B7C9CC; border-radius: 3px; min-height: 24px; min-width: 24px; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0px; width: 0px; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }
QSplitter::handle { background: transparent; }
QGraphicsView { background: #E9EFF1; border: 1px solid #DCE5E7; border-radius: 8px; }
QListWidget { background: white; border: none; outline: none; }
QListWidget::item { padding: 12px 10px; border-radius: 5px; }
QListWidget::item:selected { background: #E4F1ED; color: #116C62; }
QDoubleSpinBox { background: white; border: 1px solid #DCE5E7; border-radius: 5px; padding: 7px; }
QTabWidget::pane { border: none; border-top: 1px solid #E0E8EA; background: white; }
QTabBar::tab { padding: 8px 7px; color: #4B6268; background: white; border-bottom: 2px solid transparent; }
QTabBar::tab:selected { color: #147D71; border-bottom: 2px solid #147D71; font-weight: 600; }
QTabBar#settingsPrimaryNav::tab { padding: 10px 17px; border-bottom: 3px solid transparent; font-weight: 600; }
QTabBar#settingsPrimaryNav::tab:selected { color: #116C62; background: #E4F1ED; border-bottom: 3px solid #147D71; }
QTabBar#settingsPrimaryNav::tab:hover { background: #F0F8F6; }

QToolButton { background: white; border: 1px solid #DCE5E7; border-radius: 5px; padding: 8px; }
QToolButton:hover { background: #E4F1ED; }
QCheckBox { spacing: 8px; }
QStatusBar { background: white; border-top: 1px solid #E0E8EA; color: #4B6268; font-size: 12px; }
QPushButton:focus, QToolButton:focus, QComboBox:focus { border: 2px solid #147D71; }
QTableWidget:focus, QListWidget:focus { border: 1px solid #147D71; }
QMenu { background: white; border: 1px solid #DCE5E7; padding: 6px; }
QMenu::item { padding: 9px 18px; }
QMenu::item:selected { background: #E4F1ED; }
"""
STYLE=STYLE.replace('CHEVRON_PATH',(Path(__file__).parent/'chevron.svg').as_posix())

def icon(kind, color='#607B80'):
    """Uniform original line icons, drawn locally."""
    pix=QPixmap(24,24);pix.fill(Qt.GlobalColor.transparent)
    p=QPainter(pix);p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(QColor(color),1.7,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap,Qt.PenJoinStyle.RoundJoin))
    if kind=='search':
        p.drawEllipse(QRectF(4,4,11,11));p.drawLine(14,14,20,20)
    elif kind=='library':
        for x,y in ((4,4),(14,4),(4,14),(14,14)):p.drawRoundedRect(QRectF(x,y,6,6),1,1)
    elif kind=='editor':
        p.drawLine(6,17,17,6);p.drawLine(17,6,20,9);p.drawLine(20,9,9,20);p.drawLine(9,20,4,21);p.drawLine(4,21,6,17)
    elif kind=='clock':
        p.drawEllipse(QRectF(3,3,18,18));p.drawLine(12,7,12,12);p.drawLine(12,12,16,14)
    elif kind=='print':
        p.drawRect(QRectF(7,3,10,5));p.drawRoundedRect(QRectF(3,8,18,10),2,2);p.drawRect(QRectF(7,13,10,8))
    elif kind=='star':
        points=[QPointF(12,2),QPointF(15,8),QPointF(22,9),QPointF(17,14),QPointF(18,21),QPointF(12,18),QPointF(6,21),QPointF(7,14),QPointF(2,9),QPointF(9,8),QPointF(12,2)]
        for a,b in zip(points,points[1:]):p.drawLine(a,b)
    elif kind=='expand':
        for x,y,dx,dy in ((3,3,1,1),(21,3,-1,1),(3,21,1,-1),(21,21,-1,-1)):
            p.drawLine(x,y,x+dx*6,y);p.drawLine(x,y,x,y+dy*6)
    elif kind=='plus':
        p.drawLine(12,5,12,19);p.drawLine(5,12,19,12)
    elif kind=='arrow':
        p.drawLine(4,12,20,12);p.drawLine(14,6,20,12);p.drawLine(14,18,20,12)
    elif kind=='filter':
        for y,x in ((5,8),(12,16),(19,10)):
            p.drawLine(3,y,21,y);p.setBrush(QColor('white'));p.drawEllipse(QPointF(x,y),2,2)
    else:
        p.drawEllipse(QRectF(5,5,14,14));p.drawEllipse(QRectF(10,10,4,4))
        for x,y,x2,y2 in ((12,2,12,5),(12,19,12,22),(2,12,5,12),(19,12,22,12)):p.drawLine(x,y,x2,y2)
    p.end();return QIcon(pix)


STYLE += """
QLineEdit[invalid="true"], QPlainTextEdit[invalid="true"] { border: 1px solid #B04C49; background: #FFF8F7; }
QLabel#fieldError { color: #A13935; font-size: 11px; }
QLabel#emissionSummary { color: #173940; font-size: 15px; font-weight: 600; }
QFrame#emissionFooter { background: white; border: 1px solid #DCE5E7; border-radius: 8px; }
QPlainTextEdit { background: white; border: 1px solid #DCE5E7; border-radius: 7px; padding: 7px; }
QWidget#workForm { background: white; }
QTableWidget { alternate-background-color: #F8FAFA; }
"""


# R3D: ensure dialogs remain readable when Windows uses a dark system palette.
# Native Windows file pickers keep their operating-system appearance.
STYLE += """
QDialog, QMessageBox, QInputDialog {
    background-color: #F3F6F7; color: #223B40;
}
QDialog QLabel, QMessageBox QLabel, QInputDialog QLabel {
    color: #223B40; background-color: transparent;
}
QDialog QFrame#surface { background-color: white; border: 1px solid #DCE5E7; }
QDialog QLineEdit, QDialog QPlainTextEdit, QDialog QTextEdit {
    background-color: white; color: #223B40;
}
QDialog QTabWidget::pane { background-color: white; }
QDialog QAbstractItemView { background-color: white; color: #223B40; }
QMessageBox QPushButton, QInputDialog QPushButton { min-width: 85px; }
QToolTip { background-color: #FFFFFF; color: #173940; border: 1px solid #BECFD2; }
"""
