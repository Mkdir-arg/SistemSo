# configuracion

`configuracion` es un shell de administracion y setup, no un dominio autonomo.

## Responsabilidad

- Exponer accesos de configuracion para modulos activos.
- Mantener la UI resiliente si un editor o capacidad opcional esta inactivo.

## Ejemplo

El acceso al editor de `flujos` solo se muestra cuando `flujos` esta activo.

## Literalidad fisica

Las views, forms y templates viven bajo `interfaces/`; los selectors y services con ORM/Django viven bajo `infrastructure/`. `configuracion` no debe contener logica de dominio de modulos verticales.
