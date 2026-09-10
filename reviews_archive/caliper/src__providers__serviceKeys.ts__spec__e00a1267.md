# Spec review — src/providers/serviceKeys.ts

- Source: `src/providers/serviceKeys.ts` (25 lines) · Reviewer: ZCode in-session (GLM-5.3) · sha256: `e00a12673bda4731ee9b933ad7ebaf0edf986d9ac8e43a82f25c2688e8654002` · 2026-08-31 · mode: **spec** · registry: `spec/settings-keys.json` (+ WIZ-KEY-GATE id set)
- Context pack: full read; key id set cross-checked against WIZ-KEY-GATE's unlocking set and FEATURES settings-keys ("six key rows").

## Verdict
Conforms — six keys with ids exactly matching the contract's unlocking set (replicate, openrouter, eachlabs present among huggingface/spacexai/groq). `isServiceKeyId` guards the write route's id validation.

## Divergences
None. (Staleness note, non-spec: hints say openrouter/eachlabs adapters "to come" — both are live surfaces per FEATURES optimizer-cloud-brain / replicate-models. Comment-only.)

## UNJUDGEABLE HERE
- SET-KEYS-ONE-PLACE observable (SAVED chip, no typing box, CLEAR-then-paste) — settings window component + vite.keys.ts.
- WIZ-KEY-GATE behavior (film path live/not-live with reasons) — wizard layer.
