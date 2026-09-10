# Synthesis - the catalog brain rows wave (2026-09-06)

Six single-file units in bug mode; one synthesis:

1. **[FIXED IN-WAVE] The name collision** - vite.llm.ts's own LLM_MODELS
   is the models-llm PATH; the catalog import is aliased. Caught by tsc
   (`find does not exist on string`) during the wave, not after.
2. **[FIXED IN-WAVE] The hidden non-brain entries** - the catalog carries
   an embedder, a reranker, AND a 30B coder beyond the five obvious
   brains; the first filter offered them all as brain seats. isCatalogBrain
   (derived from the roles the catalog already speaks) excludes the
   knowledge-store machinery; the 30B coder gained its grounded ceiling
   (262144, its own card).
3. **[VERIFIED] No live download fired** - GB-scale downloads on the
   owner's line are not test fixtures; the 202/409 shapes are code-traced
   and the shelf-refusal path remains live-proven by local-brain-shelf.
4. **[VERIFIED] Every ceiling grounded** - six values, each quoted from
   the model's own HF card this session; pinned in vitest so drift fails
   loudly.

Evidence: tsc exit 0, vitest 434/434 (6 new assertions in the ceilings
test), harness fast tier 58 pass / 0 fail / 4 honest skips -
catalog-brain-rows PASS live (get-it rows with ceilings in the real
picker).
