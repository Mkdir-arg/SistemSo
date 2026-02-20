# Sistema de Solapas Dinámicas - Arquitectura y Guía de Implementación

## 📋 Resumen Ejecutivo

Este documento describe la arquitectura del sistema de **solapas dinámicas** para gestionar múltiples programas por ciudadano en el sistema SEDRONAR.

### Concepto Principal
- Un ciudadano puede estar inscrito en **múltiples programas simultáneamente**
- Cada programa aparece como una **solapa dinámica** en el legajo del ciudadano
- Las solapas se crean automáticamente cuando se acepta una **derivación** o se hace una **inscripción directa**
- Cada programa tiene su propia estructura y campos específicos

---

## 🏗️ Arquitectura de Modelos

### 1. Programa (Catálogo)
```python
Programa
├── codigo: "NACHEC", "ECONOMICO", etc.
├── nombre: "ÑACHEC", "Acompañamiento Económico"
├── tipo: Enum de tipos de programa
├── color: Color hex para UI
├── icono: Nombre del icono
├── orden: Orden de visualización
└── configuración: requiere_evaluacion, requiere_plan, etc.
```

### 2. InscripcionPrograma (Relación Ciudadano-Programa)
```python
InscripcionPrograma
├── ciudadano: FK a Ciudadano
├── programa: FK a Programa
├── codigo: Código único de inscripción
├── estado: PENDIENTE, ACTIVO, EN_SEGUIMIENTO, CERRADO
├── via_ingreso: DIRECTO, DERIVACION_INTERNA, DERIVACION_EXTERNA
├── responsable: Usuario responsable
├── legajo_id: UUID del legajo específico del programa
└── fechas: inscripcion, inicio, cierre
```

### 3. DerivacionPrograma (Derivaciones entre Programas)
```python
DerivacionPrograma
├── ciudadano: FK a Ciudadano
├── programa_origen: FK a Programa (nullable)
├── programa_destino: FK a Programa
├── motivo: TextField
├── urgencia: BAJA, MEDIA, ALTA
├── estado: PENDIENTE, ACEPTADA, RECHAZADA
└── inscripcion_creada: FK a InscripcionPrograma (al aceptar)
```

---

## 🔄 Flujo de Trabajo

### Escenario 1: Derivación desde Programa Existente
```
1. Usuario está en Programa A (ej: Acompañamiento SEDRONAR)
2. Profesional crea derivación a Programa B (ej: ÑACHEC)
3. Derivación queda en estado PENDIENTE
4. Responsable de Programa B revisa y ACEPTA
5. Se crea automáticamente InscripcionPrograma
6. Aparece nueva solapa "ÑACHEC" en el legajo del ciudadano
```

### Escenario 2: Derivación Espontánea
```
1. Ciudadano llega directamente a Programa B
2. Se crea derivación sin programa_origen (espontánea)
3. Se acepta y crea InscripcionPrograma
4. Aparece solapa del programa
```

---

## 🎨 Sistema de Solapas

### Solapas Estáticas (Siempre Visibles)
1. **Resumen** - Vista general del ciudadano
2. **Red Familiar** - Contactos y vínculos
3. **Archivos** - Documentos adjuntos

### Solapas Dinámicas (Según Programas Activos)
- Se generan automáticamente por cada InscripcionPrograma activa
- Cada solapa tiene: Nombre, Color, Icono, Badge, Link específico

### Ejemplo Visual
```
┌─────────────────────────────────────────────────────────────┐
│ [Resumen] [Acompañamiento SEDRONAR] [ÑACHEC] [Red Familiar] [Archivos] │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Servicio de Solapas (SolapasService)

### Métodos Principales

- `obtener_solapas_ciudadano(ciudadano)` - Lista completa de solapas
- `obtener_programas_activos(ciudadano)` - Programas activos
- `obtener_programas_disponibles_derivacion(ciudadano)` - Programas para derivar
- `crear_inscripcion_directa(ciudadano, programa, responsable)` - Inscripción directa
- `cerrar_inscripcion(inscripcion, motivo, usuario)` - Cerrar inscripción

---

## 🚀 Archivos Creados

1. **models_programas.py** - Modelos Programa, InscripcionPrograma, DerivacionPrograma
2. **services_solapas.py** - Lógica de negocio para solapas dinámicas
3. **views_solapas.py** - Vistas para gestión de programas y derivaciones
4. **ciudadano_detalle_solapas.html** - Template con solapas dinámicas

---

## 📝 Próximos Pasos

1. Ejecutar migraciones
2. Crear fixture con programa SEDRONAR
3. Migrar legajos existentes a InscripcionPrograma
4. Definir estructura del programa ÑACHEC
5. Desarrollar vistas específicas de ÑACHEC
