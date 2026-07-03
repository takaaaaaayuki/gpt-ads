from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "sources.json"
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORTS_DIR = ROOT / "reports"
PUBLIC_DIR = ROOT / "public"
LOG_DIR = ROOT / "logs"


def load_dotenv(path: Path | None = None) -> None:
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(ROOT / ".ms-playwright"))
    env_path = path or ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_sources(path: Path | None = None) -> dict[str, Any]:
    config_path = path or CONFIG_PATH
    return json.loads(config_path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class RuntimeOptions:
    max_items_per_run: int
    min_importance: str
    use_sample_data: bool = False


def runtime_options(use_sample_data: bool = False) -> RuntimeOptions:
    return RuntimeOptions(
        max_items_per_run=int(os.getenv("GPT_ADS_MAX_ITEMS_PER_RUN", "20")),
        min_importance=os.getenv("GPT_ADS_MIN_IMPORTANCE", "B").upper(),
        use_sample_data=use_sample_data or os.getenv("GPT_ADS_USE_SAMPLE_DATA", "0") == "1",
    )


def ensure_dirs() -> None:
    for directory in [RAW_DIR, PROCESSED_DIR, REPORTS_DIR, PUBLIC_DIR, LOG_DIR, PUBLIC_DIR / "data"]:
        directory.mkdir(parents=True, exist_ok=True)
