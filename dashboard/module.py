from system_modules.definitions import ModuleDefinition


MODULE_DEFINITION = ModuleDefinition(
    slug="dashboard",
    display_name="Dashboard",
    app_config="dashboard",
    module_type="shell",
    removable=False,
    description="Shell de metricas e indicadores del backoffice.",
    managed_groups=("dashboardVer",),
)
