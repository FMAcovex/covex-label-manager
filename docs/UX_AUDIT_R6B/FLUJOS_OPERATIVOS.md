# Experiencia operativa y coste de interacción

Los recuentos son **análisis de recorrido de la interfaz actual**, contrastado con controles/controladores y pruebas, no tiempos medidos con operadores. Una acción es un clic/selección o rellenar un campo completo; un bloque de texto cuenta como una entrada, no como pulsaciones. No se cuentan movimientos del ratón ni inspección visual. Scroll, selección de archivo, corrección de errores y navegación inicial se indican aparte. Los mínimos asumen controles visibles, revisión elegible y ninguna corrección. La serie de capturas usa servicios temporales para preparar ciertos estados: no se presenta como un ensayo de usabilidad de extremo a extremo.

| Objetivo | Secuencia mínima analizada | Acciones | Cambios de pantalla principal | Riesgo de fricción |
|---|---|---:|---:|---|
| Preparar y registrar lote desde Biblioteca | Seleccionar; Preparar emisión; nombre; crear; lote; PN; PB; pestaña Formato; cantidad; vista previa; Emitir; confirmar | 12 | 1, Biblioteca→Emisión | Inspector requiere scroll; primer trabajo pide identidad y datos por pestañas; preview obligatorio es útil. |
| PDF de prueba desde trabajo ya válido | Actualizar vista previa si falta; PDF de prueba; destino; guardar | 3–4 | 0; compacto requiere alternar datos/PDF | Dos acciones relacionadas, pero preview interno y exportar archivo no son lo mismo. |
| Modificar diseño pendiente | Seleccionar; abrir Editor; seleccionar campo; cambiar propiedad; guardar diseño | 5 | 1 | Lista lateral puede estar oculta; propiedades bajo scroll. Preview/inspección del resultado añaden acciones necesarias. |
| Ajustar campos de una revisión vigente | Seleccionar; abrir Editor; Ajustar campos…; motivo; crear variante DRAFT; seleccionar campo; modificar; guardar | 8 | 1 | Código/nombre propuestos reducen entradas; falta explicar con claridad la independencia de la variante. No concede aprobación. |
| Registrar aprobación externa de revisión pendiente | Seleccionar; Registrar aprobación; responsable; referencia; reconocimiento; Registrar; confirmación | 7 | 0; dos modales | Segundo control duplicado confunde. La confirmación de retirada anterior debe mantenerse. |
| Enviar/aprobar variante | Abrir menú; Enviar a revisión; confirmar; reabrir menú; Aprobar; responsable; referencia; fecha; aceptar formulario; elegir evidencia; confirmar | ≥11 | 0, con varios modales/selectores | Requiere estado apropiado y documento externo real. Validación del servicio puede rechazar opciones aparentemente disponibles. |
| Consultar PDF histórico | Historial; seleccionar registro; Verificar y ver PDF | 3 | 1 | La selección ya inspecciona integridad pero no carga la vista; hay un segundo paso explícito de consulta. No eliminar verificación. |
| Registrar reimpresión desde Historial | Seleccionar registro; Reimpresión; motivo; Registrar; confirmar | 5 | 0 | Números/casilla prellenados. Subconjunto o casilla distinta añaden 1 acción cada uno; reconocimiento heredado añade otra. |
| Enviar PDF registrado a impresora | Imprimir PDF registrado; seleccionar impresora; confirmar diálogo | ≥3 | 0, modal SO | Hoja usada añade aviso; disponibilidad/driver no se ejercitan en Linux. Entrega a driver ≠ papel confirmado. |
| Guardar operador | Configuración; Preferencias y datos; identificador; Guardar | 4 | 1 | Dock residual puede interferir; no es autenticación. |
| Copia verificada | Configuración; Preferencias y datos; Crear copia; confirmar; cerrar aviso | 5 | 1 | Operación avanzada razonablemente explícita. Restauración sigue offline. |

## Qué pasos son útiles y cuáles conviene reducir

La selección de revisión/variante, la comprobación del diseño, el motivo de reimpresión, la evidencia de aprobación y las confirmaciones finales no son «clics sobrantes». Mantienen la intención y el registro. El rediseño debe reducir búsqueda, scroll accidental, reapertura de menús y cambios de contexto, no suprimir estas barreras.

Operaciones evitables demostradas: recorrer un catálogo de transición cuando se busca gestión nativa de revisiones/variantes; localizar una acción inferior tras varios bloques del Inspector; recuperar manualmente un panel ocultado por tamaño; cerrar un dock fuera de contexto; interpretar dos botones de aprobación y dos tipos de calibración con etiquetas ambiguas. La cantidad de scroll depende de resolución/factor/estado y no se convierte en un número fijo de clics.

## Separación por frecuencia

| Uso frecuente | Uso ocasional documentado | Administración avanzada / aceptación |
|---|---|---|
| Buscar, seleccionar revisión/variante, abrir trabajo, datos de lote/recipiente, preview, emitir, consultar/reimprimir | Editar variante, importar documento, nueva revisión, registrar aprobación, seleccionar formato/perfil | Importación masiva/conciliación, exportación íntegra, CM/duplicados, backup/restauración, calibración, maestros de estado, auditoría, R6A/R6B |

La frecuencia propuesta debe confirmarse con operadores; no existe telemetría de uso en esta auditoría. La aprobación puede ser frecuente para un responsable documental, pero no debe compartir jerarquía con la emisión cotidiana de un operador.

## Criterios de aceptación de la experiencia

- Usuario puede explicar qué está editando: revisión documental, variante de diseño o trabajo de lote; los tres estados aparecen sin contradicción.
- Un trabajo ya creado y válido no exige pasar por Editor ni volver a crear la identidad del documento para emitir.
- El modo compacto ofrece el mismo conjunto de operaciones con un camino visible, sin depender de conocer un icono sin texto.
- Al salir de Editor, el dock no invade Biblioteca/Historial/Configuración y no se pierde el trabajo.
- Se puede corregir cada aviso desde un resumen con destino claro y confirmar que no hay emisión duplicada tras un fallo/reintento.
- Comparar con operadores autorizados usando escenarios ficticios: éxito a la primera, acciones de recuperación, pantallas visitadas y errores de interpretación. No fijar segundos de mejora sin medición inicial.
