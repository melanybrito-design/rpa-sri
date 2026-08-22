from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from sri.errors import SRIChangedError


def _click_text(page: Page, text: str) -> None:
    locator = page.get_by_text(text, exact=True).first
    try:
        # SRI renderiza los submenús después de expandir la categoría. `is_visible`
        # no espera; esta espera explícita evita intentar el segundo clic antes de tiempo.
        locator.wait_for(state="visible")
        locator.click()
    except PlaywrightTimeoutError as exc:
        raise SRIChangedError(f'No se encontró "{text}". Es posible que el SRI haya cambiado su interfaz.')


def _expand_side_menu(page: Page) -> None:
    """Expande el menú cuando SRI lo deja en modo reducido de solo íconos."""
    target = page.get_by_text("FACTURACIÓN ELECTRÓNICA", exact=True).first
    try:
        target.wait_for(state="visible", timeout=1_000)
        return
    except PlaywrightTimeoutError:
        pass

    candidates = (
        "[aria-label*='menú' i]", "[aria-label*='menu' i]",
        "[title*='menú' i]", "[title*='menu' i]",
        "button:has-text('☰')",
    )
    for selector in candidates:
        toggle = page.locator(selector).first
        if toggle.count() and toggle.is_visible():
            toggle.click()
            target.wait_for(state="visible")
            return
    # Último recurso semántico: en la vista mostrada por SRI el primer botón
    # visible del encabezado es el icono hamburguesa del menú lateral.
    for toggle in page.get_by_role("button").all():
        if toggle.is_visible():
            toggle.click()
            try:
                target.wait_for(state="visible", timeout=3_000)
                return
            except PlaywrightTimeoutError:
                continue
    raise SRIChangedError("No se encontró el control para expandir el menú lateral del SRI.")


def navigate_to_comprobantes_recibidos(page: Page) -> None:
    # Textos visibles en la captura facilitada; no usa coordenadas ni clases dinámicas.
    _expand_side_menu(page)
    _click_text(page, "FACTURACIÓN ELECTRÓNICA")
    _click_text(page, "Comprobantes electrónicos recibidos")
    page.wait_for_load_state("domcontentloaded")
