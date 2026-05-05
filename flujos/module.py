from system_modules.definitions import ModuleDefinition, UrlDefinition


MODULE_DEFINITION = ModuleDefinition(
    slug="flujos",
    display_name="Flujos",
    app_config="flujos",
    module_type="removable",
    description="Editor visual y runtime del motor de flujos.",
    managed_groups=("programaConfigurar", "programaOperar"),
    web_routes=(
        UrlDefinition(
            handle="flujos.editor",
            route="flujos/",
            urlconf="flujos.interfaces.web.urls",
            namespace="flujos_editor",
            app_name="flujos_editor",
        ),
    ),
    api_routes=(
        UrlDefinition(
            handle="flujos.api",
            route="api/",
            urlconf="flujos.interfaces.api.urls",
            namespace="flujos",
            app_name="flujos",
        ),
    ),
    adapter_points=("configuracion/templates/configuracion/programa_list.html",),
)
