# colibri bug review - src/film/autopilot.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 78994f9b - 2026-08-26
mode: bug - context: every consumer traced from vite.film.ts (buildLadder feeds autopilot-run, autopilot-bill, availability gates, fallback rungs); autopilot.test.ts read in full; git b0212df/f9c5a4d (the loop-closes + price-truth era)

## Verdict

Shippable after the one fix below. The pure core is disciplined (patch whitelist, step monotonicity, grid-heals-count storyboard validation) - but the feature b0212df shipped to close the learning loop was silently dead.

## Fixed since this review (same session)

- [HIGH] resolveLadder looked up learned win-rates by bare `slug` while winRatesFromRuns keys its map by the full "service/slug" reference (the engines' stored form per the FilmDefaults contract and every writer: wizard picks, autopilot-run picks, run records). Every lookup missed, so "best" silently degenerated to price order and "balanced" never proved an engine - ratings never taught the ladder. The existing test masked it by keying its fixture map with bare slugs (encoding the bug). FIX: a winOf() helper queries `${service}/${slug}`; the test fixture corrected to full refs and a new regression ties winRatesFromRuns output to resolveLadder ordering end to end.

## Missing safeguards

- applyRecordPatch accepts unvalidated shapes into PATCHABLE sections (idea/shape as any JSON) - a crafted local POST can poison a record into downstream TypeErrors; the wizard's own client only sends well-formed patches. Defensive shape checks would harden it.
- fitDialogue split of an over-long line can exceed the last shot's cap on very long scripts (word-count remainder), self-limiting via the 12s shot clamp.

## Verified-correct (adversarial passes, findings deleted)

- validateStoryboard's zero-shot guard, entry-0 completeness burden, mid-gap inheritance; shotGrid zero/reversed-span impossibility (snap radius 0.35s vs >=2.5s sub-spans, verified arithmetically in the analysis.ts review).
- resolveLadder seed-family per-service version resolution, denylist invisibility, byPrice null-handling, `service+slug` concat keys (no collision among known service ids).
- applyRecordPatch step monotonicity with the done->producing repair exception (traced against autopilot-run's allowStepBack).
