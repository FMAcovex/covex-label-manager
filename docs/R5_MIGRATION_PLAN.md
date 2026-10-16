# R5 — Migración y exportación de biblioteca: contrato

## R5A: inventario y migración manual asistida
- Entrada local desde una carpeta autorizada o una biblioteca SharePoint previamente sincronizada/descargada por el usuario. Sin acceso automático al tenant, sin envío de etiquetas reales a GitHub.
- Previsualización con SHA-256, nombre y revisión propuestos, clasificación NEW/DUPLICATE/REVIEW/ERROR y CSV de conciliación.
- NEW puede importarse solo con selección explícita. El servicio vuelve a verificar contenido y catálogo. Todo importado conserva estado PENDING y requiere revisión posterior de diseño/campos/recorte/aprobación.
- Duplicados en revisiones existentes o dentro de la selección se omiten. Varios archivos/revisiones del mismo nombre, coincidencias históricas, indicios de etiquetas de cliente/anuladas y documentos PDF multipágina se bloquean para conciliación manual. No se deben inferir versiones a partir de nombres como si fueran datos GMP definitivos.
- La cancelación detiene nuevos documentos, pero no revierte los registrados. El CSV puede guardarse fuera de la carpeta de datos protegida.
- COVEX Label Manager no cambia SQLite v4 ni ficheros aprobados existentes. Pruebas CI con documentos sintéticos.

## R5B: exportación masiva documental (pendiente)
- ZIP bajo elección explícita del usuario, con todas las etiquetas, originales, PDF maestros, revisiones, metadatos y hashes verificados, sin SQLite ni emisiones por defecto.
- Opción de todas las revisiones o solo la última, manifiesto SHA-256 y verificación de integridad del ZIP.
- No confundir con el backup de recuperación de la aplicación, y no publicar documentos reales en GitHub.

## R5C: conciliación del libro máster SharePoint (pendiente)
- Inventario de fuente maestra, referencias/códigos, revisiones y clientes. Resolver conflictos y variantes, controlar el recorte y trazabilidad.
- Copia de seguridad previa, informe de diferencias y aceptación por Calidad antes de usar los registros importados.
