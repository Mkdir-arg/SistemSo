# ✅ Sistema de Solapas Dinámicas - Lógica Final

## 🎯 Reglas de Visualización

### Solapas SIEMPRE Visibles (Estáticas)
1. **Resumen** - Primera solapa, vista general
2. **Cursos y Actividades** - Actividades del centro
3. **Red Familiar** - Vínculos y contactos
4. **Archivos** - Documentos adjuntos

### Solapas CONDICIONALES (Dinámicas)
- **Acompañamiento SEDRONAR** - Solo si tiene LegajoAtencion activo
- **ÑACHEC** - Solo si tiene inscripción activa en ÑACHEC
- **Otros Programas** - Solo si tiene inscripción activa

---

## 📐 Orden de Visualización

```
[Resumen] → [Programas Activos] → [Cursos y Actividades] → [Red Familiar] → [Archivos]
   ↑              ↑                        ↑                      ↑              ↑
Siempre      Solo si tiene           Siempre                Siempre        Siempre
            inscripción activa
```

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Ciudadano nuevo (sin programas)
```
[Resumen] [Cursos y Actividades] [Red Familiar] [Archivos]
```
**Total: 4 solapas**

---

### Ejemplo 2: Ciudadano con Acompañamiento SEDRONAR
```
[Resumen] [Acompañamiento SEDRONAR] [Cursos y Actividades] [Red Familiar] [Archivos]
```
**Total: 5 solapas**

---

### Ejemplo 3: Ciudadano derivado a ÑACHEC (derivación PENDIENTE)
```
[Resumen] [Acompañamiento SEDRONAR] [Cursos y Actividades] [Red Familiar] [Archivos]
```
**Total: 5 solapas** (ÑACHEC NO aparece porque la derivación está pendiente)

---

### Ejemplo 4: Ciudadano derivado a ÑACHEC (derivación ACEPTADA)
```
[Resumen] [Acompañamiento SEDRONAR] [ÑACHEC] [Cursos y Actividades] [Red Familiar] [Archivos]
```
**Total: 6 solapas** (ÑACHEC aparece porque la derivación fue aceptada)

---

### Ejemplo 5: Ciudadano solo en ÑACHEC (cerró Acompañamiento)
```
[Resumen] [ÑACHEC] [Cursos y Actividades] [Red Familiar] [Archivos]
```
**Total: 5 solapas** (Acompañamiento desapareció porque se cerró)

---

### Ejemplo 6: Ciudadano en 3 programas simultáneos
```
[Resumen] [Acompañamiento SEDRONAR] [ÑACHEC] [Económico] [Cursos y Actividades] [Red Familiar] [Archivos]
```
**Total: 7 solapas**

---

## 🔄 Ciclo de Vida de una Solapa Dinámica

```
1. DERIVACIÓN CREADA
   Estado: PENDIENTE
   Solapa: ❌ NO VISIBLE
   
2. DERIVACIÓN ACEPTADA
   Estado: ACEPTADA
   Se crea: InscripcionPrograma (estado=ACTIVO)
   Solapa: ✅ VISIBLE
   
3. PROGRAMA ACTIVO
   Estado: ACTIVO o EN_SEGUIMIENTO
   Solapa: ✅ VISIBLE
   
4. PROGRAMA CERRADO
   Estado: CERRADO
   Solapa: ❌ NO VISIBLE (desaparece)
```

---

## 📊 Tabla de Estados

| Estado InscripcionPrograma | Solapa Visible | Notas |
|----------------------------|----------------|-------|
| PENDIENTE | ❌ NO | Derivación no aceptada aún |
| ACTIVO | ✅ SÍ | Programa activo |
| EN_SEGUIMIENTO | ✅ SÍ | Programa en seguimiento |
| SUSPENDIDO | ❌ NO | Programa suspendido temporalmente |
| CERRADO | ❌ NO | Programa finalizado |

---

## 🎨 Identificación Visual

### Solapas Estáticas
- Color: Gris/Negro estándar
- Sin indicador de color
- Siempre en la misma posición

### Solapas Dinámicas
- Color: Según programa (ej: azul para SEDRONAR, verde para ÑACHEC)
- Indicador: Punto de color al lado del nombre
- Posición: Entre "Resumen" y "Cursos y Actividades"

---

## 🚀 Implementación

### Código del Servicio
```python
# services_solapas.py

SOLAPAS_ESTATICAS = [
    {'id': 'resumen', 'nombre': 'Resumen', 'orden': 0},
    {'id': 'cursos_actividades', 'nombre': 'Cursos y Actividades', 'orden': 900},
    {'id': 'red_familiar', 'nombre': 'Red Familiar', 'orden': 998},
    {'id': 'archivos', 'nombre': 'Archivos', 'orden': 999}
]

def obtener_solapas_ciudadano(ciudadano):
    solapas = []
    
    # 1. Resumen (siempre)
    solapas.append(SOLAPAS_ESTATICAS[0])
    
    # 2. Programas activos (dinámicas)
    inscripciones = InscripcionPrograma.objects.filter(
        ciudadano=ciudadano,
        estado__in=['ACTIVO', 'EN_SEGUIMIENTO']
    )
    
    for inscripcion in inscripciones:
        solapas.append({
            'nombre': inscripcion.programa.nombre,
            'orden': 100 + inscripcion.programa.orden,
            'color': inscripcion.programa.color,
            'estatica': False
        })
    
    # 3. Cursos, Red, Archivos (siempre)
    solapas.extend(SOLAPAS_ESTATICAS[1:])
    
    # 4. Ordenar
    solapas.sort(key=lambda x: x['orden'])
    
    return solapas
```

---

## ✅ Checklist de Validación

- [x] Resumen siempre visible
- [x] Cursos y Actividades siempre visible
- [x] Red Familiar siempre visible
- [x] Archivos siempre visible
- [x] Acompañamiento solo si tiene inscripción activa
- [x] ÑACHEC solo si tiene inscripción activa
- [x] Programas dinámicos entre Resumen y Cursos
- [x] Orden correcto de solapas
- [x] Colores distintivos por programa
- [x] Solapa desaparece al cerrar programa

---

## 🎯 Resumen Ejecutivo

**4 Solapas Estáticas** (siempre visibles):
1. Resumen
2. Cursos y Actividades
3. Red Familiar
4. Archivos

**N Solapas Dinámicas** (según programas activos):
- Aparecen entre "Resumen" y "Cursos y Actividades"
- Solo si InscripcionPrograma.estado in ['ACTIVO', 'EN_SEGUIMIENTO']
- Cada programa con su color distintivo
- Desaparecen al cerrar el programa

**Orden Final**:
```
Resumen → [Programa 1] → [Programa 2] → ... → Cursos → Red → Archivos
```
