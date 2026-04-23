import json

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import RequestFactory, TestCase, override_settings

from system_modules.context_processors import module_capabilities
from system_modules.models import ModuleState
from system_modules.registry import get_module_registry
from system_modules.services import get_assignable_groups_queryset, module_is_active


class ModuleRegistryTests(TestCase):
    def setUp(self):
        get_module_registry.cache_clear()
        self.addCleanup(get_module_registry.cache_clear)

    def test_sync_module_catalog_creates_rows_from_settings(self):
        call_command("sync_module_catalog")

        self.assertTrue(ModuleState.objects.filter(slug="turnos").exists())
        self.assertTrue(ModuleState.objects.filter(slug="chatbot").exists())
        self.assertTrue(ModuleState.objects.filter(slug="conversaciones").exists())

    def test_module_is_active_uses_database_state(self):
        call_command("sync_module_catalog")
        ModuleState.objects.filter(slug="turnos").update(is_enabled=False)

        self.assertFalse(module_is_active("turnos"))

    def test_context_processor_exposes_capabilities_and_json_payload(self):
        call_command("sync_module_catalog")
        ModuleState.objects.filter(slug="turnos").update(is_enabled=False)
        request = RequestFactory().get("/")

        payload = module_capabilities(request)

        self.assertFalse(payload["module_capabilities"]["turnos"]["is_active"])
        self.assertIn("chatbot", payload["active_module_slugs"])
        parsed = json.loads(payload["module_capabilities_json"])
        self.assertFalse(parsed["turnos"]["is_active"])

    def test_assignable_groups_hides_groups_for_inactive_modules(self):
        call_command("sync_module_catalog")
        Group.objects.create(name="turnoConfigurar")
        Group.objects.create(name="Administrador")
        ModuleState.objects.filter(slug="turnos").update(is_enabled=False)

        visible = list(get_assignable_groups_queryset().values_list("name", flat=True))

        self.assertNotIn("turnoConfigurar", visible)
        self.assertIn("Administrador", visible)

    def test_assignable_groups_keeps_existing_user_groups_visible(self):
        call_command("sync_module_catalog")
        turno_group = Group.objects.create(name="turnoOperar")
        ModuleState.objects.filter(slug="turnos").update(is_enabled=False)
        user = User.objects.create_user(username="operador", password="secret")
        user.groups.add(turno_group)

        visible = list(
            get_assignable_groups_queryset(instance=user).values_list("name", flat=True)
        )

        self.assertIn("turnoOperar", visible)

    @override_settings(
        SYSTEM_MODULES=(
            "turnos.module:TURNOS_MODULE",
            "chatbot.module:CHATBOT_MODULE",
        )
    )
    def test_sync_marks_removed_modules_as_uninstalled(self):
        call_command("sync_module_catalog")
        self.assertTrue(ModuleState.objects.get(slug="chatbot").is_installed)

        with override_settings(SYSTEM_MODULES=("turnos.module:TURNOS_MODULE",)):
            get_module_registry.cache_clear()
            call_command("sync_module_catalog")

        chatbot_state = ModuleState.objects.get(slug="chatbot")
        self.assertFalse(chatbot_state.is_installed)
        self.assertFalse(chatbot_state.is_enabled)

    def test_unknown_module_is_not_active(self):
        call_command("sync_module_catalog")
        self.assertFalse(module_is_active("modulo-fantasma"))
