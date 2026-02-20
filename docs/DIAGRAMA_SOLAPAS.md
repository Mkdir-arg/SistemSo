# 📊 Sistema de Solapas - Diagrama Visual Actualizado

## Estructura de Solapas

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         LEGAJO DEL CIUDADANO                                     │
│                      Juan Pérez - DNI 12345678                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  NAVEGACIÓN DE SOLAPAS                                                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌────────┐  ┌──────────────┐  ┌────────┐  ┌────────────┐  ┌──────────┐  ┌────────┐
│  │Resumen │  │Acompañamiento│  │ÑACHEC  │  │Cursos y    │  │Red       │  │Archivos│
│  │        │  │SEDRONAR      │  │        │  │Actividades │  │Familiar  │  │        │
│  └────────┘  └──────────────┘  └────────┘  └────────────┘  └──────────┘  └────────┘
│      ▲              ▲              ▲              ▲              ▲            ▲
│   ESTÁTICA      DINÁMICA       DINÁMICA       ESTÁTICA       ESTÁTICA    ESTÁTICA
│   (siempre)   (si tiene)     (si tiene)      (siempre)      (siempre)   (siempre)
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Solapas Estáticas (Siempre Visibles)

### 1. Resumen
- **Posición**: Primera (orden: 0)
- **Contenido**: Vista general del ciudadano, datos personales, resumen de programas activos
- **Siempre visible**: ✅

### 2. Cursos y Actividades
- **Posición**: Después de programas dinámicos (orden: 900)
- **Contenido**: Actividades del centro, talleres, cursos en los que está inscrito
- **Siempre visible**: ✅

### 3. Red Familiar
- **Posición**: Penúltima (orden: 998)
- **Contenido**: Vínculos familiares, contactos de emergencia, profesionales tratantes
- **Siempre visible**: ✅

### 4. Archivos
- **Posición**: Última (orden: 999)
- **Contenido**: Documentos adjuntos, consentimientos, informes
- **Siempre visible**: ✅

---

## Solapas Dinámicas (Según Programas Activos)

### Características:
- **Aparecen solo si el ciudadano tiene inscripción activa**
- **Posición**: Entre "Resumen" y "Cursos y Actividades" (orden: 100-899)
- **Color distintivo**: Cada programa tiene su color
- **Indicador visual**: Punto de color al lado del nombre

### Ejemplos:

#### Acompañamiento SEDRONAR
- **Aparece cuando**: Ciudadano tiene LegajoAtencion activo
- **Color**: #6366f1 (azul índigo)
- **Contenido**: Evaluación inicial, plan de intervención, seguimientos, eventos críticos

#### ÑACHEC
- **Aparece cuando**: Se acepta derivación a ÑACHEC
- **Color**: #10b981 (verde)
- **Contenido**: Evaluación familiar, plan familiar, seguimientos familiares

#### Acompañamiento Económico
- **Aparece cuando**: Se acepta derivación a programa económico
- **Color**: #f59e0b (amarillo)
- **Contenido**: Evaluación económica, plan de apoyo, seguimientos

---

## Ejemplos de Visualización

### Caso 1: Ciudadano sin programas activos
```
┌──────────────────────────────────────────────────────────────┐
│ [Resumen] [Cursos y Actividades] [Red Familiar] [Archivos]  │
└──────────────────────────────────────────────────────────────┘
```

### Caso 2: Ciudadano solo en Acompañamiento SEDRONAR
```
┌────────────────────────────────────────────────────────────────────────────┐
│ [Resumen] [Acompañamiento SEDRONAR 🔵] [Cursos] [Red Familiar] [Archivos] │
└────────────────────────────────────────────────────────────────────────────┘
```

### Caso 3: Ciudadano en múltiples programas
```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ [Resumen] [Acompañamiento SEDRONAR 🔵] [ÑACHEC 🟢] [Cursos] [Red Familiar] [Archivos]  │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

### Caso 4: Ciudadano en 3 programas
```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [Resumen] [Acompañamiento 🔵] [ÑACHEC 🟢] [Económico 🟡] [Cursos] [Red Familiar] [Archivos]          │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Aparición de Solapas Dinámicas

```
INICIO
  │
  ├─ Ciudadano sin programas
  │  └─> Solo solapas estáticas: [Resumen] [Cursos] [Red] [Archivos]
  │
  ├─ Se crea LegajoAtencion (Acompañamiento SEDRONAR)
  │  └─> Aparece solapa: [Acompañamiento SEDRONAR]
  │
  ├─ Se deriva a ÑACHEC
  │  ├─> Derivación PENDIENTE (solapa NO aparece aún)
  │  └─> Se ACEPTA derivación
  │      └─> Aparece solapa: [ÑACHEC]
  │
  ├─ Se cierra programa SEDRONAR
  │  └─> Desaparece solapa: [Acompañamiento SEDRONAR]
  │      └─> Queda solo: [ÑACHEC]
  │
  └─ Se cierran todos los programas
     └─> Solo solapas estáticas: [Resumen] [Cursos] [Red] [Archivos]
```

---

## Orden de Visualización

| Orden | Tipo | Solapa | Condición |
|-------|------|--------|-----------|
| 0 | Estática | Resumen | Siempre |
| 100-899 | Dinámica | Programas activos | Si tiene inscripción activa |
| 900 | Estática | Cursos y Actividades | Siempre |
| 998 | Estática | Red Familiar | Siempre |
| 999 | Estática | Archivos | Siempre |

---

## Código de Ejemplo

```python
# Obtener solapas de un ciudadano
from legajos.services_solapas import SolapasService

ciudadano = Ciudadano.objects.get(dni='12345678')
solapas = SolapasService.obtener_solapas_ciudadano(ciudadano)

# Resultado para ciudadano con Acompañamiento SEDRONAR y ÑACHEC:
# [
#   {'nombre': 'Resumen', 'orden': 0, 'estatica': True},
#   {'nombre': 'Acompañamiento SEDRONAR', 'orden': 101, 'estatica': False, 'color': '#6366f1'},
#   {'nombre': 'ÑACHEC', 'orden': 102, 'estatica': False, 'color': '#10b981'},
#   {'nombre': 'Cursos y Actividades', 'orden': 900, 'estatica': True},
#   {'nombre': 'Red Familiar', 'orden': 998, 'estatica': True},
#   {'nombre': 'Archivos', 'orden': 999, 'estatica': True}
# ]
```

---

## Resumen

✅ **Solapas Estáticas (4)**: Siempre visibles
- Resumen
- Cursos y Actividades
- Red Familiar
- Archivos

✅ **Solapas Dinámicas (N)**: Aparecen según programas activos
- Acompañamiento SEDRONAR (si tiene legajo activo)
- ÑACHEC (si tiene inscripción activa)
- Otros programas (según derivaciones aceptadas)

✅ **Orden**: Resumen → [Programas] → Cursos → Red → Archivos

✅ **Lógica**: Las solapas de programas solo aparecen cuando hay InscripcionPrograma activa
