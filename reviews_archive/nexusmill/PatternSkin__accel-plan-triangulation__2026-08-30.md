# Three-plan adversarial triangulation - accel.py remediation plans (A=grok-4.3, B=hy4-preview, C=in-session colibri)
judge: independent in-session subagent with repo access (plans anonymized, authorship stripped)
date: 2026-08-30 | subject: HY4-ACCEL-PROBETIMEOUT + HY4-ACCEL-KCLAMP plans | file sha ded218ea37a3e563
ground truth verified live: cKDTree(3).query(k=5) pads idx with n + inf distance, never raises.

## CONVERGENCE (all three, bytes-confirmed - the safe core)
- F1: replace the three literals with _config("probe_timeout", 90/90/240); only 3 call sites; defaults unchanged.
- F2: scipy branch is the only in-process backend without a clamp; kk = max(1, min(int(k), m)) is the fix expression.
- Both edits small and revertible.

## DIVERGENCE (judged against bytes)
- A's _config special-case edit: REFUTED and a REGRESSION - _config already int-types by default; A's `int(v)` raises on junk env, each probe's blanket except would swallow it and falsely mark SciPy/GPU broken from a config typo.
- A's line numbers: ALL SEVEN REFUTED (three beyond EOF of the 1667-line file). Fabricated.
- A's verification one-liner: POSIX env syntax on Windows and observes nothing. A's KCLAMP test never forces the scipy backend - born green on scipy-less machines.
- B's quoted code: CONFIRMED verbatim (nothing fabricated). "or raise" imprecise (scipy pads, never raises). B never mentions the worker tier.
- C's "worker runs FIRST" (call order :909 before :914): CONFIRMED - only C noticed.
- C's "worker runs scipy and would return the same OOB padding": REFUTED ON BOTH COUNTS - accel_worker.py is torch->numpy only, and BOTH worker backends already clamp (:85, :101; _OPS passes int(meta k) :116). CONSEQUENCE: branch-only fixes (A, B) are sufficient on every reachable path as shipped; C's fix is also sufficient, simpler and uniformizing - but its claimed NECESSITY was fabricated.
- C's single-knob semantics (env can LOWER gpu's 240) + ~2x wall from _retry_run attempts=2: CONFIRMED; unremarked by A/B.
- C's "no caller passes k>m" future-facing note: CONFIRMED (projections.py:433 pre-clamps min(13, m)).
- C's clamp line refs off by 2 and 1 (955->953, 976->977); all other C refs exact.
- Tests-as-described: A/B propose pytest files - convention mismatch (ZERO pytest usage in tests/harness; pytest installed but the files would be orphans - no runner tier, no spec row). C's battery is the verified repo pattern (pskpkg stub import, spec_results row, covenant + safe-edit discipline).

## GRADES
| Plan | F1 | F2 |
|---|---|---|
| A (grok-4.3) | D | D+ |
| B (hy4-preview) | A- | A- |
| C (in-session) | A | B+ |

RANKING: C > B > A. Decisive differentiator: C is the only plan whose test plan exists in this
repo as described. Counterweight stated in the same breath: on F2, B beats C on factual
accuracy - B fabricated nothing; C invented the worker-scipy mechanism to declare rival
approaches insufficient (they are not). A is sunk independently: zero of seven line refs
survive contact with the file.

## META-FINDING (the lesson)
None of the three plans (nor the gated docket) actually read accel_worker.py - the two lines
that settle the whole sufficiency debate (:85/:101 clamps, torch/numpy-only). C looked in the
right direction and GUESSED; A and B never looked. Adversarial triangulation caught what the
author was defending - again.
