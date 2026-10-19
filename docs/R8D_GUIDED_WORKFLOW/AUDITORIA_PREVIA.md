# Auditoría previa R8D

Base inspeccionada antes de programar: R8C `8859f21ab77878b3e5c874bfac0023d0c8ad2ca3`. Sólo fixtures sintéticos. La guía de entorno se usa para reutilizar Python/Qt/MuPDF fijados; no requiere nuevos paquetes ni alterar SQLite.

## Problemas y controles comprobados en código

| Flujo/control real | Situación R8C | Decisión R8D |
| --- | --- | --- |
| `window.py:StudioWindow`, cabecera | Biblioteca/Editor/Emisión/Historial/Configuración/Estados al mismo nivel; no inicio operativo | Inicio por tareas y acceso consistente al asistente; conservar accesos existentes |
| `emission_centre.py:new_emission_work` | Diálogo exige nombre, revisión y variante antes de introducir datos; selector técnico de todas las revisiones | Buscador en pantalla, identidad/documentación visibles, elección explícita ante ambigüedad |
| `WorkPanel` | Nuevo/Copiar/Recargar, selector/Abrir, guardado y otros botones; cantidad y copias en pestaña Formato | Presentación guiada del mismo WorkPanel, cantidad visible, herramientas técnicas en opciones adicionales |
| `WorkPanel.display` | Formulario ya construido desde fields_json; valores conservados, pero no marca todos los obligatorios | Reutilizar contrato y añadir indicación de obligatoriedad en presentación guiada |
| `refresh_emission_review` y `automatic_preview` | Errores junto al campo, PDF real en trabajador aislado, token/generación/hash | Reutilizar exactamente revisión y vista previa, nunca un compositor alternativo |
| Footer Centro | Guardar/PDF de prueba/Emitir/Imprimir juntos | Separar revisar y resultado final, conservar confirmación documental y distinguir impresión externa |
| `WorkPanel` Estado | Revisión histórica o vigente, ubicación, alineaciones y composición, todo junto | Sección «Añadir etiqueta de estado», explicación «Aprobado» ≠ aprobación documental |
| `variants.py:build_variant_menu` | Ya filtra acciones por ciclo y explica bloqueos | Mantener sin duplicar gestión documental; explicar variante en ayuda breve |
| `advanced_editor.py`, `workspace.py` | Tres zonas, tipografía/ejemplos/geometría y PDF real, protecciones nativas R8A/B | Conservar objetos/controladores; no rediseñar ni sustituir el Editor |
| `status_manager.py`, `status_fields_dialog.py` | Biblioteca integrada, editor de estado y emisión individual existentes | Acceso directo desde Inicio/administración; no nuevo catálogo de estados |
| `sheet_designer.py` | Diseñador físico y perfiles existentes | Mismo diseñador desde opciones de formato; no nuevo contrato |
| `emission_appearance.py` | Prueba temporal y derivación DRAFT sin aprobación implícita | Acceso desde revisión guiada, mismas guardas antes de INTENT |
| Historial `HistoryMixin` | PDF verificado, reimpresión con motivo y registro | Acceso desde Inicio/resultado; no imprimir ni modificar registros para nuevo lote |
| `SettingsMixin` | Operador, datos, copia verificada, diagnóstico y compatibilidad | Accesos explícitos, sin sistema de permisos nuevo |
| `EmissionWorkMixin.flush_emission_work` | CAS por UID/generación, retiene datos en pantalla si falla | Compartir único trabajo activo; bloquear navegación si no se guarda |
| `operator_error`, `work_action` | Algunas rutas muestran str(ex), potencial ruta o excepción técnica | Mensajes operativos controlados; detalles al diagnóstico privado R8A |
| Puente Tkinter | `legacy_process` bloquea modificaciones; servicios/identidad compartidos | Mismo bloqueo para asistente e Inicio, sin crear segundo motor |

## Método de medición antes/después

Una acción es un click/activación de control, selección o edición de un campo; no se cuentan caracteres. Cambios de pantalla son cambios de página/pestaña; los diálogos se cuentan aparte. Las cinco tareas se describirán como secuencias reproducibles y no como tiempos o ahorro inventados. Estado inicial, revisión/variante y datos sintéticos iguales. Las confirmaciones obligatorias se cuentan en ambos recorridos. Medición automatizada separada de aceptación con operarios.

## Arquitectura prevista

Inicio y asistente nativos añadidos a `FunctionalWindow` después de construir los controladores actuales. Un `WorkPanel` guiado se integra en `work_panels`; no persiste nada fuera de `api.work`. La vista PDF guiada observa el resultado validado del Centro, sin regenerar un diseño distinto. Los cambios de pantalla guardan con el mismo CAS; volver al Centro conserva UID/generación. No se copian lotes/pesos/fechas al preparar otra emisión. La definitiva llama al controlador actual, con sus confirmaciones, revisión, hash e historial.

## Validación obligatoria planificada

Regresiones sobre controles PySide6 reales, servicios/PDF/SQLite reales y fixtures privados; seis tamaños lógicos, tres escalas Windows, comparación R8C/R8D, recorrido del EXE extraído, suite completa y tres CI exactas. No sustituir operaciones críticas con mocks; sólo automatizar la respuesta humana de confirmación o destino de guardado. No eliminar aserciones ni extender timeouts para obtener verde. Evidencia binaria fuera de Git. R8A/B/C y 87 capacidades conservadas; aceptación integral y GMP siguen pendientes.
