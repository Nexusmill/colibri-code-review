# colibri feature review - colibri-bounty/tests/test_p2_llm.py

- source: `colibri-bounty/tests/test_p2_llm.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `a88b8dac48b923115d1a2e9db7d46d447d0187e702ada70705667954ed0e23cd`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0594 (in=6054 out=7886)

## grok-4.7 output (verbatim)

## What this module does
This suite pins the paid LLM tier in `p2_llm`: `OpenRouterClient.chat` is a budget-capped OpenRouter call (call count, input tokens, output tokens, per-call `max_tokens`) that prices from `PRICE_MAP`, retries a 429 once, and clamps session-cumulative completion counts before they can defeat the cap. `review_unit` and `verify_unit` are the per-file review and numbered-candidate verify passes; they parse replies with `extract_json_array` / `classify_json_array`, and verify keeps the original candidate objects joined by `n`. The contract is that replay spend stays disclosed and a starved or rewritten reply is not scored as a clean negative.

## Suggested add-ons
**1. Verify join disposition counters**
Value: High
Effort: S
What: On each `verify_unit` call, record kept vs dropped counts by reason (missing `n`, non-int `n`, ghost `n`, duplicate `n`) on `OpenRouterClient.usage`, separate from `unparsed_replies` and from a real model reject.
Why it helps the user: A fail-closed join drop currently collapses to `[]`, the same shape as “model rejected every candidate.” That understates recall and hides a denominator hole the number-join path already knows how to classify.
How: Extend the `n`-join inside `verify_unit` (the path `test_verify_unit_number_join_fails_closed` and `test_verify_unit_returns_original_candidates_by_number` already exercise). Write the counters next to the existing `usage["unparsed_replies"]` update; do not change which originals are returned.

**2. Measurement-conditions stamp**
Value: High
Effort: S
What: Put a small conditions block on `OpenRouterClient.usage`: model slug, which price pair was applied (`PRICE_MAP` hit, explicit `price_per_m`, or `UNKNOWN_MODEL_PRICE_PER_M`), and a stable id of the prompt text actually sent.
Why it helps the user: Precision and disclosed USD are only like-for-like across replays if the run record names the model, the rate behind `cost_usd`, and the prompt. Those are constructor args and module constants today, with no field the funnel already reads.
How: Resolve the price source where `OpenRouterClient` already chooses between `PRICE_MAP`, `DEFAULT_PRICE_PER_M`, and `UNKNOWN_MODEL_PRICE_PER_M`. Have `review_unit` and `verify_unit` stamp ids derived from `REVIEW_PROMPT` and `VERIFY_PROMPT` (the message body those functions already build).

**3. Budget headroom query**
Value: Med
Effort: S
What: A read-only headroom view — calls left, input tokens left, output tokens left, and whether the next `chat` would raise `BudgetExceeded` — without changing the pre-transport raise.
Why it helps the user: The cap-bound drop (tail units never sent) is a coverage gap, not a finding. Callers can only see it by catching `BudgetExceeded` after attempting a unit. Headroom lets the fan-out stop, name units not sent, and keep the exception path fail-closed.
How: Add the query on `OpenRouterClient` beside the checks `chat` already uses for `max_calls`, `max_input_tokens`, and `max_output_tokens`. Leave `review_unit` / `verify_unit` as callers; do not swallow `BudgetExceeded`.

## Nice-to-haves
- Record `BASE_URL` and the model slug on `usage` so a replay manifest names the endpoint without a new client.
- On `review_unit`, record whether `context_block` was attached and its character length, so protocol-pack overhead is visible against the input-token cap.
- Optional stdlib response cache in front of `OpenRouterClient.chat` (key = model + message body), with `usage["cache_hits"]` disclosed, so corpus re-runs do not re-spend; `FakeTransport.post` is the existing seam.
- Note on the chat path whether the single 429 retry fired, so a flaky provider shows up in spend reviews without changing the one-retry policy.

- ACCEPT verify join disposition counters (kept/dropped by reason on usage) - the n-join classifies but only unparsed_replies is surfaced; cited tests verified.
- ACCEPT measurement-conditions stamp on usage (model slug, price-pair source, prompt id) - price source trio + REVIEW/VERIFY_PROMPT hooks verified.
- ACCEPT read-only budget headroom view (exception path stays fail-closed).
- NOTE: run-1's verify_unit echo-join fix is IMPLEMENTED (test_verify_unit_returns_original_candidates_by_number) - grok built on the current state, no re-suggestion.
- DEFER nice-to-haves (BASE_URL stamp, context_block length).
