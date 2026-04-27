import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from types import SimpleNamespace

from django.contrib.auth.models import Group, User
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase, override_settings
from django.urls import NoReverseMatch, clear_url_caches, reverse

from system_modules.infrastructure.services import sync_installed_modules
from system_modules.models import ModuleState
from system_modules.registry import clear_module_registry


PROJECT_ROOT = Path(__file__).resolve().parents[2]


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

    def test_process_starts_and_shell_renders_when_conversaciones_folder_is_absent(self):
        script = r"""
import importlib.abc
import os
import sys
from types import SimpleNamespace

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings_test"
os.environ.setdefault("DJANGO_SECRET_KEY", "test-secret-key")

import config.modules as project_modules

project_modules.INSTALLED_PROJECT_MODULES[:] = [
    slug for slug in project_modules.INSTALLED_PROJECT_MODULES
    if slug != "conversaciones"
]

import config.settings_test as smoke_settings

smoke_settings.DATABASES["default"]["NAME"] = os.environ["MODULE_SMOKE_SQLITE"]


class BlockConversaciones(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "conversaciones" or fullname.startswith("conversaciones."):
            raise ModuleNotFoundError("blocked conversaciones for removable-module smoke")
        return None


sys.meta_path.insert(0, BlockConversaciones())

import django

django.setup()

from django.core.management import call_command

call_command("migrate", run_syncdb=True, verbosity=0, interactive=False)

from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.urls import NoReverseMatch, reverse

request = RequestFactory().get("/portal/")
request.user = AnonymousUser()
request.resolver_match = SimpleNamespace(url_name="home", kwargs={})

reverse("portal:home")
render_to_string("includes/base.html", {"request": request}, request=request)

try:
    reverse("conversaciones:lista")
except NoReverseMatch:
    pass
else:
    raise AssertionError("conversaciones routes must not be published when the module is not installed")
"""
        env = os.environ.copy()
        env["DJANGO_SETTINGS_MODULE"] = "config.settings_test"
        env.setdefault("DJANGO_SECRET_KEY", "test-secret-key")

        with tempfile.TemporaryDirectory() as tmpdir:
            env["MODULE_SMOKE_SQLITE"] = str(Path(tmpdir) / "module-smoke.sqlite3")
            result = subprocess.run(
                [sys.executable, "-c", textwrap.dedent(script)],
                cwd=PROJECT_ROOT,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )

        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
