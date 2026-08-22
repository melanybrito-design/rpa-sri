import unicodedata

from playwright.sync_api import Error as PlaywrightError, Page, TimeoutError as PlaywrightTimeoutError
from config.settings import DEFAULT_TIMEOUT
from sri.errors import ElementNotFoundError, SRIChangedError


def _normalise(text: str) -> str:
    return "".join(char for char in unicodedata.normalize("NFD", text.casefold()) if unicodedata.category(char) != "Mn").strip()


def _matching_option(options: list[str], values: tuple[str, ...]) -> str | None:
    normalized = {_normalise(value) for value in values}
    exact = next((option for option in options if _normalise(option) in normalized), None)
    if exact:
        return exact
    # SRI alterna singular/plural y a veces omite palabras de enlace. Comparar
    # las palabras relevantes permite seleccionar, por ejemplo, "Notas crédito".
    ignored = {"de", "del", "la", "el", "comprobante"}
    for option in options:
        option_words = set(_normalise(option).split())
        for value in values:
            words = {word for word in _normalise(value).split() if word not in ignored}
            if words and words.issubset(option_words):
                return option
    return None


def _select_by_label_or_option(page: Page, labels: tuple[str, ...], values: tuple[str, ...]):
    for label in labels:
        control = page.get_by_label(label, exact=False)
        if control.count():
            option = _matching_option(control.locator("option").all_inner_texts(), values)
            if option:
                try:
                    control.select_option(label=option)
                    return control
                except PlaywrightError:
                    pass
    for select in page.locator("select").all():
        options = select.locator("option").all_inner_texts()
        option = _matching_option(options, values)
        if option:
            try:
                select.select_option(label=option)
                return select
            except PlaywrightError:
                continue
    raise ElementNotFoundError(f"No se encontró un selector compatible con: {', '.join(values)}")


def select_period(page: Page, period: dict) -> None:
    year_control = _select_by_label_or_option(page, ("Año", "Anio", "Periodo año"), (str(period["year"]),))
    month_control = _select_by_label_or_option(page, ("Mes", "Periodo mes"), (str(period["month"]), str(period["month_name"])))
    all_control = _select_by_label_or_option(page, ("Día", "Dia", "Fecha", "Periodo emisión"), ("Todos", "Todas"))
    selected_year = year_control.locator("option:checked").inner_text().strip()
    selected_month = month_control.locator("option:checked").inner_text().strip()
    selected_day = all_control.locator("option:checked").inner_text().strip()
    expected_month = (str(period["month"]), str(period["month"]).zfill(2), str(period["month_name"]).lower())
    if str(period["year"]) not in selected_year or not any(value in selected_month.lower() for value in expected_month):
        raise SRIChangedError("El período seleccionado no coincide con el período solicitado.")
    if _normalise(selected_day) not in {"todos", "todas"}:
        raise SRIChangedError('El filtro de día no quedó seleccionado en "Todos".')


def select_comprobante_type(page: Page, comprobante: dict) -> None:
    aliases = tuple(comprobante["aliases"])
    _select_by_label_or_option(page, ("Tipo de comprobante", "Tipo comprobante", "Comprobante"), aliases)


def consult(page: Page) -> None:
    button = page.get_by_role("button", name="Consultar").or_(page.get_by_text("Consultar", exact=True)).first
    if not button.is_visible():
        raise SRIChangedError('No se encontró el botón "Consultar". Es posible que el SRI haya cambiado su interfaz.')
    previous_content = page.locator("body").inner_text()
    button.click()
    # La pantalla es una aplicación dinámica: DOMContentLoaded ya ocurrió y no
    # indica que el resultado cambió. Esperar el cambio visible evita descargar
    # el reporte del tipo consultado anteriormente.
    try:
        page.wait_for_function(
            "previous => document.body.innerText !== previous",
            arg=previous_content,
            timeout=DEFAULT_TIMEOUT,
        )
    except PlaywrightTimeoutError as exc:
        raise SRIChangedError("La consulta no actualizó resultados; no se intentó descargar un reporte anterior.") from exc


def has_no_results(page: Page) -> bool:
    text = page.locator("body").inner_text().lower()
    return any(phrase in text for phrase in (
        "no se encontraron", "no existen registros", "no existen datos", "sin resultados",
    ))
