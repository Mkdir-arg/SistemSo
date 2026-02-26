import os
import django
from django.core.asgi import get_asgi_application

# Configure Django FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import after Django setup
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import conversaciones.routing
import ai_squad.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            conversaciones.routing.websocket_urlpatterns
            + ai_squad.routing.websocket_urlpatterns
        )
    ),
})