# Worklog temporal

## 2026-05-01 - Resolver conflictos PR codex/modular-monolith-strict -> Dev

**Tarea:** Resolver conflictos de merge de `Dev` en `codex/modular-monolith-strict`.

**Archivos creados:**
- `docs/tmp/WORKLOG.md`

**Archivos modificados:**
- `config/settings.py`
- `config/urls.py`
- `conversaciones/interfaces/web/urls.py`
- `conversaciones/interfaces/web/views/public.py`
- `conversaciones/infrastructure/services/portal_bot.py`
- `docs/team/changelog.md`
- `portal_ciudadano/views.py`
- `templates/includes/base.html`
- `templates/includes/sidebar/opciones.html`
- `tramites/application/services.py`
- `tramites/interfaces/api/serializers.py`
- `tramites/interfaces/api/urls.py`
- `tramites/interfaces/api/views.py`
- `tramites/module.py`

**Cambios realizados:**
- Se resolvieron conflictos manteniendo la estructura modular canónica de la rama del PR.
- Se agregaron `portal_ciudadano` y `reclamos` como apps legacy no modularizadas para no duplicar apps ya declaradas en `config.modules`.
- Se conservaron rutas opcionales por registry modular y se agregaron solo rutas directas para apps nuevas no modularizadas.
- Se movió la API nueva de `tramites` a `tramites/interfaces/api` y los services a `tramites/application`.
- Se actualizaron imports legacy de `portal_ciudadano` y `conversaciones`.
- Se aceptó la eliminación del selector legacy `portal/selectors/ciudadano.py`.

**Decisiones o supuestos:**
- `tramites`, `chatbot`, `conversaciones` y `flujos` siguen publicando rutas mediante `module.py`.
- `portal_ciudadano` y `reclamos` se mantienen como apps directas porque llegaron desde `Dev` sin layout modular.

**Pendientes:**
- Ejecutar tests/checks solo si se pide explícitamente.
