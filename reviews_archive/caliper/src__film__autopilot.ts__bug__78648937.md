source: src/film/autopilot.ts
reviewer: tencent/hy4-preview (scan ladder hunt T1) + M3 grok-4.6 escalation
sha256: 786489378808ecb8ad912a6b62d04a7b1581bf0bafa64b49823ad850cf75a1d3
date: 2026-09-19 11:50
mode: bug
context: two-tier doctrine; gate chain; 230s brain calls normal; prior hunts excluded

Findings: 1 HIGH + 1 LOW, both CONFIRMED and FIXED:
- [HIGH] deriveEngineCards emitted battery-FAILED engines sitting on the live shoot ladder (the fail-guard covered only unseen owner cards in the second loop) - a proven-broken engine stayed pickable and spendable. FIXED: the live-ladder loop skips battery[ref] === "fail" before any push. Pinned.
- [LOW] validateStoryboard accepted out-of-canon cutIn values (the canon check lived only in parseRedraft) - an invalid transition lived in the approved plan until a repair tripped over it. FIXED: the words mapping validates against CUTIN_CANON (carried values only; shot 0's cutIn is dropped by design). Pinned.
M3 (grok-4.6 high, context-loaded): "no new findings".
