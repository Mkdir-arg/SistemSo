from django.contrib import admin

from .models import ModuleState
from .services import sync_module_catalog


@admin.register(ModuleState)
class ModuleStateAdmin(admin.ModelAdmin):
    list_display = ("slug", "display_name", "is_installed", "is_enabled", "updated_at")
    list_filter = ("is_installed", "is_enabled")
    search_fields = ("slug", "display_name")
    readonly_fields = (
        "slug",
        "display_name",
        "description",
        "is_installed",
        "depends_on",
        "managed_groups",
        "nav_items",
        "route_handles",
        "api_handles",
        "websocket_handles",
        "startup_hooks",
        "adapter_points",
        "created_at",
        "updated_at",
    )
    actions = ("enable_selected", "disable_selected", "sync_catalog")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Enable selected modules")
    def enable_selected(self, request, queryset):
        queryset.filter(is_installed=True).update(is_enabled=True)

    @admin.action(description="Disable selected modules")
    def disable_selected(self, request, queryset):
        queryset.filter(is_installed=True).update(is_enabled=False)

    @admin.action(description="Sync module catalog")
    def sync_catalog(self, request, queryset):
        created, updated = sync_module_catalog()
        self.message_user(
            request,
            f"Catalog synchronized. created={created} updated={updated}",
        )

    def changelist_view(self, request, extra_context=None):
        sync_module_catalog()
        return super().changelist_view(request, extra_context=extra_context)
