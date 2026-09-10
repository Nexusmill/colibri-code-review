# colibri bug review - src/App.tsx

reviewer: ZCode (GLM-5.3, in-session) - sha256 76f94f4a - 2026-08-27
mode: bug - context: full-sweep round five; callers and contracts traced in-session

## Verdict

Clean - socket lifecycle (reentrant-safe per the ws review), hotkey typing guards, 16:9 resizeTo in try/catch (tab-refused), stage-scale fit on resize.
