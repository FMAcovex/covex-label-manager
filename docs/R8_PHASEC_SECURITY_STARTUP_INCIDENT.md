# Fase C — Incidencia de cuarentena y cierre en un equipo Windows

## Situación (21/10/2026)

En el PC del usuario se solicita elevación al extraer y posteriormente un antivirus
pone componentes del portable en cuarentena. El usuario también informa de un
cierre inesperado al iniciar o utilizar la aplicación. **No hay evidencia para
considerar las detecciones un falso positivo ni para atribuir el cierre
exclusivamente al antivirus.** El paquete generado y extraído en Windows CI
superó sus regresiones, pero eso no sustituye aceptación en el endpoint.

Resultado: aceptación de la Fase C **BLOQUEADA**. No realizar pruebas con
etiquetas reales, no registrar emisiones y no usar datos GMP productivos.

## Evidencia de referencia del paquete PR #48

- PR #48 integrada, árbol fusionado de referencia: `31698a350e80f0da18980640d96a2113143bbec6`.
- GitHub Actions CI Qt: `39425179437`, artifact `12266986799`.
- Compilación del artifact Qt: `df8c6d96a28f2b8e992c6beae02125294f1499ac`;
  el diff de archivos frente al merge #48 es vacío. No implica firma o aptitud de seguridad.
- SHA-256 del ejecutable principal: `4e25192db990b88a5182badcaf19a2359962ea74e27126ee7695fde5f882b7ba`.
- SHA-256 del ejecutable auxiliar: `e7f01da97f04beaa75f55d3b10ea0276e2748bb99f4b449a6d70e2552acedd55`.
- Ambos hashes coinciden con `BUILD_MANIFEST.json` dentro del ZIP inspeccionado.
  Esto demuestra coherencia con el build inspeccionado, **no inocuidad**.

## Datos a recoger sin desactivar ninguna protección

1. Captura del evento en Cuarentena/Historial de protección: producto
   antivirus, identificador o nombre exacto de la detección, archivo afectado,
   acción y hora. Ocultar rutas personales o de la organización si se comparte.
2. Distinguir si el archivo puesto en cuarentena es
   `COVEXLabelManager_Qt.exe`, `legacy/COVEXLabelManager_Legacy.exe`
   o una DLL en `_internal`. El cierre podría depender de cuál falte.
3. Si Seguridad/IT confirma que se puede continuar y se recupera un paquete
   completo y autorizado, ejecutar `DIAGNOSTICAR_ARRANQUE_QT.bat` dentro
   del portable: abre la DEMO ficticia y deja la consola mostrando el
   código de salida y si desapareció uno de los ejecutables.
4. Si la aplicación permanece accesible, exportar un diagnóstico desde
   Configuración (R8A) y revisar su contenido antes de compartirlo.
   Ante terminación nativa o por antivirus puede no existir traza Python.
5. IT/Seguridad debe valorar el resultado y, si procede, remitir
   la muestra original/identificador al proveedor antivirus para análisis
   de posible falso positivo. No restaurar archivos ni crear exclusiones
   a ciegas; no desactivar el antivirus.

## Cambios de esta PR

Se agrega un **lanzador de diagnóstico de operador**, sin elevación, sin
persistencia nueva y sin modificar el programa. `start /wait` evita que
desaparezca la ventana antes de mostrar el código de salida; detecta ausencias
del ejecutable principal, auxiliar y carpeta `_internal`.
No intenta eludir cuarentena, Defender, AVG, políticas corporativas ni firmas.
No recoge documentos, datos personales, lotes o diagnósticos brutos.

No se cambia `main_qt.py`, el motor PDF, SQLite v4, el esquema, la aprobación
documental, las 87 capacidades ni el resto de lanzadores.

## Condiciones para desbloquear aceptación

- Archivo detectado, identificación y dictamen de Seguridad/IT registrados.
- Paquete completo y de procedencia verificada, autorizado por IT para ensayo.
- Apertura, uso y cierre de demo sin terminaciones inesperadas en el PC objetivo;
  verificar también retorno de un cierre normal y un flujo de emisión ficticio.
- Solo entonces reiniciar la Fase C con etiquetas reales autorizadas.

Una CI verde o un ZIP íntegro **no certifica que el antivirus lo acepte**,
ni sustituye firma digital, controles IT o validación GMP.
