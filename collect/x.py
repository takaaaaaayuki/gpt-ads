from __future__ import annotations

import logging
import os
import re
import urllib.parse
from pathlib import Path
from typing import Any

from project.models import SourceItem
from project.settings import RAW_DIR

LOGGER = logging.getLogger(__name__)
STATUS_RE = re.compile(r"/([^/\s]+)/status/(\d+)")


def collect_x(config: dict[str, Any]) -> list[SourceItem]:
    """Best-effort loginless X collector.

    X frequently blocks logged-out automated browsing. This function keeps the
    interface stable and uses Playwright when available, but returns an empty
    list instead of failing the whole run.
    """

    if not config.get("enabled", True):
        return []
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception:
        LOGGER.warning("Browser Use失敗: Playwright is not installed. X collection skipped.")
        return []

    items: list[SourceItem] = []
    keywords = config.get("search_keywords", [])[: int(config.get("max_keywords_per_run", 3))]
    max_posts = int(config.get("max_posts_per_keyword", 8))
    headless = os.getenv("GPT_ADS_X_HEADLESS", "1") != "0"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                locale="ja-JP",
                timezone_id="Asia/Tokyo",
                viewport={"width": 1365, "height": 900},
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
            )
            page = context.new_page()
            for keyword in keywords:
                query = urllib.parse.quote(keyword)
                url = f"https://x.com/search?q={query}&src=typed_query&f=live"
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(int(config.get("wait_ms", 7000)))
                if _is_login_wall(page):
                    _save_debug_page(page, keyword, "login_wall")
                    LOGGER.warning("Xログイン失敗: login wall shown for keyword=%s", keyword)
                    continue
                articles = page.locator("article").all()[:max_posts]
                if not articles:
                    _save_debug_page(page, keyword, "no_articles")
                    LOGGER.warning("情報取得失敗: X no articles for keyword=%s", keyword)
                    continue
                for article in articles:
                    text = article.inner_text(timeout=5000).strip()
                    if not text:
                        continue
                    link = _extract_status_url(article)
                    if not link:
                        continue
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    author = lines[0] if lines else ""
                    title = _build_title(lines, keyword)
                    metrics = _extract_metrics(lines)
                    published_at = _extract_datetime(article)
                    items.append(
                        SourceItem(
                            source="x",
                            title=title[:120],
                            url=link,
                            text=text,
                            author=author,
                            published_at=published_at,
                            metrics=metrics,
                        )
                    )
            context.close()
            browser.close()
    except Exception as exc:  # noqa: BLE001
        reason = str(exc).splitlines()[0]
        LOGGER.error("Browser Use失敗: loginless X collection failed: %s", reason)
    return items


def _is_login_wall(page: Any) -> bool:
    text = page.locator("body").inner_text(timeout=5000).lower()
    markers = [
        "log in",
        "sign in",
        "ログイン",
        "アカウントを作成",
        "join x today",
    ]
    return any(marker in text for marker in markers) and not page.locator("article").count()


def _extract_status_url(article: Any) -> str:
    links = article.locator("a[href*='/status/']").all()
    for link in links:
        href = link.get_attribute("href") or ""
        match = STATUS_RE.search(href)
        if not match:
            continue
        username, status_id = match.groups()
        return f"https://x.com/{username}/status/{status_id}"
    return ""


def _build_title(lines: list[str], keyword: str) -> str:
    for line in lines:
        if len(line) >= 12 and not line.startswith("@") and line.lower() not in {"follow", "フォロー"}:
            return line
    return keyword


def _extract_datetime(article: Any) -> str:
    times = article.locator("time").all()
    if not times:
        return ""
    return times[0].get_attribute("datetime") or ""


def _extract_metrics(lines: list[str]) -> dict[str, int]:
    metrics = {"replies": 0, "reposts": 0, "likes": 0}
    joined = " ".join(lines)
    patterns = {
        "replies": r"(?i)(?:reply|返信)\s*(\d+(?:\.\d+)?[K万]?)",
        "reposts": r"(?i)(?:repost|リポスト)\s*(\d+(?:\.\d+)?[K万]?)",
        "likes": r"(?i)(?:like|いいね)\s*(\d+(?:\.\d+)?[K万]?)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, joined)
        if match:
            metrics[key] = _parse_count(match.group(1))
    return metrics


def _parse_count(value: str) -> int:
    normalized = value.replace(",", "").strip()
    if normalized.endswith("K"):
        return int(float(normalized[:-1]) * 1000)
    if normalized.endswith("万"):
        return int(float(normalized[:-1]) * 10000)
    try:
        return int(float(normalized))
    except ValueError:
        return 0


def _save_debug_page(page: Any, keyword: str, reason: str) -> None:
    if os.getenv("GPT_ADS_X_DEBUG", "1") == "0":
        return
    debug_dir = RAW_DIR / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    safe_keyword = re.sub(r"[^A-Za-z0-9ぁ-んァ-ン一-龥_-]+", "_", keyword)[:40]
    base = debug_dir / f"x_{safe_keyword}_{reason}"
    try:
        Path(f"{base}.html").write_text(page.content(), encoding="utf-8")
        page.screenshot(path=f"{base}.png", full_page=True)
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("X debug save failed: %s", str(exc).splitlines()[0])
