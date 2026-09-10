# Colibri review — src/providers/openrouterVideo.ts (feature)

- **Source:** `src/providers/openrouterVideo.ts` · **sha256:** c09230c4
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack**: the OpenRouter shelf mapping (owner 2026-08-22: "the price isn't one number, it's conditional — it has to be a blob"; 2026-08-23: one formatting path); synthesizeOrSchema feeds CloudPane/ModelScreen and the film SHOT route; verified: last_frame filtered but never synthesized; unchanged since 3f395f0 (2026-08-23).

## What this module does

The OpenRouter catalog mapping: sku normalization (`duration_seconds*` already USD/s, `cents_*` halved, `video_tokens*` honestly flagged un-priceable), `orPriceSummary` — THE one-line price every UI quotes (page headline first, skus as the honest fallback; the two-paths bug is dead), `synthesizeOrSchema` — the capability record becomes the form (prompt, first_frame image, duration/resolution/aspect enums with sensible defaults, generate_audio, seed), `parseOrPagePricing` (headline = FIRST from-rate, never min-of-page — the i2v-floor bug), and the video/image mappers.

## Suggested add-ons

**last_frame synthesis** — Value Med · Effort S
- What: `frameImages` collects first_frame|last_frame (line 93), but only first_frame ever becomes a form field (94-96). A model supporting last_frame gets no way to receive one.
- Why: last-frame video is the natural bookend tool (ending on a specified frame — the turn's landing); the capability arrives in the raw record and is silently dropped at synthesis. One more property when `last_frame` is listed, mirroring the first_frame field.
- How: `properties.end_image = { type: "string", format: "uri", … }` gated on the same list; runOrVideo forwards it if the API names it (verify per-model at adoption).

**Option-priced estimation from skus** — Value Low-Med · Effort S
- perSecondUsd takes the MINIMUM eligible sku; a duration×resolution picker could quote the matching sku for the chosen options instead of the floor. Pairs with the replicateBrowser `rates` finding — both providers collect more price truth than they consume.

**Audio default note** — `generate_audio` defaults true (line 103); the film flow overrides it; a one-off pane run on an audio-capable model bills audio by default. A hint on the field ("audio adds cost — the film flow mutes it") or default-false is an owner call (the no-audio ruling was film-scoped).

## Nice-to-haves

- `parseOrPagePricing`'s context-window scrub is battle-tested; a fixture corpus of real pages in tests would pin it further. Low.
