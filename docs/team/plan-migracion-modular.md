# Plan de migracion modular

## Fase 0 - Baseline y ADR

- Partir de `origin/Dev` en worktree limpio.
- Congelar el diseno del monolito modular activable.
- Corregir drift documental base.

## Fase 1 - Control plane

- Crear `system_modules/`.
- Registrar modulos instalados en `settings.SYSTEM_MODULES`.
- Persistir `ModuleState`.
- Exponer guards, context processor, admin y `sync_module_catalog`.

## Fase 2 - Shells resilientes

- Volver module-aware al sidebar, dashboard, portal ciudadano y widgets globales.
- Dejar que los shells oculten capacidades faltantes sin romper templates ni JS.

## Fase 3 - Piloto hexagonal en `turnos`

- Mover reglas de negocio a `turnos/domain`.
- Orquestar casos de uso en `turnos/application`.
- Encapsular ORM, mail y cache en `turnos/infrastructure`.
- Mantener URLs y adapters legacy.

## Fase 4 - Modulos opcionales iniciales

- Registrar `chatbot`, `conversaciones`, `tramites` y `flujos`.
- Aplicar guards y shell integration.
- No reescribir los modulos sin necesidad.

## Fase 5 - Hotspot `legajos`

- Extraer primero servicios, views y templates por subdominio.
- Posponer la particion de modelos/tablas hasta tener contratos mas claros.

## Fase 6 - Limpieza final

- Retirar compatibilidades sobrantes donde ya no agreguen valor.
- Consolidar tests de arquitectura.
- Cerrar documentacion y checklist final.
