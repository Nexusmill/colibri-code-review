# colibri bug review - src/install/catalog.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 870cd7e2 - 2026-08-27
mode: bug - context: full-sweep round five

## Verdict

Clean - pure data; every URL is a huggingface.co resolve link matching the downloader's allowlist.
