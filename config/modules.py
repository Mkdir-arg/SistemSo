from importlib import import_module
from importlib.util import find_spec

DEFAULT_MODULE_ATTR = "MODULE_DEFINITION"

CORE_PROJECT_APPS = (
    "system_modules",
    "users",
    "core",
    "healthcheck",
)

INSTALLED_PROJECT_MODULES = [
    "portal",
    "dashboard",
    "configuracion",
    "legajos",
    "turnos",
    "chatbot",
    "conversaciones",
    "tramites",
    "flujos",
]


def _load_module_definition(slug):
    module_path = f"{slug}.module"
    try:
        spec = find_spec(module_path)
    except ModuleNotFoundError:
        spec = None
    if spec is None:
        return None
    module = import_module(module_path)
    return getattr(module, DEFAULT_MODULE_ATTR, None)


def get_installed_project_app_configs(module_slugs=None):
    apps = []
    for slug in module_slugs or INSTALLED_PROJECT_MODULES:
        definition = _load_module_definition(slug)
        if definition is None:
            continue
        apps.append(definition.app_config)
    return apps
