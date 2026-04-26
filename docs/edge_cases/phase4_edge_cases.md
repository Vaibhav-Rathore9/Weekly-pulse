# Phase 4 — Edge Cases & Failure Modes

## Agent Pipeline
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 1 | **Ingestion returns 0 reviews for a product** | Log: "No reviews found for {product}. Skipping." Exit 0. Do not run clustering or LLM. Do not record as "delivered". |
| 2 | **Ingestion returns reviews from only one source** (e.g., App Store down) | Proceed with available reviews. Log a warning: "Only {source} reviews available." |
| 3 | **Processing pipeline fails mid-way** (e.g., LLM API down) | Catch the exception. Record `status=failed` in SQLite. Log the error. Exit with non-zero code. |
| 4 | **Pipeline produces 0 themes** (all reviews are noise) | Use the fallback single-cluster approach from Phase 2. If that also fails, render a "No themes identified" report. |
| 5 | **Rendering fails** (e.g., template error) | Catch the exception. Record `status=failed`. Do not attempt delivery. |

## Idempotency
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 6 | **Process crashes after ingestion but before recording the run** | On restart, `is_already_delivered()` returns `False`. The run is retried from scratch. This is safe because ingestion is read-only. |
| 7 | **Process crashes after MCP delivery but before recording** (Phase 6) | This is the dangerous case. The Doc/email may exist but state says "not delivered". Mitigation: query the Doc for the heading anchor before appending. If it exists, skip append and just record. |
| 8 | **SQLite database is corrupted** | On startup, run an integrity check. If corruption detected, rename the file and create a new DB. Log a CRITICAL warning about lost history. |
| 9 | **`--force` flag used on a production run** | Allow it, but log a WARNING: "Force re-run requested. This may create duplicate content if delivery was partially completed." |

## Dry-Run
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 10 | **`data/output/` directory does not exist** | Create it automatically. |
| 11 | **File already exists for the same product+week** | Overwrite the file. Log: "Overwriting existing dry-run output." |
| 12 | **Disk full — cannot write output files** | Catch `IOError`. Log the error. Exit with non-zero code. |

## Config
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 13 | **Config file is valid YAML but missing required keys** | Validate on load. Raise `ConfigurationError` with the missing key name. |
| 14 | **Config file has an unsupported product name** | Warn but do not crash. Only process products that have valid app IDs configured. |
| 15 | **Environment variable overrides config file value** | Support `PULSE_LLM_API_KEY`, `PULSE_TOKEN_BUDGET`, etc. Environment variables take precedence over config file. |

## Logging
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 16 | **Log directory does not exist** | Create `data/logs/` automatically. |
| 17 | **Log file grows very large** (many backfill runs) | Each run creates a new log file. Individual files should not grow unbounded. |
