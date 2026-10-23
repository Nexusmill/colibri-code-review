source: adversary-gate/test_finding_adjudicator.py
model: glm-5.3 (in-session)
sha256: fd677ae80048ebad349e0ce847b906cd1e6e352d35c5ccf0ebf07e805e4d9f20
date: 2026-10-10 13:48
mode: bug
# Review: adversary-gate/test_finding_adjudicator.py (bug mode)

Context pack: the module under test (its own docstring contract); the test-specific
classes from the skill's Phase 0; the earlier red run (5 failures) as red-green
evidence for the extraction assertions.

## Verdict
Sound. Assertions demonstrated the ability to fail (the header-shape bug produced
a real IndexError/assert failures before the fixture was corrected - genuine
red-green, not tautologies).

## Checks performed
- No assertions that cannot fail (each asserts a specific disposition/count;
  the garbage-input tests assert emptiness on inputs that WOULD produce content
  on a parser regression).
- No network, no env-var leaks (the ADVERSARY_ADJUDICATE_OFF kill-switch test
  lives in the integration smoke, not here, and deletes the var).
- Deterministic: pure string fixtures, no time/random.
- Corpus T3 sibling check ran out-of-band against junk/exp_diffs.json (parse
  crash-free on all 10 real diffs; production-shape -/+ pair detected on a real
  _safe_edit.py line).
