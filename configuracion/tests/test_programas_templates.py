from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from legajos.models_programas import Programa
from system_modules.infrastructure.services import sync_installed_modules


class ProgramaListTemplateTests(TestCase):
    def setUp(self):
        sync_installed_modules()
        self.user = User.objects.create_user(
            username="programa-config",
            password="clave-segura-123",
            is_staff=True,
        )
        self.user.groups.add(Group.objects.create(name="programaConfigurar"))
        self.programa = Programa.objects.create(
            codigo="PROG-PAUSA-001",
            nombre="Programa Pausa",
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
            estado=Programa.Estado.ACTIVO,
        )
        self.client.force_login(self.user)

    def test_programa_list_renders_pause_handler_and_support_scripts(self):
        response = self.client.get(reverse("configuracion:programas"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "function cambiarEstado")
        self.assertContains(response, "form-cambiar-estado")
        self.assertContains(response, "sweetalert2@11")
        self.assertContains(response, f"cambiarEstado({self.programa.pk}, 'SUSPENDIDO'")