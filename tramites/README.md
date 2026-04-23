# tramites

`tramites` se incorpora al control plane como modulo opcional.

## Estado actual

- Catalogo explicito con `tramites/module.py`.
- Guard de modulo en las vistas de backoffice.
- Sidebar del backoffice aware del estado del modulo.

## Objetivo de esta etapa

No se reescribe el modulo. Se garantiza activacion/desactivacion limpia y sin choque con otros modulos.
