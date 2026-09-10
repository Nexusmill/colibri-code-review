# colibri bug review - vite.keys.ts (delta)

source: vite.keys.ts · reviewer: ZCode GLM-5.3 in-session · sha256 8095d571 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs be9fe8c0 @ 3fe3a83 2026-08-22); full current file read (74 lines).

## Verdict

Shippable - no defects.

## Bugs & vulnerabilities

None. The factory pattern holds: keyRoutes(readBody) closes over the body reader and returns a 2-arg handler, so the composer's 2-arg mount is correct (verified against the live mount in vite.caliper.ts). servicePresence is a read-only presence trio with label fallback.

## Missing safeguards

- none material (EXPECTED_PREFIX mismatch is advisory by design - documented).

## Fixed since last review

- (prior had no open findings)

## Verified-correct

- readServiceKey's non-null bound (isServiceKeyId guards the stores key); token write null-means-clear; formatOk only on paste with a known expected prefix.
