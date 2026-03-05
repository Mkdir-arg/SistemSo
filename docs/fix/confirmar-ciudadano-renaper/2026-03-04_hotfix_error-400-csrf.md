# Error 400 al confirmar ciudadano — HOTFIX

> Fecha: 2026-03-04
> Tipo: HOTFIX
> Funcionalidad afectada: `confirmar-ciudadano-renaper`
> Severidad: ALTA

---

## Problema

Al hacer POST en `/legajos/ciudadanos/confirmar/` en produccion, Django devuelve HTTP 400. El operador no puede completar el alta de ciudadano via RENAPER.

## Causa raiz

`CSRF_COOKIE_HTTPONLY = True` estaba configurado en `settings_production.py` y en el bloque `prd` de `settings.py`. Esta flag hace que la cookie CSRF sea HttpOnly (inaccesible para JavaScript), pero en el contexto de proxy nginx + HTTPS → gunicorn → Django, interfiere con la validacion del token CSRF en el POST, resultando en un 400.

Segun la documentacion oficial de Django, esta flag no aporta seguridad real y puede causar problemas en setups con proxy SSL.

## Impacto

- Usuarios afectados: todos los operadores con acceso al modulo de ciudadanos
- Funcionalidad bloqueada: creacion de ciudadanos via RENAPER (flujo completo bloqueado)
- Workaround disponible: No

## Fix aplicado

| Archivo | Cambio |
|---------|--------|
| `config/settings_production.py` | Eliminado `CSRF_COOKIE_HTTPONLY = True` (linea 17) |
| `config/settings.py` | Eliminado `CSRF_COOKIE_HTTPONLY = True` del bloque `if ENVIRONMENT == "prd"` (linea 357) |

## Verificacion

1. Acceder a `/legajos/ciudadanos/nuevo/`
2. Ingresar un DNI valido y consultar RENAPER
3. En el formulario de confirmacion, completar y enviar
4. Verificar que el ciudadano queda guardado sin error 400

## Checklist de deploy

```
[ ] git pull origin Dev
[ ] docker-compose up --build -d
[ ] Test funcional: RENAPER lookup → confirmar → ciudadano creado OK
[ ] Verificar ausencia de 400 en logs: /legajos/ciudadanos/confirmar/
[ ] Monitorear logs 10 minutos post-deploy
```

## Deuda tecnica generada

Ninguna. El fix es la solucion definitiva.
