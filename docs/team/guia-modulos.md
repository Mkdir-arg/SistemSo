# Guia de implementacion de nuevos modulos

## Objetivo

Agregar modulos nuevos sin romper el monolito ni depender de magia implicita.

## Paso 1 - Crear descriptor explicito

Crear `mi_modulo/module.py` y apuntar rutas a `interfaces/`:

```python
from system_modules.definitions import ModuleDefinition, NavItemDefinition, UrlDefinition

MODULE_DEFINITION = ModuleDefinition(
    slug="mi_modulo",
    display_name="Mi modulo",
    app_config="mi_modulo",
    description="Que hace",
    managed_groups=("miGrupo",),
    nav_items=(
        NavItemDefinition(
            handle="mi_modulo.nav",
            label="Mi modulo",
            url_name="mi_modulo:inicio",
            required_groups=("Administrador",),
        ),
    ),
    web_routes=(
        UrlDefinition(
            handle="mi_modulo.ui",
            route="mi-modulo/",
            urlconf="mi_modulo.interfaces.web.urls",
            namespace="mi_modulo",
            app_name="mi_modulo",
        ),
    ),
    adapter_points=("portal", "dashboard"),
)
```

## Paso 2 - Registrar el modulo

Agregar el slug en `config/modules.py::INSTALLED_PROJECT_MODULES`.

## Paso 3 - Crear layout hexagonal literal

Todo modulo debe crear esta base, incluso si alguna capa empieza fina:

```text
mi_modulo/
  module.py
  domain/
    entities.py
    policies.py
    errors.py
  application/
    dto.py
    ports.py
    services.py
  infrastructure/
    orm_repositories.py
    notifications.py
    signals.py
  interfaces/
    module_api.py
    web/
      urls.py
      views.py
      forms.py
    api/
      urls.py
```

La logica de dominio va en `domain/`; los casos de uso en `application/`; Django ORM, email, cache, signals, clock y transaction en `infrastructure/`; views, forms, serializers, templates, static y URLConfs en `interfaces/`.

## Paso 4 - Integrar shells

- Ocultar navegacion si el modulo no esta activo.
- Evitar `reverse()` o includes fuera de condiciones de modulo.
- Si el shell consume JS global, leer `module_capabilities_json`.

## Paso 5 - Tests minimos

- Sync del catalogo.
- Guard HTML y/o JSON.
- Shell sin links rotos cuando el modulo esta inactivo.
- Smoke test del contrato publico del modulo.

## Paso 6 - Documentacion

- README del modulo.
- Entrada en `docs/funcionalidades/_index.md`.
- Documento de version en `docs/funcionalidades/<slug>/`.
- Si una capa queda fina, explicarlo en el README del modulo.

## Checklist rapido

- Descriptor explicito
- Registro en `config/modules.py`
- Cuatro capas canonicas
- Rutas en `interfaces/web/urls.py` y `interfaces/api/urls.py`
- Guards aplicados
- Shell degradado
- Tests nuevos
- README y docs
