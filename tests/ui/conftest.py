import os
import re
from pathlib import Path

import pytest


DEFAULT_BASE_URL = "http://localhost:8000"


def pytest_addoption(parser):
    parser.addoption(
        "--e2e-base-url",
        action="store",
        default=None,
        help="Base URL for UI E2E tests. Defaults to E2E_BASE_URL or localhost:8000.",
    )


@pytest.fixture(scope="session")
def e2e_base_url(pytestconfig):
    value = pytestconfig.getoption("--e2e-base-url") or os.getenv("E2E_BASE_URL")
    return (value or DEFAULT_BASE_URL).rstrip("/")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(autouse=True)
def collect_browser_artifacts_on_failure(request, context, page):
    if "ui" not in request.node.keywords:
        yield
        return

    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield

    failed = any(
        getattr(request.node, attr, None) and getattr(request.node, attr).failed
        for attr in ("rep_setup", "rep_call", "rep_teardown")
    )
    if not failed:
        context.tracing.stop()
        return

    test_name = re.sub(r"[^a-zA-Z0-9_.-]+", "_", request.node.nodeid)
    artifact_dir = Path("test-results") / test_name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(artifact_dir / "failure.png"), full_page=True)
    context.tracing.stop(path=str(artifact_dir / "trace.zip"))
