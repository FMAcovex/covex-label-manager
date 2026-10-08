# R3A — Biblioteca y navegación Studio

Base oficial: main 0.3.1, bd6e92e. Rama feature/r3a-studio-navigation; no integrar sin autorización del propietario. Sin tag/release de R3A ni modificación directa de main.

## Resultado funcional

Inicio directo en Biblioteca. Cabecera horizontal Biblioteca/Editor/Emisión/Historial/Configuración. Filtros combinables a la izquierda, tabla predeterminada con metadatos disponibles en el centro e inspector documental con imagen/revisiones/acciones a la derecha. Paneles laterales ajustables y ocultables, scroll cuando hace falta; desconocidos vacíos y filtros sin datos deshabilitados. Origen e incorporación siguen separados; documentos de clientes no se aprueban por importación.

Clic selecciona; doble clic/Enter/Abrir etiqueta abre Editor. Ctrl+K mantiene buscador rápido. Favoritas y recientes reutilizan R2. Acciones conserva importación individual/carpeta, ficha/documentos, nueva revisión, registro de aprobación externa, metadatos y comparación básica. Preparar emisión solo se habilita para revisión vigente e íntegra; el preflight definitivo sigue en el motor. Pendientes pueden abrirse y preparar un PDF de prueba desde Emisión; no permiten definitiva.

Editor reutiliza el componente avanzado existente integrado en la pestaña; no es todavía el Editor R3B. Navegar conserva ajustes/datos/filtros en memoria; cambiar de revisión con trabajo sin guardar requiere confirmar descarte. No lleva datos de un lote a otra etiqueta. El Centro de impresión existente continúa accesible desde Emisión; administración y configuraciones existentes siguen disponibles. No se añaden tarjetas de inicio administrativas.

## Verificación

- Base 0.3.1: 49 tests pasan y 1 omitido.
- R3A/Linux con display de prueba: 53 tests pasan y 1 omitido (Word). Incluyen vistas reales Tk, filtros, navegación conservando lote/envases/estado, apertura Editor y conservación de ajustes, confirmación al cambiar de revisión, Ctrl+K/paneles, biblioteca vacía y todos los accesos; integridad/aprobación del botón de preparación.
- Smoke gráfico R1/R2 satisfactorio con Tk 8.6: previsualización, filtros/favoritas, comparación existente, Editor avanzado, buscador rápido, envases, Centro de impresión, historial y configuración sin errores de callback.
- 11 PDF sintéticos / 19 páginas: geometría y raster de 144 dpi idénticos a 0.3.1. Motor/persistencia/rutas/migraciones sin modificaciones. No acredita validación con maestros privados ni impresión física.
- `tests/capture_r3a.py` produce capturas de ventanas reales con documentos/maestros/datos sintéticos, guardadas en test-results/r3a (no versionadas). No documentos originales ni información de fabricación.
- Workflow Windows existente conserva lock/hashes y PyInstaller onedir. Los nuevos tests Tk se ejecutan en Windows. Consultar resultado de la PR; build/núcleo no acreditan aceptación interactiva en equipos COVEX ni Word/impresión.

## Comprobación del propietario

1. Descargar exclusivamente el artefacto de la PR con job Windows satisfactorio. Extraer en carpeta nueva, sin reemplazar data. Hacer copia completa de los datos existentes con la app cerrada y reutilizar esa COPIA junto al EXE o con COVEX_LABEL_DATA.
2. Verificar inicio en Biblioteca, tamaños de ventana/escala de Windows, columnas y scroll, paneles, filtros combinados, favoritas/recientes y Ctrl+K. Vacíos no deben convertirse en metadatos inventados.
3. Abrir un borrador, cambiar un ajuste sin guardar, navegar a Biblioteca/Historial y regresar al Editor: conservar ajuste. Intentar abrir otro diseño: cancelación debe conservar el anterior.
4. Preparar datos de prueba en Emisión (lote, numeración, envases, estado, formato), navegar y regresar: conservar. Cambiar etiqueta: confirmar descarte y no heredar campos del lote anterior. No confundir conservación en sesión con recuperación tras cierre.
5. Comprobar 00-R1 pendiente, bloqueo de definitiva y acceso al PDF de prueba; revisar ficha/aprobación externa, importación, perfiles/calibración, catálogo y backups existentes. Maestros y emisones anteriores permanecen locales.
6. Revisar capturas y aprobar o pedir ajustes antes de autorizar el merge. R3B/R3C no comienzan hasta la integración autorizada de la fase precedente.

## Límites explícitos

Sin autoguardado/recuperación de trabajos (R3B), sin sincronización nueva de datos variables Editor/Emisión, sin nuevo modelo de variante, sin editor nativo completo ni rediseño del Centro de emisión (R3C). Tabla predeterminada; tarjetas opcionales pospuestas. R2.5 sigue pendiente; no se añade comparación/superposición nueva. No firma electrónica, ERP/SharePoint, red, servidores ni cambios de base. Main continúa sin protección técnica efectiva; PR y aprobación del propietario son el procedimiento operativo.
