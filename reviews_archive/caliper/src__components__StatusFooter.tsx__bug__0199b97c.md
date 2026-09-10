<!-- colibri review
source: src/components/StatusFooter.tsx
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 0199b97cd06c38f03cd21473326bd679434d84a1ced8fad9f59b1f7d646f1c26
date: 2026-09-06
mode: bug
context: E-1 wave (node self-identification); live-verified through :4173 + backend 8188 this session; prior reviews consulted via _manifest.json (delta reviews)
-->

## Verdict
Shippable. Delta: canonical state + 30s poll (interval cleaned on unmount), canonical prop into VramDiagnostic, verdict gated on vram presence, one line rendered with the chassis vocabulary (diag-line + diag-dim baseline / text-danger drift - the class is proven in the build by QueueSurface usage). DOM-verified and pixel-verified through the running app this session (screenshot: line dim, complete, uncluttered below the process list).

## Bugs & vulnerabilities
(none confirmed)

- REFUTED in pass 3: "the 30s poll could outlive the footer" - the effect returns clearInterval, same pattern as the three existing polls beside it.

## Postscript (adversary round 1 remediation, same session)
The external gate's LOW-2 was accepted: the pre-self-id tooltip overstated
("restarting the backend loads the current copy" - only true when the
custom_nodes file is itself current). Now says restart loads whatever copy
sits in custom_nodes and names the sync duty. Re-verified: tsc 0, vitest
438/438, build 0, tier 59/0/4 exit 0, footer re-screenshotted in sync.
Reviewed bytes advanced to 1baa792e (this postscript covers the delta).
