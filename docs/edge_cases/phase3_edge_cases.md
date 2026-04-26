# Phase 3 — Edge Cases & Failure Modes

## Docs Renderer
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 1 | **Zero themes in the input JSON** | Render a section with the heading and a note: "No significant themes identified for this period." Do not crash. |
| 2 | **Theme with zero validated quotes** | Render the theme with its name and action idea, but omit the quotes sub-section for that theme. Add a note: "No verbatim quotes available." |
| 3 | **Quote text contains Markdown special characters** (`*`, `_`, `#`, `|`) | Escape special characters to prevent rendering artifacts. |
| 4 | **Extremely long theme name (> 100 chars)** | Truncate to 80 chars with `...`. This should rarely happen if the LLM engine is well-prompted. |
| 5 | **Product name contains special characters** | Sanitise product name in the heading. Only allow alphanumeric, spaces, and hyphens. |
| 6 | **Unicode characters in quotes** (emojis, non-Latin scripts) | Render as-is. Markdown supports unicode. |

## Email Renderer
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 7 | **Doc ID is not yet known** (Phase 3 runs before Phase 6 integration) | Use a placeholder: `[DOC_LINK_PLACEHOLDER]`. The delivery module replaces this at send time. |
| 8 | **Heading anchor contains spaces or special characters** | URL-encode the anchor in the deep link. |
| 9 | **Email HTML exceeds Gmail size limit (25 MB)** | Extremely unlikely for a text-based summary. But if it does, truncate themes to top 5 and add a "See full report in Docs" note. |
| 10 | **Plain-text fallback is missing** | Always generate both HTML and plain-text. If template rendering fails for one format, log and use the other as fallback. |

## Template Engine
| # | Edge Case | Expected Behavior |
|---|-----------|-------------------|
| 11 | **Jinja2 template file is missing** | Raise `FileNotFoundError` with the expected template path. Do not fall back to a hardcoded string. |
| 12 | **Template has a syntax error** | Jinja2 raises `TemplateSyntaxError`. Catch and log with the template file name and line number. |
| 13 | **Input JSON has unexpected/extra fields** | Templates should only reference known fields. Extra fields are ignored. Missing fields should use Jinja2 defaults (`| default('')`). |
