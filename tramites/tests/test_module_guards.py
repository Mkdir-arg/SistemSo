from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from system_modules.models import ModuleState
from system_modules.services import sync_module_catalog


class TramitesModuleGuardsTests(TestCase):
    def setUp(self):
        sync_module_catalog()
        self.user = User.objects.create_user(
            username="tramites-admin",
            password="clave-segura-123",
            is_staff=True,
        )

    def test_tramites_list_returns_403_when_module_is_disabled(self):
        ModuleState.objects.filter(slug="tramites").update(is_enabled=False)
        self.client.force_login(self.user)

        response = self.client.get(reverse("tramites:lista_tramites"))

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Tramites", status_code=403)
