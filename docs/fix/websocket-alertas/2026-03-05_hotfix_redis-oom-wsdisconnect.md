# Redis OOM causa WSDISCONNECT inmediato en WebSocket — HOTFIX

> Fecha: 2026-03-05
> Tipo: HOTFIX
> Funcionalidad afectada: `websocket-alertas`, `websocket-conversaciones`
> Severidad: ALTA

---

## Problema

Los WebSockets de `/ws/alertas/` y `/ws/conversaciones/` conectaban (WSCONNECT) pero desconectaban al cabo de 1-2 segundos (WSDISCONNECT). El cliente JS reintentaba cada 3 segundos generando un loop infinito de reconexiones, registrado como Internal Server Error en error.log.

Ademas, algunos intentos de conexion mostraban WSREJECT (codigo 4403 = usuario sin grupos requeridos) — eso es comportamiento esperado, no un bug.

## Causa raiz

Redis tenia `mem_limit: 200m` sin `maxmemory-policy` configurada. Cuando Redis se queda sin memoria, las operaciones de escritura (como `channel_layer.group_add()`) fallan silenciosamente o con error. El consumer de Channels captura la excepcion en el `try/except` de `connect()` y llama `self.close(code=1011)`, causando el WSDISCONNECT inmediato.

## Impacto

- Usuarios afectados: todos los usuarios con grupos habilitados para WebSocket
- Funcionalidad bloqueada: alertas en tiempo real y lista de conversaciones en tiempo real
- El sistema seguia funcionando (fallback a polling HTTP), pero sin notificaciones push

## Fix aplicado

| Archivo | Cambio |
|---------|--------|
| `docker-compose.prod.yml` | `mem_limit` Redis: 200m → 400m |
| `docker-compose.prod.yml` | `memswap_limit` Redis: 300m → 500m |
| `docker-compose.prod.yml` | Agregado `--maxmemory 350mb --maxmemory-policy allkeys-lru` al comando de Redis |

El `maxmemory-policy allkeys-lru` asegura que Redis descarte keys menos usadas antes de llenarse, en lugar de fallar silenciosamente.

## Verificacion

```bash
docker logs nodo-redis --tail=20
# Debe mostrar: "maxmemory policy set to allkeys-lru"

docker logs nodo-websocket --tail=30
# No deben aparecer WSDISCONNECT inmediatos (< 5 segundos post-WSCONNECT)
```

## Checklist de deploy

```
[ ] git pull origin Dev
[ ] docker-compose -f docker-compose.prod.yml up --build -d
[ ] docker ps — todos los containers healthy
[ ] Verificar WSCONNECT sin WSDISCONNECT inmediato en nodo-websocket logs
[ ] Monitorear error.log 10 minutos
```

## Deuda tecnica generada

- Monitorear uso de memoria de Redis en produccion. Si vuelve a llenarse, evaluar aumentar `mem_limit` a 600m o separar cache y channel layer en instancias Redis distintas (DB 0 para cache, DB 1 para channels).
- El WSREJECT (4403) de algunos usuarios es comportamiento esperado pero podria mejorar la UX mostrando un mensaje mas claro en el frontend en lugar de reintentar en loop.
