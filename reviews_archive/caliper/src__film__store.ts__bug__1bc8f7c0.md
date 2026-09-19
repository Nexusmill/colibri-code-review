source: src/film/store.ts
reviewer: tencent/hy4-preview (scan ladder hunt T2)
sha256: 1bc8f7c0912b474341b842853b6c66880be98627f45497c4b8f92fb226ad601b
date: 2026-09-19 13:02
mode: bug
context: film state store; world-model-first laws excluded

1 finding, CONFIRMED + FIXED: [LOW] slugify sliced AFTER the dash trim, so truncation could reintroduce a trailing separator the trim had removed. FIXED: cap before trim. Scan log: %TEMP%/hunt2/film__store.md
