# Review - bug mode

- source: src/install/catalog.ts
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: contextTokens field + grounded values on six brains;
  isCatalogBrain helper)
- context pack: every value grounded from the model's own HF card this
  session (Qwen3-4B-2507 262144, Gemma-3-4B 131072, LFM2-8B 32k,
  Qwen2.5-Coder-7B 32768 native config, Nemotron-3-Nano 262144, Qwen3-
  Coder-30B 262144); consumers ScreenStage picker + brainProviders.test.

## Verdict

Shippable. Optional field, grounded values pinned by test, and the
embedder/reranker exclusion is derived from the roles the catalog already
speaks.

## Bugs & vulnerabilities

None CONFIRMED. Traced: isCatalogBrain excludes by role substring
(embeddings/rerank) - matches exactly the two knowledge-store entries;
every brain-seat entry carries a ceiling (test-enforced, so a future
catalog addition without a ceiling fails loudly).

## Missing safeguards

- The values are ceilings; the sidecar serves 16k regardless - the
  comment and the picker hint both say so.
