# Contexto Funcional del Proyecto

> **Regla:** El Analista Funcional lee este documento ANTES de escribir cualquier user story.
> **Regla:** El Documentador actualiza este documento al cierre de cada Fase 5.
> Última actualización: 2026-03-12 (sesión 6 — /definir derivacion-e-inscripcion)

---

## Qué es el sistema

SistemSo es un sistema de gestión estatal. Permite a organismos de gobierno gestionar ciudadanos, programas sociales e instituciones. Tiene dos superficies: el **backoffice** (para operadores y profesionales del estado) y el **portal ciudadano** (acceso público para el ciudadano).

Los tres dominios centrales son:
- **Ciudadanos** — toda la información del ciudadano trazada: programas, ayudas, grupo familiar, domicilio, historial
- **Programas** — procesos configurables con flujos, capacidades activables y ciclo de vida propio
- **Instituciones** — entidades que brindan servicios al estado, puntos donde se dan las actividades de los programas

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

### Búsqueda de ciudadanos
- Los operadores pueden buscar ciudadanos por **nombre** (parcial) o por **DNI**
- La búsqueda debe ser suficientemente rápida para ser usada durante una atención telefónica

### Ciudadanos
- Se identifican por **DNI** (campo único en el sistema) — no puede haber dos registros del mismo ciudadano
- La identidad se verifica contra **RENAPER** (DNI + sexo) en el registro desde el portal ciudadano
- Alta también disponible de forma manual cuando RENAPER no está disponible
- Un ciudadano puede estar inscripto en múltiples programas simultáneamente
- Un ciudadano puede estar en múltiples instituciones

#### Información registrada en la ficha del ciudadano
- **Datos básicos:** DNI, nombre, apellido, fecha nacimiento, género, teléfono, email, domicilio, provincia, municipio, foto
- **Grupo familiar** (ya implementado)
- **Situación habitacional:** tipo de vivienda, tenencia, condiciones
- **Situación laboral / económica:** situación laboral, ingreso estimado, obra social
- **Nivel educativo**
- **Cobertura médica / medicación habitual** *(campo sensible — requiere `ciudadanoSensible`)*
- **Documentación:** DNI físico, estado RENAPER, estado migratorio *(campo sensible)*
- **Observaciones / notas libres**

#### Hub del ciudadano `/legajos/ciudadanos/<id>/`
El perfil del ciudadano es el centro de toda su información. Tiene solapas estáticas y dinámicas con badge behavior:

| Solapa | Tipo | Qué muestra |
|--------|------|-------------|
| Resumen | Estática | Vista general del ciudadano |
| Cursos y Actividades | Estática | Historial de actividades en instituciones |
| Red Familiar | Estática | Grupo familiar |
| Archivos | Estática | Documentos adjuntos |
| Programas | Dinámica | Programas en los que está inscripto |
| Turnos | Dinámica | Turnos asignados |
| Instituciones | Dinámica | Instituciones donde fue atendido |
| Conversaciones | Dinámica | Consultas y chat con operadores |
| Derivaciones | Dinámica | Historial de derivaciones |
| Alertas | Dinámica | Alertas activas |
| Línea de tiempo | Dinámica | Todo lo que pasó cronológicamente |

**Comportamiento de solapas:** contador numérico en cada tab · las dinámicas se ocultan si no tienen datos · indicador visual si hay algo que requiere atención

#### Roles del ciudadano
| Rol | Qué permite |
|-----|------------|
| `ciudadanoVer` | Ver la ficha completa (sin campos sensibles) |
| `ciudadanoCrear` | Crear y editar ciudadanos |
| `ciudadanoSensible` | Acceder a campos de salud, documentación migratoria y campos marcados como sensibles |

#### Acceso por ámbito
- Operador de **institución** → ve solo ciudadanos que pasaron por esa institución
- Operador de **programa / backoffice** → ve todos los ciudadanos, gestiona solo los de su ámbito

#### Confidencialidad en dos capas
- Campos de salud y documentación migratoria → sensibles por defecto (requieren `ciudadanoSensible`)
- El operador puede marcar campos adicionales como sensibles al cargar el ciudadano

### Instituciones
- Pasan por un flujo de aprobación: BORRADOR → ENVIADO → REVISION → APROBADO/RECHAZADO
- Solo instituciones APROBADAS pueden ofrecer servicios activos
- Tipos: DTC, CAAC, CCC, CAI, IC, CT (según clasificación SEDRONAR)
- Una institución puede tener múltiples encargados (ManyToMany con User)
- Una institución puede tener su propia `ConfiguracionTurnos` (OneToOne)
- Cada institución tiene un **legajo institucional** con: personal, evaluaciones periódicas, planes de fortalecimiento (actividades) e indicadores de monitoreo
- Una institución puede estar habilitada para ejecutar múltiples programas (`InstitucionPrograma`)

#### Roles de institución — backoffice
| Rol | Qué permite |
|-----|------------|
| `institucionVer` | Ver el catálogo de instituciones y sus datos |
| `institucionAdministrar` | Crear, editar, aprobar/rechazar instituciones |

#### Roles internos del panel institución
| Rol | Qué permite |
|-----|------------|
| `EncargadoInstitucion` | Acceso total al panel + gestionar usuarios internos (crear/eliminar administrativos y profesores) + único que puede solicitar revisión o reactivación |
| `AdministrativoInstitucion` | Configura actividades, asigna profesores, ve turnos — no puede gestionar usuarios |
| `ProfesorInstitucion` | Toma asistencia en actividades, se asigna a actividades — ve nombre, foto y contacto básico del ciudadano (sin ficha completa ni campos sensibles) |

#### Panel institución — tercera superficie del sistema
- URL: `/institucion/` — superficie propia con middleware y base template separados
- Mismo sistema de login Django — el sistema detecta el rol y redirige automáticamente al panel institución
- Patrón arquitectónico idéntico al portal ciudadano (`portal/`)
- Los tres roles (`EncargadoInstitucion`, `AdministrativoInstitucion`, `ProfesorInstitucion`) acceden exclusivamente a esta superficie

#### Reactivación de institución RECHAZADA
- Una institución RECHAZADA puede solicitar reactivación
- La puede iniciar la propia institución desde su panel (botón "Solicitar reactivación") **o** el backoffice la inicia y notifica a la institución
- El proceso se guarda como `REACTIVACION` — historial diferenciado de la aprobación original
- La institución recibe notificación informando que es un proceso de reactivación, no una aprobación nueva

#### Evaluaciones periódicas a instituciones
- Son **tareas territoriales aplicadas a instituciones** — mismo mecanismo que las tareas del motor de flujos
- Las crean los administradores del programa desde el backoffice
- Se asignan a un operador territorial que las completa desde la **app de campo (móvil)**
- El resultado queda vinculado al legajo de la institución evaluada
- **Prerequisitos:** motor de flujos (US-006) + app móvil definida y operativa

#### Indicadores de monitoreo
- Métricas internas de la institución: alumnos activos, profesores, actividades en curso, turnos agendados

### Actividades institucionales

- Una actividad **siempre pertenece a una institución** — no existen actividades sin institución
- Las actividades viven en el legajo institucional como `PlanFortalecimiento`
- Tipos: `PREVENCION`, `TRATAMIENTO`, `REDUCCION_RIESGO`, `REINSERCION`, `CAPACITACION`
- Una actividad puede tener su propia `ConfiguracionTurnos` para ofrecer turnos propios
- Un ciudadano puede estar inscripto en **múltiples actividades simultáneamente**

#### Tipos de acceso a una actividad

| Tipo | Descripción | Quién puede inscribir |
|------|-------------|----------------------|
| **LIBRE** | Actividad abierta | El ciudadano desde el portal, o cualquier operador/encargado |
| **REQUIERE_PROGRAMA** | Solo para inscriptos en un programa específico | Solo operadores que gestionen ese programa o encargados de la institución |

**Campo en `PlanFortalecimiento`:** `tipo_acceso = LIBRE | REQUIERE_PROGRAMA`. Si es `REQUIERE_PROGRAMA`, FK al `Programa` asociado.

#### Cupo y lista de espera

- El cupo máximo es **opcional** — se configura al crear la actividad
- La lista de espera es **opcional** — se configura junto con el cupo
- Cuando se libera un cupo con lista de espera activa, hay dos modos (configurable):
  - **Automático**: se asigna al siguiente en la lista sin intervención
  - **Manual**: el operador elige quién de la lista ocupa el lugar

#### Fechas de la actividad

- Fecha de inicio y fecha de fin son **opcionales**
- Si se configura fecha de fin y se llega a ella → todos los ciudadanos `ACTIVO` pasan automáticamente a `FINALIZADO`

#### Clases (entidad dentro de la actividad)

- Una actividad se organiza en **clases** — entidades con: fecha, hora de inicio, duración y título opcional
- Las clases son creadas con anticipación por el staff o el encargado de la institución
- La asistencia se registra **por clase** — valores: `PRESENTE / AUSENTE / JUSTIFICADO / TARDANZA`
- Pueden registrar asistencia: el **staff asignado a la actividad** + el **encargado de la institución**

#### Inscripción a una actividad

El ciudadano queda en `InscriptoActividad` con estados:

| Estado | Cómo se llega |
|--------|--------------|
| `INSCRITO` | Al inscribirse, antes de la primera clase |
| `ACTIVO` | Al comenzar a participar |
| `FINALIZADO` | Automático al llegar la fecha fin de la actividad, o manual si el staff lo marca como completado satisfactoriamente |
| `ABANDONADO` | Manual por operador/staff, o auto-desinscripción del ciudadano desde el portal |

**Al inscribirse:** el ciudadano recibe un **código de inscripción** como confirmación y lo ve en su perfil del portal.

**Al abandonar:** los turnos pendientes de la actividad se cancelan y los slots vuelven a estar disponibles.

#### Staff de la actividad

- Se crea y gestiona desde la solapa de gestión dentro de la institución
- Se asigna a una actividad específica desde dentro de la actividad misma
- Solo el staff asignado + el encargado de la institución pueden registrar asistencia

#### Vista del ciudadano — solapa "Cursos y Actividades"

La tarjeta de cada actividad muestra: **nombre, institución, estado, próxima clase, asistencia acumulada**.
Incluye tanto actividades activas como historial completo.
El ciudadano también puede ver su **porcentaje de asistencia** desde el portal.

### Derivaciones

Actualmente existen dos modelos de derivación en el sistema que **se unificarán** (US-021):

| Modelo | Estado | Origen | Destino |
|--------|--------|--------|---------|
| `Derivacion` | Legacy — deprecar | `LegajoAtencion` SEDRONAR | Institución + Actividad opcional |
| `DerivacionInstitucional` | Nuevo | `Ciudadano` | `InstitucionPrograma` (institución + programa) |

**Decisión tomada:** unificar en un solo modelo que sale desde `Ciudadano`. La `Derivacion` legacy se depreca cuando `LegajoAtencion` migre al motor de flujos (US-006).

El modelo unificado tendrá:
- Origen: `Ciudadano`
- Destino: puede ser `InstitucionPrograma` (ciudadano va a programa en institución) o `PlanFortalecimiento` (ciudadano va a actividad específica)
- `tipo_inicio`: `DERIVACION` (cualquier operador) | `INSCRIPCION_DIRECTA` (solo gestores del programa destino)
- Estados: `PENDIENTE` → `ACEPTADA` / `RECHAZADA`
- Urgencia: `BAJA` / `MEDIA` / `ALTA`
- Campos: motivo, respuesta, quién deriva, quién responde, fecha respuesta
- Sin vencimiento: las derivaciones PENDIENTE quedan indefinidamente hasta que el operador destino actúe

#### Quién acepta una derivación
El **operador del programa destino** acepta o rechaza manualmente. No hay aceptación automática.

#### Notificaciones
- **Operador destino:** recibe badge + alerta en bandeja cuando llega una derivación nueva
- **Ciudadano:** no recibe notificación activa. Lo puede ver en su portal, sección Programas

#### Reglas de validación (se verifican antes de crear la derivación)
- ✅ Se puede derivar si la derivación anterior al mismo programa fue RECHAZADA (o el flujo fue rechazado)
- ❌ No se puede derivar si ya existe una derivación PENDIENTE al mismo programa → aviso al operador
- ❌ No se puede derivar si el ciudadano ya está ACTIVO en ese programa → aviso al operador
- ✅ Un ciudadano puede tener derivaciones PENDIENTE a **distintos programas** simultáneamente

#### Ciclo de vida completo
```
[Operador crea derivación — desde perfil ciudadano o desde dashboard de programa]
        ↓
  Derivacion → PENDIENTE
  Operador del programa destino recibe badge + alerta en bandeja
        ↓
  [RECHAZA] → Derivacion = RECHAZADA
              InscripcionPrograma NO se crea
  [ACEPTA]  → Derivacion = ACEPTADA
              InscripcionPrograma creado (estado PENDIENTE)
                    ↓
              Flujo inicia (InstanciaFlujo creada)
                    ↓
              [Si el flujo tiene paso "rechazar" configurado y se rechaza]
              → InstanciaFlujo = RECHAZADO
              → InscripcionPrograma = INACTIVO
              [Si el flujo completa sin rechazo]
              → InscripcionPrograma = ACTIVO
                    ↓
              Cierre automático (un solo acto) | Baja manual (persistente)
```

#### Puntos de entrada en la UI
| Desde | Quién | Comportamiento |
|-------|-------|----------------|
| Perfil del ciudadano `/legajos/ciudadanos/<id>/` | Cualquier operador | Elige destino (programa/institución/actividad) libremente |
| Dashboard del programa | Gestor del programa | Busca ciudadano; origen queda registrado automáticamente como el programa actual |

### Programas sociales
- Catálogo unificado: sirve tanto para ciudadanos como para instituciones
- Todo programa pertenece a una jerarquía organizacional: **Secretaría → Subsecretaría → Programa** (exactamente dos niveles)
- Todo programa tiene un flujo configurable — sin excepción
- Solo usuarios con el rol **`ConfiguracionPrograma`** pueden crear y configurar programas

#### Estados del modelo Programa

```
BORRADOR → ACTIVO → SUSPENDIDO → INACTIVO
```

| Estado | Acepta nuevos ingresos | Inscripciones en curso | Descripción |
|--------|----------------------|----------------------|-------------|
| `BORRADOR` | ❌ | ❌ | Sin flujo configurado |
| `ACTIVO` | ✅ | ✅ | Operativo |
| `SUSPENDIDO` | ❌ | ✅ continúan | Cerrado a nuevos ingresos, los existentes siguen su flujo |
| `INACTIVO` | ❌ | ❌ | Programa cerrado completamente |

#### Naturaleza de un programa
Los programas tienen dos naturalezas con distinto ciclo de vida post-flujo:

| | Un solo acto | Persistente |
|--|--|--|
| Tiene flujo | ✅ | ✅ |
| Post-flujo | Cerrado automáticamente | Sigue abierto hasta baja manual |
| Alimentación continua | ❌ | ✅ según lo que configure el flujo |
| Puede tener turnos | ✅ (activable) | ✅ (activable) |

- **Un solo acto**: el ciudadano atraviesa el flujo completo, se aprueba o no, y el caso cierra automáticamente
- **Persistente**: el ciudadano entra al programa, traversa el flujo, y **permanece activo** hasta que un operador registra la baja. Durante ese tiempo el flujo puede seguir alimentando información

#### Turnos en programas
- **Ambos tipos** de programa pueden tener turnos configurados — la distinción un solo acto / persistente no afecta esta capacidad
- La activación de turnos depende exclusivamente de si el programa tiene `tiene_turnos = True` en su configuración

#### Cupos y lista de espera en programas
- Un programa puede tener **cupo máximo** configurado (cantidad de inscripciones activas simultáneas)
- Si el programa tiene cupo y está lleno, los nuevos ingresos entran a una **lista de espera**
- La lista de espera es opcional — se configura junto con el cupo en la configuración del programa
- Si no tiene cupo configurado, el programa acepta ingresos sin límite

#### Puntos de entrada de un ciudadano a un programa
Hay dos caminos para que un ciudadano ingrese a un programa. Son la **misma acción** con la misma estructura de datos — la diferencia es solo de permiso y punto de origen:

| Camino | Quién lo hace | `tipo_inicio` |
|--------|--------------|-----------|
| **Derivación** | Cualquier operador del backoffice | `DERIVACION` |
| **Inscripción directa** | Solo gestores del programa destino | `INSCRIPCION_DIRECTA` |

**Regla absoluta:** en ambos casos el ciudadano SIEMPRE debe completar el flujo completo. No existe aprobación automática ni salto de pasos.

#### Momento de creación de InscripcionPrograma
`InscripcionPrograma` se crea **al momento de ACEPTAR la derivación** (no al completar el flujo). El flujo corre sobre una inscripción ya existente en estado PENDIENTE.

#### Estados de un ciudadano en un programa — dos capas
1. **Estado general** (de la inscripción): `ACTIVO` / `INACTIVO` / `DADO_DE_BAJA`
2. **Estado del paso actual** (de la instancia de flujo): nombre configurable por el administrador del flujo al definir cada paso — ejemplo: "En evaluación", "En seguimiento", "Pendiente de documentación"

#### Roles dentro de un programa
- Cada paso del flujo tiene un **rol asignado** — solo operadores con ese rol pueden ejecutar ese paso
- Los roles son específicos del programa — cada programa define qué roles existen y qué pasos gestionan
- Ejemplo: paso 1 "Aceptar derivación" → rol `mda` del programa; paso 2 → mismo u otro rol

#### Flujos de programas
- El flujo define completamente el comportamiento del programa: pasos, formularios, evaluaciones, tareas territoriales, roles por paso
- Las **tareas territoriales** son un tipo de nodo dentro del flujo (formulario que se completa en app móvil y vuelve vinculado al ciudadano/caso)
- El motor de flujos se adapta del sistema NODO (backend Django, editor visual React — pendiente de implementación)

### Roles y permisos del sistema

Todos los roles son grupos Django independientes — no existe jerarquía entre ellos. Un usuario puede tener múltiples roles simultáneamente. El Administrador (`is_staff`) puede asignar y quitar roles en cualquier momento.

#### Mapa completo de roles

| Módulo | Rol | Qué permite |
|--------|-----|------------|
| **Ciudadanos** | `ciudadanoVer` | Ver ficha del ciudadano (sin campos sensibles) |
| | `ciudadanoCrear` | Crear y editar ciudadanos |
| | `ciudadanoSensible` | Ver campos de salud, documentación migratoria y campos marcados como sensibles |
| **Instituciones** | `institucionVer` | Ver el catálogo de instituciones y sus datos |
| | `institucionAdministrar` | Crear, editar, aprobar/rechazar instituciones |
| **Programas — configuración** | `secretariaConfigurar` | Crear y editar Secretarías y Subsecretarías |
| | `programaConfigurar` | Crear y configurar programas (wizard, flujo, capacidades) |
| **Programas — operativa** | `programaOperar` | Gestionar inscripciones, derivaciones, seguimiento de ciudadanos en programas |
| **Turnos — configuración** | `turnoConfigurar` | Crear y configurar `ConfiguracionTurnos` (horarios, modos, disponibilidades) |
| **Turnos — operativa** | `turnoOperar` | Gestionar agenda: confirmar, rechazar, cancelar turnos de ciudadanos |
| **Conversaciones** | `conversacionOperar` | Acceder a la bandeja de conversaciones, responder ciudadanos via chat |
| **Dashboard** | `dashboardVer` | Ver el panel de control con métricas e indicadores |
| **Configuración sistema** | `sistemaConfigurar` | Gestionar parámetros globales (email, integraciones, etc.) |
| **Usuarios y roles** | `usuarioAdministrar` | Crear usuarios, asignar y revocar roles |
| **Reportes** | `reportesVer` | Ver y exportar reportes del sistema |

#### Roles especiales (no son grupos Django)

| Rol especial | Naturaleza | Qué permite |
|-------------|-----------|------------|
| `is_superuser` | Flag Django | Acceso total sin restricciones — solo para DevOps/soporte técnico |
| `Ciudadanos` (grupo portal) | Grupo Django | Identifica a los usuarios del portal ciudadano — no acceden al backoffice |
| `EncargadoInstitucion` | Grupo Django | Usuario externo representante de una ONG/organismo — acceso limitado a su institución |

#### Roles renombrados respecto al código existente

| Nombre viejo (en código) | Nombre nuevo (acordado) | Módulo |
|--------------------------|------------------------|--------|
| `configurarSecretaria` | `secretariaConfigurar` | Programas — configuración |
| `ConfiguracionPrograma` | `programaConfigurar` | Programas — configuración |
| `Administradores de Turnos` | `turnoConfigurar` | Turnos — configuración |

> **Nota técnica:** los nombres viejos están en el código actualmente. La migración de nombres se hace como parte de US-011 (data migration de grupos Django).

#### Reglas de acceso

- Un usuario sin ningún rol en el backoffice no puede acceder a ninguna sección
- El portal ciudadano es completamente separado — los usuarios del portal pertenecen al grupo `Ciudadanos`
- `EncargadoInstitucion` accede solo a la vista de su institución — no al backoffice general
- `is_superuser` no es un rol operativo, solo para mantenimiento técnico

---

### Turnos
- Los turnos son configurables por entidad (Programa, Institución, Actividad)
- `ConfiguracionTurnos` es el modelo nuevo (v2). `RecursoTurnos` es legacy (v1) — coexisten
- Modos: AUTO (ciudadano elige), MANUAL (operador asigna), AMBOS
- Cuando `requiere_aprobacion=True` el turno nace en estado PENDIENTE
- Cuando `requiere_aprobacion=False` el turno nace directamente en CONFIRMADO
- Un turno cancelado por el sistema notifica al ciudadano por email (best-effort)

### Portal ciudadano
El portal es la superficie pública para el ciudadano. Está completamente separado del backoffice via middleware. Lo que el ciudadano puede hacer:

| Funcionalidad | Estado |
|--------------|--------|
| Registro y login con email/password | ✅ Implementado (iteración 1) |
| Ver su perfil y datos del legajo | ✅ Implementado (iteración 1) |
| Ver sus programas y estado en cada uno | 🟡 Pendiente (iteración 2) |
| Inscribirse a un programa | 🟡 Pendiente (iteración 2) |
| Solicitar turno online | 🟡 Pendiente (iteración 6) |
| Iniciar chat con un operador | 🟡 Pendiente (iteración 3) |
| Ver sus documentos | 🟡 Pendiente (iteración 4) |
| Recibir notificaciones | 🟡 Pendiente (iteración 5) |

### Conversaciones
- Un ciudadano puede iniciar una conversación desde el portal
- El sistema intenta asignación automática a un operador
- Las conversaciones tienen WebSocket en tiempo real
- Estados: activa → cerrada

### Trazabilidad y auditoría
- **Todo el sistema es trazable** — cada acción queda registrada: quién configuró, quién cambió estado, quién aceptó una derivación, quién dio de baja, qué hizo el ciudadano en el portal
- La auditoría clínica (`AuditoriaEvaluacion`, `AuditoriaCiudadano`) existe y funciona para el módulo SEDRONAR
- La trazabilidad general del sistema (inscripciones, cambios de estado de programas, turnos, derivaciones) debe extenderse al resto de los módulos como parte del diseño de cada feature

#### Baja manual de un ciudadano en un programa persistente
- Se ejecuta mediante un botón explícito desde la vista del ciudadano en el programa
- Registra: quién dio la baja, fecha y hora, motivo (campo obligatorio)
- Al dar la baja: la inscripción pasa a `DADO_DE_BAJA`, el flujo activo se suspende, los turnos pendientes se cancelan
- Solo pueden dar de baja operadores con el rol correspondiente al programa

### ÑACHEC
- Es un programa específico con su propio modelo de legajo (`CasoNachec`)
- Tiene lógica de evaluación de vulnerabilidad propia
- Se gestiona separado del legajo de atención estándar

---

## Preguntas abiertas sin resolver

> El Analista Funcional debe responder estas preguntas ANTES de diseñar features relacionadas.

- [ ] ¿Un turno puede reprogramarse o solo cancelarse y crear uno nuevo?
- [ ] ¿Qué pasa con los turnos si se desactiva una institución? ¿Se cancelan en cascada?
- ~~¿El ciudadano recibe notificación cuando es derivado a otro programa?~~ → Resuelto: no recibe notificación activa, lo ve en su portal sección Programas
- ~~¿Los operadores pueden ver legajos de cualquier ciudadano o solo los asignados a su institución?~~ → Resuelto: depende del ámbito (institución vs. programa)
- [ ] ¿Existe un concepto de "guardia" o atención urgente fuera del sistema de turnos?
- [ ] ¿El operador que marca un campo de ciudadano como "sensible" puede también desmarcarlo, o requiere un rol especial?
- [ ] ¿La foto del ciudadano requiere `ciudadanoSensible` o la ve cualquiera con `ciudadanoVer`?
- [ ] ¿Qué muestra exactamente la solapa "Resumen" del hub ciudadano?
- [ ] ¿El toggle "requiere turno" en un programa persistente — lo activa solo `ConfiguracionPrograma` o también el Operador?
- ~~¿Las actividades son parte de un programa o son entidades independientes?~~ → Resuelto: siempre pertenecen a una institución. Tienen tipo de acceso LIBRE o REQUIERE_PROGRAMA.
- ~~¿La asignación de profesionales a actividades — es uno por muchos?~~ → Resuelto: muchos (StaffActividad con rol_en_actividad)

---

## Lo que el usuario NO pidió pero podría necesitar

> El Analista debe tener esto en mente para proponer mejoras en el momento oportuno.

- Recordatorios automáticos 24hs antes de un turno (Celery/cron — deuda pendiente)
- Notificaciones push / WhatsApp (no solo email)
- Vista mensual de agenda de turnos (hoy solo hay vista diaria)
- Exportación a PDF del legajo de atención
- Estadísticas de asistencia a turnos (ausentismo)
- Integración con sistema de expedientes municipales

## Tareas técnicas futuras documentadas

> Existen como componentes del sistema pero requieren /definir y documentación formal antes de implementar.

- **App móvil** — existe y recibe tareas territoriales completadas por operadores de campo. Devuelve formularios al sistema. Requiere documentar: cómo se conecta (API REST), autenticación, gestión de usuarios propios. Pendiente de `/definir app-movil`.
- **Sistema de alertas** — `AlertaEventoCritico` existe en `LegajoAtencion` pero el sistema de alertas general no está definido. Qué las genera (turno faltado, inscripción vencida, derivación sin respuesta, evento clínico), quién las recibe, cómo se marcan como leídas. Pendiente de `/definir alertas`.

---

## Contexto de sesiones anteriores

> El Analista actualiza esta sección al final de cada sesión importante.

### 2026-03-09 (sesión 1)
- Se diseñó e implementó el sistema de turnos configurables (backoffice completo)
- Se definió que los turnos pueden originarse desde: portal genérico, programa, institución, actividad, derivación, legajo de atención, backoffice por teléfono
- Se aprobó la coexistencia de `RecursoTurnos` (legacy) y `ConfiguracionTurnos` (nuevo)
- Se creó la app `turnos/` separada de `portal/` por razones de separación de responsabilidades
- Se documentaron 17 funcionalidades del sistema en `docs/funcionalidades/`
- Se agregó la burbuja de mejora automática al CLAUDE.md

### 2026-03-09 (sesión 2 — /definir estructura general y programas)
- Se redefinió el propósito del sistema: plataforma de gestión estatal, dos superficies (backoffice / portal ciudadano), tres dominios (ciudadanos, programas, instituciones)
- Se definió la naturaleza de los programas: un solo acto (cierre automático post-flujo) vs. persistente (sigue abierto hasta baja manual)
- Se estableció que todo programa tiene un flujo obligatorio — sin flujo = estado BORRADOR
- Se definió la jerarquía organizacional: Secretaría → Subsecretaría (dos niveles fijos)
- Se definió que las tareas territoriales son un nodo dentro del flujo, no configuración separada
- Se adoptó el motor de flujos del sistema NODO como referencia para implementación futura
- Se estableció el rol `ConfiguracionPrograma` como único autorizado para crear/configurar programas

### 2026-03-09 (sesión 3 — /definir ciudadano y legajo ciudadano)
- Se expandió la ficha del ciudadano: situación habitacional, laboral, educativa, médica, documentación, notas, foto
- Se definió el hub del ciudadano con 4 solapas estáticas + 7 dinámicas con badge behavior
- Se definieron los roles: `ciudadanoVer`, `ciudadanoCrear`, `ciudadanoSensible`
- Se definió el acceso por ámbito: institución ve sus ciudadanos, backoffice ve todos
- Se estableció deuda planificada: `LegajoAtencion` migra al motor de flujos en el futuro
- Se resolvió que el DNI único previene duplicados — no hay proceso de deduplicación manual

### 2026-03-12 (sesión 9 — /definir editor visual de flujos)
- Stack decidido: React Flow + Vite para el editor, Alpine.js para el resto del sistema
- Definidos 10 tipos de nodo: Inicio, Formulario, Evaluación, Condición, Aprobación, Tarea territorial, Email, Espera, Asignación, Fin
- El form builder del nodo Formulario vive en el panel lateral del mismo editor (sin navegación fuera)
- Flujos versionados — instancias en curso no se ven afectadas al publicar nueva versión
- Registrada decisión técnica DT-004 y DT-005 en arquitectura.md

### 2026-03-12 (sesión 8 — /definir instituciones)
- Definida la tercera superficie del sistema: Panel Institución en `/institucion/` con middleware propio
- Definidos tres roles internos: EncargadoInstitucion (todo + usuarios), AdministrativoInstitucion (configuración), ProfesorInstitucion (asistencia)
- Definido flujo de reactivación de institución rechazada (desde panel o desde backoffice)
- Definidas las evaluaciones periódicas: tareas territoriales aplicadas a instituciones via app móvil → legajo institución
- Agregadas US-025, US-026, US-027 al backlog

### 2026-03-12 (sesión 7 — /definir actividades)
- Se definió el flujo completo de inscripción: LIBRE desde portal, REQUIERE_PROGRAMA solo por operador/encargado
- Se definió la entidad Clase (fecha + hora + duración + título opcional) como unidad de asistencia
- Se definieron los cuatro estados del ciudadano en actividad: INSCRITO → ACTIVO → FINALIZADO / ABANDONADO
- Se definió que FINALIZADO ocurre automáticamente al llegar la fecha fin, o manualmente al completar
- Se definió la lista de espera con dos modos: automático y manual (configurable por actividad)
- Se definió código de inscripción como confirmación al ciudadano
- Se definió que el ciudadano ve % de asistencia desde el portal
- Se agregaron US-022, US-023, US-024 al backlog

### 2026-03-12 (sesión 6 — /definir derivacion-e-inscripcion)
- Se cerró el modelo completo de derivación e inscripción directa: son la misma acción, diferente permiso y punto de entrada
- Se definió que `InscripcionPrograma` se crea al ACEPTAR la derivación (no al completar el flujo)
- Se definió que el operador del programa destino acepta/rechaza manualmente (sin automatismo)
- Se definieron las reglas de validación: no si hay PENDIENTE al mismo programa, no si ya está ACTIVO
- Se definieron los dos puntos de entrada UI: perfil ciudadano (cualquier operador) + dashboard del programa (origen automático)
- Se definió que el ciudadano ve sus derivaciones en el portal sección Programas (sin notificación activa)
- Se definió que el operador destino recibe badge + alerta en bandeja al recibir derivación nueva
- Se definió que la cancelación no existe como acción directa — el rechazo ocurre dentro del flujo si se configura

### 2026-03-11 (sesión 5 — análisis instituciones, actividades y derivaciones)
- Confirmado: actividades siempre pertenecen a una institución, nunca son flotantes
- Confirmado: actividades tienen dos tipos de acceso — LIBRE (inscripción directa) y REQUIERE_PROGRAMA (debe estar inscripto en el programa primero)
- Confirmado: los dos modelos de derivación (`Derivacion` legacy y `DerivacionInstitucional`) se unifican en uno solo que sale desde `Ciudadano`
- Detectados bugs de permisos en turnos: `turnoConfigurar` usa nombre viejo, `turnoOperar` no aplicado (documentados en `docs/errores/`)
- Detectado: portal ciudadano de turnos funciona solo con modelo legacy `RecursoTurnos` (documentado en `docs/requerimientos/`)
- Agregadas US-018 a US-021 al backlog: permisos instituciones, panel encargado, tipo_acceso en actividades, unificación derivaciones

### 2026-03-09 (sesión 4 — /definir roles y permisos, mapa completo del sistema)
- Se cerró el mapa completo de roles del sistema: 14 roles operativos + 3 roles especiales
- Roles organizados por módulo: Ciudadanos, Instituciones, Programas (configuración/operativa), Turnos (configuración/operativa), Conversaciones, Dashboard, Configuración sistema, Usuarios y roles, Reportes
- Se acordaron los nombres definitivos en español-técnico (ej: `secretariaConfigurar`, `programaConfigurar`, `turnoConfigurar`) — rompiendo con los nombres mixtos anteriores
- Se confirmó que todos los roles son grupos Django independientes (sin jerarquía entre ellos)
- Se clarificó que el portal ciudadano usa el grupo `Ciudadanos` separado del backoffice
- Se agregó US-011 como prerequisito de todos los features de permisos

---

## Glosario del negocio

| Término | Definición |
|---------|-----------|
| **Ficha del ciudadano** | Perfil central del ciudadano con toda su información social — hub en `/legajos/ciudadanos/<id>/` |
| **Legajo de atención** | ⚠️ Entidad SEDRONAR-específica (deuda técnica). Seguimiento clínico-social — migrará al motor de flujos en el futuro |
| **Inscripción a programa** | Relación entre un ciudadano y un programa — el ciudadano "entra" al programa via `InscripcionPrograma` |
| **Derivación** | Transferencia de un ciudadano de un programa/institución a otro |
| **Inscripción** | Alta de un ciudadano en un programa social |
| **Recurso de turnos** | Entidad que ofrece slots de atención (legacy: `RecursoTurnos`) |
| **Configuración de turnos** | Nueva entidad configurable que reemplaza el recurso (v2) |
| **NODO** | Institución de la red SEDRONAR que funciona como punto territorial |
| **ÑACHEC** | Programa específico de la red con lógica de evaluación propia |
| **Backoffice** | Interfaz interna para operadores y profesionales (no pública) |
| **Portal ciudadano** | Interfaz pública para ciudadanos (`/portal/mi-perfil/`) |
| **Programa de un solo acto** | Programa cuyo ciclo de vida cierra automáticamente al completar el flujo |
| **Programa persistente** | Programa que permanece abierto por tiempo indefinido hasta baja manual explícita |
| **Tarea territorial** | Formulario asignado a un operador de campo, completado en app móvil, vinculado al ciudadano/caso |
| **Flujo de programa** | Secuencia de pasos configurables que define el comportamiento completo de un programa |
| **Secretaría / Subsecretaría** | Jerarquía organizacional a la que pertenece un programa (dos niveles fijos) |
| **programaConfigurar** | Rol (antes `ConfiguracionPrograma`) — permite crear y configurar programas |
| **secretariaConfigurar** | Rol (antes `configurarSecretaria`) — permite crear y editar Secretarías y Subsecretarías |
| **turnoConfigurar** | Rol (antes `Administradores de Turnos`) — permite configurar turnos |
| **programaOperar** | Rol — gestiona inscripciones, derivaciones y seguimiento en programas |
| **turnoOperar** | Rol — gestiona la agenda de turnos (confirmar, rechazar, cancelar) |
| **ciudadanoVer** | Rol que permite ver la ficha del ciudadano (sin campos sensibles) |
| **ciudadanoCrear** | Rol que permite crear y editar ciudadanos |
| **ciudadanoSensible** | Rol que permite acceder a campos de salud, documentación migratoria y campos sensibles |
| **Hub del ciudadano** | Perfil central del ciudadano con todas sus solapas — `/legajos/ciudadanos/<id>/` |
| **Campo sensible** | Campo de la ficha del ciudadano que requiere el rol `ciudadanoSensible` para ser visible |
| **LegajoAtencion** | Entidad clínico-social SEDRONAR-específica — deuda técnica planificada para migrar al motor de flujos |
