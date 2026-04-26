"""
Agent Orchestrator - Connects Ingestion, Processing, and Rendering.
Enforces idempotency and structures logging.
"""
import os
import time
import logging
from datetime import datetime, timezone
import yaml

from ..config import get_product_config, load_config
from ..phase1.ingestion import fetch_app_store_reviews, fetch_google_play_reviews, normalize_reviews
from ..phase1.state import is_already_delivered, record_run
from ..phase2.pipeline import process_reviews
from ..phase3.renderer import render_markdown, render_email

# Ensure log directory exists
config = load_config()
log_dir = config.get("logging", {}).get("dir", "data/logs")
os.makedirs(log_dir, exist_ok=True)

# File logger
log_file = os.path.join(log_dir, f"pulse_{datetime.now().strftime('%Y%m%d')}.log")
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-8s  %(name)s  %(message)s"))
logging.getLogger().addHandler(file_handler)

logger = logging.getLogger(__name__)

def _current_iso_week() -> str:
    """Return the current ISO week as 'YYYY-WNN'."""
    now = datetime.now(timezone.utc)
    iso = now.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"

def run_pulse(product: str, iso_week: str = None, weeks: int = None, dry_run: bool = False, force: bool = False):
    """
    Run the full end-to-end pulse agent for a specific product.
    """
    iso_week = iso_week or _current_iso_week()
    
    try:
        cfg = get_product_config(product)
    except ValueError as e:
        logger.error(e)
        return
        
    weeks = weeks or cfg.get("default_review_window_weeks", 8)
    doc_id = cfg.get("doc_id", "Unknown")
    
    logger.info("="*50)
    logger.info("Starting Pulse Agent: Product=%s, Week=%s, Window=%dw, DryRun=%s", product, iso_week, weeks, dry_run)
    
    # 1. Idempotency Check
    if not force and is_already_delivered(product, iso_week):
        logger.info("SKIP: Pulse already delivered for %s / %s. Use --force to re-run.", product, iso_week)
        return
        
    start_time = time.time()
    
    # 2. Ingestion
    logger.info("Phase 1: Ingestion")
    app_store = fetch_app_store_reviews()
    gplay = fetch_google_play_reviews()
    df = normalize_reviews(app_store, gplay, weeks=weeks)
    
    if df.empty:
        logger.warning("No reviews found. Aborting.")
        return
        
    review_count = len(df)
    
    # 3. Processing
    logger.info("Phase 2: Processing Pipeline")
    results = process_reviews(df)
    themes = results.get("themes", [])
    
    # 4. Rendering
    logger.info("Phase 3: Rendering")
    doc_md = render_markdown(product, iso_week, review_count, themes)
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    subject, email_html, email_txt = render_email(product, iso_week, review_count, themes, doc_url)
    
    # 5. Delivery (or Dry Run)
    if dry_run:
        logger.info("DRY RUN: Saving output locally.")
        os.makedirs("data/output", exist_ok=True)
        with open("data/output/report.md", "w", encoding="utf-8") as f:
            f.write(doc_md)
        with open("data/output/email.html", "w", encoding="utf-8") as f:
            f.write(email_html)
        logger.info("Dry run complete. Saved to data/output/")
        
        # We don't record delivered status on dry run.
        record_run(product, iso_week, "pending", review_count)
        
    else:
        logger.info("DELIVERY: (Phase 6 Placeholder)")
        # TODO: Phase 6 MCP delivery logic goes here.
        # record_run(product, iso_week, "delivered", review_count)
    
    elapsed = time.time() - start_time
    logger.info("Pulse Agent run completed in %.1fs.", elapsed)
    logger.info("="*50)
