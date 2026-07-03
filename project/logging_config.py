from __future__ import annotations

import logging
from pathlib import Path

from project.settings import LOG_DIR


def configure_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

