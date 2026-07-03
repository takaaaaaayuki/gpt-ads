from __future__ import annotations

from project.models import SourceItem, utc_now_iso


def sample_items() -> list[SourceItem]:
    now = utc_now_iso()
    return [
        SourceItem(
            source="x",
            title="ChatGPT広告の表示設計に関する議論が増加",
            url="https://example.com/x/chatgpt-ads-discussion",
            text="ChatGPTのような会話型AIに広告が入る場合、検索広告とは違い、回答文脈の中で自然さと透明性をどう両立するかが重要になる。",
            author="sample",
            published_at=now,
            metrics={"likes": 128, "reposts": 32, "replies": 14},
        ),
        SourceItem(
            source="youtube",
            title="Google AdsのAI自動化アップデート解説",
            url="https://example.com/youtube/google-ads-ai",
            text="Google広告のAI自動化、クリエイティブ生成、ターゲティング最適化に関する解説動画。広告運用者の役割が手動調整からAIへの指示設計へ移っている。",
            author="sample channel",
            published_at=now,
            metrics={"views": 4200},
        ),
        SourceItem(
            source="blog",
            title="生成AI時代のブランド露出はSEOからGEOへ",
            url="https://example.com/blog/generative-engine-optimization",
            text="AI検索やチャットボット回答内でブランドがどのように引用されるかが、マーケティング上の新しい論点になっている。",
            author="sample blog",
            published_at=now,
        ),
    ]

