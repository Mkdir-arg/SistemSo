# Sprint Actual — SistemSo

> Estado: Sin sprint activo
> Inicio: —
> Fin: —

## Objetivo del sprint

_Se define en el sprint planning._

## Items del sprint

| ID | User Story | Estado | Notas |
|----|-----------|--------|-------|
| DX-001 | Como equipo de desarrollo quiero estandarizar `users`, `portal` institucional y `turnos` con services/selectors/views delgadas para mejorar DX y testabilidad | ✅ Completado | Trabajo técnico ejecutado fuera de sprint formal el 2026-03-13 |
| DX-002 | Como equipo de desarrollo quiero refactorizar `configuracion` institucional y de actividades con selectors/services/forms explícitos para bajar acoplamiento y facilitar testing | ✅ Completado | Slice 2 ejecutado el 2026-03-13 sin cambios de modelo |
| DX-003 | Como equipo de desarrollo quiero refactorizar `legajos` en ciudadanos y admisión para ordenar RENAPER, sesión y consultas reutilizables | ✅ Completado | Slice 3 ejecutado el 2026-03-13 sin cambios de modelo |
| DX-004 | Como equipo de desarrollo quiero refactorizar el flujo clínico base de `legajos` para separar evaluación, planes, seguimientos y derivaciones en selectors/services/forms consistentes | ✅ Completado | Slice 4 ejecutado el 2026-03-13 sin cambios de modelo |
| DX-005 | Como equipo de desarrollo quiero cerrar el hotspot restante del legajo clínico en eventos, reportes, exportación y responsable para eliminar lógica y templates inconsistentes | ✅ Completado | Slice 5 ejecutado el 2026-03-13 sin cambios de modelo |
| DX-006 | Como equipo de desarrollo quiero separar físicamente `legajos/views.py` por dominios para que el módulo sea más navegable y mantenible sin romper compatibilidad | ✅ Completado | Slice 6 ejecutado el 2026-03-13 sin cambios de modelo ni URLs |
| DX-007 | Como equipo de desarrollo quiero completar la modularización de `legajos/views.py` dejando una fachada pura y moviendo la operativa institucional a un módulo propio | ✅ Completado | Slice 7 ejecutado el 2026-03-13 sin cambios de modelo, URLs ni templates |
| DX-008 | Como equipo de desarrollo quiero modularizar `conversaciones` con selectors, services y views separadas para bajar el acoplamiento del chat sin romper sus endpoints | ✅ Completado | Slice 8 ejecutado el 2026-03-13 manteniendo URLs y contrato AJAX/WebSocket |
| DX-009 | Como equipo de desarrollo quiero alinear la API auxiliar de `conversaciones` al patrón de selectors/services para eliminar queries y permisos inline duplicados | ✅ Completado | Slice 9 ejecutado el 2026-03-13 sin cambios de rutas ni modelos |
| DX-010 | Como equipo de desarrollo quiero separar físicamente `configuracion/views.py` por dominios para que la app siga el mismo patrón modular del resto del refactor | ✅ Completado | Slice 10 ejecutado el 2026-03-13 sin cambios de URLs, modelos ni templates |
| DX-011 | Como equipo de desarrollo quiero habilitar namespaces consistentes en `users`, `core` y `healthcheck` sin romper los names legacy mientras se migra el proyecto | ✅ Completado | Slice 11 ejecutado el 2026-03-13 con compatibilidad dual namespaced/legacy |
| DX-012 | Como equipo de desarrollo quiero migrar consumidores claros a `core:*` y `users:*` para empezar a retirar dependencia de names legacy | ✅ Completado | Slice 12 ejecutado el 2026-03-13 solo sobre templates con names no ambiguos |
| DX-013 | Como equipo de desarrollo quiero modularizar `chatbot` y validar payloads JSON para bajar acoplamiento entre chat público y administración | ✅ Completado | Slice 13 ejecutado el 2026-03-13 sin cambios de rutas ni modelos |
| DX-014 | Como equipo de desarrollo quiero corregir el contrato real frontend/backend de `chatbot` y endurecer CSRF en sus endpoints principales | ✅ Completado | Slice 14 ejecutado el 2026-03-13 alineando rutas, shape JSON y protección CSRF |
| DX-015 | Como equipo de desarrollo quiero corregir el contrato real de `conversaciones` y endurecer CSRF en sus endpoints JSON sin romper la UX actual | ✅ Completado | Slice 15 ejecutado el 2026-03-13 alineando evaluación pública, URLs renderizadas y protección CSRF |
| DX-016 | Como equipo de desarrollo quiero estabilizar el runtime de la lista en vivo de `conversaciones` para evitar doble suscripción y paths hardcodeados | ✅ Completado | Slice 16 ejecutado el 2026-03-13 alineando `conversaciones_lista_ws.js` con URLs renderizadas y guard de inicialización |
| DX-017 | Como equipo de desarrollo quiero cerrar los consumidores residuales de `conversaciones` fuera de su lista principal para reducir hardcodes cross-app | ✅ Completado | Slice 17 ejecutado el 2026-03-13 moviendo config de URLs a `base.html`, detalle operador y portal ciudadano |
| DX-018 | Como equipo de desarrollo quiero extraer consultas ciudadanas de `portal/views_ciudadano.py` a capas más claras para bajar acoplamiento y mejorar testabilidad | ✅ Completado | Slice 18 ejecutado el 2026-03-13 con forms, selectors y services dedicados |

## Impedimentos

_Ninguno._

---

## Historial de sprints anteriores

Ver `docs/team/changelog.md` para el detalle de cada sprint.
