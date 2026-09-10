# colibri bug review - src/film/calibrate.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 13542250 - 2026-08-27
mode: bug - context: full-sweep round five

## Verdict

Clean - cap-aware battery plan with a conservative unpriced estimate that cannot crowd out the known-cheap; service tiers keyed from full service/slug references (consistent with round 3's win-rate fix).
