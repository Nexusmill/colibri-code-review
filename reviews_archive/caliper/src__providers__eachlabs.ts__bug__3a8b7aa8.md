# colibri bug review - src/providers/eachlabs.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 3a8b7aa8 - 2026-08-27
mode: bug - context: full-sweep round five

## Verdict

Clean - failure reasons read from output-then-logs (the live music-03 empty-reason lesson is encoded); cents-to-USD conversion; cheapest-first mapping with nulls last.
