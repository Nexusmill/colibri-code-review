<!-- colibri review
source: src/stores/queueStore.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: ce2616724d64ed0ac981d458136272be3e872e8acd5cd613730a70f5e24ed4a4
date: 2026-09-06
mode: bug
context: E-4 wave (queue/deck quality batch); copy-diagnostics verified live with clipboard result; etaMs live null-with-basis
-->

## Verdict
Shippable. Two-line delta: the Job preflight type + copy gain etaMs. No behavior change elsewhere.

## Postscript (adversary round 3 remediation, same session)
Job gained startedAt, stamped at execution_start - the bench-median ETA must
measure the RENDER, never queue wait (gate catch: a job queued behind other
work opened its own render already "past bench median").
(bytes advanced to 70d77bf8)
