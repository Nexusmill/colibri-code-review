# colibri bug review - src/api/catalog.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 93147b7a - 2026-08-27
mode: bug - context: full-sweep round five

## Verdict

Clean - the one mapping every price-bearing UI reads (deck dropdown, settings, pane); schemas carried for OR/EL, lazy-loaded for replicate.
