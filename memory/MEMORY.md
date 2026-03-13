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
- Se completó el decimoséptimo slice sobre `conversaciones`.
- Los scripts globales y consumidores cross-app del dominio ya usan configuración renderizada por Django en lugar de rutas hardcodeadas.
- Se completó el decimoctavo slice sobre `portal`.
- Las consultas ciudadanas ahora viven en `views_ciudadano_consultas.py`, `selectors_ciudadano.py` y `services_consultas.py`, con forms explícitos para nueva consulta y envío de mensaje.
- Se completó el decimonoveno slice sobre `portal`.
- Los turnos ciudadanos ahora viven en `views_ciudadano_turnos.py`, `selectors_turnos_ciudadano.py` y `services_turnos_ciudadano.py`, con form explícito para confirmar el turno.
- Se completó el vigésimo slice sobre `portal`.
- La autenticación y el registro ciudadano ahora viven en `views_ciudadano_auth.py` y `services_ciudadano_auth.py`, con tests de flujo de alta y vinculación.
- Se completó el vigésimo primer slice sobre `portal`.
- Perfil, programas y mis datos ahora viven en `views_ciudadano_perfil.py`, `selectors_ciudadano_perfil.py` y `services_ciudadano_perfil.py`.
- Se completó el vigésimo segundo slice sobre `ÑACHEC`.
- Prestaciones, cierre/reapertura y dashboard ya viven en módulos propios y `views_nachec.py` quedó parcialmente como fachada compatible.
- Se completó el vigésimo tercer slice sobre `ÑACHEC`.
- Evaluación profesional y activación de plan ahora viven en `views_nachec_decisiones.py`.
- Se completó el vigésimo cuarto slice sobre `ÑACHEC`.
- La operación territorial restante ahora vive en `views_nachec_operacion.py` y `views_nachec.py` quedó como fachada pura.
- Se completó el vigésimo quinto slice sobre `legajos`.
- `legajos/forms.py` quedó como fachada y el módulo ahora separa ciudadanía, clínica y operativa en archivos distintos.
- Se completó el vigésimo sexto slice sobre `turnos`.
- El backoffice ahora se reparte en módulos dedicados, con mixins de permisos reutilizables y CBVs para el CRUD repetible.
- Se completó el vigésimo séptimo slice sobre `contactos`.
- El módulo legacy ahora usa selectors para lectura compuesta, un service de adjuntos y una fachada compatible para no romper URLs/imports.
- Se completó el vigésimo octavo slice sobre consumers transversales de rutas.
- `users:logout`, `chatbot:send_message` y `conversaciones:detalle` ya están consumidos desde namespaces/config renderizada en los puntos más visibles.
- Se completó el vigésimo noveno slice sobre `legajos/urls.py`.
- El conflicto nominal de `cerrar_alerta` quedó resuelto con names explícitos por dominio.
- Se completó el trigésimo slice sobre `users`.
- El service del listado de usuarios ya expone reverses y `url_name` namespaced.

## Próxima etapa sugerida

- El siguiente hotspot real pasó a ser el bloque territorial restante de `ÑACHEC`: validación, asignación, relevamiento y evidencias.
- El siguiente hotspot real pasó a ser decidir entre profundizar `ÑACHEC` con services/selectors propios o atacar la deuda transversal restante de auth namespaces y `turnos` legacy.
- El siguiente hotspot real pasó a ser `turnos/views_backoffice.py` o `legajos/views_simple_contactos.py`, porque ya no queda retorno alto inmediato en seguir partiendo `ÑACHEC`.
- El siguiente hotspot real pasó a ser `legajos/views_simple_contactos.py` o la deuda transversal remanente de namespaces/auth.
- El siguiente hotspot real pasó a ser la deuda transversal remanente de namespaces/auth y algunos hardcodes legacy de rutas, porque los grandes monolitos internos ya bajaron mucho.
- El siguiente hotspot real pasó a ser la limpieza de `legajos/urls.py`, pero ahí ya hay riesgo alto por names duplicados y consumidores legacy sin cobertura suficiente.
- El siguiente hotspot real ya no es tan claro: queda sobre todo deuda de reordenamiento profundo de `legajos/urls.py` y algunos consumidores legacy con cobertura insuficiente.
- El siguiente hotspot real ya entra en rendimientos decrecientes: quedan aliases legacy y reordenamientos más profundos de URLs que exigen mejor cobertura funcional para no romper contrato.
- En paralelo, sigue pendiente definir una política única de responsables de legajo y evaluar si conviene separar `legajos` por apps en una etapa posterior.
