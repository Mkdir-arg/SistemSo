# conversaciones

`conversaciones` queda registrado como modulo opcional del monolito.

## Estado actual

- Catalogo explicito con `conversaciones/module.py`.
- Guards en vistas publicas y de backoffice.
- Sidebar, dashboard, portal ciudadano y scripts globales renderizan segun `module_capabilities`.

## Superficies afectadas

- `/conversaciones/`
- Dashboard de metricas
- Alertas globales
- Portal ciudadano de consultas

## Si se desactiva

- El shell no publica accesos ni widgets dependientes del modulo.
- Las vistas responden `module_inactive`.
- El resto del sistema sigue operativo.
