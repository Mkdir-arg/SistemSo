"""Verifica que ambas vistas muestren los 2 casos vivos sin importar version."""
from django.test import Client
from django.contrib.auth import get_user_model

admin = get_user_model().objects.filter(is_superuser=True).first()
client = Client(HTTP_HOST="localhost:8000")
client.force_login(admin)

print("=" * 60)
print("PANEL DEL PROGRAMA — /legajos/programas/6/")
print("=" * 60)
resp = client.get("/legajos/programas/6/", HTTP_HOST="localhost:8000")
html = resp.content.decode("utf-8", "replace")
print(f"  status: {resp.status_code}")
checks = [
    ("2 instancias activas", "2 instancias activas"),
    ("DNI Veronica", "36397539"),
    ("DNI Matias", "40732138"),
    ("Veronica nombre", "Veronica Anahi PERCIANTE"),
    ("Matias nombre", "Matias FARIÑA"),
    ("Pantalla del nodo seccion", "Pantalla del nodo"),
]
for label, needle in checks:
    print(f"  {'OK' if needle in html else '!!'} {label}: {'presente' if needle in html else 'AUSENTE'}")

print()
print("=" * 60)
print("EDITOR — /flujos/programas/6/flujo/editar/")
print("=" * 60)
resp = client.get("/flujos/programas/6/flujo/editar/", HTTP_HOST="localhost:8000")
html = resp.content.decode("utf-8", "replace")
print(f"  status: {resp.status_code}")
import re
m = re.search(r'<strong>Instancias activas</strong>\s*(\d+)', html)
if m:
    print(f"  Instancias activas en el header del editor: {m.group(1)}")
else:
    print(f"  No se pudo extraer el contador de instancias activas del editor")
