# 🎯 Sistema de Solapas Dinámicas - Resumen Ejecutivo

## Concepto

**Un ciudadano puede participar en múltiples programas simultáneamente. Cada programa aparece como una solapa dinámica en su legajo.**

---

## 📐 Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CIUDADANO                                   │
│                     (Juan Pérez - DNI 12345678)                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ tiene múltiples
                                  ▼
        ┌─────────────────────────────────────────────────────┐
        │         INSCRIPCIONES A PROGRAMAS                    │
        └─────────────────────────────────────────────────────┘
                 │                │                │
                 ▼                ▼                ▼
        ┌────────────┐   ┌────────────┐   ┌────────────┐
        │ Programa 1 │   │ Programa 2 │   │ Programa 3 │
        │  SEDRONAR  │   │   ÑACHEC   │   │ ECONÓMICO  │
        │  (Activo)  │   │  (Activo)  │   │ (Cerrado)  │
        └────────────┘   └────────────┘   └────────────┘
             │                 │
             ▼                 ▼
        Solapa visible    Solapa visible
```

---

## 🔄 Flujo de Derivación

```
PASO 1: Crear Derivación
┌──────────────────────────────────────────────────────────┐
│ Profesional en Programa A decide derivar a Programa B    │
│ Estado: PENDIENTE                                         │
└──────────────────────────────────────────────────────────┘
                        ↓
PASO 2: Notificación
┌──────────────────────────────────────────────────────────┐
│ Responsable de Programa B recibe notificación            │
│ Puede: ACEPTAR o RECHAZAR                                │
└──────────────────────────────────────────────────────────┘
                        ↓
PASO 3: Aceptación
┌──────────────────────────────────────────────────────────┐
│ Se crea InscripcionPrograma automáticamente               │
│ Estado: ACTIVO                                            │
└──────────────────────────────────────────────────────────┘
                        ↓
PASO 4: Solapa Dinámica
┌──────────────────────────────────────────────────────────┐
│ Aparece nueva solapa en el legajo del ciudadano          │
│ [Resumen] [SEDRONAR] [ÑACHEC ✨] [Red] [Archivos]       │
└──────────────────────────────────────────────────────────┘
```

---

## 🗂️ Estructura de Solapas

### Vista del Legajo del Ciudadano

```
┌─────────────────────────────────────────────────────────────────┐
│  Juan Pérez - DNI 12345678                    [Derivar] [+]     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────┐ ┌──────────────┐ ┌────────┐ ┌──────────┐ ┌─────────┐│
│  │Resumen│ │Acompañamiento│ │ÑACHEC  │ │Red       │ │Archivos ││
│  │      │ │SEDRONAR      │ │        │ │Familiar  │ │         ││
│  └──────┘ └──────────────┘ └────────┘ └──────────┘ └─────────┘│
│     ▲            ▲              ▲           ▲            ▲      │
│  Estática    Dinámica       Dinámica   Estática    Estática    │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CONTENIDO DE LA SOLAPA ACTIVA                                  │
│                                                                  │
│  [Aquí se muestra el contenido específico del programa]         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Modelos Principales

### 1. Programa (Catálogo)
Define los programas disponibles en el sistema.

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| codigo | Identificador único | "NACHEC" |
| nombre | Nombre visible | "ÑACHEC" |
| color | Color en UI | "#10b981" |
| icono | Icono | "groups" |
| orden | Orden de visualización | 2 |

### 2. InscripcionPrograma
Registra la participación del ciudadano en un programa.

| Campo | Descripción | Valores |
|-------|-------------|---------|
| ciudadano | FK a Ciudadano | - |
| programa | FK a Programa | - |
| estado | Estado actual | ACTIVO, CERRADO |
| via_ingreso | Cómo ingresó | DIRECTO, DERIVACION |
| legajo_id | ID del legajo específico | UUID |

### 3. DerivacionPrograma
Gestiona derivaciones entre programas.

| Campo | Descripción | Valores |
|-------|-------------|---------|
| programa_origen | Desde dónde deriva | Nullable |
| programa_destino | Hacia dónde deriva | Required |
| estado | Estado | PENDIENTE, ACEPTADA |
| urgencia | Prioridad | BAJA, MEDIA, ALTA |

---

## ✅ Ventajas

1. **Escalable**: Agregar nuevos programas es simple
2. **Flexible**: Cada programa tiene su propia estructura
3. **Trazable**: Historial completo de derivaciones
4. **Intuitivo**: Navegación clara entre programas
5. **Centralizado**: Vista unificada del ciudadano

---

## 🎯 Casos de Uso

### Caso 1: Ciudadano con consumo problemático necesita apoyo familiar
```
1. Está en "Acompañamiento SEDRONAR"
2. Profesional detecta necesidad de apoyo familiar
3. Deriva a "ÑACHEC"
4. Se acepta derivación
5. Ahora tiene 2 solapas activas
6. Cada programa con su propio seguimiento
```

### Caso 2: Ciudadano llega directamente a ÑACHEC
```
1. No tiene programas activos
2. Se crea derivación espontánea a "ÑACHEC"
3. Se acepta
4. Aparece solapa "ÑACHEC"
5. Luego puede derivarse a otros programas si es necesario
```

---

## 📁 Archivos Creados

```
legajos/
├── models_programas.py          ← Modelos nuevos
├── services_solapas.py          ← Lógica de negocio
├── views_solapas.py             ← Vistas
└── templates/legajos/
    └── ciudadano_detalle_solapas.html  ← Template

docs/
└── ARQUITECTURA_SOLAPAS_DINAMICAS.md  ← Documentación
```

---

## 🚀 Implementación

### Paso 1: Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### Paso 2: Crear Programa SEDRONAR
```python
from legajos.models_programas import Programa

Programa.objects.create(
    codigo='SEDRONAR',
    nombre='Acompañamiento SEDRONAR',
    tipo='ACOMPANAMIENTO_SEDRONAR',
    color='#6366f1',
    icono='medical_services',
    orden=1
)
```

### Paso 3: Migrar Legajos Existentes
```bash
python manage.py migrar_legajos_a_programas
```

### Paso 4: Crear Programa ÑACHEC
```python
Programa.objects.create(
    codigo='NACHEC',
    nombre='ÑACHEC',
    tipo='NACHEC',
    color='#10b981',
    icono='groups',
    orden=2
)
```

---

## 💡 Ejemplo de Código

```python
# Obtener solapas de un ciudadano
from legajos.services_solapas import SolapasService

ciudadano = Ciudadano.objects.get(dni='12345678')
solapas = SolapasService.obtener_solapas_ciudadano(ciudadano)

# Resultado:
# [
#   {'nombre': 'Resumen', 'estatica': True},
#   {'nombre': 'Acompañamiento SEDRONAR', 'color': '#6366f1'},
#   {'nombre': 'ÑACHEC', 'color': '#10b981'},
#   {'nombre': 'Red Familiar', 'estatica': True},
# ]
```

---

## ❓ Preguntas Frecuentes

**P: ¿Puede un ciudadano estar en el mismo programa dos veces?**  
R: No, la restricción `unique_together` lo previene.

**P: ¿Qué pasa si rechazo una derivación?**  
R: La derivación queda en estado RECHAZADA y NO se crea la inscripción.

**P: ¿Puedo cerrar una inscripción?**  
R: Sí, al cerrarla la solapa desaparece pero queda en el historial.

**P: ¿Cómo agrego un nuevo programa?**  
R: Creas el modelo del legajo específico y registras el programa en el catálogo.

---

**¿Listo para implementar? 🚀**
