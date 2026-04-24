from system_modules.definitions import ModuleDefinition, NavItemDefinition, UrlDefinition


MODULE_DEFINITION = ModuleDefinition(
    slug="turnos",
    display_name="Turnos",
    app_config="turnos",
    module_type="non_removable",
    removable=False,
    description="Turnos de backoffice y portal ciudadano.",
    managed_groups=("turnoConfigurar", "turnoOperar"),
    nav_items=(
        NavItemDefinition(
            handle="turnos.portal.nav",
            label="Mis Turnos",
            url_name="portal:ciudadano_mis_turnos",
            required_groups=("Ciudadanos",),
        ),
    ),
    web_routes=(
        UrlDefinition(
            handle="turnos.backoffice",
            route="turnos/",
            urlconf="turnos.urls",
            namespace="turnos",
            app_name="turnos",
        ),
    ),
    adapter_points=(
        "portal.views.ciudadano_turnos",
        "portal.services.turnos_ciudadano",
        "turnos.views.backoffice",
    ),
)
