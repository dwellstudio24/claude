#!/usr/bin/env python3
"""
Dwell Studio 24 — Pinterest Pin Automation
Usage: python main.py create <wordpress-article-url>
"""

import os
import sys
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

load_dotenv()

BASE_DIR  = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
console = Console()


# ── Config helpers ────────────────────────────────────────────────────────────

def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def get_pinterest_client():
    from src.pinterest_client import PinterestClient
    token = os.getenv("PINTEREST_ACCESS_TOKEN")
    if not token:
        console.print("[red]Error:[/red] PINTEREST_ACCESS_TOKEN not set in .env")
        sys.exit(1)
    return PinterestClient(token)


def resolve_board_id(categories: list, boards_cfg: dict) -> str:
    mapping  = boards_cfg.get("category_mapping", {})
    board_ids = boards_cfg.get("boards", {})
    for cat in categories:
        for kw, board_key in mapping.items():
            if kw in cat:
                bid = board_ids.get(board_key, "")
                if bid and bid != "BOARD_ID_HERE":
                    return bid
    fallback = board_ids.get("default", "")
    return fallback if (fallback and fallback != "BOARD_ID_HERE") else ""


# ── Pin draft ─────────────────────────────────────────────────────────────────

@dataclass
class PinDraft:
    index: int
    angle: str
    main_kw: str
    title: str
    description: str
    label: str
    subtitle: str
    style: str              # "A" or "B"
    image_url: str
    all_image_urls: list    # for swapping
    publish_date_iso: str  = ""
    publish_date_display: str = ""
    skipped: bool = False
    image_bytes: bytes = field(default=None, repr=False)


# ── Commands ──────────────────────────────────────────────────────────────────

@click.group()
def cli():
    """Dwell Studio 24 — Pinterest Pin Automation"""
    pass


@cli.command()
@click.argument("article_url")
@click.option("--board-id", default=None, help="Override Pinterest board ID")
@click.option("--dry-run", is_flag=True, help="Generate images but don't post")
@click.option("--skip-review", is_flag=True, help="Post without interactive review")
@click.option("--kw-file", default=None, type=click.Path(exists=True),
              help="YAML file with main_kws / core_kw / other_kws")
def create(article_url, board_id, dry_run, skip_review, kw_file):
    """Generate, preview and schedule pins from a WordPress article URL."""

    cfg        = load_yaml(BASE_DIR / "config.yaml")
    boards_cfg = load_yaml(BASE_DIR / "boards.yaml")

    # ── Step 1: Scrape article ───────────────────────────────────────────────
    console.print("\n[bold cyan]Step 1/5[/bold cyan] Fetching article…")
    from src.wp_scraper import scrape_article
    try:
        article = scrape_article(article_url)
    except Exception as e:
        console.print(f"[red]Failed:[/red] {e}")
        sys.exit(1)

    console.print(f"  [green]✓[/green] [bold]{article.title}[/bold]")
    console.print(f"  [green]✓[/green] {len(article.all_image_urls)} image(s) found")

    if not article.all_image_urls:
        console.print("[red]No images found. Cannot create pins.[/red]")
        sys.exit(1)

    # ── Step 2: Gather keywords ──────────────────────────────────────────────
    console.print("\n[bold cyan]Step 2/5[/bold cyan] Keywords…")
    main_kws, core_kw, other_kws = _gather_keywords(kw_file)

    pin_count = len(main_kws) * 5 if main_kws else cfg.get("scheduling", {}).get("pins_per_article", 10)

    # ── Step 3: Generate content ─────────────────────────────────────────────
    console.print(f"\n[bold cyan]Step 3/5[/bold cyan] Generating {pin_count} pin variations…")
    from src.content_generator import generate_pins
    try:
        pins_content = generate_pins(
            article_title=article.title,
            article_excerpt=article.excerpt,
            article_text=article.full_text,
            article_url=article_url,
            categories=article.categories,
            count=pin_count,
            main_kws=main_kws if main_kws else None,
            core_kw=core_kw,
            other_kws=other_kws,
        )
    except Exception as e:
        console.print(f"[red]Content generation failed:[/red] {e}")
        sys.exit(1)
    console.print(f"  [green]✓[/green] {len(pins_content)} pins ready")

    # ── Step 4: Build schedule ───────────────────────────────────────────────
    console.print(f"\n[bold cyan]Step 4/5[/bold cyan] Building schedule…")
    from src.scheduler import build_schedule, to_pinterest_format, to_display_format
    tz       = cfg.get("scheduling", {}).get("timezone", "America/Los_Angeles")
    spread   = cfg.get("scheduling", {}).get("spread_days", 14)
    offset   = cfg.get("scheduling", {}).get("start_offset_days", 1)
    schedule = build_schedule(len(pins_content), start_offset_days=offset,
                              spread_days=spread, timezone_str=tz)

    images = article.all_image_urls
    drafts = []
    for i, pin in enumerate(pins_content):
        img_url = images[i % len(images)]
        dt = schedule[i] if i < len(schedule) else schedule[-1]
        drafts.append(PinDraft(
            index=pin.index, angle=pin.angle, main_kw=pin.main_kw,
            title=pin.title, description=pin.description,
            label=pin.label, subtitle=pin.subtitle, style=pin.style,
            image_url=img_url, all_image_urls=images,
            publish_date_iso=to_pinterest_format(dt),
            publish_date_display=to_display_format(dt, tz),
        ))

    # ── Step 5: Review ───────────────────────────────────────────────────────
    if not skip_review:
        console.print(f"\n[bold cyan]Step 5/5[/bold cyan] Review  "
                      "[dim](k=keep · s=swap image · e=edit text · x=skip · q=finish review)[/dim]\n")
        drafts = _interactive_review(drafts)
    else:
        console.print(f"\n[bold cyan]Step 5/5[/bold cyan] Skipping review — {len(drafts)} pins queued\n")

    active = [d for d in drafts if not d.skipped]
    if not active:
        console.print("[yellow]All pins skipped.[/yellow]")
        return

    # ── Save draft text file ─────────────────────────────────────────────────
    slug = _url_slug(article_url)
    date_str = datetime.now().strftime("%Y%m%d")
    out_dir = OUTPUT_DIR / f"{date_str}_{slug}"
    out_dir.mkdir(parents=True, exist_ok=True)

    draft_path = out_dir / f"pin_copy_{date_str}_{slug}.md"
    _save_draft(active, article.title, article_url, main_kws, core_kw, other_kws, draft_path)
    console.print(f"\n  [dim]Draft saved → {draft_path}[/dim]")

    # ── Resolve board ────────────────────────────────────────────────────────
    resolved_board = board_id or resolve_board_id(article.categories, boards_cfg)
    if not resolved_board and not dry_run:
        resolved_board = _pick_board_interactively(get_pinterest_client())

    _print_summary(active, resolved_board, dry_run)

    if dry_run:
        console.print("\n[yellow]Dry run — images will be generated but not posted.[/yellow]")
    else:
        if not click.confirm(f"\nPost {len(active)} pins to Pinterest?", default=True):
            console.print("Aborted.")
            return

    # ── Generate images & post ───────────────────────────────────────────────
    from src.image_designer import create_style_a, create_style_b
    client = get_pinterest_client() if not dry_run else None
    posted = 0

    for d in active:
        console.print(f"  Pin {d.index}/{len(active)} [{d.style}] {d.main_kw}…", end=" ")
        try:
            if d.style == "B" and len(d.all_image_urls) >= 2:
                img_urls = (d.all_image_urls * 4)[:4]
                img_bytes = create_style_b(img_urls, d.label, d.title, d.subtitle)
            else:
                img_bytes = create_style_a(d.image_url, d.label, d.title, d.subtitle)

            # Save locally
            img_path = out_dir / f"pin_{d.index:02d}_{d.angle.lower().replace(' ', '_')}.jpg"
            img_path.write_bytes(img_bytes)

            if not dry_run:
                from src.image_processor import to_base64
                result = client.create_pin(
                    board_id=resolved_board,
                    title=d.title,
                    description=d.description,
                    image_base64=to_base64(img_bytes),
                    link=article_url,
                    publish_date=d.publish_date_iso,
                )
                posted += 1
                console.print(f"[green]✓[/green] {result.pin_url}")
            else:
                posted += 1
                console.print(f"[green]✓[/green] saved → {img_path.name}")

        except Exception as e:
            console.print(f"[red]✗[/red] {e}")

    action = "generated" if dry_run else "scheduled"
    console.print(f"\n[bold green]Done![/bold green] {posted}/{len(active)} pins {action}.")
    console.print(f"  Images saved → [cyan]{out_dir}[/cyan]\n")


# ── Keyword gathering ─────────────────────────────────────────────────────────

def _gather_keywords(kw_file: Optional[str]) -> tuple:
    """Return (main_kws, core_kw, other_kws). Interactive or from file."""
    if kw_file:
        data = load_yaml(Path(kw_file))
        return (data.get("main_kws", []), data.get("core_kw", ""),
                data.get("other_kws", []))

    use_kws = click.confirm(
        "  Add Pinterest keywords for SEO-optimised titles & descriptions?",
        default=True
    )
    if not use_kws:
        return [], "", []

    console.print("\n  [bold]Main Keywords[/bold] [dim](from Pinterest Trends — press Enter after each, blank line to finish)[/dim]")
    console.print("  [dim]Example: japandi dining room[/dim]")
    main_kws = []
    while len(main_kws) < 4:
        kw = click.prompt(f"  Main KW {len(main_kws)+1}", default="", show_default=False)
        if not kw.strip():
            break
        main_kws.append(kw.strip().lower())

    core_kw = ""
    if main_kws:
        console.print("\n  [bold]Core Keyword[/bold] [dim](2nd Pinterest Trends KW — used in title or description)[/dim]")
        core_kw = click.prompt("  Core KW", default="", show_default=False).strip().lower()

    other_kws = []
    console.print("\n  [bold]Other Keywords[/bold] [dim](from PinClicks — blank line to finish)[/dim]")
    console.print("  [dim]Optional tags: [secondary] style genre · [contextual] material/method · [qualifier] size/budget[/dim]")
    console.print("  [dim]Or just list them — system auto-assigns first=secondary, second=contextual, third=qualifier[/dim]")
    while True:
        kw = click.prompt("  KW", default="", show_default=False)
        if not kw.strip():
            break
        other_kws.append(kw.strip().lower())

    return main_kws, core_kw, other_kws


# ── Interactive review ────────────────────────────────────────────────────────

def _interactive_review(drafts: list) -> list:
    for draft in drafts:
        console.rule(f"[bold]Pin {draft.index}/{len(drafts)}[/bold]  ·  {draft.angle}  ·  Style {draft.style}")
        _print_pin_panel(draft)

        while True:
            choice = click.prompt("  Action", default="k",
                                  prompt_suffix=" [k/s/e/x/q] > ").strip().lower()
            if choice == "k":
                break
            elif choice == "s":
                draft = _swap_image(draft)
                _print_pin_panel(draft)
            elif choice == "e":
                draft = _edit_text(draft)
                _print_pin_panel(draft)
            elif choice == "x":
                draft.skipped = True
                console.print("  [dim]Skipped.[/dim]")
                break
            elif choice == "q":
                console.print("[yellow]Review finished early — remaining pins posted as-is.[/yellow]")
                return drafts
            else:
                console.print("  [dim]k=keep  s=swap image  e=edit text  x=skip  q=quit review[/dim]")

    return drafts


def _print_pin_panel(d: PinDraft):
    content = (
        f"[bold]Title:[/bold]       {d.title}\n\n"
        f"[bold]Description:[/bold] {d.description}\n\n"
        f"[bold]Image label:[/bold] {d.label}  •  {d.subtitle}\n"
        f"[bold]Image URL:[/bold]   {d.image_url[:80]}\n"
        f"[bold]Layout:[/bold]      Style {d.style} {'(grid)' if d.style == 'B' else '(hero)'}\n"
        f"[bold]Scheduled:[/bold]   {d.publish_date_display}"
    )
    console.print(Panel(content, expand=False, border_style="blue"))


def _swap_image(draft: PinDraft) -> PinDraft:
    console.print("\n  Available images:")
    for i, url in enumerate(draft.all_image_urls):
        marker = " [cyan]← current[/cyan]" if url == draft.image_url else ""
        console.print(f"    [{i+1}] {url.split('/')[-1][:60]}{marker}")
    idx = click.prompt("  Pick number", type=int, default=1) - 1
    if 0 <= idx < len(draft.all_image_urls):
        draft.image_url = draft.all_image_urls[idx]
        console.print("  [green]✓[/green] Image updated.")
    return draft


def _edit_text(draft: PinDraft) -> PinDraft:
    console.print("\n  [bold]Edit Title[/bold] (max 100 chars)")
    t = click.prompt("  Title", default=draft.title)
    if t: draft.title = t[:100]

    console.print("  [bold]Edit Description[/bold] (max 500 chars)")
    d = click.prompt("  Description", default=draft.description)
    if d: draft.description = d[:500]

    console.print("  [bold]Edit Image label[/bold] (shown on image, e.g. INSPIRATIONS)")
    lb = click.prompt("  Label", default=draft.label)
    if lb: draft.label = lb.upper()

    console.print("  [bold]Edit Subtitle[/bold] (shown on image, e.g. STYLING + TIPS)")
    sub = click.prompt("  Subtitle", default=draft.subtitle)
    if sub: draft.subtitle = sub.upper()

    return draft


# ── Helpers ───────────────────────────────────────────────────────────────────

def _print_summary(drafts: list, board_id: str, dry_run: bool):
    label = "DRY RUN — " if dry_run else ""
    t = Table(title=f"{label}Pin Schedule", box=box.SIMPLE_HEAVY, show_lines=True)
    t.add_column("#",      style="dim", width=3)
    t.add_column("KW",     width=22)
    t.add_column("Angle",  width=14)
    t.add_column("Style",  width=7)
    t.add_column("Title",  width=36)
    t.add_column("Date",   width=22)
    for d in drafts:
        if not d.skipped:
            t.add_row(str(d.index), d.main_kw or "—", d.angle, f"Style {d.style}",
                      d.title[:35], d.publish_date_display)
    console.print(t)
    if board_id:
        console.print(f"  Board: [cyan]{board_id}[/cyan]\n")


def _save_draft(drafts, article_title, article_url, main_kws, core_kw, other_kws, path: Path):
    lines = [
        f"# Pin Copy — {article_title}\n",
        "## Keywords Used",
        f"- Main: {', '.join(main_kws) if main_kws else 'auto'}",
        f"- Core: {core_kw or 'auto'}",
        f"- Other: {', '.join(other_kws) if other_kws else 'auto'}",
        "",
        f"## Blog Post URL\n{article_url}\n",
    ]
    for d in drafts:
        lines += [
            f"---\nPin {d.index} ({d.angle} · Main KW: {d.main_kw})",
            f"Title:\n{d.title}\n",
            f"Description:\n{d.description}\n",
            f"Image label: {d.label}  |  Subtitle: {d.subtitle}  |  Style: {d.style}",
            f"Scheduled: {d.publish_date_display}\n",
        ]
    from datetime import datetime
    lines += [f"\n---\n生成日: {datetime.now().strftime('%Y-%m-%d')}\nステータス: 下書き"]
    path.write_text("\n".join(lines), encoding="utf-8")


def _url_slug(url: str) -> str:
    from urllib.parse import urlparse
    parts = [p for p in urlparse(url).path.strip("/").split("/") if p]
    return (parts[-1] if parts else "article")[:40]


def _pick_board_interactively(client) -> str:
    boards = client.get_boards()
    if not boards:
        console.print("[red]No boards found.[/red]")
        sys.exit(1)
    console.print("\nPick a board:")
    for i, b in enumerate(boards):
        console.print(f"  [{i+1}] {b['name']}  [dim]{b['id']}[/dim]")
    idx = click.prompt("Board number", type=int, default=1) - 1
    return boards[max(0, min(idx, len(boards)-1))]["id"]


# ── Other commands ─────────────────────────────────────────────────────────────

@cli.command()
def boards():
    """List all Pinterest boards with IDs."""
    client = get_pinterest_client()
    t = Table(title="Your Pinterest Boards", box=box.SIMPLE_HEAVY)
    t.add_column("Name", style="bold")
    t.add_column("Board ID", style="cyan")
    t.add_column("Privacy")
    for b in client.get_boards():
        t.add_row(b.get("name", ""), b.get("id", ""), b.get("privacy", ""))
    console.print(t)
    console.print("\n[dim]Copy these IDs into boards.yaml[/dim]")


@cli.command()
def verify():
    """Verify Pinterest credentials."""
    client = get_pinterest_client()
    try:
        info = client.verify_token()
        console.print(f"[green]✓ Connected as:[/green] {info.get('username', 'unknown')}")
    except Exception as e:
        console.print(f"[red]Failed:[/red] {e}")


@cli.command()
def auth():
    """Run Pinterest OAuth flow."""
    client_id     = os.getenv("PINTEREST_CLIENT_ID") or click.prompt("App ID")
    client_secret = os.getenv("PINTEREST_CLIENT_SECRET") or click.prompt("App Secret", hide_input=True)
    from src.pinterest_client import get_oauth_token
    try:
        token = get_oauth_token(client_id, client_secret)
        console.print(f"\n[green]✓ Token:[/green]\n\n  {token}\n")
        console.print("[dim]Add to .env as PINTEREST_ACCESS_TOKEN[/dim]")
    except Exception as e:
        console.print(f"[red]Auth failed:[/red] {e}")


if __name__ == "__main__":
    cli()
