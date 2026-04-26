# Phase 3 — Evaluation Checklist

## Functional Tests

### Docs Renderer
- [ ] Output starts with an H2 heading: `## {Product} — Weekly Review Pulse — {ISO_Week}`.
- [ ] Contains a "Top Themes" section listing all themes with descriptions.
- [ ] Contains a "Real User Quotes" section with ≥ 1 validated quote per theme (where available).
- [ ] Contains an "Action Ideas" section with one idea per theme.
- [ ] Contains a "What This Solves" footer section.
- [ ] Output is valid Markdown (parseable by a Markdown parser without errors).
- [ ] Matches the sample output format in `ProblemStatement.md` (lines 54-69).

### Email Renderer
- [ ] HTML output contains a `<subject>` or subject is returned separately.
- [ ] Subject line format: `Weekly Review Pulse — {Product} — {ISO_Week}`.
- [ ] Body contains top 3 themes as bullet points.
- [ ] Body contains a "Read full report →" hyperlink.
- [ ] Hyperlink placeholder is formatted as `https://docs.google.com/document/d/{DOC_ID}#heading={ANCHOR}`.
- [ ] Plain-text fallback is included alongside HTML.
- [ ] HTML renders correctly when opened in a browser (no broken tags).

### Template Engine
- [ ] Jinja2 templates exist in `src/templates/` for both Docs and Email.
- [ ] Templates are separate from Python logic (no inline HTML strings).
- [ ] Changing a template does not require code changes.

## Determinism
- [ ] Running the Docs Renderer twice with the same input JSON produces byte-identical output.
- [ ] Running the Email Renderer twice with the same input JSON produces byte-identical output.

## Formatting
- [ ] No raw JSON or debugging artifacts in the rendered output.
- [ ] Quotes are wrapped in quotation marks.
- [ ] Markdown heading levels are consistent (H2 for title, H3 for sections).
