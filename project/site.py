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
      --bg: #f3f5ef;
      --surface: #ffffff;
      --surface-soft: #f8faf5;
      --ink: #10231d;
      --muted: #65746d;
      --line: #d9e2dc;
      --line-strong: #b8c8bf;
      --gpt: #10a37f;
      --gpt-dark: #0b6b57;
      --gpt-ink: #062b22;
      --gold: #b7791f;
      --red: #b42318;
      --shadow: 0 18px 45px rgba(16, 35, 29, 0.10);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
      letter-spacing: 0;
    }
    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background:
        radial-gradient(circle at 8% 0%, rgba(16, 163, 127, 0.14), transparent 28%),
        linear-gradient(180deg, rgba(255, 255, 255, 0.64), transparent 34%);
      z-index: -1;
    }
    header {
      background:
        linear-gradient(135deg, #08251d 0%, #103c31 58%, #0f5e4b 100%);
      color: #fff;
      padding: 28px 24px 34px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.14);
    }
    .wrap { max-width: 1180px; margin: 0 auto; }
    .top {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: flex-end;
      flex-wrap: wrap;
    }
    .brand {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      color: rgba(255, 255, 255, 0.78);
      font-size: 13px;
      font-weight: 700;
      margin-bottom: 10px;
      text-transform: uppercase;
    }
    .brand-mark {
      width: 28px;
      height: 28px;
      border-radius: 8px;
      display: inline-grid;
      place-items: center;
      background: rgba(255, 255, 255, 0.12);
      border: 1px solid rgba(255, 255, 255, 0.24);
      color: #b9f3df;
      font-weight: 800;
    }
    h1 { margin: 0; font-size: 34px; line-height: 1.12; }
    .subtitle { margin: 10px 0 0; color: #d5e8df; font-size: 15px; max-width: 720px; line-height: 1.7; }
    .generated {
      color: #d5e8df;
      font-size: 13px;
      padding: 9px 12px;
      background: rgba(255, 255, 255, 0.10);
      border: 1px solid rgba(255, 255, 255, 0.18);
      border-radius: 8px;
    }
    main { padding: 22px 24px 52px; }
    .toolbar {
      display: grid;
      grid-template-columns: minmax(260px, 1fr) minmax(150px, 210px) minmax(150px, 210px);
      gap: 12px;
      margin: -46px 0 18px;
      align-items: center;
      background: rgba(255, 255, 255, 0.92);
      border: 1px solid rgba(255, 255, 255, 0.72);
      border-radius: 12px;
      padding: 12px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(14px);
    }
    input, select {
      width: 100%;
      min-height: 44px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 9px 12px;
      background: #fff;
      color: var(--ink);
      font: inherit;
      outline: none;
    }
    input:focus, select:focus {
      border-color: var(--gpt);
      box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.15);
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }
    .stat {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      box-shadow: 0 10px 26px rgba(16, 35, 29, 0.05);
    }
    .stat strong { display: block; font-size: 25px; line-height: 1; }
    .stat span { color: var(--muted); font-size: 13px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }
    article {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 13px;
      min-width: 0;
      box-shadow: 0 12px 30px rgba(16, 35, 29, 0.06);
      transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
    }
    article:hover {
      transform: translateY(-2px);
      border-color: var(--line-strong);
      box-shadow: 0 18px 42px rgba(16, 35, 29, 0.11);
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
      background: #edf7f3;
      color: var(--gpt-dark);
      font-size: 12px;
      font-weight: 700;
      border: 1px solid #d5eee4;
    }
    .source-youtube { background: #fff1f0; color: #c0362c; border-color: #ffd7d3; }
    .source-blog { background: #ecfdf3; color: #087443; border-color: #c9f2dc; }
    .importance-S { background: #fff7df; color: #8a5200; border-color: #f4d58a; }
    .importance-A { background: #eaf8f1; color: #067647; border-color: #bfe7d2; }
    .importance-B { background: #fff7ed; color: #b54708; border-color: #fed7aa; }
    .importance-C { background: #f2f4f7; color: #475467; border-color: #e4e7ec; }
    h2 {
      margin: 0;
      font-size: 19px;
      line-height: 1.35;
      overflow-wrap: anywhere;
    }
    .byline {
      color: var(--muted);
      font-size: 12px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    p { margin: 0; color: #33483f; line-height: 1.72; }
    ul { margin: 0; padding-left: 20px; color: #33483f; line-height: 1.6; }
    li + li { margin-top: 5px; }
    .source-link {
      margin-top: auto;
      color: var(--gpt-dark);
      font-weight: 700;
      text-decoration: none;
      overflow-wrap: anywhere;
      border-top: 1px solid var(--line);
      padding-top: 12px;
    }
    .source-link:hover {
      color: var(--gpt);
    }
    .empty {
      padding: 28px;
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--muted);
      grid-column: 1 / -1;
    }
    @media (max-width: 780px) {
      header { padding: 20px 16px; }
      main { padding: 16px; }
      .toolbar { margin-top: -28px; }
      .toolbar { grid-template-columns: 1fr; }
      .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .grid { grid-template-columns: 1fr; }
      h1 { font-size: 27px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="wrap top">
      <div>
        <div class="brand"><span class="brand-mark">G</span><span>GPT Ads Intelligence</span></div>
        <h1>GPT Ads Portal</h1>
        <p class="subtitle">ChatGPT広告、AI検索、生成AIマーケティングの動きを追うリサーチポータル</p>
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
    const labels = { youtube: "YouTube", blog: "Web記事", newsletter: "ニュースレター" };
    const generated = document.getElementById("generated");
    const query = document.getElementById("query");
    const source = document.getElementById("source");
    const importance = document.getElementById("importance");
    const itemsEl = document.getElementById("items");
    const statsEl = document.getElementById("stats");
    generated.textContent = `更新: ${new Date(DATA.generatedAt).toLocaleString("ja-JP")}`;

    [...new Set(DATA.items.map((item) => item.source).filter((name) => name !== "x"))].forEach((name) => {
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
        youtube: items.filter((item) => item.source === "youtube").length,
        blog: items.filter((item) => item.source === "blog").length,
        high: items.filter((item) => ["S", "A"].includes(item.importance)).length,
      };
      statsEl.innerHTML = `
        <div class="stat"><strong>${counts.total}</strong><span>表示中</span></div>
        <div class="stat"><strong>${counts.youtube}</strong><span>YouTube</span></div>
        <div class="stat"><strong>${counts.blog}</strong><span>Web記事</span></div>
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
            <span class="badge source-${item.source}">${labels[item.source] || item.source}</span>
            <span class="badge importance-${item.importance}">重要度 ${item.importance || "C"}</span>
            <span class="badge">${item.category || "未分類"}</span>
          </div>
          <h2>${escapeHtml(item.title)}</h2>
          <div class="byline">
            <span>${escapeHtml(item.author || labels[item.source] || "")}</span>
            <span>${formatDate(item.published_at)}</span>
          </div>
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
    function formatDate(value) {
      if (!value) return "";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return escapeHtml(value);
      return date.toLocaleDateString("ja-JP", { year: "numeric", month: "short", day: "numeric" });
    }
    query.addEventListener("input", (event) => { state.query = event.target.value; render(); });
    source.addEventListener("change", (event) => { state.source = event.target.value; render(); });
    importance.addEventListener("change", (event) => { state.importance = event.target.value; render(); });
    render();
  </script>
</body>
</html>
"""
