# colibri bug review - vite.routes.ts (delta)

source: vite.routes.ts · reviewer: ZCode GLM-5.3 in-session · sha256 54c9654c (full sha in manifest) · 2026-09-05 · mode: bug (delta vs a9e1c274 @ af12a90 2026-08-22)
context: diff 15+13; prior review a9e1c274 carried; cross-file: modelRoutes.gatedRouteConfig (cache-hit review cc62d771 family), every resolvedRoute consumer (film engine, chips, settings).

## Verdict

Shippable - the delta makes the cloud-only profile genuinely reversible.

## Bugs & vulnerabilities

None new. resolvedRoute now resolves through gatedRouteConfig (stored LOCAL routes gated out of cloud-only resolution without erasure); the profile switch preserves config.routes (the 2026-09-02 gate finding - the old wipe made "reversible" a lie); GET's resolved rows use the same gated truth the engine uses.

## Missing safeguards

- (unchanged) model-routes.json last-write-wins across concurrent POSTs (single-user console tempo).

## Fixed since last review

- cloud-only profile switch no longer wipes stored routes - FIXED in this delta.

## Verified-correct

- The GET handler still returns the UNGATED config (settings shows what is stored) while every resolved value is gated - display vs behavior traced consistent; servicePresence dedupes the prior inline trio.
