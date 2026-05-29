"""
Pinterest pin content generator — fully compliant with pinterestagent.md spec.

Flow:
  4 Main KWs × 5 angle templates = 20 pins
  Each pin: Main KW in title+desc, Core KW in title or desc,
            Hidden KWs (secondary/contextual/qualifier) in desc only.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PinContent:
    index: int
    angle: str
    main_kw: str
    title: str
    description: str
    label: str        # small top label on the image
    subtitle: str     # supporting line on the image
    style: str        # "A" or "B" (layout style)


# ── 5 angle templates ─────────────────────────────────────────────────────────
# Placeholders:
#   {main_kw}     → Pinterest Trends main keyword
#   {core_kw}     → Pinterest Trends core/secondary keyword
#   {sec_kw}      → Hidden keyword (secondary/style genre)
#   {ctx_kw}      → Hidden keyword (material/method)
#   {qual_kw}     → Hidden keyword (size/budget/qualifier)

ANGLES = [
    # ① Emotional / Atmosphere
    {
        "name": "Emotional",
        "title_templates": [
            "{main_kw}: Create a Space That Feels Like a Calm Retreat",
            "The {main_kw} Look That Makes You Never Want to Leave",
            "Transform Your Home with These {core_kw} Vibes",
        ],
        "desc_template": (
            "There's something about a beautifully designed {main_kw} that just makes you breathe a little easier. 🌿 "
            "That effortless {sec_kw} feeling — {ctx_kw}, warm layered textures, and intentional calm — "
            "is everything. Whether your space is {qual_kw} or larger, this vibe is completely achievable. "
            "Save this for your next refresh!"
        ),
        "label": "INSPIRATIONS",
        "style": "A",
    },
    # ② How-To / Practical
    {
        "name": "How-To",
        "title_templates": [
            "How to Get the {main_kw} Look — Step by Step",
            "Easy {main_kw} Ideas That Actually Work",
            "Simple Steps to a Stunning {core_kw} Space",
        ],
        "desc_template": (
            "Wondering how to pull off the perfect {main_kw}? Here's exactly what to do. ✨ "
            "Start with {ctx_kw} as your base, layer in {sec_kw} pieces, "
            "and keep it {qual_kw}-friendly by editing ruthlessly. "
            "It's more effortless than it looks — I promise. Tap to get the full guide!"
        ),
        "label": "HOW TO",
        "style": "B",
    },
    # ③ Inspiration / Aspirational
    {
        "name": "Inspiration",
        "title_templates": [
            "Stunning {main_kw} Ideas You Need to Try",
            "{main_kw} Inspo: Beautiful Looks for Every Home",
            "The Ultimate {core_kw} Inspiration Round-Up",
        ],
        "desc_template": (
            "Looking for {main_kw} inspiration that actually feels achievable? You found it. 🏡 "
            "These serene, grounded spaces blend {sec_kw} style with {ctx_kw} for a look "
            "that's timeless and effortlessly chic — no matter your budget or how {qual_kw} your space is. "
            "Tap to explore all the ideas!"
        ),
        "label": "INSPIRATIONS",
        "style": "B",
    },
    # ④ Secret / Insight
    {
        "name": "Insight",
        "title_templates": [
            "The {main_kw} Secret Most Designers Won't Tell You",
            "What Makes a {main_kw} Actually Work (It's Not What You Think)",
            "Transform Your Space with This {core_kw} Design Secret",
        ],
        "desc_template": (
            "Here's what separates a good {main_kw} from a great one: it's all about intentionality. "
            "The right {ctx_kw}, a {sec_kw} foundation, and editing your space down to only what you love. "
            "Even {qual_kw} spaces can feel like a sanctuary when you get this right. "
            "Save this — you'll want to come back to it! ✨"
        ),
        "label": "DESIGN TIPS",
        "style": "A",
    },
    # ⑤ Inclusive / Universal
    {
        "name": "Universal",
        "title_templates": [
            "{main_kw} Ideas That Work for Every Home Style",
            "Beautiful {main_kw} — No Matter Your Budget",
            "{core_kw} Looks for Every Space, Every Style",
        ],
        "desc_template": (
            "You don't need a massive budget or a perfectly curated home to nail the {main_kw} look. 🤍 "
            "With a few intentional {ctx_kw} choices and a nod to {sec_kw} design principles, "
            "any space — even a {qual_kw} one — can feel warm, airy, and beautifully grounded. "
            "Tap to find the ideas that fit YOUR home!"
        ),
        "label": "FOR EVERY HOME",
        "style": "A",
    },
]


# ── Keyword parser ────────────────────────────────────────────────────────────

def parse_other_kws(other_kws: list) -> dict:
    """
    Auto-assign other_kws to roles.
    User can tag with [secondary], [contextual], [qualifier] prefixes,
    or the first 3 are assigned in order.
    """
    sec, ctx, qual = [], [], []

    for kw in other_kws:
        kw = kw.strip()
        kl = kw.lower()
        if kl.startswith("[secondary]"):
            sec.append(kl.replace("[secondary]", "").strip())
        elif kl.startswith("[contextual]"):
            ctx.append(kl.replace("[contextual]", "").strip())
        elif kl.startswith("[qualifier]"):
            qual.append(kl.replace("[qualifier]", "").strip())
        elif kl.startswith("[core]"):
            pass  # handled separately
        else:
            # Auto-assign by position
            if len(sec) == 0:
                sec.append(kw)
            elif len(ctx) == 0:
                ctx.append(kw)
            elif len(qual) == 0:
                qual.append(kw)
            else:
                sec.append(kw)  # extra → secondary pool

    return {
        "secondary": sec,
        "contextual": ctx,
        "qualifier":  qual,
    }


def _pick(lst: list, i: int, fallback: str) -> str:
    if not lst:
        return fallback
    return lst[i % len(lst)]


# ── Main generator ─────────────────────────────────────────────────────────────

def generate_pins(
    article_title: str,
    article_excerpt: str,
    article_text: str,
    article_url: str,
    categories: list,
    count: int = 10,
    # Extended keyword params
    main_kws: Optional[list] = None,
    core_kw: Optional[str] = None,
    other_kws: Optional[list] = None,
    api_key: Optional[str] = None,   # kept for compatibility, not used
) -> list:
    """
    Generate pins per pinterestagent.md spec.
    If main_kws provided: 4 KWs × 5 angles = 20 pins.
    Else: fall back to template mode using article title.
    """
    if main_kws:
        return _generate_from_keywords(main_kws, core_kw or "", other_kws or [])

    # ── Template fallback (no KWs provided) ──────────────────────────────────
    topic, room, style = _extract_topic(article_title, categories)
    # Build synthetic KW inputs
    synthetic_main = [topic]
    synthetic_core = f"{style} {room}" if room != "space" else style
    synthetic_other = [style, room, "neutral palette", "small space"]
    return _generate_from_keywords(
        synthetic_main, synthetic_core, synthetic_other,
        max_pins=min(count, 5)
    )


def _generate_from_keywords(
    main_kws: list,
    core_kw: str,
    other_kws: list,
    max_pins: int = None,
) -> list:
    parsed = parse_other_kws(other_kws)
    pins = []
    global_idx = 1

    for ki, main_kw in enumerate(main_kws):
        for ai, angle in enumerate(ANGLES):
            if max_pins and global_idx > max_pins:
                break

            sec = _pick(parsed["secondary"], ki + ai, "minimalist")
            ctx = _pick(parsed["contextual"], ki + ai, "natural wood tones")
            qual = _pick(parsed["qualifier"],  ki + ai, "small space")

            title_tmpl = angle["title_templates"][ai % len(angle["title_templates"])]

            title = title_tmpl.format(
                main_kw=main_kw.title(),
                core_kw=core_kw.title() if core_kw else main_kw.title(),
            )[:100]

            desc = angle["desc_template"].format(
                main_kw=main_kw,
                core_kw=core_kw or main_kw,
                sec_kw=sec,
                ctx_kw=ctx,
                qual_kw=qual,
            )[:500]

            # Image design text
            label = angle["label"]
            # Subtitle = core_kw or condensed from title
            subtitle_base = core_kw or sec or main_kw
            subtitle = subtitle_base.upper() if subtitle_base else ""

            pins.append(PinContent(
                index=global_idx,
                angle=angle["name"],
                main_kw=main_kw,
                title=title,
                description=desc,
                label=label,
                subtitle=subtitle,
                style=angle["style"],
            ))
            global_idx += 1

        if max_pins and global_idx > max_pins:
            break

    return pins


# ── Fallback topic extraction (no KWs mode) ───────────────────────────────────

import re

_STYLE_KWS = [
    "japandi", "minimalist", "scandinavian", "nordic", "wabi-sabi",
    "organic modern", "coastal modern", "boho",
]
_ROOM_KWS = [
    "living room", "bedroom", "kitchen", "bathroom", "dining room",
    "home office", "entryway", "mudroom", "laundry room", "outdoor",
]
_NOISE = re.compile(
    r'\s+(ideas|tips|guide|inspiration|inspo|decor|design|style|'
    r'roundup|list|picks|examples|photos)\s*$', re.I
)


def _extract_topic(title: str, categories: list):
    text = title.lower()
    style = "Japandi"
    for kw in _STYLE_KWS:
        if kw in text or any(kw in c.lower() for c in categories):
            style = kw.title()
            break
    room = "space"
    for kw in _ROOM_KWS:
        if kw in text or any(kw in c.lower() for c in categories):
            room = kw.title()
            break
    topic = re.sub(r'^\d+\s+', '', title).split(':')[0].strip()
    topic = _NOISE.sub('', topic).strip()
    return topic, room, style
