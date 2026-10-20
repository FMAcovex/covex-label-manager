# R8-RC4B · Pulido de interfaz y claridad de configuración

## Objetivo
Agrupar la interfaz de configuración, explicar la conciliación con el libro máster
y distinguir el tamaño físico de la etiqueta del zoom y de la colocación por hoja.
La seguridad documental y el motor PDF se conservan.

## Configuración y datos
- **General / Resumen**: cifras locales y accesos frecuentes sin efectos sobre datos.
- **General / Preferencias y copias**: operador (modifica preferencia local), ruta (consulta)
  y copia ZIP (crea un archivo; no restaura).
- **Gestión documental / Libro máster**: abre conciliación de solo lectura sobre
  XLSX/CSV/TSV local. No accede a SharePoint, no importa etiquetas, no aprueba
  revisiones y no modifica SQLite. Inventario de carpeta es otra función separada.
- **Gestión documental / Catálogo CM**: importa DOCX con confirmación y muestra
  duplicados sin fusión automática.
- **Gestión documental / Maestros de estado**: registro de aprobación externa
  existente, con cotejo, responsabilidad y referencia obligatorios.
- **Administración avanzada**: auditoría local, herramientas de aceptación,
  exportación de diagnóstico y acceso a la configuración clásica.

## Conciliar libro máster
1. Seleccionar archivo local y hoja.
2. Confirmar columnas obligatorias: denominación y revisión; código recomendado.
   Mostrar columnas opcionales para comparar cliente, estado, origen, etc.
3. Comparar sin modificar datos; ver coincidencias y discrepancias con nombres
   en castellano. Filtrar **Requieren revisión** o **Solo en biblioteca**.
4. Seleccionar una fila para ver el significado y las discrepancias.
5. Exportar ZIP verificable (CSV/JSON y huellas SHA-256), sin edición.

**Atención:** «Solo en biblioteca» no demuestra que el documento deba retirarse:
el libro puede ser parcial. Los códigos Excel con ceros iniciales deben ser texto.
Las revisiones/documentos pendientes de aprobación siguen pendientes.

## Centro de emisión
- **Recipientes** es el número de envases; **Copias** es el número de etiquetas
  iguales por cada envase; **Números** el subconjunto a emitir.
- Ancho/alto/margen/separación/desplazamiento/seguridad se explican en mm.
- **Cuadrícula**: ancho/alto físicos aplicables a las casillas regulares.
- **Distribución libre**: cada casilla tiene tamaño y posición propios; el cambio
  se hace en «Modificar tamaño y posición de cada etiqueta».
- El zoom del PDF es solo una vista; la impresión física debe probarse al 100 %.
- «Más opciones» diferencia herramientas de formato de las de trazabilidad.

## Límites
No se modifican firmas, aprobación documental, contratos de emisión, SQLite v4,
motores de conversión/PDF, importación ni histórico. CI sintética no sustituye
pruebas con Word real, impresoras/Windows 10-11 o validación GMP.
