"""Inspecciona la version publicada del programa 6 para ver que bloques tiene."""
import json
from legajos.models_programas import Programa
from flujos.infrastructure.ui_renderer import has_display_blocks, build_display_only_sections

p = Programa.objects.get(pk=6)
v = p.flujo_activo
print(f"Version publicada: v{v.numero_version} ({v.estado})")
print()

definicion = v.definicion
nodos = definicion.get("nodos", [])
print(f"Total nodos: {len(nodos)}")
print()

for nodo in nodos:
    nid = nodo.get("id")
    nombre = nodo.get("nombre")
    tipo = nodo.get("tipo")
    config = nodo.get("config") or {}
    ui = config.get("ui")

    print(f"=== Nodo: {nombre!r} (id={nid}, tipo={tipo}) ===")
    if not isinstance(ui, dict):
        print(f"  Sin ui_schema")
        continue
    print(f"  ui type: {ui.get('type')}")
    print(f"  has_display_blocks: {has_display_blocks(ui)}")
    print(f"  secciones: {len(ui.get('sections') or [])}")

    for i, section in enumerate(ui.get("sections") or []):
        print(f"    seccion {i}: {section.get('title')!r}")
        for j, field in enumerate(section.get("fields") or []):
            kind = field.get("kind")
            label = field.get("label")
            extra = ""
            if kind == "table":
                extra = f" mode={field.get('table_mode')} cols={len(field.get('columns') or [])} rows={len(field.get('rows') or [])}"
            elif kind == "summary":
                extra = f" items={len(field.get('items') or [])}"
            print(f"      campo {j}: kind={kind!r} label={label!r}{extra}")

    print()
    sections_preview = build_display_only_sections(ui, instancia=None)
    print(f"  build_display_only_sections (literal): {len(sections_preview)} secciones de display")
    for s in sections_preview:
        for it in s["items"]:
            print(f"    -> {it['display_kind']}: {it.get('label', '')!r}")
            if it["display_kind"] == "table":
                for r in it["rows"]:
                    cells = " | ".join(str(c["value"]) for c in r["cells"])
                    print(f"       fila: {cells}")
    print()
