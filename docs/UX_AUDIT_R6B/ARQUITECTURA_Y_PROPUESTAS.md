# Arquitectura de navegación y propuestas de rediseño

Todas las propuestas de este documento son para revisión. No hay implementación, eliminación de capacidades, cambios de SQLite ni autorización de uso productivo. Se conserva la dirección visual Industrial Moderno ya documentada; la revisión decide distribución y jerarquía.

## Alternativa A · Evolución de la estructura actual (recomendada)

Mantener los cinco destinos reconocibles y consolidar controles dentro de cada uno. Es la opción de menor cambio de aprendizaje y permite intervenir por PR pequeñas con trazabilidad de las 87 IDs.

```text
COVEX   Biblioteca   Editor   Emisión   Historial   Configuración
        documento   diseño   trabajo   registro     administración

Biblioteca
 ├─ buscar / filtros / favoritas / recientes
 ├─ tabla + inspector documental
 ├─ Documento: ficha, fuentes, metadatos, revisiones, variantes, aprobación
 └─ Intercambio: importar, inventariar, exportar, conciliar

Editor
 ├─ identidad: revisión + variante + estado
 ├─ lienzo + elementos + propiedades
 ├─ herramientas avanzadas agrupadas
 └─ datos del trabajo: pestaña contextual del panel derecho, sin dock global

Emisión
 ├─ selector de trabajo + nuevo/copiar/recuperar
 ├─ lote / recipientes / formato / estado
 ├─ comprobación y PDF real
 └─ pie: estado de guardado / prueba / emitir / imprimir registrado

Historial
 ├─ filtros + registros
 ├─ detalle + PDF registrado verificado
 └─ reimpresión con motivo y vínculo; impresión con control existente

Configuración
 ├─ General y datos: operador, ruta, copias, procedimiento de restauración
 ├─ Catálogos y documentos: CM, duplicados, maestros de estado
 ├─ Impresión: perfiles/calibración, con acceso contextual desde Emisión
 ├─ Auditoría y aceptación: registro, diagnóstico, sesiones
 └─ Compatibilidad: entradas Tk explícitas mientras sigan autorizadas
```

El árbol es una organización propuesta: «Impresión» centraliza explicación y perfiles, pero Emisión conserva sus accesos de tarea y se reutilizan los servicios actuales. No se introduce un nuevo motor ni un registro alternativo.

## Alternativa B · Navegación por tarea y detalle documental

Biblioteca y detalle documental se vuelven un espacio único con pestañas Ficha, Revisiones/variantes, Diseño y Fuentes. Emisión, Historial y Administración quedan como destinos separados. Editor sigue accesible mediante URL interna/comando y acceso directo; ninguna herramienta se elimina.

| Criterio | A: cinco destinos actuales | B: espacio documental integrado |
|---|---|---|
| Aprendizaje | Conserva nombres y rutas principales | Cambia el modelo de acceso al diseño |
| Cambios de contexto | Mejora sin reestructurar todo el stack | Reduce el salto Biblioteca→Editor y centraliza identidad |
| Riesgo técnico | Moderado: consolidación de barras y contrato de navegación | Mayor: composición, retención de trabajo y foco |
| Ejecución por fases | Buena; casi todas las mejoras son independientes | Requiere una fase de prototipo/navegación más amplia |
| Recomendación | Ejecutar primero tras aprobación | Evaluar con operadores antes de sustituir A |

## Menús y acciones propuestos

| Lugar | Presentación propuesta | Contrato que se conserva |
|---|---|---|
| Biblioteca | «Documento ▾»: Ficha, PDF maestro, Original, Metadatos, Nueva revisión, Revisiones/variantes, Registrar aprobación | Mismos servicios y guardas; separar consulta de cambio de estado. |
| Biblioteca | «Intercambio ▾»: Importar documento, Importar carpeta controlada, Inventariar carpeta, Conciliar máster, Exportar catálogo | No confundir exportación con backup; mantener confirmación de contenido confidencial. |
| Inspector | Una sola entrada de aprobación documental, identificando revisión; acción principal Abrir diseño o Preparar trabajo según tarea | Estado independiente de variante, revisión y material; no aprobar por abrir. |
| Editor | Una barra: Guardar diseño, Deshacer/Rehacer, zoom, Paneles; herramientas contextuales junto a selección | Guardado explícito y fuente fija protegida; sin autoguardar diseño. |
| Editor | Elementos incluye Nuevo/Dibujar/Eliminar; Avanzadas conserva Recorte, Anclar, Relocalizar, Escala, Zona de estado, Auxiliares, Prueba | No quitar operaciones aunque se consoliden entradas duplicadas. |
| Emisión | «Actualizar comprobación» genera preview; «Exportar PDF de prueba» guarda archivo; «Registrar emisión definitiva» confirma el registro | Prueba marcada sin issue; emisión transaccional, hash/token y snapshot. |
| Emisión | «Generar hoja patrón de calibración» y «Aplicar medidas de calibración…» | La primera no implica la segunda; preservar firma geométrica y límites. |
| Historial | Consultar detalle/PDF; Reimprimir con motivo; Enviar PDF registrado a impresora | Revalidación, números originales, motivo y vínculo; no confirmar papel automáticamente. |
| General | «Compatibilidad Tkinter…» dentro de grupo claramente secundario | Conservación técnica hasta aceptación y decisión explícita de retirada. |

## Distribución visual por pantalla

### Biblioteca

Una cabecera compacta con búsqueda, filtros esenciales y menú Intercambio. Segunda fila con vistas Todas/Favoritas/Recientes y resumen de filtros. Tabla ocupa el área restante; el Inspector conserva identidad y estado arriba, preview y detalles debajo. Acciones frecuentes ancladas al pie del Inspector. Filtros avanzados se abren en panel superpuesto o región colapsable, con chip/resumen visible; no desaparecen ni se reinician automáticamente sin feedback.

En compacto, la selección abre una ficha lateral o subvista con «Volver a resultados». La tabla conserva código/denominación/revisión/estado; los demás datos continúan en ficha y menú Columnas. El número de acciones para abrir diseño/preparar trabajo no debe aumentar.

### Editor

```text
Identidad documental · revisión · variante · estado      Guardar diseño
Deshacer / Rehacer | Ajustar / − / + | Paneles | Herramientas
┌ Elementos ─────┬──────────── Lienzo ────────────┬ Propiedades ──────┐
│ Buscar campo  │                               │ Campo / Trabajo  │
│ Nuevo/Dibujar │       PDF fijo protegido      │ Identificación   │
│ Lista campos  │       campos superpuestos     │ Posición y texto │
│ Bloqueo       │                               │ Avanzadas        │
└───────────────┴───────────────────────────────┴───────────────────┘
Diseño guardado / cambios pendientes · trabajo autoguardado por separado
```

En pantalla estrecha, Elementos y Propiedades se alternan en un único panel contextual rotulado, manteniendo selección y una forma clara de volver. Evitar que el dock de trabajo replique un segundo conjunto completo de mandos. El diseño nunca depende del zoom de vista para su escala física.

Objetivo de prototipo: al menos 50 % del alto cliente disponible para lienzo en el estado de edición normal, o una vista de lienzo ampliada accesible con un control visible. Es un objetivo a validar con texto real/fuentes autorizadas, no una promesa ya medida. No imponer un tamaño de ventana mayor que el monitor para cumplirlo.

### Emisión

Selector de trabajo y resumen de identidad en una sola cabecera; datos a la izquierda y PDF a la derecha en ancho suficiente. Modo compacto con dos vistas rotuladas, «Datos y comprobaciones» / «PDF», pero un mismo pie de estado. Avisos agrupados por error, acceso al campo y marca Prueba/Definitivo siempre visibles. Guardado local como estado persistente; exportación de prueba y registro de emisión como acciones distintas.

El formulario distingue lote común, excepciones por recipiente, formato y etiqueta de estado. La ayuda de herencia queda junto a la tabla y no solo en tooltip. Cantidades, recipientes, copias, etiquetas físicas y hojas siguen separados.

### Historial y Configuración

Historial: maestro-detalle con resumen legible, pestañas de datos y PDF; botón de reimpresión contextual que conserve motivo y vínculo. Los perfiles o valores técnicos completos pueden plegarse, pero deben seguir accesibles y exportables conforme a las funciones existentes.

Configuración: categorías breves y claras, no cinco pestañas largas comprimidas por un dock. Operador/ruta/copias en General; catálogos/maestros separados; aceptación/auditoría con señal de NO ACEPTADO. Los formularios y confirmaciones usan scroll y pie fijo, no mínimos que excedan el área disponible.

## Sistema visual Industrial Moderno

- Mantener petróleo `#173940`, verde acción `#147D71`, superficies `#F3F6F7`/blanco y bordes discretos. Añadir tokens de texto que alcancen contraste 4,5:1 sobre su superficie para texto normal; no aclarar avisos por considerarlos secundarios.
- Escala tipográfica propuesta: cuerpo 13–14 DIP, auxiliares ≥12–13 DIP con contraste suficiente, títulos contextuales 20–24 DIP. Evitar título de 27 px más dos barras grandes en la misma pantalla pequeña.
- Ritmo de espacios 4/8/12/16/24 DIP; densidad operativa configurable solo si no rompe áreas de interacción/foco. Botones frecuentes aproximadamente 32–40 DIP de alto, con texto completo o tooltip accesible sin depender solo de este.
- Verde primario para la acción de tarea; aprobaciones/retiros con texto explícito y contexto, no «botón verde = aprobar todo». Pendiente/Vigente/Retirada siempre escritos junto al color.
- Iconos lineales consistentes, con nombre accesible de contexto: «Acercar vista del documento», no «+». Foco de teclado visible; no transmitir estado exclusivamente por color.
- Definir puntos de cambio por espacio útil, probados en las seis configuraciones. No trasladar literalmente 1366 px a un umbral DIP sin considerar el factor Qt.

La aprobación del esquema visual no autoriza cambiar la lógica documental. Cada comando reubicado deberá mapearse a su capacidad y regresión antes de retirar su acceso anterior de la distribución.
