from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from project.models import SourceItem
from project.report import sort_items


def build_site(public_dir: Path, items: list[SourceItem]) -> None:
    public_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "items": [item.to_dict() for item in sort_items(items)],
    }
    data_json = json.dumps(payload, ensure_ascii=False)
    html = HTML_TEMPLATE.replace("__GPT_ADS_DATA__", data_json)
    (public_dir / "index.html").write_text(html, encoding="utf-8")


HTML_TEMPLATE = """<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GPT Ads Portal</title>
  <style>
    :root {
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #1d2430;
      --muted: #667085;
      --line: #d8dee8;
      --accent: #0f766e;
      --accent-2: #b42318;
      --chip: #eef4ff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
      letter-spacing: 0;
    }
    header {
      background: #182230;
      color: #fff;
      padding: 24px;
    }
    .wrap { max-width: 1180px; margin: 0 auto; }
    .top {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: flex-end;
      flex-wrap: wrap;
    }
    h1 { margin: 0; font-size: 28px; line-height: 1.2; }
    .subtitle { margin: 8px 0 0; color: #ccd5e1; font-size: 14px; }
    .generated { color: #ccd5e1; font-size: 13px; }
    main { padding: 22px 24px 48px; }
    .toolbar {
      display: grid;
      grid-template-columns: minmax(220px, 1fr) auto auto;
      gap: 10px;
      margin: 0 0 18px;
      align-items: center;
    }
    input, select {
      width: 100%;
      min-height: 40px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 8px 10px;
      background: #fff;
      color: var(--ink);
      font: inherit;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 18px;
    }
    .stat {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }
    .stat strong { display: block; font-size: 22px; }
    .stat span { color: var(--muted); font-size: 13px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }
    article {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      min-width: 0;
    }
    .meta {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 26px;
      padding: 3px 8px;
      border-radius: 999px;
      background: var(--chip);
      color: #1849a9;
      font-size: 12px;
      font-weight: 700;
    }
    .importance-S, .importance-A { background: #fef3f2; color: var(--accent-2); }
    .importance-B { background: #fffaeb; color: #b54708; }
    .importance-C { background: #f2f4f7; color: #475467; }
    h2 {
      margin: 0;
      font-size: 18px;
      line-height: 1.35;
      overflow-wrap: anywhere;
    }
    p { margin: 0; color: #344054; line-height: 1.65; }
    ul { margin: 0; padding-left: 20px; color: #344054; line-height: 1.55; }
    .source-link {
      margin-top: auto;
      color: var(--accent);
      font-weight: 700;
      text-decoration: none;
      overflow-wrap: anywhere;
    }
    .empty {
      padding: 28px;
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--muted);
    }
    @media (max-width: 780px) {
      header { padding: 20px 16px; }
      main { padding: 16px; }
      .toolbar { grid-template-columns: 1fr; }
      .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .grid { grid-template-columns: 1fr; }
      h1 { font-size: 24px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="wrap top">
      <div>
        <h1>GPT Ads Portal</h1>
        <p class="subtitle">GPT広告・AI広告・生成AIマーケティングの自動収集レポート</p>
      </div>
      <div class="generated" id="generated"></div>
    </div>
  </header>
  <main class="wrap">
    <section class="toolbar" aria-label="filters">
      <input id="query" type="search" placeholder="キーワードで検索">
      <select id="source">
        <option value="">すべての媒体</option>
      </select>
      <select id="importance">
        <option value="">すべての重要度</option>
        <option value="S">重要度 S</option>
        <option value="A">重要度 A</option>
        <option value="B">重要度 B</option>
        <option value="C">重要度 C</option>
      </select>
    </section>
    <section class="stats" id="stats"></section>
    <section class="grid" id="items"></section>
  </main>
  <script>
    const DATA = __GPT_ADS_DATA__;
    const state = { query: "", source: "", importance: "" };
    const labels = { x: "X", youtube: "YouTube", blog: "ブログ", newsletter: "ニュースレター" };
    const generated = document.getElementById("generated");
    const query = document.getElementById("query");
    const source = document.getElementById("source");
    const importance = document.getElementById("importance");
    const itemsEl = document.getElementById("items");
    const statsEl = document.getElementById("stats");
    generated.textContent = `更新: ${new Date(DATA.generatedAt).toLocaleString("ja-JP")}`;

    [...new Set(DATA.items.map((item) => item.source))].forEach((name) => {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = labels[name] || name;
      source.appendChild(option);
    });

    function matches(item) {
      const haystack = `${item.title} ${item.summary} ${item.text} ${item.category}`.toLowerCase();
      return (!state.query || haystack.includes(state.query.toLowerCase()))
        && (!state.source || item.source === state.source)
        && (!state.importance || item.importance === state.importance);
    }

    function renderStats(items) {
      const counts = {
        total: items.length,
        x: items.filter((item) => item.source === "x").length,
        youtube: items.filter((item) => item.source === "youtube").length,
        high: items.filter((item) => ["S", "A"].includes(item.importance)).length,
      };
      statsEl.innerHTML = `
        <div class="stat"><strong>${counts.total}</strong><span>表示中の記事</span></div>
        <div class="stat"><strong>${counts.x}</strong><span>X</span></div>
        <div class="stat"><strong>${counts.youtube}</strong><span>YouTube</span></div>
        <div class="stat"><strong>${counts.high}</strong><span>重要度A以上</span></div>
      `;
    }

    function render() {
      const filtered = DATA.items.filter(matches);
      renderStats(filtered);
      if (!filtered.length) {
        itemsEl.innerHTML = `<div class="empty">条件に合う記事がありません。</div>`;
        return;
      }
      itemsEl.innerHTML = filtered.map((item) => `
        <article>
          <div class="meta">
            <span class="badge">${labels[item.source] || item.source}</span>
            <span class="badge importance-${item.importance}">重要度 ${item.importance || "C"}</span>
            <span class="badge">${item.category || "未分類"}</span>
          </div>
          <h2>${escapeHtml(item.title)}</h2>
          <p>${escapeHtml(item.summary || item.text || "")}</p>
          <ul>${(item.points || []).slice(0, 3).map((point) => `<li>${escapeHtml(point)}</li>`).join("")}</ul>
          <a class="source-link" href="${escapeAttr(item.url)}" target="_blank" rel="noopener">元URLを開く</a>
        </article>
      `).join("");
    }

    function escapeHtml(value) {
      return String(value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
      }[char]));
    }
    function escapeAttr(value) {
      return escapeHtml(value || "#");
    }
    query.addEventListener("input", (event) => { state.query = event.target.value; render(); });
    source.addEventListener("change", (event) => { state.source = event.target.value; render(); });
    importance.addEventListener("change", (event) => { state.importance = event.target.value; render(); });
    render();
  </script>
</body>
</html>
"""

