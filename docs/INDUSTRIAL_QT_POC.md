# Industrial Moderno — prueba visual ejecutable PySide6

Base main 0.3.1 bd6e92e. PR #2 sin integrar. No es R3A terminada ni migración completa. No cambia main.py, Tkinter, servicios, motor, persistencia ni esquema 3.

## Ejecutar

Windows: descargar artefacto del workflow **Industrial Qt visual proof** de esta rama/PR, extraer ZIP interior **COVEXLabelManager_Visual_Qt.zip** y ejecutar **COVEXLabelManager_Visual_Qt.exe** en su carpeta completa, incluida _internal. No requiere Python. Mantener separado del portable actual: no copiar data. Siempre genera una base ficticia temporal con Store(seed=False); no lee COVEX_LABEL_DATA ni resources y la elimina al cerrar normalmente.

Fuentes Windows: INICIAR_PRUEBA_QT.bat usa .venv-qt independiente, Python 3.11 x64 y locks con hashes. Linux: instalar requirements.txt y prototypes/industrial_qt/requirements.txt en un entorno propio, ejecutar python qt_visual_poc.py. Requiere escritorio o Qt offscreen para pruebas. BUILD_PRUEBA_QT.bat y Actions construyen el mismo onedir.

Probar búsqueda/Ctrl+K, filtros combinados y avanzados, favoritas/recientes, columnas/selección/doble clic, revisión y Ampliar vista previa con zoom. Editor: seleccionar/mover campo, posición/tamaño/nombre, bloquear, navegar y regresar; cambios temporales. Vigente ficticia: solo lectura. Restablecer recupera diseño inicial. Sin guardado, importación, emisión o aprobación productiva.

## Alcance

Cabecera #173940, acción #147D71, fondo #F3F6F7, blanco, bordes discretos, iconos de línea homogéneos locales, fuente del sistema. Qt Widgets/Fusion; sin web, QML, WebEngine, servidores o assets externos.

Biblioteca: buscador grande, filtros frecuentes visibles/avanzados plegables, tabla principal, splitters, estado con color y texto, ficha/tooltip de metadatos, inspector con documento sintético ampliable. A menor ancho, columnas secundarias se reducen y se permite scroll horizontal para mantener nombre legible. Detalles del inspector desplazan si hace falta; acciones principales fijas.

Editor: lienzo dominante, elementos izquierda, propiedades derecha, posición/tamaño y texto/comportamiento agrupados, zoom/ajuste. PDF fijo como fuente; campos Qt seleccionables/movibles. Negrita/fuente/obligatorio cambian valores temporales, no implementan aún render tipográfico R3B. Sin composición nativa, recorte, anclajes o guardado nuevos.

Reutiliza **LocalServices, LibraryService, Store y LocalServices.thumbnail**. Qt no ejecuta SQL ni lee maestros directamente. DemoSession genera PDFs/metadatos/revisiones ficticias e invoca servicios exclusivamente sobre base temporal. UI recibe servicio, nunca datos de producción.

Funciones no adaptadas muestran alcance y accesos actuales. FUNCTIONAL_PRESERVATION_MATRIX.md recoge las capacidades que deben conservarse. Tkinter permanece íntegro y su workflow independiente se mantiene.

## Comparación

| Aspecto | R3A Tkinter PR #2 | Prueba Qt |
|---|---|---|
| Identidad | Blanco/azul y controles heredados | Industrial Moderno petróleo/turquesa |
| Biblioteca | Filtros laterales largos | Frecuentes arriba; avanzados plegables |
| Adaptación | Paneles Tk/columnas fijas | Splitters, columnas secundarias adaptables, ficha |
| Preview | Miniatura | Ampliación, zoom y desplazar |
| Editor | Componente antiguo embebido, área fija | Lienzo expansible + elementos/propiedades |
| Funciones | R1/R2/R3A actuales | Prueba interactiva parcial; sin emitir/importar |
| Distribución | Portable verificado | Build y EXE de prueba separados |

Capturas ejecutando widgets reales mediante --capture, no imágenes generadas ni HTML. Linux puede usar plataforma offscreen; Windows CI captura las mismas ventanas. Revisar en equipo COVEX y escalas 100/125/150/200 % antes de aceptar.

## Empaquetado y riesgos

Qt Essentials/shiboken6 6.8.3 fijados aparte del lock productivo. PyInstaller 6.16.0 onedir con hooks Qt; EXE de prueba excluye Tkinter/QML/Quick. Workflow instala wheels con hashes, regresión núcleo, 22 comprobaciones de widgets, build, mismas comprobaciones dentro del EXE y ZIP propio. Tamaño y SHA medidos en test-results.

Riesgos: mayor tamaño/arranque/plugins; DPI/fuentes, antivirus y Windows; diferencias de foco/eventos/diálogos; perder accesos o validaciones al adaptar. Revisar obligaciones de licencia Qt/PySide antes de entrega de uso real; no se afirma cumplimiento jurídico por empaquetar. CI acredita prueba en Windows Server 2022, no aceptación Windows 10/11, Word, impresión física o uso GMP.

No mezclar loops Tk/Qt en un proceso. Conservar ejecutable actual separado hasta completar matriz. Reutilizar núcleo, extraer coordinadores de gui.py al migrar cada pantalla, no duplicar motor, introducir SQL desde Qt o cambiar esquema innecesariamente.

## Coste y recomendación

Estimación orientativa de ingeniería, no precio/compromiso: Biblioteca/navegación 3–5 jornadas; adaptar editor actual con recorte/anclajes/guardado 6–10; emisión/envases/estado 5–8; historial/importación/configuración/backups 4–6; regresión/portable/DPI 3–5. Total **21–34 jornadas** para trasladar UI actual completa, sin ampliaciones R3B/R3C. Revisar tras primera adaptación; Word/impresión y deuda gui.py pueden aumentarlo.

Recomiendo **PySide6 para la futura interfaz**, condicionado a aprobar esta dirección visual. Más adecuado para lienzo, paneles, atajos y adaptación profesional, reutilizando servicios/motor/SQLite. Aprobar Biblioteca/Editor primero; después delimitar R3A Qt y acceso a legacy hasta verificar el 100 %. No integrar PR #2 ni iniciar R3B/R3C ahora.

Referencias oficiales consultadas 09/10/2026: [Qt deployment](https://doc.qt.io/qtforpython-6/deployment/index.html), [Qt/PyInstaller](https://doc.qt.io/qtforpython-6/deployment/deployment-pyinstaller.html), [PyInstaller hooks](https://pyinstaller.org/en/v6.16.0/hooks-config.html), [PySide6](https://pypi.org/project/PySide6/).


## Revisión de usabilidad aprobable — octubre 2026

La dirección visual y PySide6 están aprobados como objetivo de R3, condicionados a preservar todas las funciones. Esta revisión continúa siendo una prueba aislada en PR #3: no migra la aplicación ni autoriza su integración. PR #2 permanece sin integrar y main sin cambios. La matriz de 87 capacidades sigue siendo obligatoria, sin eliminar filas ni declarar funciones migradas por tener un botón informativo.

- Biblioteca: tabla principal sin barra lateral permanente. Categoría, Origen y Estado visibles; siete filtros avanzados en panel plegable, con contador de filtros activos aun estando cerrado. Todas, Favoritas y Recientes permanecen a mano.
- Código, Denominación, Versión y Estado siempre presentes, en ese orden. Denominación aprovecha el ancho libre. Extras adaptados al ancho real de la tabla y configurables en Columnas; la selección conserva identidad al ordenar. Inspector y ficha completa mantienen todos los metadatos, identificadores y referencias.
- Pocos resultados: tabla de altura reducida y ayuda contextual para continuar con la selección. Búsqueda sin resultados desactiva acciones documentales y no conserva una selección falsa.
- Inspector: Información, Versiones y Documentos. Abrir Editor, Favorita y accesos de emisión visibles. Panel ocultable y reabrible; compacto lo pliega automáticamente al entrar, sin bloquear su reapertura. Las acciones documentales avanzadas siguen claramente identificadas como no migradas.
- PDF: proporciones conservadas en ajuste, rueda y botones de zoom. Ajustar vuelve al documento completo; 100 % indica el ajuste actual, no tamaño físico de impresión. Vista ampliada con ajuste y controles propios; al aumentar zoom se desplaza el documento deliberadamente, sin recortarlo ni alterar su geometría.
- Editor: lienzo central predominante, herramientas contextuales avanzadas desplegables sin abandonar el documento y paneles ocultables mediante Paneles. Propiedades y elementos desplazan únicamente su contenido cuando la altura disponible lo exige. En ventanas bajas se compactan cabecera, títulos y controles. Texto fijo del PDF y propiedades temporales continúan siendo una demostración, no composición nativa ni guardado.

### Verificación de resolución y escala

Se ejecutan comprobaciones reales sobre Qt Widgets y nuevamente sobre el EXE en Windows Server 2022 con QT_SCALE_FACTOR 1, 1.25 y 1.5. Se verifican ventanas equivalentes a 1920×1080 y 1366×768, descontando un margen de marco, presencia de columnas prioritarias, proporciones, documento completo al ajustar, paneles, metadatos configurables y no modificación de plantillas.

Estos factores ejercitan el escalado de Qt en Windows CI. **No equivalen a cambiar la configuración nativa de pantalla de Windows a 100/125/150 %**, ni prueban cambio entre monitores, escalado mixto o aceptación en Windows 10/11 de COVEX. Esas pruebas reales siguen pendientes antes de aceptar R3A Qt funcional. Las capturas son QWidget.grab de ventanas ejecutadas, no imágenes generadas ni montajes.

Secuencia siguiente: validación visual de esta revisión; después rama y PR propias para R3A Qt funcional, reutilizando lo útil de PR #2 y #3 y verificando la matriz de 87 capacidades. R3B/R3C no iniciadas. Motor PDF, SQLite, servicios, configuraciones, datos reales e historial permanecen intactos.
