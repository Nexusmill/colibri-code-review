# Colibri review — src/surfaces/GenerateSurface.tsx (feature)

- **Source:** `src/surfaces/GenerateSurface.tsx` · **sha256:** f943cbc4
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** reads bundlesStore + queueStore + constraints + generateStore (cloud seat); the fixed-geometry Row pattern (dim+inert, never removed); FEATURES.md `generate-source-select`, `generate-cloud-pane`, `stepper-detent`; the FRAMES_MAX comment at line 23; last touch 82ff326 (2026-08-31).

## What this module does

The two glass panes: the parameter pane is one seat with two modes — LOCAL (instrumented controls: prompt/negative, steps scrub+slider, CFG with the PINNED latch, fps, frames with detent snapping, freely-typeable width/height, seed with the single Random/Fixed key, advanced drawer) or the schema-driven CloudPane when the source selector seats a cloud model. Rows for unused params stay present but dimmed and inert (fixed panel geometry for the art). The render pane hosts ScreenStage with a running badge; the snap correction and queue-error chips ride the pane across both seats.

## Suggested add-ons

**Aspect/size preset keys** — Value Med · Effort S
- What: 2-3 chips setting width/height to engine-legal combos for the selected bundle (e.g. 768×512 / 512×768 / square), each an exact multiple pair.
- Why: width/height are the freest controls in the app (any 64-4096 value, no multiple enforcement — verified, see the constraints.ts review); presets give the one-tap path to legal shapes and reduce the wrong-dimension waste class at its source. Pairs with, not replaces, the constraint vocabulary add-on.
- How: constants per bundle kind beside the inputs; sets both fields through the existing `set()`.

**Prompt history recall** — Value Med · Effort S
- What: a small "recent" affordance under the prompt textarea listing the last few prompts queued for this bundle (click to restore).
- Why: prompts persist per bundle but editing overwrites; REPRODUCE covers rendered work only, and a good prompt discarded by a paste is gone. Click-safe by construction (restoring text writes nothing to disk).
- How: store-side history (bundlesStore review's add-on) + a list here; exactly one restore action per row.

**VRAM-fit estimate beside RUN** — Value Med-High · Effort M
- Filed in the queueStore review; the display naturally lives in this pane beside the queue-error chip. Cross-referenced, not duplicated.

## Nice-to-haves

- The 4s snap toast could state the DETENT grammar ("snapped to 8n+1") — it already does; no change. Recorded as a verified non-gap.
- Placeholder copy is bundle-aware (the Anima white-out hint) — good pattern; extend to Krea/LTX with their known gotchas as they're documented in the corpus.
