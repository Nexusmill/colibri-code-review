# colibri bug review - src/components/StatusFooter.tsx (delta)

source: src/components/StatusFooter.tsx · reviewer: ZCode GLM-5.3 in-session · sha256 47f263c6 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs c345b763 @ b1f6a1a 2026-08-19)
context: diff 6+1; prior review c345b763 carried; tiers.ts fmtGb (cache-hit family).

## Verdict

Shippable - the GB display rule unified on the truncating fmtGb (the residual-shelf rounding twin: this local toFixed(1) once ROUNDED, so the doctrine's own 7.9992 GiB boundary read "8.0" here while the wizard's floor said 7).

## Bugs & vulnerabilities

None new.

## Missing safeguards

- none new.

## Fixed since last review

- the fmtGb rounding twin (project-memory residual shelf) - FIX VERIFIED in this delta; the unit conversion (bytes -> GiB before fmtGb) is stated and correct.
