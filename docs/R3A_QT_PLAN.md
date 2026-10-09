# R3A Qt funcional — plan y revisión

Base: main 0.3.1. Rama feature/r3a-qt-functional. No integrar sin autorización. PR #2 y #3 siguen abiertas.

1. Reutilizar Industrial Moderno aprobado y servicios existentes; Biblioteca persistente, búsqueda/filtros, favoritos/recientes, ficha/documentos, metadatos documentados, revisión, aprobación externa e importación individual.
2. Retener vistas y trabajo activo. Edición Qt de campos existentes con guardado explícito y confirmación Guardar/Descartar/Cancelar. Recorte, espacio de estado, anclaje, comparación básica, importación carpeta, centro de impresión, emisión, historial y administración permanecen reales en Tkinter, con acceso explícito y mismos datos. No sustituir la aplicación distribuida.
3. Completar regresión y compilación Windows independiente con ambos ejecutables. Comprobar integridad, estados, no emisión accidental de pruebas y conservación de datos.
4. Entregar capturas Biblioteca amplia/compacta y Editor completo/Ajuste avanzado, matriz 87 filas y resultados. Aceptación interactiva COVEX pendiente antes de integración.

## Ejecutar y actualizar

En fuentes: INICIAR_R3A_QT.bat, opcional --demo para datos ficticios. En portable experimental: extraer carpeta completa y abrir COVEXLabelManager_Qt.exe --demo. Para revisar datos existentes use una COPIA completa de data con aplicación cerrada y establezca COVEX_LABEL_DATA a esa copia antes de arrancar; no copiar originales al repositorio. Puede usar --data-dir en Qt. Los modos --capture/--self-check ignoran datos reales y generan una sesión ficticia desechable.

La carpeta legacy es obligatoria para herramientas no migradas. No abrir otra instancia de la aplicación distribuida simultáneamente sobre los mismos datos. Cierre el compañero para volver a editar Qt. La ventana anterior conserva su formulario de emisión al navegar; cambiar de revisión descarta la configuración específica previa para no heredar datos de otro producto. Esto no equivale a guardar o recuperar un trabajo tras cerrar la aplicación.

Actualizaciones: extraer binarios nuevos en carpeta nueva. Conservar data y COVEX_LABEL_DATA; no sobrescribirlos desde el ZIP. Los scripts rechazan destinos que contengan datos. El paquete no incluye maestros, históricos, originales, credenciales ni información de fabricación. La aprobación estética, una nueva variante 00-R1 y una instalación no conceden aprobación documental.

## Usabilidad y alcance real

Filtros avanzados cerrados inicialmente; recordar apertura es opcional y se guarda sin tocar maestros. Todos los filtros activos aparecen fuera del panel. Pocos resultados muestran una franja breve de selección, sin duplicar acciones del inspector. Abrir Editor sirve para diseño, Preparar emisión exige vigencia/integridad y abre la versión anterior, PDF de prueba abre el modo explícito sin registro definitivo. Las acciones no migradas se identifican como versión anterior y abren una ventana real.

El Editor Qt representa los campos variables del PDF: posición, tamaño, identificador, nombre, fuente en puntos, negrita, obligatoriedad y bloqueo. La plantilla fija permanece PDF; no se implementa composición nativa. El zoom conserva proporciones y Ajustar muestra el documento completo. Recorte/zona/anclaje y su reajuste completo continúan en el editor anterior; la etiqueta no se reconstruye.

## Verificación y límites

Pytest del núcleo y Qt; comprobaciones Qt reales en fuente/EXE; compañero Tk empaquetado con emisión de un PDF marcado PRUEBA, sin emisión definitiva, revisión transferida y formulario retenido. Windows CI usa factores Qt 1/1.25/1.5 y ventanas amplias/compactas; registra dimensiones efectivas condicionadas por el escritorio virtual. No acredita DPI nativo, cambio entre monitores, Windows 10/11 COVEX, conversión Word, impresión física ni validación GMP. Estas pruebas reales siguen pendientes.

No R3B/R3C, integraciones externas, servidores, modelos nuevos de variante/producto, autoguardado, recuperación ni cambios al motor/SQLite. Usar la matriz 87 como condición de conservación y verificar cada fila antes de sustituir la distribución.
