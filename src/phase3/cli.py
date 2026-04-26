"""
CLI entry point for testing Phase 3 independently.
"""
import logging
import click
import os
from ..phase1.cli import run as phase1_run, _current_iso_week
from ..phase1.config import PRODUCT_NAME
from ..phase2.pipeline import process_reviews
from .renderer import render_markdown, render_email

logging.basicConfig(level=logging.INFO)

@click.command()
@click.option('--weeks', default=8, help="Number of weeks")
@click.pass_context
def run(ctx, weeks):
    """Run Phase 1, 2, and 3."""
    iso_week = _current_iso_week()
    product = PRODUCT_NAME.lower()
    
    # Phase 1
    df = ctx.invoke(phase1_run, weeks=weeks, iso_week=iso_week, force=True)
    if df is None or df.empty:
        click.echo("No reviews to process.")
        return
        
    total_reviews = len(df)
        
    # Phase 2
    click.echo("\n[>] Starting Phase 2 Processing...")
    results = process_reviews(df)
    themes = results.get('themes', [])
    
    # Phase 3
    click.echo("\n[>] Starting Phase 3 Rendering...")
    doc_md = render_markdown(product, iso_week, total_reviews, themes)
    
    doc_url = "https://docs.google.com/document/d/MOCK_DOC_ID/edit"
    subject, email_html, email_txt = render_email(product, iso_week, total_reviews, themes, doc_url)
    
    # Output to console
    click.echo("\n" + "=" * 60)
    click.echo("  [REPORT] Rendered Markdown (Google Docs)")
    click.echo("=" * 60)
    click.echo("(Skipping console output due to Windows encoding. Saved to file.)")
    
    click.echo("\n" + "=" * 60)
    click.echo("  [REPORT] Rendered Email (Text)")
    click.echo("=" * 60)
    click.echo(f"Subject: {subject}\n")
    click.echo("(Skipping console output due to Windows encoding. Saved to file.)")
    
    # Save output to files for inspection
    os.makedirs("data/output", exist_ok=True)
    with open("data/output/report.md", "w", encoding="utf-8") as f:
        f.write(doc_md)
    with open("data/output/email.html", "w", encoding="utf-8") as f:
        f.write(email_html)
        
    click.echo("\n[OK] Saved artifacts to data/output/")
    
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    run()
