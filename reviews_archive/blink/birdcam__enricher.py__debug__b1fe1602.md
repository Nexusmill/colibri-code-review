# Debug review — birdcam/enricher.py (planner token starvation, round 2)

- source path: birdcam/enricher.py
- model: in-session GLM (zai-individual-coding-plan/GLM-5.3)
- sha256: b1fe1602 (post-round-2 bytes; round-1 reviewed at 5091d165)
- date: 2026-10-14
- mode: debug
- context pack: jCodemunch (call_openrouter, _enrich_compilation_inner, build_plan_prompt,
  SYSTEM_PROMPT, plan_song_count, MAX_LYRICS_CHARS=3500, config pins), data/hourly_run.log
  (finish_reason 'length' on 6/8-song plans, both LLM_ATTEMPTS, 10-12..10-13),
  data/state.json (Bird Bath enriched=failed 10-08/10/10/10-12/10-13; Bird Feeder 1-song ok
  throughout), OpenRouter models API 2026-10-14 (deepseek-v4.1-flash max_completion_tokens
  943718 base / 131072 batch), remediation manifest row of 2026-10-09 (round 1: glm swap).

## Failure signal

`enrich: planning failed: planning model hit the max_tokens token ceiling before finishing
the plan (thinking models can burn the whole budget on reasoning)` — both retry attempts,
identical parameters, on every Bird Bath (long-compilation) batch since 2026-10-10. The
aborted plan returns None from _enrich_compilation_inner, so the batch posts plain: no
songs AND no title cards (intro/outro cards live in the same plan JSON). This is why the
owner saw "title cards and songs still are not working" after the 10-09 model swap.

## Root cause (CONFIRMED, executed not re-reasoned)

call_openrouter hardcoded `max_tokens: 16000` for every plan size. Content arithmetic:
8 songs x 3500-char lyrics ceiling ~= 11K tokens of content before any reasoning; the
thinking model's reasoning bills against the same output budget (empirically several K on
the 5-song plans that succeeded 10-09/10-11). 6-8-song plans exceed 16K -> finish_reason
'length' -> EnrichError. The 10-09 round-1 fix swapped the MODEL but left the BUDGET; the
new model is also a thinking model, so the same ceiling kept killing long plans (1-song
Bird Feeder plans always fit; that is why only the big daily compilations failed).

Producing caller: _enrich_compilation_inner -> call_openrouter with
build_plan_prompt(..., song_count=plan_song_count(duration, 190)) - Bird Bath days
produce 6-8 song plans; nothing caps the plan below the starvation line.

## Fix (G41 contract)

Invariant: the planner request always carries max_tokens = PLANNER_MAX_TOKENS (65536),
~3x the worst observed need (~20K) and far under the pinned model's verified
max_completion_tokens; finish_reason 'length' keeps raising the actionable error as the
last-resort signal. Sibling ledger: call_openrouter body APPLY; TestCallOpenRouter APPLY
(new budget test + prose fix in the old outage comment); _enrich_compilation_inner
ADJUDICATED (only caller, no signature change); README cost sentence APPLY.

Failure paths of the fix: none new - 65536 is within both provider variants' caps;
billing is actual tokens (the cap is not a target), so small plans cost the same as
before. Guard space: 1-song plans (unchanged), 8-song plans (3x margin), pathological
reasoning burn (still caught by the loud length error).

## Verification

- T1 RED->GREEN: test_planner_budget_covers_multi_song_plans asserts the request body
  carries PLANNER_MAX_TOKENS and pins the 65536 floor.
- T2 regression: test_length_finish_reason_raises_actionable_error still green.
- Full battery: 255 tests OK (1 pre-existing skip).
- LIVE probe (junk/probe_planner_budget.py, real key, real 110-song catalog, tier-1
  pins, NO music generation): the exact production-shaped 8-song plan completed in 123s,
  parsed to 8 pop songs with correct slot genres. The same shape starved 5/5 times in
  production logs before the fix.

## Verdict

Shippable. The budget was the constraint, not the model; round 1's model swap treated the
wrong variable. Worst remaining risk: a model that reasons past 64K would still fail -
loudly, with the actionable message, and never blocking posting (design invariant).

## Gate round 2 (adversary gate 2026-10-14, gate_20261014-135109.md)

BLOCK/WARN finding, CONFIRMED and remediated in-session: the budget raise makes the
planner the slowest enrichment call - the live probe took 123s wall time while
call_openrouter rode the shared HTTP_TIMEOUT_SECONDS=90. The probe survived because
urllib's timeout is per socket operation, not a total deadline, but that is server-
delivery behavior we do not control. Fix: PLANNER_HTTP_TIMEOUT_SECONDS=300 passed
through a new optional _http_json(timeout=...) param (default HTTP_TIMEOUT_SECONDS
preserves every other caller); tests pin the default AND the planner override
(test_http_json_timeout_default_and_override, plus the budget test's timeout asserts).
Battery: 256 OK. The gate catch is itself the round's escape-rate ledger evidence:
caught at the gate stage, lived in round-1-touched code (the budget raise).
