# Phase 1 — Evaluation Checklist

## Functional Tests

### CLI Interface
- [ ] `python -m pulse run --product groww --weeks 8` executes without errors.
- [ ] `python -m pulse run --product groww --iso-week 2026-W17` triggers a backfill for that specific week.
- [ ] Invalid product name prints a clear error and exits with non-zero code.
- [ ] Missing required arguments print usage help.

### App Store Fetcher
- [ ] Returns ≥ 1 review for each of the 5 supported products.
- [ ] All returned reviews have non-empty `text`, valid `date`, and a `rating` between 1-5.
- [ ] Handles HTTP 429 / 5xx gracefully (retry or clear error message).

### Google Play Fetcher
- [ ] Returns ≥ 1 review for each of the 5 supported products.
- [ ] Correctly maps product names to Google Play app IDs.
- [ ] Reviews include `date`, `rating`, `text`, and `app_version`.

### Normalizer
- [ ] Output DataFrame has exactly these columns: `review_id, date, source, rating, text, app_version, product`.
- [ ] No duplicate `review_id` values in the merged output.
- [ ] `source` column contains only `"app_store"` or `"google_play"`.
- [ ] `date` column is parsed into proper datetime objects.

### SQLite State Store
- [ ] `pulse_state.db` is created on first run in the `data/` directory.
- [ ] `is_already_delivered("groww", "2026-W17")` returns `False` before any run.
- [ ] After `record_run("groww", "2026-W17", "delivered", ...)`, `is_already_delivered()` returns `True`.
- [ ] Database survives process restarts (persistent file).

## Performance
- [ ] Ingestion for a single product completes in < 60 seconds.
- [ ] Combined fetch for all 5 products completes in < 5 minutes.

## Regression
- [ ] Run the full Phase 1 flow 3 times in sequence. No crashes, no data corruption.
