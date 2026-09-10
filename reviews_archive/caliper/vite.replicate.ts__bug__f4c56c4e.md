# colibri bug review - vite.replicate.ts (delta)

source: vite.replicate.ts · reviewer: ZCode GLM-5.3 in-session · sha256 f4c56c4e (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 56544768 @ b0212df 2026-08-24)
context: diff 15+8; prior review 56544768 carried; the failure-TTL defect class (one of the twelve) in mind.

## Verdict

Shippable - the delta is exactly the failure-TTL fix plus honest refresh counting.

## Bugs & vulnerabilities

None new. Failed scrapes now cache with failed:true and expire on the 15-minute FAIL_TTL instead of poisoning "publishes no price" for a week; refreshReplicatePrices counts actual refreshes (the old before/after size arithmetic was wrong and could report negative or double).

## Missing safeguards

- (unchanged from prior) collection/price caches are per-process; the persisted price cache write is every-10th scrape + final save - a crash between loses at most 9.

## Fixed since last review

- (prior had no open confirmed findings)

## Verified-correct

- freshPrice's branch (undefined = absent/stale-either-clock, null = known-no-price), save/load round-trip of the failed flag, FAIL_TTL not applied to genuinely-null prices.
