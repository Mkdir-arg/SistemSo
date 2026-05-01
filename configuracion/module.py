from system_modules.definitions import ModuleDefinition


MODULE_DEFINITION = ModuleDefinition(
    slug="configuracion",
    display_name="Configuracion",
    app_config="configuracion",
    module_type="shell",
    removable=False,
    description="Shell de configuracion operativa del sistema.",
    managed_groups=("Administrador", "programaConfigurar", "secretariaConfigurar"),
)
