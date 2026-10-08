# COVEX Label Manager 0.3.1

Aplicación de escritorio autónoma, portable Windows, principalmente de un usuario. Biblioteca, revisiones documentales, campos variables sobre PDF, emisión A4, perfiles, historial y reimpresiones. Sin servidores ni integración ERP/SharePoint. R3 no implementado.

## Contenido autorizado

Solo código, pruebas sintéticas, scripts y documentación técnica. No se distribuyen maestros originales, etiquetas reales, catálogo de materiales, documentos internos, emisiones ni bases de usuario. Una instalación nueva empieza con biblioteca vacía. Importe los documentos autorizados LOCALMENTE desde el Maestro; revise el recorte y configure campos en un borrador antes de aprobarlo. Las etiquetas de estado requieren fuentes locales existentes; no se suministran sus documentos reales en el portable.

00-R1 permanece pendiente de aprobación documental. Su código, un test aprobado, un tag o un build no constituyen aprobación para emisión. El software conserva revisiones y datos locales; no asigna metadatos no documentados.

## Ejecutar desde fuentes

Python 3.11+ con Tkinter y SQLite. En Windows, INICIAR_WINDOWS.bat prepara el entorno y arranca; en desarrollo:

```bash
python -m pip install -r requirements-dev.txt
python main.py
```

Windows portable se construye en Windows x64/Python 3.11.9 mediante BUILD_WINDOWS.bat o Actions. El destino final necesita la carpeta completa COVEXLabelManager, incluyendo _internal; no necesita Python. Word/LibreOffice no se incluyen. Todavía pendientes compilación y ejecución reales Windows, importación Word y medidas impresas.

## Datos y actualizaciones

`data/` junto a main.py o EXE, o ruta absoluta COVEX_LABEL_DATA. Contiene más que SQLite: originales, PDF maestros, emisiones y backups. No se versiona. Cerrar la aplicación, copiar data completo y extraer la nueva versión en otra carpeta; conservar el mismo data o ruta configurada. No sustituir bases ni actualizar sobre una instancia abierta. El build rechaza un destino que contenga data, SQLite o una ubicación configurada bajo ese destino. No hay actualizador automático que sobrescriba los datos.

## Verificaciones

```bash
python -m pytest -q
python scripts/check_repository_content.py
python main.py --self-check RESULTADO.json
```

Pytest crea documentos ficticios temporales, sin originales ni datos de producción. La comprobación del núcleo genera un PDF sintético y una base temporal; no abre la interfaz ni Word y no imprime. La conversión Word está omitida por defecto; requiere un ensayo real explícito. Pruebas gráficas manuales: tests/smoke_r1_r2_gui.py con pantalla disponible; capturas ficticias en test-results/, ignoradas por Git.

## Versiones y desarrollo

VERSION_HISTORY.md identifica 0.3.0 mediante v0.3.0-reference documental y 0.3.1 mediante v0.3.1. No importar el historial/bundle anterior con documentos originales. CONTRIBUTING.md exige ramas y PR para toda revisión posterior. ROADMAP.md distingue implementado, parcial, pendiente y propuesta; ARCHITECTURE.md describe límites y futura ampliación, sin conectores reales.

Ver docs/PUBLICATION_REVIEW.md y docs/WINDOWS_VALIDATION.md. La auditoría local no es inviolable y este prototipo no está validado para uso GMP productivo. Generar PDF no certifica su impresión física.
