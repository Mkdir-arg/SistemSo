import ast
from pathlib import Path

from django.test import SimpleTestCase


class TurnosArchitectureTests(SimpleTestCase):
    def _imports_for(self, relative_folder):
        folder = Path(__file__).resolve().parents[1] / relative_folder
        imports = []
        for path in folder.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)
        return imports

    def test_domain_layer_does_not_import_django(self):
        imports = self._imports_for("domain")
        self.assertFalse(any(name.startswith("django") for name in imports), imports)

    def test_application_layer_does_not_import_views_or_forms(self):
        imports = self._imports_for("application")
        self.assertFalse(
            any(
                name.startswith("turnos.views")
                or name.startswith("turnos.forms")
                or name.startswith("portal.views")
                for name in imports
            ),
            imports,
        )
