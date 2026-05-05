"""Re-intenta la inscripcion de prueba ahora que el schema esta limpio."""
from legajos.models_programas import InscripcionPrograma, Programa
from legajos.models import Ciudadano
from flujos.models import InstanciaFlujo, TareaFlujo

PROGRAMA_ID = 6

print("=" * 70)
print(f"RETRY INSCRIPCION TEST PROGRAMA pk={PROGRAMA_ID}")
print("=" * 70)

programa = Programa.objects.get(pk=PROGRAMA_ID)

# Limpiar inscripcion previa (la que fallo dejando InstanciaFlujo a medias)
huerfanas = InscripcionPrograma.objects.filter(programa=programa)
print(f"Inscripciones existentes a borrar: {huerfanas.count()}")
for ins in huerfanas:
    print(f"  - codigo={ins.codigo} ciudadano={ins.ciudadano.dni}")
huerfanas.delete()

# Re-crear con el schema limpio
ciudadano = Ciudadano.objects.first()
print(f"\nUsando ciudadano: pk={ciudadano.pk} DNI={ciudadano.dni} {ciudadano.nombre_completo}")

print("\n--- Creando InscripcionPrograma ---")
inscripcion = InscripcionPrograma.objects.create(
    ciudadano=ciudadano,
    programa=programa,
    via_ingreso=InscripcionPrograma.ViaIngreso.DIRECTO,
    estado=InscripcionPrograma.Estado.ACTIVO,
    notas="Inscripcion test post-cleanup",
)
print(f"  OK: codigo={inscripcion.codigo}")

print("\n--- Verificando InstanciaFlujo ---")
inscripcion.refresh_from_db()
try:
    instancia = inscripcion.instancia_flujo
    print(f"  OK persistida: id={instancia.id}")
    print(f"  -> nodo_actual: {instancia.nodo_actual!r}")
    print(f"  -> estado: {instancia.estado}")
    print(f"  -> version: v{instancia.version_flujo.numero_version}")
except Exception as exc:
    print(f"  !! Sin InstanciaFlujo: {type(exc).__name__}: {exc}")

print("\n--- Tareas pendientes ---")
tareas = TareaFlujo.objects.filter(instancia__inscripcion=inscripcion)
print(f"  Total: {tareas.count()}")
for t in tareas:
    print(f"  -> nodo={t.nodo_id!r} estado={t.estado}")

print("\n--- Conteo final por nodo (lo que mostraria el panel) ---")
from django.db.models import Count
for fila in (
    InstanciaFlujo.objects
    .filter(version_flujo=programa.flujo_activo, estado=InstanciaFlujo.Estado.ACTIVA)
    .values("nodo_actual")
    .annotate(total=Count("id"))
):
    print(f"  nodo={fila['nodo_actual']!r:<30} -> {fila['total']} caso(s)")

print("\n" + "=" * 70)
print("FIN")
print("=" * 70)
