# turnos

`turnos` es el piloto real de hexagono pragmatico dentro del monolito.

## Estructura

- `domain/`: reglas de estado y validaciones de workflow.
- `application/`: casos de uso ciudadanos y de backoffice.
- `infrastructure/`: repositorios ORM y notificaciones.
- `interfaces/`: API publica consumida por portal y backoffice.
- `module.py`: descriptor para `system_modules`.

## Contrato publico

- `turnos.interfaces.module_api.reservar_turno_ciudadano`
- `turnos.interfaces.module_api.cancelar_turno_ciudadano`
- `turnos.interfaces.module_api.aprobar_turno_backoffice`
- `turnos.interfaces.module_api.rechazar_turno_backoffice`
- `turnos.interfaces.module_api.cancelar_turno_backoffice`
- `turnos.interfaces.module_api.completar_turno_backoffice`

## Frontera de datos historica

`turnos` conserva modelos y app Django top-level porque `portal` y tablas historicas dependen de esas claves. El contrato publico no es un wrapper: los consumidores externos deben entrar por `turnos.interfaces.module_api` o por las URLs declaradas en `turnos/module.py`.

## Regla de dependencia

`turnos/domain` no importa Django. `turnos/application` no debe importar `views` ni `forms`.
