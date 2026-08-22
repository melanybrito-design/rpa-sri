from datetime import datetime
from config.defaults import MONTHS_ES


def get_current_period(now: datetime | None = None) -> dict[str, int | str]:
    now = now or datetime.now()
    return {"year": now.year, "month": now.month, "month_name": MONTHS_ES[now.month]}


def get_period_from_input() -> dict[str, int | str]:
    period = get_current_period()
    print(f"\nPeríodo detectado automáticamente: {period['month_name']} {period['year']}")
    if input("¿Desea utilizar este período? [S/n]: ").strip().lower() not in {"n", "no"}:
        return period
    while True:
        try:
            year = int(input("Año: ").strip())
            month = int(input("Mes (1-12): ").strip())
            if year >= 2000 and month in MONTHS_ES:
                return {"year": year, "month": month, "month_name": MONTHS_ES[month]}
        except ValueError:
            pass
        print("[ERROR] Ingrese un año válido y un mes entre 1 y 12.")
