# R6B — Interfaz Qt para pruebas presenciales
Acceso: Configuración → Resumen → Sesiones de pruebas R6B.

## Nueva sesión
Seleccione ZIP R6A previamente exportado, identifique equipo, Windows, usuario, commit completo y SHA-256 del portable. Seleccione ruta de archivo JSON **fuera de data**. La aplicación valida integridad del paquete R6A. No se registran automáticamente pruebas superadas.

## Apertura y seguimiento
Puede abrir un JSON de sesión o generación. El panel muestra 14 casos, estado y criterios. Seleccione un caso, introduzca resultado, responsable, fecha AAAA-MM-DD, motivo/observaciones y, si procede, una evidencia externa. PASS exige evidencia con SHA-256 válido. Otros resultados no conformes/bloqueados requieren motivo. Confirmar guarda un **nuevo JSON generación N+1**, sin sobrescribir el anterior. Guarde y archive ambos en entorno autorizado. Las referencias de archivo son locales y requieren accesibilidad futura. Verificar evidencias comprueba bytes y hashes; no certifica una prueba física.

## Límites y cierre
La interfaz no imprime ni convierte Word, no cierra UAT ni aprueba GMP. Todo estado global permanece NO ACEPTADO. SQLite v4 no cambia. Las pruebas presenciales reales (Windows 10/11, Word, impresoras, libro máster, respaldo/restore) y la firma documental del responsable de calidad siguen pendientes de R6C.
