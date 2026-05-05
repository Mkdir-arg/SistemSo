"""Extrae el HTML del tab Derivacion para analizar su estructura."""
import re
from django.test import Client
from django.contrib.auth import get_user_model

admin = get_user_model().objects.filter(is_superuser=True).first()
client = Client(HTTP_HOST="localhost:8000")
client.force_login(admin)
resp = client.get("/legajos/programas/6/", HTTP_HOST="localhost:8000")
html = resp.content.decode("utf-8", errors="replace")
print(f"Status: {resp.status_code}, total HTML: {len(html)} chars")

# Buscar todos los ids tab-flow-*
tab_ids = re.findall(r'id="tab-(flow-[\w-]+|dashboard|indicadores)"', html)
print(f"\nTabs encontrados en el HTML: {tab_ids}")

# Para cada tab-flow-*, ver su clase inicial y si contiene "Pantalla del nodo"
for tab in re.finditer(r'<div id="(tab-flow-[\w-]+)"\s+class="([^"]+)"', html):
    tab_id, classes = tab.group(1), tab.group(2)
    start = tab.start()
    # encontrar el fin del div (matching div balance es complicado, busco hasta el siguiente tab-flow- o tab-indicadores)
    next_tab = re.search(r'<div id="tab-(flow-[\w-]+|indicadores)"', html[start + len(tab.group(0)):])
    end = (start + len(tab.group(0)) + next_tab.start()) if next_tab else len(html)
    body = html[start:end]
    has_pantalla = "Pantalla del nodo" in body
    has_tabla_label = "Datos principales 2" in body
    has_dni = "ciudadano.dni" in body
    has_veronica = "Veronica" in body
    print(f"\n  TAB {tab_id} ({len(body)} chars)")
    print(f"    classes: {classes}")
    print(f"    contiene 'Pantalla del nodo': {has_pantalla}")
    print(f"    contiene 'Datos principales 2': {has_tabla_label}")
    print(f"    contiene 'ciudadano.dni': {has_dni}")
    print(f"    contiene 'Veronica': {has_veronica}")

# Buscar la primera ocurrencia de "Pantalla del nodo" y mostrar el path estructural
idx = html.find("Pantalla del nodo")
if idx > 0:
    # subir hacia atras hasta encontrar el tab-flow-
    upstream = html[:idx]
    last_tab_open = upstream.rfind('id="tab-flow-')
    if last_tab_open > 0:
        next_quote = upstream.find('"', last_tab_open + len('id="'))
        tab_id = upstream[last_tab_open + len('id="'):next_quote]
        print(f"\n>>> 'Pantalla del nodo' esta dentro del tab: {tab_id}")
    else:
        print(f"\n>>> 'Pantalla del nodo' NO esta dentro de ningun tab-flow-* upstream!")
        # Ver donde esta — fuera de tabs?
        last_dashboard = upstream.rfind('id="tab-dashboard"')
        last_indicadores = upstream.rfind('id="tab-indicadores"')
        print(f"   ultima ref tab-dashboard upstream: {last_dashboard}")
        print(f"   ultima ref tab-indicadores upstream: {last_indicadores}")
