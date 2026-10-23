# colibri feature review - colibri-bounty/tests/test_p2_scanner.py

- source: `colibri-bounty/tests/test_p2_scanner.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `3f28e38f0cde48a6df51b6b018571ed663bc0e5e2508c4d95bcc6b2d5f32619f`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0631 (in=5173 out=8788)

## grok-4.7 output (verbatim)

## What this module does
This suite drives `P2Scanner.scan` and `P2XScanner.scan` offline: a fake Slither `runner` plus a scripted `OpenRouterClient` (via `FakeClientFactory`) over a temp Solidity tree, with `FakeT.post` forbidden from hitting the network. It locks title_key dedup, `last_stats` counts, fail-soft `BudgetExceeded` / HTTP skips, basename joining of Slither hits into prompts, `context_builder` prefixing, and P2X cross-file units (`unit_chars`, combined sources, `INTERACTIONS` banner).

## Suggested add-ons
**Replay provenance on `last_stats`**
- Value: High
- Effort: S
- What: After every scan, stamp the solc id, model id, and prompt identity onto `last_stats`.
- Why it helps the user: Counts this suite already asserts (`candidates_raw`, `llm_calls`, `review_units`) are not comparable across replays unless the toolchain is named. Funnel precision is already split across unlike denominators; a number that does not record which compiler and which prompts produced it cannot be used like-for-like, and this path must not spend live to rediscover that.
- How: In `P2Scanner.scan` and `P2XScanner.scan`, where `last_stats` is filled, set `solc` from `p2_scanner.DEFAULT_INSTALLED_SOLC`, `model` from `p2_llm.DEFAULT_MODEL` (or the client’s actual model if one was passed into `OpenRouterClient`), and `prompt_id` from a stdlib digest of `p2_llm.REVIEW_PROMPT` + `p2_llm.VERIFY_PROMPT`. Pin both scanners in `test_p2_scanner_end_to_end_with_fakes` and `test_p2x_reviews_units_with_combined_sources`. Do not touch `p2_llm.BASE_URL` or `FakeT.post`.

**P2X trim disclosure**
- Value: High
- Effort: S
- What: When a cross-file unit is cut at `unit_chars`, record `units_truncated`, `chars_kept`, `chars_total`, and `files_omitted` on `last_stats`. Keep the `INTERACTIONS` banner on the bytes actually sent.
- Why it helps the user: `test_p2x_unit_budget_is_digestible` exists because ~60k-char units (5 units for 111 files) yielded 0 candidates while spend went to digesting. A trimmed unit that returns nothing currently looks like a clean contest. Fail-soft is right; a silent trim is not an honest denominator.
- How: Extend the unit builder inside `P2XScanner.scan` that already enforces `P2XScanner.unit_chars` and emits the banner asserted by `test_p2x_multi_file_unit_carries_interactions_banner`. Do not raise the 20_000 cap. Lock it with a sibling of `test_p2x_reviews_units_with_combined_sources` that writes sources longer than `unit_chars` and reads `last_stats`.

**Static-hit join outcome counters**
- Value: Med
- Effort: S
- What: Count Slither hits attached vs left unmatched (`"(none)"`) on `last_stats`. Do not change the basename join.
- Why it helps the user: `test_static_hits_join_by_basename_not_abspath` exists because `filename_absolute` / `filename_short` used to leave every review with no static context, which changes what the model is asked and therefore precision. `last_stats` has no field for that, so a contaminated prompt is invisible in the funnel table. Disclosure only — the basename key stays.
- How: In the join inside `P2Scanner.scan` (same path `P2XScanner.scan` uses before the prompt), tally `source_mapping` entries (`filename_relative`, `filename_short`, `filename_absolute`) matched on `path.name` into `static_hits_attached` / `static_hits_unmatched`. Assert attached ≥ 1 from `test_static_hits_join_by_basename_not_abspath` (payload `SLITHER_ABS`) and both zero from the empty-detectors runner in `test_context_builder_block_rides_every_unit`.

## Nice-to-haves
- Beside existing `budget_stopped` and `llm_errors`, append `last_stats["skipped"]` rows (`path` + `BudgetExceeded` vs other error) from the handlers `test_p2_scanner_partial_on_budget_stop` and `test_api_error_is_fail_soft_not_fatal` already drive.
- Record whether `context_builder` ran and its prefix length on `last_stats`; `test_context_builder_block_rides_every_unit` only checks `startswith`.
- Put P2X member basenames on each finding (objects already expose `.title` / `.severity` / `.path`) so downstream title_key dedup can see cross-file scope without merging unlike tier denominators.
- Fail-soft count of files whose pragma does not match `DEFAULT_INSTALLED_SOLC` (disclose, do not skip the file) so a `^0.8.10` tree scanned with another installed solc stays visible.

- ACCEPT replay provenance on last_stats (solc id, model id, prompt digest) - cited tests + DEFAULT_INSTALLED_SOLC/REVIEW_PROMPT hooks verified.
- ACCEPT P2X trim disclosure (units_truncated/chars_kept/chars_total/files_omitted) - the 60k-unit 0-candidate history is in-test; a trimmed unit returning nothing looks clean today.
- ACCEPT static-hit join outcome counters (attached vs "(none)") - the basename-join history is exactly the class; disclosure only.
- DEFER nice-to-haves (skipped rows list, context_builder ran/length).
