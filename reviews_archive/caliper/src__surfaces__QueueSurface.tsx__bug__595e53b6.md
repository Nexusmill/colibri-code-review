<!-- colibri review
source: src/surfaces/QueueSurface.tsx
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 595e53b63c7346767f6655f1e44e5d9b9802d4b8f6ca55abde7f80a7cfff8199
date: 2026-09-06
mode: bug
context: E-4 wave (queue/deck quality batch); copy-diagnostics verified live with clipboard result; etaMs live null-with-basis
-->

## Verdict
Shippable. The orphan row's title speaks the graph; etaLine is pure (null without basis, remaining-seconds with basis, past-median honesty); rendered with its basis tooltip.

- REFUTED in pass 3: "etaLine could render a negative countdown" - the past-median branch speaks words, not numbers.

## Postscript (adversary round 3 remediation, same session)
etaLine now counts from startedAt (execution_start), silence until the stamp
exists; queuedAt stays in the param type as documentation that queue wait is
deliberately ignored. Regression-pinned in QueueSurface.test.tsx (5s render
behind 120s queue wait reads "eta ~55s", not past-median).
(bytes advanced to 5e4ec9f2)
