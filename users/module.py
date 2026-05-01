from system_modules.definitions import ModuleDefinition


MODULE_DEFINITION = ModuleDefinition(
    slug="users",
    display_name="Usuarios y permisos",
    app_config="users",
    module_type="core",
    removable=False,
    is_core=True,
    description="Autenticacion, usuarios backoffice y asignacion de grupos.",
    managed_groups=("usuarioAdministrar", "Administrador"),
)
