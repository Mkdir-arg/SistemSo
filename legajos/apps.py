from django.apps import AppConfig


class LegajosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'legajos'
    verbose_name = 'Legajos'
    
    def ready(self):
        import legajos.signals
        import legajos.signals_alertas
        import legajos.signals_historial
        import legajos.signals_programas  # Importar signals de programas
