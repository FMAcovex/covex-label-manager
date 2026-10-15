"""Toolkit-specific explicit migration decision. No filesystem side effects."""
MESSAGE = ("Esta carpeta contiene una instalación anterior. Para abrirla es necesario "
           "actualizar SQLite a v4. Se creará y verificará una copia completa antes del cambio.\n\n"
           "Los ejecutables anteriores no podrán escribir en la carpeta actualizada. "
           "Para volver a v3 deberá restaurar la copia en otra carpeta. "
           "Cierre todos los demás ejecutables antes de continuar.\n\n"
           "¿Autoriza actualizar esta instalación?\n\nCarpeta: ")

def qt_confirmation(root, parent=None):
    from PySide6.QtWidgets import QMessageBox
    return QMessageBox.question(parent, 'Autorizar actualización SQLite v4', MESSAGE+str(root),
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        QMessageBox.StandardButton.Cancel) == QMessageBox.StandardButton.Yes

def tk_confirmation(root, parent=None):
    from tkinter import messagebox
    return messagebox.askokcancel('Autorizar actualización SQLite v4', MESSAGE+str(root),
        parent=parent, default='cancel', icon='warning') is True
