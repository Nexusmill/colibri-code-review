# colibri bug review - vite.openrouter.ts (delta)

source: vite.openrouter.ts · reviewer: ZCode GLM-5.3 in-session · sha256 ce80adca (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 1d310b9d @ 68ad09e 2026-08-23)
context: diff 10+4; prior review 1d310b9d carried.

## Verdict

Shippable - the failure-TTL fix twin of vite.replicate's.

## Bugs & vulnerabilities

None new. scrapeModelPrice now throws on !ok so HTTP failures take the marked-failed path (15-min retry clock) instead of being cached as a week of "no price published"; parse failures on an OK page also land in the failed cache entry via the catch.

## Missing safeguards

- (unchanged) page scrape is unauthenticated HTML; layout changes degrade to estimate (band-honest by design).

## Fixed since last review

- (prior had no open confirmed findings)

## Verified-correct

- The throw-on-!ok restructure traced through enrich()'s catch; SUCCESSFUL parses cache unmarked (7-day TTL).
