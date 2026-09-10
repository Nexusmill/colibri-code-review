# colibri bug review - src/stores/bundlesStore.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 436cd891 - 2026-08-19T07:55:05
mode: bug - context: full-session repo knowledge (call sites traced by read; stores/surfaces/api cross-checked)

## Verdict

Shippable. Findings below survived the adversarial pass; refuted drafts were deleted.

## Bugs & vulnerabilities

- No new findings. Load-refusal issue surfacing, id migration + auto-PUT, and VRAM-gated select all traced; select() with the vram node unreachable (getCaliperVram catch -> null -> no models) skips the auto-unload on tight VRAM - PLAUSIBLE degradation, noted not fixed.
