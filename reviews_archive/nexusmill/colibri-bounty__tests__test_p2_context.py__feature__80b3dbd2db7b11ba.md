# colibri feature review - colibri-bounty/tests/test_p2_context.py

- source: `colibri-bounty/tests/test_p2_context.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `80b3dbd2db7b11bad1b9e29ee359abeba3f8ed776a1559d45e78079fde6604fc`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse) [effort medium - degenerate-retry regime]
- cost: ~$0.0373 (in=4031 out=4880)

## grok-4.7 output (verbatim)

## What this module does
This suite locks the P2 context-pack contract: `code_map` names in-scope Solidity declarations and `@scope` dependency roots while dropping test trees, comments, and bare path imports, and `priors_pack` / `pack_builder` / `build_pack` attach leave-one-out paid-finding priors under a character budget. It treats two invariants as gates: the target contest's judging titles never enter the pack, and a code map larger than the pack cap must not drop the priors section or the "where to look, never whether to report" steering text.

## Suggested add-ons
- **Value:** High **Effort:** S **What:** Pin default budgets to `p2_context.PRIORS_CAP_CHARS` and `p2_context.PACK_CAP_CHARS` instead of the literal `300` / `2_000` caps. **Why it helps the user:** S3 prompt size is part of the measurement denominator; a silent constant edit would move precision/recall with no suite failure. **How:** Extend `test_priors_pack_respects_char_cap` and `test_priors_survive_a_huge_code_map` to call `priors_pack` / `build_pack` once with the constants and once with defaults omitted, and assert the same truncation boundary.
- **Value:** High **Effort:** S **What:** Prefix-safe leave-one-out: a contest slug that is a prefix or substring of another filename must exclude only the named contest. **Why it helps the user:** Corpus slugs collide (`eth` vs `ethena`); a loose match either leaks the target's truths or drops a valid prior class, both of which contaminate the replay. **How:** Extend `test_priors_are_strictly_leave_one_out` with a sibling `target-extra-judging.json` whose title must remain, and keep the exclusion check on `priors_pack(..., exclude_contest=)` plus the closure from `pack_builder`.
- **Value:** High **Effort:** M **What:** Fail-soft prior load that still emits the priors section when one judging file is unreadable, with a visible skip count. **Why it helps the user:** One dirty corpus file should not erase the prior channel the huge-map gate already says must always ride; a disclosed skip keeps the replay honest instead of looking like "no paid classes." **How:** Add a case beside `test_priors_survive_a_huge_code_map` that drops a non-JSON `*-judging.json` next to a good file and asserts `priors_pack` / `build_pack` still contain the good title plus an explicit skipped-file line.

## Nice-to-haves
- Assert `pack_builder`'s closure leave-one-outs the target title, not only that `CODE MAP` and `PRIORS` headers exist (`test_pack_builder_closure_carries_both_sections`).
- Assert the steering clauses from `test_priors_direct_attention_never_gate_reporting` also survive inside `build_pack` when the map is clipped.
- Replace the `"2" in m` file-count check in `test_code_map_lists_contracts_and_deps` with a count taken from the map's own file-count field so unrelated digits cannot satisfy it.
- Feed `code_map` one `library` and one `abstract contract` via `write_tree` and lock that both names surface next to `Vault` / `IPool`.

- ACCEPT pin caps to PRIORS_CAP_CHARS/PACK_CAP_CHARS instead of literals - VERIFIED: the tests hardcode max_chars=300 (L58) and 2_000 (L98).
- ACCEPT prefix-safe leave-one-out lock (eth vs ethena sibling; module uses exact == today) - locks the exclusion against regression.
- ACCEPT visible skip count when a judging file fails to parse (module silently continues today).
- DEFER 4 nice-to-haves (closure LOO assert, steering survival when clipped, file-count field assert, library/abstract surfacing).
