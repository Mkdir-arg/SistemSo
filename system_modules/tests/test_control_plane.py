from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import RequestFactory, TestCase, override_settings
from django.urls import clear_url_caches, reverse

from system_modules.guards import module_required
from system_modules.models import ModuleState
from system_modules.registry import clear_module_registry, get_module_registry
from system_modules.infrastructure.services import (
    get_assignable_groups_queryset,
    module_is_active,
    sync_installed_modules,
)


class ModuleCatalogTests(TestCase):
    @override_settings(INSTALLED_PROJECT_MODULES=["chatbot", "conversaciones"])
    def test_catalog_loads_only_installed_project_modules(self):
        clear_module_registry()
        registry = get_module_registry()

        self.assertTrue(registry.has("chatbot"))
        self.assertTrue(registry.has("conversaciones"))
        self.assertFalse(registry.has("tramites"))
        self.assertEqual(registry.missing_slugs, ())

    @override_settings(INSTALLED_PROJECT_MODULES=["chatbot", "missing_demo"])
    def test_catalog_tolerates_missing_module_folder(self):
        clear_module_registry()
        registry = get_module_registry()

        self.assertTrue(registry.has("chatbot"))
        self.assertFalse(registry.has("missing_demo"))
        self.assertEqual(registry.missing_slugs, ("missing_demo",))

    @override_settings(INSTALLED_PROJECT_MODULES=["chatbot"])
    def test_sync_marks_removed_module_as_not_installed_without_deleting_state(self):
        clear_module_registry()
        sync_installed_modules()
        self.assertTrue(ModuleState.objects.get(slug="chatbot").is_installed)

        with override_settings(INSTALLED_PROJECT_MODULES=[]):
            clear_module_registry()
            sync_installed_modules()

        state = ModuleState.objects.get(slug="chatbot")
        self.assertFalse(state.is_installed)
        self.assertFalse(state.is_enabled)

    @override_settings(INSTALLED_PROJECT_MODULES=["chatbot"])
    def test_modules_command_enables_disables_and_lists_module(self):
        clear_module_registry()
        call_command("modules", "sync")

        call_command("modules", "disable", "chatbot")
        self.assertFalse(module_is_active("chatbot"))

        call_command("modules", "enable", "chatbot")
        self.assertTrue(module_is_active("chatbot"))

        call_command("modules", "list")


class ModuleGuardAndPermissionsTests(TestCase):
    @override_settings(INSTALLED_PROJECT_MODULES=["chatbot"])
    def test_inactive_module_returns_controlled_response(self):
        clear_module_registry()
        sync_installed_modules()
        ModuleState.objects.filter(slug="chatbot").update(is_enabled=False)

        def view(request):
            return None

        request = RequestFactory().get("/chatbot/")
        request.user = User(username="tester")
        response = module_required("chatbot")(view)(request)

        self.assertEqual(response.status_code, 403)
        self.assertContains(
            response,
            "Modulo no disponible. Contacta a un administrador.",
            status_code=403,
        )

    @override_settings(INSTALLED_PROJECT_MODULES=["chatbot"])
    def test_inactive_module_managed_groups_are_hidden_for_new_assignment(self):
        clear_module_registry()
        sync_installed_modules()
        Group.objects.create(name="chatbotAdministrar")
        Group.objects.create(name="Administrador")
        ModuleState.objects.filter(slug="chatbot").update(is_enabled=False)

        names = set(get_assignable_groups_queryset().values_list("name", flat=True))

        self.assertNotIn("chatbotAdministrar", names)
        self.assertIn("Administrador", names)

    @override_settings(INSTALLED_PROJECT_MODULES=["chatbot"])
    def test_existing_user_keeps_hidden_group_visible_when_editing(self):
        clear_module_registry()
        sync_installed_modules()
        hidden = Group.objects.create(name="chatbotAdministrar")
        user = User.objects.create_user(username="existing")
        user.groups.add(hidden)
        ModuleState.objects.filter(slug="chatbot").update(is_enabled=False)

        names = set(
            get_assignable_groups_queryset(instance=user).values_list("name", flat=True)
        )

        self.assertIn("chatbotAdministrar", names)


class ModuleUrlconfTests(TestCase):
    @override_settings(INSTALLED_PROJECT_MODULES=["tramites"])
    def test_not_installed_module_routes_are_not_published(self):
        clear_module_registry()
        clear_url_caches()

        with self.assertRaises(Exception):
            reverse("chatbot:chat_interface")

        self.assertEqual(reverse("tramites:lista_tramites"), "/tramites/")
