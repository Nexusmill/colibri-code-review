# colibri bug review - vite.power.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 c8627db3 - 2026-08-27
mode: bug - context: full-sweep round five

## Verdict

Clean - the stop is OBSERVED before any restart/off claim; detached restart tail survives app death; the sidecar dies with OFF.
