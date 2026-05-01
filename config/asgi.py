import os
import django
from django.core.asgi import get_asgi_application
from importlib import import_module

# Configure Django FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import after Django setup
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from system_modules.registry import get_module_registry


def _websocket_urlpatterns():
    patterns = []
    for _definition, route in get_module_registry().websocket_routes():
        module = import_module(route.urlconf)
        patterns.extend(getattr(module, route.attribute))
    return patterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            _websocket_urlpatterns()
        )
    ),
})
