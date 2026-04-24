from system_modules.definitions import ModuleDefinition, NavItemDefinition, UrlDefinition


MODULE_DEFINITION = ModuleDefinition(
    slug="chatbot",
    display_name="Chatbot",
    app_config="chatbot",
    module_type="removable",
    description="Asistente conversacional y bubble global de soporte.",
    managed_groups=("chatbotAdministrar",),
    nav_items=(
        NavItemDefinition(
            handle="chatbot.admin.nav",
            label="Chatbot",
            url_name="chatbot:admin_panel",
            required_groups=("Administrador",),
        ),
    ),
    web_routes=(
        UrlDefinition(
            handle="chatbot.ui",
            route="chatbot/",
            urlconf="chatbot.interfaces.web.urls",
            namespace="chatbot",
            app_name="chatbot",
        ),
    ),
    api_routes=(
        UrlDefinition(
            handle="chatbot.api",
            route="api/chatbot/",
            urlconf="chatbot.interfaces.api.urls",
        ),
    ),
    adapter_points=("templates/components/chatbot_bubble.html",),
)
