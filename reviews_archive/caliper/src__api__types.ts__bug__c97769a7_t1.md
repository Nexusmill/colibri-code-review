source: src/api/types.ts
reviewer: tencent/hy4-preview (scan ladder hunt T1) + M3 grok-4.6 escalation
sha256: c97769a7ed5a93ab958e3eb3f65b6ecac48b7c88d5fde98c0feaac2e505c56c5
date: 2026-09-19 11:45
mode: bug
context: shared API vocabulary; consumers verified in-session

Findings: 1 HIGH + 2 MEDIUM.
- [HIGH] CONFIRMED (downgraded practical impact) + FIXED: CaliperVram declared the reading fields required on BOTH shapes - the error path carries only {error}. Every runtime consumer happened to be guarded, but the contract invited unguarded reads. FIXED: discriminated union CaliperVramReading | {error} + exported isVramReading guard; StatusFooter/bundlesStore narrow at each read site and the diagnostics speak the node's error sentence. M3 (grok-4.6 high, context-loaded with these findings): "no new findings".
- [MEDIUM] CONFIRMED + FIXED: WsEvent lacked execution_interrupted - an interrupt from ANY client let the trailing executing-null mark the interrupted job DONE with partial outputs (reachable via the app's own CLEAR THE WEDGE). FIXED: union variant + ws.ts normalizer case + queueStore failed/"Interrupted." handling. Pinned (ws.test.ts + stores.test.ts).
- [MEDIUM] REFUTED: execution_error nodeId/nodeType nullability - the normalizer maps missing ids to "?" fallbacks; the type describes the normalized shape, not the wire.
M3 pass recorded as lineage toward the three-model lock at this sha (hy4 found material; exhaustion count reset).
