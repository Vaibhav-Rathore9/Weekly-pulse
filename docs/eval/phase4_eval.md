# Phase 4 — Evaluation Checklist

## Functional Tests

### Agent Pipeline
- [ ] `python -m pulse run --product groww --weeks 8 --dry-run` completes successfully.
- [ ] Produces a Markdown file in `data/output/{product}_{iso_week}_report.md`.
- [ ] Produces an HTML file in `data/output/{product}_{iso_week}_email.html`.
- [ ] Output files match expected format from Phase 3 eval.
- [ ] Pipeline chains correctly: Ingest → PII Scrub → Embed → Cluster → LLM → Validate → Render.

### Idempotency
- [ ] First run for `(groww, 2026-W17)` completes fully.
- [ ] Second run for `(groww, 2026-W17)` is skipped with a log message: "Already delivered for groww / 2026-W17. Skipping."
- [ ] `--force` flag overrides the idempotency check and re-runs.
- [ ] Different products for the same week run independently.
- [ ] Different weeks for the same product run independently.

### Dry-Run Mode
- [ ] `--dry-run` flag writes output to `data/output/` and does NOT attempt MCP delivery.
- [ ] Dry-run still records the run in SQLite with `status=dry_run` (not `delivered`).
- [ ] A subsequent non-dry-run for the same week is NOT blocked by a prior dry-run.

### Logging & Auditing
- [ ] Console output shows: product, ISO week, review count, theme count, validation rate, token usage, wall-clock time.
- [ ] Logs are also written to `data/logs/{product}_{iso_week}_{timestamp}.log`.
- [ ] Log files persist across runs.
- [ ] Error cases produce ERROR-level log entries with stack traces.

### Config Management
- [ ] `config.yaml` is loaded on startup.
- [ ] Changing `review_window` in config changes the date range fetched.
- [ ] Changing `token_budget` in config affects the LLM processing cap.
- [ ] Missing config file raises a clear error: "config.yaml not found."
- [ ] Invalid config values (e.g., `review_window: -1`) are caught during validation.

## Integration Tests
- [ ] Run the full pipeline for all 5 supported products in sequence. No crashes.
- [ ] Run 3 products in quick succession. SQLite handles concurrent writes correctly.

## Performance
- [ ] End-to-end dry-run for a single product completes in < 5 minutes.
