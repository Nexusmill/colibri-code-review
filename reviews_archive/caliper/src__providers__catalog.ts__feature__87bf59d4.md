# Colibri review — src/providers/catalog.ts (feature)

- **Source:** `src/providers/catalog.ts` · **sha256:** 87bf59d4
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the role→backend catalog (docs/GENERATION_PROVIDERS.md era); forRole still resolves film.score (vite.film's resolveScoreEntry) while keyframe/segment moved to the routes system; the minimax rate-card comment is the price-truth doctrine's origin stone; unchanged since a31fcb5 (2026-08-27).

## What this module does

64 lines: the generation-role catalog (anima keyframes local, LTX segments local, minimax music-2.6 on Replicate at the RATE-CARD $0.15 — the comment records the median-vs-rate correction in full), `forRole` resolution, and the SpendRecord shape with `spendTotal` — the ledger every gate and bill reads.

## Suggested add-ons

**Retire the superseded roles honestly** — Value Low-Med · Effort S
- film.keyframe and film.segment route through the universal model routes today (resolvedRoute in vite.film); the catalog's local entries for them are read only as the score overlay's default shape. Either shrink the Role type to what's live (score) or comment the two entries as overlay-shape-only — the file currently reads as if all three roles resolve here, which is how drift starts.

**SpendRecord gains a source field** — Value Low · Effort S
- Records carry costUsd; null-cost entries tally 0 with a label note applied at the call site. A `source?: "usage" | "rate" | "unknown"` field makes the ledger self-describing (the R1 provenance theme at the ledger level) — the bill's gate compares against these sums.

## Nice-to-haves

- The $0.15 rate rides a comment as doctrine; folding owner-verified prices into one shared table (vite.film's OWNER_PRICES) would give the score entry a single home.
