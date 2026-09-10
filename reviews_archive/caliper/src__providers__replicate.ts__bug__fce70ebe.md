# colibri bug review - src/providers/replicate.ts (delta)

source: src/providers/replicate.ts · reviewer: ZCode GLM-5.3 in-session · sha256 fce70ebe (full sha in manifest) · 2026-09-05 · mode: bug (delta vs b030d0cd @ bad7e58 2026-08-22)
context: diff 39+4; prior review b030d0cd carried; the live-learned account quirks (6 creates/min burst-1, version-endpoint creates) in mind; consumers: film engine, battery, score/voice routes.

## Verdict

Shippable - the pacer and the version-endpoint create are the two verified-live fixes.

## Bugs & vulnerabilities

None new. pacedFetch serializes MUTATING calls behind a 12s minimum gap (GETs pass through); the gate only waits and stamps lastCreate - the fetch runs outside the chain, so a failed/timeout call never poisons the chain; runPrediction resolves the model's latest_version first and creates via POST /predictions with the explicit version (the by-model endpoint 404s on some accounts).

## Missing safeguards

- The version lookup is one extra GET per prediction (unpaced, cheap); a model with no latest_version fails loudly ("publishes no runnable version") - honest.

## Fixed since last review

- (prior had no open findings)

## Verified-correct

- setCreatePacingForTests seam only touches the gap; poll loop/deadline unchanged (10 min, prior-reviewed).
