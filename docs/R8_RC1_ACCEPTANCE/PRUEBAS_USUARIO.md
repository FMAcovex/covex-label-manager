# COVEX Label Manager R8-RC1 — aceptación del usuario

Versión candidata: **R8-RC1**, fuente `main`, commit **504e542b17bbb8bfe2210fca8c9e19016aa42970**. No es una publicación oficial ni una autorización productiva. Este guion operativo deriva de [R8_INTEGRAL_ACCEPTANCE_PLAN.md](../R8_INTEGRAL_ACCEPTANCE_PLAN.md); no sustituye los procedimientos de Calidad.

## Antes de empezar

1. Descargar únicamente el portable Qt enlazado en [ENTREGA.md](ENTREGA.md). Las evidencias son otra descarga; el portable Tk de la CI general no es otra versión que haya que comparar.
2. Guardar el ZIP interno como `COVEX-Label-Manager-R8-RC1-main-504e542b17bb-Windows-x64.zip`, sin modificar su contenido. El artefacto de Actions conserva su nombre técnico con el SHA completo. El ZIP exterior de GitHub y el ZIP interno tienen hashes diferentes: comprobar el **interno** con `Get-FileHash .\COVEX-Label-Manager-R8-RC1-main-504e542b17bb-Windows-x64.zip -Algorithm SHA256` y el valor de ENTREGA.md.
3. Extraer **todo** en una carpeta nueva, local y escribible. No ejecutar desde el ZIP ni copiar sólo el EXE. Abrir `COVEXLabelManager_Qt\BUILD_MANIFEST.json`: `commit` debe ser el SHA anterior. Lanzar `COVEXLabelManager_Qt.exe`; el compañero Legacy de su subcarpeta es parte de esta misma versión, no una alternativa que deba arrancarse por separado. No requiere servidor; Word/conversor e impresora sí requieren el entorno local autorizado.
4. Utilizar un entorno de aceptación aislado y una copia autorizada/verificada de los datos; no trabajar sobre el catálogo productivo ni sobrescribirlo. Registrar Windows 10/11, escala, resolución, conversor, impresora y operador en [RESULTADOS.csv](RESULTADOS.csv). El botón de demostración usa datos ficticios: no valida los documentos de COVEX.
5. Descargar las plantillas CSV y editar una copia local con Excel/LibreOffice. Todas las pruebas comienzan **No probado**. Repetir las esenciales en 1366×768 y 1920×1080, a 100 %, 125 % y 150 %, en los Windows autorizados. Crear filas adicionales por configuración.

Los documentos reales sólo se utilizan en el entorno autorizado del usuario. No adjuntarlos, ni bases, capturas internas, PDFs, lotes o diagnósticos sin revisar a GitHub. Las evidencias de aceptación pueden ser referencias privadas, no archivos públicos.

Para fijar explícitamente una carpeta de datos **exclusiva de aceptación**, abrir PowerShell en la carpeta del EXE y usar, por ejemplo:

```powershell
.\COVEXLabelManager_Qt.exe --data-dir 'C:\COVEX-Aceptacion-R8-RC1\datos'
```

Elegir una ruta local autorizada y escribible que no contenga datos productivos. No omitir esta opción si existe una configuración `COVEX_LABEL_DATA` del puesto que pueda apuntar a producción. Si se ensaya sobre una copia, preparar y verificar la copia completa mediante el procedimiento autorizado, no sólo el archivo SQLite. La opción no copia ni aprueba documentos por sí sola. Para explorar exclusivamente datos ficticios se puede usar `PROBAR_DEMO_QT.bat`, pero la demo es temporal y no sirve como prueba de persistencia entre reinicios de una sesión real.

## Prueba 1 — Biblioteca e importación

1. Abrir Biblioteca e Importar por carpeta; seleccionar una carpeta autorizada con Word y revisar clasificación sugerida, código, nombre y revisión. Corregirlos antes de importar; revisar vista previa y confirmar.
2. Abrir la etiqueta importada en Editor. Volver a Biblioteca, buscar por código y nombre, aplicar/quitar filtros y consultar revisiones/variantes y documentos conservados.
3. Abrir de nuevo el importador y cancelarlo/cerrarlo sin importar.

**Comprobar:** conversión Word real correcta, datos no inventados, documento recuperable y cierre del importador sin cerrar la aplicación. La importación no aprueba el documento. Registrar conversor y versión; PDF sintético de CI no demuestra compatibilidad con Word real.

## Prueba 2 — Editor

1. Abrir un diseño pendiente editable o crear una variante DRAFT autorizada para ensayos. Dibujar un campo y cambiar ejemplo/texto permitido, tamaño, fuente, color y posición.
2. Probar selección, bloqueo, zoom, deshacer/rehacer y PDF real; guardar, cerrar Editor y recuperar el mismo diseño.
3. Intentar modificar directamente una revisión/variante aprobada: debe estar protegida. Las modificaciones deben seguir el ciclo de una nueva variante/revisión; no aprobar para completar esta prueba.

**Comprobar:** campo y PDF coinciden, no se pierde texto al cambiar de selección, geometría/tipografía se conservan y el original aprobado permanece intacto. Si un cambio requiere aprobación documental, anotarlo y dejar bloqueada su emisión definitiva.

## Prueba 3 — Etiquetas de estado

1. Consultar Sin analizar, Aprobado y Rechazado, con sus revisiones explícitas. Editar únicamente campos variables permitidos.
2. Preparar prueba independiente e integrar el estado en una etiqueta de producto. Revisar modos Ajustar proporcional y Rellenar protegido.
3. Comprobar color, símbolos, textos fijos, márgenes y medidas. Intentar un recorte crítico en copia de ensayo: debe bloquearse, no desaparecer silenciosamente.

**Comprobar:** el tipo «Aprobado» no otorga aprobación documental. No deben deformarse proporciones ni perderse contenido crítico; el PDF y la identidad documental deben corresponder al estado elegido.

## Prueba 4 — Asistente de emisión

1. Inicio → Nueva emisión: seleccionar explícitamente producto, revisión y variante cuando haya alternativas.
2. Introducir lote y demás campos requeridos por ese diseño; probar kg/g/mg coherentes con el sufijo documental, varios recipientes, datos particulares y copias permitidas.
3. Continuar a Revisar etiqueta, esperar el PDF dinámico y revisar datos, formato, dimensiones, recipientes y estado integrado. Volver atrás, corregir y comprobar que el PDF se actualiza sin mezclar trabajos.
4. Generar una prueba. Sólo si el diseño y procedimiento están realmente autorizados en el entorno de aceptación, revisar la confirmación completa y emitir definitivamente. Si no hay autorización, comprobar el bloqueo y registrar el subcaso definitivo como Bloqueado, no conforme ficticio ni aprobación simulada.

**Comprobar:** cuatro pasos, conservación de valores al retroceder, PRUEBA claramente separada, no emisión con preview obsoleta y éxito únicamente después de registro. Cancelar la confirmación no emite ni duplica.

## Prueba 5 — Emisión avanzada

1. Pasar desde el asistente al Centro avanzado y volver: mismo trabajo y datos, sin duplicar lote ni borrar borrador.
2. Revisar perfiles, formatos, distribución, recipientes y copias. Cambiar una opción y comprobar el PDF real.
3. Aplicar ajustes tipográficos temporales y comprobar la marca PRUEBA / NO GMP y bloqueo de definitiva; cancelar/restaurar. Si se conserva un diseño diferente, debe ser una nueva variante DRAFT sometida al ciclo documental externo.

**Comprobar:** no hay un segundo motor ni un atajo para saltarse aprobación; formatos y ajustes conservan la identidad documental y las guardas anteriores.

## Prueba 6 — Historial

1. Consultar una emisión de aceptación autorizada, revisar identidad, valores y evidencia; abrir su PDF registrado.
2. Reimprimir mediante la acción correspondiente e introducir motivo conforme al procedimiento.
3. Consultar la relación con el original y confirmar que repetir la acción no registra otra emisión accidental del mismo trabajo.

**Comprobar:** PDF original inalterado, trazabilidad de reimpresión y ausencia de duplicaciones. Una reimpresión no es otro lote; enviar a la cola no demuestra que el papel haya salido correctamente.

## Prueba 7 — Estabilidad

1. Navegar repetidamente entre Biblioteca, Editor, asistente, Centro e Historial. Abrir/cerrar diálogos y Editor; guardar/cerrar normalmente y recuperar borradores.
2. Cancelar una vista previa y comprobar recuperación. Ensayos de interrupción inesperada/concurrencia sólo sobre copias aisladas, con autorización y sin escrituras productivas; no provocar un corte eléctrico en producción.
3. Intentar recuperar un trabajo tras el ensayo controlado. Ante conflicto, no sobrescribir datos de otra sesión; revisar aviso y datos conservados.
4. Configuración → exportar diagnóstico privado. Revisar su contenido antes de compartir y conservarlo en el canal autorizado, separado de backup documental.

**Comprobar:** sin cierre global, pérdida o corrupción; guardas de cierre/autoguardado, SQLite v4 e historial íntegros. Anotar duración y ciclos; una sesión corta no acredita fiabilidad indefinida.

## Prueba 8 — Impresión física

1. Utilizar impresora, controlador y papel de aceptación identificados. Imprimir el PDF al 100 % / tamaño real, sin «ajustar a página» automático salvo procedimiento específico.
2. Probar hojas A4 y otros formatos necesarios, distintos puestos/posiciones, márgenes y recipientes/copias.
3. Medir dimensiones con instrumento adecuado y comparar impresión con PDF: legibilidad, símbolos, colores, contenido y ausencia de recortes. Aplicar tolerancias documentadas por COVEX, no inventadas por esta guía.
4. Revisar cola, atascos, cancelaciones y procedimiento antes de repetir para evitar duplicados físicos.

**Comprobar:** correspondencia PDF/papel y medidas dentro de tolerancia aprobada. CI, raster o «impresión enviada» no permiten marcar este recorrido como Conforme.

## Cómo registrar y comunicar el resultado

En RESULTADOS.csv anotar **Conforme / No conforme / No probado / Bloqueado**, observación, referencia privada, fecha y versión; un recorrido con subcasos sin ejecutar no debe declararse íntegramente Conforme. Para detalle, duplicar la fila y especificar el subcaso.

En INCIDENCIAS.csv registrar una fila por defecto reproducible y agrupar la revisión posterior en un único paquete correctivo, evitando PR cosméticas aisladas. P0: corrupción/pérdida, identidad errónea, emisión no autorizada o duplicada. P1: recorrido esencial bloqueado, recorte/ilegibilidad crítica o impresión incorrecta. P2: dificultad operativa sin pérdida ni bypass. P3: ajuste menor. Calidad determina el riesgo GMP real; la prioridad no lo sustituye.

Ante P0/P1, suspender el recorrido afectado, conservar evidencia local y notificar por canal autorizado. No desactivar controles ni aprobar para desbloquear pruebas. Cierre técnico, aceptación del usuario, aprobación documental y validación GMP son decisiones distintas. Los tres últimos siguen pendientes hasta sus actas externas.
