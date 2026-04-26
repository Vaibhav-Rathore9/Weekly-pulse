"""
CLI entry point for the Weekly Product Review Pulse.

Usage:
    python -m src.phase1 run --weeks 8
    python -m src.phase1 run --iso-week 2026-W17
    python -m src.phase1 run --weeks 8 --force
"""

import logging
import sys
import time
from datetime import datetime, timezone

import click
import pandas as pd

from .config import DEFAULT_REVIEW_WINDOW_WEEKS, PRODUCT_NAME
from .ingestion import (
    fetch_app_store_reviews,
    fetch_google_play_reviews,
    normalize_reviews,
)
from .state import is_already_delivered, record_run

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("pulse")


def _current_iso_week() -> str:
    """Return the current ISO week as 'YYYY-WNN'."""
    now = datetime.now(timezone.utc)
    iso = now.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def _print_summary(df: pd.DataFrame, elapsed: float) -> None:
    """Print a human-readable summary table of the fetched reviews."""
    total = len(df)
    if total == 0:
        click.echo("\n[!] No reviews found.\n")
        return

    app_store_count = len(df[df["source"] == "app_store"])
    gplay_count = len(df[df["source"] == "google_play"])

    date_col = df["date"].dropna()
    if len(date_col) > 0:
        oldest = date_col.min().strftime("%Y-%m-%d")
        newest = date_col.max().strftime("%Y-%m-%d")
    else:
        oldest = newest = "N/A"

    avg_rating = df["rating"].mean()

    click.echo("\n" + "=" * 60)
    click.echo("  [REPORT]  Groww -- Review Ingestion Summary")
    click.echo("=" * 60)
    click.echo(f"  Total reviews      : {total}")
    click.echo(f"  App Store          : {app_store_count}")
    click.echo(f"  Google Play        : {gplay_count}")
    click.echo(f"  Date range         : {oldest}  ->  {newest}")
    click.echo(f"  Average rating     : {avg_rating:.2f} / 5")
    click.echo(f"  Elapsed time       : {elapsed:.1f}s")
    click.echo("=" * 60)

    # Rating distribution
    click.echo("\n  Rating Distribution:")
    for star in range(5, 0, -1):
        count = len(df[df["rating"] == star])
        bar = "#" * (count // max(total // 40, 1))
        click.echo(f"    {'*' * star}{'  ' * (5 - star)}  {count:>4}  {bar}")

    click.echo()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
@click.group()
def cli():
    """Weekly Product Review Pulse -- AI Agent CLI."""
    pass


@cli.command()
@click.option(
    "--weeks", "-w",
    type=int,
    default=DEFAULT_REVIEW_WINDOW_WEEKS,
    show_default=True,
    help="Number of weeks of reviews to fetch (1-52).",
)
@click.option(
    "--iso-week",
    type=str,
    default=None,
    help="Specific ISO week to label this run (e.g. 2026-W17). Defaults to current week.",
)
@click.option(
    "--force", is_flag=True, default=False,
    help="Force re-run even if already delivered.",
)
def run(weeks: int, iso_week: str | None, force: bool):
    """Fetch and normalise Groww reviews from App Store & Google Play."""

    # --- Validate inputs ---
    if weeks < 1 or weeks > 52:
        click.echo("[ERROR] --weeks must be between 1 and 52.", err=True)
        sys.exit(1)

    iso_week = iso_week or _current_iso_week()
    product = PRODUCT_NAME.lower()

    click.echo(f"\n[>] Pulse run: product={product}, iso_week={iso_week}, window={weeks}w")

    # --- Idempotency check ---
    if not force and is_already_delivered(product, iso_week):
        click.echo(
            f"[OK] Already delivered for {product} / {iso_week}. "
            f"Use --force to re-run."
        )
        sys.exit(0)

    start = time.time()

    # --- Ingest ---
    click.echo("\n[1/3] Fetching App Store reviews ...")
    app_store = fetch_app_store_reviews()

    click.echo("[2/3] Fetching Google Play reviews ...")
    gplay = fetch_google_play_reviews()

    # --- Normalise ---
    click.echo("[3/3] Normalising and de-duplicating ...")
    df = normalize_reviews(app_store, gplay, weeks=weeks)

    elapsed = time.time() - start

    # --- Summary ---
    _print_summary(df, elapsed)

    # --- Record the run ---
    record_run(
        product=product,
        iso_week=iso_week,
        status="pending",  # Phase 1 only does ingestion; later phases update to delivered
        review_count=len(df),
    )
    click.echo(f"[DB] Run recorded in state DB (status=pending, {len(df)} reviews).\n")

    return df


def main():
    cli()


if __name__ == "__main__":
    main()
