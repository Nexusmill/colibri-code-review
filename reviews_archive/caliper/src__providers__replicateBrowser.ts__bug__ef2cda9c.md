<!-- source: src/providers/replicateBrowser.ts | reviewer: glm-5.3-zai-in-session | sha256: ef2cda9c39318aa7da247d7fd4e1c0d9c36ffb107392287e87cd3e5fc31635fb | date: 2026-09-16 | mode: bug -->
<!-- context: owner commission 2026-09-16: colibri bug hunt on the NEXT top ten files by import PageRank (the board past the hunted ten); fresh-context subagent per file under the 0.3.0 doctrine (prior review = context, never a skip; delta files report new/changed only + close the loop). -->

## Verdict

Not clean — 3 new findings (1 MEDIUM, 2 LOW). The delta (commit f921506, 2026-09-05 — the only change since sha c800ee9f) adds `tiersFromRates`, `estimateRunCost`, and the dominant-rate-family rewrite of `budgetCutoff`/`withBudget`. The in-file math is solid (billable-metric guard applied on every rates read, per-second filtering, honest floor/fallback bases, quartile arithmetic unchanged from the old code, family gating keeps cross-unit rows unbadged — all verified against 22/22 passing tests, `npx vitest run src/providers/replicateBrowser.test.ts`). The defects are at the new functions' boundary with their one production consumer: the battery estimate bypasses the owner-override price map and discards the basis string the function was built to speak, and the per-image branch prices "per thousand" units at face value.

## Fixed since last review

The prior artifact (.colibri_reviews/src__providers__replicateBrowser.ts__bug__c800ee9f.md, 2026-08-27) recorded verdict "Clean" with zero findings — nothing was open, so there is nothing to mark fixed/still-open/verified-stale. (Its feature-mode sibling's suggestion "consume the rates map" was implemented in this delta as `estimateRunCost` + `tiersFromRates` — verified consumed at vite.film.ts:2035 and vite.film.ts:2632.)

## Bugs & vulnerabilities

**[MEDIUM] estimateRunCost's only production caller bypasses OWNER_PRICES and discards the basis string — the battery's per-clip record can quote a page/median price for an owner-priced engine, unmarked** - `line 174` (function) + consumer `vite.film.ts:2632`
- What: `estimateRunCost(info, opts)` accepts only the scraped `PriceInfo`; the owner-override layer (`OWNER_PRICES`, vite.film.ts:223) is applied by consumers everywhere else — buildLadder's price-truth order (vite.film.ts:283-296, owner first), the bill's tier map (vite.film.ts:2035, owner tiers spread last), and even the same line's openrouter branch (`e.priceUsd` is owner-aware from buildLadder). The battery call site passes `replicatePriceInfo(e.slug)` raw, so a replicate engine with an owner entry — `replicate/prunaai/p-video` (owner perSecond $0.02, a shoot engine eligible for the `buildLadder("cheap")` battery pool) — gets its estPerClip from the page rate card or, worse, the p50 median fallback (the function's own doc: "medians underprice ~75x"). Additionally `est.basis` — the provenance marker the function exists to produce ("the bill names each line's price basis", docs/FEATURES.md `film-bill-basis`) — is never read at the call site; only `est.usd` survives into `estPerClip` (vite.film.ts:2644) and the corpus line prints a bare `≈$X/clip` (vite.film.ts:2657).
- Trigger: run the calibration battery over a replicate engine that has an OWNER_PRICES entry (owner/page disagreement) or whose page publishes only a median — then read `knowledge/measured-results.md` (append-only, "the optimizer's memory") or the persisted battery health.
- Impact: the optimizer's durable memory and battery-health file record a non-owner price basis with no source marker — exactly the wrongness class the owner's 2026-08-24 ruling ("owner-verified overrides rule") and the film-bill-basis feature were built against. Not a spend gate (the approval total `plan.estTotalUsd` comes from owner-aware `priceUsd`), so no direct mis-spend; severity capped at MEDIUM.
- Fix: at vite.film.ts:2632 consult `ownerPrice("replicate", e.slug)` first (perSecond × meanSeconds, basis "owner-verified") and fall through to `estimateRunCost` otherwise; persist `est.basis` alongside `estPerClip` (or prefix the corpus line with it). CONFIRMED (code-verified at both sites; the openrouter/replicate asymmetry within the same expression rules out a deliberate page-only choice).

**[LOW] "per thousand" rate units are priced per unit — a legacy-shape page overquotes 1000x** - `line 201`
- What: `scrapePrice`'s legacy fallback (`line 128-129`) returns `rateUnit: "thousand output images"` (title `"per thousand output images"`, shape lifted live in the test file), and the per-output branch `/image|video|run/i.test(info.rateUnit)` matches "thousand output images" — returning `rateUsd * (opts.images ?? 1)`. $1 per thousand = $0.001/image is quoted as $1/image. The plain-sentence sibling (`line 130-131`) got this right: its regex captures "per thousand" and deliberately returns text only, exposing no `rateUsd`.
- Trigger: a model page publishing the legacy JSON-title shape with "thousand" and no `metric_display`/p50, fed to `estimateRunCost` — including seconds-only callers (the battery), which fall through to this branch with `images` defaulting to 1.
- Impact: 1000x overquote — fails safe direction, and today's only consumer is the record path from finding 1; kept LOW. CONFIRMED by trace + live-captured shape; production reachability rare (video pages in the battery rarely carry this legacy image-model shape).
- Fix: in `estimateRunCost`'s per-output branch, skip (or divide by 1000 for) units matching /\bthousand\b|\bper 1,?000\b/ — mirroring the plain-text path's refusal.

**[LOW] floor basis mislabels a tiered rate as "base rate, treat as a floor" when the card has no untiered second unit** - `line 195`
- What: with a requested resolution no unit matches, `base = secondUnits.find(!/480p|720p|1080p/) ?? secondUnits[0]!` — if every second unit is tiered (e.g. only `"output second (1080p)"`), the 1080p rate is quoted for a 720p request under the basis `"(720p unstated - base rate, treat as a floor)"`. A higher tier's rate is not a floor for a lower tier; the label inverts the direction of the error.
- Trigger: a rate card publishing only resolution-tiered second rates, plus a caller passing `resolution` — no production caller passes `resolution` today (tests only), so this is PLAUSIBLE, unverified because no captured live shape has tier-only second rates.
- Impact: a wrong direction hint on an overquote; low.
- Fix: when the base-fallback lands on a tiered unit, say so in the basis ("(720p unstated - quoted at the card's 1080p rate)") or widen the band to null.

## Missing safeguards

- `withBudget` (line 245) recomputes `dominantRateFamily(base)` that `budgetCutoff` (line 235) already computed internally — harmless duplication today, but the two can silently diverge if one is ever edited alone; hoist the family out of `budgetCutoff`.
- `dominantRateFamily` (line 230) breaks count ties by Map insertion order (= runCount sort order) — deterministic but arbitrary; a tie between "output image" and "output second" families decides which rows can badge, unmarked. A `Math.max` on a canonical unit sort (or exposing the tie in the return) would make it auditable.
- `tiersFromRates` (line 163) recognizes only 720p/1080p tokens — 480p/4K rate units resolve nothing (deliberate per the comment, but the bill's finish vocabulary already includes "2K" via FINISH_TIERS; if pages start publishing "(2k)" units they will be silently dropped from `shootTier`).
- `estimateRunCost` ignores draft-mode rates entirely (`draftPerSecond` lives only in OWNER_PRICES) — an option-priced estimate for a draft-mode run has no path through this function; worth a doc comment saying drafts are owner-map-only so future callers don't assume coverage.

context-pack: jcodemunch local/Caliper find_importers + search_text; consumers read at vite.film.ts:219-335 (OWNER_PRICES, price-truth order), 2010-2075 (tierOf/tier map), 2540-2668 (battery), vite.replicate.ts:16-130 (price cache, no owner layer); tests read in full; vitest 22/22 green; delta isolated to commit f921506 via per-commit sha256 walk.

new-findings: 3
