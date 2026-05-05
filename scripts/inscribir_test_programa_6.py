"""Crea una inscripcion de prueba en programa 6 para disparar InstanciaFlujo."""
from legajos.models_programas import InscripcionPrograma, Programa
from flujos.models import InstanciaFlujo, TareaFlujo

PROGRAMA_ID = 6

print("=" * 70)
print(f"INSCRIPCION DE PRUEBA EN PROGRAMA pk={PROGRAMA_ID}")
print("=" * 70)

programa = Programa.objects.get(pk=PROGRAMA_ID)
print(f"Programa: {programa.nombre} (codigo={programa.codigo})")
print(f"Flujo activo: v{programa.flujo_activo.numero_version}")

# Buscar Ciudadano model
try:
    from legajos.models import Ciudadano
except ImportError:
    from ciudadanos.models import Ciudadano

# Mostrar primeros 5 ciudadanos
print()
print("--- Primeros 5 ciudadanos disponibles ---")
ciudadanos_top = list(Ciudadano.objects.all()[:5])
for c in ciudadanos_top:
    print(f"  pk={c.pk:>4} | DNI={c.dni:<12} | {c.nombre_completo}")

if not ciudadanos_top:
    print("!! No hay ningun Ciudadano cargado en la base. Cancelando.")
    raise SystemExit(1)

# Tomar el primero
ciudadano = ciudadanos_top[0]
print()
print(f"Eligiendo ciudadano pk={ciudadano.pk} ({ciudadano.nombre_completo}) para la inscripcion.")

# Verificar que no este ya inscrito
ya_inscrito = InscripcionPrograma.objects.filter(
    ciudadano=ciudadano, programa=programa
).first()
if ya_inscrito:
    print(f"!! Este ciudadano ya esta inscrito (codigo={ya_inscrito.codigo}, estado={ya_inscrito.estado}).")
    print("   Probando con el siguiente disponible...")
    encontrado = None
    for c in Ciudadano.objects.all().iterator():
        if not InscripcionPrograma.objects.filter(ciudadano=c, programa=programa).exists():
            encontrado = c
            break
    if not encontrado:
        print("!! Todos los ciudadanos ya estan inscriptos. Cancelando.")
        raise SystemExit(1)
    ciudadano = encontrado
    print(f"  Usando ciudadano pk={ciudadano.pk} ({ciudadano.nombre_completo})")

print()
print("--- Creando InscripcionPrograma ---")
inscripcion = InscripcionPrograma.objects.create(
    ciudadano=ciudadano,
    programa=programa,
    via_ingreso=InscripcionPrograma.ViaIngreso.DIRECTO,
    estado=InscripcionPrograma.Estado.ACTIVO,
    notas="Inscripcion de prueba creada desde script diagnostico",
)
print(f"  OK: codigo={inscripcion.codigo}, estado={inscripcion.estado}")

# Verificar si signal disparo y creo InstanciaFlujo
print()
print("--- Verificando InstanciaFlujo ---")
try:
    instancia = inscripcion.instancia_flujo
    print(f"  OK: InstanciaFlujo creada")
    print(f"  -> id: {instancia.id}")
    print(f"  -> nodo_actual: {instancia.nodo_actual!r}")
    print(f"  -> estado: {instancia.estado}")
    print(f"  -> version: v{instancia.version_flujo.numero_version}")
except Exception as exc:
    print(f"  !! No se creo InstanciaFlujo: {type(exc).__name__}: {exc}")
    print("     Buscando por inscripcion explicitamente...")
    instancias = InstanciaFlujo.objects.filter(inscripcion=inscripcion)
    print(f"     Encontradas: {instancias.count()}")
    for inst in instancias:
        print(f"     -> id={inst.id} nodo={inst.nodo_actual!r} estado={inst.estado}")

# Tareas pendientes derivadas
print()
print("--- Tareas pendientes para esta instancia ---")
tareas = TareaFlujo.objects.filter(instancia__inscripcion=inscripcion).order_by("-id")
print(f"  Total: {tareas.count()}")
for t in tareas:
    print(f"  -> id={t.id} nodo={t.nodo_id!r} estado={t.estado}")

print()
print("=" * 70)
print("FIN")
print("=" * 70)
