# colibri bug review - src/providers/openrouter.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 a195fd9c - 2026-08-27
mode: bug - context: full-sweep round five

## Verdict

Clean - chat parse, true-cost math across all rounds, four-decimal sub-dime formatting; hourly pricing cache (nulls cached on fetch failure, but pricing is a cheap per-model refetch).
