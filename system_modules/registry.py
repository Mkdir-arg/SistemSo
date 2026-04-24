import importlib
import sys
from functools import lru_cache
from importlib import import_module
from importlib.util import find_spec

from django.conf import settings

DEFAULT_MODULE_ATTR = "MODULE_DEFINITION"


def _load_definition_from_slug(slug):
    module_name = f"{slug}.module"
    try:
        spec = find_spec(module_name)
    except ModuleNotFoundError:
        spec = None
    if spec is None:
        return None
    module = import_module(module_name)
    if hasattr(module, DEFAULT_MODULE_ATTR):
        return getattr(module, DEFAULT_MODULE_ATTR)
    for value in module.__dict__.values():
        if value.__class__.__name__ == "ModuleDefinition":
            return value
    return None


class ModuleRegistry:
    def __init__(self, definitions, missing_slugs=()):
        self._definitions = {definition.slug: definition for definition in definitions}
        self.missing_slugs = tuple(missing_slugs)

    def all(self):
        return tuple(self._definitions.values())

    def get(self, slug):
        return self._definitions[slug]

    def has(self, slug):
        return slug in self._definitions

    def installed_app_configs(self):
        return tuple(definition.app_config for definition in self.all())

    def web_routes(self):
        for definition in self.all():
            for route in definition.web_routes:
                yield definition, route

    def api_routes(self):
        for definition in self.all():
            for route in definition.api_routes:
                yield definition, route

    def websocket_routes(self):
        for definition in self.all():
            for route in definition.websocket_routes:
                yield definition, route


@lru_cache(maxsize=1)
def get_module_registry():
    definitions = []
    missing_slugs = []
    for slug in tuple(getattr(settings, "INSTALLED_PROJECT_MODULES", ())):
        definition = _load_definition_from_slug(slug)
        if definition is None:
            missing_slugs.append(slug)
            continue
        definitions.append(definition)
    return ModuleRegistry(definitions, missing_slugs)


def clear_module_registry():
    get_module_registry.cache_clear()
    try:
        from django.urls import clear_url_caches

        clear_url_caches()
    except Exception:
        return
    if "config.urls" in sys.modules:
        importlib.reload(sys.modules["config.urls"])
        try:
            from django.urls import clear_url_caches

            clear_url_caches()
        except Exception:
            return
