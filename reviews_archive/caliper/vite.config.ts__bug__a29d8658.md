# colibri bug review - vite.config.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 a29d8658 - 2026-08-27
mode: bug - context: full-sweep round five

## Verdict

Clean - Origin stripped on both proxied paths (the aiohttp 403 lesson); the websocket stays direct to 8188 per the architecture note; port 4173 (the Windows excluded range).
