# Product Backlog — SistemSo

> Actualizado: 2026-03-09

## Leyenda
- 🟡 Pendiente
- 🔵 En sprint
- ✅ Completado
- ❌ Descartado

## Features pendientes

| ID | User Story | Complejidad | Notas |
|----|-----------|-------------|-------|
| US-004 | Como usuario con rol `configurarSecretaria` quiero gestionar el catálogo de Secretarías y Subsecretarías y vincular Programas a una Subsecretaría para organizar los programas dentro de la jerarquía organizacional | Mediano 🟡 | Diseño técnico completo aprobado. Ver `docs/requerimientos/2026-03-09_estructura-programas-y-flujos.md`. Paso 1 de 4. |
| US-005 | Como usuario con rol `ConfiguracionPrograma` quiero configurar un programa mediante un wizard (datos básicos, jerarquía, naturaleza, capacidades activables) para poder dar de alta programas correctamente tipificados | Grande 🟡 | Requiere US-004 completada primero. Paso 2 de 4. |
| US-006 | Como desarrollador quiero un motor de flujos backend (app `flujos/`) con modelos, runtime y tipos de nodo para que los programas puedan tener flujos configurables | Grande 🟡 | Adaptar backend del sistema NODO (referencia documentada). Requiere US-005. Paso 3 de 4. |
| US-007 | Como usuario con rol `ConfiguracionPrograma` quiero un editor visual de flujos para diseñar el flujo de un programa mediante drag & drop | Grande 🟡 | Requiere decisión de stack (React para editor). Requiere US-006. Paso 4 de 4. |
| US-008 | Como operador quiero que la ficha del ciudadano incluya situación habitacional, laboral, educativa, médica, documentación migratoria, notas y foto para tener toda la información social centralizada | Mediano 🟡 | Ver `docs/requerimientos/2026-03-09_ciudadano-hub-y-roles.md` |
| US-009 | Como operador quiero ver el hub del ciudadano con solapas estáticas y dinámicas con badge behavior para acceder a toda su información desde un solo lugar | Mediano 🟡 | Requiere US-008. Solapas dinámicas: Programas, Turnos, Instituciones, Conversaciones, Derivaciones, Alertas, Línea de tiempo |
| US-010 | Como administrador quiero gestionar los roles `ciudadanoVer`, `ciudadanoCrear` y `ciudadanoSensible` para controlar quién accede a qué información del ciudadano | Pequeño 🟡 | Incluye filtro por ámbito (institución vs. backoffice) |
| US-011 | Como administrador quiero que todos los roles del sistema (`configurarSecretaria`, `ConfiguracionPrograma`, `ciudadanoVer`, `ciudadanoCrear`, `ciudadanoSensible`) existan como grupos Django desde el inicio | Pequeño 🟡 | Data migration o management command. Prerequisito para todos los features de permisos |
| US-012 | Como operador quiero ingresar un ciudadano a un programa (via derivación o inscripción directa) e iniciar su flujo obligatorio para gestionar su proceso de admisión hasta el cierre | Grande 🟡 | Dos caminos de entrada: derivación (cualquier operador) o inscripción directa (solo gestores del programa). Ambos inician el flujo completo. Pendiente `/definir derivacion-e-inscripcion` antes de estimar |
| US-013 | Como operador quiero poder buscar un ciudadano por nombre o DNI de forma rápida para atender consultas telefónicas sin demoras | Pequeño 🟡 | Búsqueda por nombre parcial y DNI exacto |
| US-014 | Como usuario con rol `ConfiguracionPrograma` quiero configurar cupo máximo y lista de espera en un programa para controlar la capacidad de inscripciones simultáneas | Pequeño 🟡 | Campo `cupo_maximo` (opcional) y `tiene_lista_espera` en la config del programa. Incluir en US-005 (wizard) |
| US-015 | Como ciudadano quiero ver mis programas, inscribirme, solicitar turnos y chatear con un operador desde el portal | Grande 🟡 | Iteraciones 2-6 del portal ciudadano (ya planificadas). Ver `docs/funcionalidades/portal-ciudadano/v1.0` |
| US-016 | Como organismo quiero que todas las acciones del sistema queden trazadas (quién hizo qué, cuándo y sobre qué entidad) para cumplir con los requisitos de auditoría estatal | Grande 🟡 | Auditoría transversal — aplica a inscripciones, derivaciones, cambios de estado, turnos, configuraciones |
| US-017 | Como operador quiero dar de baja a un ciudadano de un programa persistente registrando motivo y fecha para cerrar su caso formalmente | Pequeño 🟡 | Botón de baja con campo motivo obligatorio. Cancela turnos pendientes y suspende flujo activo |

---

## Completadas

| ID | User Story | Complejidad |
|----|-----------|-------------|
| US-001 | Como operador quiero registrar y gestionar ciudadanos (alta via RENAPER o manual, edición, búsqueda) para poder abrirles legajos e inscribirlos en programas | Mediano ✅ |
| US-002 | Como profesional quiero gestionar el legajo de atención SEDRONAR de un ciudadano (evaluación inicial, plan de intervención, seguimientos, derivaciones, eventos críticos) | Grande ✅ |
| US-003 | Como operador quiero gestionar el sistema de turnos configurable (ConfiguracionTurnos, disponibilidades, agenda, bandeja de pendientes, aprobación/rechazo) | Grande ✅ |
| US-004-PREV | Como ciudadano quiero acceder al portal para ver mis programas, solicitar turnos y contactar un operador via chat | Grande ✅ |
| US-005-PREV | Como operador quiero gestionar conversaciones con ciudadanos en tiempo real via WebSocket | Mediano ✅ |

---

## Pendiente de /definir antes de poder estimar

| Dominio | Por qué no tiene US todavía |
|---------|----------------------------|
| Instituciones | Solo definidas a nivel flujo de aprobación. Falta definir qué gestiona internamente |
| Actividades | Completamente indefinidas — ¿son parte de instituciones o de programas? Bloquea US-009 |
| Roles y permisos | Mapa completo del sistema sin cerrar — hay roles sueltos definidos por dominio |
| Derivación e inscripción | Flujo completo definido conceptualmente pero sin criterios de aceptación |
| App móvil | Existe pero sin documentar — cómo se conecta, auth, usuarios propios |
| Alertas | Sistema general sin definir — qué las genera, quién las recibe, cómo se resuelven |

---

## Ideas sin refinar

_Acá van las ideas crudas antes de convertirlas en user stories._
