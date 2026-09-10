<!-- colibri review
source: src/components/DeckControls.tsx
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: b64cbd06b3670ae3725df1e2bc7928c9e8f3aa1f7d4d7ee0e82eb82e0d7a2702
date: 2026-09-06
mode: bug
context: E-4 wave (queue/deck quality batch); copy-diagnostics verified live with clipboard result; etaMs live null-with-basis
-->

## Verdict
Shippable. The done span became a button (same text-info tone, hover underline, an arrow suffix naming the jump); click lands on Outputs. The failed line stays a span - a failure has nowhere to jump.
