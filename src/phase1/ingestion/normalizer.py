"""
Normalizer — merges App Store and Google Play reviews into a single DataFrame
with a unified schema and de-duplicates by review_id.

Unified schema:
    review_id   : str       (prefixed: "appstore_..." or "gplay_...")
    date        : datetime  (timezone-aware, nullable)
    source      : str       ("app_store" | "google_play")
    rating      : int       (1-5)
    text        : str       (non-empty)
    app_version : str|None
    product     : str       ("groww")
"""

import logging
from datetime import datetime, timedelta, timezone

import pandas as pd
from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)

def _is_valid_review(text: str) -> bool:
    """Check if the text is > 5 words and written in English."""
    if not text:
        return False
        
    words = text.split()
    if len(words) <= 5:
        return False
        
    try:
        return detect(text) == 'en'
    except LangDetectException:
        return False


def normalize_reviews(
    app_store_reviews: list[dict],
    google_play_reviews: list[dict],
    weeks: int = 8,
) -> pd.DataFrame:
    """
    Merge, validate, filter, and de-duplicate reviews from both sources.

    Args:
        app_store_reviews: Raw review dicts from the App Store fetcher.
        google_play_reviews: Raw review dicts from the Google Play fetcher.
        weeks: Only keep reviews from the last N weeks.

    Returns:
        A pandas DataFrame with the unified schema, sorted by date (newest first).
    """
    all_reviews = app_store_reviews + google_play_reviews

    if not all_reviews:
        logger.warning("No reviews received from either source.")
        return pd.DataFrame(columns=[
            "review_id", "date", "source", "rating", "text", "app_version", "product"
        ])

    df = pd.DataFrame(all_reviews)

    # --- Validate required fields ---
    initial_count = len(df)

    # Drop rows missing required fields
    required = ["review_id", "text", "rating"]
    for col in required:
        if col in df.columns:
            df = df.dropna(subset=[col])
    # Filter for >5 words and English language
    before_filter = len(df)
    df = df[df["text"].apply(_is_valid_review)]
    
    dropped = initial_count - len(df)
    if dropped:
        logger.info("Dropped %d reviews (missing fields, < 6 words, or non-English).", dropped)

    # --- Clamp ratings to 1–5 ---
    df["rating"] = df["rating"].clip(1, 5).astype(int)

    # --- De-duplicate by review_id ---
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["review_id"], keep="first")
    dupes = before_dedup - len(df)
    if dupes:
        logger.info("Removed %d duplicate reviews.", dupes)

    # --- Filter by date window ---
    cutoff = datetime.now(timezone.utc) - timedelta(weeks=weeks)
    if "date" in df.columns:
        # Keep reviews with a valid date within the window, plus those with no date
        has_date = df["date"].notna()
        in_window = df["date"] >= cutoff
        df = df[~has_date | in_window]
        filtered_out = before_dedup - dupes - len(df)
        if filtered_out > 0:
            logger.info(
                "Filtered out %d reviews older than %d weeks.", filtered_out, weeks
            )

    # --- Sort by date descending ---
    df = df.sort_values("date", ascending=False, na_position="last")
    df = df.reset_index(drop=True)

    logger.info(
        "Normalised %d reviews (App Store: %d, Google Play: %d).",
        len(df),
        len(df[df["source"] == "app_store"]),
        len(df[df["source"] == "google_play"]),
    )

    return df
