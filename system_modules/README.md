# system_modules

`system_modules` es el control plane del monolito modular.

## Responsabilidades

- Cargar el catalogo explicito de modulos desde `config/modules.py::INSTALLED_PROJECT_MODULES`.
- Persistir el estado por instancia en `ModuleState`.
- Diferenciar modulo instalado vs modulo activo.
- Exponer guards, contexto de templates y helpers para formularios/permisos.
- Sincronizar metadata del catalogo con `python manage.py modules sync`.

## Piezas principales

- `module.py`: descriptor del propio control plane como modulo core.
- `domain/`, `application/`, `infrastructure/`, `interfaces/`: layout canonico del modulo, aunque varias capas sean finas porque el dominio real es el registry.
- `definitions.py`: `ModuleDefinition` y `NavItemDefinition`.
- `registry.py`: carga y cachea el catalogo instalado.
- `infrastructure/services.py`: `ModuleResolver`, sincronizacion interna del catalogo, helpers de grupos y capacidades.
- `guards.py`: `module_required`, `ModuleRequiredMixin`, `ModuleActivePermission`.
- `context_processors.py`: publica `module_capabilities` y `active_module_slugs`.
- `models.py`: `ModuleState` con `is_installed` e `is_enabled`.

## Contrato operacional

- Si un modulo sale de `INSTALLED_PROJECT_MODULES`, `python manage.py modules sync` lo marca como `is_installed=False` y `is_enabled=False`.
- Si un modulo esta instalado pero inactivo, los guards devuelven `403` con payload `module_inactive`.
- Los grupos gestionados por modulos inactivos o no instalados se ocultan en la administracion de usuarios.

## Comando clave

```powershell
py -3 manage.py modules list
py -3 manage.py modules enable chatbot
py -3 manage.py modules disable chatbot
py -3 manage.py modules sync
```

## Regla importante

No hay autodiscovery por filesystem. El catalogo es explicito, legible y testeable.

## Literalidad fisica

`system_modules` no expone `services.py`, `signals.py` ni templates en la raiz como contrato publico. Los services y signals que dependen de Django viven en `infrastructure/`, y el template de modulo inactivo vive en `interfaces/templates/`.
