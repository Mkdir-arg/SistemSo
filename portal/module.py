from system_modules.definitions import ModuleDefinition


MODULE_DEFINITION = ModuleDefinition(
    slug="portal",
    display_name="Portal ciudadano",
    app_config="portal",
    module_type="shell",
    removable=False,
    description="Shell publico para ciudadanos e instituciones externas.",
    managed_groups=("Ciudadanos", "EncargadoInstitucion"),
)
