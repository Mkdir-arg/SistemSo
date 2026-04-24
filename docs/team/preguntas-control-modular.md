# Preguntas de control

## Nivel 1

1. Cual es la diferencia entre modulo no instalado y modulo instalado pero inactivo.
2. Por que `config.modules.INSTALLED_PROJECT_MODULES` es preferible a autodiscovery por filesystem.
3. Que responsabilidad tiene `system_modules` y cual no.

## Nivel 2

1. Por que `portal`, `dashboard` y `configuracion` se tratan como shells y no como dominios.
2. Por que todos los modulos tienen `domain/application/infrastructure/interfaces`, incluso si una capa queda fina.
3. Que riesgo se evita al migrar consumidores antes de borrar una fachada publica.

## Nivel 3

1. Que pasaria si un modulo nuevo importa `views` de otro modulo para reutilizar una pantalla.
2. Como ocultarias grupos y accesos de un modulo removido del catalogo sin borrar datos historicos.
3. Por que `legajos` no se parte en esta fase aunque siga siendo el hotspot principal.
