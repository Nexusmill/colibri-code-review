# colibri bug review - src/film/budget.ts (delta)

source: src/film/budget.ts · reviewer: ZCode GLM-5.3 in-session · sha256 7f6c26b82a9bb1f22b7f3f6a08a5a00384970e91815c8dbc1ca36e2273876c10 · 2026-09-05 · mode: bug (delta vs 70ac6616 @ 8d6ad75 2026-08-24)
context: full current file read (116 lines); delta 3+1 (tier/draft-rate plumbing); cross-file: the bill's ONLY caller (vite.film.ts autopilot-bill, e827383d) and the gate consumers (GateCtx/perStepOf), autopilot-run's strategyRef logic, budget.test.ts.

## Verdict

Shippable in-file - the arithmetic is honest and the prior fix holds. One cross-file contract gap (the caller's, filed here because this is the bill's contract): the bill is strategy-blind while the run is strategy-aware.

## Bugs & vulnerabilities

**[HIGH - cross-file, caller-side] the draft-first bill never prices the FINISH pass, and prices the shoot leg from the wrong engine** - contract gap between `vite.film.ts autopilot-bill` (pick("shoot") = engines.shoot override or ladder default) and `autopilot-run`/`autopilot-finish` (strategyRef = shape.draftEngine/finishEngine by mode). For a draft-first run the bill quotes ONE pass at the default/override engine rate; `autopilot-finish` then discards every segment and re-shoots the whole film on the finish engine under the SAME ceiling. With the ledger-sync gate, spent (draft total) + est crosses worstUsd (~total x 1.15 x band) within the first ~15% of the finish pass → HALT; the recovery path ("re-approve a higher bill") recomputes the same strategy-blind bill, so it cannot re-price either. No unapproved dollar crosses the ceiling (the gate holds - money-safe), but the finishing switch cannot complete for any pricier finish engine, and the approval quoted the wrong number. Fix: make autopilot-bill strategy-aware (price the pair: draft pass + finish pass as separate lines for draft-first, finish-engine rates for straight-finish), and/or autopilot-finish requires a fresh bill+approval for the finish pass. FINAL GRADE PENDING FilmWizard row (if the wizard re-bills with finish pricing before the switch, downgrade).

## Missing safeguards

- parseTiers first-match-wins on free text can grab a rate for a tier mentioned in prose before the table (accepted honesty trade - band widens only when absent, not when wrong; pre-existing).

## Fixed since last review

- [MEDIUM] voice leg null-coercion - FIX VERIFIED present (line 80 null-guards usd and unit together; total nulls, band widens).

## Verified-correct (adversarial passes, findings deleted)

- Tier/draft-rate selection: native rides statedTier, draft-720p rides draftRate with shootUnknownDraft widening the band when the base stands in, draft-480p at base unmarked. unknowns counting (nulls + tier/draft-unknown flags), bandPct cap at 1, total/worst only when all known, full-precision totalUsd.
- The 15% retry margin stays an explicit itemized line inside the total (owner's itemized-approval direction).
- gateStep: free steps pass, non-finite/non-positive ceilings halt (fail-closed), epsilon comparison.
