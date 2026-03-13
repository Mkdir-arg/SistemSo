from importlib import import_module

from django.test import SimpleTestCase


class DashboardPackageExportsTests(SimpleTestCase):
    def test_views_and_signals_packages_are_importable(self):
        from dashboard.views import DashboardView

        self.assertIsNotNone(DashboardView)
        self.assertIsNotNone(import_module("dashboard.signals"))
