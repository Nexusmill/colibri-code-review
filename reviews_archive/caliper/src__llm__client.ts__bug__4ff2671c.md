# colibri bug review - src/llm/client.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 4ff2671c - 2026-08-27
mode: bug - context: full-sweep round five

## Verdict

Clean - VRAM purge only for the local brain (cloud spawns touch nothing); agent wrappers propagate server errors honestly.
