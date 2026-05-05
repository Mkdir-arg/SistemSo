"""Analiza la version publicada actual y las URLs de resolucion de tareas."""
import json
from legajos.models_programas import Programa
from flujos.models import InstanciaFlujo, TareaFlujo
from django.urls import reverse, NoReverseMatch

p = Programa.objects.get(pk=6)
v = p.flujo_activo
print("=" * 60)
print(f"VERSION PUBLICADA: v{v.numero_version} ({v.estado})")
print("=" * 60)

definicion = v.definicion or {}
nodos = definicion.get("nodos", [])
transiciones = definicion.get("transiciones", [])

print(f"\n--- Nodos ({len(nodos)}) ---")
for n in nodos:
    print(f"  id={n.get('id')!r:<35} tipo={n.get('tipo')!r:<15} nombre={n.get('nombre')!r}")

print(f"\n--- Transiciones ({len(transiciones)}) ---")
for t in transiciones:
    cond = t.get("condicion")
    cond_str = ""
    if cond:
        cond_str = f"  condicion: {cond.get('campo')} {cond.get('operador')} {cond.get('valor')!r}"
    else:
        cond_str = "  (libre)"
    print(f"  desde={t.get('desde')!r} -> hasta={t.get('hasta')!r}")
    print(cond_str)

# Buscar el nodo Derivacion (accion_humana)
nodo_humano = next((n for n in nodos if n.get("tipo") == "accion_humana"), None)
if nodo_humano:
    print(f"\n--- Nodo {nodo_humano.get('nombre')!r} ui_schema ---")
    ui = (nodo_humano.get("config") or {}).get("ui") or {}
    print(f"  type: {ui.get('type')}")
    for s in ui.get("sections", []):
        print(f"  Seccion: {s.get('title')!r}")
        for f in s.get("fields", []):
            kind = f.get("kind")
            label = f.get("label")
            id_ = f.get("id")
            extra = ""
            if kind in ("radio", "select"):
                opts = f.get("options", [])
                extra = f"  options=[{', '.join(o.get('value', '?')+ ':' + o.get('label', '?') for o in opts)}]"
            elif kind == "table":
                extra = f"  cols={len(f.get('columns', []))} rows={len(f.get('rows', []))}"
            elif kind == "checkbox":
                extra = f"  required={f.get('required')}"
            print(f"    field id={id_!r:<25} kind={kind!r:<10} label={label!r}{extra}")

print("\n" + "=" * 60)
print("INSTANCIAS Y TAREAS PENDIENTES")
print("=" * 60)

instancias_activas = (
    InstanciaFlujo.objects
    .filter(version_flujo__flujo__programa=p, estado=InstanciaFlujo.Estado.ACTIVA)
    .select_related("inscripcion__ciudadano", "version_flujo")
)
for inst in instancias_activas:
    c = inst.inscripcion.ciudadano
    print(f"\n  InstanciaFlujo id={inst.id} v{inst.version_flujo.numero_version}")
    print(f"    ciudadano: {c.nombre_completo} (DNI {c.dni})")
    print(f"    nodo_actual: {inst.nodo_actual}")

    tareas = TareaFlujo.objects.filter(instancia=inst)
    for t in tareas:
        print(f"    tarea id={t.id} nodo={t.nodo_id!r} estado={t.estado}")

print("\n" + "=" * 60)
print("URLS DE RESOLUCION DE TAREAS")
print("=" * 60)
try:
    print(f"  Bandeja: {reverse('flujos:bandeja_tareas')}")
except NoReverseMatch as e:
    print(f"  !! Bandeja: {e}")

t = TareaFlujo.objects.filter(estado=TareaFlujo.Estado.PENDIENTE).first()
if t:
    try:
        print(f"  Detalle tarea pendiente (id={t.id}): {reverse('flujos:tarea_detalle', kwargs={'tarea_id': t.id})}")
    except NoReverseMatch as e:
        print(f"  !! Detalle: {e}")
