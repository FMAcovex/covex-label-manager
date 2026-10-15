# R3B2 — implementación por puertas verificables

Base: e83953b023a6c40702a276745a1fcaeae278dbd1. Esquema autorizado por el usuario el 15/10/2026; PR #8 permanece referencia, sin integrar.

## Puerta 1: migración y recuperación

Módulos aislados `migration_v4`, `schema_v4`, `canonical`. No activados todavía desde Store/arranque. El flujo trabaja sobre snapshot, verifica filas/archivos, instala barrera mediante mkdir exclusivo, publica storage_v4 y conserva backup completo con manifiesto. La recuperación no mezcla bases ni elimina archivos legacy inesperados. El formato antiguo sin migrar se conserva para construir y probar los ejecutables reales anteriores.

Pruebas sintéticas: integridad de backup/restauración, idempotencia, rechazo de esquema/hash inválido, cortes en las cinco fases, carrera de creación legacy, serialización canónica. `scripts/migration_gate.py` mata el proceso con código 73 en cada fase y genera recibos de restauración exacta. En Windows construye los entrypoints Tk y Qt SIN CAMBIOS del commit base y prueba fuentes y EXE frente a handles exclusivos y barrera. La prueba exige diagnóstico SQLite y ausencia de cambios; un error de dependencias no cuenta como bloqueo.

La puerta Windows es obligatoria antes de avanzar con repositorio de variantes, PDF e interfaz. Resultados pendientes en esta primera publicación. Nada de esta rama migra datos reales. No squash/merge autorizado. R3B3/R3C/conectores excluidos; Word real, impresión, Windows 10/11, equipos COVEX y GMP no certificados.

## Estado comprobado al 15/10/2026

- Regresión Linux/Python 3.12 con Qt offscreen: **144 correctas, 2 omitidas** (Word real y exclusión de handles propia de Windows). Migración específica: **17 correctas, 1 omitida** de Windows. La ejecución de Qt requiere `QT_QPA_PLATFORM=offscreen` en este host sin pantalla.
- Cinco terminaciones abruptas por `os._exit(73)`, recuperación v3/v4 según fase y restauración exacta del backup. Pruebas adicionales preservan dos emisiones históricas, relación de reimpresión, variables/perfil, UIDs y snapshots NULL. Backup incluye evidencias y datos WAL aún no checkpointados. Fallo DDL revierte completamente staging; backup corrupto y esquema alterado se rechazan; audit de recuperación se registra una sola vez.
- Vector canónico conocido (decimales, Unicode NFC, -0 y exponente) SHA-256 `c59ed642cbc30ff3b0fbcea26eb3c0e32718a6ebfc1a4ce16959401d83ce33ad`. Se exige el mismo valor en el script y la CI Windows.
- Recibo local y hashes de los archivos ensayados: [R3B2_MIGRATION_LOCAL_RESULTS.json](R3B2_MIGRATION_LOCAL_RESULTS.json). Son evidencias sintéticas Linux; `windows_old_executables_proven=false` expresamente.
- El workflow nuevo tuvo un error inicial YAML, ya corregido y validado localmente. El intento posterior de Windows y su reintento terminaron antes de asignar runner: `runner_id=0`, `steps=[]`, sin artefactos. [Ejecución 38697115989, intento 2](https://github.com/FMAcovex/covex-label-manager/actions/runs/38697115989/attempts/2). También el workflow Windows preexistente terminó sin pasos. Los conectores no han devuelto el motivo administrativo; no se atribuye a facturación, permisos o código sin evidencia.

**Puerta Windows NO superada.** No se implementan las fases 2–5 ni se activa migración desde Store. No hay capturas de variantes ni portable R3B2 nuevo porque esas etapas dependen de esta comprobación. Para reanudar se necesita una ejecución Windows efectiva del workflow, que construye por sí mismo ambos EXE anteriores. Si la barrera falla en esa ejecución, se presentará una alternativa antes de seguir, tal como exige la autorización. No se solicita nueva aprobación del esquema para repetir la prueba ya autorizada.
