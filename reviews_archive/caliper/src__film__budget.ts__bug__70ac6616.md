# colibri bug review - src/film/budget.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 70ac6616 - 2026-08-26
mode: bug - context: callers vite.film autopilot-bill (prices built from ladder picks, voicePerLine nullable) and runProduce's GateCtx; budget.test.ts read; the owner's price-truth rulings (f9c5a4d/8d6ad75)

## Verdict

Shippable after the one fix below. The bill's honesty contract had one silent breach.

## Fixed since this review (same session)

- [MEDIUM] The voice line computed `usd: round3(narrationLines * prices.voicePerLine!)` behind a non-null assertion while `voicePerLine` is legitimately nullable - `number * null` is 0, so an unpriced voice engine billed as a KNOWN $0.00: the total stayed confident, the band never widened, the approval ceiling was quoted on fiction. Score and transcribe legs null correctly; voice alone coerced. FIX: the same null-guard as its unit ternary; regression test added (voice nulls, total nulls, band widens 20%).

## Verified-correct (adversarial passes, findings deleted)

- parseTiers' first-match-wins and two blob grammars; draft-720p draft-rate fallback honesty (shootUnknownDraft widens the band when the base stands in); the itemized 15% retry margin inside the total (owner's itemized-approval direction); worstUsd = total x (1+band) with band from unknowns only; gateStep's epsilon and free-step pass.
