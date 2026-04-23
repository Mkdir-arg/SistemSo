from system_modules.definitions import ModuleDefinition


CONVERSACIONES_MODULE = ModuleDefinition(
    slug="conversaciones",
    display_name="Conversaciones",
    description="Chat ciudadano-operador y bandeja operativa.",
    managed_groups=("Conversaciones", "OperadorCharla"),
    route_handles=("conversaciones.public", "conversaciones.backoffice"),
    api_handles=("conversaciones.api",),
    websocket_handles=("conversaciones.realtime",),
    adapter_points=(
        "portal.views.ciudadano_consultas",
        "portal.services.consultas",
        "templates/includes/base.html",
    ),
)
