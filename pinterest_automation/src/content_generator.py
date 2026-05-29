"""
Template-based pin content generator — no API key required.
Extracts topic keywords from the article title and fills 10 angle templates.
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class PinContent:
    index: int
    angle: str
    title: str
    description: str


# ── 10 pin angle templates ────────────────────────────────────────────────────
# Placeholders:
#   {topic}   → full topic phrase  e.g. "Japandi Dining Room"
#   {room}    → room name only     e.g. "dining room"
#   {style}   → design style       e.g. "Japandi"
#   {url_hint}→ short article hint (not used in text, for reference)

TEMPLATES = [
    {
        "angle": "Problem / Solution",
        "title": "{topic} Ideas: Finally Create the Calm Space You've Been Dreaming Of",
        "description": (
            "Does your {room} feel cluttered, cold, or just… off? "
            "You're not alone — and the good news is, it doesn't take a full renovation to fix it. "
            "A {style} approach gives you that warm, serene vibe with simple, intentional choices. "
            "Tap to see all the ideas!"
        ),
    },
    {
        "angle": "Quick Tips",
        "title": "Simple {topic} Tips That Actually Work (Even for Beginners!)",
        "description": (
            "You don't need a big budget or a design degree to get that effortless {style} look. "
            "A few small tweaks — the right textures, a neutral palette, natural wood — "
            "can totally transform your {room}. "
            "Save this for your next refresh!"
        ),
    },
    {
        "angle": "Inspirational / Aspirational",
        "title": "Stunning {topic} Inspo: Create Your Most Serene Space Yet",
        "description": (
            "Imagine walking into a {room} that feels like a breath of fresh air — "
            "warm, airy, and beautifully put together. "
            "That's the magic of {style} design. "
            "Natural materials, clean lines, cozy layers. "
            "Tap to get inspired!"
        ),
    },
    {
        "angle": "How-To Guide",
        "title": "How to Design a {topic}: Your Step-by-Step Guide",
        "description": (
            "Not sure where to start with your {room} makeover? I've got you! "
            "From choosing the right color palette to picking furniture that lasts, "
            "this guide walks you through everything. "
            "It's easier than it looks — promise. Tap to read!"
        ),
    },
    {
        "angle": "Trending / Popular",
        "title": "{topic}: The Design Trend Everyone's Obsessed With Right Now",
        "description": (
            "There's a reason {style} is everywhere right now — it just works. "
            "Timeless, calm, and effortlessly chic, a {style} {room} never goes out of style. "
            "Whether you're starting from scratch or just refreshing a few pieces, "
            "this is the inspo you need. Tap to explore!"
        ),
    },
    {
        "angle": "Before & After",
        "title": "Transform Your {room} with These {topic} Ideas",
        "description": (
            "You'd be surprised what a few intentional changes can do to a {room}. "
            "Swap out heavy drapes for linen, add a natural wood accent, "
            "and suddenly your space feels twice as big and ten times more inviting. "
            "See how it's done — tap to get the ideas!"
        ),
    },
    {
        "angle": "Color & Material Spotlight",
        "title": "{topic}: The Perfect Neutral Palette for a Warm, Inviting Space",
        "description": (
            "Color can make or break a {room} — and in {style} design, "
            "it's all about warm neutrals, natural wood tones, and earthy textures. "
            "Think soft beige, warm white, and muted sage. "
            "So grounding, so beautiful. Tap to see the full palette guide!"
        ),
    },
    {
        "angle": "Small Space Ideas",
        "title": "Small {room}? No Problem — These {topic} Ideas Still Work",
        "description": (
            "Living with a tiny {room} doesn't mean giving up on style. "
            "{style} design is actually perfect for smaller spaces — "
            "less clutter, smarter furniture, and a lighter color palette "
            "make every square foot count. Tap for ideas that actually fit!"
        ),
    },
    {
        "angle": "Shopping & Styling Guide",
        "title": "The Best Pieces for a Beautiful {topic} (On Any Budget)",
        "description": (
            "You don't have to splurge to get that curated {style} look. "
            "I've rounded up the best {room} pieces — from affordable finds to splurge-worthy gems — "
            "that nail that warm, natural, effortless vibe. "
            "Tap to shop the look!"
        ),
    },
    {
        "angle": "Personal Story (Toki's Voice)",
        "title": "What I Learned Designing My Own {topic} (And What I'd Do Differently)",
        "description": (
            "Honest talk — getting my {room} to feel the way I wanted took a few tries. "
            "But the {style} principles I landed on? Game changer. "
            "I'm sharing everything I learned so you don't have to figure it out the hard way. "
            "Tap to read my story!"
        ),
    },
]


# ── Keyword extraction ────────────────────────────────────────────────────────

STYLE_KEYWORDS = [
    "japandi", "minimalist", "scandinavian", "nordic", "wabi-sabi",
    "organic modern", "coastal modern", "boho", "japandi boho",
]

ROOM_KEYWORDS = [
    "living room", "bedroom", "kitchen", "bathroom", "dining room",
    "home office", "entryway", "mudroom", "laundry room", "outdoor",
    "kids room", "nursery", "playroom",
]


_TRAILING_NOISE = re.compile(
    r'\s+(ideas|tips|guide|inspiration|inspo|decor|design|look|style|'
    r'roundup|list|picks|examples|photos|pictures)\s*$',
    re.IGNORECASE,
)


def _extract_topic_parts(article_title: str, categories: list) -> tuple:
    """Return (topic, room, style) extracted from title and categories."""
    text = article_title.lower()

    # Detect style
    style = "Japandi"  # default for Dwell Studio 24
    for kw in STYLE_KEYWORDS:
        if kw in text or any(kw in c.lower() for c in categories):
            style = kw.title()
            break

    # Detect room
    room = "space"
    for kw in ROOM_KEYWORDS:
        if kw in text or any(kw in c.lower() for c in categories):
            room = kw.title()
            break

    # Build topic — strip listicle numbers ("10 Japandi..." → "Japandi...")
    topic = re.sub(r'^\d+\s+', '', article_title)
    # Strip subtitle after colon
    topic = topic.split(':')[0].strip()
    # Strip trailing noise words ("Ideas", "Tips", "Guide", etc.)
    topic = _TRAILING_NOISE.sub('', topic).strip()
    # Trim to reasonable length
    if len(topic) > 50:
        topic = topic[:50].rsplit(' ', 1)[0]

    return topic, room, style


def generate_pins(
    article_title: str,
    article_excerpt: str,
    article_text: str,
    article_url: str,
    categories: list,
    count: int = 10,
    api_key: Optional[str] = None,   # kept for API compatibility, not used
) -> list:
    """Generate pin content using templates — no AI API required."""

    topic, room, style = _extract_topic_parts(article_title, categories)

    pins = []
    for i, tmpl in enumerate(TEMPLATES[:count]):
        def fill(text: str) -> str:
            return (
                text
                .replace("{topic}", topic)
                .replace("{room}", room)
                .replace("{style}", style)
            )

        pins.append(PinContent(
            index=i + 1,
            angle=tmpl["angle"],
            title=fill(tmpl["title"])[:100],
            description=fill(tmpl["description"])[:500],
        ))

    return pins
