from system_modules.definitions import ModuleDefinition


FLUJOS_MODULE = ModuleDefinition(
    slug="flujos",
    display_name="Flujos",
    description="Editor visual y runtime del motor de flujos.",
    managed_groups=("programaConfigurar",),
    route_handles=("flujos.editor",),
    api_handles=("flujos.api",),
    adapter_points=("configuracion/templates/configuracion/programa_list.html",),
)
