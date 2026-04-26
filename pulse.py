"""
Root CLI for the Weekly Product Review Pulse AI Agent.
"""
import logging
import click
from dotenv import load_dotenv

from src.phase4.orchestrator import run_pulse

# Load environment variables first
load_dotenv()

# Setup base logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

@click.group()
def cli():
    """Weekly Product Review Pulse -- AI Agent CLI."""
    pass

@cli.command()
@click.option('--product', '-p', required=True, help="Product name (e.g. groww)")
@click.option('--weeks', '-w', type=int, help="Number of weeks of reviews to fetch (1-52). Overrides config.")
@click.option('--iso-week', type=str, help="Specific ISO week (e.g. 2026-W17). Defaults to current week.")
@click.option('--dry-run', is_flag=True, help="Run without delivering. Saves artifacts locally.")
@click.option('--force', is_flag=True, help="Force re-run even if already delivered.")
def run(product: str, weeks: int, iso_week: str, dry_run: bool, force: bool):
    """Run the end-to-end review agent."""
    run_pulse(
        product=product.lower(),
        iso_week=iso_week,
        weeks=weeks,
        dry_run=dry_run,
        force=force
    )

if __name__ == "__main__":
    cli()
