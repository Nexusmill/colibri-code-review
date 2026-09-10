# colibri bug review - src/bundles/constraints.ts (delta)

source: src/bundles/constraints.ts · reviewer: ZCode GLM-5.3 in-session · sha256 01434323 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs bd427237 @ d70c277 2026-08-16)
context: diff 2+2; prior review bd427237 carried.

## Verdict

Shippable - the hardcoded "8n+1" messages now quote the bundle's own detent string (the shown-vs-sent truthfulness class).

## Bugs & vulnerabilities

None new. violations() and snapMessage() interpolate b.constraints.frames (validated parseable at load AND save by schema.ts), so the message always names the constraint actually enforced.

## Missing safeguards

- none new.

## Fixed since last review

- (prior had no open findings)
