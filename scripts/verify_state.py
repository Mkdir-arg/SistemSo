"""Verifica estado real de inscripciones, instancias y version publicada."""
from legajos.models_programas import InscripcionPrograma, Programa
from flujos.models import InstanciaFlujo, VersionFlujo

p = Programa.objects.get(pk=6)
print(f"Programa: {p.nombre}")
print(f"flujo_activo: v{p.flujo_activo.numero_version} (estado={p.flujo_activo.estado})")
print()

print("--- Versiones ---")
for v in VersionFlujo.objects.filter(flujo__programa=p).order_by("-numero_version"):
    print(f"  v{v.numero_version} estado={v.estado}")

print()
print("--- Inscripciones ---")
for ins in InscripcionPrograma.objects.filter(programa=p):
    inst = getattr(ins, "instancia_flujo", None)
    inst_info = ""
    if inst:
        inst_info = f" -> instancia id={inst.id} v{inst.version_flujo.numero_version} nodo={inst.nodo_actual!r} estado={inst.estado}"
    print(f"  {ins.codigo} ciudadano={ins.ciudadano.nombre_completo} estado={ins.estado}{inst_info}")

print()
print("--- Todas las InstanciaFlujo del programa ---")
for inst in InstanciaFlujo.objects.filter(version_flujo__flujo__programa=p).select_related("inscripcion__ciudadano"):
    print(f"  id={inst.id} v{inst.version_flujo.numero_version} nodo={inst.nodo_actual!r} estado={inst.estado} ciudadano={inst.inscripcion.ciudadano.nombre_completo}")

print()
print("--- Lo que ve el view (filtra por version_publicada=v?, estado=ACTIVA) ---")
qs = (
    InstanciaFlujo.objects
    .filter(version_flujo=p.flujo_activo, estado=InstanciaFlujo.Estado.ACTIVA)
    .select_related("inscripcion__ciudadano")
)
print(f"  count: {qs.count()}")
for inst in qs:
    print(f"    -> id={inst.id} nodo={inst.nodo_actual!r} ciudadano={inst.inscripcion.ciudadano.nombre_completo}")
