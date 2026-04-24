from system_modules.definitions import ModuleDefinition


MODULE_DEFINITION = ModuleDefinition(
    slug="healthcheck",
    display_name="Healthcheck",
    app_config="healthcheck",
    module_type="core",
    removable=False,
    is_core=True,
    description="Endpoints de salud requeridos por despliegue y Docker.",
)
