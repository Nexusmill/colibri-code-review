source: adversary-gate/finding_adjudicator.py
model: glm-5.3 (in-session)
sha256: 3f63047be1ec691794367f0b7dda474e8979658e0ec130d0090b910e2a2d3de5
date: 2026-10-10 13:48
mode: bug
# Review: adversary-gate/finding_adjudicator.py (bug mode)

Context pack: experiment #10 program ledger (adj-FP 0/15, anchored-confirm ~100%);
jCodemunch outline of adversary_gate.py for integration points; the E10 junk
adjudicator this module ports; corpus validation against junk/exp_diffs.json.

## Verdict
Shippable as an evidence-only layer. The load-bearing invariant - the module
cannot influence a verdict because nothing in it is wired to verdict logic -
holds by construction (verified: no callers outside payload annotation and
BLOCK-path evidence).

## Bugs & vulnerabilities
None CONFIRMED. Verified-checked classes:
- flush() closure over loop-rebound run lists (rebinding happens in the same
  function scope; re-verified per-file isolation) - correct.
- guard-inversion false positive on words containing "not" ("if note is") -
  impossible: replace() needs the literal "not " with space; "note " does not
  match. Checked by test_guard_not_none_family_detected + corpus run.
- garbage inputs (empty diff, non-diff text) return [] - test_garbage_input_crash_free.

## Missing safeguards (by-design, documented in module docstring)
- MAX_DELTAS=40 silently caps the delta list (marked in payload when capped).
- fragment anchoring accepts a match in ANY + line of the diff (loose by
  design: the reviewer quoted the diff, not necessarily the file body).
- adjudication never verifies reachability here (the E10 reach probe needs the
  code index; the gate runs without it) - dispositions are anchor-level only.
