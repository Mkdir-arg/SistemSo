# Contexto Funcional del Proyecto

> **Regla:** El Analista Funcional lee este documento ANTES de escribir cualquier user story.
> **Regla:** El Documentador actualiza este documento al cierre de cada Fase 5.
> Última actualización: 2026-03-13

---

## Qué es el sistema

SistemSo es una plataforma de gestión social municipal. Permite a organismos de gobierno (SEDRONAR y similares) gestionar ciudadanos en situación de vulnerabilidad, sus legajos de atención, inscripciones a programas sociales, derivaciones entre instituciones, y turnos.

---

## Actores del sistema

| Actor | Quién es | Qué hace |
|-------|----------|---------|
| **Operador backoffice** | Empleado del organismo | Gestiona legajos, conversaciones, turnos, derivaciones |
| **Profesional** | Psicólogo, trabajador social, etc. | Lleva legajos de atención, planes de intervención, seguimientos |
| **Administrador** | Rol técnico/supervisor | Configura el sistema, aprueba instituciones, gestiona usuarios |
| **Ciudadano** | Persona en situación de vulnerabilidad | Accede al portal para turnos, ver sus programas, hacer consultas |
| **Encargado de Institución** | Representante de una ONG/organismo | Registra su institución, ve el estado del trámite |

---

## Reglas de negocio confirmadas

> Estas decisiones fueron tomadas y NO deben cuestionarse sin revisión explícita del usuario.

### Ciudadanos
- Se identifican por **DNI** (campo único en el sistema)
- La identidad se verifica contra **RENAPER** en el registro del portal ciudadano
- Un ciudadano puede tener legajos en múltiples programas simultáneamente
- Un ciudadano puede estar en múltiples instituciones

### Instituciones
- Pasan por un flujo de aprobación: BORRADOR → ENVIADO → REVISION → APROBADO/RECHAZADO
- Solo instituciones APROBADAS pueden ofrecer servicios activos
- Tipos: DTC, CAAC, CCC, CAI, IC, CT (según clasificación SEDRONAR)
- Una institución puede tener múltiples encargados (ManyToMany con User)

### Programas sociales
- Catálogo unificado: sirve tanto para ciudadanos como para instituciones
- Un ciudadano se inscribe a un programa → `InscripcionPrograma`
- Las derivaciones entre programas generan una `DerivacionPrograma`
- Estados de inscripción: PENDIENTE → ACTIVO / EN_SEGUIMIENTO → CERRADO / SUSPENDIDO

### Turnos
- Los turnos son configurables por entidad (Programa, Institución, Actividad)
- `ConfiguracionTurnos` es el modelo nuevo (v2). `RecursoTurnos` es legacy (v1) — coexisten
- Modos: AUTO (ciudadano elige), MANUAL (operador asigna), AMBOS
- Cuando `requiere_aprobacion=True` el turno nace en estado PENDIENTE
- Cuando `requiere_aprobacion=False` el turno nace directamente en CONFIRMADO
- Un turno cancelado por el sistema notifica al ciudadano por email (best-effort)

### Conversaciones
- Un ciudadano puede iniciar una conversación desde el portal
- El sistema intenta asignación automática a un operador
- Las conversaciones tienen WebSocket en tiempo real
- Estados: activa → cerrada

### ÑACHEC
- Es un programa específico con su propio modelo de legajo (`CasoNachec`)
- Tiene lógica de evaluación de vulnerabilidad propia
- Se gestiona separado del legajo de atención estándar

---

## Preguntas abiertas sin resolver

> El Analista Funcional debe responder estas preguntas ANTES de diseñar features relacionadas.

- [ ] ¿Los programas sociales tienen fecha de vencimiento? ¿O son indefinidos?
- [ ] ¿Un turno puede reprogramarse o solo cancelarse y crear uno nuevo?
- [ ] ¿Qué pasa con los turnos si se desactiva una institución? ¿Se cancelan en cascada?
- [ ] ¿El ciudadano recibe notificación cuando es derivado a otro programa?
- [ ] ¿Los operadores pueden ver legajos de cualquier ciudadano o solo los asignados a su institución?
- [ ] ¿Existe un concepto de "guardia" o atención urgente fuera del sistema de turnos?
- [ ] ¿El toggle "requiere turno" en Programa/Institución/Actividad — lo activa solo el Admin o también el Operador?

---

## Lo que el usuario NO pidió pero podría necesitar

> El Analista debe tener esto en mente para proponer mejoras en el momento oportuno.

- Recordatorios automáticos 24hs antes de un turno (Celery/cron — deuda pendiente)
- Notificaciones push / WhatsApp (no solo email)
- Vista mensual de agenda de turnos (hoy solo hay vista diaria)
- Exportación a PDF del legajo de atención
- Estadísticas de asistencia a turnos (ausentismo)
- App mobile para operadores de campo
- Integración con sistema de expedientes municipales

---

## Contexto de sesiones anteriores

> El Analista actualiza esta sección al final de cada sesión importante.

### 2026-03-09
- Se diseñó e implementó el sistema de turnos configurables (backoffice completo)
- Se definió que los turnos pueden originarse desde: portal genérico, programa, institución, actividad, derivación, legajo de atención, backoffice por teléfono
- Se aprobó la coexistencia de `RecursoTurnos` (legacy) y `ConfiguracionTurnos` (nuevo)
- Se creó la app `turnos/` separada de `portal/` por razones de separación de responsabilidades
- Se documentaron 17 funcionalidades del sistema en `docs/funcionalidades/`
- Se agregó la burbuja de mejora automática al CLAUDE.md

### 2026-03-13
- Se ejecutó el primer slice del refactor interno de DX sobre `users`, `portal` institucional y `turnos`
- El registro institucional público dejó de depender de FBVs con POST raw y se migró a `FormView` + services/selectors
- La administración de usuarios movió persistencia de grupos y `Profile` fuera de los forms
- El backoffice de turnos separó lecturas reutilizables (`selectors_turnos`) y acciones de negocio (`services_turnos`)
- No se modificaron reglas de negocio ni modelos; el objetivo fue reducir acoplamiento y preparar una base más testeable para siguientes features
- Se ejecutó el segundo slice del refactor DX sobre `configuracion`, focalizado en detalle institucional, detalle de actividad, staff, derivaciones e inscriptos
- Los flujos operativos del módulo dejaron de depender de `POST` raw en las pantallas principales y pasaron a forms explícitos más services transaccionales
- No se alteraron reglas de negocio institucionales ni estados funcionales; el cambio fue estructural para mejorar mantenibilidad y testabilidad
- Se ejecutó el tercer slice del refactor DX sobre `legajos`, acotado a ciudadanos y admisión
- El flujo de RENAPER y el wizard de admisión dejaron de repartir manejo de sesión y orquestación en múltiples views
- La carga manual del ciudadano quedó separada del formulario de confirmación RENAPER, corrigiendo una inconsistencia de UI con el campo DNI
- Se ejecutó el cuarto slice del refactor DX sobre `legajos`, enfocado en legajo de atención, evaluación, planes, seguimientos, derivaciones y cierre/reapertura
- La edición del plan de intervención dejó de depender de inputs hardcodeados que ignoraban los datos existentes
- Las acciones clínicas base del legajo ahora comparten services/selectors reutilizables y forms más acotados a validación/mapeo
- Se ejecutó el quinto slice del refactor DX sobre `legajos`, enfocado en eventos críticos, reportes, exportación y cambio de responsable
- Los templates clínicos dejaron de referenciar campos inexistentes del dominio y ahora reflejan la estructura real de los modelos
- Reportes y acciones AJAX del módulo ya no concentran orquestación inline en `views.py`
- Se ejecutó el sexto slice del refactor DX sobre `legajos`, enfocado en separar físicamente las views por dominios
- `legajos/views.py` quedó como fachada compatible y el código se repartió entre `views_ciudadanos.py` y `views_clinico.py`
- El cambio no altera rutas ni comportamiento funcional, pero reduce fricción para futuros refactors y tests del módulo
- Se ejecutó el séptimo slice del refactor DX sobre `legajos`, enfocado en completar la modularización física de las views
- La operativa institucional y de actividades pasó a `views_operativa.py` y `legajos/views.py` quedó como fachada pura de compatibilidad
- El cambio tampoco altera reglas funcionales ni rutas, pero deja el módulo listo para seguir atacando deuda por subdominio en lugar de por archivo monolítico
- Se ejecutó el octavo slice del refactor DX sobre `conversaciones`, enfocado en separar chat público, backoffice, métricas y orquestación
- El módulo dejó de concentrar parsing manual de payloads y queries repetidas en un solo `views.py`; ahora usa selectors, services y forms livianos sin cambiar las URLs
- Se mantuvo explícitamente el contrato actual del chat y los endpoints AJAX/WebSocket legacy para no introducir regresiones funcionales en el frontend
- Se ejecutó el noveno slice del refactor DX sobre `conversaciones`, enfocado en alinear la API auxiliar de alertas y detalle en vivo
- Las APIs internas del chat ya no repiten permisos, queries ni marcado de mensajes leídos por fuera de la nueva capa del módulo
- El comportamiento visible no cambió; el beneficio fue coherencia interna y menor costo de mantenimiento
- Se ejecutó el décimo slice del refactor DX sobre `configuracion`, enfocado en modularización física de las views
- La app dejó de concentrar geografía, institucional y actividades en un solo `views.py`; ahora usa módulos por dominio con una fachada compatible
- Tampoco hubo cambios funcionales visibles; el valor del corte fue bajar el costo cognitivo y alinear la estructura interna con el resto del refactor
- Se ejecutó el undécimo slice del refactor DX sobre URLs y namespaces raíz del proyecto
- `users`, `core` y `healthcheck` ya exponen namespaces consistentes sin retirar todavía los names legacy
- El cambio fue deliberadamente incremental para evitar una rotura transversal en templates y `reverse()`
- Se ejecutó el duodécimo slice del refactor DX sobre consumidores de URLs
- Varias pantallas internas ya consumen `core:*` y `users:*` en lugar de names legacy sin namespace
- Se dejó autenticación fuera de este corte porque `login/logout` requieren una decisión más cuidadosa por convivencia con Django auth
- Se ejecutó el decimotercer slice del refactor DX sobre `chatbot`
- El módulo ya no mezcla chat de usuario y panel administrativo en un solo `views.py`, y valida payloads JSON con forms livianos
- El comportamiento visible no cambió; el objetivo fue bajar acoplamiento y preparar mejor base para futuras mejoras del bot
- Se ejecutó el decimocuarto slice del refactor DX sobre `chatbot`, enfocado en alinear el contrato real entre frontend y backend
- El chat del bot ya no depende de rutas hardcodeadas inconsistentes ni de `@csrf_exempt` en sus endpoints principales
- Además se agregaron tests para cubrir el shape de respuesta esperado por el frontend y el enforcement de CSRF
- Se ejecutó el decimoquinto slice del refactor DX sobre `conversaciones`, enfocado en el contrato real del chat ciudadano y operador
- La evaluación del ciudadano volvió al dominio público real de la funcionalidad y dejó de chocar con una vista protegida de backoffice
- Los POST JSON del chat ya no dependen de `@csrf_exempt`; ahora usan URLs renderizadas por Django y cabecera CSRF explícita
- Se ejecutó el decimosexto slice del refactor DX sobre `conversaciones`, enfocado en la lista en vivo del backoffice
- La pantalla dejó de cargar dos veces el runtime WebSocket de lista y ya no depende de URLs hardcodeadas para refrescar detalle/cierre
- El comportamiento visible no cambió, pero baja el riesgo de conexiones duplicadas y facilita la migración de rutas
- Se ejecutó el decimoséptimo slice del refactor DX sobre `conversaciones`, enfocado en consumidores residuales del módulo fuera de su lista principal
- Los scripts globales de alertas/estadísticas y algunos consumidores en portal/backoffice ya no embeben rutas de `conversaciones` en archivos estáticos
- El comportamiento visible tampoco cambió, pero el módulo quedó más coherente transversalmente y con menos acoplamiento a paths fijos
- Se ejecutó el decimoctavo slice del refactor DX sobre `portal`, enfocado en consultas ciudadanas
- La parte de consultas salió de `portal/views_ciudadano.py` y ahora usa forms, selectors y services dedicados
- El flujo visible no cambió, pero ahora valida mejor los POST, fija ownership de conversaciones en un único lugar y suma tests del dominio
- Se ejecutó el decimonoveno slice del refactor DX sobre `portal`, enfocado en turnos ciudadanos
- La parte de turnos salió de `portal/views_ciudadano.py` y ahora usa forms, selectors y services dedicados
- El flujo visible no cambió, pero ahora valida la confirmación con formularios Django y encapsula disponibilidad, reserva y cancelación en una capa reutilizable
- Se ejecutó el vigésimo slice del refactor DX sobre `portal`, enfocado en autenticación y registro ciudadano
- El login y el alta por pasos ya no viven dentro de `portal/views_ciudadano.py`; ahora usan un módulo de vistas propio y un service de auth/registro
- El comportamiento visible no cambió, pero quedó aislada la lógica de throttling por IP, sesión de registro y creación/vinculación de cuentas ciudadanas
- Se ejecutó el vigésimo primer slice del refactor DX sobre `portal`, enfocado en perfil, programas y mis datos
- El resto del perfil ciudadano salió de `portal/views_ciudadano.py` y ahora vive en `views_ciudadano_perfil.py`, con selectors y services propios
- El comportamiento visible no cambió, pero el archivo histórico del portal ciudadano quedó reducido a una fachada de compatibilidad
- Se ejecutó el vigésimo segundo slice del refactor DX sobre `ÑACHEC`, enfocado en prestaciones, cierre/reapertura y dashboard
- `legajos/views_nachec.py` dejó de concentrar esos bloques y ahora funciona parcialmente como fachada compatible
- El comportamiento visible no cambió, pero el hotspot principal del módulo bajó de tamaño antes de entrar en validación, relevamiento y evaluación
- Se ejecutó el vigésimo tercer slice del refactor DX sobre `ÑACHEC`, enfocado en evaluación y activación de plan
- La evaluación profesional, la ampliación/rechazo y la activación del plan ahora viven en `views_nachec_decisiones.py`
- El comportamiento visible no cambió, pero `legajos/views_nachec.py` quedó por debajo de las 1000 líneas antes de atacar asignación y relevamiento
- Se ejecutó el vigésimo cuarto slice del refactor DX sobre `ÑACHEC`, enfocado en la operación territorial restante
- Validación, asignación, reasignación, relevamiento y evidencias ahora viven en `views_nachec_operacion.py`
- El comportamiento visible no cambió, pero `legajos/views_nachec.py` quedó finalmente como fachada pura y el hotspot principal de `ÑACHEC` dejó de concentrar la implementación real

---

## Glosario del negocio

| Término | Definición |
|---------|-----------|
| **Legajo** | Expediente de un ciudadano en el sistema |
| **Legajo de atención** | Seguimiento clínico/social de un ciudadano por un profesional |
| **Derivación** | Transferencia de un ciudadano de un programa/institución a otro |
| **Inscripción** | Alta de un ciudadano en un programa social |
| **Recurso de turnos** | Entidad que ofrece slots de atención (legacy: `RecursoTurnos`) |
| **Configuración de turnos** | Nueva entidad configurable que reemplaza el recurso (v2) |
| **NODO** | Institución de la red SEDRONAR que funciona como punto territorial |
| **ÑACHEC** | Programa específico de la red con lógica de evaluación propia |
| **Backoffice** | Interfaz interna para operadores y profesionales (no pública) |
| **Portal ciudadano** | Interfaz pública para ciudadanos (`/portal/mi-perfil/`) |
