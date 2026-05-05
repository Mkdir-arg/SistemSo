"""Diagnostico temporal: por que el programa 6 muestra 0 instancias activas."""
from legajos.models_programas import InscripcionPrograma, Programa
from flujos.models import InstanciaFlujo, TareaFlujo, VersionFlujo

PROGRAMA_ID = 6

print("=" * 70)
print(f"DIAGNOSTICO PROGRAMA pk={PROGRAMA_ID}")
print("=" * 70)

try:
    p = Programa.objects.get(pk=PROGRAMA_ID)
except Programa.DoesNotExist:
    print(f"!! No existe programa con pk={PROGRAMA_ID}")
    raise SystemExit(1)

print(f"Programa: {p.nombre} (tipo={p.tipo})")
print(f"Flujo activo: {p.flujo_activo}")
if p.flujo_activo:
    print(f"  -> version publicada: v{p.flujo_activo.numero_version}")
    print(f"  -> estado: {p.flujo_activo.estado}")

print()
print("--- Versiones de flujo del programa ---")
for v in VersionFlujo.objects.filter(flujo__programa=p).order_by("-numero_version"):
    print(f"  v{v.numero_version} | estado={v.estado} | nodos={len((v.definicion or {}).get('nodos', []))}")

print()
print("--- Inscripciones al programa ---")
total_insc = InscripcionPrograma.objects.filter(programa=p).count()
print(f"Total inscripciones (todas): {total_insc}")
for estado in InscripcionPrograma.objects.filter(programa=p).values_list("estado", flat=True).distinct():
    count = InscripcionPrograma.objects.filter(programa=p, estado=estado).count()
    print(f"  - estado={estado}: {count}")

# Inscripciones con / sin instancia de flujo
con_instancia = InscripcionPrograma.objects.filter(programa=p, instancia_flujo__isnull=False).count()
sin_instancia = InscripcionPrograma.objects.filter(programa=p, instancia_flujo__isnull=True).count()
print(f"  - con instancia_flujo: {con_instancia}")
print(f"  - sin instancia_flujo: {sin_instancia}")

print()
print("--- Instancias de flujo de este programa ---")
total_inst = InstanciaFlujo.objects.filter(version_flujo__flujo__programa=p).count()
print(f"Total instancias (cualquier version): {total_inst}")
print()
print("Por version y estado:")
from django.db.models import Count
for fila in (
    InstanciaFlujo.objects
    .filter(version_flujo__flujo__programa=p)
    .values("version_flujo__numero_version", "estado")
    .annotate(total=Count("id"))
    .order_by("-version_flujo__numero_version", "estado")
):
    print(f"  v{fila['version_flujo__numero_version']:>3} | estado={fila['estado']:<10} | total={fila['total']}")

print()
print("--- Activas por nodo (en la version publicada) ---")
if p.flujo_activo:
    activas_por_nodo = (
        InstanciaFlujo.objects
        .filter(version_flujo=p.flujo_activo, estado=InstanciaFlujo.Estado.ACTIVA)
        .values("nodo_actual")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    if activas_por_nodo:
        for fila in activas_por_nodo:
            print(f"  nodo={fila['nodo_actual']!r:<30} -> {fila['total']}")
    else:
        print("  (sin instancias activas en v" + str(p.flujo_activo.numero_version) + ")")

print()
print("--- Tareas pendientes (en la version publicada) ---")
if p.flujo_activo:
    tareas_por_nodo = (
        TareaFlujo.objects
        .filter(instancia__version_flujo=p.flujo_activo, estado=TareaFlujo.Estado.PENDIENTE)
        .values("nodo_id")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    if tareas_por_nodo:
        for fila in tareas_por_nodo:
            print(f"  nodo={fila['nodo_id']!r:<30} -> {fila['total']}")
    else:
        print("  (sin tareas pendientes)")

print()
print("=" * 70)
print("FIN DIAGNOSTICO")
print("=" * 70)
