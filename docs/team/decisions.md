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

## 2026-03-13 — `legajos` empieza por ciudadanos y admisión

- Contexto: `legajos` mezcla varios dominios y no era realista refactorizarlo completo en un solo corte.
- Decisión: el slice 3 se enfocó en la entrada principal del módulo: listado/detalle de ciudadano, consulta RENAPER y wizard de admisión.
- Regla derivada: en módulos monolíticos, atacar primero el flujo de entrada con más visibilidad y reutilización antes de tocar submódulos laterales.
- Consecuencia: el manejo de sesión y las queries repetidas ya no viven pegadas a las views del flujo base.

## 2026-03-13 — `legajos` clínico conserva compatibilidad con actividades dinámicas

- Contexto: el flujo clínico base tenía lógica de evaluación/planes/seguimientos/derivaciones inline en views y el formulario de plan no representaba correctamente los datos existentes al editar.
- Decisión: el slice 4 movió orquestación a `services_legajos.py`, lecturas a `selectors_legajos.py` y mantuvo compatibilidad con actividades dinámicas adicionales del plan parseando los slots enviados por `POST`.
- Regla derivada: cuando un form legacy convive con inputs dinámicos fuera del schema declarado, el refactor debe preservar ese contrato antes de endurecer validaciones.
- Consecuencia: se corrige una inconsistencia funcional real en edición de planes sin introducir un corte abrupto del flujo histórico.
