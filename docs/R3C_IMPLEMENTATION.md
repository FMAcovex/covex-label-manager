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

## Implementación y contratos finales

- R3C1: `EmissionCentreMixin` conserva WorkPanel compartido con Editor. Valida con
  `review_work`, presenta errores junto al dato y exige una vista previa vigente
  antes de confirmar. Su token incluye trabajo/generación y maestro de estado.
  Prueba y definitivo se generan por WorkRepository; la prueba exportada conserva
  el hash exacto. Se verifica de nuevo después del diálogo de confirmación.
- R3C2: `HistoryService` concentra consulta/verificación/preparación/reproducción.
  Tk también utiliza este coordinador. Reimpresión conserva datos, copias,
  estado, perfil y diseño originales; solo cambia selección/casilla inicial.
  `emission_contract.record_issue` comprueba de nuevo origen, PDF, snapshot,
  identidad y datos en BEGIN IMMEDIATE. La huella del origen detecta cambios
  entre render y registro. Catálogo bloqueado frente a backup concurrente.
- R3C3: formularios multilínea, proporción/restaurar tamaño, perfiles reutilizables,
  tabla/pegado, previsualización multipágina y mensajes sin rutas internas. El
  formato/prueba del Editor muestra etiquetas/hojas/avisos y «Cerrar» (#7).
  No modifica composición maestra, textos fijos ni motor PDF.

No se añaden estados de impresión física. La confirmación registra generación
PDF. Un fallo posterior al commit de trabajo se reconcilia como ISSUED; un fallo
anterior conserva EMITTING para recuperación expresa. Histórico sin snapshot/hash
mantiene advertencia y aceptación expresa; no inventa integridad retrospectiva.

Resultados, paridad, instrucciones de pruebas y límites en [R3C_PARITY.md](R3C_PARITY.md).
CI final entrega informes JSON/XML, capturas de ventanas reales sintéticas y
portable con acompañante. Las 87 IDs se mantienen, sin afirmar 100 % de migración.
