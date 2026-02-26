# ai_squad/context_builder.py
from __future__ import annotations
import os
from pathlib import Path
from django.conf import settings
from django.apps import apps


class ProjectContextBuilder:
    """Construye contexto del proyecto Django para el agente."""
    
    @staticmethod
    def build_context() -> dict:
        """
        Extrae información relevante del proyecto Django.
        
        Returns:
            dict con apps, modelos, urls, etc.
        """
        return {
            "django_version": "4.2",
            "apps": ProjectContextBuilder._get_installed_apps(),
            "models": ProjectContextBuilder._get_models_summary(),
            "urls": ProjectContextBuilder._get_urls_summary(),
            "base_dir": str(settings.BASE_DIR),
        }
    
    @staticmethod
    def _get_installed_apps() -> list[str]:
        """Lista de apps propias del proyecto (excluye Django/libs)."""
        django_apps = {
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.admindocs',
            'rest_framework',
            'channels',
            'django_redis',
            'health_check',
            'silk',
            'drf_spectacular',
            'django_extensions',
            'django_filter',
            'django_simple_history',
        }
        
        return [
            app for app in settings.INSTALLED_APPS
            if app not in django_apps and not app.startswith('health_check.')
        ]
    
    @staticmethod
    def _get_models_summary() -> list[str]:
        """Resumen de modelos existentes."""
        models_info = []
        
        for app_config in apps.get_app_configs():
            if app_config.name in ProjectContextBuilder._get_installed_apps():
                for model in app_config.get_models():
                    fields = [f.name for f in model._meta.get_fields()[:5]]  # Primeros 5 campos
                    models_info.append(
                        f"{app_config.name}.{model.__name__} ({', '.join(fields)}...)"
                    )
        
        return models_info[:20]  # Limitar a 20 modelos
    
    @staticmethod
    def _get_urls_summary() -> list[str]:
        """Resumen de URLs principales."""
        # Por ahora retornamos las apps conocidas
        # En una versión más avanzada podríamos parsear urls.py
        return [
            "/admin/",
            "/api/legajos/",
            "/api/core/",
            "/api/chatbot/",
            "/api/users/",
            "/api/ai-squad/runs/",
            "/legajos/",
            "/configuracion/",
            "/conversaciones/",
            "/portal/",
            "/tramites/",
        ]
    
    @staticmethod
    def get_file_content(relative_path: str) -> str | None:
        """
        Lee el contenido de un archivo del proyecto.
        
        Args:
            relative_path: Ruta relativa desde BASE_DIR
        
        Returns:
            Contenido del archivo o None si no existe
        """
        try:
            file_path = Path(settings.BASE_DIR) / relative_path
            if file_path.exists() and file_path.is_file():
                return file_path.read_text(encoding='utf-8')
        except Exception:
            pass
        return None
