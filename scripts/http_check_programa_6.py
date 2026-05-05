"""HTTP request real al endpoint del programa 6 (autenticado) y busca la seccion."""
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.filter(is_superuser=True).first()
print(f"Admin: {admin}")

client = Client(HTTP_HOST="localhost:8000")
client.force_login(admin)

resp = client.get("/legajos/programas/6/", HTTP_HOST="localhost:8000")
print(f"Status: {resp.status_code}")
print(f"HTML length: {len(resp.content)}")

content = resp.content.decode("utf-8", errors="replace")

needles = [
    "Pantalla del nodo",
    "Vista del operador en esta etapa",
    "Sin casos parados en esta etapa",
    "ciudadano.dni",
    "DNI",
    "Datos principales 2",
    "Casos que hoy están acá",
    "v11 publicada",
]

for needle in needles:
    found = needle in content
    print(f"  {'OK' if found else '!!'}  {needle!r}: {'presente' if found else 'AUSENTE'}")

# Buscar context donde aparece la primera vez "Pantalla del nodo"
idx = content.find("Pantalla del nodo")
if idx > 0:
    print(f"\n--- contexto alrededor de 'Pantalla del nodo' (idx={idx}) ---")
    print(content[max(0, idx-100):idx+500])
