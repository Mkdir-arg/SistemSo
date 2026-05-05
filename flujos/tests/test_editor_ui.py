from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from flujos.models import Flujo, VersionFlujo
from legajos.models_programas import Programa
from system_modules.infrastructure.services import sync_installed_modules


class FlujosEditorUiTests(TestCase):
    def setUp(self):
        sync_installed_modules()
        self.user = User.objects.create_user(
            username='flujos-editor-ui',
            password='clave-segura-123',
            is_staff=True,
        )
        self.user.groups.add(Group.objects.create(name='programaConfigurar'))
        self.programa = Programa.objects.create(
            codigo='PROG-EDITOR-001',
            nombre='Programa Editor',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        self.flujo = Flujo.objects.create(
            programa=self.programa,
            nombre='Flujo Programa Editor',
        )
        VersionFlujo.objects.create(
            flujo=self.flujo,
            estado=VersionFlujo.Estado.BORRADOR,
            definicion={
                'nodos': [
                    {'id': 'inicio', 'tipo': 'inicio', 'nombre': 'Inicio'},
                    {'id': 'fin', 'tipo': 'fin', 'nombre': 'Fin'},
                ],
                'transiciones': [
                    {'desde': 'inicio', 'hasta': 'fin', 'condicion': None},
                ],
            },
            creado_por=self.user,
        )
        self.client.force_login(self.user)

    def test_editor_renders_operational_summary_and_guidance(self):
        response = self.client.get(reverse('flujos_editor:editor_flujo', args=[self.programa.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cómo usar este editor')
        self.assertContains(response, 'Diseño del flujo')
        self.assertContains(response, 'Borrador disponible')
        self.assertContains(response, 'Versiones registradas')
        self.assertContains(response, reverse('flujos:api_definicion', args=[self.programa.pk]))
        self.assertContains(response, 'flow-editor-root')