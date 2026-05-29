import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse, urljoin


@dataclass
class ArticleData:
    title: str
    url: str
    excerpt: str
    categories: list
    featured_image_url: Optional[str]
    all_image_urls: list
    full_text: str


def scrape_article(url: str) -> ArticleData:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; DwellStudio24Bot/1.0)"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    title = _get_meta(soup, "og:title") or _text(soup.find("h1")) or ""
    excerpt = (
        _get_meta(soup, "og:description")
        or _get_meta_name(soup, "description")
        or ""
    )
    featured_image_url = _get_meta(soup, "og:image") or None

    gallery_images = _scrape_content_images(soup, url)

    # Deduplicate, featured first
    all_images = []
    if featured_image_url:
        all_images.append(featured_image_url)
    for img in gallery_images:
        if img not in all_images:
            all_images.append(img)

    categories = _extract_categories(soup, url)
    full_text = _extract_text(soup)[:3000]

    return ArticleData(
        title=title,
        url=url,
        excerpt=excerpt,
        categories=categories,
        featured_image_url=featured_image_url,
        all_image_urls=all_images,
        full_text=full_text,
    )


def _get_meta(soup: BeautifulSoup, property_name: str) -> Optional[str]:
    tag = soup.find("meta", property=property_name)
    return tag.get("content", "").strip() if tag else None


def _get_meta_name(soup: BeautifulSoup, name: str) -> Optional[str]:
    tag = soup.find("meta", {"name": name})
    return tag.get("content", "").strip() if tag else None


def _text(tag) -> Optional[str]:
    return tag.get_text(strip=True) if tag else None


def _scrape_content_images(soup: BeautifulSoup, base_url: str) -> list:
    skip = {"logo", "icon", "avatar", "emoji", "spinner", "loading", "banner-ad"}
    images = []

    content = (
        soup.find("article")
        or soup.find(class_="entry-content")
        or soup.find(class_="post-content")
        or soup.find(id="content")
    )
    if not content:
        return images

    for img in content.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src", "")
        if not src:
            continue
        src = urljoin(base_url, src)
        src_lower = src.lower()
        if any(s in src_lower for s in skip):
            continue
        # Skip tiny tracking pixels
        w = img.get("width", "")
        h = img.get("height", "")
        try:
            if int(w) < 100 or int(h) < 100:
                continue
        except (ValueError, TypeError):
            pass
        images.append(src)

    return images


def _extract_categories(soup: BeautifulSoup, url: str) -> list:
    categories = set()
    design_keywords = [
        "living-room", "bedroom", "kitchen", "bathroom", "dining-room",
        "japandi", "minimalist", "color", "paint", "furniture", "decor",
        "entryway", "home-office", "outdoor", "laundry",
    ]
    for part in url.lower().split("/"):
        for kw in design_keywords:
            if kw in part:
                categories.add(kw.replace("-", " "))

    for tag in soup.find_all("a", rel=lambda r: r and "category" in r):
        categories.add(tag.get_text(strip=True).lower())

    return list(categories)


def _extract_text(soup: BeautifulSoup) -> str:
    for tag in soup.find_all(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    content = (
        soup.find("article")
        or soup.find(class_="entry-content")
        or soup.find(class_="post-content")
        or soup.body
    )
    return content.get_text(separator=" ", strip=True) if content else ""
