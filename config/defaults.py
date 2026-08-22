"""Valores compartidos que no contienen información privada."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRI_URL = "https://srienlinea.sri.gob.ec/sri-en-linea/inicio/NAT"
OUTPUT_ROOT = Path.home() / "Desktop" / "Reportes_SRI"
LOGS_ROOT = PROJECT_ROOT / "logs"

SCHEDULE_HOUR = 10
SCHEDULE_MINUTE = 0

DEFAULT_TIMEOUT = 20_000
NAVIGATION_TIMEOUT = 60_000
DOWNLOAD_TIMEOUT = 60_000
MAX_RETRIES = 3
HEADLESS = True

COMPROBANTES = (
    {"nombre": "Facturas", "aliases": ("Factura", "Facturas", "FACTURA"), "nombre_archivo": "Facturas"},
    {"nombre": "Notas de crédito", "aliases": ("Nota de crédito", "Notas de crédito", "Nota de Credito", "Notas de Credito", "Nota crédito", "NOTA DE CREDITO"), "nombre_archivo": "Notas_Credito"},
    {"nombre": "Notas de débito", "aliases": ("Nota de débito", "Notas de débito", "Nota de Debito", "Notas de Debito", "Nota débito", "NOTA DE DEBITO"), "nombre_archivo": "Notas_Debito"},
    {"nombre": "Retenciones", "aliases": ("Retención", "Retencion", "Comprobante de retención", "COMPROBANTE DE RETENCION"), "nombre_archivo": "Retenciones"},
)

MONTHS_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}
