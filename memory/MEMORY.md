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
- Se completó el quinto slice sobre `legajos`, enfocado en eventos críticos, reportes, exportación y cambio de responsable.
- Se corrigieron templates clínicos que todavía dependían de campos inexistentes del modelo actual.
- Se completó el sexto slice sobre `legajos`, enfocado en modularización física de views.
- `legajos/views.py` ahora funciona como fachada compatible y el código de ciudadanía/admisión y clínica vive en módulos separados.
- Se completó el séptimo slice sobre `legajos`, enfocado en terminar la modularización física de views.
- `legajos/views.py` quedó como fachada pura y la operativa institucional/actividades vive en `legajos/views_operativa.py`.
- Se completó el octavo slice sobre `conversaciones`, enfocado en modularización del chat.
- `conversaciones/views.py` quedó como fachada compatible y el módulo ahora usa `views_public.py`, `views_backoffice.py`, `selectors_conversaciones.py`, `services_chat.py` y `forms_chat.py`.
- Se completó el noveno slice sobre `conversaciones`, enfocado en la API auxiliar.
- `conversaciones/api_views.py` y `api_extra.py` ya reutilizan selectors/services en lugar de repetir lógica inline.
- Se completó el décimo slice sobre `configuracion`, enfocado en modularización física.
- `configuracion/views.py` quedó como fachada compatible y la app ahora reparte geografía, institucional y actividades en módulos separados.
- Se completó el undécimo slice sobre namespaces.
- `users`, `core` y `healthcheck` ya tienen `app_name` y `config/urls.py` expone includes namespaced en paralelo a los legacy.
- Se completó el duodécimo slice sobre migración inicial de consumidores.
- Templates internos ya usan `core:*` y `users:*` en varios puntos no ambiguos; autenticación quedó pendiente aparte.
- Se completó el decimotercer slice sobre `chatbot`.
- `chatbot/views.py` quedó como fachada compatible y el módulo ahora usa forms/selectors/services y vistas separadas para superficie pública y admin.
- Se completó el decimocuarto slice sobre `chatbot`.
- El módulo ya alinea rutas/rendered URLs, shape JSON del chat y CSRF en sus endpoints principales.
- Se completó el decimoquinto slice sobre `conversaciones`.
- El chat ciudadano y el detalle de operador ya consumen URLs renderizadas por Django, la evaluación volvió a la superficie pública real y los POST JSON principales del módulo ya no usan `@csrf_exempt`.
- Se completó el decimosexto slice sobre `conversaciones`.
- La lista en vivo ya no carga dos veces `conversaciones_lista_ws.js`, el runtime WebSocket es idempotente y toma URLs operativas desde el DOM renderizado.

## Próxima etapa sugerida

- El siguiente hotspot real pasó a ser cerrar la migración de consumidores sensibles (`login/logout`) y la deuda residual de tiempo real en `conversaciones`, especialmente el polling del chat ciudadano y la convergencia con WebSockets.
- En paralelo, sigue pendiente definir una política única de responsables de legajo y evaluar si conviene separar `legajos` por apps en una etapa posterior.
