# Phase 2 — Evaluation Checklist

## Functional Tests

### PII Scrubber
- [ ] Redacts phone numbers in formats: `+91-9876543210`, `(555) 123-4567`, `9876543210`.
- [ ] Redacts email addresses: `user@example.com`, `user+tag@domain.co.in`.
- [ ] Redacts URLs: `https://example.com/path`.
- [ ] Preserves the rest of the review text unchanged.
- [ ] Returns a PII report: `{ emails_found: N, phones_found: N, urls_found: N }`.

### Embedder
- [ ] Produces a numpy array of shape `(n_reviews, embedding_dim)`.
- [ ] Embedding dimension matches the configured model (e.g., 1536 for `text-embedding-3-small`).
- [ ] Handles batch sizes correctly (e.g., batches of 100 for API calls).
- [ ] Empty or very short texts (< 3 words) produce valid embeddings without error.
- [ ] API failures are retried (max 2 retries).

### Clusterer
- [ ] Returns cluster labels as an integer array of length `n_reviews`.
- [ ] Noise reviews are labeled `-1`.
- [ ] With ≥ 50 diverse reviews, produces ≥ 2 distinct clusters.
- [ ] Cluster sizes are reasonable (no single cluster containing > 80% of reviews).

### LLM Engine
- [ ] For each cluster, returns a JSON object matching the schema: `{ name, quotes, action_idea }`.
- [ ] `name` is ≤ 6 words.
- [ ] `quotes` contains 2-3 items.
- [ ] `action_idea` is a single actionable sentence.
- [ ] Total token usage per run is logged and stays within the configured budget.

### Quote Validator
- [ ] Validates that each quote is a literal substring of a review in the cluster.
- [ ] Comparison is case-insensitive and whitespace-normalised.
- [ ] Invalid quotes are discarded.
- [ ] If > 50% of quotes fail, triggers one retry with a stricter prompt.
- [ ] Overall validation pass rate is ≥ 80%.

### End-to-End Pipeline
- [ ] `process_reviews(normalised_df)` returns a valid JSON matching the full schema.
- [ ] The JSON contains ≥ 2 themes with validated quotes and action ideas.
- [ ] No PII appears in any quote or theme name.

## Performance
- [ ] Full processing pipeline (PII → Embed → Cluster → LLM → Validate) completes in < 3 minutes for 500 reviews.
- [ ] Token usage is logged and does not exceed the per-run budget.
