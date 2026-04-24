import ast
from pathlib import Path

from django.test import SimpleTestCase


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODULES_WITH_PUBLIC_CONTRACTS = (
    "chatbot",
    "conversaciones",
    "configuracion",
    "core",
    "dashboard",
    "flujos",
    "legajos",
    "portal",
    "tramites",
    "turnos",
    "users",
)
OPTIONAL_ROUTE_MODULES = ("chatbot", "conversaciones", "flujos", "tramites")
LEGACY_WRAPPER_PREFIXES = (
    "views_",
    "services_",
    "selectors_",
    "forms_",
    "signals_",
)


class ModularArchitectureTests(SimpleTestCase):
    def test_public_legacy_wrappers_are_removed(self):
        offenders = []
        for module in MODULES_WITH_PUBLIC_CONTRACTS:
            module_path = PROJECT_ROOT / module
            if not module_path.exists():
                continue
            for path in module_path.glob("*.py"):
                if path.name.startswith(LEGACY_WRAPPER_PREFIXES):
                    offenders.append(path.relative_to(PROJECT_ROOT).as_posix())

        self.assertEqual(offenders, [])

    def test_every_project_module_declares_public_contract(self):
        missing = []
        for module in MODULES_WITH_PUBLIC_CONTRACTS:
            module_path = PROJECT_ROOT / module
            if module_path.exists() and not (module_path / "module.py").exists():
                missing.append(module)

        self.assertEqual(missing, [])

    def test_domain_layers_do_not_import_django(self):
        offenders = []
        for domain_path in PROJECT_ROOT.glob("*/domain"):
            for path in domain_path.rglob("*.py"):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        names = [alias.name for alias in node.names]
                    elif isinstance(node, ast.ImportFrom):
                        names = [node.module or ""]
                    else:
                        continue
                    if any(name == "django" or name.startswith("django.") for name in names):
                        offenders.append(path.relative_to(PROJECT_ROOT).as_posix())

        self.assertEqual(offenders, [])

    def test_optional_routes_are_not_hardcoded_in_root_urlconf(self):
        urlconf = (PROJECT_ROOT / "config" / "urls.py").read_text(encoding="utf-8")
        offenders = [
            module
            for module in OPTIONAL_ROUTE_MODULES
            if f'include("{module}.' in urlconf or f"include('{module}." in urlconf
        ]

        self.assertEqual(offenders, [])

    def test_removable_modules_do_not_import_other_module_internals(self):
        internal_segments = (".views", ".forms", ".services", ".selectors")
        offenders = []
        for module in OPTIONAL_ROUTE_MODULES:
            module_path = PROJECT_ROOT / module
            if not module_path.exists():
                continue
            for path in module_path.rglob("*.py"):
                if "tests" in path.parts:
                    continue
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if not isinstance(node, ast.ImportFrom) or not node.module:
                        continue
                    for other in MODULES_WITH_PUBLIC_CONTRACTS:
                        if other == module:
                            continue
                        if any(
                            node.module == f"{other}{segment}"
                            or node.module.startswith(f"{other}{segment}.")
                            for segment in internal_segments
                        ):
                            offenders.append(
                                f"{path.relative_to(PROJECT_ROOT).as_posix()} -> {node.module}"
                            )

        self.assertEqual(offenders, [])
