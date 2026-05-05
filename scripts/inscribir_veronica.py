"""Inscribe a Veronica PERCIANTE en programa 6 para ver datos en v11."""
from legajos.models_programas import InscripcionPrograma, Programa
from legajos.models import Ciudadano
from flujos.models import InstanciaFlujo, TareaFlujo
from flujos.infrastructure.ui_renderer import build_display_only_sections

DNI = "36397539"
PROGRAMA_ID = 6

programa = Programa.objects.get(pk=PROGRAMA_ID)
print(f"Programa: {programa.nombre} (v{programa.flujo_activo.numero_version} publicada)")

ciudadano = Ciudadano.objects.filter(dni=DNI).first()
if ciudadano is None:
    print(f"!! No se encontro ciudadano con DNI {DNI}")
    raise SystemExit(1)
print(f"Ciudadano: pk={ciudadano.pk} {ciudadano.nombre_completo} (DNI {ciudadano.dni})")

ya = InscripcionPrograma.objects.filter(ciudadano=ciudadano, programa=programa).first()
if ya:
    print(f"!! Ya inscripta: codigo={ya.codigo}")
    raise SystemExit(0)

print("\n--- Creando InscripcionPrograma ---")
inscripcion = InscripcionPrograma.objects.create(
    ciudadano=ciudadano,
    programa=programa,
    via_ingreso=InscripcionPrograma.ViaIngreso.DIRECTO,
    estado=InscripcionPrograma.Estado.ACTIVO,
    notas="Inscripcion test para validar v11",
)
print(f"  OK: codigo={inscripcion.codigo}")

inscripcion.refresh_from_db()
try:
    instancia = inscripcion.instancia_flujo
    print(f"\n--- InstanciaFlujo ---")
    print(f"  id: {instancia.id}")
    print(f"  nodo_actual: {instancia.nodo_actual!r}")
    print(f"  estado: {instancia.estado}")
    print(f"  version: v{instancia.version_flujo.numero_version}")
except Exception as exc:
    print(f"  !! sin instancia: {exc}")
    raise SystemExit(1)

# Buscar el nodo correspondiente y resolver la pantalla
definicion = instancia.version_flujo.definicion
nodo = next((n for n in definicion["nodos"] if n.get("id") == instancia.nodo_actual), None)
if nodo:
    ui = (nodo.get("config") or {}).get("ui")
    sections = build_display_only_sections(ui, instancia=instancia)
    print(f"\n--- Pantalla resuelta para este caso ---")
    for s in sections:
        print(f"  Seccion: {s['title']!r}")
        for it in s["items"]:
            print(f"    -> {it['display_kind']}: {it.get('label', '')}")
            if it["display_kind"] == "table":
                for r in it["rows"]:
                    cells = " | ".join(str(c["value"]) for c in r["cells"])
                    print(f"       {cells}")

print("\n--- Conteo final v11 ---")
from django.db.models import Count
total = InstanciaFlujo.objects.filter(version_flujo=programa.flujo_activo, estado=InstanciaFlujo.Estado.ACTIVA).count()
print(f"  Instancias activas en v11: {total}")
