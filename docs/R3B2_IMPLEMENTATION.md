# R3B2 — implementación por puertas verificables

Base: e83953b023a6c40702a276745a1fcaeae278dbd1. Esquema autorizado por el usuario el 15/10/2026; PR #8 permanece referencia, sin integrar.

## Puerta 1: migración y recuperación

Módulos aislados `migration_v4`, `schema_v4`, `canonical`. No activados todavía desde Store/arranque. El flujo trabaja sobre snapshot, verifica filas/archivos, instala barrera mediante mkdir exclusivo, publica storage_v4 y conserva backup completo con manifiesto. La recuperación no mezcla bases ni elimina archivos legacy inesperados. El formato antiguo sin migrar se conserva para construir y probar los ejecutables reales anteriores.

Pruebas sintéticas: integridad de backup/restauración, idempotencia, rechazo de esquema/hash inválido, cortes en las cinco fases, carrera de creación legacy, serialización canónica. `scripts/migration_gate.py` mata el proceso con código 73 en cada fase y genera recibos de restauración exacta. En Windows construye los entrypoints Tk y Qt SIN CAMBIOS del commit base y prueba fuentes y EXE frente a handles exclusivos y barrera. La prueba exige diagnóstico SQLite y ausencia de cambios; un error de dependencias no cuenta como bloqueo.

La puerta Windows es obligatoria antes de avanzar con repositorio de variantes, PDF e interfaz. Resultados pendientes en esta primera publicación. Nada de esta rama migra datos reales. No squash/merge autorizado. R3B3/R3C/conectores excluidos; Word real, impresión, Windows 10/11, equipos COVEX y GMP no certificados.
