from types import SimpleNamespace

from django.contrib.auth.models import Group, User
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase, override_settings
from django.urls import NoReverseMatch, clear_url_caches, reverse

from system_modules.infrastructure.services import sync_installed_modules
from system_modules.models import ModuleState
from system_modules.registry import clear_module_registry


class ModuleFunctionalSmokeTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def tearDown(self):
        clear_module_registry()
        clear_url_caches()

    def _staff_request(self, path="/inicio/"):
        user = User.objects.create_user(
            username="smoke-admin",
            password="secret",
            is_staff=True,
            is_superuser=True,
        )
        for name in (
            "Administrador",
            "Conversaciones",
            "OperadorCharla",
            "Supervisor",
        ):
            group, _ = Group.objects.get_or_create(name=name)
            user.groups.add(group)
        request = self.factory.get(path)
        request.user = user
        request.resolver_match = SimpleNamespace(route=path.strip("/") or "inicio/", kwargs={})
        return request

    @override_settings(INSTALLED_PROJECT_MODULES=["portal", "dashboard", "configuracion", "legajos", "turnos"])
    def test_shell_base_renders_when_optional_modules_are_not_installed(self):
        clear_module_registry()
        clear_url_caches()

        request = self._staff_request()
        rendered = render_to_string("includes/base.html", {"request": request}, request=request)

        self.assertNotIn("window.conversacionesConfig", rendered)
        self.assertNotIn("chatbot_bubble", rendered)
        with self.assertRaises(NoReverseMatch):
            reverse("chatbot:admin_panel")
        with self.assertRaises(NoReverseMatch):
            reverse("conversaciones:lista")
        with self.assertRaises(NoReverseMatch):
            reverse("tramites:lista_tramites")
        with self.assertRaises(NoReverseMatch):
            reverse("flujos_editor:editor_flujo", args=[1])

    def test_shell_base_hides_optional_scripts_when_modules_are_disabled(self):
        sync_installed_modules()
        ModuleState.objects.filter(
            slug__in=("chatbot", "conversaciones", "tramites", "flujos")
        ).update(is_enabled=False)

        request = self._staff_request()
        rendered = render_to_string("includes/base.html", {"request": request}, request=request)

        self.assertNotIn("window.conversacionesConfig", rendered)
        self.assertNotIn("custom/js/conversaciones_lista_ws.js", rendered)
        self.assertNotIn('id="chatbot-bubble"', rendered)
        self.assertNotIn("data-send-message-url", rendered)
