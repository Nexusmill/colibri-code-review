# Colibri review — src/components/DeckControls.tsx (feature)

- **Source:** `src/components/DeckControls.tsx` · **sha256:** be37f2c1
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the four measured wells; reads bundlesStore/queueStore/routesStore/generateStore + llm client + catalog; FEATURES.md `generate-source-select`, `render-guard`, `optimizer-console`; verified absence: no click affordance on status lines; last touch 91620a1 (2026-09-02).

## What this module does

The deck: well 1 the Generate legend; well 2 Queue render (constraint-gated, single-guard toggle, "queue = local" note when the pane seats cloud); well 3 the status instrument — cloud-run line leading over local progress (R3), last terminal job (done·seed / failed), untracked server-busy honesty, AI ON/OPTIMIZE/SET UP AI with pending-answering labels and LOUD provisioning, and the VRAM Unload/Keep prompt; well 4 SourceSelect — LOCAL|CLOUD keys, the cloud-only profile's own truth, the type→service→model cascade with honest loading/error/empty states and seated-model liveness, all through the shared DeckDropdown (keyboard cursor, price on the row).

## Suggested add-ons

**The status well's done-line is a jump** — Value Med · Effort S
- What: "done · seed N" (line 173) becomes a press — one click opens the output (openAsset with reveal, the ruling-40 pattern) or seats Outputs.
- Why: pervasive-responsiveness — the well ANNOUNCES the finished render but the press that sees it lives elsewhere; every other announcement in the app carries its own next click. The failed line could jump to Queue similarly.

**Estimated time beside progress** — Value Med · Effort M
- The display side of the queueStore ETA add-on (R1): "KSampler 12/30 · ~2m left (7 measured runs)". Sourced from the corpus or absent honestly.

**OPTIMIZE key as a brain menu** — Value Low-Med · Effort S
- The key currently cycles on/off with default-brain semantics; a long-press or secondary chip could open the brain picker (the console owns it today — the deck is where AI is first touched).

## Nice-to-haves

- The catalog retry button (SourceSelect) could auto-retry once on error before showing the manual retry — halves the transient-error clicks. Low.
