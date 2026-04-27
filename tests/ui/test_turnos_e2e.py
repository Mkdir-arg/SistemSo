import re
import unittest
from datetime import date, timedelta

try:
    import pytest
    from playwright.sync_api import expect
except ModuleNotFoundError as exc:
    raise unittest.SkipTest("UI E2E requiere pytest-playwright y se ejecuta con run-ui-tests.ps1") from exc

from tests.ui.helpers import (
    E2E_CITIZEN_DNI,
    E2E_RESOURCE_NAME,
    E2E_TURNO_MOTIVO,
    login_ciudadano,
    login_operador,
    logout_ciudadano,
)


pytestmark = pytest.mark.ui


def test_ciudadano_solicita_turno_y_operador_lo_aprueba(page, e2e_base_url):
    target_date = date.today() + timedelta(days=1)

    login_ciudadano(page, e2e_base_url)
    page.goto(f"{e2e_base_url}/portal/mi-perfil/turnos/solicitar/")

    resource_card = page.locator("h4", has_text=E2E_RESOURCE_NAME).locator(
        "xpath=ancestor::div[contains(@class, 'bg-white')][1]"
    )
    expect(resource_card).to_be_visible()
    resource_card.get_by_role("link", name=re.compile(r"Elegir horario", re.I)).click()

    calendar_url = page.url.split("?")[0]
    page.goto(f"{calendar_url}?anio={target_date.year}&mes={target_date.month}")
    page.get_by_role("button", name=str(target_date.day), exact=True).click()

    slot = page.get_by_role("button", name=re.compile(r"09:00\s*-\s*09:30"))
    expect(slot).to_be_visible()
    slot.click()

    continue_link = page.get_by_role("link", name=re.compile(r"Continuar", re.I))
    expect(continue_link).to_be_visible()
    expect(continue_link).to_have_attribute(
        "href", re.compile(r"/portal/mi-perfil/turnos/solicitar/\d+/confirmar/\?fecha=")
    )
    continue_link.click()
    expect(page).to_have_url(re.compile(r"/confirmar/\?fecha="))

    expect(page.get_by_text(E2E_RESOURCE_NAME)).to_be_visible()
    page.locator("#motivo").fill(E2E_TURNO_MOTIVO)
    page.get_by_role("button", name=re.compile(r"Confirmar turno", re.I)).click()

    expect(page.get_by_text(re.compile(r"Turno en espera", re.I))).to_be_visible()
    expect(page.get_by_text(re.compile(r"Pendiente", re.I))).to_be_visible()

    logout_ciudadano(page)
    login_operador(page, e2e_base_url)

    pending_row = page.locator("tr", has_text=E2E_RESOURCE_NAME).filter(
        has_text=E2E_CITIZEN_DNI
    ).first
    expect(pending_row).to_be_visible()
    pending_row.get_by_role("button", name=re.compile(r"Aprobar", re.I)).click()

    expect(page.get_by_text(re.compile(r"Turno .* confirmado", re.I))).to_be_visible()
    expect(
        page.get_by_role("heading", name=re.compile(r"Sin turnos pendientes", re.I))
    ).to_be_visible()

    page.context.clear_cookies()
    login_ciudadano(page, e2e_base_url)
    page.goto(f"{e2e_base_url}/portal/mi-perfil/turnos/")

    confirmed_turn = page.locator("p", has_text=E2E_RESOURCE_NAME).locator(
        "xpath=ancestor::div[contains(@class, 'rounded-xl')][1]"
    ).filter(has_text="Confirmado")
    expect(confirmed_turn).to_be_visible()
