from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from system_modules.models import ModuleState
from system_modules.infrastructure.services import sync_installed_modules


class ConversacionesModuleGuardsTests(TestCase):
    def setUp(self):
        sync_installed_modules()
        self.user = User.objects.create_user(
            username="operador-chat",
            password="clave-segura-123",
            is_staff=True,
        )
        self.user.groups.add(Group.objects.create(name="Conversaciones"))

    def test_public_chat_returns_403_when_module_is_disabled(self):
        ModuleState.objects.filter(slug="conversaciones").update(is_enabled=False)

        response = self.client.get(reverse("conversaciones:chat_ciudadano"))

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Conversaciones", status_code=403)

    def test_backoffice_list_returns_403_when_module_is_disabled(self):
        ModuleState.objects.filter(slug="conversaciones").update(is_enabled=False)
        self.client.force_login(self.user)

        response = self.client.get(reverse("conversaciones:lista"))

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Conversaciones", status_code=403)

    def test_rest_api_returns_module_inactive_when_module_is_disabled(self):
        ModuleState.objects.filter(slug="conversaciones").update(is_enabled=False)
        self.client.force_login(self.user)

        response = self.client.get(
            "/api/conversaciones/alertas/count/",
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["code"], "module_inactive")
