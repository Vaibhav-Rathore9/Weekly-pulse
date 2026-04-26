"""
CLI entry point for testing Phase 2 independently.
"""
import logging
import click
import json
from dotenv import load_dotenv

load_dotenv()

from ..phase1.cli import run as phase1_run
from .pipeline import process_reviews

logging.basicConfig(level=logging.INFO)

@click.command()
@click.option('--weeks', default=8, help="Number of weeks")
@click.option('--iso-week', default=None, help="ISO week")
@click.pass_context
def run(ctx, weeks, iso_week):
    """Run Phase 1 and Phase 2."""
    df = ctx.invoke(phase1_run, weeks=weeks, iso_week=iso_week, force=True)
    
    if df is None or df.empty:
        click.echo("No reviews to process.")
        return
        
    click.echo("\n[>] Starting Phase 2 Processing...")
    results = process_reviews(df)
    
    click.echo("\n" + "=" * 60)
    click.echo("  [REPORT] Phase 2 Results")
    click.echo("=" * 60)
    click.echo(json.dumps(results, indent=2))
    
if __name__ == "__main__":
    run()
