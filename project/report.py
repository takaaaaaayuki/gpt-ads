from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path

from project.models import SourceItem


IMPORTANCE_ORDER = {"S": 0, "A": 1, "B": 2, "C": 3}


def sort_items(items: list[SourceItem]) -> list[SourceItem]:
    return sorted(
        items,
        key=lambda item: (IMPORTANCE_ORDER.get(item.importance, 9), item.source, item.title),
    )


def render_markdown(items: list[SourceItem], generated_at: datetime | None = None) -> str:
    now = generated_at or datetime.now()
    grouped: dict[str, list[SourceItem]] = defaultdict(list)
    for item in sort_items(items):
        grouped[item.source].append(item)

    lines = [
        "# GPT Ads Report",
        "",
        f"Generated: {now.strftime('%Y-%m-%d %H:%M')}",
        "",
        "GPT広告・AI広告・生成AIマーケティング領域の収集レポートです。",
        "",
    ]
    for source in ["x", "youtube", "blog", "newsletter"]:
        if source not in grouped:
            continue
        lines.extend([f"## {source.upper()}", ""])
        for item in grouped[source]:
            lines.extend(
                [
                    "━━━━━━━━━━━━━━",
                    "",
                    f"### {item.title}",
                    "",
                    "## 要約",
                    item.summary or item.text[:400] or item.title,
                    "",
                    "## ポイント",
                ]
            )
            for point in item.points[:5]:
                lines.append(f"- {point}")
            lines.extend(
                [
                    "",
                    "## カテゴリ",
                    item.category or "-",
                    "",
                    "## 重要度",
                    item.importance or "C",
                    "",
                    "## 元URL",
                    item.url or "-",
                    "",
                ]
            )
    return "\n".join(lines).strip() + "\n"


def write_report(path: Path, items: list[SourceItem]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(items), encoding="utf-8")

