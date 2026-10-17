# Registro priorizado de incidencias

Base y capturas: ver README.md y EVIDENCIAS.md. «Demostrado» exige fuente y/o reproducción descrita; «pendiente» expresa una hipótesis o una comprobación externa todavía no hecha. No se ha demostrado corrupción, emisión incorrecta ni bypass de aprobación.

Prioridades: P0 = riesgo de integridad/seguridad inmediato demostrado (ninguno identificado); P1 = bloqueo o degradación importante del flujo; P2 = error de orientación, claridad o consistencia; P3 = refinamiento. Frecuencia es la exposición esperada, no telemetría. Riesgo GMP es una estimación contextual: A/M/B = alto/medio/bajo; no equivale a fallo GMP demostrado. Esfuerzo orientativo en días de desarrollo + pruebas, después de aprobar alcance: XS <0,5; S 0,5–1; M 1–3; L 3–6. No es presupuesto comprometido.

| ID | Hallazgo / estado | P / severidad | Impacto / frecuencia | Riesgo GMP estimado | Esfuerzo / dependencia |
|---|---|---|---|---|---|
| UX-01 | Dos botones de Inspector distintos abren aprobación de revisión; demostrado | P2 / media | Confunde consulta documental y cambio de estado; cada consulta | M: intención errónea, mitigada por diálogo y servicio | S; aprobar vocabulario y conservar un acceso claro |
| UX-02 | «Revisiones y variantes» conduce al catálogo de transición Tk; demostrado | P1 / alta | Desvío de una operación ya Qt; frecuente al buscar revisión | M: confusión entre entidades/ventanas | S; navegación nativa aprobada, mantener compatibilidad explícita |
| UX-03 | Modales no caben en objetivo 1366×768/125–150 %; demostrado en Qt/Xorg | P1 / alta | Formularios o cierre fuera del área objetivo; equipos compactos | M: lectura parcial, no bypass demostrado | M; política de scroll + pruebas Windows |
| UX-04 | Editor compacto oculta elementos y reduce mucho el lienzo; demostrado | P1 / alta | Edición y aprendizaje degradados; cada edición compacta | M: dificultad para revisar el diseño | L; reorganización de barras/paneles, pruebas de geometría |
| UX-05 | Inspector y herramientas de trabajo importantes quedan bajo scroll; demostrado | P2 / media | Aprobación, preparación, pegado/perfiles menos descubribles; frecuente | M: elección de ruta más larga/confusa | M; jerarquía y área útil mínimas |
| UX-06 | Dock de trabajo persiste al entrar en Configuración; demostrado | P1 / alta | Comprime incluso cabecera/navegación; cambia contexto operativo | M: trabajo activo aparece en pantalla administrativa | S–M; contrato único de navegación y retención |
| UX-07 | Compacto oculta zoom, abrir PDF y nota del visor; demostrado | P2 / media | Controles y advertencias solo en ruta ampliada; vista compacta | M: contexto de comprobación menos visible | M; visor compacto con acceso a todas las acciones |
| UX-08 | Menú documental mezcla tareas frecuentes, administración y códigos R5A/R5C; demostrado | P2 / media | Mayor búsqueda/curva de aprendizaje; recurrente | B | S–M; aprobar arquitectura de acciones |
| UX-09 | «Calibrar hoja» y «Calibrar impresora» parecen equivalentes, pero no lo son; demostrado | P2 / media | Expectativa errónea de haber calibrado por generar PDF | M: interpretación de calibración | S; redacción con alcance y estado |
| UX-10 | `resizeEvent` sustituye «Restablecer diseño» por «Restablecer campos»/«Restablecer»; demostrado | P2 / media | Acción afecta más que lo que su etiqueta sugiere | M: descarte/restauración de diseño; undo mitiga | S; etiqueta única + alcance/confirmación según impacto |
| UX-11 | Menú de variantes habilita por existencia de selección, no por transición aplicable; demostrado por fuente | P2 / media | Acción aparentemente disponible acaba en error del servicio | M: intención confusa, guardas conservadas | M; modelo de comandos por estado; no mover guardas al UI |
| UX-12 | Modales mezclan Cancel/Close/OK con textos españoles; informes técnicos JSON; demostrado | P2 / media | Menor comprensión y consistencia; usos administrativos | B | S; glosario y formato humano + detalle técnico plegable |
| UX-13 | Botones simbólicos sin nombre accesible explícito; asociación real de campos pendiente | P2 / media | Posible dificultad con lector/teclado; transversal | B–M según tarea | M; árbol accesible/UIA y pruebas de teclado |
| UX-14 | Texto `subtle` de 12 px tiene contraste insuficiente frente a fondos principales; demostrado por tokens | P2 / media | Avisos secundarios difíciles de leer; muy frecuente | M si contiene instrucciones operativas | S; tokens de texto y verificación por superficie |
| UX-15 | Importación/conversión por documento ocurre en hilo UI; estructura demostrada, pausa real no cronometrada | P1 / alta potencial | Interfaz puede no responder durante Word/PDF grande | M: reintentos/cancelación mal interpretada | L; worker aislado con conexión propia, progreso/cancelación segura |
| UX-16 | Matriz histórica conserva clasificación R3C y textos de transición; demostrado | P2 / media | Percepción de funciones perdidas o no migradas | B–M: documentación operativa incoherente | S; actualizar documentación en cambio posterior aprobado |
| UX-17 | Varias capas de guardado y dos paneles con mismos mandos; demostrado | P2 / media | Confunde guardar diseño con autoguardar trabajo | M: diseño vs lote no equivalentes | M–L; separar entidades visualmente sin unificar persistencia |
| UX-18 | Pérdida general de funciones visuales anteriores; sospecha no confirmada | Investigación | No hay golden histórica suficiente ni caso concreto identificado | Sin asignación hasta demostrar | M; comparación de artefactos anteriores y entrevistas |
| UX-19 | Medidas de formato muestran largas colas decimales binarias; demostrado | P2 / media | Lectura/edición de mm menos clara; trabajo con tamaño derivado | B–M: interpretación de precisión, motor no alterado | S; formato de presentación y round-trip exacto |

## Evidencia y reproducción por incidencia

### UX-01 · Entrada duplicada de aprobación

En Biblioteca, seleccionar revisión pendiente → Inspector → Documentos → «Documentos y aprobación externa» abre `approve_revision`. El botón inferior «Registrar aprobación de revisión…» llama al mismo método. `BaseFunctionalWindow.build_library` desconecta y reconecta el primer control; `approve_revision` abre `RevisionApprovalDialog`.

Fuente: [functional.py](../../covex_label_manager/qt_ui/functional.py), `build_library` y `approve_revision`. Evidencia: `03-biblioteca-documentos`, `24-aprobacion-revision` en la galería; `observations.approval_accesses` del JSON. No se recomienda borrar una capacidad: mantener una acción explícita de registro y hacer que la consulta documental cumpla su nombre.

### UX-02 · Acceso residual heredado

Biblioteca → Inspector → Versiones → Revisiones y variantes. Resultado: `show_access('document') → navigate('document') → catalog`, con explicación de Tk y botón para abrir versión anterior. No abre el selector ni el gestor Qt. La misma ventana dispone de «Variantes ▾» y «Gestionar variantes».

Fuente: [window.py](../../covex_label_manager/qt_ui/window.py), `build_library/show_access/navigate`; [functional.py](../../covex_label_manager/qt_ui/functional.py), `navigate/open_catalog_legacy`. Evidencia: `35-acceso-heredado-residual`, booleano `revisions_variants_opens_legacy_catalog=true` en las seis configuraciones. La contingencia Tk sigue siendo necesaria hasta aceptación; el desvío ordinario no lo es.

### UX-03 · Diálogos con altura mínima superior al objetivo

Intentar abrir/formar cada modal al área cliente objetivo de 1366×768/150 %: **910×472 DIP** tras reservar 40 DIP. Qt impide reducir Formato físico y prueba PDF por debajo de **607 DIP**, UAT por debajo de **554 DIP** y conciliación por debajo de **676 DIP**. Son respectivamente unos **911, 831 y 1014 px** de alto, antes de decoración. Al 125 % también hay ventanas mayores que el área pedida; a 1920×1080 no se observa este exceso en la serie.

Fuentes: [advanced_editor.py](../../covex_label_manager/qt_ui/advanced_editor.py) `edit_output`, [uat_session_dialog.py](../../covex_label_manager/qt_ui/uat_session_dialog.py), [master_reconcile_ui.py](../../covex_label_manager/qt_ui/master_reconcile_ui.py). Evidencia: `dynamic-10`, `32-sesion-uat`, `32b-sesion-uat-casos`, `33-conciliar-master`; métricas en resultados-visuales.json. Es una reproducción del contrato de tamaño Qt; repetir con escritorio Windows real. Propuesta: contenido desplazable, resumen compacto y pie siempre disponible; no quitar información ni confirmaciones.

### UX-04 / UX-05 · Espacio y controles poco visibles

En el Editor inicial de 1366×768/100 %, el lienzo mide aproximadamente 260 DIP de alto; al 150 % queda en torno a 104 DIP. La cabecera global, título, barra de zoom/undo, variante y alta de campo ocupan cinco franjas. Debajo de 1100 DIP de anchura `StudioWindow.resizeEvent` oculta Elementos; se puede recuperar con Paneles/Avanzadas, pero no hay una indicación persistente de que se ocultó. Las casillas de snap/cuadrícula y propiedades tienen textos cortados o scroll estrecho.

En Biblioteca normal, las acciones inferiores del Inspector requieren desplazamiento vertical; es accesibilidad reducida, no desaparición ni botón inoperante. Las herramientas Pegar Excel/Guardar perfil/Calibrar hoja también están al final del panel desplazable de Emisión.

Fuentes: [window.py](../../covex_label_manager/qt_ui/window.py), `build_library/build_editor/resizeEvent`; [emission_centre.py](../../covex_label_manager/qt_ui/emission_centre.py), `build_emission_page`. Capturas `01`, `07`, `08`, `10`, `12`, `14` y `16`, comparando 1366/150 con 1920/100. Las alturas se contrastan en los rectángulos del control `Preview` del inventario runtime, no se extrapolan como tamaño físico del PDF.

### UX-06 · Dock fuera de contexto

Editor → Datos del trabajo → Configuración. El dock sigue visible (`dock_visible_in_settings=true` en todas las combinaciones). `SettingsMixin.navigate` resuelve y guarda pero retorna sin pasar por el cierre del dock de `EmissionWorkMixin.navigate`. En 1366/150 llega a comprimir el encabezado y los textos de navegación.

Fuentes: [settings.py](../../covex_label_manager/qt_ui/settings.py), `navigate`; [work.py](../../covex_label_manager/qt_ui/work.py), `navigate/show_editor_work`. Captura `34-config-dock-residual`. No se ha demostrado mezcla ni escritura incorrecta de datos. Ocultar el dock al salir del Editor debe conservar el trabajo y su estado, no descartarlo.

### UX-07 · Visor compacto

Emisión a altura <650 DIP → Vista previa PDF. `PdfPane.compact` oculta `tools` y `note`; desaparecen Ajustar, zoom, Abrir PDF y la nota de contexto del visor. Página y Ampliar permanecen; el feedback del centro también mantiene parte de la advertencia. No son acciones eliminadas del motor.

Fuente: [pdf_view.py](../../covex_label_manager/qt_ui/pdf_view.py). Captura `16-emision-preview` al 150 %. La propuesta debe ofrecer las acciones en un menú visible y mantener una indicación de prueba/definitivo siempre presente.

### UX-08 / UX-09 / UX-10 / UX-11 / UX-12

Menús efectivos completos en `observations.menus`; expresiones de fábricas y bucles en inventario-sitios.json. Calibrar hoja ejecuta `calibrate_emission` (genera regla PDF); Calibrar impresora abre `CalibrationDialog` y acepta medidas. Restablecer se construye con nombre de diseño y se renombra desde la base al redimensionar. `variant_menu` habilita las transiciones solo por selección no nula, mientras el servicio valida el ciclo. Los cuadros estándar y conciliación/UAT conservan Close/Cancel en esta plataforma; Windows puede localizar algunos, pero no debe dependerse de ello para toda la UI.

Fuentes: `actions_menu`, `variant_menu`, `StudioWindow.resizeEvent`, `calibrate_emission`, `WorkPanel.calibrate_printer`, `QDialogButtonBox` de cada módulo. Capturas `24`, `28`, `30`, `31`, `32`, `33`. No fusionar calibración ni estados por el parecido del nombre.

### UX-13 / UX-14 · Accesibilidad

El registro observado incluye `accessible_name`, tooltip, texto y geometría, pero no un árbol accesible de Windows. `+`/`−` requieren nombre explícito de contexto; falta demostrar el anuncio real de cada entrada de formulario. `QFormLayout` puede asociar etiqueta y control, por lo que un `accessibleName` vacío no prueba por sí solo un defecto.

El token `subtle` **#72868C** sobre blanco tiene contraste **3,82:1** y sobre **#F3F6F7**, **3,51:1** (fórmula sRGB WCAG); no alcanza 4,5:1 para texto normal a 12 px. Es una medición de tokens, no una certificación WCAG de toda la app. El texto deshabilitado está excluido de esta conclusión. Fuente: [style.py](../../covex_label_manager/qt_ui/style.py), `QLabel#subtle`. Recalcular sobre superficies reales y comprobar foco/iconos/selección antes de aceptación.

### UX-15 · Conversión en hilo UI

`ControlledImportDialog.step` llama de forma síncrona a `api.catalog_migration_apply`; la importación por documento llega al conversor. El temporizador separa archivos, no libera el hilo durante la conversión. El diálogo R3F conservado tiene la misma limitación documentada. No se realizó un ensayo Word grande ni se midió tiempo de bloqueo; queda prohibido describirlo como cuelgue reproducido o pérdida de datos.

### UX-16 / UX-17 / UX-18 · Conservación y percepción

La matriz histórica tiene encabezado R3C y recuento 66/4/10/7; el código actual incluye Configuración R3D, comparador R3F, carpeta controlada R5B y envío R4C. Los mixins también conservan textos/métodos de transición, algunos reemplazados y otros todavía alcanzables. La presencia de un texto obsoleto en fuente no demuestra que se muestre: esta auditoría distingue los casos capturados.

Diseño usa `save_work` y trabajo usa `flush_emission_work`; ambos tienen controles llamados Guardar en contextos cercanos. El dock compartido ofrece además acciones de trabajo dentro del Editor. Conservar la separación de persistencia y nombrarla explícitamente. La sospecha de funciones visuales perdidas requiere reproducir cada caso frente a un artefacto histórico autorizado y la misma resolución; no se recomienda recuperar funcionalidades no implementadas como si hubieran existido.

### UX-19 · Precisión de medidas en presentación

Emisión → Formato y emisión, con tamaño derivado del PDF sintético: los campos muestran `152.39999999999998` y `105.83333333333333` mm. `WorkPanel.display` convierte el valor del perfil con `str`, sin formato de lectura. Evidencia: captura `14-emision-formato` a 1920/100 %. No se ha demostrado un cambio de escala ni error en el PDF. Formatear la presentación con precisión explícita requiere probar el round-trip y conservar el valor interno para que un cambio visual no modifique geometría o firma de calibración.
