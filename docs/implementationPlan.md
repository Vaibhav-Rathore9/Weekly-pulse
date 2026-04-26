# Implementation Plan — Weekly Product Review Pulse AI Agent

This document is the phased execution blueprint for the Weekly Product Review Pulse system. Each phase maps directly to the component design in `docs/architecture.md`, includes concrete deliverables, dependencies, exit criteria, and references to the companion `eval/` and `edge_cases/` documents.

---

## Phase 1: Project Foundation & Review Ingestion

> **Architecture ref**: §2.1 AI Agent Orchestrator (CLI + State), §2.2 Ingestion Module

### Objective
Stand up the project skeleton, CLI entry point, SQLite state store, and both review-fetching adapters so that a single command returns a normalised DataFrame of reviews for any supported product.

### Deliverables

| # | Deliverable | Detail |
|---|-------------|--------|
| 1 | **Project scaffold** | `pyproject.toml` (or `requirements.txt`), folder layout (`src/`, `tests/`, `docs/`, `data/`), `.env.example` for API keys. |
| 2 | **CLI** | `python -m pulse run --product groww --weeks 8` and `--iso-week 2026-W17` backfill flag. Uses `click` or `argparse`. |
| 3 | **SQLite state store** | `pulse_state.db` with a `runs` table: `(product, iso_week, status, started_at, completed_at, doc_heading, message_id)`. Helper functions: `is_already_delivered()`, `record_run()`. |
| 4 | **App Store Fetcher** | Fetch reviews from Apple's iTunes RSS JSON endpoint. Handle pagination, empty feeds, and HTTP errors. |
| 5 | **Google Play Fetcher** | Fetch reviews using `google-play-scraper`. Handle country codes, language, pagination, and rate-limiting. |
| 6 | **Normalizer** | Merge both sources into a unified `reviews` DataFrame with schema: `[review_id, date, source, rating, text, app_version, product]`. De-duplicate by `review_id`. |

### Dependencies
- `requests`, `google-play-scraper`, `pandas`, `click`

### Exit Criteria
- `python -m pulse run --product groww --weeks 8` prints a summary table of fetched reviews (count, date range, source split).
- All 5 supported products return non-empty normalised review sets.
- SQLite database is created and `is_already_delivered()` correctly returns `False` for new runs and `True` for recorded ones.

### Companion Files
- [`docs/eval/phase1_eval.md`](./eval/phase1_eval.md) — Evaluation checklist
- [`docs/edge_cases/phase1_edge_cases.md`](./edge_cases/phase1_edge_cases.md) — Edge cases & failure modes

---

## Phase 2: Processing Pipeline (PII Scrub → Embed → Cluster → LLM Reasoning)

> **Architecture ref**: §2.3 Processing & Reasoning Module

### Objective
Build the analytical core: PII scrubbing, embedding, clustering, LLM theme extraction, and quote validation. Output is a structured JSON of themes, validated quotes, and action ideas.

### Deliverables

| # | Deliverable | Detail |
|---|-------------|--------|
| 1 | **PII Scrubber** | Regex patterns for phone numbers, emails, URLs. Optional: lightweight `presidio` or `spaCy` NER for names. Returns scrubbed text + PII report. |
| 2 | **Embedder** | Vectorise scrubbed reviews using OpenAI `text-embedding-3-small` (or configurable provider via `litellm`). Batch API calls, cache embeddings locally. |
| 3 | **Clusterer** | UMAP (n_components=5, metric=cosine) → HDBSCAN (min_cluster_size=5). Returns cluster labels + noise label (-1). |
| 4 | **LLM Engine** | Per-cluster prompt: "Given these reviews, name the theme in ≤6 words, extract 2-3 verbatim quotes, and suggest one action idea." Uses `litellm` for provider-agnostic calls. Token budget capped per run. |
| 5 | **Quote Validator** | For each quote returned by the LLM, assert `quote in original_review_text` (case-insensitive, whitespace-normalised). Discard failures; retry once with stricter prompt if >50% fail. |
| 6 | **Structured output** | JSON schema: `{ themes: [{ name, quotes: [{ text, review_id }], action_idea, review_count }] }`. |

### Dependencies
- Phase 1 complete (normalised reviews available).
- `umap-learn`, `hdbscan`, `litellm`, `numpy`, `scikit-learn`
- LLM API key (OpenAI / Gemini / Claude) in `.env`.

### Exit Criteria
- Pipeline takes ≥50 reviews and outputs ≥2 themes with validated quotes.
- Quote validation pass rate ≥ 80%.
- PII scrubber removes 100% of synthetic PII injected into test data.
- Entire pipeline completes within a configurable token budget.

### Companion Files
- [`docs/eval/phase2_eval.md`](./eval/phase2_eval.md)
- [`docs/edge_cases/phase2_edge_cases.md`](./edge_cases/phase2_edge_cases.md)

---

## Phase 3: Report Rendering

> **Architecture ref**: §2.4 Rendering Module

### Objective
Transform the structured JSON output from Phase 2 into two delivery-ready formats: a Markdown section (for Google Docs append) and an HTML/Text email (for Gmail).

### Deliverables

| # | Deliverable | Detail |
|---|-------------|--------|
| 1 | **Docs Renderer** | Generates Markdown with: H2 heading (`## Groww — Weekly Review Pulse — 2026-W17`), "Top Themes" section, "Real User Quotes" section, "Action Ideas" section, "What This Solves" footer. Heading serves as the stable anchor for idempotency & deep linking. |
| 2 | **Email Renderer** | HTML email with: subject line, top 3 themes as bullets, a `Read full report →` hyperlink pointing to `https://docs.google.com/document/d/{DOC_ID}#heading=...`, and plain-text fallback. |
| 3 | **Template engine** | Use Jinja2 templates stored in `src/templates/` for both renderers. Separates content logic from presentation. |

### Dependencies
- Phase 2 complete (structured JSON available).
- `jinja2`

### Exit Criteria
- Docs Renderer output matches the sample format in `ProblemStatement.md` line-by-line.
- Email Renderer produces valid HTML that renders correctly in a browser preview.
- Both renderers are deterministic: same JSON input → identical output.

### Companion Files
- [`docs/eval/phase3_eval.md`](./eval/phase3_eval.md)
- [`docs/edge_cases/phase3_edge_cases.md`](./edge_cases/phase3_edge_cases.md)

---

## Phase 4: AI Agent Orchestration & Auditing

> **Architecture ref**: §2.1 AI Agent Orchestrator (full integration)

### Objective
Wire Phase 1–3 into a single agent execution flow with idempotency enforcement, structured logging, and dry-run mode. At the end of this phase, the system runs end-to-end locally and produces the correct artifacts (without actual MCP delivery).

### Deliverables

| # | Deliverable | Detail |
|---|-------------|--------|
| 1 | **Agent pipeline** | Single `run_pulse(product, iso_week)` function that chains: idempotency check → ingest → process → render → (delivery placeholder) → record run. |
| 2 | **Idempotency gate** | Before ingestion, query SQLite. If `(product, iso_week)` has `status=delivered`, log a skip message and exit 0. |
| 3 | **Dry-run mode** | `--dry-run` flag writes rendered Markdown and HTML to `data/output/` instead of invoking MCP delivery. |
| 4 | **Structured logging** | Each run logs: product, ISO week, review count, theme count, quote validation rate, token usage, wall-clock time. Logs written to both console and `data/logs/`. |
| 5 | **Config management** | `config.yaml` for per-product settings: app IDs, Doc IDs, stakeholder emails, review window, token budgets. |

### Dependencies
- Phases 1–3 complete.
- `pyyaml` for config.

### Exit Criteria
- `python -m pulse run --product groww --weeks 8 --dry-run` produces correct Markdown + HTML files in `data/output/`.
- Re-running the same command with `--dry-run` skips execution (idempotency).
- Logs contain all required audit fields.
- Config changes (e.g., review window) are reflected without code changes.

### Companion Files
- [`docs/eval/phase4_eval.md`](./eval/phase4_eval.md)
- [`docs/edge_cases/phase4_edge_cases.md`](./edge_cases/phase4_edge_cases.md)

---

## Phase 5: MCP Server Deployment on Render

> **Architecture ref**: §2.5 Delivery via Agent Tool-Use (server side)

### Objective
Deploy the `saksham-mcp-server` on Render so it is live and authenticated against Google Workspace, ready to accept tool calls from the AI agent.

### Steps

| # | Step | Detail |
|---|------|--------|
| 1 | **Clone** | `git clone https://github.com/saksham20189575/saksham-mcp-server` |
| 2 | **Deploy on Render** | Create a Render account (GitHub SSO). Use **New → Blueprint** and point to the cloned repo. |
| 3 | **Generate `credentials.json`** | From Google Cloud Console: enable Docs + Gmail APIs, create OAuth 2.0 Client ID, download `credentials.json`. |
| 4 | **Generate `token.json`** | Run the MCP server locally (`npm start` or equivalent), complete the OAuth consent flow in browser, which writes `token.json`. |
| 5 | **Upload secrets to Render** | Add `credentials.json` and `token.json` content as Render environment variables (or secret files). |
| 6 | **Verify deployment** | Confirm server is live at `https://saksham-mcp-server.onrender.com/` and responds to an MCP `tools/list` request. |

### Dependencies
- Google Cloud project with Docs + Gmail API enabled.
- A Google account whose mailbox and Drive will be used.

### Exit Criteria
- `https://saksham-mcp-server.onrender.com/` returns a valid MCP response.
- `tools/list` returns at least the Docs append and Gmail send tools.
- A manual test call to the Docs tool successfully creates/appends to a test document.

### Companion Files
- [`docs/eval/phase5_eval.md`](./eval/phase5_eval.md)
- [`docs/edge_cases/phase5_edge_cases.md`](./edge_cases/phase5_edge_cases.md)

---

## Phase 6: MCP Delivery Integration & End-to-End

> **Architecture ref**: §2.5 Delivery via Agent Tool-Use (client side)

### Objective
Connect the AI agent to the deployed MCP server, replacing the dry-run placeholder with real tool invocations. Achieve full end-to-end: CLI → Ingest → Process → Render → Append to Google Doc → Send Gmail.

### Deliverables

| # | Deliverable | Detail |
|---|-------------|--------|
| 1 | **MCP Client** | Use Python `mcp` SDK to connect to `https://saksham-mcp-server.onrender.com/` via SSE transport. Fetch tools on startup. |
| 2 | **Docs Appender integration** | Agent invokes the Docs tool with: `{ document_id, content (rendered Markdown), heading }`. On success, extract the heading anchor for the email deep link. |
| 3 | **Gmail Sender integration** | Agent invokes the Gmail tool with: `{ to, subject, html_body, text_body }`. The HTML body includes the deep link from step 2. |
| 4 | **Idempotency finalisation** | After successful MCP delivery, record `(product, iso_week, status=delivered, doc_heading, message_id)` in SQLite. |
| 5 | **Error handling & retry** | If MCP call fails: retry up to 2 times with exponential backoff. If still failing, record `status=failed` and alert via logs. |

### Dependencies
- Phase 4 complete (end-to-end dry-run works).
- Phase 5 complete (MCP server is live).
- `mcp` Python SDK.

### Exit Criteria
- `python -m pulse run --product groww --weeks 8` (without `--dry-run`) appends a section to the correct Google Doc.
- Stakeholder email is received with a working deep link to the Doc section.
- Re-running the same command is blocked by the idempotency gate (no duplicate Doc section, no duplicate email).
- A forced re-run (`--force`) overwrites the existing section cleanly.

### Companion Files
- [`docs/eval/phase6_eval.md`](./eval/phase6_eval.md)
- [`docs/edge_cases/phase6_edge_cases.md`](./edge_cases/phase6_edge_cases.md)

---

## Phase Dependency Graph

```
Phase 1 (Foundation & Ingestion)
    │
    ▼
Phase 2 (Processing Pipeline)
    │
    ▼
Phase 3 (Rendering)
    │
    ▼
Phase 4 (Orchestration & Auditing)
    │                  ╲
    ▼                    ▼
Phase 5 (MCP Deploy)   (can run in parallel)
    │                  ╱
    ▼
Phase 6 (Delivery Integration)
```
