from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from legajos.models import Ciudadano
from system_modules.models import ModuleState
from system_modules.services import sync_module_catalog


class PortalModuleShellTests(TestCase):
    def setUp(self):
        sync_module_catalog()
        self.group = Group.objects.create(name="Ciudadanos")
        self.user = User.objects.create_user(username="30111222", password="secret")
        self.user.groups.add(self.group)
        self.ciudadano = Ciudadano.objects.create(
            dni="30111222",
            nombre="Ana",
            apellido="Perez",
            genero="F",
            usuario=self.user,
        )

    def test_portal_home_hides_optional_accesses_when_modules_are_disabled(self):
        ModuleState.objects.filter(slug="turnos").update(is_enabled=False)
        ModuleState.objects.filter(slug="conversaciones").update(is_enabled=False)

        response = self.client.get(reverse("portal:home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse("portal:ciudadano_mis_turnos"))
        self.assertNotContains(response, reverse("portal:ciudadano_mis_consultas"))

    def test_citizen_profile_keeps_working_when_conversations_module_is_disabled(self):
        ModuleState.objects.filter(slug="turnos").update(is_enabled=False)
        ModuleState.objects.filter(slug="conversaciones").update(is_enabled=False)
        self.client.force_login(self.user)

        response = self.client.get(reverse("portal:ciudadano_mi_perfil"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse("portal:ciudadano_mis_turnos"))
        self.assertContains(response, "modulo de consultas no esta disponible")
