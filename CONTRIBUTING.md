# Desarrollo oficial

La fuente oficial de este proyecto es el repositorio privado FMAcovex/covex-label-manager. No crear copias públicas ni otros repositorios de desarrollo.

Todas las revisiones posteriores se desarrollan en ramas `fix/...`, `feature/...` o `chore/...` y se incorporan mediante pull request. No escribir directamente en main, no force push y no eliminar referencias de versiones. Cada PR incluye problema, cambio y comprobaciones, además de actualización de ROADMAP/arquitectura cuando proceda.

Antes de integrar: ejecutar `python -m pytest -q`, revisar el control de contenido y exigir el job Windows de Actions. Configurar protección/ruleset de main con PR obligatorio, sin borrado/force push, y el check Windows; si GitHub no permite hacerlo por el plan/permisos, documentar la limitación y mantener el procedimiento de PR igualmente. No afirmar que la protección remota está activa hasta verificarla.

No subir maestros, etiquetas reales, catálogos, emisiones, bases de usuario, credenciales ni capturas que reproduzcan documentos reales. El control automático rechaza formatos documentales/binarios y patrones habituales, pero no garantiza ausencia de información sensible en texto: revisar el diff. Pruebas generan fixtures SYNTHETIC; artefactos de CI no incluyen datos reales. Nuevos recursos autorizados requieren revisión específica antes de ampliar el control.

Un merge, tag, release o build no aprueba una plantilla. 00-R1 permanece pendiente de aprobación documental en los datos locales. Windows, Word e impresión requieren pruebas reales. No iniciar R3 antes de autorización de implementación y validación del diseño.

## Protección de rama

El 08/10/2026 GitHub indicó que las reglas de protección no se aplican a este repositorio privado con el plan actual. Main no está protegida técnicamente. Todas las incorporaciones deben continuar por ramas y PR con el job Windows satisfactorio; el propietario deberá valorar un plan compatible si necesita impedir técnicamente commits directos. No se ha contratado ni cambiado ningún plan.
