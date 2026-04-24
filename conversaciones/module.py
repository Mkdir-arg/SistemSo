from system_modules.definitions import ModuleDefinition, UrlDefinition, WebsocketDefinition


MODULE_DEFINITION = ModuleDefinition(
    slug="conversaciones",
    display_name="Conversaciones",
    app_config="conversaciones",
    module_type="removable",
    description="Chat ciudadano-operador y bandeja operativa.",
    managed_groups=("Conversaciones", "OperadorCharla"),
    web_routes=(
        UrlDefinition(
            handle="conversaciones.web",
            route="conversaciones/",
            urlconf="conversaciones.interfaces.web.urls",
            namespace="conversaciones",
            app_name="conversaciones",
        ),
    ),
    api_routes=(
        UrlDefinition(
            handle="conversaciones.api",
            route="api/conversaciones/",
            urlconf="conversaciones.interfaces.api.urls",
            namespace="conversaciones_api",
            app_name="conversaciones_api",
        ),
    ),
    websocket_routes=(
        WebsocketDefinition(
            handle="conversaciones.realtime",
            urlconf="conversaciones.interfaces.realtime.routing",
        ),
    ),
    adapter_points=(
        "portal.views.ciudadano_consultas",
        "templates/includes/base.html",
    ),
)
