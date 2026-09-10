# Colibri review — vite.replicate.ts (feature)

- **Source:** `vite.replicate.ts` · **sha256:** f4c56c4e
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the price pipeline's server (owner 2026-08-21: pricing not in the API, not one format; 2026-08-24: the refresher); consumed by the ladder (replicatePriceInfo), the film engine (fetchModelDetail/readScoreChoice), CloudPane/ModelPicker via api/catalog; verified: `stale: 0` is a dead literal; last touch 19bcffc (2026-08-26).

## What this module does

The Replicate middleware: collections cached 10 minutes; the per-page price scraper (7-day cache persisted to disk, 15-minute failure clock so a transient timeout never reads as "publishes no price" for a week, polite 300ms gaps, batched cache writes); the background refresher walking all four generation categories on a 12-hour timer (wired in vite.film) and on demand; lazy enrichment of listed models; `fetchModelDetail` reading the openapi Input schema server-side; the generic /run path (magic-byte extension sniffing, traversal-safe film-id dir, provenance); the persisted score-model choice; mergeExtras guaranteeing minimax/music-2.6 is always listed.

## Suggested add-ons

**Honest refresh reporting** — Value Med · Effort S
- What: `refreshReplicatePrices` returns `{ refreshed, stale: 0 }` — `stale` is a hardcoded 0 (verified). Count what remained unfetchable (failed scrapes, unreachable categories) and surface it; the prices-refresh action's reply and the settings console can then say "refreshed 84 · 6 failed (they retry in 15 min)".
- Why: the price-truth doctrine's machinery is honest about per-page state but its aggregate report is a stub; a silent partial refresh reads as complete.

**Price-change history into the corpus** — Value Med · Effort S-M
- The cache overwrites on every refresh; a rate that MOVED is invisible. On a changed rateUsd, append a measured-results entry ("price change: <slug> $0.02 → $0.03/s, page rate card") — the append-only corpus is the established home, and it explains why a REPRODUCE bill re-priced at today's numbers differs from the film's recorded spend.

**Rate-priced budget ranking** — filed in the replicateBrowser.ts review (the cutoff ranks by median only, the rate card is already the primary price) — the data flows through this module's cache.

## Nice-to-haves

- The collection cache is in-memory only (10-min TTL, fine); the price cache persists — the asymmetry is deliberate and correct.
