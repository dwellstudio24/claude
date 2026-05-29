"""
Pinterest pin image generator — matches Dwell Studio 24's Japandi aesthetic.

Two layout styles:
  STYLE_A — single hero image + layered text overlay
  STYLE_B — 2×2 photo grid + frosted center text box
"""

import io
import textwrap
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import requests

PIN_W, PIN_H = 1080, 1920
FONTS = Path(__file__).parent.parent / "fonts"

# Font paths
F_SERIF_BOLD   = str(FONTS / "PlayfairDisplay-Bold.ttf")
F_SERIF_ITALIC = str(FONTS / "PlayfairDisplay-Italic.ttf")
F_SANS_BOLD    = str(FONTS / "Montserrat-Bold.ttf")
# Fallbacks (always present on system)
F_SYS_SERIF    = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SYS_SANS     = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

WHITE  = (255, 255, 255)
BLACK  = (20, 20, 20)
CREAM  = (248, 244, 238)
SHADOW = (0, 0, 0, 140)

WEBSITE = "DWELLSTUDIO24.COM"


# ── Public API ────────────────────────────────────────────────────────────────

def create_style_a(
    image_url: str,
    label: str,
    title: str,
    subtitle: str = "",
    website: str = WEBSITE,
    brightness: float = 0.82,
) -> bytes:
    """Single hero image with white text overlay at top."""
    img = _fetch_crop(image_url)
    img = _adjust(img, brightness=brightness)

    draw = ImageDraw.Draw(img)
    margin = 72
    y = 90

    # ── Category label (spaced caps) ────────────────────────────────────────
    f_label = _font(F_SANS_BOLD, 28)
    label_text = _space_caps(label.upper())
    draw.text((margin, y), label_text, font=f_label, fill=WHITE)
    y += 42

    # Thin rule
    draw.line([(margin, y), (margin + 220, y)], fill=WHITE, width=2)
    y += 28

    # ── Main title (large serif bold, wrapped to ~3 words/line) ─────────────
    title_lines = _wrap_impact(title.upper(), max_words=3)
    f_title = _fit_font(F_SERIF_BOLD, title_lines, max_w=PIN_W - margin * 2, max_h=780)
    lh = _line_height(f_title)
    for line in title_lines:
        _shadow_text(draw, margin, y, line, f_title)
        y += lh + 12
    y += 14

    # ── Subtitle (italic, smaller) ───────────────────────────────────────────
    if subtitle:
        draw.line([(margin, y), (margin + 180, y)], fill=WHITE, width=1)
        y += 20
        f_sub = _font(F_SERIF_ITALIC, 52)
        _shadow_text(draw, margin, y, subtitle, f_sub)

    # ── Website (bottom) ─────────────────────────────────────────────────────
    f_web = _font(F_SANS_BOLD, 22)
    tw = _text_w(draw, _space_caps(website), f_web)
    draw.text(((PIN_W - tw) // 2, PIN_H - 58), _space_caps(website),
              font=f_web, fill=(255, 255, 255, 180))

    return _to_bytes(img)


def create_style_b(
    image_urls: list,
    label: str,
    title: str,
    subtitle: str,
    website: str = WEBSITE,
) -> bytes:
    """2×2 photo grid with frosted white center text box."""
    # Ensure we have 4 images (duplicate if fewer)
    urls = (image_urls * 4)[:4]

    canvas = Image.new("RGB", (PIN_W, PIN_H), CREAM)

    cell_w, cell_h = PIN_W // 2, PIN_H // 2
    positions = [(0, 0), (cell_w, 0), (0, cell_h), (cell_w, cell_h)]

    for (x, y), url in zip(positions, urls):
        try:
            cell = _fetch_crop(url, target_w=cell_w, target_h=cell_h)
            canvas.paste(cell, (x, y))
        except Exception:
            canvas.paste(Image.new("RGB", (cell_w, cell_h), (220, 215, 208)), (x, y))

    # ── Frosted white overlay box ─────────────────────────────────────────────
    box_x, box_y = 60, PIN_H // 2 - 260
    box_w, box_h = PIN_W - 120, 520
    overlay = Image.new("RGBA", (box_w, box_h), (248, 244, 238, 235))
    canvas.paste(Image.fromarray(
        __import__('numpy').array(overlay, dtype='uint8')[..., :3]
    ), (box_x, box_y))

    draw = ImageDraw.Draw(canvas)

    # ── Text inside box ───────────────────────────────────────────────────────
    inner_x = box_x + 48
    ty = box_y + 38

    # Small label
    f_label = _font(F_SANS_BOLD, 24)
    draw.text((inner_x, ty), label, font=f_label, fill=(120, 112, 100))
    ty += 40

    # Serif italic title (large)
    title_lines = _wrap_impact(title, max_words=2)
    f_title = _fit_font(F_SERIF_ITALIC, title_lines,
                        max_w=box_w - 96, max_h=240, start=90)
    lh = _line_height(f_title)
    for line in title_lines:
        draw.text((inner_x, ty), line, font=f_title, fill=BLACK)
        ty += lh + 4
    ty += 10

    # Bold all-caps subtitle
    f_sub = _font(F_SANS_BOLD, 34)
    sub_lines = _wrap_impact(subtitle.upper(), max_words=3)
    for line in sub_lines:
        lw = _text_w(draw, line, f_sub)
        draw.text(((PIN_W - lw) // 2, ty), line, font=f_sub, fill=BLACK)
        ty += 46

    # ── Website (bottom) ─────────────────────────────────────────────────────
    f_web = _font(F_SANS_BOLD, 20)
    tw = _text_w(draw, _space_caps(website), f_web)
    draw.text(((PIN_W - tw) // 2, PIN_H - 54), _space_caps(website),
              font=f_web, fill=(140, 130, 118))

    return _to_bytes(canvas)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fetch_crop(url: str, target_w: int = PIN_W, target_h: int = PIN_H) -> Image.Image:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    return _smart_crop(img, target_w, target_h)


def _smart_crop(img: Image.Image, tw: int, th: int) -> Image.Image:
    ow, oh = img.size
    target_ratio = tw / th
    if ow / oh > target_ratio:
        nw = int(oh * target_ratio)
        left = (ow - nw) // 2
        img = img.crop((left, 0, left + nw, oh))
    else:
        nh = int(ow / target_ratio)
        top = int((oh - nh) * 0.33)
        top = max(0, min(top, oh - nh))
        img = img.crop((0, top, ow, top + nh))
    return img.resize((tw, th), Image.LANCZOS)


def _adjust(img: Image.Image, brightness: float) -> Image.Image:
    return ImageEnhance.Brightness(img).enhance(brightness)


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        # Fallback to system fonts
        fallback = F_SYS_SERIF if "Playfair" in path else F_SYS_SANS
        return ImageFont.truetype(fallback, size)


def _fit_font(path: str, lines: list, max_w: int, max_h: int, start: int = 120) -> ImageFont.FreeTypeFont:
    """Find largest font size where all lines fit within max_w × max_h."""
    dummy = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy)
    for size in range(start, 30, -4):
        f = _font(path, size)
        lh = _line_height(f)
        if all(_text_w(draw, line, f) <= max_w for line in lines) and lh * len(lines) <= max_h:
            return f
    return _font(path, 38)


def _line_height(f: ImageFont.FreeTypeFont) -> int:
    bbox = f.getbbox("Ag")
    return bbox[3] - bbox[1]


def _text_w(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _shadow_text(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font, color=WHITE):
    """Draw text with a soft drop shadow for readability."""
    draw.text((x + 3, y + 3), text, font=font, fill=(0, 0, 0, 120))
    draw.text((x, y), text, font=font, fill=color)


def _wrap_impact(text: str, max_words: int = 3) -> list:
    """Split title into short lines (max_words per line) for visual impact."""
    words = text.split()
    lines = []
    i = 0
    while i < len(words):
        lines.append(" ".join(words[i:i + max_words]))
        i += max_words
    return lines


def _space_caps(text: str) -> str:
    """Add tracked spacing between chars: 'DWELL' → 'D W E L L'"""
    return " ".join(text)


def _to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92, optimize=True)
    return buf.getvalue()
