import json

from system_modules.infrastructure.services import get_module_capabilities


def _user_group_names(request):
    user = getattr(request, "user", None)
    if not getattr(user, "is_authenticated", False):
        return []
    try:
        return list(user.groups.values_list("name", flat=True))
    except Exception:
        return []


def module_capabilities(request):
    capabilities, capabilities_json = get_module_capabilities()
    groups = _user_group_names(request)
    return {
        "module_capabilities": capabilities,
        "module_capabilities_json": capabilities_json,
        "active_module_slugs": [
            slug for slug, data in capabilities.items() if data["is_active"]
        ],
        "user_groups_list": groups,
        "user_groups_json": json.dumps(groups),
    }
