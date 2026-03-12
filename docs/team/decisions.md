# Decisiones Técnicas — SistemSo (ADRs)

> Registro de decisiones de arquitectura y negocio tomadas. Nunca se borran — si se revierte una decisión se agrega una nueva entrada.

---

## 2026-03-09 — Programas tienen flujo obligatorio

**Decisión:** Todo programa social tiene un flujo configurable. Sin flujo configurado el programa queda en estado BORRADOR y no puede activarse.

**Motivo:** Unificar el comportamiento de todos los programas bajo un motor de flujos común. Eliminar lógica ad-hoc por tipo de programa.

---

## 2026-03-09 — Jerarquía organizacional fija en dos niveles

**Decisión:** Secretaría → Subsecretaría (exactamente dos niveles). No se puede agregar más niveles.

**Motivo:** Refleja la estructura real del organismo. Evitar complejidad de árbol genérico innecesario.

---

## 2026-03-09 — Naturaleza de programa: un solo acto vs persistente

**Decisión:** Los programas tienen dos naturalezas. "Un solo acto": el caso cierra automáticamente al completar el flujo. "Persistente": el caso permanece abierto hasta baja manual explícita.

**Motivo:** Distintos programas sociales tienen ciclos de vida distintos que no deben forzarse al mismo comportamiento.

---

## 2026-03-09 — Roles como grupos Django independientes sin jerarquía

**Decisión:** Todos los roles son grupos Django. No existe jerarquía entre roles — un usuario puede tener múltiples roles simultáneamente. El administrador (`is_staff`) asigna y revoca roles.

**Motivo:** Flexibilidad operativa. Un operador puede tener simultáneamente `turnoOperar` y `ciudadanoVer` sin que un rol implique al otro.

---

## 2026-03-09 — Motor de flujos basado en sistema NODO

**Decisión:** El motor de flujos del backend se adapta del sistema NODO (Django). El editor visual usa React solo para ese componente, el resto del sistema sigue con Alpine.js.

**Motivo:** El sistema NODO ya tiene un motor de flujos probado en producción. React solo para el editor drag & drop porque Alpine.js no escala para ese caso de uso.

---

## 2026-03-09 — Tareas territoriales como nodo del flujo

**Decisión:** Las tareas territoriales (formularios completados por operadores de campo en app móvil) son un tipo de nodo dentro del flujo de un programa, no una entidad de configuración separada.

**Motivo:** Unifica la lógica de flujos. Evita una entidad paralela que duplique el concepto de "paso del flujo".

---

## 2026-03-11 — Actividades siempre pertenecen a una institución

**Decisión:** Una actividad (`PlanFortalecimiento`) siempre requiere una institución. No existen actividades flotantes sin institución asociada.

**Motivo:** Las actividades son la operativa institucional — representan lo que una institución hace. Sin institución, no hay contexto organizacional para la actividad.

---

## 2026-03-11 — Actividades tienen dos tipos de acceso: libre y por programa

**Decisión:** Una actividad puede ser de acceso **libre** (cualquier ciudadano puede inscribirse directamente) o **requiere programa** (el ciudadano debe estar inscripto en un programa específico primero).

**Campo a agregar:** `tipo_acceso = LIBRE | REQUIERE_PROGRAMA` en `PlanFortalecimiento`. Si es `REQUIERE_PROGRAMA`, FK opcional al `Programa` correspondiente.

**Motivo:** Refleja la realidad operativa: algunas actividades son abiertas a la comunidad, otras son parte del flujo de atención de un programa específico.

---

## 2026-03-11 — Unificación del modelo de Derivación

**Decisión:** Los dos modelos de derivación existentes (`Derivacion` legacy desde `LegajoAtencion`, y `DerivacionInstitucional` desde `Ciudadano`) deben unificarse en un único modelo de derivación.

**Motivo:** Dos modelos paralelos para el mismo concepto generan confusión operativa y duplicación de lógica. Cuando el motor de flujos reemplace `LegajoAtencion`, la `Derivacion` legacy quedaría huérfana de todas formas.

**Plan:** La unificación es parte del diseño del motor de flujos (US-006). El modelo unificado sale desde `Ciudadano`, no desde un legajo específico. La `Derivacion` legacy se depreca cuando `LegajoAtencion` migre al motor de flujos.
