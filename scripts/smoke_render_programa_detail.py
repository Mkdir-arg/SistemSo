"""Smoke test: renderizar el detalle del programa 6 sin servidor HTTP."""
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from legajos.models_programas import Programa
from legajos.interfaces.web.views.programas import (
    ProgramaDetailView,
    _build_program_flow_context,
)

User = get_user_model()
admin = User.objects.filter(is_superuser=True).first() or User.objects.first()
print(f"Usuario: {admin}")

factory = RequestFactory()
request = factory.get(f"/legajos/programas/6/")
request.user = admin

view = ProgramaDetailView()
view.setup(request, pk=6)
view.object = view.get_object()

context = view.get_context_data(object=view.object)
print(f"flujo_activo en context: {bool(context.get('flujo_activo'))}")

if context.get("flujo_activo"):
    for stage in context["flujo_activo"]["stages"]:
        print(f"  stage {stage['nombre']}: has_screen={stage['has_screen']} cases={len(stage['screen_cases'])}")

# Intentar renderizar el template
try:
    html = render_to_string("legajos/programas/programa_detail.html", context, request=request)
    print(f"\nTemplate render OK. Tamaño: {len(html)} chars")

    # Buscar evidencia de la nueva sección
    if "Pantalla del nodo" in html:
        print("  -> Sección 'Pantalla del nodo' presente.")
    if "Matias FARIÑA" in html:
        print("  -> Caso de Matias FARIÑA renderizado.")
    if "40732138" in html:
        print("  -> DNI 40732138 resuelto en el HTML.")
    # Verificar que NO aparezca el placeholder literal donde había datos resueltos
    if "{{ ciudadano.dni }}" in html:
        print("  !! El placeholder literal aparece - puede ser correcto si esta en la microcopy")
except Exception as exc:
    print(f"\n!! Error renderizando template: {type(exc).__name__}: {exc}")
    import traceback
    traceback.print_exc()
