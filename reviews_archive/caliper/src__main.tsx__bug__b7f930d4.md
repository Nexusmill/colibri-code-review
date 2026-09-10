# colibri bug review - src/main.tsx

reviewer: ZCode (GLM-5.3, in-session) - sha256 b7f930d4 - 2026-08-27
mode: bug - context: full-sweep round five

## Verdict

Clean - provenance hydrates before first render so every surface's first read sees the library.
