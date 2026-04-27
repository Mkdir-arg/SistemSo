from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .services import sync_installed_modules


@receiver(post_migrate)
def sync_system_modules_catalog(sender, **kwargs):
    if sender.name != "system_modules":
        return
    sync_installed_modules()
