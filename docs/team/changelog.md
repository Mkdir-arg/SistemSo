# Changelog — SistemSo

> Registro cronológico de todos los cambios implementados por el equipo.

## Formato de entrada

```
### [FECHA] Título del cambio
**Sprint**: Sprint N
**User Story**: Como [usuario]...
**Archivos modificados**: lista de archivos
**Descripción**: qué se hizo y por qué.
```

---

## 2026-03-13 — Refactor DX slice 14: `chatbot` contrato frontend/backend y CSRF

**User Story:** Como equipo de desarrollo quiero alinear el contrato entre frontend y backend del módulo `chatbot` y retirar `@csrf_exempt` en sus endpoints principales para evitar deuda funcional y mejorar seguridad.

**Archivos modificados:**
- `chatbot/views_public.py`
- `chatbot/views_admin.py`
- `chatbot/services_chatbot.py`
- `chatbot/templates/chatbot/chat_interface.html`
- `chatbot/templates/chatbot/admin_dashboard.html`
- `chatbot/static/chatbot/js/chat.js`
- `chatbot/tests/test_chatbot_services.py`

**Descripcion:** Se implementó el slice 14 del refactor DX sobre `chatbot`, corrigiendo una inconsistencia real: el JS del chat consumía rutas y shape de respuesta distintos a los expuestos por Django. Se pasaron URLs al frontend desde templates, se alineó la respuesta de `send_message` con lo que consume el JS, se agregaron tests de contrato/CSRF y se retiró `@csrf_exempt` de los endpoints principales del módulo. El cambio mantiene la misma superficie funcional visible pero elimina una fuente concreta de rotura silenciosa.

## 2026-03-13 — Refactor DX slice 13: `chatbot` modularización y validación de payloads

**User Story:** Como equipo de desarrollo quiero separar la superficie pública y administrativa de `chatbot`, extraer lecturas reutilizables y validar payloads JSON para reducir lógica en `views.py` sin cambiar las rutas del módulo.

**Archivos creados:**
- `chatbot/forms_chatbot.py`
- `chatbot/selectors_chatbot.py`
- `chatbot/services_chatbot.py`
- `chatbot/views_public.py`
- `chatbot/views_admin.py`
- `chatbot/tests/__init__.py`
- `chatbot/tests/test_chatbot_services.py`

**Archivos modificados:**
- `chatbot/views.py`

**Descripcion:** Se implementó el slice 13 del refactor DX sobre `chatbot`. El módulo ahora separa chat público y administración, valida payloads con forms livianos, encapsula el workflow principal y las operaciones administrativas en services, y usa selectors para lecturas del dashboard y conversaciones. `views.py` quedó como fachada compatible y no hubo cambios de URLs, modelos ni templates.

## 2026-03-13 — Refactor DX slice 12: migración inicial de consumidores a namespaces

**User Story:** Como equipo de desarrollo quiero empezar a consumir namespaces explícitos en templates y pantallas internas para reducir dependencia de names legacy y preparar el retiro gradual de la compatibilidad dual.

**Archivos modificados:**
- `core/templates/core/relevamientos.html`
- `core/templates/core/relevamiento_detail.html`
- `core/templates/relevamientos.html`
- `core/templates/relevamiento_detail.html`
- `users/templates/user/user_list.html`
- `users/templates/user/user_form.html`
- `users/templates/user/user_confirm_delete.html`
- `templates/includes/sidebar/opciones.html`
- `templates/includes/header.html`
- `templates/403.html`
- `templates/500.html`
- `templates/relevamientos.html`
- `templates/relevamiento_detail.html`

**Descripcion:** Se implementó el slice 12 del refactor DX, migrando consumidores claros y no ambiguos desde names legacy a `core:*` y `users:*`. Se dejaron fuera `login/logout` porque todavía conviven con `django.contrib.auth.urls` y requieren una decisión más cuidadosa. El objetivo de este corte fue empezar a consumir los namespaces nuevos ya habilitados en el slice 11 sin introducir riesgo innecesario.

## 2026-03-13 — Refactor DX slice 11: namespaces compatibles en `users`, `core` y `healthcheck`

**User Story:** Como equipo de desarrollo quiero estandarizar namespaces en módulos raíz del proyecto sin romper los nombres legacy que todavía usa el código existente.

**Archivos creados:**
- `core/tests/test_url_namespaces.py`

**Archivos modificados:**
- `config/urls.py`
- `users/urls.py`
- `core/urls.py`
- `healthcheck/urls.py`

**Descripcion:** Se implementó el slice 11 del refactor DX sobre URLs. Se agregaron `app_name` faltantes en `users`, `core` y `healthcheck`, y `config/urls.py` ahora expone también includes namespaced sin quitar los includes legacy. Esto habilita usar `users:*`, `core:*` y `healthcheck:*` de forma incremental, preservando compatibilidad con los names antiguos mientras el proyecto termina de migrar.

## 2026-03-13 — Refactor DX slice 10: `configuracion` modularización física de views

**User Story:** Como equipo de desarrollo quiero separar físicamente `configuracion/views.py` por dominios para reducir fricción de navegación y edición sin cambiar URLs ni comportamiento del módulo.

**Archivos creados:**
- `configuracion/views_geografia.py`
- `configuracion/views_institucional.py`
- `configuracion/views_actividades.py`

**Archivos modificados:**
- `configuracion/views.py`

**Descripcion:** Se implementó el décimo slice del refactor DX, enfocado en modularización física de `configuracion`. El archivo monolítico se dividió en geografía, institucional y actividades, reutilizando además `TimestampedSuccessUrlMixin` donde ya existía el patrón de redirect con query timestamp. `views.py` quedó como fachada compatible y no hubo cambios de rutas, modelos ni templates.

## 2026-03-13 — Refactor DX slice 9: `conversaciones` API auxiliar alineada

**User Story:** Como equipo de desarrollo quiero alinear las APIs auxiliares de `conversaciones` con el patrón de selectors y services para que el módulo no mantenga dos estilos arquitectónicos distintos.

**Archivos modificados:**
- `conversaciones/api_views.py`
- `conversaciones/api_extra.py`
- `conversaciones/selectors_conversaciones.py`
- `conversaciones/services_chat.py`
- `conversaciones/tests/test_chat_services.py`

**Descripcion:** Se implementó el noveno slice del refactor DX, cerrando la capa API auxiliar del chat. Las alertas, previews, marcado de leídos y el detalle mínimo en vivo ahora reutilizan selectors y services ya introducidos en el slice 8, en lugar de repetir queries y permisos inline. No hubo cambios de rutas, modelos ni migraciones.

## 2026-03-13 — Refactor DX slice 8: `conversaciones` modularización y selectors

**User Story:** Como equipo de desarrollo quiero desacoplar el módulo `conversaciones` separando vistas públicas y de backoffice, extrayendo queries reutilizables y validación de payloads para reducir lógica en `views.py` sin cambiar las URLs.

**Archivos creados:**
- `conversaciones/forms_chat.py`
- `conversaciones/selectors_conversaciones.py`
- `conversaciones/services_chat.py`
- `conversaciones/views_public.py`
- `conversaciones/views_backoffice.py`
- `conversaciones/tests/__init__.py`
- `conversaciones/tests/test_chat_services.py`

**Archivos modificados:**
- `conversaciones/views.py`

**Descripcion:** Se implementó el octavo slice del refactor DX, focalizado en `conversaciones`. La bandeja, métricas y detalle pasaron a depender de selectors explícitos; la orquestación de inicio de conversación, mensajes, cierre, cola y asignación automática quedó encapsulada en `services_chat.py`; y `views.py` pasó a ser una fachada compatible que reexporta `views_public.py` y `views_backoffice.py`. Se mantuvieron las URLs y el contrato AJAX/WebSocket actual, incluyendo los `@csrf_exempt` legacy donde removerlos sería riesgoso sin tocar frontend.

## 2026-03-13 — Refactor DX slice 7: `legajos` fachada pura de views

**User Story:** Como equipo de desarrollo quiero completar la separación física de `legajos/views.py` para que el archivo quede como una fachada pura y el dominio operativo/institucional tenga su propio módulo mantenible.

**Archivos creados:**
- `legajos/views_operativa.py`

**Archivos modificados:**
- `legajos/views.py`

**Descripcion:** Se implementó el séptimo slice del refactor DX sobre `legajos`, completando la modularización física del módulo de views. El bloque operativo e institucional se movió a `views_operativa.py` y `views.py` quedó como fachada de reexportación compatible para ciudadanía/admisión, clínica, contactos y operativa. No hubo cambios funcionales, de modelos, URLs ni migraciones; el objetivo fue reducir el tamaño cognitivo del módulo y dejar una base más predecible para seguir refactorizando.

## 2026-03-13 — Refactor DX Slice 3: legajos ciudadanos y admisión

**User Story:** Como equipo de desarrollo quiero refactorizar el flujo de ciudadanos y admisión en `legajos` para reducir lógica en views, ordenar el manejo de sesión y dejar una base más mantenible para el resto del módulo.

**Archivos creados:**
- `legajos/selectors_ciudadanos.py`
- `legajos/services_ciudadanos.py`
- `legajos/services_admision.py`
- `legajos/tests/__init__.py`
- `legajos/tests/test_ciudadanos_admision.py`

**Archivos modificados:**
- `legajos/forms.py`
- `legajos/views.py`
- `legajos/urls.py`
- `legajos/templates/legajos/ciudadano_renaper_form.html`

**Descripcion:** Se ejecutó el tercer slice del refactor DX sobre `legajos`, acotado a ciudadanos y admisión. Se extrajeron selectors para lista/detalle y métricas, services para RENAPER y para el wizard de admisión con manejo de sesión, se limpiaron formularios por contexto y se corrigió la duplicación real de rutas en `legajos/urls.py`. No hubo cambios de modelo ni migraciones.

## 2026-03-13 — Refactor DX Slice 2: configuracion institucional y actividades

**User Story:** Como equipo de desarrollo quiero seguir estandarizando la capa de configuración institucional con services, selectors y forms explícitos para reducir acoplamiento en views y poder evolucionar el módulo sin romper workflows operativos.

**Archivos creados:**
- `configuracion/selectors_instituciones.py`
- `configuracion/services_actividades.py`
- `configuracion/tests/__init__.py`
- `configuracion/tests/test_services_actividades.py`

**Archivos modificados:**
- `configuracion/forms.py`
- `configuracion/views.py`
- `configuracion/views_extra.py`
- `configuracion/templates/configuracion/inscripto_form.html`
- `configuracion/templates/configuracion/staff_editar_form.html`
- `configuracion/templates/configuracion/actividad_editar_form.html`

**Descripcion:** Se ejecutó el segundo slice del refactor DX sobre `configuracion`, focalizado en instituciones y actividades. Las queries de detalle institucional y de actividad se extrajeron a selectors, los workflows de staff/derivaciones/inscriptos/actividad quedaron en services transaccionales y los formularios dejaron de depender de `POST` raw en los flujos principales. No hubo cambios de modelos ni migraciones.

## 2026-03-13 — Refactor DX Slice 1: users, portal institucional y turnos

**User Story:** Como equipo de desarrollo quiero estandarizar la arquitectura interna con services, selectors, forms y views más delgadas para reducir costo de cambio y mejorar testabilidad sin alterar el comportamiento funcional del sistema.

**Archivos creados:**
- `core/mixins.py`
- `core/selectors_geografia.py`
- `users/selectors_usuarios.py`
- `users/services_admin.py`
- `users/views_admin.py`
- `users/views_auth.py`
- `portal/forms_public.py`
- `portal/selectors_public.py`
- `portal/services_registro.py`
- `portal/views_public.py`
- `turnos/selectors_turnos.py`
- `turnos/services_turnos.py`
- `users/tests/test_user_admin_services.py`
- `portal/tests/test_registro_institucion.py`
- `turnos/tests/test_turno_actions.py`

**Archivos modificados:**
- `core/views.py`
- `users/forms.py`
- `users/services.py`
- `users/views.py`
- `portal/views.py`
- `portal/urls.py`
- `turnos/views_backoffice.py`

**Descripcion:** Se implementó el primer slice del refactor estructural de DX. `users` movió persistencia de grupos/profile a services; `portal` institucional pasó de FBVs con POST raw a `FormView` + services/selectors y dejó de usar `@csrf_exempt` en ese flujo; `turnos` extrajo queries de backoffice a selectors y acciones de estado a services transaccionales. No hubo cambios de modelos ni migraciones.

## 2026-03-13 — Refactor DX slice 4: `legajos` flujo clínico base

**User Story:** Como equipo de desarrollo quiero refactorizar el flujo clínico base de `legajos` para separar queries, orquestación y formularios en evaluación, planes, seguimientos, derivaciones y acciones de cierre/reapertura.

**Archivos creados:**
- `legajos/selectors_legajos.py`
- `legajos/services_legajos.py`
- `legajos/tests/test_legajo_workflow.py`

**Archivos modificados:**
- `legajos/forms.py`
- `legajos/views.py`
- `legajos/templates/legajos/plan_form.html`
- `legajos/templates/legajos/legajo_cerrar.html`
- `legajos/templates/legajos/legajo_reabrir.html`

**Descripcion:** Se implementó el cuarto slice del refactor DX sobre `legajos`, acotado al legajo de atención. Las queries de listados y detalle pasaron a selectors; la orquestación de evaluación, planes, seguimientos, derivaciones y cierre/reapertura pasó a services; los forms dejaron de persistir JSON dinámico en `save()` y el template del plan dejó de ignorar los valores existentes al editar. No hubo cambios de modelos ni migraciones.

## 2026-03-13 — Refactor DX slice 5: `legajos` eventos, reportes y responsable

**User Story:** Como equipo de desarrollo quiero cerrar el hotspot restante del legajo clínico para ordenar eventos críticos, reportes, exportación y cambio de responsable sin depender de views y templates fuera de contrato con los modelos.

**Archivos modificados:**
- `legajos/forms.py`
- `legajos/selectors_legajos.py`
- `legajos/services_legajos.py`
- `legajos/views.py`
- `legajos/templates/legajos/evento_form.html`
- `legajos/templates/legajos/evento_list.html`
- `legajos/templates/legajos/evaluacion_list.html`
- `legajos/templates/legajos/plan_list.html`
- `legajos/templates/legajos/reportes.html`
- `legajos/templates/legajos/dispositivo_derivaciones.html`
- `legajos/tests/test_legajo_workflow.py`

**Descripcion:** Se implementó el quinto slice del refactor DX sobre `legajos`, enfocado en eventos críticos, reportes, exportación CSV, derivaciones por dispositivo y cambio de responsable. Se extrajeron selectors/services para estos flujos, `EventoCriticoForm` dejó de persistir side effects en `save()`, y se corrigieron templates que referenciaban campos inexistentes del modelo (`descripcion`, `gravedad`, `motivo_consulta`, `diagnostico`, `activo`, `origen`). No hubo cambios de modelo ni migraciones.

## 2026-03-13 — Refactor DX slice 6: `legajos` separación física de views por dominio

**User Story:** Como equipo de desarrollo quiero separar físicamente `legajos/views.py` por dominios para reducir el costo de navegación y edición sin tocar las URLs ni romper imports existentes.

**Archivos creados:**
- `legajos/views_ciudadanos.py`
- `legajos/views_clinico.py`

**Archivos modificados:**
- `legajos/views.py`

**Descripcion:** Se implementó el sexto slice del refactor DX sobre `legajos`, enfocado en modularización física. `views.py` quedó como fachada compatible y el contenido se repartió en `views_ciudadanos.py` y `views_clinico.py`. No hubo cambios funcionales deliberados, de modelos ni de rutas; el objetivo fue bajar el tamaño del archivo monolítico y dejar una base más predecible para seguir refactorizando el módulo.

## 2026-03-05 — Mejora de logging detallado

**User Story:** Como desarrollador, quiero logs detallados en tiempo real del backend, requests HTTP y nginx para diagnosticar problemas en producción.

**Archivos creados:**
- `core/middleware.py` — `RequestLoggingMiddleware`

**Archivos modificados:**
- `config/settings.py` — `console` handler en LOGGING, `django.request` a WARNING, middleware registrado
- `nginx.conf` — `log_format detailed` con `$request_time` y `$upstream_response_time`

**Descripcion:** Tres mejoras de observabilidad: (A) console handler para ver logs con `docker logs nodo-web`; (B) middleware que loguea cada request con método, URL, usuario, IP, status y duración; (D) formato de access log en nginx con tiempos de respuesta totales y de upstream.

---

## 2026-03-05 — [HOTFIX] Redis OOM causa WSDISCONNECT en WebSocket

**Archivos modificados:**
- `docker-compose.prod.yml` — Redis mem_limit 200m→400m, agregado maxmemory 350mb + allkeys-lru

**Descripcion:** WebSockets de alertas y conversaciones conectaban y desconectaban en 1-2 segundos. Causa: Redis sin `maxmemory-policy` se quedaba sin memoria y fallaba `channel_layer.group_add()`. Fix: aumentar limite y configurar eviccion LRU.

---

## 2026-03-04 — [HOTFIX] Error 400 al confirmar ciudadano via RENAPER

**Archivos modificados:**
- `config/settings_production.py` — eliminado `CSRF_COOKIE_HTTPONLY = True`
- `config/settings.py` — eliminado `CSRF_COOKIE_HTTPONLY = True` del bloque prd

**Descripcion:** Error 400 en POST `/legajos/ciudadanos/confirmar/`. Causa: `CSRF_COOKIE_HTTPONLY = True` interferia con validacion CSRF detras del proxy nginx+HTTPS. Fix: eliminar esa flag (no aporta seguridad real segun docs de Django y rompe el flujo CSRF en proxies SSL).

---

## 2026-03-04 — Módulo de Pedidos Telegram (Bot de Voz)

**User Story:** Como vendedor de Akuna Aberturas, quiero enviar un audio de voz por Telegram con los ítems de un pedido, para que el sistema lo interprete automáticamente y lo registre como pedido en AkunCalcu.

**Archivos creados:**
- `akuna_calc/pedidos/__init__.py`
- `akuna_calc/pedidos/apps.py`
- `akuna_calc/pedidos/models.py` — modelos `PedidoTelegram` + `ItemPedidoTelegram`
- `akuna_calc/pedidos/views.py` — endpoints API + vista lista
- `akuna_calc/pedidos/urls.py`
- `akuna_calc/pedidos/migrations/0001_initial.py`
- `akuna_calc/pedidos/templates/pedidos/pedidos_list.html`
- `docs/n8n-pedidos-workflow.md` — JSON del workflow n8n listo para importar

**Archivos modificados:**
- `akuna_calc/akuna_calc/settings.py` — agregado `pedidos` a `INSTALLED_APPS`
- `akuna_calc/akuna_calc/urls.py` — agregado `path('pedidos/', ...)`
- `docker-compose.yml` — agregada variable `TELEGRAM_BOT_SECRET`

**Descripción:** Implementación completa del flujo de pedidos por voz vía Telegram. El bot transcribe el audio (Whisper), extrae ítems con GPT-4o-mini, crea un borrador en Django, pide confirmación al usuario y según la respuesta confirma o cancela el pedido. Ver en `http://localhost:8080/pedidos/`.

---

## 2026-03-04 — Documento V1 del sistema

**User Story:** Como equipo de desarrollo, quiero un documento V1 del sistema.
**Archivos creados:** `docs/V1-sistema.md`
**Descripción:** Análisis completo del sistema. Se documentaron 8 módulos, sus procesos, cálculos internos, arquitectura técnica, flujos de trabajo, integraciones y glosario del negocio.

---

## 2026-03-04 — Setup del equipo de agentes

**Descripción**: Se configuró la estructura del equipo de desarrollo con metodología Scrum guiado.
- Creado `CLAUDE.md` con roles, workflow y convenciones
- Creado `docs/team/` con backlog, sprint, decisions, changelog
- Creados comandos personalizados en `.claude/commands/`
- Inicializada memoria del proyecto en `memory/MEMORY.md`

---

## 2026-03-13 — Refactor DX Slice 15: `conversaciones` contrato real y CSRF

**Archivos modificados:**
- `conversaciones/views_public.py`
- `conversaciones/views_backoffice.py`
- `conversaciones/views.py`
- `conversaciones/templates/conversaciones/chat_ciudadano.html`
- `conversaciones/templates/conversaciones/detalle.html`
- `conversaciones/templates/conversaciones/lista.html`
- `conversaciones/tests/test_chat_services.py`

**Descripción:** Se corrigió una inconsistencia funcional real en `conversaciones`: el chat ciudadano evaluaba contra una URL resuelta por backoffice y los fetches JSON dependían de rutas hardcodeadas sin cabecera CSRF. El slice alinea el contrato renderizado entre templates y URLs namespaced, protege los POST JSON con CSRF y agrega tests de contrato para conversación pública y respuesta de operador.

---

## 2026-03-13 — Refactor DX Slice 16: `conversaciones` runtime de lista en vivo

**Archivos modificados:**
- `conversaciones/templates/conversaciones/lista.html`
- `static/custom/js/conversaciones_lista_ws.js`
- `conversaciones/tests/test_chat_services.py`

**Descripción:** Se eliminó la doble carga de `conversaciones_lista_ws.js` en la pantalla de lista y se movió el contrato de URLs/runtime a atributos renderizados por Django. El WebSocket de lista ahora evita inicialización duplicada, usa URLs configurables para detalle/cierre/API y queda mejor preparado para la migración de namespaces.

---

## 2026-03-13 — Refactor DX Slice 17: `conversaciones` residual cross-app

**Archivos modificados:**
- `templates/includes/base.html`
- `static/custom/js/conversaciones_tiempo_real_global.js`
- `static/custom/js/conversaciones_tiempo_real.js`
- `static/custom/js/alertas_conversaciones_fallback.js`
- `static/custom/js/alertas_conversaciones_simple.js`
- `conversaciones/templates/conversaciones/detalle.html`
- `portal/templates/portal/ciudadano/consulta_detalle.html`
- `conversaciones/tests/test_chat_services.py`

**Descripción:** Se alinearon consumidores residuales de `conversaciones` fuera de la lista principal. Los scripts globales ahora toman URLs desde una configuración renderizada por Django, el detalle de operador deja de hardcodear el path WebSocket y el portal ciudadano deja de construir manualmente la URL de mensajes. El objetivo fue cerrar la deuda cross-app del módulo antes de pasar al siguiente hotspot.

---

## 2026-03-13 — Refactor DX Slice 18: `portal` consultas ciudadanas

**Archivos modificados:**
- `portal/forms.py`
- `portal/views_ciudadano.py`
- `portal/templates/portal/ciudadano/nueva_consulta.html`
- `portal/selectors_ciudadano.py`
- `portal/services_consultas.py`
- `portal/views_ciudadano_consultas.py`
- `portal/tests/test_ciudadano_consultas.py`

**Descripción:** Se extrajo el subdominio de consultas ciudadanas de `portal/views_ciudadano.py` hacia selectors, services y vistas dedicadas. El flujo de nueva consulta y envío de mensaje deja de depender de `POST` raw y pasa a forms explícitos. También se agregan tests para ownership, validación y creación de conversación/mensaje.

---

## 2026-03-13 — Refactor DX Slice 19: `portal` turnos ciudadano

**Archivos modificados:**
- `portal/forms.py`
- `portal/views_ciudadano.py`
- `portal/templates/portal/ciudadano/turno_confirmar.html`
- `portal/selectors_turnos_ciudadano.py`
- `portal/services_turnos_ciudadano.py`
- `portal/views_ciudadano_turnos.py`
- `portal/tests/test_ciudadano_turnos.py`

**Descripción:** Se extrajo el subdominio de turnos del portal ciudadano desde `portal/views_ciudadano.py` hacia selectors, services y vistas dedicadas. La confirmación del turno deja de procesar `POST` raw y pasa a un form explícito con validación de fecha y normalización del motivo. También se encapsuló la reserva/cancelación en services reutilizables y se agregaron tests del flujo ciudadano de turnos.
