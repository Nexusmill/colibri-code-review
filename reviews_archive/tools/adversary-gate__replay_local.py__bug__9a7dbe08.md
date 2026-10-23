source: adversary-gate/replay_local.py
model: glm-5.3 (in-session)
sha256: 9a7dbe080e03185b9206118ca41147be1398aa2a0181033638001fa9e059c2aa
date: 2026-10-10 13:48
mode: bug
# Review: replay_local.py - adjudicated-FP graft (bug mode, scope = the graft)

Context pack: verdicts-mode flow read at byte level (replay_one/run/
_print_verdicts_report); the gate_20261009-141354 lesson (stdout must mirror
JSON counts) checked against the new fields.

## Verdict
Shippable. Measurement-only discipline preserved (writes nothing new; adj fields
ride the existing row/report JSON).

## Graft checks
- adj computed inside try/except with the error RECORDED in adj_totals (never
  loses a round to adjudication failure).
- disagree_anchored/disagree_unanchored derive from the same adj_totals the
  DISAGREE stdout line prints - the gate_20261009-141354 stdout-mirrors-JSON
  law holds by construction.
- replay_selftest 16/16 and test_replay_local 14/14 after the graft (injected
  call path untouched).
- rows without adj (agree/CLEAR) carry no adj fields - report size unchanged
  for the agreement class.
