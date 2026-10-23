# colibri feature review - colibri-bounty/colibri_bounty/match_llm.py

- source: `colibri-bounty/colibri_bounty/match_llm.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `7470224c7f048bdbc8e8f3e1bbb446f2c8f8ba4ab9271d0e867c420978ef1638`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: module role + consumers + deliberate-decisions list (MATCHER_V3.md, gate EV-241/EV-245 lineage) + already-planned exclusions (FUNNEL_PLAN S1/S2v2/W6) + RSI ruleset (0 active) + remediation manifest (p2_llm slug pin)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0529 (in=3219 out=7737)

## grok-4.7 output (verbatim)

## What this module does

This is the opt-in paid transport for matcher v3. `build_message` renders title-band scanner/judged pairs under `ADJUDICATE_PROMPT` (contest duplicate rules, `DETAIL_CAP`/`BODY_CAP` truncation) and `adjudicate_pairs` sends them to `OpenRouterClient.chat` in chunks of `CHUNK`, returning a 1:1 bool list that promotes only a literal JSON `true`. Missing or garbage verdicts stay NO, client errors propagate, and `stats` records call health plus short `reasons` for the scoring run. `match_findings_v3` and `funnel_metrics` leave the adjudicator unset unless a run opts in.

## Suggested add-ons

**1. Prompt/run provenance on `stats`**
Value: High
Effort: S
What: Stamp a stable fingerprint of `ADJUDICATE_PROMPT` plus `CHUNK`, `DETAIL_CAP`, and `BODY_CAP` (and the client’s pinned model id if `OpenRouterClient` already exposes it) onto `stats` at the start of `adjudicate_pairs`.
Why it helps the user: The live wording change is what moved 12/60 to 16/60. Without a stamp, a later re-score cannot be attributed to this prompt versus snapshot drift, so the printed score is not an auditable measurement.
How: In `adjudicate_pairs`, `setdefault` a `provenance` dict from those module constants before the chunk loop. Do not change the message text or the promote-only-`is True` path.

**2. Actual spend on the stats the run already prints**
Value: High
Effort: S
What: After each successful `client.chat`, fold tokens and USD the client already recorded into `stats` (`usd`, `prompt_tokens`, `completion_tokens`), summed across chunks.
Why it helps the user: Doctrine is paid spend capped and disclosed, and the docstring says these stats exist so cost is observable, but the keys filled today are only `calls`, `pairs_sent`, `parse_failures`, `yes_verdicts`, and `reasons`. The $0.0346 figure cannot be reproduced from this channel.
How: Extend `adjudicate_pairs` immediately after `client.chat`. If `chat` returns only the string `extract_json_array` consumes, add a narrow last-call usage accessor on `OpenRouterClient` — do not parse the reply and do not add a second meter. Never turn a budget error into NO; keep letting it propagate.

**3. Joinable adjudication evidence (verdicts unchanged)**
Value: Med
Effort: S
What: Alongside the existing `stats["reasons"]` strings, append structured rows: global pair index, `scan_title`, `truth_title`, whether `same_bug is True`, the capped reason, and whether `_cap` truncated detail or body. Separately count omitted, ghost, non-int, and non-literal-`same_bug` rows — still NO, not a new verdict.
Why it helps the user: Band tuning from `stats["reasons"]` is already planned, but `"pair 26: …"` cannot be joined to the defect once the pairs list is gone, and a miss cannot be told apart from an 800/1200 cut or a dropped row. Whole-chunk `parse_failures` stays the only health signal today.
How: Have `_cap` report a truncated flag into `build_message`; write the row in the existing `stats["reasons"].append` site inside `adjudicate_pairs` (new key, e.g. `reason_rows`, so current string consumers keep working). Leave the `isinstance(n, int)`, range check, and `is True` gates as they are.

## Nice-to-haves

- Optional `detail_cap`/`body_cap` kwargs on `build_message` and `adjudicate_pairs`, defaulting to `DETAIL_CAP`/`BODY_CAP`, so a re-score can ablate truncation without editing the module.
- On the `if not rows` path in `adjudicate_pairs`, keep a length-capped raw reply in `stats` so the next non-zero `parse_failures` is diagnosable.
- Include the chunk start index on each reason row so a failed block of 25 is identifiable without re-deriving `start + n`.

### Triage (in-session GLM, verified against current bytes)
- ACCEPT prompt/run provenance stamp - VERIFIED: `stats` carries no fingerprint of ADJUDICATE_PROMPT/CHUNK/caps; the 12/60 -> 16/60 move was prompt-wording-driven, so re-scores are currently unattributable.
- ACCEPT actual spend on stats - VERIFIED: the only keys filled are calls/pairs_sent/parse_failures/yes_verdicts/reasons; the $0.0346 figure is not reproducible from the channel.
- ACCEPT joinable reason_rows - VERIFIED: reasons are truncated `pair N:` strings; pair identity is lost once the pairs list is gone.
- OBSERVATION (mine, not grok's): the `adjudicate_pairs` docstring still names the stats key `promoted`; the code sets `yes_verdicts` (EV-245 r1 rename). Stale docstring - fix at next touch.
- DEFER caps kwargs, raw-reply cap on parse failure, chunk-start index on reasons.
