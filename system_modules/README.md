# system_modules

`system_modules` es el control plane del monolito modular.

## Responsabilidades

- Cargar el catalogo explicito de modulos desde `settings.SYSTEM_MODULES`.
- Persistir el estado por instancia en `ModuleState`.
- Diferenciar modulo instalado vs modulo activo.
- Exponer guards, contexto de templates y helpers para formularios/permisos.
- Sincronizar metadata del catalogo con `sync_module_catalog`.

## Piezas principales

- `definitions.py`: `ModuleDefinition` y `NavItemDefinition`.
- `registry.py`: carga y cachea el catalogo instalado.
- `services.py`: `ModuleResolver`, `sync_module_catalog`, helpers de grupos y capacidades.
- `guards.py`: `module_required`, `ModuleRequiredMixin`, `ModuleActivePermission`.
- `context_processors.py`: publica `module_capabilities` y `active_module_slugs`.
- `models.py`: `ModuleState` con `is_installed` e `is_enabled`.

## Contrato operacional

- Si un modulo sale de `SYSTEM_MODULES`, `sync_module_catalog` lo marca como `is_installed=False` y `is_enabled=False`.
- Si un modulo esta instalado pero inactivo, los guards devuelven `403` con payload `module_inactive`.
- Los grupos gestionados por modulos inactivos o no instalados se ocultan en la administracion de usuarios.

## Comando clave

```powershell
py -3 manage.py sync_module_catalog
```

## Regla importante

No hay autodiscovery por filesystem. El catalogo es explicito, legible y testeable.
