source: src/stores/assetsStore.ts
reviewer: tencent/hy4-preview (scan ladder hunt T2)
sha256: 56a0a8c2d4a37c493350c6df3a149e613889712a98e85c3efd1e26cce7a99b41
date: 2026-09-19 13:18
mode: bug
context: library assets; hydrate-once set; dismiss contract in the module header

2 findings:
- [HIGH] CONFIRMED + FIXED: hydrate never consulted the dismiss set (the module's own header promises "deleted live items are held out by the dismiss set") - a dismissed live job whose provenance record landed later resurrected into the library, silently undoing the user's delete. FIXED: the hydrate loop skips dismissed ids and the items filter holds them out. Pinned (record-lands-late test).
- [HIGH] PLAUSIBLE-hygiene, deferred: hydrated.add runs before filesFromHistoryOutputs - if that shared coercion ever threw, the id would be marked hydrated while the asset never landed (hidden forever). No throw path demonstrated in its current defensive form; noted for the next pass.
Scan log: %TEMP%/hunt2/stores__assetsStore.md
