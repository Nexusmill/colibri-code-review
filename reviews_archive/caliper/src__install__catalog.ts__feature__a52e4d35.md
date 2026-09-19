# Colibri review — src/install/catalog.ts (feature)

- **Source:** `src/install/catalog.ts` · **sha256:** a52e4d35
- **Reviewer:** ZCode (GLM-5.3, in-session) · **Date:** 2026-09-14 · **Mode:** feature (FRESH — no prior feature review; bug+spec reviews exist)
- **Context pack:** #8 by import PageRank (isCatalogBrain, 7 in-degrees); importers FirstRun/install plan/vite.llm/settings; the Theme-D spree touched the LLM shelf (contextTokens grounded 2026-09-06); FEATURES rows `first-run`, `local-brain-shelf`; full read of the LLM half + manifest shapes (230 lines total).

## What this module does

Two catalogs in one file. The RENDER side: one `BundleManifest` per supported bundle, each file declared with its KIND and either a verified HF-resolve URL (host-allowlisted by the downloader) or a MANUAL note — adding a source is data, not code. The LLM side: the GGUF shelf for the llama.cpp sidecar — one file each into models-llm/, filenames+bytes verified against the HF tree API, roles spoken (brain seats vs the embedder/reranker pair that must never be seated as brain), `contextTokens` grounded from each model card, and `isCatalogBrain` as the gate.

## Suggested add-ons

**Size + sha256 on CatalogFile (render side)** — Value Med · Effort S-M
- What: `bytes?: number` and `sha256?: string` per render-catalog file; the downloader verifies after download (size always, hash when present).
- Why (verified): CatalogFile carries only `kind/name/url/manual` — the render downloader has no declared size or hash to verify against; the install-hardening tail names exactly this gap (the .part-rename: a truncated download renames into place). The LLM half already carries `bytes` (verified against the tree API) — the render half is the unverified sibling. G17's ship-pinned doctrine (hash-verified against a manifest) is the house rule for anything bundled.
- How: data entries (sizes/shas from the HF tree + a one-time hash pass), then the downloader's post-download check mirrors what the LLM path should also gain.

**Serve each model's context window (-c per model)** — Value Med · Effort S
- What: pass `contextTokens` (clamped to a sane ceiling) to the llama-server spawn so the sidecar serves what the model card promises.
- Why (verified against the field's own comment): `contextTokens` documents "the sidecar serves 16k regardless - this is the ceiling, spoken where it decides a pick" — the catalog KNOWS the window and the spawner ignores it; a 262k-context brain is served at 16k and the picker's context-based advice overstates what a session actually gets.
- How: vite.llm's spawn adds `-c min(contextTokens ?? 16384, 131072)` (VRAM-bounded — the 16 GB card shares with ComfyUI; cap conservatively); the field stops being documentation-only.

**MANUAL-note files as first-class blocked state** — Value Low · Effort S
- What: the install plan already surfaces manual files; a per-manifest `blockedBy: string` (the human note) rendered at first-run would say WHY a bundle can't one-click install, in the catalog's own words.
- Why: manual notes live in data and render where plan.ts puts them; the catalog's voice (login-gated vs local-derivation) is the difference between "waiting on me" and "impossible".
- How: pass-through display; no downloader change.

## Nice-to-haves

- A `deprecated?: boolean` flag mirroring the cloud catalog's GONE-from-catalog treatment (a HF file that moves 404s today; the downloader reports the fetch failure but the catalog keeps promising it).
