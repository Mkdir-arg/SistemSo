# Comando /comandos

Muestra la lista completa de comandos disponibles con descripcion y ejemplo de uso.

## Instrucciones para el agente

Cuando el usuario ejecuta `/comandos`, mostrar exactamente esto:

---

## Comandos disponibles

### /feature
Implementa una nueva funcionalidad siguiendo el flujo completo: Product Owner → Arquitecto → Desarrollador → Reviewer → Documentador.
Los agentes se activan automaticamente. Solo se te consulta para aprobar cada fase.

**Cuando usarlo:** nueva funcionalidad, mejora o expansion de algo existente.

**Ejemplo:**
```
/feature agregar exportacion de legajos a PDF con filtro por fecha
```

---

### /fix
Corrige un bug encontrado en desarrollo o staging. Flujo corto: Diagnostico → Fix → Revision → Documentacion.
Sin user story, directo al problema.

**Cuando usarlo:** algo no funciona como deberia, pero no es urgente ni esta en produccion.

**Ejemplo:**
```
/fix el formulario de derivaciones no guarda cuando el campo observaciones esta vacio
```

---

### /hotfix
Correccion urgente para un problema critico en produccion. Flujo minimo con un solo checkpoint.
Genera automaticamente el checklist de deploy.

**Cuando usarlo:** produccion caida, error que afecta a usuarios reales, urgencia alta.

**Ejemplo:**
```
/hotfix error 500 en el listado de ciudadanos desde las 14hs, afecta a todos los usuarios
```

---

### /sprint-plan
Planifica el sprint de la semana. Lee el backlog, propone que items incluir segun prioridad y complejidad, y genera el `current-sprint.md`.

**Cuando usarlo:** inicio de semana o inicio de nuevo sprint.

**Ejemplo:**
```
/sprint-plan
```

---

### /sprint-review
Cierra el sprint actual. Revisa que se completo, que quedo pendiente, y genera el resumen de la semana.

**Cuando usarlo:** fin de sprint, antes de planificar el siguiente.

**Ejemplo:**
```
/sprint-review
```

---

### /status
Muestra el estado actual del proyecto: sprint activo, items en progreso, ultimo cambio por modulo, y deuda tecnica pendiente.

**Cuando usarlo:** para tener un panorama rapido antes de arrancar a trabajar.

**Ejemplo:**
```
/status
```

---

### /comandos
Muestra esta lista.

**Ejemplo:**
```
/comandos
```

---

## Flujo tipico de una semana

```
Lunes    → /sprint-plan
Martes   → /feature [nueva funcionalidad]
Miercoles→ /fix [bug encontrado durante desarrollo]
Viernes  → /sprint-review
```

Si hay una urgencia en produccion en cualquier momento:
```
           /hotfix [descripcion del problema]
```
