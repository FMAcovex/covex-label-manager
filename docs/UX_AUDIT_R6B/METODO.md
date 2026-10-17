# Método, límites y reproducción

## Fuente y entorno

Último `origin/main` consultado: `afd0b06454c54e1e722596c37a6f6557883f2c16`. Se parte de un checkout limpio, se obtiene `main` y se crea una rama `chore/ux-audit-r6b` en el checkout existente; no se crea otro worktree. Las instrucciones de CONTRIBUTING exigen rama/PR, no escritura directa en main. No se modifica código funcional, tests, dependencias, locks, esquema ni configuraciones de aprobación.

Entorno: Debian 13, Python incluido 3.12.14 en `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python`; virtualenv `/workspace/cloud-setup/venv312`, dependencias fijadas por `requirements-dev.txt` y `requirements-qt.txt`, PySide6 6.8.3/Fusion. Setup previo conserva Xorg dummy en `:99`. Las pruebas usan `offscreen`; capturas finales `xcb`, Xorg 1920×1080, factores Qt 1/1.25/1.5 y áreas cliente objetivo correspondientes a 1366×768 y 1920×1080. Se reservan 40 DIP para decoración/barra. No son capturas de Windows ni de un equipo COVEX.

## Comandos ejecutados

```bash
cd /workspace/covex-label-manager
source /workspace/cloud-setup/activate.sh
uv pip check --python /workspace/cloud-setup/venv312/bin/python
python -m pytest -q --junitxml=test-results/ux-audit-baseline.xml
python /workspace/cloud-setup/ux_inventory.py
bash /workspace/cloud-setup/start-display.sh
# Repetido para (1366,768) y (1920,1080), y factor 1 / 1.25 / 1.5:
QT_QPA_PLATFORM=xcb QT_SCALE_FACTOR=1 \
    timeout 110 python /workspace/cloud-setup/ux_capture.py 1366 768
python /workspace/cloud-setup/ux_summarize.py
python scripts/check_repository_content.py
git diff --check
```

La salida completa de pruebas y capturas se conserva en `test-results/` o en `/workspace/cloud-setup/`, fuera de lo versionado. Las fuentes exactas de los cuatro auxiliares de auditoría y validación están como bloques documentales en [REPRODUCCION.md](REPRODUCCION.md); se pueden guardar fuera del checkout para reproducirlos. Generan solo documentación/artefactos y datos temporales; no son una modificación del producto ni nuevos tests declarados como parte de su suite.

## Capturas y evidencias

`DemoSession` crea 12 etiquetas ficticias y estados documentales de fixture, sin cargar `COVEX_LABEL_DATA` ni maestros de producción. El recorrido selecciona pendiente/vigente/retirada, una variante DRAFT, trabajo de lote y excepciones de validación. Para consultar Historial, genera un PDF/registro solo en la base temporal de demo mediante el servicio normal. No acepta diálogos de aprobación, no cambia la aceptación GMP, no envía a dispositivos ni convierte Word real.

Se detienen los timers de polling de la ventana para estabilizar el recorrido; las acciones y servicios siguen siendo los existentes. Los menús se inspeccionan con una subclase local sin activar comandos. Los `exec` modales se sustituyen temporalmente para mostrar, capturar y rechazar; las preguntas retornan Cancel. La captura no demuestra que cada acción termine correctamente: para eso se referencia la suite funcional y se declaran lagunas.

Cada widget se intenta ajustar al área objetivo. Si su mínimo exige más, se registra el tamaño real; no se recorta para simular adaptación. PNG por `QWidget.grab` con DPR real; SVG por render directo de widgets a `QSvgGenerator`, sin reconstrucción manual. Solo se versionan SVG documentales de datos ficticios y JSON/Markdown de evidencia, manteniendo el control de contenido del repositorio. Los PNG, SQLite y documentos temporales no entran en Git.

Los SVG son capturas vectoriales de cliente, sin decoración del SO y con imágenes sintéticas rasterizadas dentro del vector. Los tokens visuales y algunas posiciones pueden variar con fuentes/Qt/Windows. Las rutas temporales, fechas e identidades ficticias de ejecución no son una base de comparación píxel a píxel estable.

El inventario AST incluye etiquetas, gráficos, scroll, señales y fábricas; los controles creados por bucles están expresados en `loop_expansion`. No es un analizador de ejecución completa de Python: MRO, widgets retirados y callbacks se contrastan en INVENTARIO.md y runtime. Las referencias de tests por coincidencia de símbolo son pistas, no porcentajes de cobertura.

Se comprueba aparte una base nueva sintética: `PRAGMA user_version=4` y `PRAGMA quick_check=ok`. La validación documental verifica 87 IDs únicos, 884 sitios fuente, seis configuraciones/306 capturas, 123 SVG sin scripts ni referencias externas, hashes PNG y enlaces locales. El control de contenido y `git diff --check` pasan. Estos checks documentales no sustituyen pruebas de aplicación.

## Límites y controles de alcance

- Todos los estados son sintéticos. Las aprobaciones y emisiones que las pruebas generan pertenecen exclusivamente a sus fixtures. La revisión documental de un maestro real nunca se automatiza.
- No se inspecciona ni copia contenido de credenciales, datos reales, catálogo productivo o evidencias confidenciales. Git usa el proxy existente.
- No hay benchmark de operadores, medición de tiempos de Word, validación de driver ni accesibilidad UIA. Tampoco golden histórica para certificar conservación de cada aspecto visual anterior.
- La captura de `FolderImportDialog` documenta una implementación R3F conservada; la entrada de menú actual abre `ControlledImportDialog` R5B. No confundir presencia de clase con alcance de navegación.
- El diseñador de hoja consulta `QScreen`, que en Xorg es 1920×1080; los tamaños de ventana pequeños se emulan dentro de esa pantalla. El exceso mínimo de un diálogo respecto al objetivo se registra y debe repetirse con pantalla Windows real.
- La publicación se solicita como PR borrador exclusivamente documental. Abrir la PR no autoriza squash, merge, cambios de código ni aceptación de las propuestas.
