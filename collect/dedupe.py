from __future__ import annotations

import hashlib
import re
import unicodedata
from urllib.parse import urlparse

from project.models import SourceItem


def _url_key(item: SourceItem) -> str:
    return item.url.strip().lower()


def _normalized_title(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").lower()
    value = re.sub(r"https?://\S+", "", value)
    value = re.sub(r"[\s\u3000]+", "", value)
    return re.sub(r"[「」『』【】\[\]（）()\-_ー–—:：|｜,，.。!！?？/\\・~〜]", "", value)


def _content_key(item: SourceItem) -> str:
    title = _normalized_title(item.title)
    if len(title) >= 8:
        return f"{item.source}:title:{title}"
    base = f"{item.source}:{item.title}:{item.text[:300]}"
    return f"{item.source}:fallback:{hashlib.sha256(base.encode('utf-8')).hexdigest()}"


def _is_google_news_url(url: str) -> bool:
    return urlparse(url).netloc.lower().replace("www.", "") == "news.google.com"


def _quality_score(item: SourceItem) -> tuple[int, int, int, int, int]:
    url = item.url.strip()
    return (
        0 if _is_google_news_url(url) else 1,
        1 if url else 0,
        len(item.summary or ""),
        len(item.text or ""),
        len(item.points or []),
    )


def dedupe_items(items: list[SourceItem]) -> list[SourceItem]:
    unique: list[SourceItem] = []
    index_by_key: dict[str, int] = {}

    for item in items:
        keys = [_content_key(item)]
        if item.url:
            keys.append(f"url:{_url_key(item)}")

        existing_indexes = {index_by_key[key] for key in keys if key in index_by_key}
        if not existing_indexes:
            index = len(unique)
            unique.append(item)
            for key in keys:
                index_by_key[key] = index
            continue

        index = min(existing_indexes)
        current = unique[index]
        if _quality_score(item) > _quality_score(current):
            unique[index] = item

        for key in keys:
            index_by_key[key] = index

    return unique
