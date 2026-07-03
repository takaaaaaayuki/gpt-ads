from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from project.models import SourceItem


def write_jsonl(path: Path, items: Iterable[SourceItem]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for item in items:
            fh.write(json.dumps(item.to_dict(), ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[SourceItem]:
    if not path.exists():
        return []
    items: list[SourceItem] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            items.append(SourceItem.from_dict(json.loads(line)))
    return items


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

