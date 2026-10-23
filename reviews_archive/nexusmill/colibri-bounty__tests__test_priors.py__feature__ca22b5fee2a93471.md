# colibri feature review - colibri-bounty/tests/test_priors.py

- source: `colibri-bounty/tests/test_priors.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `ca22b5fee2a93471b9b15d360ae2d2e4bc0c062a0f6a0d8d055991ffb1ed8b74`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse) [effort medium - degenerate-retry regime]
- cost: ~$0.0384 (in=2492 out=5562)

## grok-4.7 output (verbatim)

## What this module does
This suite pins the W1 priors contracts that steer offline contest replay: `priors.load` yields `protocol_types` whose `classes` must exist in `data["classes"]`, and `priors.render_prompt` turns a known type into a non-empty steer block (`router-dex` includes `unsafe-token-transfer`, `residue-sweep`, and `steer depth`) while an unknown type renders `""`. `priors.classify_protocol` is pinned only on a single-fixture tree (`Router.sol`/`swap` → `router-dex`, then after unlink `Gov.sol`/`quorum`/`vote` → `governance`). `priors.DEFAULT_PATH` is never referenced.
## Suggested add-ons
### Priors-file identity for like-for-like replays
Value: High
Effort: S
What: Surface the file `priors.load` actually read (zero-arg path via `priors.DEFAULT_PATH`, plus a content digest) so a replay record can name the steer library beside its precision/recall denominator.
Why it helps the user: Prior-library drift between runs is invisible today and would contaminate before/after comparisons the same way mixed denominators already did; paid-spend decisions need the steer text pinned to the corpus run.
How: Extend `priors.load` to expose the resolved path it opened, defaulting through `priors.DEFAULT_PATH`; pin that identity next to `test_load_and_render_prompt` and `test_every_protocol_type_resolves`. Do not add a runtime dependency.

### Primary label plus other matches on mixed trees
Value: High
Effort: M
What: Keep `priors.classify_protocol`'s single primary string as the denominator key, and also return every other protocol type the same tree matches so each can be passed through `priors.render_prompt`.
Why it helps the user: The only pinned path unlinks `Router.sol` before writing `Gov.sol`, so dex+governance contests are unspecified; a silent single label under-steers classes and makes recall incomparable across mixed vs pure trees.
How: Extend `priors.classify_protocol`; leave the two asserts in `test_classify_protocol_on_tmp_tree` as the primary-label contract; union steer text by calling existing `priors.render_prompt` per extra type. Do not merge this label into agent-tier or union score tables.

### Unclassified trees stay out of the steered denominator
Value: Med
Effort: S
What: Distinguish a no-match `priors.classify_protocol` result from a known type, without changing the pinned `priors.render_prompt("nonexistent-type") == ""` fail-soft.
Why it helps the user: An unscored tree that renders empty looks like a steered run with no hits, so it inflates the denominator; honest measurement needs unclassified contests visible and excludable, same spirit as an incomplete measurement staying visible.
How: Extend `priors.classify_protocol` with an explicit no-match sentinel that is not a key of `priors.load()["protocol_types"]`; pin it beside `test_render_prompt_unknown_type_is_empty` and `test_classify_protocol_on_tmp_tree`. Callers filter on that sentinel; they do not treat `""` from `priors.render_prompt` as success.
## Nice-to-haves
- Pin that zero-arg `priors.load` reads `priors.DEFAULT_PATH` and that the path exists.
- Pin `priors.classify_protocol` on an empty directory and on a tree with no `.sol` files.
- Pin `priors.render_prompt(ptype)` contains every `spec["classes"]` entry, not only the two literals in `test_load_and_render_prompt`.
- Pin primary-label stability when both `Router.sol` and `Gov.sol` are present, so tie-break order cannot drift between runs.
- Pin `priors.render_prompt` is deterministic for a given `priors.load()` payload (stable class order, no run-specific text).

- ACCEPT priors-file identity on load (resolved path + digest beside the denominator) - like-for-like steer-library pinning.
- ACCEPT primary label + other matches on mixed trees (Router-then-Gov unlink dance leaves dex+governance unspecified today).
- ACCEPT explicit no-match sentinel distinct from render_prompt's "" fail-soft (unclassified trees must not inflate the steered denominator).
- DEFER 5 nice-to-haves (DEFAULT_PATH existence pin, empty-dir classify, full-classes render pin, tie-break stability, determinism pin).
