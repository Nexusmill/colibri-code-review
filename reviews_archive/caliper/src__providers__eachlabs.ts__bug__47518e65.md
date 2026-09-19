source: src/providers/eachlabs.ts
reviewer: tencent/hy4-preview (scan ladder hunt T2, headless hy4 CLI)
sha256: 47518e6589e305cec239cef22cdb4a1129a8f57b05f58459e6cc6dcef46b65f2
date: 2026-09-19 13:00
mode: bug
context: EachLabs adapter; BUGHUNT11 timeout/backoff laws excluded

2 findings, both CONFIRMED + FIXED (literal JSON null bodies resolve, not reject):
- [MEDIUM] a null create body crashed with TypeError instead of "eachlabs returned no prediction id". FIXED: catch-to-null + ?? {}.
- [MEDIUM] a null error body crashed the !ok branch. FIXED: ?? {} coercion.
Scan log: %TEMP%/hunt2/providers__eachlabs.md
