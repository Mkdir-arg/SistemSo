# users

`users` es parte del nucleo no removible. Resuelve autenticacion, perfiles, grupos y permisos base.

## Layout canonico

- `domain/`: politicas de identidad y permisos sin Django.
- `application/`: casos de uso de usuarios y asignacion de grupos.
- `infrastructure/`: adapters ORM y sincronizaciones con grupos Django.
- `interfaces/`: URLConfs web/API, views, forms y serializers.
- `models.py`: adapter ORM historico requerido por Django.

## Regla

Los permisos gestionados por modulos se filtran desde `system_modules`; un modulo inactivo o no instalado no debe aparecer para nuevas asignaciones.

Las views, forms, API, serializers y templates viven bajo `interfaces/`; services, selectors y signals con Django/ORM viven bajo `infrastructure/`.
