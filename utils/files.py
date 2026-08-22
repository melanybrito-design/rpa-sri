import re
import sys
from pathlib import Path


def validate_ruc(ruc: str) -> bool:
    """Validación deliberadamente flexible: 13 dígitos, como acepta normalmente SRI."""
    return bool(re.fullmatch(r"\d{13}", ruc.strip()))


def create_output_folder(ruc: str, period: dict, root: Path) -> Path:
    folder = root / ruc / str(period["year"]) / f"{int(period['month']):02d}_{period['month_name']}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def safe_filename(ruc: str, period: dict, label: str, suffix: str) -> str:
    clean = re.sub(r'[<>:"/\\|?*]+', "_", label).strip(" ._")
    return f"{ruc}_{period['year']}_{int(period['month']):02d}_{clean}{suffix}"


def unique_path(folder: Path, filename: str) -> Path:
    candidate = folder / filename
    if not candidate.exists():
        return candidate
    stem, suffix = candidate.stem, candidate.suffix
    index = 1
    while True:
        candidate = folder / f"{stem}_{index:02d}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def open_folder(folder: Path) -> None:
    import os
    if sys.platform.startswith("win"):
        os.startfile(str(folder))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        import subprocess
        subprocess.run(["open", str(folder)], check=False)
    else:
        import subprocess
        subprocess.run(["xdg-open", str(folder)], check=False)
