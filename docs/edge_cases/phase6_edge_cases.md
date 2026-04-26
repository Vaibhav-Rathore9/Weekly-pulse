# Phase 6 — Edge Cases & Failure Modes

## MCP Client
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 1 | **MCP server is unreachable** | Retry 2x with exponential backoff (5s, 15s). If all fail, record `status=failed` and exit non-zero. |
| 2 | **MCP `tools/list` returns unexpected tool names** | Log the available tools. If the expected Docs/Gmail tools are missing, raise `ConfigurationError`. |
| 3 | **SSE transport drops mid-stream** | Detect connection drop. Retry the specific tool call (not the entire pipeline). |

## Google Docs
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 4 | **Document ID in config is invalid or deleted** | MCP tool returns a 404. Log the error with the Doc ID. Record `status=failed`. |
| 5 | **Agent lacks edit permissions on the Doc** | MCP tool returns a 403. Log: "Permission denied for Doc {DOC_ID}. Ensure the MCP server's Google account has edit access." |
| 6 | **Heading anchor already exists** (crash-recovery scenario) | Before appending, query the Doc for the heading. If found, skip append and proceed to Gmail. Record the existing heading anchor. |
| 7 | **Doc content exceeds Google Docs size limit** (after many weeks) | Unlikely for text-only reports. If it happens, create a new Doc for the product and update `config.yaml`. |
| 8 | **Markdown-to-Docs conversion loses formatting** | Test with bold, bullets, and headings. Adjust the MCP tool input format if needed (some servers expect raw text, others HTML). |

## Gmail
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 9 | **Stakeholder email address is invalid** | Gmail API returns a bounce/error. Log the invalid address. Send to remaining valid addresses. |
| 10 | **Email sent but deep link is broken** (wrong anchor) | Verify the anchor by constructing the URL from the Docs MCP response. Log the full URL for debugging. |
| 11 | **Gmail send quota exceeded** (500/day for workspace, 100/day for free) | Log a quota error. Record `status=partial`. Retry on the next scheduled run. |
| 12 | **Draft mode vs. send mode** | In staging, default to `gmail_create_draft`. Only use `gmail_send` in production. Control via `config.yaml` flag: `email_mode: draft | send`. |

## Idempotency (Cross-System)
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 13 | **Doc appended but email not sent** (partial delivery) | Record `status=partial` with `doc_heading` filled and `message_id` null. Next run detects partial status and retries only the Gmail step. |
| 14 | **Email sent but Doc append failed** (unlikely ordering) | Record `status=partial` with `message_id` filled and `doc_heading` null. Next run retries only the Docs step. |
| 15 | **Agent records "delivered" but the Doc section was manually deleted** | The system trusts its local state. A manual `--force` run would be needed to re-append. Consider adding a `--verify` flag that checks the Doc before skipping. |
