import logging
from pathlib import Path
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from config.settings import DOWNLOAD_TIMEOUT
from sri.comprobantes import consult, has_no_results, select_comprobante_type
from sri.errors import DownloadFailedError, NoResultsError
from utils.files import safe_filename, unique_path


def download_report(page: Page, tipo_comprobante: dict, output_folder: Path, ruc: str, period: dict, logger: logging.Logger) -> Path:
    select_comprobante_type(page, tipo_comprobante)
    consult(page)
    if has_no_results(page):
        raise NoResultsError(tipo_comprobante["nombre"])
    button = page.get_by_role("button", name="Descargar").or_(page.get_by_text("Descargar", exact=False)).first
    if not button.is_visible():
        raise DownloadFailedError(f'No se encontró descarga para {tipo_comprobante["nombre"]}.')
    try:
        with page.expect_download(timeout=DOWNLOAD_TIMEOUT) as event:
            button.click()
        download = event.value
        suffix = Path(download.suggested_filename).suffix or ".xlsx"
        destination = unique_path(output_folder, safe_filename(ruc, period, tipo_comprobante["nombre_archivo"], suffix))
        download.save_as(destination)
    except PlaywrightTimeoutError as exc:
        raise DownloadFailedError(f"La descarga de {tipo_comprobante['nombre']} agotó el tiempo de espera.") from exc
    if not destination.exists() or destination.stat().st_size == 0:
        raise DownloadFailedError(f"El archivo descargado de {tipo_comprobante['nombre']} no es válido.")
    logger.info("Descarga correcta: %s", destination.name)
    return destination
