# scan b5f5c73ee8f3 (batch batch-1790110702-JEt5xPnHLDRGxNVUeTWx via z-ai/glm-5.3:batch)

**Findings**

1. **tests/test_cast_flow.py:122** (`test_uncertain_dialogue_opens_correct_original_passage`)
   - Trigger: `assert window.controller.book.sentences[wanted].text == book.sentences[wanted].text` — `book` is an alias of `window.controller.book` (captured line 110); no row change, reload, or swap occurs before the assert, so both operands are the same object. Even if `review_characters()` internally reloaded the book, the texts are identical by construction.
   - Impact: assertion cannot fail; false coverage that the review dialog opens the original passage. A regression that seeks into a wrong/stale book passes this line.
   - Fix: compare against an independent source, e.g. `library.books()[0].sentences[wanted].text` or a literal expected sentence text.

2. **tests/test_cast_refine.py:82-90** (`test_changed_candidate_context_invalidates_cache`)
   - Trigger: both `analyze_refined` runs use the identical book and args; the only assertion is `len(calls)==1`, i.e. cache **reuse**. Nothing changes between runs, so the invalidation-on-change behavior the name promises is never exercised.
   - Impact: a cache key that omits book/candidate content (stale analysis served after the book is edited) passes this test — exactly the bug class the name targets.
   - Fix: mutate the book between runs (e.g. change the sentence text so candidate context differs) and assert the model is re-asked (`len(calls)==2`); or rename the test to the key-stability/reuse check it actually performs.

3. **tests/test_cast_flow.py:245-254** (`test_cache_only_worker_does_not_load_model`)
   - Trigger: `analyze_book` is fully replaced by a lambda and `tmp_path` is empty (no cache exists), so the cache-completeness/model-load decision — which lives inside `analyze_book` (cf. `test_resume_does_not_repeat_completed_chunks`, which drives the cache via `analyze_book` directly) — never executes. `forbidden` can only fire if `CastScanJob.run` itself calls `ensure_backend`.
   - Impact: the named behavior "cache-only worker does not load model" has no real coverage; a regression making the cache-only path load the model stays green. The test only proves `run()` doesn't unconditionally pre-load.
   - Fix: pre-populate a complete cache (run the real `analyze_book` with a stubbed `ask`, or write the cache files) and keep the real `analyze_book` with `ensure_backend` forbidden — mirroring `test_refined_job_releases_model_even_on_cache_only_path`, which does this correctly.

VERDICT: BLOCK
