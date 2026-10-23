# colibri feature review - colibri-bounty/colibri_bounty/priors.py

- source: `colibri-bounty/colibri_bounty/priors.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `d1c95b600844d83dae2d4ef4ad02a9159ccd3dd24d08f620113f5e3ac2f61b47`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0371 (in=3038 out=5175)

## grok-4.7 output (verbatim)

## What this module does
`priors.py` loads the corpus-mined bug-class registry (`priors.json`, cached only for `DEFAULT_PATH`) and turns one protocol type into the S3 audit steer block via `render_prompt`. `classify_protocol` picks a single type by word-boundary keyword counts over truncated `*.sol` bodies, skipping test/lib/mock trees. Class-level knowledge only; an unknown or empty type yields `""`.

## Suggested add-ons
1. **Value: High | Effort: S**
   **What:** Make the S3 block actually evidence-linked: append a compact citation (paid-count, source-pack id, or whatever the class object already stores) and an explicit one-line gap when a listed class name is missing from `classes`.
   **Why it helps the user:** The steer is what the agent spends depth on. A rank with no citation cannot be weighed, and a silent `continue` drops a class with no trace in the measurement record. Fresh-contest runs stay honest about what was injected.
   **How:** In `render_prompt`, extend the `lines.append` that already reads `c.get("rank")` and `c.get("check")` to also emit present evidence fields (skip if absent). On `classes.get(name)` miss, append a single "unresolved prior" line instead of dropping it. Leave the header's corpus-mined wording intact.

2. **Value: High | Effort: M**
   **What:** Drive protocol detection from the registry, with a scored result (best, score, runner-up, margin) and a near-tie class union.
   **Why it helps the user:** Keywords are hardcoded in `classify_protocol` while types live in `priors.json`, so a new registry type never classifies and never reaches `render_prompt`. Winner-take-all also drops the second taxonomy on hybrids (vault+lending), and a 1-hit win is indistinguishable from a strong one — both distort which checks get depth.
   **How:** Add optional `keywords` on each `protocol_types` entry; `classify_protocol` reads them through `load()` and falls back to the current `scores` dict if absent. Factor the existing `scores` loop into something like `classify_scores(code_dir)` returning the per-type totals; keep `classify_protocol` as the string winner for current callers. Add `render_prompt_hybrid(types)` (or an optional extra-type arg on `render_prompt`) that unions `classes` lists, tags each line with its type, and dedups by class name when runner-up/best exceeds a fixed margin. If best score is 0, return `""` from classify and have the renderer emit a fixed "unclassified — no priors injected" line instead of silence.

3. **Value: Med | Effort: S**
   **What:** A sibling renderer that turns the same ranked checks into S2 invariant seeds (one hypothesis line per class, same order and skip rules).
   **Why it helps the user:** The module's job is to steer both the S3 audit and S2 invariant generation, but only the audit block exists. S2 otherwise re-implements the lookup or ignores the taxonomy. This is content reuse, not contest-target selection.
   **How:** New `render_invariant_seeds(protocol_type, path=DEFAULT_PATH)` beside `render_prompt`, sharing `load()` and the `protocol_types` / `classes` walk. Different line template only (class name, rank, `check` as the hypothesis). Empty input stays empty so fail-soft tiers are unchanged.

## Nice-to-haves
- Score `f.stem` and non-skipped path parts inside `classify_protocol` (higher weight than body hits) so the layout/name signal the docstring describes survives the 4000-char / 200_000-char caps.
- `classes_for(protocol_type)` accessor over the same lookup so S2/S3 do not each re-walk `protocol_types` and `classes`.
- Optional `max_classes` on `render_prompt` to cap injected lines by list order (registry order is the rank order today).
- `load()` cache key includes path identity only for `DEFAULT_PATH`; a `reload()` that clears `_CACHE` would let corpus refreshes pick up an edited `priors.json` without a process restart.

- ACCEPT evidence-linked priors block (citation fields + explicit unresolved-prior line instead of the silent `continue`) - VERIFIED: `if not c: continue` drops missing classes traceless; rank/check only today.
- ACCEPT registry-driven classification with scored result + near-tie hybrid union - VERIFIED: the keyword table is hardcoded in classify_protocol while types live in priors.json (new registry types never classify).
- ACCEPT render_invariant_seeds sibling (same ranked checks as S2 hypotheses; empty stays empty).
- DEFER 4 nice-to-haves (filename-weighted scoring, classes_for accessor, max_classes cap, reload()).
