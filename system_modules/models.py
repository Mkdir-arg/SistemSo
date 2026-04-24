from django.db import models


class ModuleState(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    module_type = models.CharField(max_length=40, default="removable")
    removable = models.BooleanField(default=True)
    is_core = models.BooleanField(default=False)
    is_installed = models.BooleanField(default=True)
    is_enabled = models.BooleanField(default=True)
    depends_on = models.JSONField(default=list, blank=True)
    managed_groups = models.JSONField(default=list, blank=True)
    nav_items = models.JSONField(default=list, blank=True)
    route_handles = models.JSONField(default=list, blank=True)
    api_handles = models.JSONField(default=list, blank=True)
    websocket_handles = models.JSONField(default=list, blank=True)
    startup_hooks = models.JSONField(default=list, blank=True)
    adapter_points = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Module state"
        verbose_name_plural = "Module states"
        ordering = ["slug"]

    def __str__(self):
        return f"{self.display_name} ({self.slug})"
