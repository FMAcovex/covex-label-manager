"""Controlled native Qt print dialog; never claim labels physically printed.

PyMuPDF rasterizes verified registered PDF pages at the device resolution.
QPrinter provides the physical target; no auto-fit, hidden selection or silent jobs.
"""
import json

import fitz
from PySide6.QtCore import QSizeF,QRectF
from PySide6.QtGui import QImage,QPainter,QPageLayout,QPageSize
from PySide6.QtPrintSupport import QPrinter,QPrintDialog,QAbstractPrintDialog
from PySide6.QtWidgets import QMessageBox

from ..canonical import canonical
from ..print_dispatch import prepare_registered,validate_device,raster_size,close_size


def _render_to_selected_printer(plan,printer):
    """Only call after an explicit accepted native print dialog."""
    dpi=int(printer.resolution())
    paper_mm=plan['paper_mm']
    size=raster_size(paper_mm,dpi)
    page_layout=printer.pageLayout()
    actual=page_layout.fullRect(QPageLayout.Unit.Millimeter)
    validate_device(plan,printer.printerName(),
        (actual.width(),actual.height()),
        printer.outputFormat()==QPrinter.OutputFormat.NativeFormat and not printer.outputFileName())
    # On a full-page print device, the origin is the physical paper corner.
    printer.setFullPage(True)
    painter=QPainter()
    started=False
    try:
        if not painter.begin(printer):
            raise RuntimeError('El controlador no ha aceptado el trabajo de impresión.')
        started=True
        with fitz.open(stream=plan['pdf_bytes'],filetype='pdf') as pdf:
            for index,page in enumerate(pdf):
                if index>0 and not printer.newPage():
                    raise RuntimeError(f'El controlador no aceptó la página {index+1}.')
                pix=page.get_pixmap(matrix=fitz.Matrix(dpi/72.0,dpi/72.0),alpha=False)
                if pix.width*pix.height>40_000_000:
                    raise ValueError('La imagen excede el límite de memoria seguro.')
                image=QImage(pix.samples,pix.width,pix.height,pix.stride,
                             QImage.Format.Format_RGB888).copy()
                if image.isNull():
                    raise RuntimeError('No se pudo rasterizar el PDF para impresión.')
                # Destination is ALWAYS real PDF size, not "fit to printable area".
                destination=QRectF(0,0,paper_mm[0]*dpi/25.4,paper_mm[1]*dpi/25.4)
                painter.drawImage(destination,image)
        if not painter.end():
            raise RuntimeError('El controlador informó de un fallo al cerrar el trabajo.')
        started=False
    except Exception:
        if started:
            try:printer.abort()
            finally:painter.end()
        raise
    return {'issue_id':plan['issue_id'],'printer':printer.printerName(),
            'pages':plan['pages'],'status':'HANDED_TO_DRIVER_UNCONFIRMED'}


def print_registered_pdf(api,issue_id,parent):
    """Return False on cancellation; True only when driver accepted all pages."""
    plan=prepare_registered(api,issue_id)
    if plan['partially_used_first_page']:
        response=QMessageBox.question(parent,'Hoja parcialmente utilizada',
            'La primera hoja tiene posiciones reservadas. Verifique la orientación y '
            'el sentido de carga; para las siguientes hojas use papel nuevo. '
            'No utilice «Ajustar a página». ¿Continuar?',
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel)
        if response!=QMessageBox.StandardButton.Yes:
            return False
    printer=QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setResolution(300)
    printer.setFullPage(True)
    printer.setPageSize(QPageSize(QSizeF(*plan['paper_mm']),QPageSize.Unit.Millimeter))
    # A reference printer is not an automatic, trustworthy queue selection.
    dlg=QPrintDialog(printer,parent)
    dlg.setWindowTitle(f'Enviar emisión #{issue_id} · Impresión sin ajuste de escala')
    dlg.setOption(QAbstractPrintDialog.PrintDialogOption.PrintToFile,False)
    if dlg.exec()!=QPrintDialog.DialogCode.Accepted:
        return False
    if printer.fromPage() or printer.toPage():
        raise ValueError('Impresión parcial de páginas no permitida aquí: use todas las hojas del PDF.')
    paper=printer.pageLayout().fullRect(QPageLayout.Unit.Millimeter)
    validate_device(plan,printer.printerName(),(paper.width(),paper.height()),
        printer.outputFormat()==QPrinter.OutputFormat.NativeFormat and not printer.outputFileName())
    current=api.history.inspect(issue_id)
    if current['token']!=plan['token']:
        raise ValueError('El registro PDF o su documentación cambió mientras elegía impresora.')
    # Print request audit precedes dispatch, so a failure never masquerades as a
    # successful print. SQLite is unchanged structurally.
    detail={'printer':printer.printerName(),'pdf_sha256':plan['pdf_sha256'],
            'pages':plan['pages'],'physical_confirmation':False}
    api.audit('PRINT_REQUEST',issue_id,canonical(detail))
    try:
        result=_render_to_selected_printer(plan,printer)
    except Exception as ex:
        api.audit('PRINT_DISPATCH_ERROR',issue_id,canonical({**detail,'error':str(ex)[:240]}))
        raise
    api.audit('PRINT_DRIVER_HANDOFF',issue_id,canonical(detail))
    return result


class PrintWorkflowMixin:
    def _send_registered_to_printer(self,issue_id,feedback):
        try:
            if getattr(self,'native_busy',False) or self.legacy_process:
                raise PermissionError('Espere a que finalice la operación anterior.')
            # Fail before opening any UI if registry/PDF/snapshot is inconsistent.
            prepare_registered(self.api,issue_id)
            result=print_registered_pdf(self.api,issue_id,self)
            if result is False:
                feedback.setText('Impresión cancelada. No se ha enviado ningún trabajo.')
                return False
            feedback.setText(
                f"Emisión #{issue_id} enviada al controlador «{result['printer']}» "
                f"({result['pages']} páginas). NO se confirma la impresión física: "
                'compruebe la cola, las hojas y las etiquetas impresas.')
            return True
        except Exception as ex:
            feedback.setText('Impresión no confirmada: '+self.operator_error(ex)+
                             ' Consulte la cola de impresión antes de volver a intentarlo.')
            QMessageBox.warning(self,'Impresión no confirmada',
                'No consta una entrega completa al controlador. Consulte la cola '
                'antes de repetir el trabajo.\n\n'+self.operator_error(ex))
            return False

    def print_emission_pdf(self):
        work=getattr(self,'emission_work',None)
        if not work or work.get('phase')!='ISSUED' or not work.get('issue_id'):
            self.emission_feedback.setText('Primero genere una emisión definitiva. No se imprime un PDF de prueba como definitivo.')
            return False
        return self._send_registered_to_printer(work['issue_id'],self.emission_feedback)

    def print_historical_pdf(self):
        issue_id=getattr(self,'history_id',None)
        if issue_id is None:return False
        return self._send_registered_to_printer(issue_id,self.history_feedback)
