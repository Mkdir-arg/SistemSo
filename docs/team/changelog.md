# Changelog — AkunCalcu

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
