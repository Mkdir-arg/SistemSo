from system_modules.definitions import ModuleDefinition, NavItemDefinition


TURNOS_MODULE = ModuleDefinition(
    slug="turnos",
    display_name="Turnos",
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
    route_handles=("turnos.backoffice", "turnos.portal"),
    api_handles=("turnos.backoffice.api", "turnos.portal.api"),
    adapter_points=(
        "portal.views.ciudadano_turnos",
        "portal.services.turnos_ciudadano",
        "turnos.views.backoffice",
    ),
)
