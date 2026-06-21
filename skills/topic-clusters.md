# Dwell Studio 24 — Topic Clusters スキル

Toki（Dwell Studio 24）専用のトピッククラスター記事制作スキル。
Pillar記事を軸に複数のCluster記事を作成し、内部リンクで結ぶことでトピカルオーソリティを高め、SEO効果を最大化する。

**記事品質基準はseo-blog-writerと完全に同じ。** KWリサーチ・執筆・クオリティチェック・WP公開まで、全工程を高クオリティで実行する。

---

## PART 1: トピッククラスター戦略の全体像

```
Pillar記事（例: "30 Boho Living Room Ideas"）
│  約2,700〜3,200語 / Hub & Spoke戦略の中心
│
├── Cluster記事① Content型 — 特定トピック深掘り
├── Cluster記事② Content型 — ハウツー・アイデア紹介
├── Cluster記事③ Content型 — スタイル・カラー解説
├── Cluster記事④ Shop型   — 特定カテゴリ商品紹介
└── ... （本数はPillarのテーマと依頼内容に応じて臨機応変に決定）
    各約1,400〜1,600語
```

**戦略の核心:**
- Pillarは「広く浅く」 → Clusterは「狭く深く」
- 相互リンクで検索エンジンにトピカルオーソリティを示す
- 各Clusterはそれ単体でも検索ランクイン可能な独立記事として作る

---

## PART 2: クラスター計画フェーズ

### Step 1: Cluster トピック選定

Pillarが完成・保存されたら直ちに実行する。

1. PillarのH2見出しを全て書き出す
2. 各H2を以下の2軸で評価:
   - 「独立した検索需要があるか」（そのH2が単体でGoogleで検索されるか）
   - 「記事として独立できるか」（1,500語以上の内容が作れるか）
3. 候補KWをMangools KWFinderで確認（volume ≥ 100、KD ≤ 45を目安）
4. Pinterest Trendsでトレンド方向を確認（トレンド%がプラスのKWを優先）
5. Clusterリストを確定 → 以下の一覧表に記録

**Cluster一覧表フォーマット:**

| # | Cluster KW | 月間検索数 | KD | トレンド% | タイプ | 優先度 |
|---|---|---|---|---|---|---|
| 1 | [KW] | [vol] | [kd] | [+/-X%] | Content / Shop | High / Mid |

---

### Step 2: 記事タイプの分類

Cluster記事は2種類。**本数はPillarのテーマ・依頼内容・検索需要に応じて臨機応変に決定する。**

| タイプ | 内容 | 特徴 |
|---|---|---|
| **Content型** | 特定トピックの深掘り・ハウツー・アイデア紹介・スタイル解説 | My Favorite Shopsセクションなし |
| **Shop型** | 特定カテゴリの商品を徹底紹介（例: "10 Best Japandi Rugs"） | My Favorite Shopsセクションあり |

**Shop型を選ぶ基準:**
- 商業的な検索意図が明確（"best ___", "buy ___", "top ___ to buy"）
- Pillar内で商品リンクが最小限だったH2トピック
- アフィリエイト収益化の可能性が高いカテゴリ

**Content型を選ぶ基準:**
- 検索意図が「知りたい・学びたい」（informational intent）
- "how to", "ideas", "tips", "guide", "what is" 系クエリ
- Pillar内で解説が浅かったH2トピックを深掘りする記事

---

### Step 3: 内部リンク設計（必須）

Pillar ↔ Cluster の相互リンクを必ず設定する。

**Cluster → Pillar（必須・各Clusterに最低1本）:**
```html
<!-- wp:paragraph -->
<p>📖 <strong>Read more:</strong> <a href="https://dwellstudio24.com/[pillar-slug]" target="_blank" rel="noopener noreferrer">[Pillar Article Title]</a></p>
<!-- /wp:paragraph -->
```

**Pillar → Cluster（Cluster保存後にREST APIで追記）:**
Pillarの該当H2セクション内に各ClusterへのREAD MOREを追記する。
→ Cluster記事が下書き保存されたら、PillarのWP投稿をREST APIで更新してリンクを追加。

**Cluster ↔ Cluster（テーマが近い場合）:**
関連するCluster同士も1〜2本リンクで結ぶ。アンカーテキストは自然な文脈の中に。

---

### ⚠️ READ MORE リンク 厳格ルール（最重要）

**使用できるURLは以下の3種類のみ。それ以外は絶対に使わない。**

| 優先順 | 使用可能なリンク | 確認方法 |
|---|---|---|
| 1 | **今回のPillar記事** | ユーザーから提供されたURL or WP REST APIで取得したslug |
| 2 | **同じCluster内で今回作成・保存済みの他のCluster記事** | WP保存後に取得したPost ID + slug |
| 3 | **実在するDwell Studio 24の既存記事** | WP REST APIで検索して実在確認済みのもののみ |

**❌ 絶対禁止:**
- 架空のタイトル・URLを作って使う（存在しない記事へのリンク）
- 「後で確認する」「プレースホルダー」として仮のURLを入れる
- URLを推測・生成する（例: `/japandi-bedroom-ideas/` など確認していないslug）

**✅ URLが確認できない場合の対処:**
- READ MORE をそのセクションでは省略する
- Pillar記事へのリンク1本のみに絞る
- 後から追加できるようにコメントアウトで残す（`<!-- READ MORE: [記事名] - URL確認後に追加 -->`）

**実装タイミング:**
- Cluster 1記事目: READ MORE = Pillarのみ（他のClusterはまだ保存前のため使えない）
- Cluster 2記事目以降: READ MORE = Pillar + 保存済みCluster記事のみ
- 全Cluster完成後: 必要に応じてREST APIで各記事を更新してリンクを追加

---

## PART 3: Cluster記事の執筆

> **品質基準:** seo-blog-writerと完全に同じ。KWリサーチ・Brand Voice・AI感排除・5エージェント品質チェック（95点以上）・WP公開設定、全て同一基準で実行する。

---

### 3.1 ブランドボイス（seo-blog-writerと同一）

「TokiがDwell Studio 24の読者に親友へのテキストを送るように書く」が基本姿勢。

#### Tone Pillars

| Pillar | What It Means in Practice |
|---|---|
| **Friendly & Warm** | Write like you're texting a friend who trusts your design advice |
| **Casual Yet Polished** | Conversational flow, but grammatically clean and thoughtful |
| **Encouraging & Helpful** | Make the reader feel "I can do this!" — never overwhelm |
| **Slightly Playful** | Light humor and personal anecdotes are welcome and encouraged |
| **Personal Touch** | Include Toki's perspective ("I always use this trick in my own space") |

#### Voice Sentence Examples
- ✅ "I know picking the right rug can feel overwhelming, but don't worry — we'll tackle it together!"
- ✅ "A few simple tweaks can really transform a room — trust me, it's easier than it looks."
- ✅ "If you're wondering about lighting, here's a little trick I always use in my own space."
- ✅ "You'll love how this little change brightens your space!"
- ✅ "I just imagine all the grease, hair, and dust getting stuck in those grooves!" ← personal, relatable humor

#### Words & Phrases to AVOID
- ❌ Unexplained technical jargon
- ❌ Harsh imperatives ("Do this now!", "You must...")
- ❌ Overly casual slang ("lit," "OMG," "slay")
- ❌ "This allows..." / "This enables..." — delete entirely
- ❌ "I would recommend considering..." → replace with "Try..." / "Go for..."
- ❌ Overly long paragraphs

#### Syntax & Pacing Rules
- Paragraphs: **under 300 characters / ~50 words** (mobile-first!)
- Use contractions: "you'll," "it's," "don't," "we're"
- Toki's first-person observation/experience: **2箇所以上必須**

---

### 3.2 KWリサーチ（必須）

各Cluster記事のKW選定は必ずMangools + Pinterest Trendsで裏付けを取る。

#### 🔍 Mangools KWFinder ブラウザリサーチ

`app.mangools.com/kwfinder` をChromeで開き、Focus Keywordを検索して以下を収集:

1. **Related Keywords タブ**: 関連KW・月間検索数・KD・トレンド%を確認
2. **Autocomplete Keywords タブ**: サジェスト系ロングテールKWを収集（H2/H3・タグ候補）
3. **SERP Overview**: 検索上位10記事のDA/PA/LPS/EVを確認

**📈 トレンド%ルール（最重要）:**
- **%がプラス（↑）のKWを最優先で選ぶ**（例: `+45%` > `+12%`）
- プラスのKWが見つからない場合のみ、マイナスKWを使用

#### 🌸 Pinterest Trendsリサーチ

`trends.pinterest.com` でFocus Keywordを検索:
- トレンドの上昇・下降グラフを確認（季節性・ピーク月を把握）
- 関連トレンドワードを収集（H2・タグ・LSIキーワードに活用）
- ブロックされる場合: WebSearchで `"pinterest trends [keyword] 2026"` を検索

**Keyword Table:**

| Type | Keyword | Intent | Notes（トレンド%） |
|---|---|---|---|
| Primary | [focus keyword] | Informational | Title + first sentence |
| Long-tail | [variation] | Navigational | H2/H3に使用 |
| LSI | [related term] | Supportive | 本文に自然に散りばめる |

**Keyword Density Target:** Focus + Secondary 5つ合計で **1.0–2.0%**

---

### 3.3 Content型 Cluster 記事構成（約1,400〜1,600語）

```
① Intro（2段落、dropCap必須）
   - Para 1: Focus Keywordを1行目に含める（疑問文禁止）
   - Para 2: この記事で何が得られるか

② Key Takeaways（H3タグ、4〜5 bullets）

③ YouTube Embed（Key Takeaways直後）

④〜⑧ H2セクション（4〜6個）
   各H2のパターン:
   └─ [IMAGE: 16:9ヒーロー画像 — Leonardo AI生成・PART 8参照]  ← H2直後・本文前
   └─ H3: 2個/H2（各≤350文字）
        └─ [IMAGE BLOCK: 9:16×2枚 columnsブロック — PART 8参照]  ← H3本文直後
   └─ READ MORE: Pillar記事へのリンクを最低1本（Step 3の厳格ルール参照 — 架空URL禁止）
   └─ My Top Tip: 🌿 1〜2箇所

⑨ FAQ（H2、5〜6問・短め・実際にGoogleで検索されるクエリ）
   ⚠️ FAQ内のH3には画像を挿入しない

⑩ The Bottom Line（H2、2段落 + Tag me CTA）
   ⚠️ The Bottom LineのH2には16:9画像を挿入しない
```

**省略するセクション（語数を1,500語に抑えるため）:**
- My Favorite Shops → なし（商品リンクはH2本文内に自然に1〜2個のみ）
- Ideas For Small [Room] → なし
- Live the [Topic] Lifestyle → なし（lifestyle特化記事のみ任意で追加）

---

### 3.4 Shop型 Cluster 記事構成（約1,400〜1,600語）

```
① Intro（2段落、dropCap必須）
   - Para 1: Focus Keywordを1行目に / "Here are my top picks" スタイル
   - Para 2: なぜこの商品カテゴリを選ぶのか・Tokiの視点

② Key Takeaways（H3タグ、4〜5 bullets）

③ YouTube Embed（Key Takeaways直後）

④〜⑧ H2セクション（商品カテゴリ or 個別商品の深掘り）
   各H2のパターン:
   └─ [IMAGE: 16:9ヒーロー画像 — Leonardo AI生成・PART 8参照]  ← H2直後・本文前
   └─ H3: 商品名 or 商品特徴
        - 具体的な商品名・素材・サイズ・価格帯
        - なぜTokiがこれを選んだか（EEAT: 一人称の視点）
        - **[商品名](URL)** でBold+リンク（WebSearchで実在URLを必ず取得・在庫確認必須）
        - My Top Tip: "I love pairing this with..."
        └─ [IMAGE BLOCK: 9:16×2枚 columnsブロック — PART 8参照]  ← H3本文直後
   └─ READ MORE: Pillar記事へのリンクを最低1本（Step 3の厳格ルール参照 — 架空URL禁止）

⑨ My Favorite Shops（H2）
   ← Joss & Main / 2Modern / AllModern の3店舗
   ← seo-blog-writerのMy Favorite Shops形式と同一（Toki's handpick voice）
   ← 商品は実在・在庫確認済みのもののみ使用
   ⚠️ My Favorite ShopsのH2には16:9画像を挿入しない

⑩ FAQ（H2、5〜6問）
   ⚠️ FAQ内のH3には画像を挿入しない

⑪ The Bottom Line（H2、2段落 + Tag me CTA）
   ⚠️ The Bottom LineのH2には16:9画像を挿入しない
```

---

### 3.5 My Favorite Shops — 執筆ルール（Shop型のみ）

seo-blog-writerと完全に同じルールを適用する。

- **H3はなし**。H2直下に intro line → "My Handpicked Selections" H3 → 各店舗パラグラフ
- 各店舗: 2〜3文 + **2〜3個のインラインリンク**（商品名をアンカーテキストにする）
- 必ず実在・在庫確認済みの商品URLを使用。WebSearchで商品PDPを確認すること
- 2Modernの在庫確認はWebFetchでは誤判定が出るためChromeブラウザで必ず確認する
- アフィリエイト免責事項を My Favorite Shops セクションの直前に入れる

**ボイステンプレート（各店舗）:**
```
[Store name] is [personal reason Toki loves it — honest, specific].
Their **[Specific Product Name](URL)** [what makes it special — material, shape, feel].
I'd also grab their **[Second Product Name](URL)** [brief personal take].
```

**Default stores（家具・インテリア記事）:**

| Store | Tagline |
|---|---|
| **Joss & Main** | Trending Furniture, Decor, Premium Quality |
| **2Modern** | Japandi-Style Furniture, Decor |
| **AllModern** | Simple and Modern Furniture, Decor |

---

### 3.6 AI感排除チェック（7項目・全記事必須）

| # | NG | OK |
|---|----|----|
| 1 | "It can sometimes depend..." | 具体的シナリオを明示 |
| 2 | "It's important to..." × 4回以上 | 3回まで・代わりに具体的アクション |
| 3 | 全段落が同じ文末パターン | バリエーションをつける |
| 4 | 箇条書き3連続 | 間にリード文やテーブルを挟む |
| 5 | "This allows..." / "This enables..." | 完全削除 |
| 6 | "I would recommend considering..." | "Try..." / "Go for..." |
| 7 | 第三者視点のみ | Toki's一人称体験談を2箇所以上 |

---

### 3.7 品質チェック — 5エージェント採点（95点以上が公開条件）

5エージェント並列採点（各20点満点、合計100点）:

**Agent 1: Design Agent (Visual & Format) [20 pts]**
- H2 structure matches TOC; each H2 opens with 1-sentence conclusion (2pts)
- Tables have consistent header and style (2pts)
- CTA placed at minimum 2 locations (2pts)
- Bold emphasis (`<strong>`) in 12–18 spots — core phrases, numbers, actions only (2pts)
- Paragraphs under 300 characters for mobile readability (2pts)
- Bullet lists have lead sentences before and after (2pts)
- All images have descriptive alt text (2pts)
- Consistent formatting throughout entire article (2pts)
- Short sentence patterns varied throughout (2pts)
- H2/H3 headings are descriptive and scannable (2pts)

**Agent 2: SEO Agent (Content Quality) [20 pts]**
- Title includes focus keyword naturally, under 75 characters (2pts)
- Meta description under 160 characters, addresses search intent (2pts)
- Body text 1,400+ words (2pts)
- Each H2 opens with a 1-sentence GEO-ready conclusion (2pts)
- 1–2 external links to authoritative US sources naturally woven in (2pts)
- E-E-A-T elements present (author credentials, data, firsthand insight) (2pts)
- FAQ section has 5+ questions (2pts)
- Minimum 1 internal link to Pillar post (+ links to other cluster articles if applicable) (2pts)
- Article structure matches search intent for the target KW (2pts)
- 2+ unique facts or original insights not found in competing articles (2pts)

**Agent 3: Editor Agent (Style & Brand Voice) [20 pts]**
- All 7 AI-feel elimination checks passed (2pts)
- American English tone throughout — warm, friendly, casual (2pts)
- Opening paragraph is 2–3 concise, engaging sentences (2pts)
- 2+ first-person observations, personal styling takes, or anecdotes (2pts)
- Interior design terms explained in plain English on first use (2pts)
- Sentences under 50 words; paragraphs under 300 characters (2pts)
- Sentence patterns and endings are varied — not repetitive (2pts)
- 2–3 short punchy one-liners or sentence fragments used for emphasis (2pts)
- "Key Takeaways" box appears at the top of the article (2pts)
- No "Welcome to..." opener in listicle/guide format (2pts)

**Agent 4: Technical Expert Agent (Interior Design Accuracy) [20 pts]**
- Product, material, or tool descriptions are accurate and current (2pts)
- DIY, styling, or decorating tips are actionable and reproducible (2pts)
- Step-by-step instructions clear enough for a non-expert homeowner (2pts)
- Technical interior design concepts explained in accessible language (2pts)
- Prices, dimensions, or product specs are specific and credible (2pts)
- Comparison information is accurate (price, style, material, availability) (2pts)
- All product links verified as real, in-stock items (2pts)
- "What to do next" or "Try this" actions are specific and doable (2pts)
- Content is consistent with current interior design trends (2pts)
- Use cases are concrete (who benefits, which room, what situation) (2pts)

**Agent 5: Persona Agent (Reader UX) [20 pts]**

Persona: Interior-loving women 25+, moms, middle-to-upper income, homemakers — reading on mobile

- The opening makes her feel "this article was written for me" (2pts)
- Interior design terms explained in approachable, non-intimidating language (2pts)
- Each H2 conclusion lets her instantly grasp the value without reading everything (2pts)
- Examples and styling ideas feel "I could actually do this in my home" (2pts)
- "Where to start" is crystal clear — no overwhelm, just clear first steps (2pts)
- Paragraphs are 3–4 sentences max — easy to skim between school pickups (2pts)
- Tables make complete sense on their own without surrounding explanation (2pts)
- FAQs match real questions she'd Google at 10pm after putting the kids to bed (2pts)
- CTA feels natural and helpful — not salesy or pushy (2pts)
- After reading, she knows exactly what to shop, do, or try next (2pts)

**修正ループ:** 95点未満 → 低スコアエージェントの指摘を優先修正 → 再採点（最大3サイクル） → 3サイクル後も未満はユーザー報告

---

## PART 4: Cluster記事のSEO・フォーマット設定

Pillar記事との差分のみ記載。それ以外はseo-blog-writerと同一ルールを適用する。

| 項目 | Pillar（seo-blog-writer） | Cluster（このスキル） |
|---|---|---|
| 語数 | 2,700〜3,200語 | 1,400〜1,600語 |
| My Top Tip | 3箇所 | 1〜2箇所 |
| External links | 2〜3本 | 1〜2本 |
| FAQ | 6〜8問 | 5〜6問 |
| My Favorite Shops | 必須 | Content型: なし / Shop型: あり |
| Ideas For Small [Room] | room記事のみ | なし |
| Live the [Topic] Lifestyle | lifestyle記事のみ | lifestyle特化記事のみ任意 |
| Intro段落数 | 3段落 | 2段落 |
| Key Takeaways bullets | 5〜6個 | 4〜5個 |

---

## PART 5: WordPress 公開設定

記事作成後、以下をWordPress REST APIで全て設定してから下書き保存する。

### 5.1 WordPress下書き保存

```python
import requests
from base64 import b64encode

WP_URL = "https://dwellstudio24.com"
# 認証情報は.envから読み込む

data = {
    "title": "Article Title",
    "content": "Gutenberg HTML content",
    "status": "draft",          # 必ずdraft（publishやfutureにしない）
    "categories": [ID1, ID2],
    "tags": [ID1, ID2],
    "slug": "focus-keyword-subtitle",  # max 75文字
}
```

**slug ルール:**
- Focus Keywordを含む英語スラッグ
- 最大75文字
- 例: `japandi-console-table-entryway-ideas` (37字)

### 5.2 Rank Math SEO設定（保存後に実行）

```python
rankmath_data = {
    "objectID": POST_ID,
    "objectType": "post",
    "meta": {
        "rank_math_focus_keyword": "primary kw,secondary kw 1,secondary kw 2,secondary kw 3,secondary kw 4",
        "rank_math_title": "%title% %sep% %sitename%",
        "rank_math_description": "Meta description (160 chars max)",
        "rank_math_robots": ["index", "follow"]
    }
}
# POST to /wp-json/rankmath/v1/updateMeta
```

**`rank_math_focus_keyword` は必ず5つ**カンマ区切り（primary + 4 LSI/secondary）
**`rank_math_title` は必ず `%title% %sep% %sitename%` を使用**

### 5.3 Content Format Requirements（記事HTML内）

| 項目 | 設定値 |
|------|--------|
| 最初の段落 | `<!-- wp:paragraph {"dropCap":true} -->` |
| Key Takeaways | H3タグ（H2にしない） |
| YouTube embed | Key Takeaways直後に1本 |
| READ MORE | Pillar記事 / 保存済みCluster記事 / 実在確認済み記事のみ（架空URL・プレースホルダー完全禁止） |
| Shopアイテムリンク | `<strong><a href="URL">Product Name</a></strong>` |

### 5.4 Dwell Studio 24 カテゴリIDリスト

| ID | カテゴリ名 |
|----|----------|
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

### 5.5 Dwell Studio 24 タグIDリスト

| ID | タグ名 |
|----|-------|
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
| 694 | Outdoor / Alfresco |
| 695 | Japandi |
| 696 | Scandinavian |
| 697 | Minimalist |
| 698 | Bohemian |
| 699 | Maximalist |
| 700 | Biophilic / Nature-inspired |
| 701 | Hygge |
| 702 | Villa Interior |
| 703 | Lighting |
| 704 | Rugs |
| 705 | Shelving |
| 706 | Terrazzo |
| 707 | Pantry |
| 708 | Coffee Bar |
| 709 | Trends |
| 710 | Spring Decor |
| 711 | Autumn / Fall Decor |
| 713 | Holiday |
| 714 | Sustainable / Eco-friendly |
| 715 | Healing Space |
| 716 | Apartment |
| 717 | Family Living |
| 718 | Kid Friendly |
| 719 | Resources |
| 720 | Reading Nook |
| 721 | Nursery |
| 722 | Summer Decor |
| 723 | Winter Decor |
| 724 | Color |
| 725 | Inspiration |
| 727 | DIY / How-to |
| 728 | Amazon Finds |
| 729 | Nordic |
| 732 | Wabi-Sabi |
| 734 | Seasonal Theme |
| 735 | Gift Guides |

---

## PART 6: 量産フロー（全体の流れ）

```
① Pillar記事を完成・WP下書き保存
② PillarのH2を全て書き出す（5〜10分）
③ 各H2を「検索需要あり・独立記事にできる」で評価
④ Mangools + Pinterest TrendsでKW確認・優先度決め（20〜30分）
⑤ Cluster一覧表を作成（KW・タイプ・優先度まで）
⑥ Content型から先に執筆 → Shop型を後（商品調査に時間がかかるため）
⑦ 各Cluster: KWリサーチ → 執筆 → 5エージェント品質チェック → WP保存
⑧ 全Cluster保存後、PillarにREAD MOREリンクを追記（REST API経由）
⑨ Cluster同士に関連リンクを追加（テーマが近いもの同士）
```

**執筆優先順:**
1. High優先度 + トレンド%プラス のClusterから着手
2. Content型を先に消化（執筆が速い）
3. Shop型は商品リサーチに時間を確保してから着手

---

## PART 7: Quick Reference

| 項目 | 設定値 |
|---|---|
| Cluster語数 | 1,400〜1,600語 |
| 品質基準 | 95点以上（5エージェント採点） |
| KW密度 | 1.0–2.0%（Focus + Secondary 5つ合計） |
| 内部リンク | Pillar→Cluster / Cluster→Pillar（必須）|
| My Favorite Shops | Shop型のみ |
| 画像 | Leonardo AI MCPで自動生成・WPメディア経由（PART 8参照） |
| WP保存ステータス | `"draft"` のみ（公開はTokiが手動） |
| Rank Math KW | 5つカンマ区切り（必須） |
| dropCap | 最初の `<!-- wp:paragraph -->` に `{"dropCap":true}` |
| YouTube embed | Key Takeaways直後に必ず1本 |

---

## PART 8: IMAGE GENERATION WITH LEONARDO AI

seo-blog-writerのPART 8と完全に同じルールを適用する。
Cluster記事での省略対象セクションは以下の通り。

### Cluster記事での画像挿入ルール

| セクション | 枚数 | サイズ | 配置 | 省略 |
|---|---|---|---|---|
| 各H2直後 | 1枚 | 16:9（1344×768px） | H2見出し直後・本文前 | My Favorite Shops（Shop型のみ）/ The Bottom Line |
| 各H3直後 | 2枚 | 9:16（768×1344px） | H3本文直後 | FAQセクション内の全H3 |

### プロンプト・生成・WPアップロード・ブロック挿入

→ **seo-blog-writerのPART 8（Step 1〜Step 4）をそのまま適用する。**

モデル・品質・サイズ設定も同一:
- Model: GPT Image 2
- Quality: low
- 16:9サイズ: width=1344, height=768
- 9:16サイズ: width=768, height=1344

### 実行タイミング（Cluster記事）

```
3.3/3.4 記事執筆完了
  ↓
PART 8 画像生成（seo-blog-writer PART 8 Step 1〜4と同手順）
  ↓
PART 5 WordPress保存（下書き）
```
