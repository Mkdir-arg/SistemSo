# Guia de implementacion de nuevos modulos

## Objetivo

Agregar modulos nuevos sin romper el monolito ni depender de magia implicita.

## Paso 1 - Crear descriptor explicito

Crear `mi_modulo/module.py`:

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
            urlconf="mi_modulo.urls",
            namespace="mi_modulo",
            app_name="mi_modulo",
        ),
    ),
    adapter_points=("portal", "dashboard"),
)
```

## Paso 2 - Registrar el modulo

Agregar el slug en `config/modules.py::INSTALLED_PROJECT_MODULES`.

## Paso 3 - Definir frontera publica

Elegir uno de estos cortes:

- Solo catalogo + guards + shell awareness.
- Modulo con service layer.
- Modulo con `domain/application/infrastructure/interfaces`.

La opcion mas profunda solo se justifica si el dominio tiene reglas o side effects relevantes.

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

## Checklist rapido

- Descriptor explicito
- Registro en `config/modules.py`
- Guards aplicados
- Shell degradado
- Tests nuevos
- README y docs
