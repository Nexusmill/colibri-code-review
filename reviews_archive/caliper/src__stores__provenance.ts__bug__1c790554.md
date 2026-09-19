source: src/stores/provenance.ts
reviewer: tencent/hy4-preview (scan ladder hunt T2)
sha256: 1c7905544fc62521a9606194d13c205a195646862ce86d6ec4cff99ab4cf3502
date: 2026-09-19 13:10
mode: bug
context: record-verb chain (BUGHUNT12 law); server file is the whole truth

1 finding, CONFIRMED + FIXED: [HIGH] send() never checked res.ok - an HTTP refusal (4xx/5xx) of a POST/PATCH/DELETE resolved as success while the optimistic cache had already moved, so the UI kept a delete/save the server never made until a later refresh silently reverted it. FIXED: only transport failures count as "middleware away"; an !ok answer triggers doHydrate so the cache reverts to server truth immediately.
Scan log: %TEMP%/hunt2/stores__provenance.md
