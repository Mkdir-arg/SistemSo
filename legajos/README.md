# legajos

`legajos` sigue siendo el hotspot mayor del repo.

## Estado actual

- Sigue siendo una app grande con varios subdominios mezclados.
- Consume el shared kernel y convive con shells y modulos opcionales.
- No se parte en esta fase para evitar un big bang de datos y rutas.
- Views, forms, API, serializers y templates viven bajo `interfaces/`.
- Services, selectors y signals con ORM/Django viven bajo `infrastructure/`.
- `models.py` y modelos historicos relacionados permanecen top-level por estabilidad de migrations/contenttypes, no como contrato publico.

## Plan posterior

La particion objetivo es:

- `ciudadania`
- `programas`
- `nachec`
- `institucional`
- `contactos`

Antes de partir tablas, el camino recomendado es extraer subdominios completos con contratos propios, manteniendo los modelos historicos encapsulados como infraestructura ORM hasta contar con migracion de datos segura.
