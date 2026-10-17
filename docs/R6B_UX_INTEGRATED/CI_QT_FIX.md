# Corrección del fallo nativo Qt de PR #29

## Diagnóstico y causa demostrada

Referencia inicial: [diagnóstico publicado](https://github.com/FMAcovex/covex-label-manager/pull/29#issuecomment-6236833031).
La suite Qt pasaba, pero el self-check Windows al 100 % terminaba sin JSON ni traceback.
La instrumentación conservó todas las comprobaciones y reveló el código nativo
`-1073740791` (`0xC0000409`), no una aserción de aceptación fallida. Ctrl+K, foco,
navegación compacta y límites de ventanas pasaban. La última secuencia era recorte → anclaje.

Se reprodujo en Linux/Qt 6.8.3 forzando `gc.collect()` antes y después de preparar
cada diálogo. GDB, instalado localmente a partir de paquetes Debian verificados por
APT fuera del checkout, capturó dos hechos consecutivos:

```text
QScreen::~QScreen()
  shiboken6 / libshiboken6.abi3.so.6.8
  gc_collect_main
  gc.collect
...
SIGSEGV:
  QScreen::virtualSiblings()
  QGuiApplication::screenAt(QPoint const&)
  QWidget::screen()
  QWidget::metric(...)
  QFont::QFont(..., QPaintDevice const*)
  QWidgetPrivate::init(...)
```

El wrapper de pantalla obtenido mediante `QWidget.screen()` quedaba ligado a un
widget transitorio. Su invalidación/recolección podía destruir el `QScreen` nativo
que Qt seguía enumerando. Por eso la caída aparecía al crear otro widget, sin poder
ser capturada por `except Exception`. Es un problema de vida útil del binding observado
con PySide 6.8.3; no se atribuye a documentos, aprobaciones ni al motor PDF.

## Corrección aplicada

- Se consulta la pantalla por `QApplication.screenAt()` con el centro global del
  diálogo, con fallback a `primaryScreen()`, sin pedir un wrapper al diálogo.
- El diseñador de hojas reutiliza ese límite adaptable en vez de consultar
  `self.screen()` durante su construcción; no cambian medidas ni perfiles de hoja.
- Se conservan wrappers de las pantallas actuales en la aplicación. Se actualizan
  al entrar en ventanas/diálogos y ante `screenAdded` / `screenRemoved`; no se
  cambia el padre nativo de pantallas, DPI, resolución ni configuración del monitor.
- Se mantiene preparación adaptable antes de la apertura nativa e idempotente.
  El cuerpo desplazable y los botones persistentes no se eliminan.
- El visor tiene protección de reentrada durante `fitInView`; las barras son
  estables durante Ajustar y reaparecen según necesidad en zoom manual. Es una
  protección adicional: por sí sola no resolvió la caída y no se presenta como causa raíz.

La variante que conserva referencias a pantallas pasó la misma reproducción con
recolección forzada que antes terminaba en SIGSEGV. La regresión incorporada ejecuta
el self-check completo en un subproceso, exige salida cero, JSON correcto y los
**86 controles**, y fuerza la recolección entre diálogos sin sustituir callbacks.
También se comprueban conservación de wrappers, actualización por hotplug, ausencia
de llamadas a `dialog.screen()`, preparación previa al show y reentrada del visor.

## CI y portable

El workflow registra progreso, código nativo de salida, traceback Python antes de
imprimirlo e informes UTF-8; usa `-X faulthandler`. El self-check se adelanta para
diagnóstico rápido, pero se conserva íntegra la suite posterior y sus umbrales,
checks congelados, puente Qt/Tk, compatibilidad y seis configuraciones visuales.

El ZIP Qt incorpora `BUILD_MANIFEST.json`, la guía R6B-UX y una verificación adicional:
CRC, ausencia de rutas inseguras/duplicadas, inventario exacto y SHA256 de cada archivo,
incluidos Qt, Legacy y `chevron.svg`. El informe `qt-archive-integrity.json` incluye
SHA256 del ZIP y commit de construcción. Los tests rechazan archivos alterados,
inventarios incompletos, rutas inseguras y contenido no registrado.

Resultados definitivos y enlaces a las tres ejecuciones y al artefacto se registran
en la [PR #29](https://github.com/FMAcovex/covex-label-manager/pull/29) y sus Checks.
El SHA del manifest puede ser el merge commit de prueba de GitHub, no el SHA del
head de la rama; debe coincidir con el checkout del run enlazado.

La serie SVG histórica de esta carpeta documenta la implementación UX integrada;
las capturas PNG/JSON del run final prueban el código corregido en Windows. No se
reescribe la auditoría `02f7ba7`. No se alteran las 87 capacidades, SQLite v4,
servicios, aprobaciones, numeración, snapshots ni reglas de emisión/reimpresión.
CI verde e integridad del ZIP no acreditan GMP, Word real ni impresión física.
