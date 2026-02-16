# Instrucciones de Implementación - Sistema de Solapas Dinámicas

## Paso 1: Crear Migraciones
```bash
python manage.py makemigrations legajos
```

## Paso 2: Ejecutar Migraciones
```bash
python manage.py migrate
```

## Paso 3: Cargar Datos Iniciales (Programas)
```bash
python manage.py loaddata programas_initial
```

## Paso 4: Migrar Legajos Existentes (DRY RUN primero)
```bash
# Simular migración sin guardar
python manage.py migrar_legajos_a_programas --dry-run

# Si todo está OK, ejecutar migración real
python manage.py migrar_legajos_a_programas
```

## Paso 5: Verificar en Admin
1. Ir a Django Admin
2. Verificar que existan los modelos:
   - Programas (debe haber 2: SEDRONAR y ÑACHEC)
   - Inscripciones a Programas (debe haber una por cada legajo)
   - Derivaciones entre Programas (vacío inicialmente)

## Paso 6: Probar Funcionalidad
1. Ir al detalle de un ciudadano
2. Verificar que aparezca la solapa "Acompañamiento SEDRONAR"
3. Crear una derivación a ÑACHEC
4. Aceptar la derivación
5. Verificar que aparezca la solapa "ÑACHEC"

## Notas Importantes
- Los legajos existentes se migrarán automáticamente
- Los nuevos legajos crearán InscripcionPrograma automáticamente (signal)
- Las solapas aparecen solo si el estado es ACTIVO o EN_SEGUIMIENTO
- Al cerrar un legajo, la solapa desaparece

## Troubleshooting

### Error: Programa SEDRONAR no encontrado
```bash
python manage.py loaddata programas_initial
```

### Error: Tabla no existe
```bash
python manage.py migrate
```

### Revertir migración de legajos
No hay comando de revert, pero puedes eliminar las inscripciones:
```python
from legajos.models_programas import InscripcionPrograma
InscripcionPrograma.objects.filter(notas__contains='Migrado desde').delete()
```
