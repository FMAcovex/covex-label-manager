# Revisión previa a publicación privada — 08/10/2026

Publicación de código 0.3.1 autorizada por el propietario. Repositorio FMAcovex/covex-label-manager creado y verificado privado. Incorporación inicial por rama/PR. No se han modificado otros repositorios.

## Cambios para excluir datos internos

- Historial nuevo, sin el Git bundle ni commits originales con documentos. v0.3.0-reference es una identificación documental; v0.3.1 identifica código de consolidación sin originales.
- Excluidos todos los PDFs/DOCX, catálogo real, ejemplos cumplimentados, capturas reales y reproducciones, archivos de usuario y documentación de traspaso innecesaria.
- Recursos del portable: únicamente README. Instalación nueva vacía. Maestros/materiales de una instalación existente continúan en su carpeta local, sin borrado, reemplazo ni importación nueva de datos de referencia.
- Tests generan diagramas planos DEMO/SYNTHETIC, documentos Word ficticios y catálogo ficticio; no proceden de originales ni contienen datos reales de fabricación. Su configuración se limita al proceso de prueba.
- Auto-comprobación del EXE usa PDF y base temporales ficticios. No incorpora el generador de fixtures de tests al ejecutable.
- 00-R1 se conserva pendiente. Para datos antiguos, puede derivarse solo desde fuente local íntegra con huella conocida; nunca desde un documento incluido en GitHub. Requiere aprobación explícita real antes de emitir.

## Comprobaciones

49 pruebas pasan y una se omite (conversión Word no certificada por CI), Python 3.12/Linux. Incluyen arranque vacío, actualización manteniendo maestros/variantes/catálogo/configuraciones/preferencias, creación pendiente R1 desde fuente local y rechazo de build sobre destinos con datos. La comprobación del núcleo pasa desde fuentes. Smoke gráfico con fixtures sintéticos pasa; no acredita Windows.

Las comprobaciones geométricas con los originales realizadas antes de sanear permanecen como evidencia privada, no como archivos publicados. La suite actual verifica regresiones con documentos ficticios; no se presenta como nueva validación de todas las etiquetas COVEX.

Revisión de lista completa de archivos y de todos los objetos del historial publicable: sin documentos ni assets binarios, bases, archivos de credenciales o patrones de tokens habituales. El script de control se ejecutará también en Actions. No constituye una auditoría exhaustiva de secretos.

## Publicación y aceptación pendientes

Abrir y revisar PR de incorporación, ejecutar Actions, revisar resultados y configurar protección de main. No se ha ejecutado un build Windows todavía. Después descargar artefacto privado y aplicar WINDOWS_VALIDATION.md; Word y medidas impresas necesitan entorno real. No se ha iniciado R3 ni integración externa.
