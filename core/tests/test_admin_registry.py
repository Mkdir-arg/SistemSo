from django.contrib import admin
from django.test import SimpleTestCase

from core.models_secretaria import Secretaria, Subsecretaria


class CoreAdminRegistryTests(SimpleTestCase):
    def test_secretaria_and_subsecretaria_are_registered_in_admin(self):
        self.assertIn(Secretaria, admin.site._registry)
        self.assertIn(Subsecretaria, admin.site._registry)