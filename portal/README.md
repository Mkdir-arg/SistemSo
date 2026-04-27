# portal

`portal` es un shell del monolito, no un modulo dueno del negocio.

## Responsabilidad

- Orquestar la superficie ciudadana.
- Consumir contratos publicos de modulos activos.
- Degradar sin romper navegacion cuando un modulo opcional no esta disponible.

## Regla

La logica de negocio nueva no debe quedarse en el shell si pertenece a un modulo vertical. En `turnos`, el shell consume `turnos.interfaces.module_api`.

## Literalidad fisica

Las views, forms y templates del portal viven bajo `interfaces/`; services y selectors ciudadanos con Django/ORM viven bajo `infrastructure/`. El shell no publica entrypoints top-level como contrato publico.
