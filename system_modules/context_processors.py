from system_modules.infrastructure.services import get_module_capabilities


def module_capabilities(request):
    capabilities, capabilities_json = get_module_capabilities()
    return {
        "module_capabilities": capabilities,
        "module_capabilities_json": capabilities_json,
        "active_module_slugs": [
            slug for slug, data in capabilities.items() if data["is_active"]
        ],
    }
