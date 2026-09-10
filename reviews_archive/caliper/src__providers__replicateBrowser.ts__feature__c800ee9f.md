# Colibri review — src/providers/replicateBrowser.ts (feature)

- **Source:** `src/providers/replicateBrowser.ts` · **sha256:** c800ee9f
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the pure browser logic (owner 2026-08-21: pricing scraped tolerantly; 2026-08-24: RATE CARD first — medians underprice 75x); consumed by vite.replicate + the score overlay in vite.film; verified: `rates` map consumed only by its own test, budget cutoff ranks by median only; unchanged since f9c5a4d (2026-08-24).

## What this module does

222 pure lines: the 8-category taxonomy, collection mapping (dedupe by slug, popularity sort, extras union), the price scraper — RATE CARD FIRST (metric_display/price pairs, input/compute metrics skipped for the primary, ALL rates kept in a map "for option-priced estimation"), then p50 median, then unit-JSON, then plain sentences — `budgetCutoff` (cheapest quarter by median), `withBudget`, the ScoreChoice overlay (a chosen model carries its OWN price; the default's catalog price applies only to the default itself), fmtRuns, `sniffArtifactExt` (magic bytes name the artifact), `findImageInput` (the schema-first keyframe feed), fmtUsd.

## Suggested add-ons

**Consume the `rates` map — option-priced estimation** — Value Med · Effort S-M
- What: an `estimateRunCost(values, rates)` helper: given the chosen options (resolution, duration, draft mode), quote the matching per-unit rate instead of the primary.
- Why (verified): PriceInfo.rates collects every per-unit rate the page states and NOTHING in production reads it (only its own test does) — the comment that declared its purpose ("for option-priced estimation") describes a consumer that was never built. The bill's parseTiers re-scrapes the BLOB because this map isn't consulted; one estimation helper serves both.

**Rate-card budget ranking** — Value Med · Effort S
- `budgetCutoff` ranks by p50 median only (line 144); per-second/per-image rate-card models "do not join the ranking" per the comment — but rateUsd is now the PRIMARY price and unit-comparable within a leg (all shoot engines are per-second). Ranking the video shelf's BUDGET badge by rateUsd (falling back to p50) aligns the badge with the price the bill actually quotes.

**Audio sniffing completeness** — Value Low · Effort S
- `sniffArtifactExt` catches mp3/wav/ogg; flac ("fLaC") and m4a (MP4 container) land as "bin". Score engines emit them; two more magic-byte rows.

## Nice-to-haves

- `clampDescription` at 110 chars is fine; no change.
