# Colibri review — src/components/CloudPane.tsx (feature)

- **Source:** `src/components/CloudPane.tsx` · **sha256:** fd956975
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the center-left pane's cloud seat, sharing ModelPicker's SchemaField; FEATURES.md `generate-cloud-pane`; the measured price lesson (2026-08-28: omitted duration/resolution billed the default tier at 2.3× the quote — memory: always send explicit duration+resolution); verified absence: no duration/resolution pinning; last touch a311d65 (2026-08-27).

## What this module does

The schema-driven cloud seat: loads the chosen model's published inputs (catalog first, direct fetch for Replicate), seeds defaults including first-enum, pins required fields + image inputs (whatever they're named), folds the rest behind advanced, RUN quoting the page's own figure with the pricing blob above, SET AS DEFAULT writing the route without a settings trip, the deck's status well fed through cloudRun, and the artifact opening as a screen window + joining the library.

## Suggested add-ons

**Pin duration + resolution for video models** — Value Med-High · Effort S
- What: for video-kind models, pin the duration and resolution fields (even when the schema marks them optional) with visible values, the same way image inputs are pinned.
- Why (verified): `pinned` (CloudPane.tsx:68-70) is required + image inputs only. The film path learned the hard way that omitting these lets the engine bill its DEFAULT tier — 46 seedance renders at $0.1525 each against a bill that quoted the 480p rate ($7.01 real vs $4.82 approved). The pane is the one-off path into the same engines with the same exposure; a schema that doesn't REQUIRE resolution still lets the provider CHARGE its default.
- How: extend the pinned predicate with `kind === "video" && /duration|resolution/i.test(k)`; the film flow's own tier mapping (height ≤480/720/1080) is the precedent.

**Per-model value memory** — Value Med · Effort S
- Filed in the ModelPicker review (shared pattern, both effects re-seed from the schema on every mount); applies identically here.

**Idle-state next click** — Value Low · Effort S
- The idle line names "the LOCAL key returns your controls" — make LOCAL/CLOUD keys reachable from the pane header in one press (they live in well 4 today).

## Nice-to-haves

- The pricing blob could carry a copied-on-click affordance (the R1 price-provenance theme at the one-off scale).
