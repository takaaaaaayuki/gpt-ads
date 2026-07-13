from __future__ import annotations

import argparse
import csv
import json
import re
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from collect.dedupe import dedupe_items
from project.io import write_json, write_jsonl
from project.main import ARCHIVE_PATH, load_archive, merge_archive
from project.models import SourceItem
from project.settings import DOCS_DIR, PROCESSED_DIR, PUBLIC_DIR, ensure_dirs
from project.site import build_site


NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

ALIASES = {
    "title": ["title", "タイトル", "タイトル/内容", "投稿タイトル", "見出し", "件名"],
    "url": ["url", "URL", "投稿URL", "元URL", "リンク", "link"],
    "text": ["text", "本文", "タイトル/内容", "投稿本文", "内容", "投稿内容", "description"],
    "author": ["author", "投稿者", "投稿者・出典", "出典", "アカウント", "ユーザー", "user", "username", "account"],
    "published_at": ["published_at", "収集日", "投稿日", "投稿日時", "日時", "日付", "date", "published"],
    "summary": ["summary", "要約", "概要"],
    "category": ["category", "カテゴリ", "分類", "タグ"],
    "importance": ["importance", "重要度", "優先度", "rank"],
    "likes": ["likes", "いいね", "いいね数", "like"],
    "reposts": ["reposts", "リポスト", "リポスト数", "retweet", "retweets", "rp"],
    "replies": ["replies", "返信", "返信数", "reply"],
}


def import_x_excel(path: Path, sheet: str | None = None, dry_run: bool = False) -> tuple[int, int]:
    ensure_dirs()
    rows = read_table(path, sheet_name=sheet)
    items = [row_to_item(row) for row in rows]
    items = [item for item in items if item.url or item.text or item.title]
    items = dedupe_items(items)

    archive = load_archive()
    combined_unique = dedupe_items(archive + items)
    item_ids = {id(item) for item in items}
    new_items = [item for item in combined_unique if id(item) in item_ids]
    if dry_run:
        return len(items), len(new_items)

    merged = merge_archive(archive, new_items)
    today = datetime.now().strftime("%Y-%m-%d")
    write_jsonl(PROCESSED_DIR / f"x_import_{today}.jsonl", new_items)
    write_jsonl(ARCHIVE_PATH, merged)
    write_json(PROCESSED_DIR / "latest.json", [item.to_dict() for item in merged])
    build_site(PUBLIC_DIR, merged, new_items_count=len(new_items))
    build_site(DOCS_DIR, merged, new_items_count=len(new_items))
    return len(items), len(new_items)


def row_to_item(row: dict[str, Any]) -> SourceItem:
    title = value_for(row, "title")
    text = value_for(row, "text")
    url = normalize_url(value_for(row, "url"))
    author = value_for(row, "author")
    published_at = normalize_datetime(value_for(row, "published_at"))
    summary = value_for(row, "summary")
    category = value_for(row, "category") or "X / GPT広告"
    importance = (value_for(row, "importance") or "B").upper()
    if importance not in {"S", "A", "B", "C"}:
        importance = "B"
    if not title:
        title = make_title(text, author)
    metrics = {
        "likes": parse_int(value_for(row, "likes")),
        "reposts": parse_int(value_for(row, "reposts")),
        "replies": parse_int(value_for(row, "replies")),
    }
    points = []
    if summary and text and summary != text:
        points = ["Xで確認されたGPT広告関連の投稿です。", "詳細は元URLで一次情報を確認してください。"]
    return SourceItem(
        source="x",
        title=title,
        url=url,
        text=text or summary or title,
        author=author,
        published_at=published_at,
        category=category,
        importance=importance,
        summary=summary or text[:350] or title,
        points=points,
        metrics=metrics,
    )


def value_for(row: dict[str, Any], canonical: str) -> str:
    normalized = {normalize_key(key): value for key, value in row.items()}
    for alias in ALIASES[canonical]:
        value = normalized.get(normalize_key(alias))
        if value is not None:
            return str(value).strip()
    return ""


def normalize_key(value: str) -> str:
    return re.sub(r"[\s_\-　]+", "", str(value)).lower()


def normalize_url(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    match = re.search(r"https?://\S+", value)
    return match.group(0).rstrip("。、,") if match else value


def normalize_datetime(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M", "%Y-%m-%d", "%Y/%m/%d"]:
        try:
            return datetime.strptime(value, fmt).isoformat()
        except ValueError:
            pass
    return value


def parse_int(value: str) -> int:
    if not value:
        return 0
    normalized = str(value).replace(",", "").strip().lower()
    multiplier = 1
    if normalized.endswith("k"):
        multiplier = 1000
        normalized = normalized[:-1]
    if normalized.endswith("万"):
        multiplier = 10000
        normalized = normalized[:-1]
    try:
        return int(float(normalized) * multiplier)
    except ValueError:
        return 0


def make_title(text: str, author: str) -> str:
    base = re.sub(r"\s+", " ", text).strip()
    title = base[:58] + ("..." if len(base) > 58 else "")
    if title:
        return title
    return f"{author} のX投稿" if author else "X投稿"


def read_table(path: Path, sheet_name: str | None = None) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        return read_xlsx(path, sheet_name)
    if suffix in {".csv", ".tsv"}:
        delimiter = "\t" if suffix == ".tsv" else ","
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            return [dict(row) for row in csv.DictReader(fh, delimiter=delimiter)]
    raise ValueError(f"Unsupported file type: {path.suffix}. Use .xlsx, .csv, or .tsv.")


def read_xlsx(path: Path, sheet_name: str | None = None) -> list[dict[str, Any]]:
    with zipfile.ZipFile(path) as zf:
        shared_strings = load_shared_strings(zf)
        date_style_ids = load_date_style_ids(zf)
        sheet_path = select_sheet_path(zf, sheet_name)
        root = ET.fromstring(zf.read(sheet_path))
        rows = []
        for row in root.findall(".//x:sheetData/x:row", NS):
            values: dict[int, Any] = {}
            for cell in row.findall("x:c", NS):
                index = column_index(cell.attrib.get("r", "A1"))
                values[index] = cell_value(cell, shared_strings, date_style_ids)
            if values:
                max_index = max(values)
                rows.append([values.get(i, "") for i in range(max_index + 1)])
    if not rows:
        return []
    headers = [str(value).strip() for value in rows[0]]
    records = []
    for row in rows[1:]:
        record = {headers[index]: row[index] if index < len(row) else "" for index in range(len(headers)) if headers[index]}
        if any(str(value).strip() for value in record.values()):
            records.append(record)
    return records


def load_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    strings = []
    for item in root.findall("x:si", NS):
        strings.append("".join(text.text or "" for text in item.findall(".//x:t", NS)))
    return strings


def load_date_style_ids(zf: zipfile.ZipFile) -> set[int]:
    if "xl/styles.xml" not in zf.namelist():
        return set()
    root = ET.fromstring(zf.read("xl/styles.xml"))
    custom_date_ids = set()
    for fmt in root.findall(".//x:numFmts/x:numFmt", NS):
        code = fmt.attrib.get("formatCode", "").lower()
        if any(token in code for token in ["yy", "dd", "mm", "h:"]):
            custom_date_ids.add(int(fmt.attrib.get("numFmtId", "0")))
    built_in_date_ids = set(range(14, 23)) | {45, 46, 47}
    date_num_fmt_ids = built_in_date_ids | custom_date_ids
    date_style_ids = set()
    for index, xf in enumerate(root.findall(".//x:cellXfs/x:xf", NS)):
        num_fmt_id = int(xf.attrib.get("numFmtId", "0"))
        if num_fmt_id in date_num_fmt_ids:
            date_style_ids.add(index)
    return date_style_ids


def select_sheet_path(zf: zipfile.ZipFile, sheet_name: str | None) -> str:
    workbook = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    rel_by_id = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
    sheets = workbook.findall(".//x:sheets/x:sheet", NS)
    selected = None
    for sheet in sheets:
        if sheet_name is None or sheet.attrib.get("name") == sheet_name:
            selected = sheet
            break
    if selected is None:
        available = ", ".join(sheet.attrib.get("name", "") for sheet in sheets)
        raise ValueError(f"Sheet not found: {sheet_name}. Available sheets: {available}")
    rel_id = selected.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
    target = rel_by_id[rel_id]
    if target.startswith("/"):
        return target.lstrip("/")
    return "xl/" + target


def cell_value(cell: ET.Element, shared_strings: list[str], date_style_ids: set[int]) -> Any:
    cell_type = cell.attrib.get("t")
    value_node = cell.find("x:v", NS)
    if cell_type == "inlineStr":
        return "".join(text.text or "" for text in cell.findall(".//x:t", NS))
    if value_node is None:
        return ""
    raw = value_node.text or ""
    if cell_type == "s":
        return shared_strings[int(raw)] if raw else ""
    if cell_type == "b":
        return raw == "1"
    style_id = int(cell.attrib.get("s", "0"))
    if style_id in date_style_ids:
        try:
            return (datetime(1899, 12, 30) + timedelta(days=float(raw))).isoformat()
        except ValueError:
            return raw
    return raw


def column_index(cell_ref: str) -> int:
    letters = re.match(r"[A-Z]+", cell_ref.upper())
    if not letters:
        return 0
    total = 0
    for char in letters.group(0):
        total = total * 26 + (ord(char) - ord("A") + 1)
    return total - 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Cowork X Excel rows into GPT Ads Portal.")
    parser.add_argument("path", type=Path, help="Path to Cowork-created .xlsx, .csv, or .tsv file.")
    parser.add_argument("--sheet", help="Sheet name for .xlsx files. Defaults to first sheet.")
    parser.add_argument("--dry-run", action="store_true", help="Read and count rows without changing the portal.")
    args = parser.parse_args()
    total, added = import_x_excel(args.path, sheet=args.sheet, dry_run=args.dry_run)
    mode = "would add" if args.dry_run else "added"
    print(f"Read {total} X rows; {mode} {added} new rows.")


if __name__ == "__main__":
    main()
