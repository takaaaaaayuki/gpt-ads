from __future__ import annotations

import argparse
import logging
from datetime import datetime

from collect.dedupe import dedupe_items
from collect.rss import collect_google_news, collect_rss
from collect.sample import sample_items
from collect.x import collect_x
from collect.youtube import collect_youtube
from project.io import read_jsonl, write_json, write_jsonl
from project.logging_config import configure_logging
from project.models import SourceItem
from project.report import write_report
from project.settings import (
    PROCESSED_DIR,
    DOCS_DIR,
    PUBLIC_DIR,
    RAW_DIR,
    REPORTS_DIR,
    ensure_dirs,
    load_dotenv,
    load_sources,
    runtime_options,
)
from project.site import build_site
from slack.notifier import notify_slack
from summarize.claude import summarize_items

LOGGER = logging.getLogger(__name__)
ARCHIVE_PATH = PROCESSED_DIR / "archive.jsonl"


def run(send_slack: bool = False, demo: bool = False, skip_x: bool = False, x_only: bool = False) -> None:
    load_dotenv()
    ensure_dirs()
    configure_logging()
    options = runtime_options(use_sample_data=demo)
    sources = load_sources()
    today = datetime.now().strftime("%Y-%m-%d")

    LOGGER.info("GPT Ads collection started.")
    collected = []
    if not skip_x:
        collected.extend(collect_x(sources.get("x", {})))
    if not x_only:
        collected.extend(collect_youtube(sources.get("youtube", {})))
        collected.extend(collect_rss(sources.get("rss", {})))
        collected.extend(collect_google_news(sources.get("google_news", {})))

    if options.use_sample_data:
        LOGGER.info("Demo mode is enabled. Sample data is added for preview.")
        collected = sample_items()
    elif not collected:
        LOGGER.warning("No live items collected. Check network access, API keys, or source settings.")
        previous_items = load_archive()
        if previous_items:
            LOGGER.info("Using previous processed data to avoid overwriting the portal with an empty run.")
            report_path = REPORTS_DIR / f"{today}.md"
            write_report(report_path, previous_items)
            build_site(PUBLIC_DIR, previous_items)
            build_site(DOCS_DIR, previous_items)
            return

    raw_path = RAW_DIR / f"items_{today}.jsonl"
    write_jsonl(raw_path, collected)

    archive = load_archive()
    archive_ids = {item.stable_id for item in archive}
    unique = [item for item in dedupe_items(collected) if item.stable_id not in archive_ids]
    summarized = summarize_items(unique, options.max_items_per_run)
    archive = merge_archive(archive, summarized)

    processed_path = PROCESSED_DIR / f"items_{today}.jsonl"
    write_jsonl(processed_path, summarized)
    write_jsonl(ARCHIVE_PATH, archive)
    write_json(PROCESSED_DIR / "latest.json", [item.to_dict() for item in archive])

    report_path = REPORTS_DIR / f"{today}.md"
    write_report(report_path, summarized)
    build_site(PUBLIC_DIR, archive, new_items_count=len(summarized))
    build_site(DOCS_DIR, archive, new_items_count=len(summarized))

    if send_slack:
        notify_slack(summarized)

    LOGGER.info(
        "GPT Ads collection finished. raw=%s processed=%s report=%s site=%s",
        raw_path,
        processed_path,
        report_path,
        PUBLIC_DIR / "index.html",
    )


def load_archive() -> list[SourceItem]:
    archive = read_jsonl(ARCHIVE_PATH)
    if archive:
        return dedupe_items(archive)

    restored = []
    for path in sorted(PROCESSED_DIR.glob("items_*.jsonl")):
        restored.extend(read_jsonl(path))
    return dedupe_items(restored)


def merge_archive(existing: list[SourceItem], new_items: list[SourceItem]) -> list[SourceItem]:
    return dedupe_items(new_items + existing)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build GPT Ads research portal.")
    parser.add_argument("--send-slack", action="store_true", help="Send a Slack notification when configured.")
    parser.add_argument("--demo", action="store_true", help="Use sample data for UI preview.")
    parser.add_argument("--skip-x", action="store_true", help="Skip X collection.")
    parser.add_argument("--x-only", action="store_true", help="Collect X only.")
    args = parser.parse_args()
    run(send_slack=args.send_slack, demo=args.demo, skip_x=args.skip_x, x_only=args.x_only)


if __name__ == "__main__":
    main()
