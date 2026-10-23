source: adversary-gate/adversary_gate.py
model: glm-5.3 (in-session)
sha256: c591024d7df59a752b80edcdc8ff3af62565fcfc474cb84f58086fc8cfb0a9e8
date: 2026-10-10 13:48
mode: bug
# Review: adversary_gate.py - experiment #10 grafts (bug mode, scope = the graft)

Context pack: full file outline via jCodemunch; the three graft sites read at
byte level; integration smoke over _compose_review_payload and
_print_finding_adjudication in a temp .adversary.

## Verdict
Shippable. Verdict semantics untouched - the grafts are (1) payload enrichment
after the diff, (2) BLOCK-path evidence annotation.

## Graft checks (all verified by smoke)
- _compose_review_payload: delta block computed inside try/except, failure ->
  empty string -> payload byte-identical to pre-graft (fail-open to legacy
  behavior); no-delta diffs produce NO section (byte-stability asserted).
- Delta block rides AFTER the diff: the R1 cache doctrine (stable-first) holds.
- _print_finding_adjudication: ADVERSARY_ADJUDICATE_OFF=1 silences entirely
  (asserted); JSON persistence is best-effort inside its own try; any internal
  failure prints one line and never raises into the verdict path.
- Called ONLY on verdict == BLOCK; CLEAR/WARN paths unchanged; tier flow,
  notarization, and clearance keys untouched.
- Import follows the house deferred-sibling pattern (import adversary_audit).
