# colibri bug review - tools/see.mjs (delta)

source: tools/see.mjs · reviewer: ZCode GLM-5.3 in-session · sha256 76fcc075 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 0f91a67a @ e8dd8ef 2026-08-19)
context: diff 75+40; prior review 0f91a67a (2026-09-03) carried; the screenshot-verify protocol's own driver.

## Verdict

Shippable - the failure contract is the delta: non-zero exits with named errors at every failure point, no screenshot on failure, completion signaled by the LIVE job chip (never media presence - persisted windows rehydrate and once certified the previous run's render), persisted-screen cleared after settle+reload (async persist race discipline).

## Bugs & vulnerabilities

None new (bundle-miss and picker-mismatch are loud errors; 600s cap replaces the 180s one; finally-block cleanup closes/disconnects).

## Missing safeguards

- none new.

## Fixed since last review

- (the 2026-09-03 findings this delta fixes are the failure-contract items; verified present.)

## Verified-correct

- The error-break in the poll loop surfaces last-seen text; APP_URL env override defaults to localhost:4173.
