# Phase 1 — Edge Cases & Failure Modes

## Ingestion

### App Store RSS
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 1 | **RSS feed returns 0 reviews** (new/obscure app) | Log a warning, return empty DataFrame, do not crash. Continue with Google Play data only. |
| 2 | **RSS feed URL changes or returns 404** | Raise a clear `IngestionError` with the URL. Do not silently proceed with stale data. |
| 3 | **RSS feed returns malformed XML/JSON** | Catch parse errors, log the raw response (truncated), raise `IngestionError`. |
| 4 | **Rate limiting (HTTP 429)** | Retry with exponential backoff (max 3 retries, max wait 30s). Fail after exhaustion. |
| 5 | **Network timeout** | Set a 15s timeout. Retry once. Log the failure. |
| 6 | **Reviews in non-English languages** | Ingest as-is. Language filtering is out of scope for Phase 1 but the field should be preserved if available. |

### Google Play Scraper
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 7 | **App ID not found / invalid** | `google-play-scraper` raises an exception. Catch it, log the product + app ID, and raise `IngestionError`. |
| 8 | **Scraper returns reviews outside the requested date window** | Filter reviews by date after fetch. Only keep reviews within the configured window (e.g. last 8 weeks). |
| 9 | **Scraper blocked by Google (CAPTCHA / IP ban)** | Log the error. Consider documenting proxy/rotation as a future enhancement. Fail gracefully. |
| 10 | **Extremely long review text (>5000 chars)** | Truncate to 2000 characters during normalisation. Log truncation. |
| 11 | **Reviews with only a star rating and no text** | Discard text-less reviews during normalisation. Log the count discarded. |

## Normalizer
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 12 | **Duplicate review IDs across sources** | Should not happen (IDs are source-prefixed), but if it does, keep the first occurrence and log. |
| 13 | **Missing fields (e.g., `app_version` is null)** | Allow nulls for optional fields (`app_version`). Required fields (`review_id`, `text`, `date`, `rating`) must be present or the row is dropped. |
| 14 | **Date parsing failures** | If a date string cannot be parsed, set to `None` and log. Do not drop the review — dates are useful but not critical for clustering. |

## CLI
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 15 | **User passes `--weeks 0` or negative** | Validate input. Print error: "Weeks must be between 1 and 52." |
| 16 | **User passes a future ISO week** | Allow it (reviews won't exist yet), but warn: "No reviews found for future week." |
| 17 | **Concurrent runs for the same product+week** | SQLite file-level locking should prevent corruption. Second process should wait or fail with a clear lock error. |

## State Store
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 18 | **`pulse_state.db` is deleted between runs** | Recreate the database and tables on startup. Warn that history is lost. |
| 19 | **Disk full — cannot write to SQLite** | Catch `sqlite3.OperationalError`, log, and exit with non-zero code. |
