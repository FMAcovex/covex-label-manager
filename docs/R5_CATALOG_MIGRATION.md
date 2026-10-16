# R5 — Incorporación y exportación del catálogo de etiquetas

**R5A, rama:** feature/r5a-catalog-inventory-export. **Base:** main con R4C.

## R5A — Primera entrega de solo lectura
- Inventario local de carpetas (útil para una copia previamente autorizada del libro máster SharePoint). Calcula SHA-256 y compara contra fuentes/PDF de la biblioteca actual; estados EXACT_DUPLICATE, IDENTITY_CONFLICT o REVIEW_REQUIRED. Las identidades inferidas por nombre son orientativas y no equivalen a una clasificación GMP.
- Exportación masiva explícita desde el menú de la biblioteca: todas las revisiones, sus estados, originales existentes y PDF maestros, ZIP con manifiesto de SHA-256. Verificación del archivo generado; abortar ante originales corruptos. **No** se sobrescribe un ZIP y no se incluyen expedientes de emisiones.
- Ambos flujos no modifican los registros, la aprobación ni la base SQLite v4. El ZIP es una **exportación documental**, NO un backup restaurable; mantener la función de copia integral original.
- No se accede de forma implícita a SharePoint. El usuario deberá escoger una carpeta local/sincronizada y autorizada (o autorizar una futura integración).
- Los nombres de archivo no determinan estado documental ni revierten revisiones aprobadas. No incluir documentos reales COVEX en el repositorio público.

## R5B — Migración controlada pendiente
- Inventario y reconciliación contra el libro máster real, correspondencia código–producto–cliente–idioma–revisión y control de duplicados.
- Selección explícita por filas; no duplicar documentos idénticos, ni inferir vigencia por nombre.
- Incorporación en estado PENDING, manteniendo documentos originales y evitando modificaciones en etiquetas ya aprobadas; evidencia y resumen de conciliación.
- Distinguir actualizaciones de revisiones existentes, nuevas etiquetas y conflictos manuales.

## R5C — Consolidación y aceptación
- Informes de cobertura y diferencias respecto al libro máster autorizado, recuperación ante errores y exportación según filtros.
- Validación manual de Word real, compatibilidad Windows y comprobación del modelo de datos y GMP. 00-R1 permanece pendiente de aprobación documental.

No efectuar squash/merge ni operaciones sobre datos reales sin autorización.
