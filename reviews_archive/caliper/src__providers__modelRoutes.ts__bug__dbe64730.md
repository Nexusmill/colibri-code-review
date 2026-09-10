# colibri bug review - src/providers/modelRoutes.ts (delta)

source: src/providers/modelRoutes.ts · reviewer: ZCode GLM-5.3 in-session · sha256 dbe64730 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs cc62d771 @ f886da9 2026-08-22)
context: diff 12+1; prior review cc62d771 carried; consumers: vite.routes resolvedRoute (both GET rows and engine resolution).

## Verdict

Shippable - gatedRouteConfig is the both-ways fix (stored local routes survive the cloud-only switch AND never resolve under it).

## Bugs & vulnerabilities

None new. The gate is read-path only (returns a filtered copy; the stored config is untouched); profile !== cloud-only returns the config as-is (no copy churn).

## Missing safeguards

- none new.

## Fixed since last review

- (the 2026-09-02 wipe-vs-leak finding this closes was filed on the caller side; verified enforced here.)

## Verified-correct

- Object.fromEntries filter preserves non-local routes verbatim; resolveRoute unchanged (its own defaults reviewed at cc62d771).
