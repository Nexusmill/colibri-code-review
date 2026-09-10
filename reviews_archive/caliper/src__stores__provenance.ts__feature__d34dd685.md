# Colibri review — src/stores/provenance.ts (feature)

- **Source:** `src/stores/provenance.ts` · **sha256:** d34dd685
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the library's client memory — consumed by queueStore (save/patch), assetsStore (hydrate), provenance UI (refresh/remove); FEATURES.md `provenance-shared` (server-side truth, every browser sees every render); the 2026-08-28 separate-budgets lesson; last touch 41fb288 (2026-08-28).

## What this module does

The machine-wide library memory's client half: hydration treats the SERVER file as the whole truth (no legacy merge-back — the resurrection bug), with the legacy localStorage seed serving only the pre-fetch tick and offline sessions; a 1000-record window (room for a film's records AND the one-off shelf); save/remove/patchOutputs keeping cache and server file in lockstep (deletes leave together — no ghosts); refreshProvenance pulling records added since boot; latestRenderFor for the post-reload Generate pane.

## Suggested add-ons

**Patch-based persistence** — Value Low · Effort S-M
- Every save/remove PUTs the entire ≤1000-record array through the proxy; a per-record PATCH protocol (or debounced flush) would shrink writes. Local server, small file — honestly Low until provenance grows.

**Record versioning** — Value Low · Effort S
- ProvenanceRecord has no schema stamp; the file predates outputs-patching and could grow fields (model route used, cloud cost) with no migration story. A `v` field costs one line now, saves a migratePersisted-style pass later (the bundlesStore precedent).

## Nice-to-haves

- A `countFor(bundle)` helper — latestRenderFor's find pattern repeats in consumers; trivial.
