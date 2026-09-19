<!-- source: vite.film.ts | reviewer: zcode-glm-5.3 | sha256: 7e8ec0630538febb676e3a28af78c40abe7263018fe66e889f86f32e690bd703 | date: 2026-09-15 | mode: bug -->
<!-- context: Wave 6 FINAL delta review (post design-adversary remediation). Call sites traced live (curl through :4173, harness PASS 75/0/8, vitest 499/499, tsc 0); FEATURES row `route-intelligence` + docs/reviews/route-intelligence-2026-09-15.md are the contract. -->

## Verdict
Shippable - the three cloud legs now stamp BOTH verdicts fire-and-forget and rethrow untouched; persistence ordering is sound with the recency fix.

## Fixed since last review (this delta)
- **Fail stamps were absent at the pause** (the UI promised "last run FAILED" with no producer - the shown-vs-sent class): wired at all three cloud legs via try/catch that stamps then rethrows. CONFIRMED by reading the three catch paths; vitest pins the consumer side (both verdict orders).

## Bugs & vulnerabilities (delta)
**[NOTED, not a defect] post-success persistence failure lands fail after ok** - the ok stamp fires before writeFilm/appendProvenance
- A disk failure after a successful cloud render stamps fail later on the same entry; with newest-verdict-wins in SettingsConsole the row then says FAILED for a run whose ROUTE succeeded. The row's contract is the route's verdict, so this is a semantic edge, not a defect; reason text names the actual failure.
- Token-missing throws stamp the route FAILED - honest: the run through that route failed with that reason.

## Missing safeguards
- None added; the wraps are pure addition, callers unchanged.
