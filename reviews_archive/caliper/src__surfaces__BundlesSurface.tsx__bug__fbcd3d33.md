# colibri bug review - src/surfaces/BundlesSurface.tsx

reviewer: ZCode (GLM-5.3, in-session) - sha256 fbcd3d33 - 2026-08-27
mode: bug - context: full-sweep round five; bundlesStore save/load traced

## Verdict

Clean code-wise - addFromCatalog validates before installing; structuredClone edit copies; gated-install flow honest.

## Missing safeguards (design decisions, not fixes)

- Bundle remove is one click and unrecoverable (no backup of bundles.json).
- The editor modal's backdrop click silently discards typed edits.
