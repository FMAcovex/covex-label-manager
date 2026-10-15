# R3E — Extensión de paridad

La matriz `FUNCTIONAL_PRESERVATION_MATRIX.md` conserva sus 87 entradas y sus botones. No se eliminan suites anteriores.

| Área de referencia | Cambio R3E | Evidencia |
|---|---|---|
| Editor y biblioteca | Herramientas anteriores + campos visibles, dibujo y ocho tiradores | test_r3a_qt, test_r3b1_qt, test_r3e_qt |
| Variantes y aprobaciones | Mismo ciclo; sin mutación directa de aprobadas/retiradas | test_variants_v4, test_r3e_qt |
| Trabajos recuperables | Perfil ampliado; CAS y reconciliación previos | test_emission_work, test_emission_work_qt, test_r3e_layout |
| Motor A4 y escalado | Misma aritmética grid; cajas compartidas; proporción del maestro preservada | test_core, test_regressions_v02, test_r3e_layout |
| Nuevos papeles/libre | Ruta explícita versionada; rechazo de formato desconocido | test_r3e_layout, r3e_checks |
| Emisión / selección / estados | Servicios y recibos anteriores; copias limitadas a 1–2 | test_r3c_emission_qt, suites núcleo, r3e_checks |
| Historial/reimpresión | Snapshot extendido; motivos/numeración originales e integridad | test_r3c_history_qt, test_r3c_history, r3e_checks |
| Backup / perfiles / concurrencia | Sidecars con hash y catálogo compartido | test_r3e_layout |
| Acompañante Tk D14/I02 | Se conserva; formatos nuevos nativos bloqueados | r3e_backward_gate, gate Windows/migración y pruebas de puente anteriores |
| Ajustes R3D y diálogos | Herramientas conservadas; propiedades desplazables | test_r3d_settings_qt, capturas r3e_checks |

Las pruebas técnicas no son aprobación documental ni validación GMP. Artefactos y resultados finales se generan en Actions para el SHA de la PR.
