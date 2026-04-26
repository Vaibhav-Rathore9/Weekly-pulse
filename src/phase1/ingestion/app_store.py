"""
App Store Fetcher -- retrieves Groww reviews from Apple's App Store.

Strategy (in order of priority):
  1. Apple's iTunes RSS JSON endpoint (fastest, but often returns 0 for Indian apps).
  2. app_store_scraper library (uses Apple's internal API, sometimes blocked).
  3. If both fail, return [] and log a warning -- Google Play will be the primary source.

This is a known limitation documented in edge_cases/phase1_edge_cases.md (#1, #2).
"""

import logging
import time
from datetime import datetime, timezone

import requests

from ..config import GROWW_APP_STORE_ID

logger = logging.getLogger(__name__)

# --- RSS approach ---
_RSS_URL = (
    "https://itunes.apple.com/in/rss/customerreviews"
    "/page={page}/id={app_id}/sortBy=mostRecent/json"
)
_MAX_PAGES = 10
_REQUEST_TIMEOUT = 15
_RETRY_COUNT = 3
_RETRY_BACKOFF = 2


def _fetch_rss_page(page: int) -> list[dict]:
    """Fetch a single page of the RSS feed and return parsed review dicts."""
    url = _RSS_URL.format(page=page, app_id=GROWW_APP_STORE_ID)

    for attempt in range(1, _RETRY_COUNT + 1):
        try:
            resp = requests.get(url, timeout=_REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            entries = data.get("feed", {}).get("entry", [])
            if not entries:
                return []

            reviews = []
            for entry in entries:
                if "im:rating" not in entry:
                    continue

                review_id = entry.get("id", {}).get("label", "")
                title = entry.get("title", {}).get("label", "")
                content = entry.get("content", {}).get("label", "")
                rating = int(entry.get("im:rating", {}).get("label", "0"))
                version = entry.get("im:version", {}).get("label", "")
                date_str = entry.get("updated", {}).get("label", "")

                review_date = None
                if date_str:
                    try:
                        review_date = datetime.fromisoformat(
                            date_str.replace("Z", "+00:00")
                        )
                    except ValueError:
                        review_date = None

                text = f"{title}. {content}" if title else content

                if text.strip():
                    reviews.append({
                        "review_id": f"appstore_{review_id}",
                        "date": review_date,
                        "source": "app_store",
                        "rating": rating,
                        "text": text.strip(),
                        "app_version": version or None,
                        "product": "groww",
                    })

            return reviews

        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                wait = _RETRY_BACKOFF * (2 ** (attempt - 1))
                logger.warning(
                    "Rate limited on page %d, retrying in %ds (attempt %d/%d)",
                    page, wait, attempt, _RETRY_COUNT,
                )
                time.sleep(wait)
            else:
                logger.error("HTTP error fetching page %d: %s", page, e)
                raise
        except requests.exceptions.RequestException as e:
            wait = _RETRY_BACKOFF * (2 ** (attempt - 1))
            logger.warning(
                "Request error on page %d: %s -- retrying in %ds (%d/%d)",
                page, e, wait, attempt, _RETRY_COUNT,
            )
            time.sleep(wait)

    logger.error("Exhausted retries for RSS page %d", page)
    return []


def _fetch_via_rss() -> list[dict]:
    """Try the RSS approach across multiple pages."""
    all_reviews: list[dict] = []
    for page in range(1, _MAX_PAGES + 1):
        logger.info("Fetching App Store RSS page %d ...", page)
        page_reviews = _fetch_rss_page(page)
        if not page_reviews:
            break
        all_reviews.extend(page_reviews)
        time.sleep(0.5)
    return all_reviews


# --- app_store_scraper approach ---
def _fetch_via_scraper(count: int = 200) -> list[dict]:
    """Try using the app_store_scraper library as a fallback."""
    try:
        from app_store_scraper import AppStore

        app = AppStore(
            country="in",
            app_name="groww-stocks-mutual-fund",
            app_id=int(GROWW_APP_STORE_ID),
        )
        app.review(how_many=count)

        reviews = []
        for r in app.reviews:
            text = (r.get("review") or "").strip()
            if not text:
                continue

            title = (r.get("title") or "").strip()
            if title:
                text = f"{title}. {text}"

            review_date = r.get("date")
            if isinstance(review_date, datetime):
                if review_date.tzinfo is None:
                    review_date = review_date.replace(tzinfo=timezone.utc)
            else:
                review_date = None

            reviews.append({
                "review_id": f"appstore_{r.get('userName', '')}_{hash(text) % 100000}",
                "date": review_date,
                "source": "app_store",
                "rating": r.get("rating", 0),
                "text": text,
                "app_version": r.get("appVersion") or None,
                "product": "groww",
            })

        return reviews

    except ImportError:
        logger.debug("app_store_scraper not installed, skipping fallback.")
        return []
    except Exception as e:
        logger.warning("app_store_scraper failed: %s", e)
        return []


def fetch_app_store_reviews() -> list[dict]:
    """
    Fetch Groww reviews from the Apple App Store.

    Tries RSS first, then falls back to the scraper library.
    Returns an empty list if both fail (Google Play will be primary source).
    """
    # Strategy 1: RSS
    reviews = _fetch_via_rss()
    if reviews:
        logger.info("App Store (RSS): fetched %d reviews.", len(reviews))
        return reviews

    logger.info("App Store RSS returned 0 reviews. Trying scraper fallback ...")

    # Strategy 2: Scraper library
    reviews = _fetch_via_scraper()
    if reviews:
        logger.info("App Store (scraper): fetched %d reviews.", len(reviews))
        return reviews

    # Both failed
    logger.warning(
        "App Store: 0 reviews from both RSS and scraper. "
        "This is a known Apple limitation for some apps/regions. "
        "Proceeding with Google Play data only."
    )
    return []
