"""Verifica que el nuevo render produce datos resueltos para programa 6."""
from legajos.models_programas import Programa
from legajos.interfaces.web.views.programas import _build_program_flow_context

p = Programa.objects.get(pk=6)
ctx = _build_program_flow_context(p)
if not ctx:
    print("!! No hay contexto")
    raise SystemExit(1)

print(f"Version: v{ctx['version']} · instancias activas: {ctx['active_instances']}")
print()

for stage in ctx["stages"]:
    print(f"--- Stage: {stage['nombre']} (id={stage['id']}, tipo={stage['tipo']}) ---")
    print(f"  has_screen: {stage['has_screen']}")
    print(f"  cases: {len(stage['screen_cases'])}")
    print(f"  template sections: {len(stage['screen_template_sections'])}")
    if stage["screen_cases"]:
        for caso in stage["screen_cases"]:
            print(f"  CASO: {caso['ciudadano_nombre']} (DNI {caso['ciudadano_dni']})")
            for section in caso["sections"]:
                print(f"    sección: {section['title']!r}")
                for item in section["items"]:
                    if item["display_kind"] == "table":
                        print(f"      TABLA: {item['label']!r}")
                        for row in item["rows"]:
                            cells = ' | '.join(str(c['value']) for c in row['cells'])
                            print(f"        > {cells}")
                    elif item["display_kind"] == "summary":
                        print(f"      SUMMARY: {item['label']!r}")
                        for it in item["items"]:
                            print(f"        > {it['label']} = {it['value']}")
                    elif item["display_kind"] == "info":
                        print(f"      INFO ({item['tone']}): {item['content'][:80]}")
    print()
