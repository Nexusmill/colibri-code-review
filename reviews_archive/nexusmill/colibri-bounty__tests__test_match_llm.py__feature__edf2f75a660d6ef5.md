# colibri feature review - colibri-bounty/tests/test_match_llm.py

- source: `colibri-bounty/tests/test_match_llm.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `edf2f75a660d6ef558184d5c36635886177538901eb2f20b7d3c46e92e9ed664`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0753 (in=5696 out=10656)

## grok-4.7 output (verbatim)

## What this module does

This suite locks `match_llm`, the matcher-v3 paid band adjudicator, entirely against a fake `chat` client. It checks pair-number alignment, fail-closed parsing (garbage JSON, short arrays, non-bool `same_bug`, non-integer pair ids), prompt wording and text caps, and the stats contract (`yes_verdicts`, `reasons`, provenance, folded spend, `reason_rows`). The live paid pin is never exercised here.

## Suggested add-ons

**Per-pair disposition beside the bool vector**
Value: High. Effort: S.
What: A full-length `stats["pair_disposition"]` aligned with the list `adjudicate_pairs` already returns, marking each pair `model_yes`, `model_no`, or `unmeasured`.
Why it helps the user: Precision denominators (16/60, 13/48) cannot stay like-for-like while parse garbage, omitted rows, non-literal `same_bug`, and a real model NO all collapse to `False`. Counters exist; the matcher only consumes the bool list, so a bad chunk moves the table.
How: Extend `match_llm.adjudicate_pairs` only. Keep the bool vector fail-closed exactly as `test_adjudicate_pairs_fail_closed_on_garbage_json`, `test_adjudicate_pairs_ignores_non_bool_same_bug`, and `test_reason_row_shape_counters_fail_closed` lock it. Fill the mask from the same classification that already increments `parse_failures`, `rows_omitted`, `row_non_literal`, `row_non_int`, and `row_ghost`. Do not catch `client.chat` errors.

**Opt-in replay cache keyed by the existing provenance stamp**
Value: High. Effort: M.
What: Caller-supplied dict (default off) that skips `chat` when the prompt fingerprint and the capped payload match a prior successful chunk.
Why it helps the user: Corpus replays on `E:/bounty-corpus` re-bill identical adjudications. The 12/60 to 16/60 move was prompt-wording-driven; a key that includes `prompt_sha16` misses automatically when the prompt changes, and unchanged contests stay inside the spend cap.
How: In `match_llm.adjudicate_pairs`, before `client.chat`, hash the messages from `match_llm.build_message` and combine with `stats["provenance"]` (`prompt_sha16`, `chunk`, `detail_cap`, `body_cap`, `model`) as already asserted by `test_provenance_stamp_on_stats`. Store only chunks with no parse failure. Never replay a fail-closed chunk as a measured NO. On miss, chat and store. No new dependency; `cache=None` leaves every current test path unchanged.

**No-chat plan that shares the paid constructor**
Value: Med. Effort: S.
What: A preview of chunk count, capped messages, and the provenance fingerprint, with zero `chat` calls, so paid opt-in is a second step.
Why it helps the user: Today the only way to see capped scan/truth text and the `...[truncated]` cuts is to call `adjudicate_pairs`, which spends. Operators cannot confirm caps, chunk, and prompt hash before the pin.
How: Extend `match_llm.build_message` (public, unreferenced by this suite) and call it from both the preview and `adjudicate_pairs`, so the preview cannot drift from the paid path. Reuse `ADJUDICATE_PROMPT`, `CHUNK`, `DETAIL_CAP`, and `BODY_CAP`. Preview must not touch `client.chat` or the usage ledger.

## Nice-to-haves

- Fold `output_clamped` and `hit_ceiling` counts next to summed `usd` in the `calls_detail` path `test_spend_folded_from_client_ledger` already feeds, so a ceiling-cut chunk is not read as a model NO.
- Empty `pairs` stamps provenance with `calls == 0` and does not chat, so a contest with no band candidates is a measured zero rather than a missing row.
- Count duplicate pair numbers in one reply beside `row_ghost`; do not change which bool wins.
- Put `provenance["model"]` into any cache key when the client exposes it; this suite only locks the bare-client `None` case.

- ACCEPT per-pair disposition mask (model_yes/model_no/unmeasured beside the bool vector) - hooks verified live (parse_failures/rows_omitted/row_non_literal/row_non_int/row_ghost counters all exist).
- ACCEPT opt-in replay cache keyed on the provenance stamp - VERIFIED: the GROK47 T2 provenance/spend/reason_rows backlog LANDED with tests (test_provenance_stamp_on_stats asserts prompt_sha16/chunk/caps) - grok built on the real current state, no re-suggestion.
- ACCEPT no-chat preview sharing build_message (paid opt-in as a second step).
- NOTE: run-1's match_llm backlog is IMPLEMENTED (GROK47 T2 tests in test_match_llm.py) - the deferred rows for it are historical; no double-docket.
- DEFER 4 nice-to-haves (ceiling counts beside usd, empty-pairs measured zero, dup pair-number count, model in cache key).
