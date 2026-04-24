from django.core.management.base import BaseCommand, CommandError

from system_modules.models import ModuleState
from system_modules.registry import clear_module_registry, get_module_registry
from system_modules.services import set_module_enabled, sync_installed_modules


class Command(BaseCommand):
    help = "List, sync, enable, or disable project modules for this instance."

    def add_arguments(self, parser):
        parser.add_argument("action", choices=("list", "sync", "enable", "disable"))
        parser.add_argument("slug", nargs="?")

    def handle(self, *args, **options):
        action = options["action"]
        slug = options.get("slug")
        clear_module_registry()

        if action == "sync":
            created, updated = sync_installed_modules()
            self.stdout.write(self.style.SUCCESS(f"created={created} updated={updated}"))
            return

        if action == "list":
            sync_installed_modules()
            states = ModuleState.objects.order_by("slug")
            for state in states:
                status = "enabled" if state.is_enabled else "disabled"
                installed = "installed" if state.is_installed else "not-installed"
                self.stdout.write(f"{state.slug}: {installed}, {status}")
            missing = get_module_registry().missing_slugs
            for missing_slug in missing:
                self.stdout.write(f"{missing_slug}: missing-folder")
            return

        if not slug:
            raise CommandError(f"modules {action} requires a module slug")

        try:
            state = set_module_enabled(slug, enabled=(action == "enable"))
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        status = "enabled" if state.is_enabled else "disabled"
        self.stdout.write(self.style.SUCCESS(f"{state.slug}: {status}"))
