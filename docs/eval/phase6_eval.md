# Phase 6 — Evaluation Checklist

## Functional Tests

### MCP Client
- [ ] Agent connects to `https://saksham-mcp-server.onrender.com/` on startup.
- [ ] `tools/list` is called and available tools are logged.
- [ ] Connection handles Render cold-start delay (up to 90s timeout).

### Google Docs Integration
- [ ] Agent appends a new section to the correct Google Doc for the product.
- [ ] The appended section heading matches: `## {Product} — Weekly Review Pulse — {ISO_Week}`.
- [ ] Content includes themes, quotes, action ideas, and footer.
- [ ] The heading anchor/ID is captured from the MCP response for use in the email deep link.

### Gmail Integration
- [ ] Agent sends an email to the configured stakeholder addresses.
- [ ] Subject line: `Weekly Review Pulse — {Product} — {ISO_Week}`.
- [ ] Body contains top themes as bullets.
- [ ] Body contains a working "Read full report →" deep link to the Doc section.
- [ ] Email is received by all stakeholders.

### Idempotency (End-to-End)
- [ ] First run: Doc section created + email sent + SQLite records `status=delivered`.
- [ ] Second run: Skipped with log message. No duplicate Doc section. No duplicate email.
- [ ] `--force` run: Overwrites existing section. Sends new email. Updates SQLite.

### Error Handling
- [ ] MCP call failure → retry 2x with backoff → record `status=failed` → exit non-zero.
- [ ] Partial failure (Docs succeeds, Gmail fails) → record `status=partial` → next run retries only Gmail.

## End-to-End Smoke Test
- [ ] `python -m pulse run --product groww --weeks 8` → Doc updated + email received.
- [ ] Repeat for at least 2 other products.
- [ ] Backfill: `python -m pulse run --product groww --iso-week 2026-W15` → correct historical data.
