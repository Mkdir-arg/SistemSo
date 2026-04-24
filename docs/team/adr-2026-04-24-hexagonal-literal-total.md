# ADR 2026-04-24 - Hexagonal literal total por modulo

## Estado

Aceptado para PR #35.

## Contexto

El repositorio debe operar como padre clonable por cliente. La instancia debe poder instalar modulos desde `config/modules.py`, activar o desactivar disponibilidad desde `system_modules` y quitar modulos opcionales sin imports top-level rotos.

La migracion anterior dejo el control plane y un piloto fuerte en `turnos`, pero la documentacion permitia un hexagono pragmatico. El criterio actual exige layout hexagonal literal para todos los modulos, incluidos shells y core tecnico.

## Decision

- Todo modulo declarado tiene `domain/`, `application/`, `infrastructure/` e `interfaces/`.
- Las rutas publicas viven en `interfaces/web/urls.py`, `interfaces/api/urls.py` o adapters equivalentes como `interfaces/realtime/routing.py`.
- `module.py` debe declarar rutas apuntando a `interfaces/`.
- `domain/` no importa Django.
- `application/` no importa Django ni adapters internos como `models`, `views`, `forms`, `serializers`, `templates`, `consumers` o `routing`.
- `models.py` puede quedar top-level por estabilidad de Django, pero se considera adapter ORM de infraestructura.
- Los shells solo consumen capacidades y contratos publicos; no son duenos de dominio.

## Consecuencias

- Se gana una frontera uniforme para crear, apagar o quitar modulos.
- Se evita publicar fachadas legacy como contrato final.
- La migracion fisica de views/forms/templates puede avanzar por subdominio, pero el contrato externo ya no debe depender de URLConfs top-level.
- Los tests de arquitectura bloquean regresiones de layout, URLConfs viejas e imports Django en `domain/application`.

## Tests de control

- `system_modules.tests.test_architecture`
- `python manage.py check --settings=config.settings_test`
