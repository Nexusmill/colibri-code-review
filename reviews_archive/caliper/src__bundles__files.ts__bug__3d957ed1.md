source: src/bundles/files.ts
reviewer: tencent/hy4-preview (scan ladder hunt T2)
sha256: 3d957ed117f5196b8d77ba30335da952ba6b24d14c45c987eaf2fe5c43370e4f
date: 2026-09-19 13:14
mode: bug
context: file validation; schema flags malformed bundles but does not remove them

1 finding, CONFIRMED + FIXED: [HIGH] validateFiles iterated b.text_encoders/b.loras and dereferenced b.vae unguarded - a hand-edited or legacy bundle missing those fields (which the schema FLAGS, not removes) threw a TypeError that crashed the whole catalog validation instead of answering issues. FIXED: shape guards (Array.isArray / object check) with empty fallbacks.
Scan log: %TEMP%/hunt2/bundles__files.md
