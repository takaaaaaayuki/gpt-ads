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
        "x": sum(1 for item in items if item.source == "x"),
        "youtube": sum(1 for item in items if item.source == "youtube"),
        "blog": sum(1 for item in items if item.source == "blog"),
        "high": sum(1 for item in items if item.importance in ["S", "A"]),
    }
    return (
        ABOUT_TEMPLATE.replace("__TOTAL__", str(counts["total"]))
        .replace("__X__", str(counts["x"]))
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
      --bg: #ffffff;
      --surface: #ffffff;
      --surface-soft: #f5f6f8;
      --ink: #12141a;
      --muted: #656b76;
      --line: #e6e8ec;
      --line-strong: #d3d7de;
      --accent: #16224a;
      --accent-bright: #3454d1;
      --accent-soft: #eef1fb;
      --gold: #b7791f;
      --terracotta: #b54708;
      --youtube: #c0362c;
      --shadow: 0 20px 44px rgba(18, 20, 26, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
      word-break: auto-phrase;
    }
    .dot {
      display: inline-block;
      width: 6px;
      height: 6px;
      border-radius: 1px;
      background: var(--accent);
      flex: none;
    }
    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--accent-bright);
    }
    header.masthead {
      position: relative;
      overflow: hidden;
      background: var(--bg);
      padding: 56px 24px 40px;
      border-bottom: 1px solid var(--line);
    }
    .hero-motif {
      position: absolute;
      inset: 0;
      pointer-events: none;
      opacity: 0.5;
      background-image:
        radial-gradient(circle at 1px 1px, var(--line-strong) 1px, transparent 0),
        linear-gradient(120deg, transparent 20%, var(--accent-soft) 48%, transparent 76%);
      background-size: 24px 24px, 220% 220%;
      background-position: 0 0, 0% 0%;
      mask-image: linear-gradient(180deg, #000 0%, transparent 92%);
    }
    @media (prefers-reduced-motion: no-preference) {
      .hero-motif { animation: sweep 16s ease-in-out infinite; }
    }
    @keyframes sweep {
      0%, 100% { background-position: 0 0, 0% 0%; }
      50% { background-position: 0 0, 100% 60%; }
    }
    .wrap { max-width: 1180px; margin: 0 auto; position: relative; }
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
      gap: 6px;
      min-height: 34px;
      padding: 7px 13px;
      color: var(--ink);
      border: 1px solid var(--line-strong);
      background: #fff;
      border-radius: 3px;
      font-size: 13px;
      font-weight: 700;
      text-decoration: none;
    }
    .nav-link:hover { border-color: var(--accent); color: var(--accent-bright); }
    h1 {
      margin: 18px 0 0;
      font-size: clamp(40px, 7.5vw, 92px);
      font-weight: 800;
      line-height: 0.98;
      letter-spacing: -0.02em;
    }
    .subtitle { margin: 18px 0 0; color: var(--muted); font-size: 16px; max-width: 640px; line-height: 1.8; }
    .subtitle span { white-space: nowrap; }
    .generated {
      color: var(--muted);
      font-size: 12px;
      padding: 8px 12px;
      border: 1px solid var(--line);
      border-radius: 3px;
    }
    main { padding: 32px 24px 56px; }
    .toolbar {
      display: grid;
      grid-template-columns: minmax(260px, 1fr) minmax(135px, 170px) minmax(135px, 170px) minmax(160px, 210px) minmax(120px, 150px);
      gap: 10px;
      margin: 0 0 26px;
      align-items: center;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      box-shadow: var(--shadow);
    }
    input, select {
      width: 100%;
      min-height: 42px;
      border: 1px solid var(--line);
      border-radius: 5px;
      padding: 9px 11px;
      background: #fff;
      color: var(--ink);
      font: inherit;
      outline: none;
    }
    input:focus, select:focus {
      border-color: var(--accent-bright);
      box-shadow: 0 0 0 3px var(--accent-soft);
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 1px;
      background: var(--line);
      border: 1px solid var(--line);
      margin-bottom: 30px;
      border-radius: 8px;
      overflow: hidden;
    }
    .stat {
      background: var(--surface);
      padding: 20px 18px;
      border-top: 2px solid var(--accent-bright);
    }
    .stat strong { display: block; font-size: 30px; font-weight: 800; line-height: 1; letter-spacing: -0.01em; }
    .stat span { color: var(--muted); font-size: 12px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 1px;
      background: var(--line);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }
    article {
      background: var(--surface);
      padding: 22px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      min-width: 0;
    }
    @media (prefers-reduced-motion: no-preference) {
      article { transition: background-color 0.15s ease; }
    }
    article:hover { background: var(--surface-soft); }
    .meta {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
      align-items: center;
    }
    .meta-item {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }
    .meta-item .dot { background: var(--accent); }
    .meta-item.source-youtube .dot { background: var(--youtube); }
    .meta-item.source-youtube { color: var(--youtube); }
    .meta-item.source-x .dot { background: #101828; }
    .meta-item.source-x { color: #101828; }
    .meta-item[class*="importance-"] {
      padding: 4px 10px 4px 8px;
      border-radius: 999px;
      font-size: 11.5px;
    }
    .meta-item.importance-S .dot { background: var(--gold); }
    .meta-item.importance-S { color: #8a5a12; background: #fbf1de; }
    .meta-item.importance-A .dot { background: var(--accent-bright); }
    .meta-item.importance-A { color: var(--accent-bright); background: var(--accent-soft); }
    .meta-item.importance-B .dot { background: var(--terracotta); }
    .meta-item.importance-B { color: var(--terracotta); background: #fbe9de; }
    .meta-item.importance-C .dot { background: var(--muted); }
    .meta-item.importance-C { color: var(--muted); background: var(--surface-soft); }
    .topic-tags {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      align-items: center;
    }
    .topic-tag {
      display: inline-flex;
      align-items: center;
      min-height: 22px;
      padding: 2px 9px;
      border-radius: 999px;
      background: var(--surface-soft);
      color: #3a3a3a;
      border: 1px solid var(--line);
      font-size: 11px;
      font-weight: 700;
    }
    h2 {
      margin: 0;
      font-size: 19px;
      font-weight: 800;
      line-height: 1.4;
      overflow-wrap: anywhere;
    }
    .byline {
      color: var(--muted);
      font-size: 12px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    p { margin: 0; color: #333333; line-height: 1.75; overflow-wrap: anywhere; }
    ul { margin: 0; padding-left: 18px; color: #333333; line-height: 1.6; }
    li + li { margin-top: 5px; }
    .source-link {
      margin-top: auto;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: var(--accent-bright);
      font-weight: 700;
      text-decoration: none;
      overflow-wrap: anywhere;
      border-top: 1px solid var(--line);
      padding-top: 12px;
    }
    .source-link:hover { text-decoration: underline; }
    .empty {
      padding: 28px;
      background: var(--surface);
      color: var(--muted);
      grid-column: 1 / -1;
    }
    @media (max-width: 880px) {
      header.masthead { padding: 40px 18px 32px; }
      main { padding: 22px 16px; }
      .toolbar { grid-template-columns: 1fr 1fr; }
      .grid { grid-template-columns: 1fr; }
    }
    @media (max-width: 600px) {
      header.masthead { padding: 32px 16px 28px; }
      .toolbar { grid-template-columns: 1fr; }
      .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
  </style>
</head>
<body>
  <header class="masthead">
    <div class="hero-motif" aria-hidden="true"></div>
    <div class="wrap top">
      <div>
        <div class="eyebrow"><span class="dot"></span>GPT Ads Intelligence</div>
        <h1>GPT Ads<br>Portal</h1>
        <p class="subtitle"><span>ChatGPT広告、AI検索、</span> <span>生成AIマーケティングの</span> <span>動きを追うリサーチポータル</span></p>
      </div>
      <div class="header-actions">
        <a class="nav-link" href="about.html">このポータルについて <span>→</span></a>
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
      <select id="topic">
        <option value="">すべてのタグ</option>
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
    const state = { query: "", source: "", importance: "", topic: "", sort: "date" };
    const labels = { x: "X", youtube: "YouTube", blog: "Web記事", newsletter: "ニュースレター" };
    const generated = document.getElementById("generated");
    const query = document.getElementById("query");
    const source = document.getElementById("source");
    const importance = document.getElementById("importance");
    const topic = document.getElementById("topic");
    const sort = document.getElementById("sort");
    const itemsEl = document.getElementById("items");
    const statsEl = document.getElementById("stats");
    generated.textContent = `更新: ${new Date(DATA.generatedAt).toLocaleString("ja-JP")} / 今回追加: ${DATA.newItemsCount || 0}件`;

    [...new Set(DATA.items.map((item) => item.source))].forEach((name) => {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = labels[name] || name;
      source.appendChild(option);
    });
    DATA.items.forEach((item) => { item.topics = topicTags(item); });
    [...new Set(DATA.items.flatMap((item) => item.topics))].sort().forEach((name) => {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      topic.appendChild(option);
    });

    function matches(item) {
      const haystack = `${item.title} ${item.summary} ${item.text} ${item.category} ${(item.topics || []).join(" ")}`.toLowerCase();
      return (!state.query || haystack.includes(state.query.toLowerCase()))
        && (!state.source || item.source === state.source)
        && (!state.importance || item.importance === state.importance)
        && (!state.topic || (item.topics || []).includes(state.topic));
    }

    function renderStats(items) {
      const counts = {
        total: items.length,
        x: items.filter((item) => item.source === "x").length,
        youtube: items.filter((item) => item.source === "youtube").length,
        blog: items.filter((item) => item.source === "blog").length,
        high: items.filter((item) => ["S", "A"].includes(item.importance)).length,
      };
      statsEl.innerHTML = `
        <div class="stat"><strong>${counts.total}</strong><span>アーカイブ</span></div>
        <div class="stat"><strong>${counts.x}</strong><span>X</span></div>
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
            <span class="meta-item source-${item.source}"><span class="dot"></span>${labels[item.source] || item.source}</span>
            <span class="meta-item importance-${item.importance || "C"}"><span class="dot"></span>重要度 ${item.importance || "C"}</span>
          </div>
          <div class="topic-tags">${(item.topics || []).map((tag) => `<span class="topic-tag">${escapeHtml(tag)}</span>`).join("")}</div>
          <h2>${escapeHtml(item.title)}</h2>
          <div class="byline">
            <span>${escapeHtml(item.author || labels[item.source] || "")}</span>
            <span>${formatDate(item.published_at)}</span>
          </div>
          <p>${escapeHtml(item.summary || item.text || "")}</p>
          <ul>${(item.points || []).slice(0, 3).map((point) => `<li>${escapeHtml(point)}</li>`).join("")}</ul>
          <a class="source-link" href="${escapeAttr(item.url)}" target="_blank" rel="noopener">元URLを開く <span>↗</span></a>
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
    function topicTags(item) {
      const text = `${item.title} ${item.summary} ${item.text} ${item.category}`.toLowerCase();
      const tags = [];
      const add = (name) => { if (!tags.includes(name)) tags.push(name); };
      if (includesAny(text, ["gpt広告", "chatgpt広告", "chatgpt ads", "gpt ads", "chatgpt ad", "gpt ad"])) add("GPT広告");
      if (includesAny(text, ["ai広告", "ai ads", "ai advertising", "生成ai広告", "会話型広告", "aiエージェント広告"])) add("AI広告");
      if (includesAny(text, ["ai検索", "ai search", "aio", "llmo", "geo", "seo", "検索"])) add("AI検索/LLMO");
      if (includesAny(text, ["google ads", "meta ads", "広告運用", "campaign", "キャンペーン", "出稿", "運用", "獲得", "ファネル"])) add("広告運用");
      if (includesAny(text, ["生成aiマーケティング", "aiマーケティング", "marketing", "マーケティング", "ブランド", "brand"])) add("生成AIマーケ");
      if (includesAny(text, ["creative", "クリエイティブ", "画像生成", "動画生成", "広告素材", "バナー", "canva", "ugc"])) add("クリエイティブ");
      if (includesAny(text, ["規制", "倫理", "privacy", "policy", "政治広告", "copyright", "著作権"])) add("規制/倫理");
      if (!tags.length) add("その他");
      return tags.slice(0, 4);
    }
    function includesAny(text, terms) {
      return terms.some((term) => text.includes(term));
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
    topic.addEventListener("change", (event) => { state.topic = event.target.value; render(); });
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
      --bg: #ffffff;
      --surface: #ffffff;
      --surface-soft: #f5f6f8;
      --ink: #12141a;
      --muted: #656b76;
      --line: #e6e8ec;
      --line-strong: #d3d7de;
      --accent: #16224a;
      --accent-bright: #3454d1;
      --accent-soft: #eef1fb;
      --gold: #b7791f;
      --terracotta: #b54708;
      --shadow: 0 20px 44px rgba(18, 20, 26, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
      word-break: auto-phrase;
    }
    a { color: inherit; }
    .wrap { max-width: 1160px; margin: 0 auto; padding: 0 24px; }
    .dot {
      display: inline-block;
      width: 6px;
      height: 6px;
      border-radius: 1px;
      background: var(--accent);
      flex: none;
    }
    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--accent-bright);
      margin-bottom: 14px;
    }
    header {
      position: relative;
      overflow: hidden;
      background: var(--bg);
      border-bottom: 1px solid var(--line);
    }
    .hero-motif {
      position: absolute;
      inset: 0;
      pointer-events: none;
      opacity: 0.5;
      background-image:
        radial-gradient(circle at 1px 1px, var(--line-strong) 1px, transparent 0),
        linear-gradient(120deg, transparent 20%, var(--accent-soft) 48%, transparent 76%);
      background-size: 24px 24px, 220% 220%;
      mask-image: linear-gradient(180deg, #000 0%, transparent 92%);
    }
    @media (prefers-reduced-motion: no-preference) {
      .hero-motif { animation: sweep 16s ease-in-out infinite; }
    }
    @keyframes sweep {
      0%, 100% { background-position: 0 0, 0% 0%; }
      50% { background-position: 0 0, 100% 60%; }
    }
    .nav {
      position: relative;
      z-index: 1;
      padding-top: 22px;
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
      gap: 8px;
      color: var(--ink);
      font-size: 13px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .nav-link {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      min-height: 36px;
      padding: 8px 13px;
      color: var(--ink);
      background: #fff;
      border: 1px solid var(--line-strong);
      border-radius: 3px;
      text-decoration: none;
      font-size: 13px;
      font-weight: 700;
    }
    .nav-link:hover { border-color: var(--accent); color: var(--accent-bright); }
    .hero {
      position: relative;
      z-index: 1;
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(340px, 440px);
      gap: 42px;
      align-items: center;
      padding-top: 40px;
      padding-bottom: 64px;
    }
    h1 {
      margin: 0;
      font-size: clamp(32px, 4.6vw, 60px);
      font-weight: 800;
      line-height: 1.15;
      max-width: 780px;
      letter-spacing: -0.015em;
    }
    h1 span { white-space: nowrap; }
    .lead {
      margin: 20px 0 0;
      color: var(--muted);
      font-size: 17px;
      line-height: 1.85;
      max-width: 720px;
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
      gap: 6px;
      justify-content: center;
      min-height: 44px;
      padding: 10px 16px;
      border-radius: 5px;
      text-decoration: none;
      font-weight: 700;
      border: 1px solid transparent;
    }
    .button.primary { color: #fff; background: var(--accent); }
    .button.primary:hover { background: var(--accent-bright); }
    .button.secondary { color: var(--ink); border-color: var(--line-strong); }
    .button.secondary:hover { border-color: var(--accent); color: var(--accent-bright); }
    .signal-board {
      background: #fff;
      color: var(--ink);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 20px;
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
    .board-title { font-weight: 800; }
    .board-date { color: var(--muted); font-size: 12px; }
    .flow { display: grid; gap: 10px; margin-top: 16px; }
    .flow-step {
      display: grid;
      grid-template-columns: 30px 1fr auto;
      gap: 11px;
      align-items: center;
      border: 1px solid var(--line);
      border-radius: 5px;
      padding: 11px;
      background: var(--surface-soft);
    }
    .number {
      width: 30px;
      height: 30px;
      display: inline-grid;
      place-items: center;
      border-radius: 5px;
      background: var(--accent-soft);
      color: var(--accent);
      font-weight: 800;
      font-size: 13px;
    }
    .flow-step strong { display: block; font-size: 14px; }
    .flow-step span { color: var(--muted); font-size: 12px; }
    .tag {
      min-height: 26px;
      display: inline-flex;
      align-items: center;
      padding: 4px 9px;
      border-radius: 999px;
      background: var(--surface-soft);
      color: var(--ink);
      border: 1px solid var(--line);
      font-size: 11px;
      font-weight: 700;
      white-space: nowrap;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    main { padding: 64px 0 80px; }
    section + section { margin-top: 72px; }
    .section-head {
      display: flex;
      justify-content: space-between;
      gap: 22px;
      align-items: end;
      margin-bottom: 28px;
      flex-wrap: wrap;
    }
    h2 { margin: 0; font-size: clamp(24px, 2.8vw, 34px); font-weight: 800; line-height: 1.3; }
    .section-copy { margin: 10px 0 0; color: var(--muted); line-height: 1.85; max-width: 820px; }
    .stats { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
    .stat { background: var(--surface); padding: 20px; border-top: 2px solid var(--accent-bright); }
    .stat strong { display: block; font-size: 28px; font-weight: 800; line-height: 1; }
    .stat span { color: var(--muted); font-size: 13px; }
    .cards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
    .card { background: var(--surface); padding: 26px; }
    .card h3, .rule h3, .cost-box h3 { margin: 0 0 12px; font-size: 17px; font-weight: 800; line-height: 1.45; }
    .card p, .rule p, .cost-box p { margin: 0; color: #333333; line-height: 1.86; }
    .rule-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
    .rule { background: var(--surface); padding: 26px; }
    .rank {
      width: 32px;
      height: 32px;
      display: inline-grid;
      place-items: center;
      border-radius: 5px;
      margin-bottom: 12px;
      font-weight: 800;
    }
    .rank-s { background: #fbf1de; color: var(--gold); }
    .rank-a { background: var(--accent-soft); color: var(--accent-bright); }
    .rank-b { background: #fbe9de; color: var(--terracotta); }
    .rank-c { background: var(--surface-soft); color: var(--muted); }
    .timeline { display: grid; grid-template-columns: repeat(auto-fit, minmax(215px, 1fr)); gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
    .timeline .card { min-height: 172px; }
    .cost-layout { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; align-items: stretch; }
    .cost-box { padding: 28px; background: var(--surface); }
    .cost-box.highlight { background: var(--accent-soft); }
    .cost-box.highlight h2 { color: var(--accent); }
    .check-list { margin: 14px 0 0; padding: 0; list-style: none; display: grid; gap: 10px; color: #333333; }
    .check-list li { padding-left: 20px; position: relative; line-height: 1.65; }
    .check-list li::before {
      content: "";
      position: absolute;
      left: 0;
      top: 9px;
      width: 6px;
      height: 6px;
      border-radius: 1px;
      background: var(--accent-bright);
    }
    footer { padding: 26px 0 48px; color: var(--muted); font-size: 13px; border-top: 1px solid var(--line); }
    @media (max-width: 900px) {
      .hero { grid-template-columns: 1fr; padding-top: 96px; }
      .nav { position: absolute; top: 20px; left: 0; right: 0; padding: 0 24px; z-index: 1; }
      .stats, .cards, .rule-grid, .timeline, .cost-layout { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <div class="hero-motif" aria-hidden="true"></div>
    <nav class="nav">
      <div class="wrap nav-inner">
        <div class="brand"><span class="dot"></span>GPT Ads Intelligence</div>
        <a class="nav-link" href="index.html">ポータルを開く</a>
      </div>
    </nav>
    <div class="wrap hero">
      <div>
        <div class="eyebrow"><span class="dot"></span>社内向けリサーチ基盤</div>
        <h1><span>GPT広告の変化を、</span> <span>人が巡回しなくても</span> <span>追える状態へ。</span></h1>
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
          <div class="eyebrow"><span class="dot"></span>Archive Status</div>
          <h2>今のアーカイブ状況</h2>
          <p class="section-copy">表示件数は毎回上書きではなく、要約済みの情報を蓄積して増えていく設計です。</p>
        </div>
      </div>
      <div class="stats">
        <div class="stat"><strong>__TOTAL__</strong><span>総アーカイブ件数</span></div>
        <div class="stat"><strong>__X__</strong><span>X</span></div>
        <div class="stat"><strong>__BLOG__</strong><span>Web記事</span></div>
        <div class="stat"><strong>__YOUTUBE__</strong><span>YouTube</span></div>
        <div class="stat"><strong>__HIGH__</strong><span>重要度A以上</span></div>
      </div>
    </section>

    <section class="wrap">
      <div class="section-head">
        <div>
          <div class="eyebrow"><span class="dot"></span>Purpose</div>
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
          <div class="eyebrow"><span class="dot"></span>Selection Criteria</div>
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
          <div class="eyebrow"><span class="dot"></span>Importance Rules</div>
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
          <div class="eyebrow"><span class="dot"></span>Operation Flow</div>
          <h2>運用フロー</h2>
          <p class="section-copy">GitHub Actionsで定期実行し、収集から公開までを自動化します。</p>
        </div>
      </div>
      <div class="timeline">
        <article class="card"><h3>定期実行</h3><p>6時間ごとに自動実行。YouTube API無料枠とClaude APIコストを意識した頻度です。</p></article>
        <article class="card"><h3>情報収集</h3><p>RSS、GoogleニュースRSS、YouTubeから候補を集めます。XはCoworkが作成したExcelから追加できます。</p></article>
        <article class="card"><h3>重複除去とタグ付け</h3><p>URLを基準に重複を除外し、GPT広告、AI広告、AI検索/LLMOなどのタグで分類します。</p></article>
        <article class="card"><h3>Claude要約</h3><p>新着から最大24件を要約し、ポイント、カテゴリ、重要度を付与します。</p></article>
        <article class="card"><h3>公開</h3><p>要約済みデータをアーカイブへ追加し、GitHub Pagesで社内共有できるページを更新します。</p></article>
      </div>
    </section>

    <section class="wrap">
      <div class="cost-layout">
        <div class="cost-box highlight">
          <h2>コスト方針</h2>
          <p class="section-copy">有料APIに依存しすぎず、まずは無料で継続できる収集経路を優先しています。Claude APIだけを要約と判断に使う設計です。</p>
          <ul class="check-list">
            <li>X APIは使わず、Coworkが作成したExcelを取り込む方式にしています。</li>
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
            <li>GPT広告、AI広告、AI検索/LLMOなどのタグで絞る</li>
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
