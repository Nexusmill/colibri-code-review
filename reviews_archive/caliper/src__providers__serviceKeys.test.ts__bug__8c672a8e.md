source: src/providers/serviceKeys.test.ts
reviewer: tencent/hy4-preview (scan ladder M2, colibri bug mode via headless hy4 CLI)
sha256: 8c672a8e4095963f954f7acae0dc5d5686a15045e682ee4a9531ce8d0806e8f0
date: 2026-09-19 11:10
mode: bug
context: the guarded catalog's contract; the NEW hint pin (99f1d9b) named as the newest guard

Two findings, both MEDIUM, both CONFIRMED and remediated the same session:

## Finding 1 [MEDIUM] — Missing negative path in isServiceKeyId validation (vacuous whitelist guard)
Every negative case was blocklist-shaped (traversal/empty/undefined) — a blocklist regression would pass the suite. FIXED: isServiceKeyId("openai") and isServiceKeyId(null) now asserted false.

## Finding 2 [MEDIUM] — Case-sensitive not.toContain("to come") is a vacuous guard against capitalized variants
"(To Come)" would pass the pin. FIXED: not.toMatch(/to come/i).
