import logging
from pathlib import Path
from playwright.sync_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError

from config.settings import COMPROBANTES, LOGS_ROOT, MAX_RETRIES, OUTPUT_ROOT, SRI_PASSWORD, SRI_RUC
from sri.browser import create_browser
from sri.downloads import download_report
from sri.errors import NoResultsError, SRIError
from sri.login import login
from sri.navigation import navigate_to_comprobantes_recibidos
from sri.comprobantes import select_period
from utils.dates import get_current_period
from utils.files import create_output_folder
from utils.logger import mask_ruc, setup_logger

def existing_report(output_folder: Path, ruc: str, period: dict, comprobante: dict) -> Path | None:
    """Evita descargar otra vez un tipo que ya fue guardado correctamente."""
    prefix = f"{ruc}_{period['year']}_{int(period['month']):02d}_{comprobante['nombre_archivo']}"
    return next((path for path in output_folder.glob(f"{prefix}.*") if path.is_file() and path.stat().st_size > 0), None)


def main() -> int:
    print("=" * 50 + "\n       RPA SRI - COMPROBANTES ELECTRÓNICOS\n" + "=" * 50)
    ruc, password = SRI_RUC, SRI_PASSWORD
    period = get_current_period()
    print(f"Período automático: {period['month_name']} {period['year']}")
    output_folder = create_output_folder(ruc, period, OUTPUT_ROOT)
    logger = setup_logger(LOGS_ROOT)
    logger.info("Inicio RUC=%s período=%s", mask_ruc(ruc), period)
    results: dict[str, str] = {}
    resources = None
    had_errors = False
    try:
        print("\n[1/8] Abriendo SRI...")
        resources = create_browser()
        _, _, _, page = resources
        print("[2/8] Iniciando sesión...")
        page = login(page, ruc, password)
        print("[OK] Sesión iniciada\n[3/8] Accediendo a Facturación Electrónica...")
        navigate_to_comprobantes_recibidos(page)
        print("[OK]\n[4/8] Configurando período...")
        select_period(page, period)
        print("[OK]")
        for index, comprobante in enumerate(COMPROBANTES, start=1):
            name = comprobante["nombre"]
            print(f"[{index}/{len(COMPROBANTES)}] Procesando {name}...")
            existing = existing_report(output_folder, ruc, period, comprobante)
            if existing:
                results[name] = f"existente: {existing.name}"
                print("[INFO] Reporte ya existente; se omite para no duplicarlo")
                continue
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    path = download_report(page, comprobante, output_folder, ruc, period, logger)
                    results[name] = f"descargado: {path.name}"
                    print("[OK] Reporte descargado")
                    break
                except NoResultsError:
                    results[name] = "sin resultados"
                    print("[INFO] No se encontraron comprobantes")
                    break
                except (SRIError, PlaywrightError, PlaywrightTimeoutError) as exc:
                    logger.exception("Intento %s de %s: %s", attempt, name, exc)
                    if attempt == MAX_RETRIES:
                        had_errors = True
                        results[name] = f"error: {exc}"
                        print(f"[ERROR] {exc}")
                    else:
                        print(f"[AVISO] Intento {attempt}/{MAX_RETRIES} falló; reintentando.")
    except SRIError as exc:
        had_errors = True
        logger.exception("Error crítico: %s", exc)
        print(f"\n[ERROR] {exc}")
    except Exception as exc:
        had_errors = True
        logger.exception("Error inesperado")
        print(f"\n[ERROR] Error inesperado: {exc}")
    finally:
        password = ""  # elimina la referencia local a la contraseña
        if resources:
            playwright, browser, context, _ = resources
            context.close(); browser.close(); playwright.stop()
    print("\n" + "=" * 50 + "\nPROCESO FINALIZADO\n" + "=" * 50)
    print(f"Período: {period['month_name']} {period['year']}\n\nResultados:")
    for name in (item["nombre"] for item in COMPROBANTES):
        status = results.get(name, "no procesado")
        print(f"{'✓' if status.startswith(('descargado', 'existente')) else '⚠'} {name}: {status}")
    downloaded = sum(value.startswith("descargado") for value in results.values())
    if downloaded:
        print(f"\n✓ REPORTES DESCARGADOS CON ÉXITO: {downloaded}")
    else:
        print("\n⚠ No se descargaron reportes nuevos en esta ejecución.")
    print(f"\nTotal de archivos descargados en esta ejecución: {downloaded}")
    if downloaded:
        print("\nArchivos descargados:")
        for value in results.values():
            if value.startswith(("descargado", "existente")):
                print(f"- {value.split(': ', 1)[1]}")
    print(f"\nCARPETA DE REPORTES:\n{output_folder.resolve()}")
    return 1 if had_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
