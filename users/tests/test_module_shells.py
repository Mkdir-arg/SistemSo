from types import SimpleNamespace

from django.contrib.auth.models import Group, User
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse
from django.test.client import RequestFactory

from system_modules.models import ModuleState
from system_modules.infrastructure.services import sync_installed_modules


class BackofficeModuleShellTests(TestCase):
    def setUp(self):
        sync_installed_modules()
        self.factory = RequestFactory()
        self.admin_group = Group.objects.create(name="Administrador")
        self.programa_group = Group.objects.create(name="programaConfigurar")
        self.user = User.objects.create_user(
            username="admin-shell",
            password="secret",
            is_staff=True,
        )
        self.user.groups.add(self.admin_group)
        self.programa_user = User.objects.create_user(
            username="programa-shell",
            password="secret",
            is_staff=True,
        )
        self.programa_user.groups.add(self.programa_group)

    def test_users_screen_hides_optional_module_navigation_when_disabled(self):
        ModuleState.objects.filter(slug="chatbot").update(is_enabled=False)
        ModuleState.objects.filter(slug="conversaciones").update(is_enabled=False)
        ModuleState.objects.filter(slug="tramites").update(is_enabled=False)
        request = self.factory.get(reverse("core:inicio"))
        request.user = self.user
        request.resolver_match = SimpleNamespace(route="inicio/", kwargs={})

        rendered = render_to_string(
            "includes/sidebar/opciones.html",
            {
                "request": request,
                "branding": {
                    "active_profile": "default",
                    "colors": {"color_acento_oscuro": "#111111"},
                },
            },
            request=request,
        )

        self.assertNotIn(reverse("chatbot:admin_panel"), rendered)
        self.assertNotIn(reverse("conversaciones:lista"), rendered)
        self.assertNotIn(reverse("tramites:lista_tramites"), rendered)

    def test_users_screen_shows_flujos_navigation_for_program_role_when_enabled(self):
        request = self.factory.get(reverse("core:inicio"))
        request.user = self.programa_user
        request.resolver_match = SimpleNamespace(route="inicio/", kwargs={})

        rendered = render_to_string(
            "includes/sidebar/opciones.html",
            {
                "request": request,
                "branding": {
                    "active_profile": "default",
                    "colors": {"color_acento_oscuro": "#111111"},
                },
            },
            request=request,
        )

        self.assertIn(reverse("flujos_editor:bandeja_tareas"), rendered)
        self.assertIn(reverse("configuracion:programas"), rendered)

    def test_users_screen_hides_flujos_navigation_when_module_is_disabled(self):
        ModuleState.objects.filter(slug="flujos").update(is_enabled=False)
        request = self.factory.get(reverse("core:inicio"))
        request.user = self.programa_user
        request.resolver_match = SimpleNamespace(route="inicio/", kwargs={})

        rendered = render_to_string(
            "includes/sidebar/opciones.html",
            {
                "request": request,
                "branding": {
                    "active_profile": "default",
                    "colors": {"color_acento_oscuro": "#111111"},
                },
            },
            request=request,
        )

        self.assertNotIn(reverse("flujos_editor:bandeja_tareas"), rendered)
        self.assertNotIn(reverse("configuracion:programas"), rendered)
