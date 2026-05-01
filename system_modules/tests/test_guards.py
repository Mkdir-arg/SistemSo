from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings

from system_modules.guards import module_required
from system_modules.registry import clear_module_registry
from system_modules.models import ModuleState
from system_modules.infrastructure.services import sync_installed_modules


class ModuleGuardsTests(TestCase):
    def setUp(self):
        sync_installed_modules()
        self.factory = RequestFactory()

    def test_module_required_blocks_html_requests(self):
        ModuleState.objects.filter(slug="turnos").update(is_enabled=False)

        @module_required("turnos")
        def sample_view(request):
            return HttpResponse("ok")

        request = self.factory.get("/turnos/")
        request.user = AnonymousUser()
        response = sample_view(request)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "modulo no disponible", status_code=403)

    def test_module_required_blocks_json_requests(self):
        ModuleState.objects.filter(slug="turnos").update(is_enabled=False)

        @module_required("turnos")
        def sample_view(request):
            return HttpResponse("ok")

        request = self.factory.get(
            "/turnos/api/slots/",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_ACCEPT="application/json",
        )
        request.user = AnonymousUser()
        response = sample_view(request)

        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(
            response.content,
            {
                "code": "module_inactive",
                "module": "turnos",
                "display_name": "Turnos",
                "message": "Modulo no disponible. Contacta a un administrador.",
            },
        )

    @override_settings(INSTALLED_PROJECT_MODULES=["chatbot"])
    def test_module_required_handles_unregistered_modules_without_crashing(self):
        clear_module_registry()

        @module_required("turnos")
        def sample_view(request):
            return HttpResponse("ok")

        request = self.factory.get("/api/turnos/", HTTP_ACCEPT="application/json")
        request.user = AnonymousUser()
        response = sample_view(request)

        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(
            response.content,
            {
                "code": "module_inactive",
                "module": "turnos",
                "display_name": "Turnos",
                "message": "Modulo no disponible. Contacta a un administrador.",
            },
        )

        clear_module_registry()
