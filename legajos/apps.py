from django.apps import AppConfig


class LegajosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'legajos'
    verbose_name = 'Legajos'
    
    def ready(self):
        import legajos.infrastructure.signals  # noqa: F401
        import legajos.infrastructure.signals.alerts  # noqa: F401
        import legajos.infrastructure.signals.historial  # noqa: F401
        import legajos.infrastructure.signals.programas  # noqa: F401
        import legajos.infrastructure.signals.nachec  # noqa: F401
