# colibri bug review - src/components/DeckControls.tsx (delta)

source: src/components/DeckControls.tsx · reviewer: ZCode GLM-5.3 in-session · sha256 be37f2c1 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 432bdd01 @ 3f395f0 2026-08-23)
context: diff 10+1; prior review 432bdd01 (the rounding-twin residual lived here per project memory) carried; routesStore.profile.

## Verdict

Shippable - the cloud-only LOCAL arm states the law instead of offering dropdowns that can only fail.

## Bugs & vulnerabilities

None new.

## Missing safeguards

- (carried, residual shelf) the fmtGb rounding twin noted in project memory remains a cosmetic residual, not re-verified this pass.

## Fixed since last review

- (prior had no open confirmed findings)
