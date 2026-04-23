from django.core.management.base import BaseCommand

from system_modules.services import sync_module_catalog


class Command(BaseCommand):
    help = "Sync module definitions from settings.SYSTEM_MODULES into ModuleState."

    def handle(self, *args, **options):
        created, updated = sync_module_catalog()
        self.stdout.write(
            self.style.SUCCESS(
                f"Module catalog synchronized. created={created} updated={updated}"
            )
        )
