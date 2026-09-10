# colibri bug review - src/api/film.ts (delta)

source: src/api/film.ts · reviewer: ZCode GLM-5.3 in-session · sha256 bcb7764f (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 5d6be12d @ 6909725 2026-08-25)
context: diff ~117 lines; prior review 5d6be12d carried; every response shape cross-checked against the server handlers read this pass (vite.film.ts e827383d).

## Verdict

Shippable - the typed-client surface grew to mirror the server's new actions; shapes verified against the handlers.

## Bugs & vulnerabilities

None new. Artifacts classification renamed to the one-class-per-type contract (matches readArtifacts); runs-manager columns (name/budgetUsd/busy/verdict/halted/deleteError) match RunSummary; checkpoint/finish/redraft/song-upload/delete wrappers match their handlers' response bodies; GradeBook grew the review flags.

## Missing safeguards

- autopilotDelete's return type omits the queued flag the server sends (cosmetic typing gap - no runtime impact).

## Fixed since last review

- (prior had no open findings)

## Verified-correct

- All POST wrappers flow through the shared post() helper; no URL or path input crosses into a fetch target beyond the fixed /api/film route.
