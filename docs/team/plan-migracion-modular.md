# Plan de migracion modular

## Fase 0 - Baseline y ADR

- Partir de `origin/Dev` en worktree limpio.
- Congelar el diseno del monolito modular activable.
- Corregir drift documental base.

## Fase 1 - Control plane

- Crear `system_modules/`.
- Registrar modulos instalados en `config.modules.INSTALLED_PROJECT_MODULES`.
- Persistir `ModuleState`.
- Exponer guards, context processor, admin y `python manage.py modules sync`.

## Fase 2 - Shells resilientes

- Volver module-aware al sidebar, dashboard, portal ciudadano y widgets globales.
- Dejar que los shells oculten capacidades faltantes sin romper templates ni JS.

## Fase 3 - Layout hexagonal literal

- Crear `domain/`, `application/`, `infrastructure/` e `interfaces/` en todos los modulos declarados.
- Exigir por test los archivos base de cada capa.
- Publicar URLConfs desde `interfaces/web/urls.py`, `interfaces/api/urls.py` y adapters realtime cuando aplique.
- Mantener `models.py` top-level solo como adapter ORM de Django.

## Fase 4 - Control plane y modulos opcionales

- Registrar `chatbot`, `conversaciones`, `tramites` y `flujos`.
- Aplicar guards y shell integration.
- No publicar rutas opcionales hardcodeadas en `config/urls.py`.
- Si el modulo sale de `INSTALLED_PROJECT_MODULES`, sus rutas dejan de existir y el shell no intenta renderizar capacidades.

## Fase 5 - Hotspot `legajos`

- Mantener `legajos` como no removible por FKs historicas.
- Exponer contratos publicos desde `legajos/interfaces/module_api.py`.
- Migrar subdominios por cortes: ciudadanos, programas, institucional, clinico, nachec, alertas/reportes.
- Posponer movimiento fisico de modelos/tablas hasta tener migracion de datos segura.

## Fase 6 - Limpieza final

- Verificar que no queden fachadas publicas de compatibilidad en los modulos migrados.
- Consolidar tests de arquitectura.
- Cerrar documentacion y checklist final.

## Estado PR #35

- Control plane implementado en `system_modules`.
- Rutas de modulos movidas a adapters canonicos en `interfaces/`.
- Test de arquitectura exige layout literal y prohibe rutas declaradas fuera de `interfaces/`.
- La frontera publica queda en `interfaces/`; cualquier reubicacion fisica posterior de adapters internos debe preservar esa frontera sin crear fachadas legacy.
