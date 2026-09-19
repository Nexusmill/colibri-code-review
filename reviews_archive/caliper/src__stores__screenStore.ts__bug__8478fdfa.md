source: src/stores/screenStore.ts
reviewer: tencent/hy4-preview (scan ladder hunt T2)
sha256: 8478fdfa15647801faac12659f91cb4351a4d1be4f4f0b14e40f108cb6f4fff0
date: 2026-09-19 13:06
mode: bug
context: window OS store; closeByPrefix law excluded

2 findings:
- [MEDIUM] CONFIRMED + FIXED: assetFromOutputs took only video/image as primary - a text-only or audio-only job returned null AFTER openJobOutputs marked it seen, so it never opened a window and could never auto-open later ("words are media" is the interface's own comment). FIXED: primary chain extended to text/audio; pickFiles (assetsStore) now picks text files (.txt/.md/.json). Pinned (pickFiles text test).
- [LOW] OPEN: close/closeByPrefix merge seen ids then slice(-49) - the 50-entry session memory caps at 49 when the seen id was already present (one oldest id evicted early). Cosmetic bookkeeping; deferred.
Scan log: %TEMP%/hunt2/stores__screenStore.md
