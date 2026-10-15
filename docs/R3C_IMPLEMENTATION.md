# R3C · Centro de emisión Qt

Base obligatoria: main 86475779b1eac6f39c9098e0e9d67dd2de51d5fe.
R3A/R3B1/R3B2/R3B3 integradas. Desarrollo sintético, sin merge autorizado.

## Revisión anterior a la implementación

Qt ya dispone de Biblioteca/Editor, variantes, trabajos JSON canónicos, autoguardado,
recuperación, datos de lote/recipientes y parámetros de formato/perfil. `WorkPanel`
se comparte con Editor; la prueba abre el visor externo. `issue_emission_work`
lanza el acompañante Tk. Historial/reimpresión y calibración de emisión siguen en Tk.

Se reutilizan WorkRepository.get/save/proof/issue, bloqueo de carpeta/UID, generaciones,
reconciliación EMITTING/ISSUED, emission_contract y las restricciones SQLite v4.
No nueva tabla, columna, índice ni cambio de contrato de almacenamiento. Motor PDF
sin reescritura. Vista previa = páginas rasterizadas del PDF de prueba realmente
renderizado, con datos del trabajo; no una composición paralela de Qt.

La coordinación heredada de reimpresión se comparte mediante servicios locales:
PDF y snapshot verificados, estados/identidades/fuentes revalidados, números originales,
perfil histórico con casilla inicial explícita, motivo y vínculo obligatorio.
El histórico sin snapshot no se rellena retrospectivamente: advertencia y aceptación
expresa antes de reproducir usando la revisión documentada. Generar PDF no certifica
impresión física.

## Bloques y comprobación

1. R3C1: centro nativo, selección, formularios existentes, validación visible,
   resumen A4, vista previa real, prueba, confirmación e issue por WorkRepository.
2. R3C2: historial, detalle legible, integridad, consulta y reimpresión por contrato.
3. R3C3: Industrial Moderno, escalados/resoluciones, regresión y paridad, corrección
   de incidencia #7, portable y capturas sintéticas.

Se guardan commits por bloque. Pruebas específicas locales durante desarrollo;
regresión Windows completa y compilación al finalizar. Las 87 IDs se conservan.
Las evidencias finales y capacidades todavía en Tk se enumerarán al cerrar R3C.

Pendientes externos: Word/Office real, impresión física, Windows 10/11 y equipos
COVEX, aceptación del uso previsto/validación GMP. Sin R4/R5 ni conectores externos.
