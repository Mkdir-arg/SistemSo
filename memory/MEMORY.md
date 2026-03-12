# MEMORY

## Identidad real del repo

- El repositorio activo es `SistemSo`, no `akuna_calc`.
- Apps principales: `core`, `legajos`, `portal`, `turnos`, `conversaciones`, `chatbot`, `configuracion`, `users`, `dashboard`, `tramites`, `healthcheck`.

## Estado relevante 2026-03-13

- Se completó el primer slice del refactor DX interno.
- Slice implementado: `users`, `portal` institucional, `turnos`, con soporte en `core`.
- Patrón validado: selectors para lectura, services para orquestación, views más delgadas, formularios sin persistencia pesada.
- Se completó también el segundo slice sobre `configuracion`, enfocado en instituciones y actividades.
- `configuracion` ahora tiene `selectors_instituciones.py`, `services_actividades.py` y forms explícitos para editar inscriptos, actividades y staff.
- Se completó el tercer slice sobre `legajos`, enfocado en ciudadanos y admisión.
- `legajos` ahora tiene `selectors_ciudadanos.py`, `services_ciudadanos.py` y `services_admision.py` para RENAPER, detalle de ciudadano y wizard de admisión.
- Se completó el cuarto slice sobre `legajos`, enfocado en flujo clínico base.
- `legajos` ahora suma `selectors_legajos.py` y `services_legajos.py` para evaluación, planes, seguimientos, derivaciones y cierre/reapertura.

## Próxima etapa sugerida

- Seguir con `legajos`, ahora sobre eventos críticos, reportes, cambio de responsable y separación física de `views.py` por dominios.
- Luego entrar en `conversaciones`, que sigue concentrando lógica de lifecycle en views.
