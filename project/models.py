from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class SourceItem:
    source: str
    title: str
    url: str
    text: str = ""
    author: str = ""
    published_at: str = ""
    category: str = ""
    importance: str = "C"
    summary: str = ""
    points: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def stable_id(self) -> str:
        key = self.url or f"{self.source}:{self.title}:{self.text[:120]}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["id"] = self.stable_id
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SourceItem":
        allowed = cls.__dataclass_fields__.keys()
        return cls(**{k: data.get(k) for k in allowed if k in data})


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

