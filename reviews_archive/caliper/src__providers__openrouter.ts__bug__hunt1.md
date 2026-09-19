source: src/providers/openrouter.ts
reviewer: tencent/hy4-preview (scan ladder hunt T1)
sha256: (see session scan log - computed at dispatch; the scan header prints 16 hex chars)
date: 2026-09-19 12:10
mode: bug
context: OpenRouter chat adapter (the everything-gateway brain transport); stream handling matters

2 findings, both CONFIRMED as real stream-hygiene defects, both OPEN for the next remediation session:
- [MEDIUM] readSseLines never flushes the TextDecoder at stream end - a final multi-byte character split across the last chunk boundary is silently truncated (the last delta corrupted or dropped).
- [MEDIUM] readSseLines leaks the reader/connection on early exit (no cancel/release).
Full finding text with fixes: %TEMP%/hunt1/providers__openrouter.md (this session) and the git-history commit message.
