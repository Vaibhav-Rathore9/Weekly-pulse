"""
Google Play Fetcher — retrieves Groww reviews using the google-play-scraper library.

The library returns reviews with fields like:
  reviewId, content, score, at, appVersion, ...

We normalise these into the unified review schema.
"""

import logging
import time
from datetime import datetime, timezone

from google_play_scraper import Sort, reviews

from ..config import GROWW_PLAY_STORE_ID

logger = logging.getLogger(__name__)

_MAX_REVIEWS = 500       # safety cap per fetch
_BATCH_SIZE = 100        # reviews per API call
_RETRY_COUNT = 3
_RETRY_BACKOFF = 3       # seconds


def fetch_google_play_reviews(count: int = _MAX_REVIEWS) -> list[dict]:
    """
    Fetch Groww reviews from Google Play Store.

    Args:
        count: Maximum number of reviews to fetch (default 500).

    Returns:
        A list of normalised review dicts.
    """
    all_reviews: list[dict] = []
    continuation_token = None

    fetched = 0
    batch_num = 0

    while fetched < count:
        batch_num += 1
        batch_size = min(_BATCH_SIZE, count - fetched)

        for attempt in range(1, _RETRY_COUNT + 1):
            try:
                logger.info(
                    "Fetching Google Play batch %d (%d reviews) …",
                    batch_num, batch_size,
                )
                result, continuation_token = reviews(
                    GROWW_PLAY_STORE_ID,
                    lang="en",
                    country="in",
                    sort=Sort.NEWEST,
                    count=batch_size,
                    continuation_token=continuation_token,
                )
                break  # success
            except Exception as e:
                wait = _RETRY_BACKOFF * (2 ** (attempt - 1))
                logger.warning(
                    "Google Play error (batch %d, attempt %d/%d): %s — retrying in %ds",
                    batch_num, attempt, _RETRY_COUNT, e, wait,
                )
                time.sleep(wait)
                if attempt == _RETRY_COUNT:
                    logger.error(
                        "Exhausted retries for Google Play batch %d. "
                        "Returning %d reviews collected so far.",
                        batch_num, len(all_reviews),
                    )
                    return all_reviews

        if not result:
            logger.info("No more Google Play reviews available.")
            break

        for r in result:
            text = (r.get("content") or "").strip()
            if not text:
                continue  # skip text-less reviews

            # Truncate extremely long reviews
            if len(text) > 2000:
                logger.debug("Truncating review %s (len=%d)", r.get("reviewId"), len(text))
                text = text[:2000] + "…"

            review_date = r.get("at")
            if isinstance(review_date, datetime):
                # Ensure timezone-aware
                if review_date.tzinfo is None:
                    review_date = review_date.replace(tzinfo=timezone.utc)
            else:
                review_date = None

            all_reviews.append({
                "review_id": f"gplay_{r.get('reviewId', '')}",
                "date": review_date,
                "source": "google_play",
                "rating": r.get("score", 0),
                "text": text,
                "app_version": r.get("appVersion") or None,
                "product": "groww",
            })

        fetched += len(result)

        if continuation_token is None:
            break

        # Polite delay between batches
        time.sleep(1.0)

    logger.info("Google Play: fetched %d reviews total.", len(all_reviews))
    return all_reviews
