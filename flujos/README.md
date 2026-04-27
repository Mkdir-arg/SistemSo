# flujos

`flujos` queda tratado como modulo opcional dentro del monolito.

## Estado actual

- Catalogo explicito con `flujos/module.py`.
- Rutas HTML y API se publican desde `config/urls.py` solo si el modulo esta instalado.
- El shell de configuracion oculta el acceso al editor visual cuando el modulo esta inactivo.
- Views, forms, API y templates viven bajo `interfaces/`.

## Nota

En esta fase no se reescribe el motor. El corte fue de catalogo, guards, shell integration y ubicacion fisica canonica de adapters.
