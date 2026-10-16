# R5C — Conciliación documental de libro máster frente a biblioteca

Base: main con R5B. Rama: feature/r5c-master-reconciliation.

## Procedimiento de operación
1. Obtenga una **copia local autorizada, controlada y de solo lectura** del libro máster. No se conectan credenciales ni se descargan archivos de SharePoint automáticamente.
2. Biblioteca → Acciones → Conciliar libro máster…; seleccione CSV, TSV o XLSX, y hoja si procede.
3. Confirme correspondencia de columnas: Nombre y Revisión obligatorias; Código, Origen, Cliente, Producto, Idioma y Estado opcionales. La asociación sugerida por cabeceras **no sustituye** la confirmación del operador.
4. Ejecute la conciliación: MATCHED, MISSING_LABEL, MISSING_REVISION, METADATA_DIFFERENCE, STATE_DIFFERENCE, AMBIGUOUS, DUPLICATE_MASTER_ROW, INVALID_MASTER_ROW. Las revisiones ONLY_IN_APP se informan separadas porque el máster podría ser parcial.
5. Revise incidencias manualmente antes de cualquier incorporación R5B, corrección documental o aprobación. La comparación NO modifica SQLite v4, etiquetas, revisiones, aprobaciones, productos, originales ni estado de emisión.
6. Exporte un ZIP que contiene conciliacion.csv (UTF-8 BOM, separador ; y neutralización de fórmulas de hojas de cálculo), conciliacion.json y report-manifest.json con SHA-256. Antes de exportar se verifica que no cambiaron el libro ni el catálogo respecto a la comparación.

## Límites deliberados
- Se admiten únicamente XLSX sin macros y CSV/TSV (no XLS antiguo ni XLSM). El lector XLSX usa biblioteca estándar y lee texto y valores guardados en una hoja, no evalúa fórmulas.
- **Códigos/revisiones de Excel como números quedan bloqueados**: un valor mostrado como 00 podría estar almacenado como 0. Convierta previamente dichas columnas a texto y verifique ceros a la izquierda.
- El estado documental solo se compara si existe columna seleccionada y valor reconocido. No se infiere por nombre, color de la hoja ni carpeta. Ausencia de datos no implica equivalencia de metadatos.
- Coincidencias por nombre o código con origen/cliente explícitos; si hay más de un registro candidato se declara AMBIGUOUS. La ausencia de origen/cliente puede causar ambigüedad, jamás un emparejamiento arbitrario.
- Cobertura = coincidencias íntegras / filas únicas comparables; no incluye filas inválidas o repetidas. ONLY_IN_APP NO se propone para borrado.
- El informe puede contener datos de empresa. Debe guardarse en ubicación autorizada; **no se adjunta ni se sube a GitHub**.
- No sustituye una migración real, reconciliación GMP formal, pruebas de Word/impresoras Windows 10/11 o validación. Revisión 00-R1 continúa PENDING.
