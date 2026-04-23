from system_modules.definitions import ModuleDefinition, NavItemDefinition


CHATBOT_MODULE = ModuleDefinition(
    slug="chatbot",
    display_name="Chatbot",
    description="Asistente conversacional y bubble global de soporte.",
    nav_items=(
        NavItemDefinition(
            handle="chatbot.admin.nav",
            label="Chatbot",
            url_name="chatbot:admin_panel",
            required_groups=("Administrador",),
        ),
    ),
    route_handles=("chatbot.ui", "chatbot.admin"),
    api_handles=("chatbot.api",),
    adapter_points=("templates/components/chatbot_bubble.html",),
)
