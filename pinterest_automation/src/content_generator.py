import json
import anthropic
from dataclasses import dataclass
from typing import Optional


ANGLES = [
    "Problem / Solution",
    "Quick Tips",
    "Inspirational / Aspirational",
    "How-To Guide",
    "Trending / Popular",
    "Before & After",
    "Color & Material Spotlight",
    "Small Space Ideas",
    "Shopping & Styling Guide",
    "Personal Story (Toki's Voice)",
]


@dataclass
class PinContent:
    index: int
    angle: str
    title: str
    description: str


def generate_pins(
    article_title: str,
    article_excerpt: str,
    article_text: str,
    article_url: str,
    categories: list,
    count: int = 10,
    api_key: Optional[str] = None,
) -> list:
    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    categories_str = ", ".join(categories) if categories else "interior design, Japandi"
    angles_list = "\n".join(f"{i+1}. {a}" for i, a in enumerate(ANGLES[:count]))

    prompt = f"""You write Pinterest pin content for Toki's blog "Dwell Studio 24" — a Japandi & Japanese-inspired interior design blog.
Audience: women/moms 25+, middle-high income, love calm beautiful interiors.

ARTICLE:
Title: {article_title}
URL: {article_url}
Categories: {categories_str}
Excerpt: {article_excerpt}
Content: {article_text[:1800]}

Generate exactly {count} Pinterest pins. Each uses a different angle:
{angles_list}

TOKI'S VOICE:
- Warm, friendly, like texting a trusted friend
- Contractions always: you'll, it's, don't, we're
- Favorite words: cozy, bright, airy, serene, warm, natural, effortless, timeless, layered
- Short sentences, no jargon
- Suggest don't command: "you might want to", "I'd recommend", "consider"
- Light humor and personal touches welcome

CONSTRAINTS:
- Title: max 100 chars, keyword-rich, punchy
- Description: max 500 chars, end with a soft CTA ("Tap to see all the ideas!")

Return ONLY a JSON array of {count} objects:
[
  {{
    "angle": "Problem / Solution",
    "title": "...",
    "description": "..."
  }},
  ...
]
No markdown, no explanation — just the JSON array."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:-1])

    pins_data = json.loads(raw)

    return [
        PinContent(
            index=i + 1,
            angle=p.get("angle", ANGLES[i % len(ANGLES)]),
            title=p["title"][:100],
            description=p["description"][:500],
        )
        for i, p in enumerate(pins_data[:count])
    ]
