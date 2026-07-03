from __future__ import annotations

import json
import logging
import os
import urllib.parse
import urllib.request
from typing import Any

from project.models import SourceItem

LOGGER = logging.getLogger(__name__)
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def _get_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "GPTAdsBot/0.1"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def collect_youtube(config: dict[str, Any]) -> list[SourceItem]:
    if not config.get("enabled", True):
        return []
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        LOGGER.info("YOUTUBE_API_KEY is not set. YouTube collection skipped.")
        return []

    items: list[SourceItem] = []
    max_results = int(config.get("max_results_per_keyword", 3))
    for keyword in config.get("search_keywords", []):
        try:
            params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "date",
                "maxResults": max_results,
                "key": api_key,
            }
            search = _get_json(f"{SEARCH_URL}?{urllib.parse.urlencode(params)}")
            ids = [
                entry["id"]["videoId"]
                for entry in search.get("items", [])
                if entry.get("id", {}).get("videoId")
            ]
            stats: dict[str, dict[str, Any]] = {}
            if ids:
                video_params = {
                    "part": "statistics,snippet",
                    "id": ",".join(ids),
                    "key": api_key,
                }
                videos = _get_json(f"{VIDEOS_URL}?{urllib.parse.urlencode(video_params)}")
                stats = {entry["id"]: entry for entry in videos.get("items", [])}
            for video_id in ids:
                entry = stats.get(video_id, {})
                snippet = entry.get("snippet", {})
                statistics = entry.get("statistics", {})
                items.append(
                    SourceItem(
                        source="youtube",
                        title=snippet.get("title", ""),
                        url=f"https://www.youtube.com/watch?v={video_id}",
                        text=snippet.get("description", ""),
                        author=snippet.get("channelTitle", ""),
                        published_at=snippet.get("publishedAt", ""),
                        metrics={"views": int(statistics.get("viewCount", 0) or 0)},
                    )
                )
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("情報取得失敗: YouTube keyword=%s error=%s", keyword, str(exc).splitlines()[0])
    return items
