from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from system_modules.models import ModuleState
from system_modules.infrastructure.services import sync_installed_modules


class FlujosModuleGuardsTests(TestCase):
    def setUp(self):
        sync_installed_modules()
        self.user = User.objects.create_user(
            username="flujos-editor",
            password="clave-segura-123",
            is_staff=True,
        )
        self.user.groups.add(Group.objects.create(name="programaConfigurar"))

    def test_editor_returns_403_when_module_is_disabled(self):
        ModuleState.objects.filter(slug="flujos").update(is_enabled=False)
        self.client.force_login(self.user)

        response = self.client.get(reverse("flujos_editor:editor_flujo", args=[1]))

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Flujos", status_code=403)

    def test_api_returns_json_when_module_is_disabled(self):
        ModuleState.objects.filter(slug="flujos").update(is_enabled=False)
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("flujos:api_definicion", args=[1]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["code"], "module_inactive")
