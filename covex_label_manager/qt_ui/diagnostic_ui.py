"""One non-modal, rate-limited indication; diagnostics never show raw exceptions."""
from PySide6.QtCore import QObject, Signal, Slot, QElapsedTimer


def install_qt_diagnostics(diagnostic):
    from PySide6.QtCore import qInstallMessageHandler, QtMsgType, qVersion
    diagnostic.environment['qt'] = qVersion()
    def handler(kind, context, text):
        # Qt text/context may embed document paths; never persist either.
        if kind == QtMsgType.QtFatalMsg:diagnostic.record('qt_fatal')
        elif kind == QtMsgType.QtCriticalMsg:
            diagnostic.record('qt_critical')
            if diagnostic.notifier is not None:diagnostic.notifier()
        if previous is not None:previous(kind, context, text)
    previous = qInstallMessageHandler(handler)
    return lambda:qInstallMessageHandler(previous)


class ErrorNotifier(QObject):
    failed = Signal()

    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.elapsed = QElapsedTimer()
        self.failed.connect(self.notify)

    @Slot()
    def notify(self):
        if self.elapsed.isValid() and self.elapsed.elapsed() < 5000:return
        self.elapsed.start()
        self.window.statusBar().showMessage(
            'No se ha completado la operación. Compruebe los cambios y el historial antes de repetirla. '
            'Puede exportar el informe de diagnóstico desde Configuración.')
