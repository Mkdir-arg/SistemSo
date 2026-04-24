from system_modules.definitions import ModuleDefinition


MODULE_DEFINITION = ModuleDefinition(
    slug="legajos",
    display_name="Legajos",
    app_config="legajos",
    module_type="non_removable",
    removable=False,
    description="Ciudadanos, legajos, programas, instituciones, contactos y NACHEC.",
    managed_groups=("ciudadanoVer", "ciudadanoCrear", "programaOperar", "reportesVer"),
)
