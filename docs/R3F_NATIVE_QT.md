# R3F — Comparación e importación por carpetas en PySide6

Base: `main` `4c6c31bfc5088db755ec0a66cb74ef0c46d377c9`. Rama: `feature/r3f-native-compare-folder-import`.

## Implementación
- Comparador Qt: seleccionar dos revisiones de la misma etiqueta, dos vistas reales, superposición con opacidad y resumen de diferencias documentales (huella PDF/fuente, campos, recorte y zona de estado); solo consulta. No comparar versiones de etiquetas distintas. No declarar la superposición certificación visual ni aprobación.
- Importación por carpetas: exploración recursiva mediante `api.importable_files`, propuesta de identidad conforme a `proposed_identity`, lista previa, confirmación, progreso por documento, parada entre documentos y errores individualizados. **No revertir automáticamente** entradas ya importadas; declarar explícitamente la parcialidad. Todas las revisiones importadas quedan PENDING. Se reutiliza `api.import_label` y la conversión local Word/PDF existente; la GUI no escribe SQLite.
- Cada conversión del documento se ejecuta en el hilo de UI por compatibilidad con el servicio y SQLite; su duración puede bloquear momentáneamente la ventana. La cancelación se aplica entre documentos, no a mitad de Word/LibreOffice. Antes de aceptar R3F para carpetas muy grandes, evaluar worker aislado con conexión propia y cancelación segura.
- Mantener `qt_legacy`, Tkinter y los datos originales como contingencia técnica hasta completar pruebas reales y decidir retirada. Las llamadas no se eliminan por esta migración.
- No cambiar SQLite v4, emisiones, instantáneas, estados o 00-R1. No incorporar fuentes reales al repositorio.

## Validación por CI/UAT
1. Comparar dos revisiones y mostrar diferencias esperadas, sin escrituras ni cambios de estado. Exigir revisión diferente.
2. Carpetas con 0, 1 y múltiples archivos sintéticos; errores y cancelación entre pasos; recuento y persistencia sin duplicación silenciosa.
3. Actualizar Biblioteca tras importar, confirmar que el diseño queda PENDING y necesita revisión individual.
4. Regresiones completas Qt/Windows/migración, 87 capacidades y portable. Comparación y carpeta accesibles sin iniciar Tkinter.
5. Pruebas de DOC/DOCX real en Word instalado, archivos grandes, antivirus, Windows 10/11 y GMP siguen pendientes.
