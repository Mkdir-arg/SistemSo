# Decisiones Técnicas

> Registro corto de decisiones arquitectónicas relevantes.

## 2026-03-13 — Refactor DX incremental por slices

- Contexto: el repo real `SistemSo` no coincide con el contexto viejo de `AkunCalcu` y además concentra deuda en views/forms/urls monolíticos.
- Decisión: aplicar modernización interna por slices, empezando por `users`, `portal` institucional y `turnos`.
- Regla derivada: en apps existentes se prefieren módulos por dominio (`views_public.py`, `services_turnos.py`, `selectors_usuarios.py`) antes que convertir masivamente `views.py/forms.py/urls.py` en paquetes.
- Consecuencia: el patrón queda validado en un área acotada antes de entrar en `configuracion`, `legajos` y `conversaciones`.

## 2026-03-13 — `configuracion` primero por workflows institucionales

- Contexto: `configuracion` concentra deuda real en las pantallas operativas de instituciones y actividades, no en el CRUD geográfico.
- Decisión: el slice 2 se aplicó solo sobre detalle institucional, actividad, staff, derivaciones e inscriptos, con selectors + services + forms explícitos.
- Regla derivada: cuando una app mezcla tablas maestras simples y workflows complejos, el refactor debe empezar por los workflows que concentran side effects y queries repetidas.
- Consecuencia: se reduce riesgo de regresión y queda una base reusable antes de entrar en `legajos`.
