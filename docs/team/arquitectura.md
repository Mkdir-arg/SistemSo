# Arquitectura del Sistema

> **Regla:** El Arquitecto lee este documento ANTES de proponer cualquier diseño técnico.
> **Regla:** El Arquitecto actualiza este documento cuando toma una decisión técnica relevante.
> Última actualización: 2026-03-12

---

## Stack tecnológico

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| Backend | Python / Django | 3.12 / 4.2 |
| Base de datos | MySQL | 8.0 |
| Frontend | Tailwind CSS + Alpine.js | CDN |
| WebSocket | Django Channels + Redis | — |
| Cache | Redis | 7 |
| Servidor | Nginx + Gunicorn | — |
| Contenedores | Docker Compose | — |
| Admin UI | Django Admin | — |

---

## Estructura de apps Django

```
SistemSo/
├── config/           → settings, urls, wsgi, asgi, middlewares
├── core/             → Institucion, modelos geográficos, auditoría, utilidades base
├── legajos/          → Ciudadanos, legajos, programas, ÑACHEC, contactos, institucional
├── portal/           → Portal ciudadano (auth, turnos legacy, registro instituciones)
├── turnos/           → Backoffice de turnos configurables (NEW — app separada)
├── conversaciones/   → Chat ciudadano-operador, WebSocket
├── chatbot/          → Bot IA integrado al chat
├── users/            → Usuarios del backoffice, permisos, SolicitudCambioEmail
├── configuracion/    → UI de configuración (sin modelos propios)
├── dashboard/        → Panel principal
├── tramites/         → Módulo de trámites (stub, sin desarrollar)
└── healthcheck/      → Health checks del sistema
```

---

## Principios de arquitectura establecidos

> Estas decisiones NO deben revertirse sin una razón técnica fuerte y aprobación del usuario.

### Separación de apps
- **Nueva funcionalidad → nueva app Django.** No agregar más modelos a `legajos/`. Ya tiene 4 dominios mezclados y es deuda técnica.
- Cuando una funcionalidad involucra múltiples apps existentes, vive en la app más neutral o en una nueva.
- El backoffice y el portal ciudadano viven en apps separadas. No mezclar vistas de operador con vistas de ciudadano.

### Modelos
- Todos los modelos usan `verbose_name` y `__str__` obligatoriamente.
- Los modelos abstractos base viven en `core/models.py` (`TimeStamped`, `LegajoBase`).
- Las FKs entre apps se referencian como strings: `'legajos.Ciudadano'`, `'turnos.ConfiguracionTurnos'`.
- Los campos nuevos en modelos existentes son siempre `null=True` o tienen `default` para no romper datos.

### Migraciones
- Se crean inmediatamente después de modificar un modelo. Nunca se acumulan.
- Las migraciones con dependencias cruzadas (una app depende de otra) van en la app que agrega el campo, con `dependencies` explícitas.
- No se hacen `squashmigrations` sin coordinación explícita.

### Seguridad
- Todas las vistas del backoffice: `@login_required` mínimo.
- Vistas del portal ciudadano: `@ciudadano_required` (decorator propio en `core/decorators.py`).
- Vistas de administración de turnos: `group_required(['Administradores de Turnos'])`.
- CSRF en todos los forms POST sin excepción. Las vistas con `@csrf_exempt` son deuda técnica.

### Frontend
- Tailwind CSS via CDN (configurado en `includes/base.html`).
- Alpine.js para interactividad sin build step.
- SweetAlert2 para confirmaciones de eliminación.
- Select2 activado globalmente desde `base.html` — no duplicar.
- Los templates del backoffice extienden `includes/base.html`.
- Los templates del portal ciudadano extienden `portal/base.html`.

---

## Decisiones técnicas tomadas

### DT-001 — Coexistencia de RecursoTurnos y ConfiguracionTurnos (2026-03-09)
**Contexto:** El portal ciudadano usaba `RecursoTurnos` como única forma de configurar turnos. Se necesitaba extender el sistema para que cualquier entidad (Programa, Institución, Actividad) pudiera tener turnos configurables.

**Decisión:** Crear `ConfiguracionTurnos` en nueva app `turnos/`. `RecursoTurnos` se mantiene como legacy con un `OneToOneField` a `ConfiguracionTurnos`. `TurnoCiudadano` tiene FK a ambos, con propiedad `config_efectiva` que hace fallback.

**Por qué no se migró directo:** Los turnos históricos tienen `recurso` asignado. La migración directa hubiera roto los datos existentes.

**Consecuencia:** El código nuevo usa `configuracion`. El portal ciudadano existente sigue usando `recurso`. En v2 se migrará completamente.

---

### DT-002 — App `turnos/` separada de `portal/` (2026-03-09)
**Decisión:** El backoffice de turnos vive en `turnos/`, no en `portal/`. Razón: `ConfiguracionTurnos` es referenciada por `core`, `legajos` y `portal`. Si viviera en `portal/`, las otras apps dependerían del portal, invirtiendo la dependencia.

---

### DT-004 — Editor visual de flujos: React Flow + Vite (2026-03-12)
**Contexto:** El editor de flujos de programas requiere un canvas drag & drop con nodos conectables — funcionalidad imposible de implementar bien con Alpine.js.

**Decisión:** React (con React Flow) solo para el editor visual. El resto del sistema sigue con Alpine.js. Compilación con Vite. Los assets compilados se sirven desde `static/flujos/dist/` via Django staticfiles. La comunicación con el backend es via API REST (`GET/POST /api/flujos/<programa_id>/`).

**Por qué React Flow:** estándar de industria para grafos en React, maneja el modelo de nodos y conexiones nativamente, JSON listo para persistir, nodos completamente custom, MIT.

**Por qué no todo React:** el resto del sistema no necesita SPA. Introducir React globalmente agregaría complejidad de build sin beneficio. El editor es el único componente que lo justifica.

**Consecuencia:** se agrega `frontend/flow-editor/` a la raíz del proyecto. El pipeline de CI debe compilar el editor antes del deploy. El template `flujos/editor.html` carga los assets compilados.

---

### DT-005 — Tercera superficie: Panel Institución en `/institucion/` (2026-03-12)
**Contexto:** Las instituciones necesitan una superficie propia para sus usuarios (EncargadoInstitucion, AdministrativoInstitucion, ProfesorInstitucion) que no es el backoffice ni el portal ciudadano.

**Decisión:** Nueva app Django `institucion/` con middleware propio, base template propio y routing separado. Mismo sistema de login Django — el middleware detecta el rol y redirige a `/institucion/`. Patrón idéntico al de `portal/`.

**Por qué no usar el portal ciudadano:** el portal está diseñado para ciudadanos en situación de vulnerabilidad. Compartirlo con representantes institucionales genera disonancia de UX y complica el middleware.

---

### DT-003 — Emails de notificación de turnos como best-effort (2026-03-09)
**Decisión:** `enviar_email_confirmacion()` y `enviar_email_cancelacion()` nunca lanzan excepciones al caller. Si el envío falla, se loguea y continúa. La acción del operador (aprobar/rechazar) no depende del email.

**Razón:** El email es una notificación secundaria. Bloquear la aprobación de un turno porque el servidor SMTP falló sería un error de prioridades.

---

## Deudas técnicas documentadas

| ID | Descripción | Severidad | Cuándo surgió |
|----|-------------|-----------|--------------|
| DT-001 | `legajos/` mezcla 4 dominios (ciudadanos, programas, ÑACHEC, institucional) | Alta | Desde el inicio |
| DT-002 | `simple_history` comentado en `legajos/models.py` — sin historial de cambios | Media | Desde el inicio |
| DT-003 | `TipoPrograma` tiene entrada duplicada `NACHEC`/`ÑACHEC` | Baja | Detectada 2026-03-09 |
| DT-004 | `portal/views.py` usa `@csrf_exempt` en vistas de institución | Alta | Detectada 2026-03-09 |
| DT-005 | `RecursoTurnos` es legacy — migrar a `ConfiguracionTurnos` en v2 | Media | 2026-03-09 |
| DT-006 | Recordatorios automáticos de turnos requieren Celery (no implementado) | Media | 2026-03-09 |
| DT-007 | `configuracion/` no tiene modelos propios — es solo una capa de UI sobre `core` y `legajos` | Baja | Detectada 2026-03-09 |

---

## Mapa de dependencias entre apps

```
                ┌─────────┐
                │  core   │  ← modelos base, Institucion, geografía
                └────┬────┘
                     │ FK
          ┌──────────┴──────────┐
          │                     │
     ┌────▼────┐          ┌─────▼────┐
     │ legajos │          │  turnos  │ ← ConfiguracionTurnos
     └────┬────┘          └─────┬────┘
          │ FK                  │ FK
     ┌────▼────┐          ┌─────▼────┐
     │  portal │──────────▶  portal  │ ← TurnoCiudadano (tiene FK a ambos)
     └────┬────┘          └──────────┘
          │
     ┌────▼──────────┐
     │ conversaciones │
     └───────────────┘
          │
     ┌────▼────┐
     │ chatbot │
     └─────────┘
```

---

## Grupos de Django y permisos

| Grupo | Quiénes | Qué pueden hacer |
|-------|---------|-----------------|
| `Ciudadanos` | Usuarios del portal ciudadano | Solo su propio perfil, turnos y consultas |
| `EncargadoInstitucion` | Representantes de ONG | Ver y gestionar su institución |
| `Responsable` | Profesionales con legajos asignados | Gestionar legajos asignados |
| `Administradores de Turnos` | Operadores con permisos de config | Crear/editar ConfiguracionTurnos y disponibilidades |
| Staff Django (`is_staff=True`) | Operadores backoffice | Acceso general al backoffice |
| Superusuario (`is_superuser=True`) | Administrador del sistema | Acceso total |

---

## Patrones a seguir en código nuevo

### Vista de backoffice estándar
```python
@login_required
@group_required(['NombreGrupo'])  # si requiere grupo específico
def mi_vista(request):
    ...
```

### Template de backoffice
```html
{% extends 'includes/base.html' %}
{% block content %}
  <!-- contenido -->
{% endblock %}
{% block extra_js %}
  <!-- JS específico de esta vista -->
{% endblock %}
```

### Modelo nuevo
```python
class MiModelo(TimeStamped):  # TimeStamped de core.models
    nombre = models.CharField(max_length=200, verbose_name='Nombre')

    class Meta:
        verbose_name = 'Mi modelo'
        verbose_name_plural = 'Mis modelos'

    def __str__(self):
        return self.nombre
```

### FK cross-app
```python
# Siempre como string para evitar importación circular
ciudadano = models.ForeignKey('legajos.Ciudadano', on_delete=models.PROTECT)
```
