# healthcheck

`healthcheck` es core tecnico no removible. Expone verificaciones de salud para operacion e infraestructura.

## Layout canonico

- `domain/`: reglas o resultados de salud independientes de Django si se agregan.
- `application/`: orquestacion de checks si el modulo crece.
- `infrastructure/`: adapters para dependencias externas.
- `interfaces/`: URLConf web canonica y adapter HTTP.

## Regla

No debe depender de modulos opcionales; si un check opcional existe, debe consultarse a traves del catalogo de `system_modules`.

La URLConf y views de health check viven bajo `interfaces/web/`; no se publican entrypoints top-level.
