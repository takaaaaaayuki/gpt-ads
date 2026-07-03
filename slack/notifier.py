from __future__ import annotations

import json
import logging
import os
import urllib.request

from project.models import SourceItem

LOGGER = logging.getLogger(__name__)


def _message(items: list[SourceItem]) -> str:
    lines = ["🤖 GPT Ads Daily"]
    for item in items[:8]:
        lines.extend(
            [
                "",
                "━━━━━━━━━━━━━━",
                f"【{item.source.upper()}】 {item.title}",
                item.summary[:300],
                f"重要度: {item.importance}",
                item.url,
            ]
        )
    return "\n".join(lines)


def notify_slack(items: list[SourceItem]) -> bool:
    token = os.getenv("SLACK_BOT_TOKEN")
    channel = os.getenv("SLACK_CHANNEL_ID")
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    text = _message(items)
    if token and channel:
        payload = {"channel": channel, "text": text}
        request = urllib.request.Request(
            "https://slack.com/api/chat.postMessage",
            data=json.dumps(payload).encode("utf-8"),
            headers={"content-type": "application/json", "authorization": f"Bearer {token}"},
            method="POST",
        )
    elif webhook:
        request = urllib.request.Request(
            webhook,
            data=json.dumps({"text": text}).encode("utf-8"),
            headers={"content-type": "application/json"},
            method="POST",
        )
    else:
        LOGGER.info("Slack credentials are not set. Slack notification skipped.")
        return False

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
        if token and '"ok":true' not in body:
            LOGGER.error("Slack送信失敗: %s", body)
            return False
        return True
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("Slack送信失敗: %s", exc)
        return False

