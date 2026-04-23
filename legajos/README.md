# legajos

`legajos` sigue siendo el hotspot mayor del repo.

## Estado actual

- Sigue siendo una app grande con varios subdominios mezclados.
- Consume el shared kernel y convive con shells y modulos opcionales.
- No se parte en esta fase para evitar un big bang de datos y rutas.

## Plan posterior

La particion objetivo es:

- `ciudadania`
- `programas`
- `nachec`
- `institucional`
- `contactos`

Antes de partir tablas, el camino recomendado es extraer servicios, views y templates por subdominio.
