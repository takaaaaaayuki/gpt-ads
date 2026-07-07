from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from project.models import SourceItem
from project.report import sort_items


def build_site(public_dir: Path, items: list[SourceItem], new_items_count: int = 0) -> None:
    public_dir.mkdir(parents=True, exist_ok=True)
    sorted_items = sort_items(items)
    payload = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "newItemsCount": new_items_count,
        "items": [item.to_dict() for item in sorted_items],
    }
    data_json = json.dumps(payload, ensure_ascii=False)
    html = HTML_TEMPLATE.replace("__GPT_ADS_DATA__", data_json)
    (public_dir / "index.html").write_text(html, encoding="utf-8")
    about_html = build_about_page(sorted_items)
    (public_dir / "about.html").write_text(about_html, encoding="utf-8")


def build_about_page(items: list[SourceItem]) -> str:
    counts = {
        "total": len(items),
        "youtube": sum(1 for item in items if item.source == "youtube"),
        "blog": sum(1 for item in items if item.source == "blog"),
        "high": sum(1 for item in items if item.importance in ["S", "A"]),
    }
    return (
        ABOUT_TEMPLATE.replace("__TOTAL__", str(counts["total"]))
        .replace("__YOUTUBE__", str(counts["youtube"]))
        .replace("__BLOG__", str(counts["blog"]))
        .replace("__HIGH__", str(counts["high"]))
        .replace("__GENERATED__", datetime.now().strftime("%Y年%m月%d日 %H:%M"))
    )


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
    .header-actions {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 10px;
    }
    .nav-link {
      display: inline-flex;
      align-items: center;
      min-height: 34px;
      padding: 7px 11px;
      color: #dff5ed;
      border: 1px solid rgba(255, 255, 255, 0.22);
      background: rgba(255, 255, 255, 0.10);
      border-radius: 8px;
      font-size: 13px;
      font-weight: 700;
      text-decoration: none;
    }
    .nav-link:hover { background: rgba(255, 255, 255, 0.16); }
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
      grid-template-columns: minmax(260px, 1fr) minmax(135px, 180px) minmax(135px, 180px) minmax(120px, 160px);
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
    .date-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: var(--gpt-ink);
      background: var(--surface-soft);
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 4px 8px;
      font-weight: 700;
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
      <div class="header-actions">
        <a class="nav-link" href="about.html">このポータルについて</a>
        <div class="generated" id="generated"></div>
      </div>
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
      <select id="sort">
        <option value="date">新しい順</option>
        <option value="importance">重要度順</option>
      </select>
    </section>
    <section class="stats" id="stats"></section>
    <section class="grid" id="items"></section>
  </main>
  <script>
    const DATA = __GPT_ADS_DATA__;
    const state = { query: "", source: "", importance: "", sort: "date" };
    const labels = { youtube: "YouTube", blog: "Web記事", newsletter: "ニュースレター" };
    const generated = document.getElementById("generated");
    const query = document.getElementById("query");
    const source = document.getElementById("source");
    const importance = document.getElementById("importance");
    const sort = document.getElementById("sort");
    const itemsEl = document.getElementById("items");
    const statsEl = document.getElementById("stats");
    generated.textContent = `更新: ${new Date(DATA.generatedAt).toLocaleString("ja-JP")} / 今回追加: ${DATA.newItemsCount || 0}件`;

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
        <div class="stat"><strong>${counts.total}</strong><span>アーカイブ</span></div>
        <div class="stat"><strong>${counts.youtube}</strong><span>YouTube</span></div>
        <div class="stat"><strong>${counts.blog}</strong><span>Web記事</span></div>
        <div class="stat"><strong>${counts.high}</strong><span>重要度A以上</span></div>
      `;
    }

    function render() {
      const filtered = DATA.items.filter(matches).sort(compareItems);
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
            <span class="date-pill">${formatDate(item.published_at)}</span>
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
    function itemTime(item) {
      const date = new Date(item.published_at || 0);
      return Number.isNaN(date.getTime()) ? 0 : date.getTime();
    }
    function compareItems(a, b) {
      if (state.sort === "date") {
        const dateDelta = itemTime(b) - itemTime(a);
        if (dateDelta !== 0) return dateDelta;
      }
      const rank = { S: 0, A: 1, B: 2, C: 3 };
      return (rank[a.importance] ?? 9) - (rank[b.importance] ?? 9);
    }
    query.addEventListener("input", (event) => { state.query = event.target.value; render(); });
    source.addEventListener("change", (event) => { state.source = event.target.value; render(); });
    importance.addEventListener("change", (event) => { state.importance = event.target.value; render(); });
    sort.addEventListener("change", (event) => { state.sort = event.target.value; render(); });
    render();
  </script>
</body>
</html>
"""


ABOUT_TEMPLATE = """<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GPT Ads Portal について</title>
  <style>
    :root {
      --bg: #f3f5ef;
      --surface: #ffffff;
      --surface-soft: #f8faf5;
      --ink: #10231d;
      --muted: #65746d;
      --line: #d9e2dc;
      --gpt: #10a37f;
      --gpt-dark: #0b6b57;
      --gpt-ink: #062b22;
      --yellow: #f4d58a;
      --orange: #fed7aa;
      --red: #ffd7d3;
      --shadow: 0 20px 54px rgba(16, 35, 29, 0.12);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
      letter-spacing: 0;
    }
    a { color: inherit; }
    .wrap { max-width: 1160px; margin: 0 auto; padding: 0 24px; }
    header {
      color: #fff;
      background: #08251d;
      min-height: 86vh;
      display: flex;
      align-items: stretch;
      position: relative;
      overflow: hidden;
    }
    header::before {
      content: "";
      position: absolute;
      inset: 0;
      background-image:
        linear-gradient(rgba(255, 255, 255, 0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.045) 1px, transparent 1px);
      background-size: 42px 42px;
      opacity: 0.72;
    }
    .hero {
      position: relative;
      z-index: 1;
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(360px, 470px);
      gap: 42px;
      align-items: center;
      padding-top: 34px;
      padding-bottom: 52px;
    }
    .nav {
      position: absolute;
      top: 20px;
      left: 0;
      right: 0;
      z-index: 2;
    }
    .nav-inner {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }
    .brand {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      color: #d5e8df;
      font-size: 13px;
      font-weight: 800;
      text-transform: uppercase;
    }
    .brand-mark {
      width: 30px;
      height: 30px;
      border-radius: 8px;
      display: inline-grid;
      place-items: center;
      background: rgba(255, 255, 255, 0.12);
      border: 1px solid rgba(255, 255, 255, 0.24);
      color: #b9f3df;
      font-weight: 900;
    }
    .nav-link {
      display: inline-flex;
      align-items: center;
      min-height: 36px;
      padding: 8px 12px;
      color: #dff5ed;
      border: 1px solid rgba(255, 255, 255, 0.24);
      background: rgba(255, 255, 255, 0.10);
      border-radius: 8px;
      text-decoration: none;
      font-size: 13px;
      font-weight: 800;
    }
    .eyebrow {
      display: inline-flex;
      align-items: center;
      min-height: 30px;
      padding: 5px 10px;
      border: 1px solid rgba(185, 243, 223, 0.38);
      background: rgba(16, 163, 127, 0.14);
      border-radius: 999px;
      color: #b9f3df;
      font-size: 13px;
      font-weight: 800;
      margin-bottom: 18px;
    }
    h1 {
      margin: 0;
      font-size: 54px;
      line-height: 1.06;
      max-width: 820px;
    }
    .lead {
      margin: 20px 0 0;
      color: #d5e8df;
      font-size: 18px;
      line-height: 1.8;
      max-width: 760px;
    }
    .hero-actions {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 28px;
    }
    .button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 44px;
      padding: 10px 15px;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 800;
      border: 1px solid transparent;
    }
    .button.primary {
      color: var(--gpt-ink);
      background: #b9f3df;
    }
    .button.secondary {
      color: #dff5ed;
      border-color: rgba(255, 255, 255, 0.24);
      background: rgba(255, 255, 255, 0.10);
    }
    .signal-board {
      background: rgba(255, 255, 255, 0.94);
      color: var(--ink);
      border: 1px solid rgba(255, 255, 255, 0.74);
      border-radius: 12px;
      padding: 18px;
      box-shadow: var(--shadow);
    }
    .board-head {
      display: flex;
      justify-content: space-between;
      gap: 14px;
      align-items: center;
      padding-bottom: 14px;
      border-bottom: 1px solid var(--line);
    }
    .board-title { font-weight: 900; }
    .board-date { color: var(--muted); font-size: 12px; }
    .flow {
      display: grid;
      gap: 10px;
      margin-top: 16px;
    }
    .flow-step {
      display: grid;
      grid-template-columns: 34px 1fr auto;
      gap: 11px;
      align-items: center;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 11px;
      background: var(--surface-soft);
    }
    .number {
      width: 34px;
      height: 34px;
      display: inline-grid;
      place-items: center;
      border-radius: 8px;
      background: #e4f8ef;
      color: var(--gpt-dark);
      font-weight: 900;
    }
    .flow-step strong { display: block; font-size: 14px; }
    .flow-step span { color: var(--muted); font-size: 12px; }
    .tag {
      min-height: 28px;
      display: inline-flex;
      align-items: center;
      padding: 4px 8px;
      border-radius: 999px;
      background: #edf7f3;
      color: var(--gpt-dark);
      font-size: 12px;
      font-weight: 800;
      white-space: nowrap;
    }
    main { padding: 58px 0 78px; }
    section + section { margin-top: 68px; }
    .section-head {
      display: flex;
      justify-content: space-between;
      gap: 22px;
      align-items: end;
      margin-bottom: 26px;
      flex-wrap: wrap;
    }
    h2 {
      margin: 0;
      font-size: 29px;
      line-height: 1.25;
    }
    .section-copy {
      margin: 10px 0 0;
      color: var(--muted);
      line-height: 1.85;
      max-width: 820px;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 18px;
    }
    .stat, .card, .rule, .cost-box {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 12px 28px rgba(16, 35, 29, 0.06);
    }
    .stat { padding: 20px; }
    .stat strong { display: block; font-size: 29px; line-height: 1; }
    .stat span { color: var(--muted); font-size: 13px; }
    .cards {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 20px;
    }
    .card { padding: 24px; }
    .card h3, .rule h3, .cost-box h3 {
      margin: 0 0 12px;
      font-size: 17px;
      line-height: 1.45;
    }
    .card p, .rule p, .cost-box p {
      margin: 0;
      color: #33483f;
      line-height: 1.86;
    }
    .rule-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 20px;
    }
    .rule { padding: 24px; }
    .rank {
      width: 34px;
      height: 34px;
      display: inline-grid;
      place-items: center;
      border-radius: 8px;
      margin-bottom: 11px;
      font-weight: 900;
    }
    .rank-s { background: #fff7df; color: #8a5200; }
    .rank-a { background: #eaf8f1; color: #067647; }
    .rank-b { background: #fff7ed; color: #b54708; }
    .rank-c { background: #f2f4f7; color: #475467; }
    .timeline {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(215px, 1fr));
      gap: 18px;
    }
    .timeline .card { min-height: 172px; }
    .cost-layout {
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 20px;
      align-items: stretch;
    }
    .cost-box { padding: 26px; }
    .check-list {
      margin: 12px 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 9px;
      color: #33483f;
    }
    .check-list li {
      padding-left: 22px;
      position: relative;
      line-height: 1.6;
    }
    .check-list li::before {
      content: "";
      position: absolute;
      left: 0;
      top: 9px;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--gpt);
    }
    footer {
      padding: 24px 0 44px;
      color: var(--muted);
      font-size: 13px;
    }
    @media (max-width: 900px) {
      header { min-height: auto; }
      .hero {
        grid-template-columns: 1fr;
        padding-top: 92px;
      }
      h1 { font-size: 38px; }
      .stats, .cards, .rule-grid, .timeline, .cost-layout {
        grid-template-columns: 1fr;
      }
      .flow-step { grid-template-columns: 34px 1fr; }
      .tag { grid-column: 2; width: fit-content; }
    }
  </style>
</head>
<body>
  <header>
    <nav class="nav">
      <div class="wrap nav-inner">
        <div class="brand"><span class="brand-mark">G</span><span>GPT Ads Intelligence</span></div>
        <a class="nav-link" href="index.html">ポータルを開く</a>
      </div>
    </nav>
    <div class="wrap hero">
      <div>
        <div class="eyebrow">社内向けリサーチ基盤</div>
        <h1>GPT広告の変化を、人が巡回しなくても追える状態へ。</h1>
        <p class="lead">GPT Ads Portalは、ChatGPT広告、AI検索、生成AIマーケティングに関する情報を自動収集し、広告代理店のリサーチ観点で要約、重要度判定、アーカイブ化する社内ナレッジポータルです。</p>
        <div class="hero-actions">
          <a class="button primary" href="index.html">蓄積された情報を見る</a>
          <a class="button secondary" href="#criteria">選定基準を見る</a>
        </div>
      </div>
      <aside class="signal-board" aria-label="workflow">
        <div class="board-head">
          <div>
            <div class="board-title">How it works</div>
            <div class="board-date">Last updated: __GENERATED__</div>
          </div>
          <span class="tag">Low cost first</span>
        </div>
        <div class="flow">
          <div class="flow-step"><span class="number">1</span><div><strong>広く拾う</strong><span>YouTube、RSS、GoogleニュースRSS</span></div><span class="tag">Collect</span></div>
          <div class="flow-step"><span class="number">2</span><div><strong>関連情報だけ残す</strong><span>GPT広告、AI広告、AI検索、LLMO/GEO</span></div><span class="tag">Filter</span></div>
          <div class="flow-step"><span class="number">3</span><div><strong>Claudeで要約する</strong><span>最大24件の新着を要約、分類、重要度判定</span></div><span class="tag">Summarize</span></div>
          <div class="flow-step"><span class="number">4</span><div><strong>蓄積して共有する</strong><span>重複除去してアーカイブへ追加</span></div><span class="tag">Archive</span></div>
        </div>
      </aside>
    </div>
  </header>

  <main>
    <section class="wrap">
      <div class="section-head">
        <div>
          <h2>今のアーカイブ状況</h2>
          <p class="section-copy">表示件数は毎回上書きではなく、要約済みの情報を蓄積して増えていく設計です。</p>
        </div>
      </div>
      <div class="stats">
        <div class="stat"><strong>__TOTAL__</strong><span>総アーカイブ件数</span></div>
        <div class="stat"><strong>__BLOG__</strong><span>Web記事</span></div>
        <div class="stat"><strong>__YOUTUBE__</strong><span>YouTube</span></div>
        <div class="stat"><strong>__HIGH__</strong><span>重要度A以上</span></div>
      </div>
    </section>

    <section class="wrap">
      <div class="section-head">
        <div>
          <h2>このポータルが解決すること</h2>
          <p class="section-copy">目的は、個人の巡回作業を減らし、GPT広告領域の変化をチームで同じ粒度で見られる状態にすることです。</p>
        </div>
      </div>
      <div class="cards">
        <article class="card">
          <h3>情報収集の属人化を減らす</h3>
          <p>XやYouTube、ブログ、ニュースを毎日人が見に行く前提から、必要な情報が集まる前提へ移します。</p>
        </article>
        <article class="card">
          <h3>広告提案に使える形で残す</h3>
          <p>単なるリンク集ではなく、要約、ポイント、カテゴリ、重要度を付けて、提案やキャッチアップに使いやすくします。</p>
        </article>
        <article class="card">
          <h3>ナレッジを積み上げる</h3>
          <p>新着情報を毎回上書きせず、重複を除いてアーカイブへ追加します。過去の変化も検索できます。</p>
        </article>
      </div>
    </section>

    <section class="wrap" id="criteria">
      <div class="section-head">
        <div>
          <h2>情報を拾う基準</h2>
          <p class="section-copy">まず広く収集し、その後に広告代理店の実務に関係する情報だけを残します。</p>
        </div>
      </div>
      <div class="cards">
        <article class="card">
          <h3>対象テーマ</h3>
          <p>GPT広告、ChatGPT広告、AI広告、AI検索広告、LLMO/GEO、生成AIマーケティング、広告運用に関係する情報を対象にします。</p>
        </article>
        <article class="card">
          <h3>対象ソース</h3>
          <p>YouTube、国内外メディアRSS、公式ブログ、GoogleニュースRSSを中心に、無料または低コストで継続取得できる情報源を使います。</p>
        </article>
        <article class="card">
          <h3>除外する情報</h3>
          <p>教育、バイオ、インフラなど広告文脈が薄いAI記事や、プレゼント企画など実務インパクトが低い情報は除外します。</p>
        </article>
      </div>
    </section>

    <section class="wrap">
      <div class="section-head">
        <div>
          <h2>重要度の判定基準</h2>
          <p class="section-copy">Claudeが広告代理店のリサーチャーとして、ビジネス影響と実務活用度でSからCまで判定します。</p>
        </div>
      </div>
      <div class="rule-grid">
        <article class="rule">
          <div class="rank rank-s">S</div>
          <h3>市場影響が大きい一次情報</h3>
          <p>ChatGPT広告の開始、主要媒体の広告仕様変更、大手代理店の取り扱い開始など、すぐ共有すべき情報。</p>
        </article>
        <article class="rule">
          <div class="rank rank-a">A</div>
          <h3>提案や運用に使える情報</h3>
          <p>AI広告運用、AI検索、クリエイティブ生成、LLMO/GEOなど、実務や営業資料に転用しやすい情報。</p>
        </article>
        <article class="rule">
          <div class="rank rank-b">B</div>
          <h3>周辺トレンドとして有用</h3>
          <p>直接GPT広告ではないが、生成AIマーケティングやブランド接点の理解に役立つ情報。</p>
        </article>
        <article class="rule">
          <div class="rank rank-c">C</div>
          <h3>優先度は低いが関連あり</h3>
          <p>関連はあるものの、情報量や実務インパクトが限定的な情報。必要に応じて確認する扱い。</p>
        </article>
      </div>
    </section>

    <section class="wrap">
      <div class="section-head">
        <div>
          <h2>運用フロー</h2>
          <p class="section-copy">GitHub Actionsで定期実行し、収集から公開までを自動化します。</p>
        </div>
      </div>
      <div class="timeline">
        <article class="card"><h3>定期実行</h3><p>6時間ごとに自動実行。YouTube API無料枠とClaude APIコストを意識した頻度です。</p></article>
        <article class="card"><h3>情報収集</h3><p>RSS、GoogleニュースRSS、YouTubeから候補を集めます。Xは今回の対象外です。</p></article>
        <article class="card"><h3>重複除去</h3><p>URLを基準に同じ情報を除外し、すでにアーカイブ済みの情報は再要約しません。</p></article>
        <article class="card"><h3>Claude要約</h3><p>新着から最大24件を要約し、ポイント、カテゴリ、重要度を付与します。</p></article>
        <article class="card"><h3>公開</h3><p>要約済みデータをアーカイブへ追加し、GitHub Pagesで社内共有できるページを更新します。</p></article>
      </div>
    </section>

    <section class="wrap">
      <div class="cost-layout">
        <div class="cost-box">
          <h2>コスト方針</h2>
          <p class="section-copy">有料APIに依存しすぎず、まずは無料で継続できる収集経路を優先しています。Claude APIだけを要約と判断に使う設計です。</p>
          <ul class="check-list">
            <li>X APIは使わず、今回は収集対象から外しています。</li>
            <li>RSSとGoogleニュースRSSを中心に、追加コストのない取得を優先します。</li>
            <li>Claudeに送る件数は最大24件に制限し、要約コストを管理します。</li>
            <li>要約済み情報は再利用し、同じURLを何度も要約しないようにしています。</li>
          </ul>
        </div>
        <div class="cost-box">
          <h2>社内での使い方</h2>
          <p class="section-copy">毎日見る場所としてだけでなく、提案前の論点整理、AI広告トレンドの棚卸し、週次共有の材料として使えます。</p>
          <ul class="check-list">
            <li>最新順で直近の変化を確認する</li>
            <li>重要度S/Aだけに絞って優先確認する</li>
            <li>キーワード検索で過去ナレッジを探す</li>
            <li>元URLから一次情報へ戻って詳細確認する</li>
          </ul>
        </div>
      </div>
    </section>
  </main>

  <footer>
    <div class="wrap">GPT Ads Portal is a lightweight internal research portal for GPT ads, AI ads, and generative AI marketing signals.</div>
  </footer>
</body>
</html>
"""
