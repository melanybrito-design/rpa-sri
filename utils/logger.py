import logging
from datetime import datetime
from pathlib import Path


def mask_ruc(ruc: str) -> str:
    return f"{ruc[:3]}{'*' * max(0, len(ruc) - 6)}{ruc[-3:]}"


def setup_logger(log_dir: Path) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("rpa_sri")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    path = log_dir / f"rpa_{datetime.now():%Y-%m-%d_%H-%M-%S}.log"
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger
