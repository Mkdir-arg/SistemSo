import importlib

from django.test import SimpleTestCase


class AsgiRoutingTests(SimpleTestCase):
    def test_asgi_application_imports_catalog_websocket_routes(self):
        asgi = importlib.import_module("config.asgi")
        importlib.reload(asgi)

        self.assertIsNotNone(asgi.application)
