from __future__ import annotations

import html
import logging
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from typing import Any

from project.models import SourceItem

LOGGER = logging.getLogger(__name__)


TAG_RE = re.compile(r"<[^>]+>")


def _text(value: str | None) -> str:
    if not value:
        return ""
    return html.unescape(TAG_RE.sub(" ", value)).strip()


def _child_text(node: ET.Element, names: list[str]) -> str:
    for name in names:
        child = node.find(name)
        if child is not None and child.text:
            return child.text.strip()
    for child in node:
        local = child.tag.split("}", 1)[-1]
        if local in names and child.text:
            return child.text.strip()
    return ""


def _normalize_date(value: str) -> str:
    if not value:
        return ""
    try:
        return parsedate_to_datetime(value).isoformat()
    except (TypeError, ValueError):
        return value


def collect_rss(config: dict[str, Any]) -> list[SourceItem]:
    if not config.get("enabled", True):
        return []
    items: list[SourceItem] = []
    for feed in config.get("feeds", []):
        name = feed.get("name", "RSS")
        url = feed.get("url", "")
        if not url:
            continue
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "GPTAdsBot/0.1"})
            with urllib.request.urlopen(request, timeout=20) as response:
                xml_bytes = response.read()
            root = ET.fromstring(xml_bytes)
            entries = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
            for entry in entries[: int(feed.get("max_items", 20))]:
                title = _text(_child_text(entry, ["title"]))
                link = _child_text(entry, ["link"])
                if not link:
                    link_node = entry.find("{http://www.w3.org/2005/Atom}link")
                    link = link_node.attrib.get("href", "") if link_node is not None else ""
                description = _text(
                    _child_text(entry, ["description", "summary", "encoded", "content"])
                )
                published = _normalize_date(
                    _child_text(entry, ["pubDate", "published", "updated"])
                )
                if title and link:
                    items.append(
                        SourceItem(
                            source="blog",
                            title=title,
                            url=link,
                            text=description,
                            author=name,
                            published_at=published,
                        )
                    )
        except Exception as exc:  # noqa: BLE001
            LOGGER.error(
                "情報取得失敗: RSS feed=%s url=%s error=%s",
                name,
                url,
                str(exc).splitlines()[0],
            )
    return items


def collect_google_news(config: dict[str, Any]) -> list[SourceItem]:
    if not config.get("enabled", True):
        return []
    feed_config = {
        "enabled": True,
        "feeds": [
            {
                "name": f"Google News: {query}",
                "url": _google_news_url(query),
                "max_items": int(config.get("max_items_per_query", 10)),
            }
            for query in config.get("queries", [])
        ],
    }
    return collect_rss(feed_config)


def _google_news_url(query: str) -> str:
    encoded = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={encoded}&hl=ja&gl=JP&ceid=JP:ja"
