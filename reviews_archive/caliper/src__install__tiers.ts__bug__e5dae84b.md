source: src/install/tiers.ts
reviewer: tencent/hy4-preview (scan ladder hunt T2)
sha256: e5dae84bf2acc543c9e2a2b02b7157ef1328bb478941427f5e9a28e3c2ee5c1c
date: 2026-09-19 13:08
mode: bug
context: the approved five-rung ladder; LADDER constant is law

1 finding, CONFIRMED + FIXED: [MEDIUM] judgeTier took the FIRST CUDA device - a multi-GPU host judged itself by its smaller card and told the owner the cloud was the honest pick for work the big card does locally. FIXED: the largest vramTotal CUDA device speaks for the machine. Pinned (RTX 3050 8GB + RTX 4090 24GB -> video tier on the 4090).
Scan log: %TEMP%/hunt2/install__tiers.md
