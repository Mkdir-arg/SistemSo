from system_modules.definitions import ModuleDefinition, UrlDefinition


MODULE_DEFINITION = ModuleDefinition(
    slug="tramites",
    display_name="Tramites",
    app_config="tramites",
    module_type="removable",
    description="Gestion backoffice de tramites institucionales.",
    managed_groups=(),
    web_routes=(
        UrlDefinition(
            handle="tramites.backoffice",
            route="tramites/",
            urlconf="tramites.interfaces.web.urls",
            namespace="tramites",
            app_name="tramites",
        ),
    ),
    api_routes=(
        UrlDefinition(
            handle="tramites.api",
            route="api/tramites/",
            urlconf="tramites.interfaces.api.urls",
            namespace="tramites_api",
            app_name="tramites_api",
        ),
    ),
    adapter_points=("templates/includes/sidebar/opciones.html",),
)
