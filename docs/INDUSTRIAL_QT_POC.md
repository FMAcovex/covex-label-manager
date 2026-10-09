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

Funciones no adaptadas muestran alcance y accesos actuales. FUNCTIONAL_PRESERVATION_MATRIX.md inventaría las capacidades que deben conservarse. Tkinter permanece íntegro y su workflow independiente se mantiene.

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
