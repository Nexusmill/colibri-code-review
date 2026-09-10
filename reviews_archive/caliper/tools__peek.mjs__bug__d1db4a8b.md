# colibri bug review - tools/peek.mjs (delta)

source: tools/peek.mjs · reviewer: ZCode GLM-5.3 in-session · sha256 d1db4a8b (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 477a77cb @ 9b95dac 2026-08-20)
context: diff 30+20; prior review 477a77cb (2026-09-03) carried.

## Verdict

Shippable - the read-only probe can no longer queue a real GPU render (exact aria-label match instead of the inclusive substring that could fall through to "Queue render"), the always-true promptShown flag is anchored, cleanup runs in finally.

## Bugs & vulnerabilities

None new.

## Missing safeguards

- none new.

## Fixed since last review

- (the substrate-click and always-true-flag findings are this delta's fixes; verified present.)
