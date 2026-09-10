# colibri bug review - src/film/joins.ts (post-fix first review)

source: src/film/joins.ts · reviewer: ZCode GLM-5.3 in-session · sha256 d95bc4b8 (full sha in manifest) · 2026-09-05 · mode: bug (first review of the remediation-wave module)
context: the xfade/song remediation's pure planner; 6 unit tests including the gate-round-4 wiring regression; the adversarial commit gate reviewed this file's arithmetic end-to-end across FIVE rounds (gate_20260905-101122/-104403/-105219/-111141/-113203/-115032, the last CLEARing it).

## Verdict

Shippable - the freeze-pad/concat doctrine is implemented and adversarially verified: pads land only on dissolve-preceding cuts and are WIRED into their links (the round-4 finding - raw [i:v] operands bypassing the pad, dangling [vNpad] outputs - is fixed and pinned by the no-dangling-pad test), xfade offsets consume exactly the held tails, audio concats the song's contiguous spans, both timelines total the span sum, zero-duration probes clamp safely.

## Bugs & vulnerabilities

None open (round 4's HIGH wiring bug fixed; round 5 CLEAR).

## Missing safeguards

- A cut shorter than the crossfade length clamps its offset at 0 (degenerate, pre-existing parity with the old code).

## Verified-correct

- Every [vNpad] output consumed exactly once; dissolves[0] is always false from the call site; ceil-carved grids (autopilot.ts) guarantee slots <= the pair cap, so the planner's assumptions hold by construction.
