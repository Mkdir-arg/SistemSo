from system_modules.definitions import ModuleDefinition


MODULE_DEFINITION = ModuleDefinition(
    slug="system_modules",
    display_name="Control plane de modulos",
    app_config="system_modules",
    module_type="core",
    removable=False,
    is_core=True,
    description="Catalogo, estado activo/inactivo y capacidades publicas de modulos.",
)
