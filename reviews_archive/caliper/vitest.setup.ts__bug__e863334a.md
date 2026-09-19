<!-- source: vitest.setup.ts | reviewer: zcode-glm-5.3 | sha256: e863334ab65d8152e28e2318f78684dd73754268e657f87c400adfa7485b439d | date: 2026-09-15 | mode: bug -->
<!-- context: Wave 6 FINAL delta review (post design-adversary remediation). Call sites traced live (curl through :4173, harness PASS 75/0/8, vitest 499/499, tsc 0); FEATURES row `route-intelligence` + docs/reviews/route-intelligence-2026-09-15.md are the contract. -->

## Verdict
Shippable - one guarded shim, same class as the localStorage precedent.

## Bugs & vulnerabilities (delta: scrollIntoView shim)
- None. The shim is existence-guarded, no-op, and kills the deterministic unhandled TypeError from FilmWizard's rAF-scrolled error banner (evidence: repeated full-suite runs, zero unhandled errors after).
