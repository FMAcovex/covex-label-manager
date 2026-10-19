# COVEX Label Manager R8-RC1 — Windows Qt Portable

**Candidata para aceptación integral, no release oficial ni autorización productiva.**

## Identidad y origen

- Fuente obligatoria: `main`, **504e542b17bbb8bfe2210fca8c9e19016aa42970**.
- Árbol Git: **10cf8dd37ed7c10c65e97ebd96ca826ce2144645**, igual al R8D probado `ac4542de2f0195f84474f12de67ee9b349555cc4`.
- #33 / R8A fusionada `defcb1ffb1204a201d5b04703fde50d681a8f6dd`; #34 / R8B `6adab6e64907fb29fef8283b62a54147eb7afe85`; #35 / R8C `c54c22108207e20fba2f9f87b3f125ce2ca0bee7`; #36 / R8D es el main indicado. Todas constan MERGED el 19/10/2026. Fusiones realizadas por el propietario antes de RC1, no por este trabajo.
- Ninguna modificación funcional en RC1. Este paquete documental se revisa aparte; no requiere fusionarlo para ejecutar el portable de main y no se incluye falsamente en el manifiesto de ese build.

## Ejecución explícita sobre main

Los tres `workflow_dispatch` se solicitaron con `--ref main` y sus `head_sha` coinciden con **504e542b17bbb8bfe2210fca8c9e19016aa42970**. No se utilizan los artefactos de PR36 como build integrado.

| Workflow | Ejecución de main | Resultado |
| --- | --- | --- |
| Windows tests and portable build | [39276850333](https://github.com/FMAcovex/covex-label-manager/actions/runs/39276850333) | SUCCESS; 380 passed, 24 skipped en 228,77 s; build y self-check empaquetado correctos |
| Qt editor and functional transition | [39276855169](https://github.com/FMAcovex/covex-label-manager/actions/runs/39276855169) | **BLOQUEADO: sin conclusión publicada; cancelación solicitada después de superar el límite configurado de 25 min** |
| R3B2 migration safety gate | [39276860103](https://github.com/FMAcovex/covex-label-manager/actions/runs/39276860103) | SUCCESS; 26 pruebas en 41,08 s, gate de migración `ok: true` |

Antecedente revisado de R8D, mismo árbol pero **otro commit/build**: [Windows 39270382406](https://github.com/FMAcovex/covex-label-manager/actions/runs/39270382406), [Qt 39270382365](https://github.com/FMAcovex/covex-label-manager/actions/runs/39270382365), [Migración 39270382364](https://github.com/FMAcovex/covex-label-manager/actions/runs/39270382364), las tres SUCCESS. Las ejecuciones push canceladas durante fusiones consecutivas no son por sí solas fallos de código; no se cuentan como CI satisfactorias de RC1.

La suite general Windows no instala Qt: los casos que requieren ese entorno se comprueban por separado en el job Qt, no se consideran aprobados por estar saltados. Los grupos de pruebas de distintos jobs se solapan y no se suman como pruebas únicas.

### Incidencia RC1-CI-01 — entrega técnica retenida

La ejecución Qt comenzó el 19/10/2026 a las 15:18 UTC. Las consultas muestran la fase comparativa R8D iniciada a las 15:24:11 UTC, sin conclusión ni artefactos incluso después del límite configurado de 25 minutos. La API devuelve además 502/503 intermitentes y algunas respuestas sin detalle de pasos. Se solicitó su cancelación a las 15:45 UTC para recuperar logs; la aceptación de esa solicitud no prueba que el job haya terminado.

**Demostrado:** estado no satisfactorio/no final disponible, ausencia de artefacto Qt verificado y bloqueo de descarga del log en vivo (`Forbidden`). **Pendiente de diagnóstico:** bloqueo real del comparador/aplicación frente a interrupción del runner/servicio GitHub; no se atribuye causa raíz sin evidencia. No se ampliaron límites, quitaron controles ni se sustituyó el build por el de R8D. El archivo completo de logs sólo podrá recuperarse cuando GitHub lo publique; los intentos previos devuelven 404.

La política de descarga deniega el host exacto observado `productionresultssa18.blob.core.windows.net`. Se guardó un borrador de red para ese host y los accesos GitHub necesarios, sin cambiar scripts, credenciales o código. Guardado no equivale a aplicado/publicado. Si el archivo completo no permite continuar, revisar/guardar y publicar esa configuración es un prerrequisito externo para obtener el log en vivo; no arregla por sí solo una CI atascada.

**No se recomienda aún el cierre técnico ni se ofrece un portable como R8-RC1 verificado.** Resolver RC1-CI-01 y repetir el gate estricto sobre main antes de completar la entrega. Si se demuestra un defecto, preparar una PR correctiva independiente sin fusionarla automáticamente.

Suite completa local, Python 3.12.14 / PySide6 6.8.3 / Linux Qt offscreen: **640 passed, 2 skipped en 451,36 s**, sobre HEAD `504e542b17bbb8bfe2210fca8c9e19016aa42970`, antes de crear el commit documental de RC1. Los únicos cambios en curso eran documentación; código y pruebas idénticos a main. XML local `test-results/r8-rc1-main.xml`, log local `r8-rc1-main-pytest.log`; no se confunden con el artefacto Windows. Los dos omitidos son el ensayo Word real (requiere activación/entorno explícito, no se ejecutó) y el lector SQLite antiguo exclusivo Windows, cubierto por el gate Windows.

Comprobación complementaria Linux de este mismo código, sin parche funcional: `main_qt.py --guided-check` con Qt xcb nativo al 125 %, dos resoluciones objetivo, **14 capturas y 10 trazas**, `ok: true`, cuatro pasos, mismo trabajo, SQLite v4/integridad, original aprobado intacto, emisión PDF registrada, reimpresión y cierre normal. Se revisaron visualmente Inicio 1920 y revisión compacta 1366: navegación/acciones visibles, marca PRUEBA y controles de ampliación conservados. Es evidencia local complementaria; no sustituye aceptación humana ni el EXE Windows.

## Descarga única para el usuario

**Pendiente:** sólo se entregará el artefacto Qt publicado tras completar los controles del EXE realmente extraído del ZIP de esta ejecución. Aquí se registrarán enlace, nombre técnico, SHA-256 del ZIP interno, inventario, CRC y caducidad. No se reutilizará el ZIP de la rama R8D ni se recomendará el Tk de la CI general como segunda versión.

El nombre recomendado al guardar el ZIP interno será **COVEX-Label-Manager-R8-RC1-main-504e542b17bb-Windows-x64.zip**. El renombrado no cambia sus bytes ni SHA. El nombre del artefacto de Actions incorpora el SHA completo; BUILD_MANIFEST.json identifica commit, ejecución, versiones y cada archivo. El SHA del contenedor exterior de GitHub es distinto del de este ZIP interno.

R8-RC1 identifica esta candidatura de aceptación, no una modificación de la versión histórica 0.3.1 del código. No se retoca el EXE, ZIP ni manifiesto para cambiar rótulos después de probarlos. Para identificar inequívocamente el programa, usar conjuntamente R8-RC1, SHA de main, ejecución y hash del ZIP, no sólo un rótulo de la ventana.

Las capturas/JSON/informes se ofrecen en un artefacto técnico separado. El compañero Legacy incluido en la carpeta de la aplicación se conserva para compatibilidad; no son dos versiones candidatas distintas.

## Alcance de compatibilidad e integridad

El workflow utiliza Windows Server 2022 x64, Python 3.11.9 y dependencias fijadas con hashes. Verifica ZIP completo/inventario/CRC/SHA, recursos Qt/Legacy y arranca el EXE de **ese ZIP extraído** para los contratos R8A–R8D. Los checks recorren 100/125/150 % y los objetivos 1366×768 / 1920×1080, con área cliente ajustada por escala/barra del sistema. R8B/C/D emplean offscreen para tamaños exactos frente al límite del escritorio alojado; existen además regresiones nativas Windows. No se afirma validación física de monitores ni Windows 10/11.

Sólo datos sintéticos en CI; no se empaquetan bases corporativas ni documentos reales. La verificación Windows del ZIP y su EXE será la evidencia de integridad; si la descarga binaria a este entorno Linux está bloqueada, no se afirmará haberla ejecutado aquí ni se eludirá la política de red.

## Paquete para aceptación y cierre

- [Guía de ocho pruebas](PRUEBAS_USUARIO.md).
- [Registro editable de resultados](RESULTADOS.csv), todas **No probado**.
- [Plantilla de incidencias por prioridad](INCIDENCIAS.csv), sin datos de ejemplo que puedan confundirse con aceptación realizada.
- [Revisión consolidada, 87 capacidades, ampliaciones y licencias pendientes](REVISION_CONSOLIDADA.md).

La conclusión de cierre técnico se completará con los resultados finales. Permanecen pendientes Word real/conversor, impresora/medidas/papel, puestos Windows 10/11, aceptación de operarios, licencias, procedimientos y verificación documental. Cierre técnico no significa aceptación funcional, aprobación documental, autorización de despliegue ni validación GMP. No se crean tags/releases ni se fusiona ninguna PR en esta fase.
