from __future__ import annotations

import json
import logging
import os
import re
import urllib.request
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError

from project.models import SourceItem

LOGGER = logging.getLogger(__name__)
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
MODEL_ALIASES = {
    "claude-3-5-haiku-latest": "claude-haiku-4-5",
}
KEYWORDS = [
    "GPT",
    "ChatGPT",
    "Claude",
    "LLM",
    "AI",
    "生成AI",
    "広告",
    "マーケティング",
    "運用",
    "Google Ads",
]
AI_TERMS = [
    "gpt",
    "chatgpt",
    "claude",
    "llm",
    "ai",
    "生成ai",
    "人工知能",
]
GPT_ADS_TERMS = [
    "gpt広告",
    "chatgpt広告",
    "chatgpt ads",
    "chatgpt ad",
    "gpt ads",
    "gpt ad",
    "ai広告",
    "ai ads",
    "ai ad",
    "ai advertising",
    "llm広告",
    "生成ai広告",
    "ai search ads",
    "ai検索広告",
    "会話型広告",
    "aiエージェント広告",
    "生成aiマーケティング",
    "aiマーケティング",
    "ai検索",
    "aio",
    "llmo",
    "geo",
]
MARKETING_TERMS = [
    "ads",
    "advertis",
    "marketing",
    "brand",
    "campaign",
    "commerce",
    "shopping",
    "seo",
    "geo",
    "search",
    "広告",
    "マーケティング",
    "ブランド",
    "キャンペーン",
    "販促",
    "検索",
    "購買",
]
STRONG_AD_TERMS = [
    "ad",
    "ads",
    "advertising",
    "advertisement",
    "campaign",
    "creative",
    "brand",
    "search",
    "seo",
    "geo",
    "commerce",
    "shopping",
    "funnel",
    "lead",
    "acquisition",
    "ugc",
    "canva",
    "広告",
    "キャンペーン",
    "クリエイティブ",
    "ブランド",
    "検索",
    "購買",
    "ファネル",
    "リード",
    "獲得",
]
NEGATIVE_TERMS = [
    "classroom",
    "educator",
    "education",
    "genomics",
    "biology",
    "infrastructure",
    "core dump",
    "受付終了",
    "プレゼント",
    "書籍プレゼント",
    "gemini最新活用ガイド",
    "アクセシビリティ",
]


def is_relevant(item: SourceItem) -> bool:
    if _is_too_old(item):
        return False
    if item.source == "blog":
        text = f"{item.title}\n{item.text[:500]}\n{item.author}\n{item.category}".lower()
    else:
        text = f"{item.title}\n{item.text}\n{item.author}\n{item.category}".lower()
    from_marketing_source = "marketing" in item.author.lower() or "ad" in item.author.lower()
    has_gpt_ads = any(_contains_term(text, term) for term in GPT_ADS_TERMS)
    has_ai = any(_contains_term(text, term) for term in AI_TERMS)
    has_strong_ad_context = any(_contains_term(text, term) for term in STRONG_AD_TERMS)
    is_negative = any(_contains_term(text, term) for term in NEGATIVE_TERMS)
    if item.source == "blog":
        title = item.title.lower()
        title_has_core_theme = any(
            _contains_term(title, term)
            for term in [
                "gpt広告",
                "chatgpt広告",
                "chatgpt ads",
                "ai広告",
                "ai ads",
                "ai advertising",
                "ai検索",
                "aio",
                "geo",
                "llmo",
                "aiマーケティング",
                "生成aiマーケティング",
                "ブランド",
                "集客",
                "広告",
            ]
        )
        return has_gpt_ads and title_has_core_theme and not is_negative
    if has_gpt_ads:
        return True
    if is_negative:
        return False
    return has_ai and has_strong_ad_context and from_marketing_source


def _is_too_old(item: SourceItem) -> bool:
    max_age_days = int(os.getenv("GPT_ADS_MAX_ITEM_AGE_DAYS", "120"))
    if not item.published_at:
        return False
    try:
        published = datetime.fromisoformat(item.published_at.replace("Z", "+00:00"))
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
    except ValueError:
        return False
    return published < datetime.now(timezone.utc) - timedelta(days=max_age_days)


def _contains_term(text: str, term: str) -> bool:
    if term == "advertis":
        return "advertis" in text
    if re.fullmatch(r"[a-z0-9]+", term):
        return re.search(rf"\b{re.escape(term)}\b", text) is not None
    return term in text


def _heuristic_importance(item: SourceItem) -> str:
    text = f"{item.title} {item.text} {item.author}"
    score = 0
    for keyword in ["ChatGPT", "GPT広告", "AI広告", "ChatGPT Ads", "AI Ads", "Google Ads", "Claude", "LLM"]:
        if keyword.lower() in text.lower():
            score += 2
    for keyword in ["marketing", "brand", "campaign", "広告", "マーケティング", "ブランド"]:
        if keyword.lower() in text.lower():
            score += 1
    if "marketing" in item.author.lower() or "adweek" in item.author.lower():
        score += 2
    if item.source == "x":
        score += int(item.metrics.get("likes", 0) or 0) // 100
    if item.source == "youtube":
        score += int(item.metrics.get("views", 0) or 0) // 5000
    if score >= 4:
        return "A"
    if score >= 2:
        return "B"
    return "C"


def _heuristic_category(item: SourceItem) -> str:
    text = f"{item.title} {item.text}".lower()
    categories: list[str] = []
    if "chatgpt" in text or "gpt" in text:
        categories.append("ChatGPT広告")
    if "google ads" in text or "広告" in text:
        categories.append("広告運用")
    if "marketing" in text or "マーケティング" in text:
        categories.append("マーケティング")
    if "生成ai" in text or "ai" in text or "llm" in text:
        categories.append("生成AI活用")
    return " / ".join(dict.fromkeys(categories)) or "AI広告"


def _split_sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[。.!?])\s+", normalized)
    return [part for part in parts if part]


def summarize_without_api(item: SourceItem) -> SourceItem:
    sentences = _split_sentences(item.text or item.title)
    summary = "\n".join(sentences[:3]) if sentences else item.title
    item.summary = summary[:700]
    item.points = [
        "GPT広告・AI広告領域との関連がある情報です。",
        "広告運用、ブランド露出、生成AI活用の観点で確認対象です。",
        "詳細は元URLで一次情報を確認してください。",
    ]
    item.category = _heuristic_category(item)
    item.importance = _heuristic_importance(item)
    return item


def _build_prompt(item: SourceItem) -> str:
    return f"""あなたは広告代理店のリサーチャーです。

以下の情報から、GPT広告、AI広告、広告運用、生成AI活用、マーケティングに関する有益な情報のみ抽出してください。
有益でない場合も、重要度はCとして簡潔にまとめてください。

出力は必ずJSONのみで返してください。
キー: title, summary, points, category, importance
importanceは S / A / B / C のいずれかです。
summaryは日本語3〜5行、pointsは日本語の配列3件です。

source: {item.source}
title: {item.title}
author: {item.author}
url: {item.url}
published_at: {item.published_at}
metrics: {json.dumps(item.metrics, ensure_ascii=False)}
text:
{item.text[:5000]}
"""


def _parse_json_response(content: str) -> dict[str, object]:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def summarize_with_claude(item: SourceItem) -> SourceItem:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return summarize_without_api(item)
    configured_model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")
    model = MODEL_ALIASES.get(configured_model, configured_model)
    payload = {
        "model": model,
        "max_tokens": 900,
        "temperature": 0.2,
        "messages": [{"role": "user", "content": _build_prompt(item)}],
    }
    try:
        request = urllib.request.Request(
            ANTHROPIC_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "content-type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
        content = data["content"][0]["text"]
        parsed = _parse_json_response(content)
        item.title = parsed.get("title") or item.title
        item.summary = parsed.get("summary") or item.summary
        item.points = parsed.get("points") or item.points
        item.category = parsed.get("category") or item.category
        item.importance = (parsed.get("importance") or item.importance).upper()
        return item
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        LOGGER.error("Claude APIエラー: status=%s body=%s", exc.code, body[:500])
        return summarize_without_api(item)
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("Claude APIエラー: url=%s error=%s", item.url, exc)
        return summarize_without_api(item)


def summarize_items(items: list[SourceItem], limit: int) -> list[SourceItem]:
    relevant = [item for item in items if is_relevant(item)]
    selected = _balanced_source_selection(relevant, limit)
    return [summarize_with_claude(item) for item in selected]


def _balanced_source_selection(items: list[SourceItem], limit: int) -> list[SourceItem]:
    grouped: dict[str, list[SourceItem]] = {}
    for item in sorted(items, key=_item_timestamp, reverse=True):
        grouped.setdefault(item.source, []).append(item)
    source_order = [source for source in ["x", "youtube", "blog", "newsletter"] if source in grouped]
    source_order.extend(source for source in grouped if source not in source_order)

    selected: list[SourceItem] = []
    index = 0
    while len(selected) < limit:
        added = False
        for source in source_order:
            bucket = grouped[source]
            if index < len(bucket):
                selected.append(bucket[index])
                added = True
                if len(selected) >= limit:
                    break
        if not added:
            break
        index += 1
    return selected


def _item_timestamp(item: SourceItem) -> float:
    if not item.published_at:
        return 0
    try:
        published = datetime.fromisoformat(item.published_at.replace("Z", "+00:00"))
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        return published.timestamp()
    except ValueError:
        return 0
