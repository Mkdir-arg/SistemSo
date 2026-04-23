from functools import lru_cache
from importlib import import_module

from django.conf import settings


def _load_definition(path):
    module_path, attr_name = path.split(":", 1)
    module = import_module(module_path)
    return getattr(module, attr_name)


class ModuleRegistry:
    def __init__(self, definitions):
        self._definitions = {definition.slug: definition for definition in definitions}

    def all(self):
        return tuple(self._definitions.values())

    def get(self, slug):
        return self._definitions[slug]

    def has(self, slug):
        return slug in self._definitions


@lru_cache(maxsize=1)
def get_module_registry():
    definitions = [_load_definition(path) for path in getattr(settings, "SYSTEM_MODULES", ())]
    return ModuleRegistry(definitions)
