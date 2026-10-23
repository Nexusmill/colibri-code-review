# colibri feature review - colibri-bounty/colibri_bounty/p2_llm.py

- source: `colibri-bounty/colibri_bounty/p2_llm.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `6caa8dbe7947cc7a5049a05b95405183946f14f4176d6b982adb72b98a8d6391`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: module role + consumers + deliberate-decisions list (MATCHER_V3.md, gate EV-241/EV-245 lineage) + already-planned exclusions (FUNNEL_PLAN S1/S2v2/W6) + RSI ruleset (0 active) + remediation manifest (p2_llm slug pin)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0479 (in=5094 out=6291)

## grok-4.7 output (verbatim)

## What this module does

This is the paid Tier-2 of the replay funnel: `OpenRouterClient` posts to OpenRouter under fail-closed spend caps (wire-attempt call count, input tokens, 32k per call, 650k cumulative output) and books a labeled cost estimate from `PRICE_MAP`. `review_unit` turns one contract plus static hits (and an optional context block) into High/Medium finding candidates; `verify_unit` is the adversarial delete pass. Both recover a JSON array from model prose via `extract_json_array`.

## Suggested add-ons

### Separate a real empty verdict from an unusable reply
- Value: High
- Effort: S
- What: Record whether the model returned a JSON array, a legitimate `[]`, or prose/truncated text that did not parse.
- Why it helps the user: Replay scoring treats `[]` as a measured negative. A starved or non-JSON reply is a different event and is currently invisible, so parse failures get scored as “nothing worth reporting.”
- How: Add `classify_json_array` beside `extract_json_array` and keep the list return so `match_llm.py` does not change. `review_unit` and `verify_unit` call the classifier and increment a new `OpenRouterClient.usage` key (for example `unparsed_replies`) while still returning `[]` to `p2_scanner.py`. Put the counter on `usage` so stdout JSON stays the truth.

### Per-call ledger with an output-ceiling hit
- Value: High
- Effort: S
- What: Append one usage record per successful `chat`, including whether completion tokens hit `max_tokens_per_call` before the garbage clamp.
- Why it helps the user: Cumulative `usage` cannot attribute spend to review vs verify, or show that a call burned the whole per-call budget and came back empty. That is the same blind spot as the measured 8k starvation (`[]` at exactly the cap). Caps stay as they are.
- How: In `OpenRouterClient._account` (flag set in `chat` from the raw `usage` block before clamping), append to `self.usage["calls_detail"]`: prompt tokens, completion tokens used for the ledger, cost delta, `output_clamped`, and `hit_ceiling`. Do not change `max_tokens_per_call`, `max_output_tokens`, or the wire-attempt binding in `chat`.

### Make verify delete-only against the original candidates
- Value: High
- Effort: S
- What: Return the input candidate dicts the model kept, not the objects it echoed back.
- Why it helps the user: `VERIFY_PROMPT` says delete and return the same objects unchanged, but `verify_unit` trusts the model’s copies. Rewritten titles change the finding `match_llm.py` scores against judging truth.
- How: In `verify_unit`, after `extract_json_array` and the High/Medium filter, intersect on normalized `title` with the input `candidates` and return those original dicts. Optionally number candidates in `VERIFY_PROMPT` and match on that index so the join is not title-fragile. Leave `review_unit` as the only writer of finding text.

## Nice-to-haves

- Stamp the existing 60k/80k source slice in `review_unit` and `verify_unit` onto `usage` and add one prompt line when truncated, so partial-file units are not scored as full audits.
- Optional price refresh that sets `price_in`/`price_out` from the OpenRouter endpoints API, falling back to `PRICE_MAP` then `UNKNOWN_MODEL_PRICE_PER_M` (glm/qwen pairs are still the unverified 2026-10-17 carry); do not touch the model slug.
- Named `usage["rate_limited"]` incremented in `chat` on 429, without stopping those retries from consuming `max_calls`.
- `temperature` argument on `OpenRouterClient` (default 0.2, passed through `chat`) so the planned W6 tuning tier can vary it without forking the transport.

### Triage (in-session GLM, verified against current bytes)
- ACCEPT `classify_json_array` (real-empty vs unusable reply) - VERIFIED: `extract_json_array` returns [] both for a legitimate empty array and for prose/truncated text; replay scoring cannot tell a measured negative from a starved reply (the 8k-starvation class).
- ACCEPT per-call ledger with output-ceiling flag - consistent with the single cumulative `usage` dict; spend attribution review-vs-verify and ceiling-hit visibility are real gaps.
- ACCEPT verify_unit returns ORIGINAL candidates - VERIFIED, highest value: `survived` is built from the model's echoed dicts, not intersected with the input `candidates`; a rewritten title silently changes the text `match_llm` scores against truth. Near-defect class.
- DEFER slice stamping, OR-endpoints price refresh (aligns with the standing pricing rule), rate_limited counter, temperature kwarg (W6-adjacent).
