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
    "healthcheck",
    "legajos",
    "portal",
    "system_modules",
    "tramites",
    "turnos",
    "users",
)
CANONICAL_LAYER_DIRS = (
    "domain",
    "application",
    "infrastructure",
    "interfaces",
)
CANONICAL_LAYER_FILES = (
    "domain/entities.py",
    "domain/policies.py",
    "domain/errors.py",
    "application/dto.py",
    "application/ports.py",
    "application/services.py",
    "infrastructure/orm_repositories.py",
    "infrastructure/notifications.py",
    "interfaces/module_api.py",
    "interfaces/web/urls.py",
    "interfaces/api/urls.py",
)
CANONICAL_LAYER_PATH_CANDIDATES = (
    ("infrastructure/signals.py", "infrastructure/signals/__init__.py"),
    ("interfaces/web/views.py", "interfaces/web/views/__init__.py"),
    ("interfaces/web/forms.py", "interfaces/web/forms/__init__.py"),
)
OPTIONAL_ROUTE_MODULES = ("chatbot", "conversaciones", "flujos", "tramites")
LEGACY_WRAPPER_PREFIXES = (
    "views_",
    "services_",
    "selectors_",
    "forms_",
    "signals_",
)
FORBIDDEN_PUBLIC_ENTRYPOINTS = (
    "views",
    "views.py",
    "forms",
    "forms.py",
    "services",
    "services.py",
    "selectors",
    "selectors.py",
    "signals",
    "signals.py",
    "api_views",
    "api_views.py",
    "serializers",
    "serializers.py",
    "templates",
    "static",
    "consumers.py",
    "routing.py",
    "urls.py",
    "api_urls.py",
)
FORBIDDEN_PUBLIC_IMPORT_SEGMENTS = (
    ".views",
    ".forms",
    ".services",
    ".selectors",
    ".signals",
    ".api_views",
    ".serializers",
)
OPTIONAL_MODULE_ROUTE_LITERALS = (
    "/chatbot/",
    "/api/chatbot/",
    "/conversaciones/",
    "/api/conversaciones/",
    "/ws/conversaciones/",
    "/ws/alertas/",
    "/ws/alertas-conversaciones/",
    "/tramites/",
    "/flujos/",
    "/api/flujos/",
)


def _imported_modules_from_node(node):
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        return [node.module or ""]
    return []


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

    def test_no_top_level_public_entrypoints_remain(self):
        offenders = []
        for module in MODULES_WITH_PUBLIC_CONTRACTS:
            module_path = PROJECT_ROOT / module
            if not module_path.exists():
                continue
            for entrypoint in FORBIDDEN_PUBLIC_ENTRYPOINTS:
                candidate = module_path / entrypoint
                if candidate.exists():
                    offenders.append(candidate.relative_to(PROJECT_ROOT).as_posix())

        self.assertEqual(offenders, [])

    def test_no_package_export_tests_for_legacy_facades_remain(self):
        offenders = []
        for module in MODULES_WITH_PUBLIC_CONTRACTS:
            test_path = PROJECT_ROOT / module / "tests" / "test_package_exports.py"
            if test_path.exists():
                offenders.append(test_path.relative_to(PROJECT_ROOT).as_posix())

        self.assertEqual(offenders, [])

    def test_no_imports_from_legacy_public_entrypoints(self):
        offenders = []
        ignored_parts = {"migrations", "__pycache__"}
        for path in PROJECT_ROOT.rglob("*.py"):
            if ignored_parts.intersection(path.parts):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported_names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    imported_names = [node.module or ""]
                else:
                    continue
                for imported in imported_names:
                    for module in MODULES_WITH_PUBLIC_CONTRACTS:
                        if any(
                            imported == f"{module}{segment}"
                            or imported.startswith(f"{module}{segment}.")
                            for segment in FORBIDDEN_PUBLIC_IMPORT_SEGMENTS
                        ):
                            offenders.append(
                                f"{path.relative_to(PROJECT_ROOT).as_posix()} -> {imported}"
                            )

        self.assertEqual(offenders, [])

    def test_global_static_js_does_not_hardcode_optional_module_routes(self):
        offenders = []
        static_js_root = PROJECT_ROOT / "static" / "custom" / "js"
        for path in static_js_root.rglob("*.js"):
            text = path.read_text(encoding="utf-8-sig")
            for literal in OPTIONAL_MODULE_ROUTE_LITERALS:
                if literal in text:
                    offenders.append(f"{path.relative_to(PROJECT_ROOT).as_posix()} -> {literal}")

        self.assertEqual(offenders, [])

    def test_every_project_module_declares_public_contract(self):
        missing = []
        for module in MODULES_WITH_PUBLIC_CONTRACTS:
            module_path = PROJECT_ROOT / module
            if module_path.exists() and not (module_path / "module.py").exists():
                missing.append(module)

        self.assertEqual(missing, [])

    def test_every_project_module_has_hexagonal_layout(self):
        missing = []
        for module in MODULES_WITH_PUBLIC_CONTRACTS:
            module_path = PROJECT_ROOT / module
            if not module_path.exists():
                continue
            for layer in CANONICAL_LAYER_DIRS:
                if not (module_path / layer).is_dir():
                    missing.append(f"{module}/{layer}")

        self.assertEqual(missing, [])

    def test_every_project_module_has_canonical_layer_files(self):
        missing = []
        for module in MODULES_WITH_PUBLIC_CONTRACTS:
            module_path = PROJECT_ROOT / module
            if not module_path.exists():
                continue
            for layer_file in CANONICAL_LAYER_FILES:
                if not (module_path / layer_file).is_file():
                    missing.append(f"{module}/{layer_file}")
            for candidates in CANONICAL_LAYER_PATH_CANDIDATES:
                if not any((module_path / candidate).is_file() for candidate in candidates):
                    missing.append(f"{module}/{' or '.join(candidates)}")

        self.assertEqual(missing, [])

    def test_module_declared_routes_use_canonical_interfaces(self):
        offenders = []
        for module in MODULES_WITH_PUBLIC_CONTRACTS:
            module_path = PROJECT_ROOT / module
            module_file = module_path / "module.py"
            if not module_file.exists():
                continue
            tree = ast.parse(module_file.read_text(encoding="utf-8-sig"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.keyword) or node.arg != "urlconf":
                    continue
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    if not node.value.value.startswith(f"{module}.interfaces."):
                        offenders.append(f"{module}: {node.value.value}")

        self.assertEqual(offenders, [])

    def test_domain_layers_do_not_import_django(self):
        offenders = []
        for domain_path in PROJECT_ROOT.glob("*/domain"):
            for path in domain_path.rglob("*.py"):
                tree = ast.parse(path.read_text(encoding="utf-8-sig"))
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

    def test_application_layers_do_not_import_django_or_adapters(self):
        forbidden_modules = (
            "django",
            "rest_framework",
        )
        forbidden_segments = (
            ".models",
            ".views",
            ".forms",
            ".serializers",
            ".templates",
            ".consumers",
            ".routing",
        )
        offenders = []
        for application_path in PROJECT_ROOT.glob("*/application"):
            module = application_path.parent.name
            for path in application_path.rglob("*.py"):
                tree = ast.parse(path.read_text(encoding="utf-8-sig"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported_names = [alias.name for alias in node.names]
                    elif isinstance(node, ast.ImportFrom):
                        imported_names = [node.module or ""]
                    else:
                        continue
                    for imported in imported_names:
                        if any(imported == name or imported.startswith(f"{name}.") for name in forbidden_modules):
                            offenders.append(f"{path.relative_to(PROJECT_ROOT).as_posix()} -> {imported}")
                        if any(
                            imported == f"{module}{segment}"
                            or imported.startswith(f"{module}{segment}.")
                            for segment in forbidden_segments
                        ):
                            offenders.append(f"{path.relative_to(PROJECT_ROOT).as_posix()} -> {imported}")

        self.assertEqual(offenders, [])

    def test_optional_routes_are_not_hardcoded_in_root_urlconf(self):
        urlconf = (PROJECT_ROOT / "config" / "urls.py").read_text(encoding="utf-8")
        offenders = [
            module
            for module in OPTIONAL_ROUTE_MODULES
            if f'include("{module}.' in urlconf or f"include('{module}." in urlconf
        ]

        self.assertEqual(offenders, [])

    def test_settings_do_not_reference_removable_module_context_processors(self):
        settings_text = (PROJECT_ROOT / "config" / "settings.py").read_text(encoding="utf-8")
        offenders = [
            module
            for module in OPTIONAL_ROUTE_MODULES
            if f'"{module}.context_processors.' in settings_text
            or f"'{module}.context_processors." in settings_text
        ]

        self.assertEqual(offenders, [])

    def test_non_removable_modules_do_not_import_optional_modules_at_module_load(self):
        offenders = []
        ignored_parts = {"migrations", "tests", "__pycache__"}
        non_optional_modules = set(MODULES_WITH_PUBLIC_CONTRACTS) - set(OPTIONAL_ROUTE_MODULES)
        for module in sorted(non_optional_modules):
            module_path = PROJECT_ROOT / module
            if not module_path.exists():
                continue
            for path in module_path.rglob("*.py"):
                if ignored_parts.intersection(path.parts):
                    continue
                tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
                for imported in sum((_imported_modules_from_node(node) for node in tree.body), []):
                    if any(
                        imported == optional or imported.startswith(f"{optional}.")
                        for optional in OPTIONAL_ROUTE_MODULES
                    ):
                        offenders.append(f"{path.relative_to(PROJECT_ROOT).as_posix()} -> {imported}")

        self.assertEqual(offenders, [])

    def test_non_optional_modules_only_use_optional_module_public_contracts(self):
        offenders = []
        ignored_parts = {"migrations", "tests", "__pycache__"}
        non_optional_modules = set(MODULES_WITH_PUBLIC_CONTRACTS) - set(OPTIONAL_ROUTE_MODULES)
        for module in sorted(non_optional_modules):
            module_path = PROJECT_ROOT / module
            if not module_path.exists():
                continue
            for path in module_path.rglob("*.py"):
                if ignored_parts.intersection(path.parts):
                    continue
                tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
                for node in ast.walk(tree):
                    for imported in _imported_modules_from_node(node):
                        for optional in OPTIONAL_ROUTE_MODULES:
                            if imported == optional or imported.startswith(f"{optional}."):
                                allowed = (
                                    imported == f"{optional}.interfaces.module_api"
                                    or imported.startswith(f"{optional}.interfaces.module_api.")
                                )
                                if not allowed:
                                    offenders.append(
                                        f"{path.relative_to(PROJECT_ROOT).as_posix()} -> {imported}"
                                    )

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
                tree = ast.parse(path.read_text(encoding="utf-8-sig"))
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
