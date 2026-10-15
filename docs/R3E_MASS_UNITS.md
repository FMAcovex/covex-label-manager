# Ajuste R3E — Unidades kg en pesos PN/PB

**Motivo de UAT:** el operador debe poder escribir `0,3558 kg` además de `0,3558` al introducir peso neto (PN) y peso bruto (PB).

- En la pantalla nativa Qt se muestran PN/PB como entradas de una línea y ejemplos en kg. Se permite el sufijo `kg` (sin espacio, con espacio y cualquier combinación de mayúsculas/minúsculas) tanto en los valores comunes como en la tabla por recipiente y la importación desde Excel.
- La verificación cuantitativa interpreta ambos formatos **exclusivamente como kg**; PB debe seguir siendo mayor o igual a PN. No se aceptan otras unidades (`g`, `mg`) ni se realizan conversiones implícitas.
- El borrador, el snapshot y el registro conservan el texto exacto introducido por el operador. No se modifican emisiones históricas, maestros Word/PDF, SQLite v4 ni reglas de aprobación.
- Si el campo de la plantilla define el sufijo documental ` KG`, la impresión lo utiliza una sola vez aunque el operador haya tecleado `kg`, evitando resultados como `0,3558kg KG`. Si el maestro no define ese sufijo, la unidad introducida puede incluirse como texto del campo; comprobar la visualización física en el PDF de prueba para evitar que coincida con texto fijo del Word.
- La impresión sigue requiriendo una vista previa marcada de prueba, revisión de formato y validación/aceptación real por COVEX. No se altera el estado pendiente `00-R1`.
- Pruebas: aceptación/rechazo de unidades, comparación PN/PB, Excel, PDF PyMuPDF con sufijo y sin sufijo, persistencia y recarga de los controles Qt.
