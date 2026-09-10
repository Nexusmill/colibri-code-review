# Colibri review — src/components/StatusFooter.tsx (feature)

- **Source:** `src/components/StatusFooter.tsx` · **sha256:** 47f263c6
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the four instrument windows; FEATURES.md `vram-instrument`; the fmtGb-truncating doctrine (2026-09-03 fix); the dwm artifact-counter honesty; verified absence: no copy-diagnostics, no jump affordances; last touch a0077ba (2026-09-03).

## What this module does

The status strip: the socket lamp, host+ComfyUI-version, queue count, and the VRAM diagnostic — one source of truth for used bytes (the adapter's own counter, falling back to device stats), torch allocated/reserved + RAM, the optimizer sidecar called out as a model when llama-server holds VRAM, resident models with full-size hover + the unload key (waiting out the custom node's 4s counter cache before readback), and the Task-Manager-style per-process table where dwm's artifact values render as em dashes, never as fact.

## Suggested add-ons

**One-press copy diagnostics** — Value Med · Effort S
- What: a small copy key on the diagnostic copying the instrument's full text (device, versions, torch/RAM, resident models with sizes, process table) as plain text.
- Why: this repo's debugging culture lives on these numbers — every bug report pastes them by hand from hovers; the footer is where they all already are. Verified absent.

**Queue window as a jump** — Value Low · Effort S
- "queue 3" (window 3) is not a press; making it seat the Queue surface matches the press-carries-you doctrine (cross-ref the DeckControls done-line add-on — same family).

**VRAM trend line** — Value Low-Med · Effort S-M
- A decaying sparkline of free VRAM behind the head line would surface leaks (the class where free drifts down across a session). Visual element — needs commission.

## Nice-to-haves

- The unload key could name WHAT it will evict (the resident list is right above — a count: "unload 3 models · 9.2 GB").
