# core

`core` es parte del nucleo no removible. Concentra shared kernel, rutas base, auditoria y utilidades transversales requeridas por Django.

## Layout canonico

- `domain/`: value objects o politicas transversales sin Django.
- `application/`: servicios de aplicacion y puertos transversales cuando apliquen.
- `infrastructure/`: adapters para persistencia, cache, signals o integraciones Django.
- `interfaces/`: URLConfs web/API y adapters HTTP.
- `models.py`: adapter ORM historico, no contrato publico entre modulos.

## Regla

Los modulos funcionales no deben importar internals de `core.views` o `core.forms`; deben usar contratos explicitos o rutas publicas.
