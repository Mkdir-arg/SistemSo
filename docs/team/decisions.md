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

## 2026-03-13 — los templates deben reflejar el modelo real

- Contexto: varias pantallas de `legajos` venían renderizando campos inexistentes o nombres legacy que ya no pertenecen al schema actual.
- Decisión: el slice 5 corrigió esos templates y movió los hotspots de eventos/reportes/responsable a selectors y services para que el frontend dependa de contratos reales del dominio.
- Regla derivada: cuando un template y un modelo divergen, la prioridad es realinear el template al modelo antes de agregar más lógica de presentación.
- Consecuencia: se reduce deuda silenciosa y baja el riesgo de romper pantallas por atributos fantasma.

## 2026-03-13 — modularizar `views.py` sin romper compatibilidad

- Contexto: `legajos/views.py` seguía siendo el archivo más monolítico del proyecto aun después de extraer services y selectors.
- Decisión: el slice 6 separó ciudadanía/admisión y clínica en `views_ciudadanos.py` y `views_clinico.py`, dejando `views.py` como fachada compatible.
- Regla derivada: cuando la deuda es física/organizacional, primero conviene introducir fachadas compatibles antes de forzar cambios de imports/URLs en cascada.
- Consecuencia: se reduce el tamaño cognitivo del módulo y queda allanado el próximo paso de separar institucional/programas/actividades.

## 2026-03-13 — completar la fachada de `legajos/views.py`

- Contexto: después del slice 6, `legajos/views.py` todavía mezclaba fachada e implementación real del bloque institucional/operativo.
- Decisión: el slice 7 movió ese bloque a `views_operativa.py` y dejó `views.py` como un punto de reexportación sin lógica propia.
- Regla derivada: si una fachada temporal todavía conserva implementación, el siguiente corte debe convertirla en fachada real antes de abrir más submódulos.
- Consecuencia: el contrato de imports se mantiene estable, pero la app ya puede seguir modularizándose por dominios con menos fricción.

## 2026-03-13 — modularizar `conversaciones` preservando endpoints legacy

- Contexto: `conversaciones/views.py` mezclaba chat público, backoffice, métricas y lógica de cola con parsing manual de JSON y queries repetidas.
- Decisión: el slice 8 extrajo selectors, services y forms livianos, separó `views_public.py` y `views_backoffice.py` y dejó `views.py` como fachada compatible.
- Regla derivada: en módulos con transporte AJAX/WebSocket legacy, primero conviene separar responsabilidades y validar payloads sin cambiar rutas ni el contrato del frontend.
- Consecuencia: el módulo ya puede seguir evolucionando con menor riesgo y la deuda específica de CSRF/polling queda aislada para un corte posterior.

## 2026-03-13 — alinear la API auxiliar del chat con la misma capa de dominio

- Contexto: aun con `views.py` modularizado, `api_views.py` y `api_extra.py` seguían resolviendo permisos, previews y marcado de leídos con queries inline.
- Decisión: el slice 9 reusó selectors y services del módulo para alertas, detalle en vivo y marcado de mensajes leídos.
- Regla derivada: cuando una app expone HTML y APIs sobre el mismo dominio, ambas superficies deben consumir la misma capa de lectura/orquestación.
- Consecuencia: baja la duplicación interna y se reduce el riesgo de divergencia entre la UI principal y sus APIs auxiliares.

## 2026-03-13 — `configuracion` adopta fachada compatible de views por dominio

- Contexto: `configuracion` seguía con un `views.py` de más de 500 líneas aun después del slice 2.
- Decisión: el slice 10 separó geografía, institucional y actividades en módulos propios y dejó `views.py` como fachada compatible.
- Regla derivada: cuando una app ya tiene services/selectors pero conserva una view monolítica, el siguiente paso de DX es modularización física, no más abstracción lógica.
- Consecuencia: se reduce el costo de navegación del módulo y se homogeniza el patrón con `legajos` y `conversaciones`.

## 2026-03-13 — introducir namespaces sin romper el código legado

- Contexto: `users`, `core` y `healthcheck` seguían sin `app_name` y eso hacía menos predecible el espacio de rutas del proyecto.
- Decisión: el slice 11 agregó `app_name` y expuso includes namespaced en paralelo a los legacy.
- Regla derivada: cuando un rename global de URLs es riesgoso, primero conviene habilitar compatibilidad dual y migrar el consumo de forma incremental.
- Consecuencia: ya se pueden usar namespaces consistentes en código nuevo sin obligar a una migración agresiva del código existente.

## 2026-03-13 — migrar primero consumidores de names no ambiguos

- Contexto: una vez habilitados los namespaces, todavía había mucho consumo legacy en templates.
- Decisión: el slice 12 migró primero `core:*` y `users:*` en pantallas donde el name no colisiona con `django.contrib.auth.urls`.
- Regla derivada: en migraciones de URLs, empezar por consumidores no ambiguos y dejar autenticación para un corte específico.
- Consecuencia: avanza la estandarización real sin introducir una regresión oculta en login/logout.

## 2026-03-13 — dividir `chatbot` por superficie funcional

- Contexto: `chatbot/views.py` seguía mezclando chat del usuario, panel admin y parsing manual de payloads.
- Decisión: el slice 13 separó vistas públicas y administrativas y movió lectura/orquestación a selectors/services con forms livianos para JSON.
- Regla derivada: cuando una app combina superficie de usuario y de administración, separar primero por superficie antes de rediseñar endpoints.
- Consecuencia: la app queda consistente con el patrón del refactor DX y con mejor base para hardening posterior.

## 2026-03-13 — endurecer `chatbot` después de alinear contrato real con frontend

- Contexto: tras la modularización apareció una inconsistencia funcional entre `chat.js` y `chatbot/urls.py`/`views_public.py`.
- Decisión: el slice 14 corrigió primero el contrato real de rutas y respuesta JSON y, sobre esa base, quitó `@csrf_exempt` en los endpoints principales del módulo.
- Regla derivada: no endurecer seguridad sobre una integración rota; primero alinear contrato, después activar la protección.
- Consecuencia: `chatbot` queda funcionalmente más coherente y con mejor postura de seguridad sin tocar su UX.

## 2026-03-13 — endurecer `conversaciones` solo después de corregir su contrato público

- Contexto: el chat ciudadano usaba rutas hardcodeadas, no enviaba cabecera CSRF y evaluaba contra una URL que en realidad estaba protegida como backoffice.
- Decisión: el slice 15 corrigió primero el contrato real renderizando URLs desde Django y devolviendo la evaluación al dominio público; después retiró `@csrf_exempt` de los POST JSON principales.
- Regla derivada: en integraciones AJAX legacy, primero se corrige el contrato observable por el frontend y recién después se endurecen controles de seguridad.
- Consecuencia: `conversaciones` conserva la UX actual, pero elimina una incoherencia funcional real y mejora su postura CSRF.

## 2026-03-13 — los runtimes en vivo deben ser idempotentes y configurables

- Contexto: `conversaciones_lista_ws.js` se cargaba tanto desde `base.html` como desde `lista.html`, y además seguía dependiendo de URLs hardcodeadas para detalle, cierre y API.
- Decisión: el slice 16 eliminó la carga duplicada local, agregó un guard de inicialización global y movió las URLs operativas al DOM renderizado por Django.
- Regla derivada: si un runtime JS se inyecta globalmente desde `base.html`, debe tolerar inclusiones repetidas y tomar configuración específica de pantalla desde atributos de datos o un objeto global.
- Consecuencia: la lista en vivo de conversaciones queda más estable y más preparada para cambios futuros de rutas/namespaces.

## 2026-03-13 — la configuración de dominio compartido debe salir de archivos estáticos

- Contexto: tras los slices 15 y 16 todavía quedaban scripts globales y consumidores cross-app de `conversaciones` pegados a `/conversaciones/...`, incluso fuera de la app misma.
- Decisión: el slice 17 introdujo `window.conversacionesConfig` en `base.html` y movió a esa configuración los scripts globales de estadísticas/alertas, además de parametrizar el detalle operador y el portal ciudadano.
- Regla derivada: cuando un dominio cruza varias pantallas y apps, la fuente de verdad de sus rutas debe renderizarse desde Django y no replicarse en múltiples archivos estáticos.
- Consecuencia: baja el acoplamiento transversal del módulo y se simplifica la futura migración de namespaces/rutas.
