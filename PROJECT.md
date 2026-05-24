# Dwell Studio 24 — Full Automation Pipeline Guide

By placing this file in your Claude Code project as `CLAUDE.md` or under `.claude/commands/`, the entire article production pipeline for Dwell Studio 24 runs on autopilot. Human involvement is limited to **final quality approval** and **strategic direction decisions only**.

---

SEOで検索上位（#1）を狙うため、関連キーワードを一括調査して最も勝てるKWを特定し、SEO最強のクオリティブログを作成する。

## TOKI'S BRAND VOICE

### Who Is Toki?

TokiはDwell Studio 24のクリエイター。Japandi＆Japandi-inspiredインテリアデザインブログを運営。Southern CaliforniaにあるBuildされて77年の家に夫と3人の子供と暮らす。読者はインテリアが好きな25歳以上〜50歳くらいの女性・ママ（中〜高収入）。

---

## 1. Overview

### Site Information

- **Media Name**: Dwell Studio 24
- **Niche**: Interior Design & Home Decor
- **Article Language**: American English (all articles, no exceptions)

### What This System Does

Automates the full SEO content pipeline for Dwell Studio 24 — from keyword selection through scheduled publishing and post-publish analytics.

### Automated Workflow

1. **KW Selection Agent**: Mangools KWFinder API → competitor KW extraction → 3C analysis → SEO Knowledge 3-round critical review → finalize
2. **Research Agent**: X API v2 (30+ posts) + YouTube transcripts (5–10 videos)
3. **Design Agent**: Analyze top 10 SERP articles H2/H3 structure → common 60–70% + unique 30–40%
4. **Writing Agent**: seo-evergreen-writer 10-step workflow → AI-feel elimination → SEO Knowledge quality review 10–20 rounds
5. **Quality Agent**: 5-agent parallel scoring (95+ points required to schedule)
6. **Publishing Agent**: Featured image + H2 inline images → WordPress scheduled post (every Wed & Sat at 8:00 AM ET)
7. **Analytics Agent**: Index registration → spreadsheet update → internal link addition → KPI report

### Expected Outcomes

- 2 articles/week scheduled every **Wednesday and Saturday at 8:00 AM ET**
- Quality management based on SEO Knowledge
- GEO/LLMO compatibility (improved AI Overview citation rate)
- Human review limited to final approval and direction decisions

---

## 2. Prerequisites

### Required Tools / APIs

| Tool | Purpose | Notes |
| :---- | :---- | :---- |
| Claude Code (Anthropic CLI) | Pipeline execution | Run via Scheduled Tasks or cron |
| WordPress site | Article publishing | REST API (auto-post API) must be enabled. Rank Math plugin recommended |
| Mangools API (KWFinder) | KW research, competitor analysis, SERP analysis | API key required |
| X (Twitter) API v2 | Primary source collection (posts) | Bearer Token required. note_tweet field support |
| YouTube Data API v3 | Primary source collection (videos) | API key required |
| Google Sheets API | Data management & KPI reports | MCP integration recommended |
| Google Indexing API | Immediate index registration after publishing | Service account required. GSC owner permission required |
| AI Image Generation (Canva MCP / NanoBanana MCP or Gemini API) | Image generation (featured + inline) | Canva MCP recommended (free plan supported). NanoBanana or Gemini Flash as fallback |
| yt-dlp | YouTube auto-subtitle extraction | `pip install yt-dlp` |
| Python 3.10+ | Markdown→HTML conversion, script execution | `markdown` library (extensions: tables, extra) |
| Node.js 18+ | Some script execution | Optional |

### Auth Credentials (.env file)

```
# WordPress
WP_URL=https://dwellstudio24.com/
WP_USER=info.mail24@me.com
WP_PASSWORD=APk2GMmEtOvptE4x1NZygBv8

# X (Twitter) API v2
X_BEARER_TOKEN=YOUR_X_BEARER_TOKEN
X_API_KEY=YOUR_X_API_KEY
X_API_SECRET=YOUR_X_API_SECRET

# YouTube Data API v3
YOUTUBE_API_KEY=AIzaSyAe_jNtNjCslS4LdonUWM33Ow4myaagfS0

# Google Sheets API
GOOGLE_SHEETS_CREDENTIALS_PATH=./credentials.json
GOOGLE_SHEETS_TOKEN_PATH=./sheets-token.json

# Google Indexing API
INDEXING_SERVICE_ACCOUNT_PATH=my-youtube-api-496918-838eabbc011.json./indexing-service-account.json

# Mangools API
MANGOOLS_API_KEY=57ca0ce06e416507b37176e3531930f761474251afb88ab212eac3b28ffb19d9

# Image Generation (NanoBanana or Gemini)
NANOBANANA_API_KEY=YOUR_NANOBANANA_KEY
# or
GEMINI_API_KEY=AIzaSyCvZ_7rseV5XuI3ELq4RN3B7CIdcGbTs54

# Google Analytics (KPI reporting)
GA4_PROPERTY_ID=482967235

# Google Search Console
GSC_SITE_URL=https://search.google.com/search-console?resource_id=sc-domain%3Adwellstudio24.com

# Google Sheets
SPREADSHEET_ID=YOUR_SPREADSHEET_ID
```

---

## 3. Setup Instructions

### 3.1 Directory Structure

```
dwell-studio-24/
├── PROJECT.md                  ← This file
├── CLAUDE.md                   ← Brand voice & writing guide
├── .env                        ← Auth credentials (.gitignore target)
├── articles/                   ← Article markdown files
├── automation/
│   ├── images/                 ← Generated images
│   ├── logs/                   ← Execution logs
│   └── design/                 ← Design rules
├── data/
│   ├── x_trends/               ← X API collected data
│   └── youtube_transcripts/    ← YouTube transcripts
├── scripts/                    ← Helper scripts
├── kpi_feedback.md             ← KPI feedback (auto-updated)
└── wp_additional_css.css       ← WordPress additional CSS
```

### 3.2 WordPress Settings

1. **Enable REST API**: Default in WordPress 4.7+
2. **Create Application Password**: User Settings → Application Passwords → Create New
3. **Rank Math**: Install + activate. REST API enables meta info & schema settings.
4. **Permalink structure**: `/%category%/%postname%/` recommended
5. **Create categories**: Create interior design categories in advance and note the category IDs

---

## 4. Automation Pipeline Definition (All 7 Phases)

Execute each Phase in order. Confirm completion before moving to the next Phase.

---

### Phase 1: KW Selection Agent

**Purpose**: Determine the keyword for the next article.

**Steps**:

1. **Check Article Log**
   - Get the top "Not Started" row from the spreadsheet "Article Log" tab
   - If a "Not Started" row exists → proceed to Phase 2 with that KW (no KWFinder research needed)
   - If no "Not Started" rows → run the KW selection process below

2. **Competitor KW Extraction (3C Analysis)**
   - Use Mangools KWFinder API to discover competitors of Dwell Studio 24
   - Extract top KWs from 3–5 competitor sites
   - Filter: country=US, volume>=200, position<=20
   - Prioritize KWs where Dwell Studio 24 can offer unique value

3. **Fetch KW Data**
   - Use Mangools KWFinder API to get: Volume / KD / CPC / Intent
   - Fields: keyword, volume, difficulty, cpc, traffic_potential, intents
   - Country: US

4. **🔍 Mangools KWFinder Browser Research (Required)**

   Open `app.mangools.com/kwfinder` in Chrome and search the Focus Keyword. Collect the following:

   - **Related Keywords tab**: Related KW list, monthly search volume, KD, trend % — record in Keyword Table
   - **Autocomplete Keywords tab**: Suggest-style long-tail KWs for H2/H3 and tag candidates
   - **SERP Overview**: Check DA/PA/LPS/EV of top 10 articles (lower DR = more ranking opportunity)

   **📈 Trend % Rule (Critical):**
   - **Prioritize KWs with positive trend (↑)** (e.g., `+45%` > `+12%`)
   - Only use negative-trend KWs if no positive alternatives exist
   - Record trend data in the Notes column of the Keyword Table

5. **🌸 Pinterest Trends Research**

   Open `trends.pinterest.com` and search the Focus Keyword. Collect:

   - Trend rise/fall graph (understand seasonality and peak months)
   - Related trend words (use for H2 headings, tags, and LSI keywords in the article)
   - If blocked: use WebSearch with `"pinterest trends [keyword] 2026"` to retrieve alternative data

6. **SEO Knowledge 3-Round Critical Review**
   - Review from 9 angles, 3 times:
     1. Prioritizes long-tail (Vol ≤ 1,000)?
     2. CV distance (Do/Buy priority) correctly classified?
     3. Cannibalization risk? (check parent_topic)
     4. KD reliability (validate against DR of top SERP sites)?
     5. Topical authority design (cluster first → pillar later)?
     6. Evidence of low-DR sites ranking in competitor SERP?
     7. Does this KW allow for unique value and E-E-A-T?
     8. Is the attack sequence reasonable?
     9. Any missing KW categories?
   - If a point is valid → fix it. If not → document why it was rejected.

7. **Finalize KW & Update Spreadsheet**
   - Record finalized KW in "KW Strategy" tab
   - Add new row to "Article Log" tab (Status: KW Selection Complete)

---

### Phase 2: Research Agent

**Purpose**: Collect primary sources (X posts + YouTube transcripts) to give the article originality.

**Steps**:

1. **Collect X Primary Sources**
   - Search X API v2 for posts related to the article KW (past 1 month, min_impressions: 500)
   - Required fields:
     - `note_tweet` (full long-form tweet text — standard text field cuts off at 280 chars)
     - Full thread text (`conversation_id` + `from:{username}` to get same thread)
     - Media URLs (images/video)
     - Post URL
   - Target: 30+ posts
   - Save to `data/x_trends/x_enriched_article{N}.json`
   - Record in spreadsheet "X Primary Sources" tab (Column F: full text, 200+ chars)

2. **Collect YouTube Primary Sources**
   - Search YouTube Data API v3 for related videos (top 10)
   - Use `yt-dlp` to get auto-subtitles in English:
     ```
     yt-dlp --write-auto-sub --sub-lang en --skip-download -o "data/youtube_transcripts/%(id)s" "VIDEO_URL"
     ```
   - Save transcript files to `data/youtube_transcripts/{videoId}.txt`
   - Record in spreadsheet "YouTube Primary Sources" tab (transcript path in column)
   - **Select the best matching video to embed in the article (inserted below Key Takeaways)**

3. **🌸 Pinterest Trends Research (Article-Level)**

   Open `trends.pinterest.com` and search the Focus Keyword. Collect:

   - Trend rise/fall graph — identify seasonality and peak months
   - Related trend words — apply to H2 structure, article tags, and LSI keyword placement
   - If blocked: use WebSearch with `"pinterest trends [keyword] 2026"` to retrieve alternative data
   - Record peak months and related trend words for use in Phase 3 outline design

4. **Handling API 503 Errors**
   - Do NOT immediately fall back
   - Poll every 10 minutes, wait for recovery
   - Only log to error log and proceed if 503 occurs 3 times in a row

5. **Update Article Log**
   - Status → "Primary Sources Collected"

---

### Phase 3: Design Agent (Most Critical Phase)

**Purpose**: Analyze top SERP article structures and finalize article outline with common patterns + unique sections.

**Steps**:

1. **Extract H2/H3 Structure from Top 10 SERP Articles**
   - Use Mangools SERPChecker API to get top 10 article URLs / DA / titles
   - Fetch all 10 sites (minimum 7) and extract H2/H3 headings
   - Write all site heading structures to the spreadsheet

2. **Common Pattern Analysis**
   - Categorize all H2s across sites (e.g., "What is," "Types," "How to Choose," "Product List," "Conclusion")
   - Calculate occurrence rate per category (how many of the 10 sites have it)
   - **Common 60–70%**: H2s appearing in 50%+ of sites → include (core of search intent)
   - **Unique 30–40%**: H2s appearing in ≤25% or 0% → design from primary sources (differentiation)

3. **Assign Primary Sources to H2s**
   - For each confirmed H2, determine which X posts and YouTube content to use
   - Specify exactly which post/video segment will be used for each H2
   - Determine whether media (images/video) can be embedded in the article

4. **User Confirmation**
   - **Present the confirmed H2 outline to the user and get approval before proceeding to Phase 4**
   - In auto-run mode, this step can be skipped (controlled by setting)

5. **Update Article Log**
   - Status → "Design Complete"

---

### Phase 4: Writing Agent

**Purpose**: Generate a high-quality, SEO-optimized, evergreen article for Dwell Studio 24 in American English.

See `CLAUDE.md` for full brand voice, tone pillars, vocabulary rules, and AI-feel elimination checklist.

#### Required Article Structure

```
① Intro (3 paragraphs, dropCap on first — focus keyword in Line 1)
② Affiliate Warning Block (before Key Takeaways — manual WP pattern insertion)
③ Key Takeaways (H3 tag, 5–6 bullets)
④ YouTube Embed (1 video matching the article topic — immediately after Key Takeaways)
⑤ H2: [Core Topic 1]
   └─ H3: sub-point
   └─ H3: sub-point
   └─ READ MORE: [real internal link, open in new tab]
   └─ My Top Tip: [Toki's voice]
⑥ H2: [Core Topic 2–8...]
   └─ (repeat pattern)
⑦ H2: Ideas For Small [Room]   ← room articles only
⑧ H2: Live the [Topic] Lifestyle   ← lifestyle articles only
⑨ H2: My Favorite Shops (My fav shop list pattern)
⑩ H2: FAQ (6–8 Q&As, FAQPage Schema)
⑪ H2: The Bottom Line (3 paragraphs + Tag me CTA)
⑫ Explore More Block (select matching category)
```

#### YouTube Embed Block Format

Research a YouTube video that matches the article topic and insert it immediately below Key Takeaways:

```html
<!-- wp:embed {"url":"https://www.youtube.com/watch?v=VIDEO_ID","type":"video","providerNameSlug":"youtube","responsive":true,"className":"wp-embed-aspect-16-9 wp-has-aspect-ratio"} -->
<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper">
https://www.youtube.com/watch?v=VIDEO_ID
</div></figure>
<!-- /wp:embed -->
```

- Use YouTube Data API v3 to find the best-matching video (home design / interior channel preferred)
- Select based on: relevance to focus keyword, view count, recency, channel authority
- Verify the video is publicly available before embedding

#### Word Count & Quality Targets

- **2,800–3,200 words**
- Focus keyword density: **1.0–2.5%**
- 20%+ content drawn from primary sources (X posts + YouTube transcripts)
- 3+ unique facts or original insights not found in competing articles

#### AI-Feel Elimination Checklist (Required)

| # | Check Item | NG Example | OK Example |
|:---|:---|:---|:---|
| 1 | No vague conclusions | "This may work in some cases" | Specify exact conditions or scenarios |
| 2 | "It's important to" max 3x | Appears 4+ times | Replace with specific, actionable sentences |
| 3 | Vary sentence patterns | Every paragraph ends the same way | Mix: short punchy sentences, questions, em dashes |
| 4 | No 3 consecutive bullet lists | List → List → List | Insert lead sentence or table between lists |
| 5 | Remove "This leads to" / "As a result" | "This leads to a better result" | Describe cause-effect directly and concretely |
| 6 | Replace "I recommend considering" | "You might want to consider…" | "Try this" / "Go with X" / "Do this instead" |
| 7 | Include 2+ personal observations | Third-person perspective only | First-person anecdotes, opinions, or styling takes |

---

### Phase 5: Quality Agent

**Purpose**: Achieve 95+ points through SEO optimization and multi-perspective quality checks.

**5-Agent Quality Check (95+ points required to schedule)**

- **Agent 1: Design Agent** (Visual & Format) — 20 pts
- **Agent 2: SEO Agent** (Content Quality) — 20 pts
- **Agent 3: Editor Agent** (Style & Quality) — 20 pts
- **Agent 4: Technical Expert Agent** (Accuracy) — 20 pts
- **Agent 5: Persona Agent** (Reader UX) — 20 pts

**Correction Loop**: Score < 95 → fix lowest-scoring agent's issues → re-score → loop (max 3 cycles). After 3 cycles still < 95 → report to user.

---

### Phase 6: Publishing Agent

**Purpose**: Generate featured image and inline images, then schedule on WordPress.

**Publishing Schedule**: Every **Wednesday & Saturday at 8:00 AM ET**

**Steps**:

1. **Generate Featured Image** — Photorealistic, 16:9 (Canva MCP preferred → NanoBanana → Gemini Flash)
2. **Generate H2 Inline Images** — Photorealistic, 3–5 images; skip My Favorite Shops / FAQ / The Bottom Line
3. **Markdown → HTML Conversion** — Python `markdown` library; preserve Gutenberg blocks
4. **WordPress Scheduled Post**:
   ```json
   {
     "title": "Article Title",
     "content": "HTML content",
     "status": "draft",
     "categories": [CATEGORY_IDS],
     "slug": "focus-kw-benefit-subtitle",
     "excerpt": "Meta description (under 160 chars)"
   }
   ```
5. **Rank Math SEO** — 5 focus keywords (primary + 4 LSI), meta title, meta description
6. **FAQ Schema** — FAQPage JSON-LD via Rank Math API

---

### Phase 7: Analytics Agent

**Purpose**: Register index, update spreadsheet, add internal links, generate KPI report.

**Steps**:

1. Google Indexing API — immediate index registration
2. Update all spreadsheet tabs (Dashboard, Article Log, KW Strategy, Topic Clusters, KPI Report)
3. Auto-add internal links to existing articles
4. Update `kpi_feedback.md`
5. Create Google Drive KW Research Report (DS{NNNN} format)

---

## 5. Automated Schedule

| Schedule | Run Time (ET) | Content |
| :---- | :---- | :---- |
| Wednesday Pipeline | Every Wednesday 5:00 AM | Run Phase 1–7, schedule 1 article for Wednesday 8:00 AM |
| Saturday Pipeline | Every Saturday 5:00 AM | Run Phase 1–7, schedule 1 article for Saturday 8:00 AM |
| Daily KPI Report | Every day 10:00 PM | Generate KPI report + update kpi_feedback.md |
| Weekly Optimize | Every Monday 10:15 AM | Cannibalization check, rewrite, internal link optimization, new KW suggestions |

---

## 6. WordPress Category & Tag IDs

### Category IDs

| ID | Category Name |
|----|--------------|
| 14 | Decor + Styling |
| 58 | Rooms |
| 59 | Design Essentials |
| 60 | Living Room |
| 62 | Bedroom |
| 63 | Bathroom |
| 64 | Kitchen |
| 65 | Dining Room |
| 66 | Home Office |
| 67 | Kids' Room |
| 68 | Outdoor Living |
| 70 | Color Theory |
| 71 | Trends |
| 72 | Storage + Organization |
| 73 | DIY Workshops |
| 74 | Material Selection |
| 597 | Interior Design Styles |
| 598 | Laundry Room |
| 599 | Japandi |
| 600 | Scandinavian / Nordic |
| 601 | Wabi-Sabi |
| 603 | Coastal Modern |
| 604 | Japandi Boho |
| 605 | Minimalist |
| 609 | Afro Japandi |
| 610 | Organic Modern |
| 611 | Amazon Finds |
| 635 | Gift Guides |
| 661 | Seasons |
| 662 | Spring |
| 663 | Summer |
| 665 | Fall |
| 666 | Winter |
| 667 | Seasonal Themes |
| 738 | Entryway / Mudroom |
| 739 | Small Spaces |
| 740 | Wellness Room |

### Tag IDs

| ID | Tag Name |
|----|---------|
| 679 | Living Room |
| 680 | Bedroom |
| 681 | Kitchen |
| 682 | Bathroom |
| 683 | Dining Room |
| 685 | Home Office |
| 686 | Kids' Room |
| 687 | Laundry Room |
| 688 | Outdoor / Patio / Balcony |
| 689 | Entryway / Mudroom |
| 690 | Small Spaces |
| 691 | Storage + Organization |
| 692 | Decor + Styling |
| 695 | Japandi |
| 696 | Scandinavian |
| 697 | Minimalist |
| 698 | Bohemian |
| 700 | Biophilic / Nature-inspired |
| 701 | Hygge |
| 703 | Lighting |
| 704 | Rugs |
| 709 | Trends |
| 710 | Spring Decor |
| 711 | Autumn / Fall Decor |
| 714 | Sustainable / Eco-friendly |
| 724 | Color |
| 725 | Inspiration |
| 727 | DIY / How-to |
| 728 | Amazon Finds |
| 732 | Wabi-Sabi |

---

## 7. Seasonal Advance Publishing Schedule

Create seasonal content **3 months in advance** (Christmas/Halloween: 4 months in advance).

| Current Month | Target Seasonal Content |
|--------------|------------------------|
| January | April (Spring / Easter) |
| February | May (Mother's Day) |
| March | June (Summer Kickoff) |
| April | July (Fourth of July) |
| May | August (Late Summer) |
| June | September (Fall / Halloween advance) |
| July | October (Halloween / Fall) |
| August | November (Thanksgiving) |
| September | December (Christmas / Winter) |
| October | January (New Year Refresh) |
| November | February (Valentine's Day) |
| December | March (Spring Refresh) |

---

## 8. WordPress Block Patterns (Manual Insertion by Toki)

These patterns must be inserted manually in the WordPress editor — they cannot be inserted via REST API.

| Location | Pattern Name | How to Insert |
|------|-----------|---------|
| Before Key Takeaways | Affiliate warning | Add block ▶ Browse all ▶ Patterns ▶ Posts ▶ **Affiliate warning** |
| Each READ MORE location | Read More | Add block ▶ Browse all ▶ Patterns ▶ Posts ▶ **Read More** → Open in new tab |
| After The Bottom Line | Explore More | Add block ▶ Browse all ▶ Patterns ▶ Posts ▶ **Explore More** → select category |
| My Favorite Shops section | My fav shop list | Add block ▶ Browse all ▶ Patterns ▶ Posts ▶ **My fav shop list** |

**Explore More Block settings:**
- "View All" link → Select the **same category** as the article
- Article display area → Select the **same category** as the article

---

## 9. Troubleshooting

### API 503 Error Handling
1. Do NOT immediately fall back
2. Poll every 10 minutes (max 6 times = 60 minutes)
3. After 6 consecutive 503s → record in Error Log and proceed/re-queue

### Image Generation Failure Fallback
Order: Canva MCP → NanoBanana Pro → NanoBanana Flash → Gemini Flash
If all fail: publish without image, regenerate next day

### WP Post Error Handling
- 401 Unauthorized → Regenerate Application Password
- 403 Forbidden → Check user permissions (Administrator or Editor required)
- 500 Internal Server Error → Check WP admin error log
- Category ID error → Verify via `GET /wp/v2/categories`
