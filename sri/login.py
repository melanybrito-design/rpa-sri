import re

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from config.settings import DEFAULT_TIMEOUT, MAX_RETRIES, SRI_URL
from sri.errors import AuthenticationError, CaptchaPendingError, SiteUnavailableError


def _first_visible(page: Page, selectors: list[str]):
    for selector in selectors:
        locator = page.locator(selector).first
        if locator.count() and locator.is_visible():
            return locator
    return None


def open_login(page: Page) -> Page:
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            page.goto(SRI_URL, wait_until="domcontentloaded")
            # El SRI puede exponer el acceso como enlace, botón o elemento con texto
            # fragmentado; el selector por texto cubre esas tres variantes.
            button = page.get_by_text(re.compile(r"iniciar\s+sesi[oó]n", re.I)).first
            button.wait_for(state="visible")
            pages_before = set(page.context.pages)
            button.click()
            # Algunas versiones abren el formulario en otra pestaña. Continuar con
            # esa página, no con la portada que queda abierta detrás.
            page.wait_for_timeout(500)
            new_pages = [item for item in page.context.pages if item not in pages_before]
            if new_pages:
                page = new_pages[-1]
                page.wait_for_load_state("domcontentloaded")
            return page
        except PlaywrightTimeoutError as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                print(f"[AVISO] SRI tardó en responder; reintentando ({attempt}/{MAX_RETRIES})...")
                page.wait_for_timeout(2_000)
    raise SiteUnavailableError(f"El portal SRI no respondió tras {MAX_RETRIES} intentos.") from last_error


def login(page: Page, ruc: str, password: str) -> Page:
    page = open_login(page)
    # El formulario se muestra de forma asíncrona en SRI; esperar evita leer la
    # página de inicio antes de que el componente de autenticación se haya renderizado.
    password_input = page.locator("input[type='password']").first
    try:
        password_input.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
    except PlaywrightTimeoutError as exc:
        raise AuthenticationError("No apareció el formulario de inicio de sesión del SRI.") from exc
    ruc_input = _first_visible(page, [
        "input[name*='ruc' i]", "input[id*='ruc' i]", "input[placeholder*='ruc' i]",
        "input[name*='ident' i]", "input[id*='ident' i]", "input[placeholder*='ident' i]",
        "input[name*='usuario' i]", "input[id*='usuario' i]",
    ])
    # Si SRI cambia el atributo del usuario, usar el otro campo visible del
    # mismo formulario que contiene la contraseña, nunca el buscador del menú.
    if not ruc_input:
        form = password_input.locator("xpath=ancestor::form[1]")
        candidates = form.locator("input:not([type='password']):not([type='hidden'])")
        for candidate in candidates.all():
            if candidate.is_visible():
                ruc_input = candidate
                break
    if not ruc_input or not password_input:
        raise AuthenticationError("No se encontraron los campos de inicio de sesión del SRI.")
    ruc_input.fill(ruc)
    password_input.fill(password)
    submit = page.get_by_role("button", name="Ingresar").or_(page.get_by_role("button", name="Iniciar sesión")).first
    submit.click()
    wait_for_authenticated_session(page)
    return page


def wait_for_authenticated_session(page: Page) -> None:
    print("\nSi el SRI solicita una verificación, complétela manualmente en el navegador.")
    print("El proceso continuará al detectarse la sesión iniciada.")
    try:
        page.wait_for_function("""() => {
          const text = document.body.innerText.toLowerCase();
          const authenticatedPath = location.pathname.includes('/contribuyente/');
          return !text.includes('captcha') && (authenticatedPath || text.includes('cerrar sesión') || text.includes('mi perfil'));
        }""", timeout=180_000)
    except PlaywrightTimeoutError as exc:
        text = page.locator("body").inner_text().lower()
        if "incorrect" in text or "inválid" in text or "error" in text:
            raise AuthenticationError("Credenciales incorrectas o rechazadas por el SRI.") from exc
        raise CaptchaPendingError("No se detectó una sesión iniciada tras tres minutos. Revise CAPTCHA o credenciales.") from exc
