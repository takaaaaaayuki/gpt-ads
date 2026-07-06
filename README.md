# GPT Ads

GPT Ads is a low-cost research portal for GPT広告・AI広告・生成AIマーケティング.
It collects public information, removes duplicates, summarizes useful items, and builds a static website.

The first version is designed to work without Slack approval or API keys. When keys are added, YouTube, Claude summarization, GitHub Pages, and Slack notification can be enabled step by step.

## Output

Run the tool and these files are generated:

```text
data/raw/items_YYYY-MM-DD.jsonl
data/processed/items_YYYY-MM-DD.jsonl
data/processed/latest.json
reports/YYYY-MM-DD.md
public/index.html
logs/app.log
```

The main output for employees is:

```text
public/index.html
```

Open it in a browser to see the GPT Ads Portal.

## Quick Start

```bash
python -m project.main
```

Then open:

```text
public/index.html
```

The default command uses real sources only.
If there is no network access or no API key, the portal can be empty.

For a UI preview with sample data:

```bash
python -m project.main --demo
```

Optional local server:

```bash
python -m http.server 8000 -d public
```

Then open:

```text
http://localhost:8000
```

## Configuration

Copy the example env file:

```bash
cp .env.example .env
```

Set only the keys you want to use:

```text
ANTHROPIC_API_KEY=
YOUTUBE_API_KEY=
SLACK_BOT_TOKEN=
SLACK_CHANNEL_ID=
```

## YouTube Setup

YouTube collection uses the official YouTube Data API v3.

1. Open Google Cloud Console.
2. Create or select a project.
3. Enable `YouTube Data API v3`.
4. Create an API key.
5. Put it in `.env`:

```text
YOUTUBE_API_KEY=your_api_key_here
```

Test YouTube only:

```bash
.venv/bin/python - <<'PY'
from project.settings import load_dotenv, load_sources
from collect.youtube import collect_youtube
load_dotenv()
items = collect_youtube(load_sources()["youtube"])
print(f"YouTube items: {len(items)}")
for item in items[:5]:
    print(item.title, item.url)
PY
```

Google's documentation says YouTube Data API v3 requires a Google Account, a Google Developers Console project, authorization credentials, and enabling YouTube Data API v3 for that project.

## Claude API Setup

Claude summarization uses the Anthropic Messages API.

1. Open Claude Console.
2. Create or select a workspace.
3. Set up billing if required.
4. Create an API key.
5. Put it in `.env`:

```text
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-haiku-4-5
```

Run the full pipeline:

```bash
.venv/bin/python -m project.main
```

Anthropic's documentation says the Claude API is available through `https://api.anthropic.com`, requires a Claude Console account and API key, and uses headers including `x-api-key`, `anthropic-version`, and `content-type`.

Sources are configured in:

```text
config/sources.json
```

## Browser Setup For X

X collection is loginless and best-effort. Install Playwright only if you want to try X collection locally:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.ms-playwright" .venv/bin/python -m playwright install chromium
```

RSS works without this setup.

Test X only:

```bash
PLAYWRIGHT_BROWSERS_PATH="$(pwd)/.ms-playwright" .venv/bin/python -m project.main --x-only
```

If this returns `0`, X is likely blocking logged-out search.
Debug HTML and screenshots are saved under:

```text
data/raw/debug/
```

Run the stable portal without X:

```bash
.venv/bin/python -m project.main --skip-x
```

X strategy for the current MVP:

```text
1. Try loginless Playwright first.
2. Keep YouTube/RSS/Claude running even when X fails.
3. Avoid storing X passwords or automating Gmail/2FA.
4. Consider a logged-in session only if loginless collection is not enough.
5. Consider paid X API only as the last option.
```

## Phases

### Phase 1

- X collection interface
- Local raw data storage
- Static portal preview

The X collector is best-effort and loginless by default. X often blocks logged-out automated browsing, so this is intentionally isolated from the rest of the app.

### Phase 2

- Duplicate removal
- Claude API summarization
- Importance scoring

When `ANTHROPIC_API_KEY` is not set, a local heuristic summary is generated.

### Phase 3

- Slack Bot Token notification

Slack is optional. The site and report are still generated when Slack is not configured.

### Phase 4

- YouTube Data API collection

Set `YOUTUBE_API_KEY` to enable it.

### Phase 5

- RSS blog/newsletter collection

RSS uses Python standard library only.

### Phase 6

- GitHub Actions scheduled execution
- GitHub Pages deployment

Workflow:

```text
.github/workflows/gpt-ads.yml
```

Default schedule:

```text
Every 6 hours
```

This is intentionally less frequent than hourly to reduce Claude and API costs during the first internal trial.
Change the cron expression if hourly collection is required.

## Launch With GitHub Pages

This project currently runs locally.
To share it with employees, publish `public/index.html` with GitHub Pages.

Recommended launch flow:

```bash
git init
git branch -M main
git add .
git commit -m "Initial GPT Ads portal"
git remote add origin git@github.com:YOUR_ORG/gpt-ads.git
git push -u origin main
```

Then in GitHub:

1. Open the repository settings.
2. Open `Pages`.
3. Set the source to `GitHub Actions`.
4. Add repository secrets:

```text
ANTHROPIC_API_KEY
YOUTUBE_API_KEY
```

5. Run the `GPT Ads` workflow manually once.
6. Share the GitHub Pages URL with employees.

If company policy requires private access, use a private repository with GitHub Enterprise/organization Pages rules, or deploy the `public/` folder to an internal hosting service instead.

## Cost Policy

- Prefer RSS and official free APIs.
- Avoid paid APIs except Claude.
- Deduplicate before sending to Claude.
- Limit Claude calls with `GPT_ADS_MAX_ITEMS_PER_RUN`.
- Keep Slack optional.

Current collection policy:

```text
Collect broadly from YouTube, fixed RSS, and Japanese Google News RSS.
Filter aggressively for GPT ads / ChatGPT ads / AI ads relevance.
Summarize the top 24 items with Claude.
Show the summarized items in the portal with source, importance, and publication date.
Ignore items older than 120 days by default.
```

## Claude Skill Role

The web portal is the shared place employees can open.
Claude Skills can be added later as a usage layer: read the portal or exported data, then turn it into sales notes, weekly reports, proposal material, or trend summaries.

In short:

```text
Website = shared source of truth
Claude API = automatic summarization
Claude Skill = reusable employee workflow on top of the portal
Slack = optional notification channel
```

## Japanese Web Collection

The portal does not rely only on fixed blogs. It also uses Google News RSS search queries for Japanese GPT ads topics:

```text
ChatGPT広告
GPT広告
AI広告 生成AI
AI検索 広告
LLMO GEO 広告
AIマーケティング 広告
生成AIマーケティング 広告
ChatGPT 広告 日本
```

This helps surface Japanese articles that appear in Google News even when they are not published by the fixed RSS sources.
