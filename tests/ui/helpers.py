import re

from playwright.sync_api import Page, expect


E2E_PASSWORD = "E2eTurnos123!"
E2E_CITIZEN_DNI = "88000001"
E2E_OPERATOR_USERNAME = "e2e_turnos_operador"
E2E_RESOURCE_NAME = "E2E Turnos Recurso"
E2E_TURNO_MOTIVO = "E2E Turnos solicitud automatizada"


def login_ciudadano(page: Page, base_url: str) -> None:
    page.goto(f"{base_url}/portal/mi-perfil/login/")
    page.locator('input[name="username"]').fill(E2E_CITIZEN_DNI)
    page.locator('input[name="password"]').fill(E2E_PASSWORD)
    page.locator('button[type="submit"]').click()
    expect(page).to_have_url(re.compile(r".*/portal/mi-perfil/$"))


def logout_ciudadano(page: Page) -> None:
    page.locator('form[action="/portal/mi-perfil/logout/"] button[type="submit"]').click()
    expect(page.locator('input[name="username"]')).to_be_visible()


def login_operador(page: Page, base_url: str) -> None:
    page.goto(f"{base_url}/?next=/turnos/pendientes/")
    page.locator('input[name="username"]').fill(E2E_OPERATOR_USERNAME)
    page.locator('input[name="password"]').fill(E2E_PASSWORD)
    page.locator('button[type="submit"]').click()
    expect(page).to_have_url(re.compile(r".*/turnos/pendientes/$"))
