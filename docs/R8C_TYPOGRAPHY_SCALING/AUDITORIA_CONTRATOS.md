# R8C — auditoría previa de contratos

Base inspeccionada: `56399394424896a1adbd56a91882a7eb49282632` (R8B). Datos exclusivamente sintéticos.

| Componente | Contrato existente | Ampliación compatible prevista |
| --- | --- | --- |
| `engine.py` | Campos normalizados, cuatro modos de texto; selección histórica Arial/Liberation/DejaVu según SO | Rama tipográfica **opt-in**, fuentes PDF deterministas embebidas; no cambiar `_fonts()` ni la rama histórica |
| `editor_layout.py`, variantes | Campos JSON, historial completo, bloqueo geométrico, hash y generación | Atributo opcional `typography` versionado; guardar por las mismas rutas documentales |
| `status_design.py` | Contrato 1, rectángulos absolutos en puntos; normalización elimina atributos desconocidos | Contrato 2 explícito para nuevas propiedades; lectura/renderizado de contrato 1 sin reinterpretación |
| `status_catalog.py` | Revisión, hash, aprobación externa, snapshots, PDF individual | Mismo catálogo y ciclo; ampliación opcional de formato/composición, sin migración SQL |
| `status_combined.py`, motor | Resolución explícita de revisión; ajuste proporcional centrado; fondo y variables dibujados separadamente | Composición única fondo+variables y transformación uniforme, ajuste/relleno con inspección conservadora de contenido crítico |
| `work.py`, `emission_centre.py` | Borrador recuperable, guardado CAS, prueba en subproceso, token contra resultados obsoletos | Ajustes temporales persistidos en el trabajo, visibles como prueba; mismos invalidación, generación, token y cierre seguro |
| `emission_work.py`, `emission_contract.py` | Intención, render, comprobación documental, receipt y registro SQLite v4 | Bloqueo de personalizaciones temporales **antes de la intención** y también en el motor; conversión explícita a variante DRAFT, nunca aprobación |
| `sheet_designer.py`, perfiles | Formato físico proporcional, perfiles CAS con checksum; zoom independiente | Reutilizar formato/perfiles y copia de trabajos; no crear un segundo catálogo tipográfico |
| Historial/reimpresión | Snapshot, fuente y hashes; PDF registrado verificado | Mantener PDF histórico exacto; no añadir parámetros por defecto a diseños/snapshots antiguos |

## Decisiones de seguridad

- SQLite de producto continúa en v4 y el catálogo de estados conserva su esquema.
- Las nuevas fuentes proceden de los recursos incorporados por PyMuPDF/MuPDF; se embeben en el PDF. No buscar fuentes en el equipo para diseños nuevos ni distribuir TTF externos.
- La ausencia de un recurso o glifo bloquea la nueva representación: no sustituir silenciosamente una tipografía documental.
- La tipografía histórica continúa por la implementación original. Las nuevas opciones sólo se activan mediante un contrato explícito.
- Rellenar no significa estirar: se calcula un recorte fuente uniforme. Texto fijo, imágenes, trazos y campos variables se consideran críticos. Los fondos planos sin borde pueden recortarse; cualquier duda bloquea el relleno y ofrece ajuste/variante.
- Un perfil operativo o trabajo copiado no es una aprobación GMP. Los ajustes de apariencia temporales bloquean toda emisión definitiva hasta restablecerlos o documentarlos en una variante que siga su ciclo externo.
- Revisiones, variantes, aprobaciones y procedencia no se infieren del aspecto visual ni del tipo «Aprobado».

No se ha realizado validación GMP ni aceptación manual Windows. R8D queda fuera de alcance.
