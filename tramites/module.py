from system_modules.definitions import ModuleDefinition


TRAMITES_MODULE = ModuleDefinition(
    slug="tramites",
    display_name="Tramites",
    description="Gestion backoffice de tramites institucionales.",
    managed_groups=("Administrador", "Supervisor"),
    route_handles=("tramites.backoffice",),
    adapter_points=("templates/includes/sidebar/opciones.html",),
)
