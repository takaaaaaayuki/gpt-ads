from __future__ import annotations

import hashlib

from project.models import SourceItem


def _fingerprint(item: SourceItem) -> str:
    if item.url:
        return item.url.strip().lower()
    base = f"{item.source}:{item.title}:{item.text[:300]}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def dedupe_items(items: list[SourceItem]) -> list[SourceItem]:
    seen: set[str] = set()
    unique: list[SourceItem] = []
    for item in items:
        key = _fingerprint(item)
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique

