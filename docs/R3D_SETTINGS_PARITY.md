# R3D · Configuración Qt, cuadros modales y auditoría de paridad

Base: main R3C integrado, commit dcf0b91e3c153d5e822ce07f7181bcedc6121b4c.

## Propósito
Completar Configuración en PySide6, igualando las funciones reales de \`BaseApplication.page_admin\`: operador, ubicación de datos, copia ZIP, catálogo CM, duplicados, aprobación de maestros de estado y auditoría. Incluir recuentos del Inicio clásico. Se reutilizan los **mismos métodos LocalServices**; no se escribe SQLite desde el UI y no cambia el esquema v4.

## Cambios visuales
- Pantalla nativa Qt de cinco pestañas: Resumen, Preferencias y datos, Catálogo CM, Maestros de estado y Auditoría local.
- Cuadros de diálogo Qt (QDialog/QMessageBox/QInputDialog), etiquetas, entradas, listas y tooltip con fondo y texto claros en Windows con tema oscuro.
- Paneles con scroll para escalado elevado; etiquetas y acciones con nombres inequívocos.
- El vínculo a Configuración clásica permanece como compatibilidad hasta aceptación real.

## Criterios de integridad
1. Guardar operador exige identificador de al menos 3 caracteres. No se reescribe el historial.
2. Directorio de datos solo lectura; trasladar datos requiere cerrar procesos y procedimiento de copia integral.
3. Copia usa LocalServices.backup con bloqueo y verificación; confirma previamente, no sobrescribe anteriores. Restauración manual/offline conservada.
4. Importar CM usa read_cm e import_materials; cancela sin modificaciones; sin borrado automático ni corrección de duplicados.
5. Maestros de estado: selecciona pendiente, requiere responsable, referencia externa y confirmación explícita de cotejo Word; usa approve_status_master y no aprueba por abrir/navegar.
6. Auditoría es solo consulta de los últimos eventos del registro local.
7. No se modifica ningún maestro, diseño fijo, 00-R1, motor PDF, snapshot o trabajo recuperable.
8. Modo demo crea y modifica únicamente datos temporales ficticios.
9. Se conservan accesos Tk como compatibilidad y se comparan las **87 capacidades** de la matriz histórica.

## Auditoría de las 87 capacidades frente a la versión anterior

Revisados métodos de Tkinter en gui.py, LocalServices, ventanas Qt y matriz de 87 IDs.
- R3C: **66 Qt, 4 parciales, 10 anteriores, 7 motor**.
- R3D (objetivo, sujeto a CI/aceptación): **75 Qt, 3 parciales, 2 anteriores, 7 motor**.
- C01–C07 y C10 pasan a Qt (8 capacidades). M11 pasa de parcial a Qt (1).
- D14 (comparador básico de imágenes) e I02 (importación masiva con progreso y cancelación) permanecen en Tk. No se deben describir como Qt ni retirar hasta migración y paridad probada.
- Parciales D03 (conservación de originales por motor), D04 (incorporación y origen/carpeta) e I01 (Word con conversor local y ensayos reales pendientes).
- Verificar por flujo, no solamente por disponibilidad de un botón. No hay prueba de aceptación GMP, Windows 10/11 reales, Word real ni impresión física.

## Puerta de aceptación
Pruebas sintéticas de operador, backup con manifiesto, CM acumulativo, cancelación y bloqueo de aprobación, tema claro en modales, 87 IDs y regresiones Qt/Tk/Windows. Comparar capturas en Windows 1366×768 al 125/150 %. **No hacer merge ni afirmar compatibilidad productiva sin autorización**.
