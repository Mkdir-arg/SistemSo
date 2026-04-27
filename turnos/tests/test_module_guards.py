from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from system_modules.models import ModuleState
from system_modules.infrastructure.services import sync_installed_modules


class TurnosModuleGuardsTests(TestCase):
    def setUp(self):
        sync_installed_modules()
        self.user = User.objects.create_user(
            username="turnos-admin",
            password="clave-segura-123",
            is_staff=True,
        )
        self.user.groups.add(Group.objects.create(name="turnoOperar"))

    def test_backoffice_view_returns_403_when_module_is_disabled(self):
        ModuleState.objects.filter(slug="turnos").update(is_enabled=False)
        self.client.force_login(self.user)

        response = self.client.get(reverse("turnos:home"))

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Turnos", status_code=403)

    def test_backoffice_api_returns_json_when_module_is_disabled(self):
        ModuleState.objects.filter(slug="turnos").update(is_enabled=False)
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("turnos:api_slots"),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["code"], "module_inactive")
