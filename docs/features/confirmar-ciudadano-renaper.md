# Confirmar Ciudadano — RENAPER

> Archivo generado automaticamente por el Documentador.
> Los agentes deben leer este archivo antes de modificar cualquier cosa relacionada con esta funcionalidad.

---

## Estado actual

Flujo de creacion de ciudadano via RENAPER: busqueda por DNI → validacion → confirmacion de datos → guardado.
El usuario hace una consulta a RENAPER, los datos se guardan en sesion, y se redirige a un formulario pre-completado para confirmar y guardar el ciudadano.

## Archivos principales

| Archivo | Rol |
|---------|-----|
| `legajos/views.py` | `CiudadanoRenaperView`, `CiudadanoConfirmarView` |
| `legajos/forms.py` | `CiudadanoForm` |
| `legajos/urls.py` | `ciudadano_confirmar` (linea 21 y 78) |
| `legajos/templates/legajos/ciudadano_confirmar_form.html` | Template del formulario de confirmacion |
| `config/settings.py` | Configuracion CSRF y sesiones |
| `config/settings_production.py` | Overrides de produccion |

## Dependencias

- Depende de: API RENAPER (`RENAPER_API_URL`), sesion Django para pasar datos entre vistas
- Usada por: flujo de alta de ciudadanos, legajos

---

## Historial de cambios

| Fecha | Tipo | Titulo | Quien |
|-------|------|--------|-------|
| 2026-03-04 | HOTFIX | Error 400 al confirmar ciudadano en produccion | Agente |

---

### 2026-03-04 — HOTFIX: Error 400 al confirmar ciudadano en produccion

**Impacto en produccion:**
Todos los usuarios afectados. No era posible crear ciudadanos via RENAPER. El formulario de confirmacion devolia 400 al hacer POST.

**Causa raiz:**
`CSRF_COOKIE_HTTPONLY = True` en settings de produccion interferia con la validacion CSRF en el flujo nginx (HTTPS proxy) → gunicorn → Django. Con esta flag, el middleware CSRF no podia validar correctamente el token del formulario contra la cookie en el contexto de proxy SSL.

**Fix aplicado:**
- `config/settings_production.py:17` — eliminado `CSRF_COOKIE_HTTPONLY = True`
- `config/settings.py:357` — eliminado `CSRF_COOKIE_HTTPONLY = True` del bloque `if ENVIRONMENT == "prd"`

**Workaround aplicado antes del fix:** Ninguno
**Deuda tecnica generada:** Ninguna — el fix es la solucion definitiva
**Checklist de deploy:** Pendiente de aplicar en produccion
