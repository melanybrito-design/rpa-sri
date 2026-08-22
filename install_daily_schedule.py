"""Instala o elimina la ejecución diaria del RPA en macOS (launchd)."""
import argparse
import os
import plistlib
import subprocess
import sys
from pathlib import Path

from config.settings import LOGS_ROOT, PROJECT_ROOT, SCHEDULE_HOUR, SCHEDULE_MINUTE

LABEL = "ec.sri.rpa-descargas"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"


def install() -> None:
    """Crea el programador con las rutas del equipo que lo instala."""
    LOGS_ROOT.mkdir(parents=True, exist_ok=True)
    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    service = {
        "Label": LABEL,
        "ProgramArguments": [str(Path(sys.executable).resolve()), str(PROJECT_ROOT / "main.py")],
        "WorkingDirectory": str(PROJECT_ROOT),
        "StartCalendarInterval": {"Hour": SCHEDULE_HOUR, "Minute": SCHEDULE_MINUTE},
        "StandardOutPath": str(LOGS_ROOT / "scheduler.out.log"),
        "StandardErrorPath": str(LOGS_ROOT / "scheduler.error.log"),
    }
    with PLIST_PATH.open("wb") as file:
        plistlib.dump(service, file)
    subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}", str(PLIST_PATH)], check=False, capture_output=True)
    subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(PLIST_PATH)], check=True)
    print(f"Programación instalada: todos los días a las {SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d}.")


def uninstall() -> None:
    if PLIST_PATH.exists():
        subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}", str(PLIST_PATH)], check=False)
        PLIST_PATH.unlink()
    print("Programación diaria eliminada.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uninstall", action="store_true", help="Elimina la programación diaria.")
    args = parser.parse_args()
    uninstall() if args.uninstall else install()
