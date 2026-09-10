# Colibri review — src/workflows/fill.ts (feature)

- **Source:** `src/workflows/fill.ts` · **sha256:** 46a9ea98
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the workflow builder every render passes through (queueStore, bench, film's local legs, graph seeding); LTX_DISTILLED_SIGMAS sourced from Lightricks' published example; verified: lora strength literal at 106, negative-slot/template coupling; unchanged since 110acee (2026-08-19).

## What this module does

114 lines: slot-templated workflow filling ({{slot}} substitution, unfilled = loud error), the four templates, `modelConsumers` derived from the template itself, the `finite()` NaN gate at the last build-time point (NaN passes both violations and the filler), `slotsFor` (video bundles demand audio VAE + frames/fps), and `buildWorkflow` — constraints first, the ManualSigmas swap onto Lightricks' published 9-sigma schedule at the 8-step distilled default (any other count falls back to BasicScheduler honestly), and the lora chain rewiring every model consumer.

## Suggested add-ons

**Lora strength from the bundle** — Value Med · Effort S-M
- The R1-confirmed finding's code home: `strength_model: 1` is a literal (line 106). The bundle carries loras as bare filenames; a strength field (schema add-on, R1) flows through slotsFor into the chain. Anima-Turbo's lora is permanently pinned at full strength today.

**Negative-slot/template coupling check** — Value Low-Med · Effort S
- `slotsFor` sets `negative` only when the TEMPLATE declares `hasNegative` (line 78); a bundle whose defaults carry a negative on a negative-less template silently drops it. Today's factory data is consistent (verified: LTX/Krea defaults carry no negative), but custom bundles can hit it — a load-time or save-time warning naming the mismatch is one check in validateFiles's spirit.

**Dimension snap as defense-in-depth** — Low
- width/height are `Math.round`ed here (line 68-69); once the constraint vocabulary (R1) defines multiples, snapping here too catches API-driven builds (benches, film legs) that bypass the deck. Cross-referenced, not separately valuable.

## Nice-to-haves

- The ManualSigmas swap is steps==8-specific; a steps<=8 table for lower counts would need Lightricks' schedule — leave until measured.
