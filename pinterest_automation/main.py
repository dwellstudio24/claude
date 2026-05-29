#!/usr/bin/env python3
"""
Dwell Studio 24 — Pinterest Pin Automation
Usage: python main.py create <wordpress-article-url>
"""

import os
import sys
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

load_dotenv()

BASE_DIR = Path(__file__).parent
console = Console()


# ── Helpers ─────────────────────────────────────────────────────────────────

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
    mapping = boards_cfg.get("category_mapping", {})
    board_ids = boards_cfg.get("boards", {})

    for cat in categories:
        for keyword, board_key in mapping.items():
            if keyword in cat:
                board_id = board_ids.get(board_key, "")
                if board_id and board_id != "BOARD_ID_HERE":
                    return board_id

    fallback = board_ids.get("default", "")
    if not fallback or fallback == "BOARD_ID_HERE":
        console.print("[yellow]Warning:[/yellow] No board matched. Using first board from your account.")
        return ""
    return fallback


@dataclass
class PinDraft:
    index: int
    angle: str
    title: str
    description: str
    image_url: str
    image_bytes: Optional[bytes] = None
    publish_date_iso: str = ""
    publish_date_display: str = ""
    skipped: bool = False
    posted: bool = False


# ── Commands ─────────────────────────────────────────────────────────────────

@click.group()
def cli():
    """Dwell Studio 24 — Pinterest Pin Automation"""
    pass


@cli.command()
@click.argument("article_url")
@click.option("--board-id", default=None, help="Override board ID")
@click.option("--dry-run", is_flag=True, help="Generate content but don't post to Pinterest")
@click.option("--count", default=10, show_default=True, help="Number of pins to create")
@click.option("--skip-review", is_flag=True, help="Post all pins without interactive review")
def create(article_url: str, board_id: Optional[str], dry_run: bool, count: int, skip_review: bool):
    """Generate and schedule pins from a WordPress article URL."""

    cfg = load_yaml(BASE_DIR / "config.yaml")
    boards_cfg = load_yaml(BASE_DIR / "boards.yaml")

    # ── Step 1: Scrape article ───────────────────────────────────────────────
    console.print(f"\n[bold cyan]Step 1/4[/bold cyan] Fetching article…")
    from src.wp_scraper import scrape_article
    try:
        article = scrape_article(article_url)
    except Exception as e:
        console.print(f"[red]Failed to fetch article:[/red] {e}")
        sys.exit(1)

    console.print(f"  [green]✓[/green] Title: [bold]{article.title}[/bold]")
    console.print(f"  [green]✓[/green] Images found: {len(article.all_image_urls)}")
    console.print(f"  [green]✓[/green] Categories: {', '.join(article.categories) or 'none detected'}")

    if not article.all_image_urls:
        console.print("[red]No images found in article. Cannot create pins.[/red]")
        sys.exit(1)

    # ── Step 2: Generate content ─────────────────────────────────────────────
    console.print(f"\n[bold cyan]Step 2/4[/bold cyan] Generating {count} pin variations with Claude…")
    from src.content_generator import generate_pins
    try:
        pins_content = generate_pins(
            article_title=article.title,
            article_excerpt=article.excerpt,
            article_text=article.full_text,
            article_url=article_url,
            categories=article.categories,
            count=count,
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )
    except Exception as e:
        console.print(f"[red]Content generation failed:[/red] {e}")
        sys.exit(1)

    console.print(f"  [green]✓[/green] {len(pins_content)} pin variations ready")

    # ── Step 3: Build schedule ───────────────────────────────────────────────
    console.print(f"\n[bold cyan]Step 3/4[/bold cyan] Building schedule…")
    from src.scheduler import build_schedule, to_pinterest_format, to_display_format
    schedule_tz = cfg.get("scheduling", {}).get("timezone", "America/Los_Angeles")
    spread_days = cfg.get("scheduling", {}).get("spread_days", 14)
    start_offset = cfg.get("scheduling", {}).get("start_offset_days", 1)

    schedule = build_schedule(
        count=count,
        start_offset_days=start_offset,
        spread_days=spread_days,
        timezone_str=schedule_tz,
    )

    # ── Step 4: Build drafts ─────────────────────────────────────────────────
    # Cycle through available images across 10 pins
    images = article.all_image_urls
    drafts = []
    for i, pin in enumerate(pins_content):
        img_url = images[i % len(images)]
        dt = schedule[i] if i < len(schedule) else schedule[-1]
        drafts.append(PinDraft(
            index=pin.index,
            angle=pin.angle,
            title=pin.title,
            description=pin.description,
            image_url=img_url,
            publish_date_iso=to_pinterest_format(dt),
            publish_date_display=to_display_format(dt, schedule_tz),
        ))

    # ── Interactive review ───────────────────────────────────────────────────
    if not skip_review:
        console.print(f"\n[bold cyan]Step 4/4[/bold cyan] Review each pin  "
                      "[dim](k=keep · s=swap image · e=edit text · x=skip · q=quit)[/dim]\n")
        drafts = _interactive_review(drafts, images)
    else:
        console.print(f"\n[bold cyan]Step 4/4[/bold cyan] Skipping review — posting all {count} pins\n")

    active_drafts = [d for d in drafts if not d.skipped]
    if not active_drafts:
        console.print("[yellow]All pins were skipped. Nothing to post.[/yellow]")
        return

    # ── Resolve board ────────────────────────────────────────────────────────
    resolved_board = board_id or resolve_board_id(article.categories, boards_cfg)
    if not resolved_board:
        resolved_board = _pick_board_interactively(get_pinterest_client())

    if dry_run:
        _print_summary(active_drafts, resolved_board, dry_run=True)
        return

    # ── Post to Pinterest ────────────────────────────────────────────────────
    client = get_pinterest_client()
    _print_summary(active_drafts, resolved_board, dry_run=False)

    confirm = click.confirm(f"\nPost {len(active_drafts)} pins to Pinterest?", default=True)
    if not confirm:
        console.print("Aborted.")
        return

    from src.image_processor import fetch_and_crop, to_base64

    posted = 0
    for draft in active_drafts:
        try:
            console.print(f"  Posting pin {draft.index}/{count}…", end=" ")

            image_b64 = to_base64(fetch_and_crop(draft.image_url))

            result = client.create_pin(
                board_id=resolved_board,
                title=draft.title,
                description=draft.description,
                image_base64=image_b64,
                link=article_url if cfg.get("pin_link_to_article", True) else None,
                publish_date=draft.publish_date_iso,
            )
            draft.posted = True
            posted += 1
            console.print(f"[green]✓[/green] {result.pin_url}")

        except Exception as e:
            console.print(f"[red]✗[/red] {e}")

    console.print(f"\n[bold green]Done![/bold green] {posted}/{len(active_drafts)} pins scheduled.\n")


def _interactive_review(drafts: list, all_images: list) -> list:
    for draft in drafts:
        console.rule(f"[bold]Pin {draft.index} of {len(drafts)}[/bold]  ·  {draft.angle}")
        _print_pin_panel(draft)

        while True:
            choice = click.prompt(
                "  Action",
                default="k",
                prompt_suffix=" [k/s/e/x/q] > ",
            ).strip().lower()

            if choice == "k":
                break
            elif choice == "s":
                draft = _swap_image(draft, all_images)
                _print_pin_panel(draft)
            elif choice == "e":
                draft = _edit_text(draft)
                _print_pin_panel(draft)
            elif choice == "x":
                draft.skipped = True
                console.print("  [dim]Skipped.[/dim]")
                break
            elif choice == "q":
                console.print("[yellow]Review quit early. Remaining pins will be posted as-is.[/yellow]")
                return drafts
            else:
                console.print("  [dim]k=keep  s=swap image  e=edit text  x=skip  q=quit[/dim]")

    return drafts


def _print_pin_panel(draft: PinDraft):
    content = (
        f"[bold]Title:[/bold]       {draft.title}\n\n"
        f"[bold]Description:[/bold] {draft.description}\n\n"
        f"[bold]Image:[/bold]       {draft.image_url}\n"
        f"[bold]Scheduled:[/bold]   {draft.publish_date_display}"
    )
    console.print(Panel(content, expand=False, border_style="blue"))


def _swap_image(draft: PinDraft, all_images: list) -> PinDraft:
    console.print("\n  Available images:")
    for i, url in enumerate(all_images):
        marker = " [cyan]← current[/cyan]" if url == draft.image_url else ""
        short = url.split("/")[-1][:60]
        console.print(f"    [{i+1}] {short}{marker}")

    idx = click.prompt("  Pick image number", type=int, default=1) - 1
    if 0 <= idx < len(all_images):
        draft.image_url = all_images[idx]
        console.print(f"  [green]✓[/green] Image updated.")
    else:
        console.print("  [yellow]Invalid choice, keeping original.[/yellow]")
    return draft


def _edit_text(draft: PinDraft) -> PinDraft:
    console.print("\n  Edit title (leave blank to keep):")
    new_title = click.prompt("  Title", default=draft.title)
    if new_title:
        draft.title = new_title[:100]

    console.print("\n  Edit description (leave blank to keep):")
    new_desc = click.prompt("  Description", default=draft.description)
    if new_desc:
        draft.description = new_desc[:500]

    return draft


def _print_summary(drafts: list, board_id: str, dry_run: bool):
    label = "DRY RUN — " if dry_run else ""
    t = Table(title=f"{label}Pin Schedule", box=box.SIMPLE_HEAVY, show_lines=True)
    t.add_column("#", style="dim", width=3)
    t.add_column("Angle", width=24)
    t.add_column("Title", width=40)
    t.add_column("Scheduled", width=24)

    for d in drafts:
        if not d.skipped:
            t.add_row(str(d.index), d.angle, d.title, d.publish_date_display)

    console.print(t)
    console.print(f"  Board ID: [cyan]{board_id}[/cyan]\n")


def _pick_board_interactively(client) -> str:
    boards = client.get_boards()
    if not boards:
        console.print("[red]No boards found on your Pinterest account.[/red]")
        sys.exit(1)

    console.print("\nPick a board:")
    for i, b in enumerate(boards):
        console.print(f"  [{i+1}] {b['name']}  [dim]{b['id']}[/dim]")

    idx = click.prompt("Board number", type=int, default=1) - 1
    return boards[max(0, min(idx, len(boards)-1))]["id"]


# ── Other commands ────────────────────────────────────────────────────────────

@cli.command()
def boards():
    """List all Pinterest boards with their IDs."""
    client = get_pinterest_client()
    boards_list = client.get_boards()

    t = Table(title="Your Pinterest Boards", box=box.SIMPLE_HEAVY)
    t.add_column("Name", style="bold")
    t.add_column("Board ID", style="cyan")
    t.add_column("Privacy")

    for b in boards_list:
        t.add_row(b.get("name", ""), b.get("id", ""), b.get("privacy", ""))

    console.print(t)
    console.print("\n[dim]Copy these IDs into boards.yaml[/dim]")


@cli.command()
def auth():
    """Run Pinterest OAuth flow to generate an access token."""
    client_id = os.getenv("PINTEREST_CLIENT_ID") or click.prompt("Pinterest App ID")
    client_secret = os.getenv("PINTEREST_CLIENT_SECRET") or click.prompt("Pinterest App Secret", hide_input=True)

    console.print("\n[cyan]Opening Pinterest in your browser…[/cyan]")
    console.print("[dim]Waiting for authorization (120s timeout)…[/dim]\n")

    from src.pinterest_client import get_oauth_token
    try:
        token = get_oauth_token(client_id, client_secret)
        console.print(f"[green]✓ Access token:[/green]\n\n  {token}\n")
        console.print("[dim]Add this to your .env file as PINTEREST_ACCESS_TOKEN[/dim]")
    except Exception as e:
        console.print(f"[red]Auth failed:[/red] {e}")


@cli.command()
def verify():
    """Verify your Pinterest credentials."""
    client = get_pinterest_client()
    try:
        info = client.verify_token()
        console.print(f"[green]✓ Connected as:[/green] {info.get('username', 'unknown')}")
        console.print(f"  Account type: {info.get('account_type', 'unknown')}")
    except Exception as e:
        console.print(f"[red]Verification failed:[/red] {e}")


if __name__ == "__main__":
    cli()
